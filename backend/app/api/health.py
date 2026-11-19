"""
System health and metadata endpoints.
"""
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.session import get_db
from backend.app.models.article import Article
from backend.app.models.event import Event
from backend.app.models.ingestion_job import IngestionJob
from backend.app.models.experiment import Experiment
from backend.app.core.config import settings

router = APIRouter(tags=["Health & Metadata"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns system status, active configuration, and database connection state.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/metadata")
def get_system_metadata(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns system dashboard summary statistics:
    - total articles
    - assigned articles
    - unassigned / noise articles
    - total events
    - total sources
    - total experiments
    - latest ingestion timestamp
    """
    total_articles = db.query(func.count(Article.id)).scalar() or 0
    assigned_articles = db.query(func.count(Article.id)).filter(Article.assigned_event_id.isnot(None)).scalar() or 0
    unassigned_articles = total_articles - assigned_articles
    
    total_events = db.query(func.count(Event.id)).scalar() or 0
    total_experiments = db.query(func.count(Experiment.id)).scalar() or 0
    
    # Active sources
    unique_sources = [r[0] for r in db.query(Article.source_name).distinct().all()]
    
    # Latest ingestion timestamp
    latest_article = db.query(Article.ingested_at).order_by(Article.ingested_at.desc()).first()
    latest_ingested_at = latest_article[0].isoformat() if latest_article else None

    # Distribution of events by category
    categories_counts = {}
    cat_rows = db.query(Event.category, func.count(Event.id)).group_by(Event.category).all()
    for cat, count in cat_rows:
        categories_counts[cat] = count

    return {
        "total_articles": total_articles,
        "assigned_articles": assigned_articles,
        "unassigned_articles": unassigned_articles,
        "total_events": total_events,
        "total_sources": len(unique_sources),
        "sources": unique_sources,
        "total_experiments": total_experiments,
        "latest_ingestion_timestamp": latest_ingested_at,
        "event_categories_distribution": categories_counts,
        "default_model": settings.DEFAULT_EMBEDDING_MODEL,
        "hybrid_weights": {
            "alpha_semantic": settings.DEFAULT_ALPHA_SEMANTIC,
            "beta_temporal": settings.DEFAULT_BETA_TEMPORAL,
            "gamma_entity": settings.DEFAULT_GAMMA_ENTITY
        }
    }


@router.get("/sources")
def get_sources_list(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns list of all active news sources in database with article counts.
    """
    rows = db.query(Article.source_name, func.count(Article.id)).group_by(Article.source_name).all()
    sources = [{"name": r[0], "article_count": r[1]} for r in rows]
    return {"sources": sources}
