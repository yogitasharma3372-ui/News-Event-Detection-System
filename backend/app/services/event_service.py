"""
Event detection and management service.
Orchestrates clustering, event creation, title/summary generation, timelines, and manual review.
"""
import uuid
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func

from backend.app.models.article import Article
from backend.app.models.event import Event
from backend.app.models.event_assignment import EventAssignment
from backend.app.ml.tfidf_model import TfidfBaselineModel
from backend.app.ml.embedding_model import SemanticEmbeddingModel
from backend.app.ml.ner_extractor import EntityExtractor
from backend.app.ml.temporal_scoring import TemporalScorer
from backend.app.ml.hybrid_scorer import HybridScorer
from backend.app.ml.clusterer import EventClusterer
from backend.app.ml.title_generator import EventTitleSummaryGenerator
from backend.app.core.config import settings

title_generator = EventTitleSummaryGenerator()
entity_extractor = EntityExtractor()


class EventService:
    def __init__(self, db: Session):
        self.db = db

    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        return self.db.query(Event).filter(Event.id == event_id).first()

    def list_events(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Event], int]:
        query = self.db.query(Event)

        if category:
            query = query.filter(Event.category == category)
        if status:
            query = query.filter(Event.status == status)
        if search:
            query = query.filter(Event.title.ilike(f"%{search.strip()}%"))

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(Event.last_observed_at)).offset(offset).limit(page_size).all()
        return items, total

    def get_event_articles(self, event_id: str) -> List[Article]:
        return self.db.query(Article).filter(Article.assigned_event_id == event_id).order_by(asc(Article.published_at)).all()

    def get_event_timeline(self, event_id: str) -> List[Dict[str, Any]]:
        """
        Produce a chronological timeline of articles comprising the event.
        """
        articles = self.get_event_articles(event_id)
        if not articles:
            return []

        first_observed_time = articles[0].published_at
        timeline: List[Dict[str, Any]] = []

        for idx, art in enumerate(articles):
            # Fetch assignment score
            assignment = self.db.query(EventAssignment).filter(
                EventAssignment.article_id == art.id,
                EventAssignment.event_id == event_id
            ).first()

            combined_score = assignment.combined_score if assignment else 1.0

            # Excerpt
            body = art.body.strip()
            excerpt = body[:220] + "..." if len(body) > 220 else body

            timeline.append({
                "article_id": art.id,
                "headline": art.headline,
                "source_name": art.source_name,
                "source_url": art.source_url,
                "published_at": art.published_at,
                "summary_excerpt": excerpt,
                "combined_score": round(combined_score, 4),
                "is_first_observed": (art.published_at == first_observed_time)
            })

        return timeline

    def detect_events_hybrid(
        self,
        alpha: float = 0.55,
        beta: float = 0.25,
        gamma: float = 0.20,
        similarity_threshold: float = 0.60,
        decay_hours: float = 72.0,
        reprocess_all: bool = True
    ) -> Dict[str, Any]:
        """
        Run end-to-end event detection on articles.
        Preserves manual user reviews and assigns new clusters.
        """
        articles_query = self.db.query(Article)
        all_articles = articles_query.all()
        if not all_articles:
            return {"status": "no_articles", "events_created": 0}

        # Check manually reviewed assignments to preserve them
        manual_assignments = self.db.query(EventAssignment).filter(
            EventAssignment.is_manual_review == True
        ).all()
        manual_article_ids = {ma.article_id: ma.event_id for ma in manual_assignments}

        # Select articles eligible for automated clustering (excluding those locked by manual review)
        clustering_articles = [a for a in all_articles if a.id not in manual_article_ids]
        if not clustering_articles:
            return {"status": "all_articles_manually_locked", "events_created": 0}

        n = len(clustering_articles)
        texts = [f"{a.headline}. {a.body}" for a in clustering_articles]
        hashes = [a.content_hash for a in clustering_articles]
        timestamps = [a.published_at for a in clustering_articles]

        # 1. Semantic similarities
        embed_model = SemanticEmbeddingModel(
            model_name=settings.DEFAULT_EMBEDDING_MODEL,
            cache_dir=settings.EMBEDDING_CACHE_DIR
        )
        embeddings = embed_model.encode_batch(texts, hashes)
        semantic_matrix = embed_model.compute_similarity_matrix(embeddings)

        # 2. Temporal proximity
        temporal_scorer = TemporalScorer(decay_hours=decay_hours)
        temporal_matrix = temporal_scorer.compute_temporal_matrix(timestamps)

        # 3. Entity overlap
        all_entities = []
        for art in clustering_articles:
            if art.entities_json:
                try:
                    data = json.loads(art.entities_json)
                    all_entities.append(data.get("all", []))
                except Exception:
                    ext = entity_extractor.extract_entities(f"{art.headline} {art.body}")
                    all_entities.append(ext["all"])
            else:
                ext = entity_extractor.extract_entities(f"{art.headline} {art.body}")
                all_entities.append(ext["all"])

        import numpy as np
        entity_matrix = np.ones((n, n), dtype=float)
        for i in range(n):
            for j in range(i + 1, n):
                score = entity_extractor.compute_jaccard_similarity(all_entities[i], all_entities[j])
                entity_matrix[i, j] = score
                entity_matrix[j, i] = score

        # 4. Combined matrix
        hybrid_scorer = HybridScorer(alpha=alpha, beta=beta, gamma=gamma)
        combined_matrix = hybrid_scorer.compute_combined_matrix(semantic_matrix, temporal_matrix, entity_matrix)

        # 5. Cluster
        clusterer = EventClusterer(similarity_threshold=similarity_threshold, min_cluster_size=2)
        cluster_labels, stats = clusterer.cluster_similarity_matrix(combined_matrix)

        # 6. Group articles by cluster
        clusters_dict: Dict[int, List[int]] = {}
        for idx, lbl in enumerate(cluster_labels):
            if lbl >= 0:
                clusters_dict.setdefault(lbl, []).append(idx)

        # Clear existing non-manual events if reprocess_all is requested
        if reprocess_all:
            # Only delete events that have no manual assignments
            existing_events = self.db.query(Event).all()
            for ev in existing_events:
                has_manual = any(ma.event_id == ev.id for ma in manual_assignments)
                if not has_manual:
                    # Unassign articles belonging to this event
                    for art in ev.articles:
                        art.assigned_event_id = None
                    self.db.delete(ev)
            self.db.commit()

        # 7. Create Events and Assignments
        events_created = 0
        for cluster_id, member_indices in clusters_dict.items():
            member_articles = [clustering_articles[idx] for idx in member_indices]
            member_articles.sort(key=lambda a: a.published_at)

            first_seen = member_articles[0].published_at
            last_seen = member_articles[-1].published_at

            headlines = [a.headline for a in member_articles]
            body_dicts = [{"headline": a.headline, "body": a.body, "source_name": a.source_name} for a in member_articles]

            # Generate representative title and extractive summary
            title = title_generator.select_representative_title(headlines)
            summary = title_generator.generate_extractive_summary(body_dicts)
            category = title_generator.infer_category([a.headline + " " + a.body for a in member_articles])

            # Collect key entities
            cluster_ents = set()
            for idx in member_indices:
                cluster_ents.update(all_entities[idx][:5])
            key_entities_json = json.dumps({"all": sorted(list(cluster_ents))[:10]})

            event_id = f"evt-{uuid.uuid4().hex[:10]}"
            new_event = Event(
                id=event_id,
                title=title,
                description=summary,
                first_observed_at=first_seen,
                last_observed_at=last_seen,
                category=category,
                status="active",
                article_count=len(member_articles),
                average_confidence=1.0,
                model_version="hybrid-1.0",
                assignment_method="hybrid",
                key_entities_json=key_entities_json
            )
            self.db.add(new_event)

            for idx in member_indices:
                art = clustering_articles[idx]
                art.assigned_event_id = event_id
                art.processing_status = "processed"

                # Calculate avg combined score to cluster peers
                peer_scores = [combined_matrix[idx, other_idx] for other_idx in member_indices if other_idx != idx]
                avg_peer_score = float(np.mean(peer_scores)) if peer_scores else 1.0

                assignment = EventAssignment(
                    id=f"asg-{uuid.uuid4().hex[:10]}",
                    article_id=art.id,
                    event_id=event_id,
                    assignment_method="hybrid",
                    semantic_score=float(semantic_matrix[idx, idx]),
                    temporal_score=1.0,
                    entity_score=1.0,
                    combined_score=avg_peer_score,
                    model_version="hybrid-1.0",
                    is_manual_review=False
                )
                self.db.add(assignment)

            events_created += 1

        # Mark unassigned noise articles
        for idx, lbl in enumerate(cluster_labels):
            if lbl == -1:
                art = clustering_articles[idx]
                art.assigned_event_id = None
                art.processing_status = "processed_unassigned"

        self.db.commit()

        return {
            "status": "success",
            "events_created": events_created,
            "total_articles": n,
            "clustered_articles": sum(len(m) for m in clusters_dict.values()),
            "noise_articles": stats["noise_count"]
        }

    def review_article_assignment(
        self,
        article_id: str,
        target_event_id: Optional[str] = None,
        create_new_event: bool = False,
        new_event_title: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Human reviewer override workflow.
        Manually reassign an article to another event, create a new event, or detach as noise.
        Records an audit assignment marked as is_manual_review=True.
        """
        article = self.db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise ValueError(f"Article '{article_id}' not found.")

        old_event_id = article.assigned_event_id

        if create_new_event:
            title = new_event_title or f"Manual Event: {article.headline[:60]}"
            new_evt_id = f"evt-man-{uuid.uuid4().hex[:8]}"
            target_event = Event(
                id=new_evt_id,
                title=title,
                description=article.headline,
                first_observed_at=article.published_at,
                last_observed_at=article.published_at,
                category=article.category or "General",
                status="active",
                article_count=1,
                average_confidence=1.0,
                model_version="manual_review",
                assignment_method="manual"
            )
            self.db.add(target_event)
            assigned_event_id = new_evt_id
        else:
            assigned_event_id = target_event_id
            if target_event_id:
                target_event = self.get_event_by_id(target_event_id)
                if not target_event:
                    raise ValueError(f"Target event '{target_event_id}' not found.")

        # Update article
        article.assigned_event_id = assigned_event_id
        article.processing_status = "manually_reviewed"

        # Log assignment record
        assignment = EventAssignment(
            id=f"asg-man-{uuid.uuid4().hex[:10]}",
            article_id=article.id,
            event_id=assigned_event_id or old_event_id or "unassigned",
            assignment_method="manual",
            semantic_score=1.0,
            temporal_score=1.0,
            entity_score=1.0,
            combined_score=1.0,
            model_version="human_expert",
            is_manual_review=True,
            reviewer_notes=notes,
            previous_event_id=old_event_id
        )
        self.db.add(assignment)

        # Update article counts on events
        if old_event_id:
            old_evt = self.get_event_by_id(old_event_id)
            if old_evt:
                remaining = self.db.query(Article).filter(Article.assigned_event_id == old_event_id).count()
                old_evt.article_count = max(0, remaining - 1)

        if assigned_event_id:
            new_evt = self.get_event_by_id(assigned_event_id)
            if new_evt:
                new_count = self.db.query(Article).filter(Article.assigned_event_id == assigned_event_id).count()
                new_evt.article_count = new_count + 1

        self.db.commit()
        return {
            "status": "success",
            "article_id": article_id,
            "assigned_event_id": assigned_event_id,
            "previous_event_id": old_event_id
        }
