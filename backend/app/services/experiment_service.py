"""
Research Experiment Service.
Executes research pipelines, evaluates metrics on ground truth datasets,
and logs reproducible experiment artifacts in SQLite.
"""
import uuid
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.experiment import Experiment
from backend.app.models.article import Article
from backend.app.evaluation.evaluator import ResearchEvaluator


class ExperimentService:
    def __init__(self, db: Session):
        self.db = db
        self.evaluator = ResearchEvaluator()

    def list_experiments(self) -> List[Experiment]:
        return self.db.query(Experiment).order_by(desc(Experiment.start_time)).all()

    def get_experiment_by_id(self, exp_id: str) -> Optional[Experiment]:
        return self.db.query(Experiment).filter(Experiment.id == exp_id).first()

    def run_experiment(
        self,
        name: str,
        dataset_name: str = "default",
        algorithm: str = "hybrid",
        alpha: float = 0.55,
        beta: float = 0.25,
        gamma: float = 0.20,
        similarity_threshold: float = 0.60,
        decay_hours: float = 72.0,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> Experiment:
        """
        Run an experiment against benchmark articles and record quantitative results.
        """
        exp_id = f"exp-{uuid.uuid4().hex[:10]}"
        params = {
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma,
            "similarity_threshold": similarity_threshold,
            "decay_hours": decay_hours,
            "embedding_model": embedding_model
        }

        # Query benchmark articles from DB
        articles = self.db.query(Article).all()
        article_dicts = [
            {
                "id": a.id,
                "headline": a.headline,
                "body": a.body,
                "published_at": a.published_at,
                "content_hash": a.content_hash,
                "ground_truth_event_id": a.ground_truth_event_id,
                "entities": json.loads(a.entities_json).get("all", []) if a.entities_json else []
            }
            for a in articles
        ]

        if not article_dicts:
            # Fallback to test fixture if database is currently empty
            import os
            fixture_path = "./data/fixtures/test_news_events.json"
            if os.path.exists(fixture_path):
                with open(fixture_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    for item in raw_data:
                        item["published_at"] = datetime.fromisoformat(item["published_at"].replace("Z", "+00:00"))
                        item["content_hash"] = str(hash(item["headline"]))
                    article_dicts = raw_data

        exp = Experiment(
            id=exp_id,
            name=name,
            dataset_name=dataset_name,
            algorithm=algorithm,
            parameters_json=json.dumps(params),
            status="running",
            start_time=datetime.now(timezone.utc)
        )
        self.db.add(exp)
        self.db.commit()

        try:
            result = self.evaluator.run_experiment(
                articles=article_dicts,
                algorithm=algorithm,
                alpha=alpha,
                beta=beta,
                gamma=gamma,
                similarity_threshold=similarity_threshold,
                decay_hours=decay_hours,
                embedding_model_name=embedding_model
            )

            metrics = result.get("metrics", {})
            exp.metrics_json = json.dumps(metrics)
            exp.status = "completed"
            exp.runtime_seconds = result.get("runtime_seconds")
            exp.evaluated_articles_count = metrics.get("evaluated_articles_count", len(article_dicts))
            exp.reference_clusters_count = metrics.get("reference_clusters_count", 0)
            exp.detected_clusters_count = metrics.get("detected_clusters_count", 0)
            exp.end_time = datetime.now(timezone.utc)
            self.db.commit()

        except Exception as e:
            exp.status = "failed"
            exp.error_message = str(e)
            exp.end_time = datetime.now(timezone.utc)
            self.db.commit()

        return exp

    def run_ablation_comparison(
        self,
        similarity_threshold: float = 0.60,
        decay_hours: float = 72.0
    ) -> List[Dict[str, Any]]:
        """
        Runs the 4-way ablation benchmark and returns side-by-side comparative metrics.
        """
        articles = self.db.query(Article).all()
        article_dicts = [
            {
                "id": a.id,
                "headline": a.headline,
                "body": a.body,
                "published_at": a.published_at,
                "content_hash": a.content_hash,
                "ground_truth_event_id": a.ground_truth_event_id,
                "entities": json.loads(a.entities_json).get("all", []) if a.entities_json else []
            }
            for a in articles
        ]
        if not article_dicts:
            import os
            fixture_path = "./data/fixtures/test_news_events.json"
            if os.path.exists(fixture_path):
                with open(fixture_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    for item in raw_data:
                        item["published_at"] = datetime.fromisoformat(item["published_at"].replace("Z", "+00:00"))
                        item["content_hash"] = str(hash(item["headline"]))
                    article_dicts = raw_data

        return self.evaluator.run_ablation_study(
            articles=article_dicts,
            similarity_threshold=similarity_threshold,
            decay_hours=decay_hours
        )
