"""
Evaluation and ablation study API endpoints.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services.experiment_service import ExperimentService

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Ablation"])


@router.post("/ablation")
def run_ablation_study(
    similarity_threshold: float = Query(0.60, ge=0.0, le=1.0),
    decay_hours: float = Query(72.0, gt=0.0),
    db: Session = Depends(get_db)
):
    """
    Execute 4-way ablation benchmark comparison:
    1. Semantic similarity only
    2. Semantic + Temporal decay
    3. Semantic + Entity overlap
    4. Proposed Full Hybrid
    """
    service = ExperimentService(db)
    try:
        results = service.run_ablation_comparison(
            similarity_threshold=similarity_threshold,
            decay_hours=decay_hours
        )
        return {"ablation_results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
