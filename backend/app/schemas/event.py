"""
Pydantic schemas for Event clusters and article assignments.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.article import ArticleResponse


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "Unclassified"
    status: str = "active"


class EventResponse(EventBase):
    id: str
    first_observed_at: datetime
    last_observed_at: datetime
    article_count: int
    average_confidence: float
    model_version: str
    assignment_method: str
    key_entities_json: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    items: List[EventResponse]
    total: int
    page: int
    page_size: int
    pages: int


class EventDetailResponse(EventResponse):
    articles: List[ArticleResponse] = []


class EventAssignmentResponse(BaseModel):
    id: str
    article_id: str
    event_id: str
    assignment_method: str
    semantic_score: float
    temporal_score: float
    entity_score: float
    combined_score: float
    model_version: str
    is_manual_review: bool
    reviewer_notes: Optional[str] = None
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ManualReviewRequest(BaseModel):
    article_id: str
    target_event_id: Optional[str] = Field(None, description="Event ID to assign, or null to make unassigned/noise")
    create_new_event: bool = Field(False, description="Whether to create a brand new event for this article")
    new_event_title: Optional[str] = None
    notes: Optional[str] = None


class TimelineItem(BaseModel):
    article_id: str
    headline: str
    source_name: str
    source_url: Optional[str] = None
    published_at: datetime
    summary_excerpt: str
    combined_score: float
    is_first_observed: bool = False
