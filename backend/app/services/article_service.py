"""
Article business logic service.
Handles storage, retrieval, filtering, pagination, and entity extraction.
"""
import uuid
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, desc

from backend.app.models.article import Article
from backend.app.models.event import Event
from backend.app.ml.preprocessor import clean_text, compute_content_hash
from backend.app.ml.ner_extractor import EntityExtractor

entity_extractor = EntityExtractor()


class ArticleService:
    def __init__(self, db: Session):
        self.db = db

    def get_article_by_id(self, article_id: str) -> Optional[Article]:
        return self.db.query(Article).filter(Article.id == article_id).first()

    def get_article_by_hash(self, content_hash: str) -> Optional[Article]:
        return self.db.query(Article).filter(Article.content_hash == content_hash).first()

    def list_articles(
        self,
        search: Optional[str] = None,
        source_name: Optional[str] = None,
        category: Optional[str] = None,
        assigned_status: Optional[str] = None, # "assigned", "unassigned", "all"
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Article], int]:
        """
        Query articles with flexible filtering, date ranges, and pagination.
        """
        query = self.db.query(Article)

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(or_(
                Article.headline.ilike(search_term),
                Article.body.ilike(search_term)
            ))

        if source_name:
            query = query.filter(Article.source_name == source_name)

        if category:
            query = query.filter(Article.category == category)

        if assigned_status == "assigned":
            query = query.filter(Article.assigned_event_id.isnot(None))
        elif assigned_status == "unassigned":
            query = query.filter(Article.assigned_event_id.is_(None))

        if start_date:
            query = query.filter(Article.published_at >= start_date)
        if end_date:
            query = query.filter(Article.published_at <= end_date)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(Article.published_at)).offset(offset).limit(page_size).all()

        return items, total

    def import_articles_batch(self, article_dicts: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Batch import normalized articles into database.
        Skips exact duplicates by content_hash and extracts entities.
        """
        inserted_count = 0
        skipped_count = 0

        for item in article_dicts:
            c_hash = item.get("content_hash")
            if not c_hash:
                c_hash = compute_content_hash(item["headline"], item["body"])

            # Check duplicate
            existing = self.get_article_by_hash(c_hash)
            if existing:
                skipped_count += 1
                continue

            # Extract entities
            text_for_ner = f"{item['headline']} {item['body']}"
            entities = entity_extractor.extract_entities(text_for_ner)
            entities_json = json.dumps(entities)

            art_id = item.get("id") or f"art-{uuid.uuid4().hex[:10]}"

            article = Article(
                id=art_id,
                external_id=item.get("external_id"),
                headline=item["headline"],
                body=item["body"],
                description=item.get("description"),
                source_name=item["source_name"],
                source_url=item.get("source_url"),
                published_at=item["published_at"],
                language=item.get("language", "en"),
                content_hash=c_hash,
                ground_truth_event_id=item.get("ground_truth_event_id"),
                category=item.get("category"),
                entities_json=entities_json,
                processing_status="pending"
            )

            self.db.add(article)
            inserted_count += 1

        self.db.commit()
        return {"inserted": inserted_count, "skipped": skipped_count}
