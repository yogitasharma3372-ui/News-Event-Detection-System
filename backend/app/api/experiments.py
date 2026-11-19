"""
Research Experiments API endpoints.
"""
import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.experiment import Experiment
from backend.app.schemas.experiment import ExperimentRunRequest, ExperimentResponse
from backend.app.services.experiment_service import ExperimentService

router = APIRouter(prefix="/experiments", tags=["Research Experiments"])


@router.get("", response_model=List[ExperimentResponse])
def list_experiments(db: Session = Depends(get_db)):
    service = ExperimentService(db)
    experiments = service.list_experiments()
    results = []
    for exp in experiments:
        params = json.loads(exp.parameters_json) if exp.parameters_json else {}
        metrics = json.loads(exp.metrics_json) if exp.metrics_json else None
        results.append({
            "id": exp.id,
            "name": exp.name,
            "dataset_name": exp.dataset_name,
            "algorithm": exp.algorithm,
            "parameters": params,
            "metrics": metrics,
            "status": exp.status,
            "runtime_seconds": exp.runtime_seconds,
            "evaluated_articles_count": exp.evaluated_articles_count,
            "reference_clusters_count": exp.reference_clusters_count,
            "detected_clusters_count": exp.detected_clusters_count,
            "error_message": exp.error_message,
            "start_time": exp.start_time,
            "end_time": exp.end_time
        })
    return results


@router.post("", response_model=ExperimentResponse)
def create_and_run_experiment(request: ExperimentRunRequest, db: Session = Depends(get_db)):
    service = ExperimentService(db)
    try:
        exp = service.run_experiment(
            name=request.name,
            dataset_name=request.dataset_name,
            algorithm=request.algorithm,
            alpha=request.alpha_semantic,
            beta=request.beta_temporal,
            gamma=request.gamma_entity,
            similarity_threshold=request.similarity_threshold,
            decay_hours=request.temporal_decay_hours,
            embedding_model=request.embedding_model
        )

        params = json.loads(exp.parameters_json) if exp.parameters_json else {}
        metrics = json.loads(exp.metrics_json) if exp.metrics_json else None

        return {
            "id": exp.id,
            "name": exp.name,
            "dataset_name": exp.dataset_name,
            "algorithm": exp.algorithm,
            "parameters": params,
            "metrics": metrics,
            "status": exp.status,
            "runtime_seconds": exp.runtime_seconds,
            "evaluated_articles_count": exp.evaluated_articles_count,
            "reference_clusters_count": exp.reference_clusters_count,
            "detected_clusters_count": exp.detected_clusters_count,
            "error_message": exp.error_message,
            "start_time": exp.start_time,
            "end_time": exp.end_time
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    service = ExperimentService(db)
    exp = service.get_experiment_by_id(experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail=f"Experiment '{experiment_id}' not found.")
    params = json.loads(exp.parameters_json) if exp.parameters_json else {}
    metrics = json.loads(exp.metrics_json) if exp.metrics_json else None
    return {
        "id": exp.id,
        "name": exp.name,
        "dataset_name": exp.dataset_name,
        "algorithm": exp.algorithm,
        "parameters": params,
        "metrics": metrics,
        "status": exp.status,
        "runtime_seconds": exp.runtime_seconds,
        "evaluated_articles_count": exp.evaluated_articles_count,
        "reference_clusters_count": exp.reference_clusters_count,
        "detected_clusters_count": exp.detected_clusters_count,
        "error_message": exp.error_message,
        "start_time": exp.start_time,
        "end_time": exp.end_time
    }
