# Evaluation Protocol and Research Benchmark Metrics

## 1. Overview

This document specifies the exact mathematical metrics, partition standards, and ablation configurations implemented in the News Event Detection and Tracking System.

---

## 2. Clustering Metrics

### 2.1 B-Cubed Metric Suite (Item-Level Evaluation)
Standard cluster purity metrics are frequently biased by cluster size and number of singletons. B-cubed evaluation directly estimates per-item precision and recall:

For every article $i$ in evaluation partition $D$ ($|D| = N$):
- Let $C(i)$ be the set of articles assigned to the same predicted cluster as article $i$.
- Let $L(i)$ be the set of articles assigned to the same reference ground-truth cluster as article $i$.

The per-item precision $P_i$ and recall $R_i$ are:
$$P_i = \frac{|C(i) \cap L(i)|}{|C(i)|}$$
$$R_i = \frac{|C(i) \cap L(i)|}{|L(i)|}$$

Aggregating across the entire dataset:
$$\text{Precision}_{\text{B-cubed}} = \frac{1}{N} \sum_{i=1}^N P_i$$
$$\text{Recall}_{\text{B-cubed}} = \frac{1}{N} \sum_{i=1}^N R_i$$
$$F_{1\text{, B-cubed}} = \frac{2 \cdot \text{Precision}_{\text{B-cubed}} \cdot \text{Recall}_{\text{B-cubed}}}{\text{Precision}_{\text{B-cubed}} + \text{Recall}_{\text{B-cubed}}}$$

#### Noise and Singleton Policy
- Articles with reference label `None` or predicted label `-1` (unassigned noise) are mapped to unique synthetic IDs ($L(i) = \{\text{true\_singleton\_}i\}$, $C(i) = \{\text{pred\_singleton\_}i\}$).
- This guarantees $|L(i)| = 1$ and $|C(i)| = 1$, strictly preventing disparate noise articles from falsely matching one another and inflating performance.

### 2.2 Adjusted Rand Index (ARI)
Corrects the standard Rand Index for chance cluster agreement:
$$\text{ARI} = \frac{\text{Index} - \text{Expected Index}}{\text{Max Index} - \text{Expected Index}} \in [-1.0, 1.0]$$
A score of $1.0$ indicates perfect agreement; values near $0.0$ indicate random clustering.

### 2.3 Normalized Mutual Information (NMI)
Measures the information-theoretic reduction in entropy of ground-truth cluster labels given predicted cluster labels:
$$\text{NMI}(L, C) = \frac{2 \cdot I(L; C)}{H(L) + H(C)} \in [0.0, 1.0]$$

### 2.4 Pairwise Precision, Recall, and F1
Evaluates all $\binom{N}{2} = \frac{N(N-1)}{2}$ candidate pairs:
- **True Positive (TP)**: Both articles share the same ground-truth cluster and are placed in the same predicted cluster.
- **False Positive (FP)**: Articles are from different ground-truth clusters but placed in the same predicted cluster.
- **False Negative (FN)**: Articles belong to the same ground-truth cluster but split into separate predicted clusters.

---

## 3. Standard 4-Way Ablation Benchmark Design

To isolate the empirical contribution of each feature modality, the system provides an automated 4-way ablation protocol:

| Variant | Name | Semantic ($\alpha$) | Temporal ($\beta$) | Entity ($\gamma$) | Scientific Objective |
|---|---|---|---|---|---|
| **$M_1$** | **Semantic Only** | $1.00$ | $0.00$ | $0.00$ | Evaluate dense sentence embeddings in isolation without time or entity features. |
| **$M_2$** | **Semantic + Time** | $0.70$ | $0.30$ | $0.00$ | Test whether exponential temporal decay resolves semantic collisions across time. |
| **$M_3$** | **Semantic + Entity** | $0.75$ | $0.00$ | $0.25$ | Test whether named-entity Jaccard overlap filters semantically similar cross-topic stories. |
| **$M_4$** | **Proposed Full Hybrid** | $0.55$ | $0.25$ | $0.20$ | Assess whether unifying all three modalities yields superior overall B-cubed $F_1$. |
