"""
Pydantic schemas for live ingestion jobs and provider configurations.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class IngestionJobCreate(BaseModel):
    provider: str = Field(..., description="'rss' or 'newsapi'")
    query: Optional[str] = Field(None, description="Topic keyword or query")
    feed_url: Optional[str] = Field(None, description="Custom RSS/Atom feed URL")
    max_articles: int = Field(25, ge=1, le=100)


class IngestionJobResponse(BaseModel):
    id: str
    provider: str
    query: Optional[str] = None
    status: str
    articles_fetched: int
    articles_inserted: int
    duplicates_skipped: int
    failures: int
    error_summary: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DatasetValidationReport(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    errors: List[str] = []
    preview: List[dict] = []
