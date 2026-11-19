"""
Hybrid Scoring Engine combining semantic, temporal, and entity similarity.
combined_score = alpha * semantic_score + beta * temporal_score + gamma * entity_score
Requires: alpha + beta + gamma = 1.0
"""
from typing import Dict, Any, List, Optional
import numpy as np


class HybridScorer:
    """
    Computes unified pairwise similarity combining semantic similarity,
    temporal proximity, and named entity overlap.
    """
    def __init__(self, alpha: float = 0.55, beta: float = 0.25, gamma: float = 0.20):
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.gamma = float(gamma)
        self.validate_weights()

    def validate_weights(self) -> None:
        """
        Validate that weights are non-negative and sum to 1.0 within numerical tolerance.
        """
        if self.alpha < 0 or self.beta < 0 or self.gamma < 0:
            raise ValueError(f"Weights must be non-negative: alpha={self.alpha}, beta={self.beta}, gamma={self.gamma}")
        total = self.alpha + self.beta + self.gamma
        if not np.isclose(total, 1.0, atol=1e-3):
            raise ValueError(f"Weights alpha ({self.alpha}) + beta ({self.beta}) + gamma ({self.gamma}) must sum to 1.0 (got {total:.4f})")

    def score_pair(self, semantic_score: float, temporal_score: float, entity_score: float) -> float:
        """
        Calculate weighted combined score for an article pair.
        """
        s = np.clip(semantic_score, 0.0, 1.0)
        t = np.clip(temporal_score, 0.0, 1.0)
        e = np.clip(entity_score, 0.0, 1.0)

        combined = (self.alpha * s) + (self.beta * t) + (self.gamma * e)
        return float(np.clip(combined, 0.0, 1.0))

    def compute_combined_matrix(
        self,
        semantic_matrix: np.ndarray,
        temporal_matrix: np.ndarray,
        entity_matrix: np.ndarray
    ) -> np.ndarray:
        """
        Vectorized combination of semantic, temporal, and entity matrices.
        """
        combined = (
            self.alpha * semantic_matrix +
            self.beta * temporal_matrix +
            self.gamma * entity_matrix
        )
        return np.clip(combined, 0.0, 1.0)
