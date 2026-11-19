"""
SQLAlchemy Event model representing detected clusters of related news articles.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, utc_now


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    first_observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    last_observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    category: Mapped[str] = mapped_column(String(64), default="Unclassified", nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False, index=True) # active, quiet, historical
    
    article_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    
    # Model provenance
    model_version: Mapped[str] = mapped_column(String(64), default="initial", nullable=False)
    assignment_method: Mapped[str] = mapped_column(String(64), default="hybrid", nullable=False)
    
    # Dominant entities JSON (e.g. {"persons": [...], "orgs": [...], "locs": [...]})
    key_entities_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    articles = relationship("Article", back_populates="event")
    assignments = relationship("EventAssignment", back_populates="event", cascade="all, delete-orphan")
