"""
Event Clustering Engine supporting batch agglomerative clustering and incremental assignment.
Distinguishes genuine event clusters from singleton noise articles.
"""
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.cluster import AgglomerativeClustering


class EventClusterer:
    """
    Executes distance-thresholded Agglomerative Clustering on precomputed similarity matrices.
    """
    def __init__(self, similarity_threshold: float = 0.60, min_cluster_size: int = 2):
        self.similarity_threshold = float(similarity_threshold)
        self.min_cluster_size = min_cluster_size
        self.distance_threshold = float(1.0 - self.similarity_threshold)

    def cluster_similarity_matrix(self, sim_matrix: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Cluster N items from their pairwise similarity matrix.
        Returns:
            cluster_labels: 1D array of cluster IDs (-1 indicates unassigned noise)
            summary_stats: metadata containing counts of clusters, singletons, etc.
        """
        n = sim_matrix.shape[0]
        if n == 0:
            return np.array([], dtype=int), {"total_clusters": 0, "noise_count": 0}
        if n == 1:
            # Single article is unassigned noise or singleton
            return np.array([-1], dtype=int), {"total_clusters": 0, "noise_count": 1}

        # Convert similarity to distance matrix: D = 1 - S, bounded in [0, 1]
        dist_matrix = np.clip(1.0 - sim_matrix, 0.0, 1.0)
        # Ensure diagonal is zero
        np.fill_diagonal(dist_matrix, 0.0)

        clustering = AgglomerativeClustering(
            metric="precomputed",
            linkage="average",
            distance_threshold=self.distance_threshold,
            n_clusters=None
        )
        raw_labels = clustering.fit_predict(dist_matrix)

        # Count cluster sizes
        unique_labels, counts = np.unique(raw_labels, return_counts=True)
        size_map = dict(zip(unique_labels, counts))

        # Assign -1 (noise) to clusters smaller than min_cluster_size
        final_labels = np.zeros(n, dtype=int)
        valid_cluster_mapping = {}
        next_cid = 0

        for idx, lbl in enumerate(raw_labels):
            if size_map[lbl] < self.min_cluster_size:
                final_labels[idx] = -1 # Noise / unassigned singleton
            else:
                if lbl not in valid_cluster_mapping:
                    valid_cluster_mapping[lbl] = next_cid
                    next_cid += 1
                final_labels[idx] = valid_cluster_mapping[lbl]

        noise_count = int(np.sum(final_labels == -1))
        total_clusters = len(valid_cluster_mapping)

        stats = {
            "total_items": n,
            "total_clusters": total_clusters,
            "noise_count": noise_count,
            "distance_threshold": self.distance_threshold,
            "similarity_threshold": self.similarity_threshold
        }
        return final_labels, stats

    def assign_incremental(
        self,
        candidate_scores: Dict[str, float]
    ) -> Tuple[Optional[str], float]:
        """
        Evaluate candidate existing events for an incoming article.
        Returns:
            (best_event_id, confidence) if max score >= similarity_threshold
            (None, max_score) if no existing event meets the threshold
        """
        if not candidate_scores:
            return None, 0.0

        best_event_id = max(candidate_scores, key=candidate_scores.get)
        best_score = candidate_scores[best_event_id]

        if best_score >= self.similarity_threshold:
            return best_event_id, float(best_score)
        return None, float(best_score)
