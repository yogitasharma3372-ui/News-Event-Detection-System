"""
Research experiment orchestrator and ablation study runner.
Executes baseline models and proposed hybrid methods on benchmark datasets
and collects empirical performance metrics.
"""
import time
from typing import List, Dict, Any, Optional
import numpy as np

from backend.app.ml.tfidf_model import TfidfBaselineModel
from backend.app.ml.embedding_model import SemanticEmbeddingModel
from backend.app.ml.ner_extractor import EntityExtractor
from backend.app.ml.temporal_scoring import TemporalScorer
from backend.app.ml.hybrid_scorer import HybridScorer
from backend.app.ml.clusterer import EventClusterer
from backend.app.evaluation.metrics import compute_clustering_metrics


class ResearchEvaluator:
    """
    Standardized research evaluation runner for news event detection experiments.
    """
    def __init__(self, embedding_cache_dir: str = "./data/cache/embeddings"):
        self.embedding_cache_dir = embedding_cache_dir
        self.tfidf_model = TfidfBaselineModel()
        self.ner_extractor = EntityExtractor()

    def run_experiment(
        self,
        articles: List[Dict[str, Any]],
        algorithm: str = "hybrid",
        alpha: float = 0.55,
        beta: float = 0.25,
        gamma: float = 0.20,
        similarity_threshold: float = 0.60,
        decay_hours: float = 72.0,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> Dict[str, Any]:
        """
        Execute an experiment on a dataset and return quantitative metrics.
        Articles must contain: headline, body, published_at, content_hash, and optionally ground_truth_event_id.
        """
        start_time = time.time()
        n = len(articles)
        if n == 0:
            return {"error": "Cannot evaluate on empty dataset."}

        texts = [f"{a.get('headline', '')}. {a.get('body', '')}" for a in articles]
        hashes = [a.get("content_hash", str(hash(t))) for a, t in zip(articles, texts)]
        timestamps = [a.get("published_at") for a in articles]
        true_labels = [a.get("ground_truth_event_id") for a in articles]

        clusterer = EventClusterer(similarity_threshold=similarity_threshold, min_cluster_size=2)

        # 1. Compute similarity matrix according to algorithm
        if algorithm == "tfidf":
            sim_matrix = self.tfidf_model.compute_similarity_matrix(texts)

        elif algorithm == "semantic":
            embed_model = SemanticEmbeddingModel(model_name=embedding_model_name, cache_dir=self.embedding_cache_dir)
            embeddings = embed_model.encode_batch(texts, hashes)
            sim_matrix = embed_model.compute_similarity_matrix(embeddings)

        elif algorithm == "hybrid" or algorithm.startswith("ablation"):
            # Compute semantic component
            embed_model = SemanticEmbeddingModel(model_name=embedding_model_name, cache_dir=self.embedding_cache_dir)
            embeddings = embed_model.encode_batch(texts, hashes)
            semantic_matrix = embed_model.compute_similarity_matrix(embeddings)

            # Compute temporal component
            temporal_scorer = TemporalScorer(decay_hours=decay_hours)
            temporal_matrix = temporal_scorer.compute_temporal_matrix(timestamps)

            # Compute entity overlap component
            entity_matrix = np.ones((n, n), dtype=float)
            all_entities = []
            for art in articles:
                # Use cached entities if available
                if art.get("entities") and isinstance(art["entities"], list):
                    all_entities.append(art["entities"])
                else:
                    ext = self.ner_extractor.extract_entities(f"{art.get('headline', '')} {art.get('body', '')}")
                    all_entities.append(ext["all"])

            for i in range(n):
                for j in range(i + 1, n):
                    score = self.ner_extractor.compute_jaccard_similarity(all_entities[i], all_entities[j])
                    entity_matrix[i, j] = score
                    entity_matrix[j, i] = score

            # Combine using weights
            hybrid_scorer = HybridScorer(alpha=alpha, beta=beta, gamma=gamma)
            sim_matrix = hybrid_scorer.compute_combined_matrix(semantic_matrix, temporal_matrix, entity_matrix)

        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        # 2. Cluster
        pred_labels, cluster_stats = clusterer.cluster_similarity_matrix(sim_matrix)
        runtime = time.time() - start_time

        # 3. Compute metrics if ground truth labels are present
        has_ground_truth = any(l is not None for l in true_labels)
        if has_ground_truth:
            metrics = compute_clustering_metrics(true_labels, pred_labels, runtime_seconds=runtime)
        else:
            metrics = {
                "bcubed_precision": None,
                "bcubed_recall": None,
                "bcubed_f1": None,
                "adjusted_rand_index": None,
                "normalized_mutual_info": None,
                "evaluated_articles_count": n,
                "reference_clusters_count": 0,
                "detected_clusters_count": cluster_stats["total_clusters"],
                "runtime_seconds": round(runtime, 4)
            }

        return {
            "algorithm": algorithm,
            "parameters": {
                "alpha": alpha,
                "beta": beta,
                "gamma": gamma,
                "similarity_threshold": similarity_threshold,
                "decay_hours": decay_hours,
                "embedding_model": embedding_model_name
            },
            "metrics": metrics,
            "cluster_stats": cluster_stats,
            "runtime_seconds": round(runtime, 4),
            "predicted_labels": pred_labels.tolist()
        }

    def run_ablation_study(
        self,
        articles: List[Dict[str, Any]],
        similarity_threshold: float = 0.60,
        decay_hours: float = 72.0
    ) -> List[Dict[str, Any]]:
        """
        Execute standard 4-way ablation study:
        1. Semantic similarity only (alpha=1.0, beta=0.0, gamma=0.0)
        2. Semantic + Temporal (alpha=0.70, beta=0.30, gamma=0.0)
        3. Semantic + Entity (alpha=0.75, beta=0.0, gamma=0.25)
        4. Proposed Full Hybrid (alpha=0.55, beta=0.25, gamma=0.20)
        """
        ablation_configs = [
            {
                "name": "Semantic Only",
                "alpha": 1.0, "beta": 0.0, "gamma": 0.0,
                "description": "Baseline semantic cosine similarity alone"
            },
            {
                "name": "Semantic + Time",
                "alpha": 0.70, "beta": 0.30, "gamma": 0.0,
                "description": "Semantic similarity regularized with exponential temporal decay"
            },
            {
                "name": "Semantic + Entity",
                "alpha": 0.75, "beta": 0.0, "gamma": 0.25,
                "description": "Semantic similarity regularized with named-entity Jaccard overlap"
            },
            {
                "name": "Proposed Full Hybrid",
                "alpha": 0.55, "beta": 0.25, "gamma": 0.20,
                "description": "Unified semantic, temporal decay, and entity overlap model"
            }
        ]

        results = []
        for cfg in ablation_configs:
            res = self.run_experiment(
                articles=articles,
                algorithm="hybrid",
                alpha=cfg["alpha"],
                beta=cfg["beta"],
                gamma=cfg["gamma"],
                similarity_threshold=similarity_threshold,
                decay_hours=decay_hours
            )
            res["configuration_name"] = cfg["name"]
            res["description"] = cfg["description"]
            results.append(res)

        return results
