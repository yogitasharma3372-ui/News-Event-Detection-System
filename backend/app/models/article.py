"""
SQLAlchemy Article model representing raw and processed news stories.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, utc_now


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    headline: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    language: Mapped[str] = mapped_column(String(16), default="en", nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    
    # Event clustering association
    assigned_event_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("events.id"), nullable=True, index=True)
    ground_truth_event_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    
    # Extracted entity metadata and categories (JSON-encoded strings for SQLite portability)
    entities_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    
    # Processing pipeline status
    processing_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    event = relationship("Event", back_populates="articles")
    assignments = relationship("EventAssignment", back_populates="article", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_articles_published_source", "published_at", "source_name"),
    )
