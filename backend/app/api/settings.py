"""
System configuration and parameter tuning API endpoints.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import numpy as np

from backend.app.db.session import get_db
from backend.app.schemas.settings import SystemSettingsUpdate, SystemSettingsResponse
from backend.app.models.system_setting import SystemSetting
from backend.app.core.config import settings

router = APIRouter(prefix="/settings", tags=["Settings & Configuration"])


@router.get("", response_model=SystemSettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    # Retrieve persisted overrides if available
    db_settings = {}
    for row in db.query(SystemSetting).all():
        db_settings[row.key] = row.value

    alpha = float(db_settings.get("alpha_semantic", settings.DEFAULT_ALPHA_SEMANTIC))
    beta = float(db_settings.get("beta_temporal", settings.DEFAULT_BETA_TEMPORAL))
    gamma = float(db_settings.get("gamma_entity", settings.DEFAULT_GAMMA_ENTITY))
    model = db_settings.get("default_embedding_model", settings.DEFAULT_EMBEDDING_MODEL)
    threshold = float(db_settings.get("similarity_threshold", settings.DEFAULT_SIMILARITY_THRESHOLD))
    decay = float(db_settings.get("temporal_decay_hours", settings.DEFAULT_TEMPORAL_DECAY_HOURS))

    weights_sum = alpha + beta + gamma
    is_valid = np.isclose(weights_sum, 1.0, atol=1e-3)

    return {
        "settings": {
            "default_embedding_model": model,
            "alpha_semantic": alpha,
            "beta_temporal": beta,
            "gamma_entity": gamma,
            "similarity_threshold": threshold,
            "temporal_decay_hours": decay,
            "has_newsapi_key": bool(settings.NEWSAPI_KEY)
        },
        "weights_valid": is_valid,
        "description": "Configures hybrid clustering weights (alpha + beta + gamma = 1.0), distance thresholds, and embedding models."
    }


@router.put("", response_model=SystemSettingsResponse)
def update_settings(update: SystemSettingsUpdate, db: Session = Depends(get_db)):
    weights_sum = update.alpha_semantic + update.beta_temporal + update.gamma_entity
    if not np.isclose(weights_sum, 1.0, atol=1e-3):
        raise HTTPException(
            status_code=400,
            detail=f"Hybrid weights must sum to 1.0 (got {weights_sum:.4f})."
        )

    # Persist in system_settings table
    to_save = {
        "default_embedding_model": (update.default_embedding_model, "Default sentence transformer model"),
        "alpha_semantic": (str(update.alpha_semantic), "Weight for semantic embedding cosine similarity"),
        "beta_temporal": (str(update.beta_temporal), "Weight for exponential temporal decay"),
        "gamma_entity": (str(update.gamma_entity), "Weight for named-entity Jaccard overlap"),
        "similarity_threshold": (str(update.similarity_threshold), "Minimum hybrid similarity to merge into event cluster"),
        "temporal_decay_hours": (str(update.temporal_decay_hours), "Half-decay window in hours for temporal scoring")
    }

    for key, (val, desc) in to_save.items():
        existing = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if existing:
            existing.value = val
        else:
            db.add(SystemSetting(key=key, value=val, description=desc))

    if update.newsapi_key:
        settings.NEWSAPI_KEY = update.newsapi_key

    db.commit()

    return {
        "settings": {
            "default_embedding_model": update.default_embedding_model,
            "alpha_semantic": update.alpha_semantic,
            "beta_temporal": update.beta_temporal,
            "gamma_entity": update.gamma_entity,
            "similarity_threshold": update.similarity_threshold,
            "temporal_decay_hours": update.temporal_decay_hours,
            "has_newsapi_key": bool(settings.NEWSAPI_KEY)
        },
        "weights_valid": True,
        "description": "Settings successfully updated and persisted."
    }
