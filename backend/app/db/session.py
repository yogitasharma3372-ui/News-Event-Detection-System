"""
Database engine and session management.
Provides thread-safe SQLite connection and FastAPI dependency injection.
"""
from typing import Generator
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.base import Base

# Ensure parent directory for database exists if using relative path
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///./"):
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./data/cache", exist_ok=True)
    os.makedirs("./data/cache/embeddings", exist_ok=True)

# SQLite specific connect_args to allow multithreading in FastAPI
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all database tables if they do not exist."""
    # Import all models so that Base.metadata has registered tables
    from backend.app.models.article import Article
    from backend.app.models.event import Event
    from backend.app.models.event_assignment import EventAssignment
    from backend.app.models.experiment import Experiment
    from backend.app.models.ingestion_job import IngestionJob
    from backend.app.models.system_setting import SystemSetting
    
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy database session,
    ensuring it is closed after request handling.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
