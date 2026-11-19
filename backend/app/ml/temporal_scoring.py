"""
Temporal proximity and decay scoring model.
Implements exponential temporal decay: S_temporal = exp(-delta_hours / tau_hours).
"""
import math
from datetime import datetime
from typing import Optional, List
import numpy as np


class TemporalScorer:
    """
    Computes time-aware similarity scores between articles based on publication timestamps.
    Articles published close together have a temporal score near 1.0;
    as time delta increases, score smoothly decays towards 0.0.
    """
    def __init__(self, decay_hours: float = 72.0):
        if decay_hours <= 0:
            raise ValueError("decay_hours parameter must be greater than zero.")
        self.decay_hours = decay_hours

    def compute_temporal_score(self, dt1: Optional[datetime], dt2: Optional[datetime]) -> float:
        """
        Calculate exponential decay score between two timestamps:
        score = exp( - |t1 - t2| / tau )
        If either timestamp is missing, returns neutral prior of 0.5.
        """
        if dt1 is None or dt2 is None:
            return 0.5

        delta_seconds = abs((dt1 - dt2).total_seconds())
        delta_hours = delta_seconds / 3600.0

        score = math.exp(-delta_hours / self.decay_hours)
        return float(np.clip(score, 0.0, 1.0))

    def compute_temporal_matrix(self, timestamps: List[Optional[datetime]]) -> np.ndarray:
        """
        Compute N x N pairwise temporal proximity matrix.
        """
        n = len(timestamps)
        if n == 0:
            return np.empty((0, 0), dtype=float)

        matrix = np.ones((n, n), dtype=float)
        for i in range(n):
            for j in range(i + 1, n):
                score = self.compute_temporal_score(timestamps[i], timestamps[j])
                matrix[i, j] = score
                matrix[j, i] = score

        return matrix
