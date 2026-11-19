"""
Pydantic schemas for Article requests, responses, and validation.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ArticleBase(BaseModel):
    headline: str = Field(..., min_length=3, max_length=512, description="Article title / headline")
    body: str = Field(..., min_length=10, description="Full article text content")
    source_name: str = Field(..., min_length=1, max_length=128, description="Publisher or news agency name")
    source_url: Optional[str] = Field(None, max_length=1024, description="Validated web link to original publication")
    published_at: datetime = Field(..., description="UTC publication timestamp")
    external_id: Optional[str] = Field(None, max_length=128, description="Originating identifier from feed or provider")
    language: str = Field("en", max_length=16)
    category: Optional[str] = Field(None, max_length=64)
    ground_truth_event_id: Optional[str] = Field(None, max_length=64, description="Optional ground truth cluster for research benchmark")


class ArticleCreate(ArticleBase):
    pass


class ArticleResponse(ArticleBase):
    id: str
    content_hash: str
    assigned_event_id: Optional[str] = None
    entities_json: Optional[str] = None
    processing_status: str
    processing_error: Optional[str] = None
    ingested_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArticleListResponse(BaseModel):
    items: List[ArticleResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ArticleFilterParams(BaseModel):
    search: Optional[str] = None
    source_name: Optional[str] = None
    category: Optional[str] = None
    assigned_status: Optional[str] = None # "assigned", "unassigned", "all"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    page_size: int = 20
