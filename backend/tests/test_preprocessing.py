"""
Unit tests for text preprocessing, tokenization, and content hashing.
"""
import pytest
from backend.app.ml.preprocessor import clean_text, tokenize, compute_content_hash


def test_clean_text_normalizes_whitespace_and_html():
    raw_html = "<p>Breaking: Major   earthquake strikes &nbsp; <b>Japan</b>!</p>"
    cleaned = clean_text(raw_html)
    assert "<p>" not in cleaned
    assert "<b>" not in cleaned
    assert "  " not in cleaned
    assert "Major earthquake strikes Japan!" in cleaned


def test_tokenize_filters_stopwords_and_short_words():
    text = "The James Webb telescope discovered an ancient and massive galaxy."
    tokens = tokenize(text, remove_stopwords=True)
    # 'the', 'an', 'and' are stopwords and should be removed
    assert "the" not in tokens
    assert "and" not in tokens
    assert "telescope" in tokens
    assert "galaxy" in tokens
    assert "discovered" in tokens


def test_compute_content_hash_deterministic():
    h1 = "Earthquake strikes Sendai"
    b1 = "A powerful tremor shook the coast on Monday."
    
    hash_a = compute_content_hash(h1, b1)
    hash_b = compute_content_hash(h1, b1)
    assert hash_a == hash_b
    assert len(hash_a) == 64 # SHA-256 hex length


def test_compute_content_hash_insensitive_to_whitespace():
    hash_normal = compute_content_hash("Headline Test", "Body content test")
    hash_spaced = compute_content_hash("  Headline   Test  ", "Body   content   test\n")
    assert hash_normal == hash_spaced
