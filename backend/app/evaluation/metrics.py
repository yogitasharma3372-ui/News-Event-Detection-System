"""
Evaluation metrics implementation for story and news event clustering.
Implements B-cubed (Precision, Recall, F1), Adjusted Rand Index (ARI),
Normalized Mutual Information (NMI), and pairwise clustering metrics.
"""
from typing import Dict, List, Any, Optional
import numpy as np
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score


def compute_bcubed_metrics(
    true_labels: List[Any],
    pred_labels: List[Any],
    noise_label: Any = -1
) -> Dict[str, float]:
    """
    Compute B-cubed Precision, Recall, and F1 score.
    
    Mathematical definition:
    For each item i:
      Let C(i) be the set of items in the same predicted cluster as i.
      Let L(i) be the set of items in the same reference (ground truth) cluster as i.
      Precision_i = |C(i) ∩ L(i)| / |C(i)|
      Recall_i    = |C(i) ∩ L(i)| / |L(i)|
    
    Overall Precision = (1 / N) * sum(Precision_i)
    Overall Recall    = (1 / N) * sum(Recall_i)
    B-cubed F1        = 2 * Precision * Recall / (Precision + Recall)
    
    Note on noise handling:
    If an item has true_label = None or pred_label = noise_label (-1),
    it is treated as a unique singleton cluster of size 1 so that noise items
    are never falsely merged into a single collective cluster.
    """
    n = len(true_labels)
    if n == 0 or len(pred_labels) != n:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    # Normalize true labels and predicted labels to handle noise / singletons
    norm_true: List[str] = []
    norm_pred: List[str] = []

    for i in range(n):
        t = true_labels[i]
        p = pred_labels[i]
        
        # Ground truth: if None or empty, assign a unique singleton ID
        if t is None or t == "" or t == -1:
            norm_true.append(f"__true_singleton_{i}__")
        else:
            norm_true.append(str(t))

        # Predicted: if noise label, assign a unique singleton ID
        if p == noise_label or p is None or p == "":
            norm_pred.append(f"__pred_singleton_{i}__")
        else:
            norm_pred.append(str(p))

    # Precompute cluster membership sets for efficiency
    pred_clusters: Dict[str, set] = {}
    true_clusters: Dict[str, set] = {}

    for idx, (p, t) in enumerate(zip(norm_pred, norm_true)):
        pred_clusters.setdefault(p, set()).add(idx)
        true_clusters.setdefault(t, set()).add(idx)

    precisions = []
    recalls = []

    for i in range(n):
        c_i = pred_clusters[norm_pred[i]]
        l_i = true_clusters[norm_true[i]]

        intersection_size = len(c_i & l_i)
        prec_i = intersection_size / len(c_i)
        rec_i = intersection_size / len(l_i)

        precisions.append(prec_i)
        recalls.append(rec_i)

    precision = float(np.mean(precisions))
    recall = float(np.mean(recalls))

    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = float(2 * precision * recall / (precision + recall))

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }


def compute_pairwise_metrics(
    true_labels: List[Any],
    pred_labels: List[Any],
    noise_label: Any = -1
) -> Dict[str, float]:
    """
    Compute pair-level precision, recall, and F1 score across all N*(N-1)/2 item pairs.
    """
    n = len(true_labels)
    if n < 2 or len(pred_labels) != n:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    # Normalize singletons
    norm_true = [f"__true_{i}__" if t is None or t == "" or t == -1 else str(t) for i, t in enumerate(true_labels)]
    norm_pred = [f"__pred_{i}__" if p == noise_label or p is None or p == "" else str(p) for i, p in enumerate(pred_labels)]

    tp = 0
    fp = 0
    fn = 0

    for i in range(n):
        for j in range(i + 1, n):
            same_true = (norm_true[i] == norm_true[j])
            same_pred = (norm_pred[i] == norm_pred[j])

            if same_pred and same_true:
                tp += 1
            elif same_pred and not same_true:
                fp += 1
            elif not same_pred and same_true:
                fn += 1

    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }


def compute_clustering_metrics(
    true_labels: List[Any],
    pred_labels: List[Any],
    runtime_seconds: float = 0.0,
    noise_label: Any = -1
) -> Dict[str, Any]:
    """
    Compute complete suite of research evaluation metrics:
    B-cubed (P/R/F1), ARI, NMI, and Pairwise (P/R/F1).
    """
    n = len(true_labels)
    if n == 0:
        return {
            "bcubed_precision": 0.0,
            "bcubed_recall": 0.0,
            "bcubed_f1": 0.0,
            "adjusted_rand_index": 0.0,
            "normalized_mutual_info": 0.0,
            "pairwise_precision": 0.0,
            "pairwise_recall": 0.0,
            "pairwise_f1": 0.0,
            "evaluated_articles_count": 0,
            "reference_clusters_count": 0,
            "detected_clusters_count": 0,
            "runtime_seconds": round(runtime_seconds, 4)
        }

    bcubed = compute_bcubed_metrics(true_labels, pred_labels, noise_label=noise_label)
    pairwise = compute_pairwise_metrics(true_labels, pred_labels, noise_label=noise_label)

    # Convert to integer categorical IDs for ARI and NMI
    norm_true = [f"__t_{i}__" if t is None or t == "" or t == -1 else str(t) for i, t in enumerate(true_labels)]
    norm_pred = [f"__p_{i}__" if p == noise_label or p is None or p == "" else str(p) for i, p in enumerate(pred_labels)]

    ari = float(adjusted_rand_score(norm_true, norm_pred))
    nmi = float(normalized_mutual_info_score(norm_true, norm_pred))

    ref_clusters = len(set(norm_true))
    det_clusters = len(set(norm_pred))

    return {
        "bcubed_precision": bcubed["precision"],
        "bcubed_recall": bcubed["recall"],
        "bcubed_f1": bcubed["f1"],
        "adjusted_rand_index": round(ari, 4),
        "normalized_mutual_info": round(nmi, 4),
        "pairwise_precision": pairwise["precision"],
        "pairwise_recall": pairwise["recall"],
        "pairwise_f1": pairwise["f1"],
        "evaluated_articles_count": n,
        "reference_clusters_count": ref_clusters,
        "detected_clusters_count": det_clusters,
        "runtime_seconds": round(runtime_seconds, 4)
    }
