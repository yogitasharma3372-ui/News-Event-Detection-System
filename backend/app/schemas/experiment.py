"""
Pydantic schemas for research experiments and evaluation benchmarks.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ExperimentRunRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    dataset_name: str = Field("default", description="Fixture dataset or imported dataset key")
    algorithm: str = Field("hybrid", description="'tfidf', 'semantic', 'hybrid', or ablation names")
    
    # Hybrid parameters
    alpha_semantic: float = Field(0.55, ge=0.0, le=1.0)
    beta_temporal: float = Field(0.25, ge=0.0, le=1.0)
    gamma_entity: float = Field(0.20, ge=0.0, le=1.0)
    
    similarity_threshold: float = Field(0.60, ge=0.0, le=1.0)
    temporal_decay_hours: float = Field(72.0, gt=0.0)
    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2")


class EvaluationMetrics(BaseModel):
    bcubed_precision: float
    bcubed_recall: float
    bcubed_f1: float
    adjusted_rand_index: float
    normalized_mutual_info: float
    pairwise_precision: Optional[float] = None
    pairwise_recall: Optional[float] = None
    pairwise_f1: Optional[float] = None
    evaluated_articles_count: int
    reference_clusters_count: int
    detected_clusters_count: int
    runtime_seconds: float


class ExperimentResponse(BaseModel):
    id: str
    name: str
    dataset_name: str
    algorithm: str
    parameters: Dict[str, Any]
    metrics: Optional[EvaluationMetrics] = None
    status: str
    runtime_seconds: Optional[float] = None
    evaluated_articles_count: int
    reference_clusters_count: int
    detected_clusters_count: int
    error_message: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AblationComparisonResult(BaseModel):
    configurations: List[Dict[str, Any]]
