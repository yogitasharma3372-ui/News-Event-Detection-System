"""
CLI script to execute the 4-way ablation comparative study.
Usage:
    python scripts/evaluate_models.py
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.db.session import init_db, SessionLocal
from backend.app.services.experiment_service import ExperimentService


def main():
    init_db()
    db = SessionLocal()
    service = ExperimentService(db)

    print("Running 4-Way Ablation Benchmark Comparison...")
    results = service.run_ablation_comparison(similarity_threshold=0.60, decay_hours=72.0)

    print("\n" + "="*80)
    print(f"{'Model Variant':<25} | {'B-cubed F1':<10} | {'Precision':<10} | {'Recall':<10} | {'ARI':<8} | {'NMI':<8}")
    print("="*80)
    for r in results:
        m = r["metrics"]
        print(f"{r['configuration_name']:<25} | {m['bcubed_f1']*100:>8.1f}% | {m['bcubed_precision']*100:>8.1f}% | {m['bcubed_recall']*100:>8.1f}% | {m['adjusted_rand_index']:>8.3f} | {m['normalized_mutual_info']:>8.3f}")
    print("="*80)
    db.close()


if __name__ == "__main__":
    main()
