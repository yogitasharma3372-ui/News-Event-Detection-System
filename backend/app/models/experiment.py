"""
SQLAlchemy Experiment model storing research experiment runs and evaluation metrics.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base, utc_now


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    dataset_name: Mapped[str] = mapped_column(String(128), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(64), nullable=False) # tfidf, semantic, hybrid
    
    # Serialized parameters and metrics
    parameters_json: Mapped[str] = mapped_column(Text, nullable=False) # alpha, beta, gamma, threshold, model
    metrics_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # bcubed_f1, ari, nmi, runtime, etc.
    
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False) # pending, running, completed, failed
    runtime_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    evaluated_articles_count: Mapped[int] = mapped_column(default=0, nullable=False)
    reference_clusters_count: Mapped[int] = mapped_column(default=0, nullable=False)
    detected_clusters_count: Mapped[int] = mapped_column(default=0, nullable=False)
    
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
