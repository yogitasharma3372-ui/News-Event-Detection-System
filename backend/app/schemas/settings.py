"""
Pydantic schemas for application settings and model parameters.
"""
from typing import Dict, Any
from pydantic import BaseModel, Field


class SystemSettingsUpdate(BaseModel):
    default_embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2")
    alpha_semantic: float = Field(0.55, ge=0.0, le=1.0)
    beta_temporal: float = Field(0.25, ge=0.0, le=1.0)
    gamma_entity: float = Field(0.20, ge=0.0, le=1.0)
    similarity_threshold: float = Field(0.60, ge=0.0, le=1.0)
    temporal_decay_hours: float = Field(72.0, gt=0.0)
    newsapi_key: str = Field("", description="Optional NewsAPI key (stored safely)")


class SystemSettingsResponse(BaseModel):
    settings: Dict[str, Any]
    weights_valid: bool
    description: str
