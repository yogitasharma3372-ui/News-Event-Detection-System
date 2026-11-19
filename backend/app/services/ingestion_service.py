"""
Live news ingestion service and incremental online event assignment.
"""
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.ingestion_job import IngestionJob
from backend.app.models.article import Article
from backend.app.models.event import Event
from backend.app.models.event_assignment import EventAssignment
from backend.app.ingestion.rss_provider import RSSNewsProvider
from backend.app.ingestion.newsapi_provider import NewsAPIProvider
from backend.app.ml.preprocessor import compute_content_hash, clean_text
from backend.app.ml.ner_extractor import EntityExtractor
from backend.app.ml.embedding_model import SemanticEmbeddingModel
from backend.app.ml.temporal_scoring import TemporalScorer
from backend.app.ml.hybrid_scorer import HybridScorer
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.rss_provider = RSSNewsProvider()
        self.newsapi_provider = NewsAPIProvider()
        self.entity_extractor = EntityExtractor()
        self.temporal_scorer = TemporalScorer(decay_hours=settings.DEFAULT_TEMPORAL_DECAY_HOURS)
        self.hybrid_scorer = HybridScorer(
            alpha=settings.DEFAULT_ALPHA_SEMANTIC,
            beta=settings.DEFAULT_BETA_TEMPORAL,
            gamma=settings.DEFAULT_GAMMA_ENTITY
        )
        self.embed_model = SemanticEmbeddingModel(
            model_name=settings.DEFAULT_EMBEDDING_MODEL,
            cache_dir=settings.EMBEDDING_CACHE_DIR
        )

    def list_jobs(self) -> List[IngestionJob]:
        return self.db.query(IngestionJob).order_by(desc(IngestionJob.start_time)).all()

    def get_job_by_id(self, job_id: str) -> Optional[IngestionJob]:
        return self.db.query(IngestionJob).filter(IngestionJob.id == job_id).first()

    def trigger_ingestion(
        self,
        provider: str = "rss",
        query: Optional[str] = None,
        feed_url: Optional[str] = None,
        max_articles: int = 25,
        api_key: Optional[str] = None
    ) -> IngestionJob:
        """
        Execute an ingestion job from RSS or NewsAPI, deduplicate, and incrementally assign.
        """
        job_id = f"job-{uuid.uuid4().hex[:10]}"
        job = IngestionJob(
            id=job_id,
            provider=provider,
            query=query,
            status="running",
            start_time=datetime.now(timezone.utc)
        )
        self.db.add(job)
        self.db.commit()

        try:
            if provider == "rss":
                fetched = self.rss_provider.fetch_articles(query=query, limit=max_articles, feed_url=feed_url)
            elif provider == "newsapi":
                fetched = self.newsapi_provider.fetch_articles(query=query, limit=max_articles, api_key=api_key)
            else:
                raise ValueError(f"Unknown provider '{provider}'. Choose 'rss' or 'newsapi'.")

            job.articles_fetched = len(fetched)
            inserted = 0
            duplicates = 0

            for item in fetched:
                c_hash = compute_content_hash(item["headline"], item["body"])
                existing = self.db.query(Article).filter(Article.content_hash == c_hash).first()
                if existing:
                    duplicates += 1
                    continue

                # Extract entities
                ext = self.entity_extractor.extract_entities(f"{item['headline']} {item['body']}")
                entities_json = json.dumps(ext)

                art_id = f"art-{uuid.uuid4().hex[:10]}"
                article = Article(
                    id=art_id,
                    external_id=item.get("external_id"),
                    headline=item["headline"],
                    body=item["body"],
                    source_name=item["source_name"],
                    source_url=item.get("source_url"),
                    published_at=item["published_at"],
                    language=item.get("language", "en"),
                    content_hash=c_hash,
                    entities_json=entities_json,
                    processing_status="pending"
                )
                self.db.add(article)
                self.db.flush() # Flush to register article in session

                # Perform incremental online assignment against active events
                self._assign_incremental(article, ext.get("all", []))
                inserted += 1

            job.articles_inserted = inserted
            job.duplicates_skipped = duplicates
            job.status = "completed"
            job.end_time = datetime.now(timezone.utc)
            self.db.commit()

        except Exception as e:
            logger.error(f"Ingestion job {job_id} failed: {e}")
            job.status = "failed"
            job.error_summary = str(e)
            job.failures += 1
            job.end_time = datetime.now(timezone.utc)
            self.db.commit()

        return job

    def _assign_incremental(self, article: Article, entities: List[str]) -> None:
        """
        Evaluate article against recent active events.
        Assigns to nearest matching cluster if hybrid score exceeds threshold.
        """
        # Fetch active events from recent 7 days
        active_events = self.db.query(Event).filter(Event.status == "active").all()
        if not active_events:
            article.processing_status = "unassigned_no_events"
            return

        art_text = f"{article.headline}. {article.body}"
        art_embed = self.embed_model.encode_article(art_text, article.content_hash)

        best_score = 0.0
        best_event: Optional[Event] = None
        best_components = (0.0, 0.0, 0.0)

        for evt in active_events:
            # Compare with event's representative title and timeline
            evt_text = f"{evt.title}. {evt.description or ''}"
            evt_hash = compute_content_hash(evt.title, evt.description or "")
            evt_embed = self.embed_model.encode_article(evt_text, evt_hash)

            # 1. Semantic score
            import numpy as np
            sem_score = float(np.dot(art_embed, evt_embed))
            sem_score = float(np.clip((sem_score + 1.0) / 2.0, 0.0, 1.0))

            # 2. Temporal score (comparing with last observed article in event)
            temp_score = self.temporal_scorer.compute_temporal_score(article.published_at, evt.last_observed_at)

            # 3. Entity score
            evt_entities = []
            if evt.key_entities_json:
                try:
                    evt_entities = json.loads(evt.key_entities_json).get("all", [])
                except Exception:
                    pass
            ent_score = self.entity_extractor.compute_jaccard_similarity(entities, evt_entities)

            # Combined score
            comb_score = self.hybrid_scorer.score_pair(sem_score, temp_score, ent_score)

            if comb_score > best_score:
                best_score = comb_score
                best_event = evt
                best_components = (sem_score, temp_score, ent_score)

        if best_event and best_score >= settings.DEFAULT_SIMILARITY_THRESHOLD:
            # Assign to existing event
            article.assigned_event_id = best_event.id
            article.processing_status = "incrementally_assigned"
            best_event.article_count += 1
            if article.published_at > best_event.last_observed_at:
                best_event.last_observed_at = article.published_at

            assignment = EventAssignment(
                id=f"asg-inc-{uuid.uuid4().hex[:10]}",
                article_id=article.id,
                event_id=best_event.id,
                assignment_method="incremental_hybrid",
                semantic_score=best_components[0],
                temporal_score=best_components[1],
                entity_score=best_components[2],
                combined_score=best_score,
                model_version="incremental-1.0",
                is_manual_review=False
            )
            self.db.add(assignment)
        else:
            article.processing_status = "unassigned_below_threshold"
