"""
Unit tests for ML modules: TF-IDF, Semantic, Temporal, NER, Hybrid scoring, and Clustering.
"""
from datetime import datetime, timezone, timedelta
import numpy as np
import pytest

from backend.app.ml.tfidf_model import TfidfBaselineModel
from backend.app.ml.temporal_scoring import TemporalScorer
from backend.app.ml.ner_extractor import EntityExtractor
from backend.app.ml.hybrid_scorer import HybridScorer
from backend.app.ml.clusterer import EventClusterer
from backend.app.ml.title_generator import EventTitleSummaryGenerator


def test_tfidf_baseline_model():
    model = TfidfBaselineModel()
    texts = [
        "Major earthquake hits northern Japan causing tremor in Sendai",
        "Sendai struck by offshore earthquake and tsunami warnings",
        "European Central Bank decides to raise benchmark interest rates"
    ]
    sim_matrix = model.compute_similarity_matrix(texts)
    assert sim_matrix.shape == (3, 3)
    # Sendai earthquake articles should have higher similarity than ECB article
    assert sim_matrix[0, 1] > sim_matrix[0, 2]
    assert np.isclose(sim_matrix[0, 0], 1.0)


def test_temporal_scoring():
    scorer = TemporalScorer(decay_hours=72.0)
    t0 = datetime(2024, 3, 11, 10, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(hours=2)
    t2 = t0 + timedelta(hours=72) # exactly 1 half-decay window
    t3 = t0 + timedelta(days=30) # far in future

    s_close = scorer.compute_temporal_score(t0, t1)
    s_half = scorer.compute_temporal_score(t0, t2)
    s_far = scorer.compute_temporal_score(t0, t3)

    assert 0.95 < s_close <= 1.0
    assert np.isclose(s_half, np.exp(-1.0), atol=0.01) # exp(-1) ~= 0.3678
    assert s_far < 0.01
    assert s_close > s_half > s_far


def test_ner_extractor_and_jaccard():
    extractor = EntityExtractor(use_spacy=False)
    text1 = "President Christine Lagarde spoke at European Central Bank in Frankfurt."
    text2 = "European Central Bank officials in Frankfurt met with Christine Lagarde."
    text3 = "A massive earthquake hit Sendai, Japan early Monday morning."

    ents1 = extractor.extract_entities(text1)["all"]
    ents2 = extractor.extract_entities(text2)["all"]
    ents3 = extractor.extract_entities(text3)["all"]

    sim_related = extractor.compute_jaccard_similarity(ents1, ents2)
    sim_unrelated = extractor.compute_jaccard_similarity(ents1, ents3)

    assert sim_related > 0.4
    assert sim_related > sim_unrelated


def test_hybrid_scorer_validation():
    # Valid weights
    scorer = HybridScorer(alpha=0.5, beta=0.3, gamma=0.2)
    score = scorer.score_pair(0.8, 0.6, 0.4)
    expected = 0.5 * 0.8 + 0.3 * 0.6 + 0.2 * 0.4
    assert np.isclose(score, expected)

    # Invalid weights sum
    with pytest.raises(ValueError):
        HybridScorer(alpha=0.6, beta=0.6, gamma=0.1)

    # Negative weight
    with pytest.raises(ValueError):
        HybridScorer(alpha=-0.1, beta=0.6, gamma=0.5)


def test_clusterer_groups_and_handles_noise():
    clusterer = EventClusterer(similarity_threshold=0.60, min_cluster_size=2)
    
    # 4 items: items 0 & 1 are strongly similar, items 2 & 3 are strongly similar, item 4 is noise
    sim_matrix = np.array([
        [1.0, 0.85, 0.1,  0.1,  0.05],
        [0.85, 1.0, 0.12, 0.08, 0.02],
        [0.1,  0.12, 1.0, 0.90, 0.03],
        [0.1,  0.08, 0.90, 1.0, 0.01],
        [0.05, 0.02, 0.03, 0.01, 1.0]
    ])

    labels, stats = clusterer.cluster_similarity_matrix(sim_matrix)
    assert len(labels) == 5
    # Items 0 & 1 in same cluster
    assert labels[0] == labels[1] and labels[0] >= 0
    # Items 2 & 3 in same cluster
    assert labels[2] == labels[3] and labels[2] >= 0
    # Cluster 1 != Cluster 2
    assert labels[0] != labels[2]
    # Item 4 is unassigned noise
    assert labels[4] == -1
    assert stats["noise_count"] == 1
    assert stats["total_clusters"] == 2


def test_event_title_and_category_generation():
    gen = EventTitleSummaryGenerator()
    headlines = [
        "Magnitude 7.2 earthquake strikes Sendai coast",
        "Tsunami advisory lifted after 7.2 tremor in Sendai",
        "Sendai bullet trains resume after offshore earthquake"
    ]
    title = gen.select_representative_title(headlines)
    assert "Sendai" in title or "earthquake" in title

    category = gen.infer_category(["Earthquake offshore Sendai triggered tsunami advisory for coastal areas."])
    assert category == "Natural Disasters"
