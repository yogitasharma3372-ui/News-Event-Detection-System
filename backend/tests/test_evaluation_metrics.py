"""
Unit tests for research evaluation metrics: B-cubed, ARI, NMI, pairwise.
Verifies against hand-calculated ground truth cases.
"""
import numpy as np
import pytest

from backend.app.evaluation.metrics import (
    compute_bcubed_metrics,
    compute_pairwise_metrics,
    compute_clustering_metrics
)


def test_bcubed_perfect_match():
    # Perfect clustering
    true_labels = ["c1", "c1", "c2", "c2"]
    pred_labels = [0, 0, 1, 1]

    bcubed = compute_bcubed_metrics(true_labels, pred_labels)
    assert bcubed["precision"] == 1.0
    assert bcubed["recall"] == 1.0
    assert bcubed["f1"] == 1.0


def test_bcubed_overclustering():
    # Two true clusters split into four predicted clusters
    true_labels = ["c1", "c1", "c2", "c2"]
    pred_labels = [0, 1, 2, 3]

    bcubed = compute_bcubed_metrics(true_labels, pred_labels)
    # Every predicted cluster has size 1, so precision is 1.0
    assert bcubed["precision"] == 1.0
    # True cluster size is 2, intersection is 1, so recall is 1/2 = 0.5
    assert bcubed["recall"] == 0.5
    # F1 = 2 * (1 * 0.5) / 1.5 = 2/3 ~= 0.6667
    assert np.isclose(bcubed["f1"], 0.6667, atol=1e-3)


def test_bcubed_underclustering():
    # All items merged into one predicted cluster
    true_labels = ["c1", "c1", "c2", "c2"]
    pred_labels = [0, 0, 0, 0]

    bcubed = compute_bcubed_metrics(true_labels, pred_labels)
    # Intersection is 2, predicted size is 4, precision is 2/4 = 0.5
    assert bcubed["precision"] == 0.5
    # Recall is 2/2 = 1.0
    assert bcubed["recall"] == 1.0
    assert np.isclose(bcubed["f1"], 0.6667, atol=1e-3)


def test_bcubed_noise_handling():
    # True noise singleton should not match predicted noise singleton
    true_labels = ["c1", "c1", None, None]
    pred_labels = [0, 0, -1, -1] # -1 is noise

    bcubed = compute_bcubed_metrics(true_labels, pred_labels, noise_label=-1)
    # Predicted noise items are treated as distinct singletons, matching true distinct singletons
    assert bcubed["precision"] == 1.0
    assert bcubed["recall"] == 1.0
    assert bcubed["f1"] == 1.0


def test_pairwise_metrics():
    true_labels = ["c1", "c1", "c2", "c2"]
    pred_labels = [0, 0, 1, 1]

    pairwise = compute_pairwise_metrics(true_labels, pred_labels)
    assert pairwise["precision"] == 1.0
    assert pairwise["recall"] == 1.0
    assert pairwise["f1"] == 1.0


def test_complete_clustering_metrics_suite():
    true_labels = ["event_a", "event_a", "event_b", "event_b", None]
    pred_labels = [1, 1, 2, 2, -1]

    metrics = compute_clustering_metrics(true_labels, pred_labels, runtime_seconds=0.05, noise_label=-1)
    assert metrics["bcubed_f1"] == 1.0
    assert metrics["adjusted_rand_index"] == 1.0
    assert metrics["normalized_mutual_info"] == 1.0
    assert metrics["evaluated_articles_count"] == 5
    assert metrics["detected_clusters_count"] == 3
