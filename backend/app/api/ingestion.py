"""
Live News Ingestion API endpoints.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.ingestion import IngestionJobCreate, IngestionJobResponse
from backend.app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/ingestion", tags=["Live Ingestion"])


@router.get("/jobs", response_model=List[IngestionJobResponse])
def list_ingestion_jobs(db: Session = Depends(get_db)):
    service = IngestionService(db)
    return service.list_jobs()


@router.post("/jobs", response_model=IngestionJobResponse)
def trigger_ingestion_job(request: IngestionJobCreate, db: Session = Depends(get_db)):
    service = IngestionService(db)
    try:
        job = service.trigger_ingestion(
            provider=request.provider,
            query=request.query,
            feed_url=request.feed_url,
            max_articles=request.max_articles
        )
        return job
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs/{job_id}", response_model=IngestionJobResponse)
def get_ingestion_job(job_id: str, db: Session = Depends(get_db)):
    service = IngestionService(db)
    job = service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Ingestion job '{job_id}' not found.")
    return job
