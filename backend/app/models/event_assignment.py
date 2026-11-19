"""
SQLAlchemy EventAssignment model logging each article-to-event association.
Preserves audit history and distinguishes automated ML assignments from manual corrections.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, Float, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, utc_now


class EventAssignment(Base):
    __tablename__ = "event_assignments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    article_id: Mapped[str] = mapped_column(String(64), ForeignKey("articles.id"), nullable=False, index=True)
    event_id: Mapped[str] = mapped_column(String(64), ForeignKey("events.id"), nullable=False, index=True)
    
    assignment_method: Mapped[str] = mapped_column(String(64), default="hybrid", nullable=False) # tfidf, semantic, hybrid, manual
    
    semantic_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    temporal_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    entity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    combined_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    model_version: Mapped[str] = mapped_column(String(64), default="1.0.0", nullable=False)
    
    # Manual review protection
    is_manual_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    previous_event_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    article = relationship("Article", back_populates="assignments")
    event = relationship("Event", back_populates="assignments")

    __table_args__ = (
        Index("ix_assignments_art_event", "article_id", "event_id"),
    )
