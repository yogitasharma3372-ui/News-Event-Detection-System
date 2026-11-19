"""
Article management and search API endpoints.
"""
import json
import math
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.article import Article
from backend.app.schemas.article import ArticleResponse, ArticleListResponse
from backend.app.services.article_service import ArticleService
from backend.app.ingestion.file_provider import FileDatasetProvider

router = APIRouter(prefix="/articles", tags=["Articles"])
file_provider = FileDatasetProvider()


@router.get("", response_model=ArticleListResponse)
def list_articles(
    search: Optional[str] = Query(None, description="Keyword search in headline or body"),
    source_name: Optional[str] = Query(None, description="Filter by publisher/source"),
    category: Optional[str] = Query(None, description="Filter by category"),
    assigned_status: Optional[str] = Query(None, description="'assigned', 'unassigned', or 'all'"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = ArticleService(db)
    items, total = service.list_articles(
        search=search,
        source_name=source_name,
        category=category,
        assigned_status=assigned_status,
        start_date=start_date,
        end_date=end_date,
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


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: str, db: Session = Depends(get_db)):
    service = ArticleService(db)
    article = service.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found.")
    return article


@router.post("/validate-upload")
async def validate_upload(
    file: UploadFile = File(...),
):
    """
    Dry-run validation of uploaded CSV or JSON file before committing to database.
    Returns preview of parsed rows, validation errors, and duplicate count.
    """
    content = await file.read()
    try:
        report = file_provider.parse_and_validate(content, file.filename)
        # Exclude full article list from preview response to conserve bandwidth
        return {
            "filename": file.filename,
            "total_rows": report["total_rows"],
            "valid_rows": report["valid_rows"],
            "invalid_rows": report["invalid_rows"],
            "duplicate_rows": report["duplicate_rows"],
            "errors": report["errors"],
            "preview": report["preview"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import")
async def import_articles_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Import and persist validated news articles from CSV or JSON file.
    """
    content = await file.read()
    try:
        report = file_provider.parse_and_validate(content, file.filename)
        valid_records = report["valid_articles"]
        
        service = ArticleService(db)
        result = service.import_articles_batch(valid_records)

        return {
            "status": "success",
            "filename": file.filename,
            "inserted": result["inserted"],
            "skipped_duplicates": result["skipped"] + report["duplicate_rows"],
            "invalid_rows": report["invalid_rows"],
            "errors": report["errors"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import-fixture")
def import_fixture_dataset(db: Session = Depends(get_db)):
    """
    One-click import of the verified test fixture dataset (14 articles across 4 events + noise).
    """
    import os
    fixture_path = "./data/fixtures/test_news_events.json"
    if not os.path.exists(fixture_path):
        raise HTTPException(status_code=404, detail="Fixture dataset file not found.")

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        item["published_at"] = datetime.fromisoformat(item["published_at"].replace("Z", "+00:00"))

    service = ArticleService(db)
    result = service.import_articles_batch(data)

    return {
        "status": "success",
        "dataset": "test_news_events.json",
        "inserted": result["inserted"],
        "skipped_duplicates": result["skipped"]
    }
