"""
TF-IDF vectorizer and Cosine Similarity baseline model.
Provides vector representation, pairwise similarity matrix calculation, and query projection.
"""
from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.ml.preprocessor import clean_text


class TfidfBaselineModel:
    """
    TF-IDF feature extractor and cosine similarity calculator for news articles.
    """
    def __init__(self, max_features: int = 5000, ngram_range: Tuple[int, int] = (1, 2)):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words="english",
            sublinear_tf=True
        )
        self.is_fitted = False

    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """
        Fit vectorizer vocabulary on provided texts and return dense TF-IDF matrix.
        """
        cleaned_texts = [clean_text(t) for t in texts]
        if not cleaned_texts:
            return np.empty((0, 0))
        sparse_mat = self.vectorizer.fit_transform(cleaned_texts)
        self.is_fitted = True
        return sparse_mat.toarray()

    def transform(self, texts: List[str]) -> np.ndarray:
        """
        Transform new texts into TF-IDF vector representations using fitted vocabulary.
        """
        if not self.is_fitted:
            raise ValueError("TfidfBaselineModel must be fitted before calling transform().")
        cleaned_texts = [clean_text(t) for t in texts]
        return self.vectorizer.transform(cleaned_texts).toarray()

    def compute_similarity_matrix(self, texts: List[str]) -> np.ndarray:
        """
        Calculate N x N pairwise cosine similarity matrix across all texts.
        Values are bounded in [0.0, 1.0].
        """
        if len(texts) == 0:
            return np.empty((0, 0))
        if len(texts) == 1:
            return np.ones((1, 1), dtype=float)
            
        vectors = self.fit_transform(texts)
        sim_matrix = cosine_similarity(vectors)
        # Numerical clip to ensure exact [0, 1] bounds
        return np.clip(sim_matrix, 0.0, 1.0)
