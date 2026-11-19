"""
CLI script to execute a research clustering experiment.
Usage:
    python scripts/run_experiment.py --algo hybrid --alpha 0.55 --beta 0.25 --gamma 0.20
"""
import sys
import os
import argparse
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.db.session import init_db, SessionLocal
from backend.app.services.experiment_service import ExperimentService


def main():
    parser = argparse.ArgumentParser(description="Run clustering research experiment.")
    parser.add_argument("--algo", default="hybrid", choices=["tfidf", "semantic", "hybrid"])
    parser.add_argument("--alpha", type=float, default=0.55)
    parser.add_argument("--beta", type=float, default=0.25)
    parser.add_argument("--gamma", type=float, default=0.20)
    parser.add_argument("--threshold", type=float, default=0.60)
    parser.add_argument("--decay", type=float, default=72.0)
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    service = ExperimentService(db)

    print(f"Executing {args.algo.upper()} experiment (alpha={args.alpha}, beta={args.beta}, gamma={args.gamma})...")
    exp = service.run_experiment(
        name=f"CLI {args.algo.upper()} Run",
        algorithm=args.algo,
        alpha=args.alpha,
        beta=args.beta,
        gamma=args.gamma,
        similarity_threshold=args.threshold,
        decay_hours=args.decay
    )

    metrics = json.loads(exp.metrics_json) if exp.metrics_json else {}
    print("\n--- Quantitative Results ---")
    print(f"Status: {exp.status}")
    print(f"B-cubed F1: {metrics.get('bcubed_f1')}")
    print(f"B-cubed Precision: {metrics.get('bcubed_precision')}")
    print(f"B-cubed Recall: {metrics.get('bcubed_recall')}")
    print(f"Adjusted Rand Index (ARI): {metrics.get('adjusted_rand_index')}")
    print(f"Normalized Mutual Info (NMI): {metrics.get('normalized_mutual_info')}")
    print(f"Runtime: {exp.runtime_seconds:.2f}s")
    db.close()


if __name__ == "__main__":
    main()
