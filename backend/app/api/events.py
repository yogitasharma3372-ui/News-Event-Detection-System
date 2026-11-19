"""
Event cluster exploration and management API endpoints.
"""
from typing import Optional, List, Dict, Any
import math
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.event import (
    EventResponse,
    EventListResponse,
    EventDetailResponse,
    ManualReviewRequest,
    TimelineItem
)
from backend.app.services.event_service import EventService
from backend.app.core.config import settings

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=EventListResponse)
def list_events(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = EventService(db)
    items, total = service.list_events(
        category=category,
        status=status,
        search=search,
        page=page,
        page_size=page_size
    )

    pages = math.ceil(total / page_size) if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }


@router.get("/{event_id}", response_model=EventDetailResponse)
def get_event(event_id: str, db: Session = Depends(get_db)):
    service = EventService(db)
    evt = service.get_event_by_id(event_id)
    if not evt:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found.")
    articles = service.get_event_articles(event_id)
    evt_dict = {
        "id": evt.id,
        "title": evt.title,
        "description": evt.description,
        "first_observed_at": evt.first_observed_at,
        "last_observed_at": evt.last_observed_at,
        "category": evt.category,
        "status": evt.status,
        "article_count": evt.article_count,
        "average_confidence": evt.average_confidence,
        "model_version": evt.model_version,
        "assignment_method": evt.assignment_method,
        "key_entities_json": evt.key_entities_json,
        "created_at": evt.created_at,
        "updated_at": evt.updated_at,
        "articles": articles
    }
    return evt_dict


@router.get("/{event_id}/timeline", response_model=List[TimelineItem])
def get_event_timeline(event_id: str, db: Session = Depends(get_db)):
    service = EventService(db)
    timeline = service.get_event_timeline(event_id)
    if not timeline:
        raise HTTPException(status_code=404, detail=f"No timeline found for event '{event_id}'.")
    return timeline


@router.post("/detect")
def trigger_event_detection(
    alpha: float = Query(0.55, ge=0.0, le=1.0),
    beta: float = Query(0.25, ge=0.0, le=1.0),
    gamma: float = Query(0.20, ge=0.0, le=1.0),
    similarity_threshold: float = Query(0.60, ge=0.0, le=1.0),
    decay_hours: float = Query(72.0, gt=0.0),
    reprocess_all: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Run end-to-end clustering on articles using configured hybrid weights and thresholds.
    """
    service = EventService(db)
    try:
        result = service.detect_events_hybrid(
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            similarity_threshold=similarity_threshold,
            decay_hours=decay_hours,
            reprocess_all=reprocess_all
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assignments/review")
def review_assignment(request: ManualReviewRequest, db: Session = Depends(get_db)):
    """
    Manual review workflow: reassign an article to an event, create a new event, or detach as noise.
    """
    service = EventService(db)
    try:
        result = service.review_article_assignment(
            article_id=request.article_id,
            target_event_id=request.target_event_id,
            create_new_event=request.create_new_event,
            new_event_title=request.new_event_title,
            notes=request.notes
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
