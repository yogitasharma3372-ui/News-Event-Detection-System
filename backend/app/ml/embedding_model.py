"""
Dense Semantic Embedding Model using Sentence-Transformers with persistent disk caching.
Caches vector embeddings by SHA-256 content hash and model name.
"""
import os
import json
import logging
from typing import List, Dict, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.ml.preprocessor import clean_text

# Configure HuggingFace environment settings for robust Windows operation
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

logger = logging.getLogger(__name__)


class SemanticEmbeddingModel:
    """
    Manages Sentence Transformer embedding generation and local disk caching.
    Ensures model is loaded once (singleton) and reused across API calls.
    """
    _instance: Optional["SemanticEmbeddingModel"] = None
    _model = None
    _model_name: str = ""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", cache_dir: str = "./data/cache/embeddings"):
        self.model_name = model_name
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self._ensure_model_loaded()

    def _ensure_model_loaded(self) -> None:
        """
        Lazy load SentenceTransformer model into memory if not already cached.
        """
        if SemanticEmbeddingModel._model is None or SemanticEmbeddingModel._model_name != self.model_name:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer: {self.model_name}")
                SemanticEmbeddingModel._model = SentenceTransformer(self.model_name)
                SemanticEmbeddingModel._model_name = self.model_name
                logger.info("SentenceTransformer successfully loaded.")
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer '{self.model_name}': {e}. Fallback will be used if needed.")
                SemanticEmbeddingModel._model = None

    def _get_cache_path(self, content_hash: str) -> str:
        safe_model_id = self.model_name.replace("/", "_")
        return os.path.join(self.cache_dir, f"{content_hash}_{safe_model_id}.npy")

    def encode_article(self, text: str, content_hash: str) -> np.ndarray:
        """
        Encode a single article text into a normalized 1D embedding vector.
        Checks disk cache first before performing neural inference.
        """
        cache_path = self._get_cache_path(content_hash)
        if os.path.exists(cache_path):
            try:
                return np.load(cache_path)
            except Exception:
                pass

        cleaned = clean_text(text)
        if SemanticEmbeddingModel._model is not None:
            vec = SemanticEmbeddingModel._model.encode(cleaned, normalize_embeddings=True)
            vec = np.asarray(vec, dtype=np.float32)
        else:
            # Deterministic fallback pseudo-semantic embedding for offline/testing if model fails
            rng = np.random.default_rng(abs(hash(cleaned[:100])) % (2**32))
            vec = rng.standard_normal(384).astype(np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm

        try:
            np.save(cache_path, vec)
        except Exception as e:
            logger.debug(f"Failed to write embedding cache to {cache_path}: {e}")

        return vec

    def encode_batch(self, texts: List[str], content_hashes: List[str]) -> np.ndarray:
        """
        Batch encode multiple articles, leveraging cache for previously seen items
        and passing only uncached articles to the neural model in one batch.
        """
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        n = len(texts)
        embeddings: List[Optional[np.ndarray]] = [None] * n
        missing_indices: List[int] = []
        missing_texts: List[str] = []

        # 1. Inspect cache
        for i, (text, chash) in enumerate(zip(texts, content_hashes)):
            cache_path = self._get_cache_path(chash)
            if os.path.exists(cache_path):
                try:
                    embeddings[i] = np.load(cache_path)
                    continue
                except Exception:
                    pass
            missing_indices.append(i)
            missing_texts.append(clean_text(text))

        # 2. Encode uncached items in single batch
        if missing_texts:
            if SemanticEmbeddingModel._model is not None:
                new_vecs = SemanticEmbeddingModel._model.encode(
                    missing_texts, 
                    batch_size=32, 
                    normalize_embeddings=True, 
                    show_progress_bar=False
                )
                new_vecs = np.asarray(new_vecs, dtype=np.float32)
            else:
                new_vecs = []
                for t in missing_texts:
                    rng = np.random.default_rng(abs(hash(t[:100])) % (2**32))
                    v = rng.standard_normal(384).astype(np.float32)
                    norm = np.linalg.norm(v)
                    new_vecs.append(v / norm if norm > 0 else v)
                new_vecs = np.array(new_vecs, dtype=np.float32)

            for idx, vec in zip(missing_indices, new_vecs):
                embeddings[idx] = vec
                c_path = self._get_cache_path(content_hashes[idx])
                try:
                    np.save(c_path, vec)
                except Exception:
                    pass

        return np.array(embeddings, dtype=np.float32)

    def compute_similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Compute pairwise cosine similarity matrix between dense normalized embeddings.
        Values are scaled to [0.0, 1.0].
        """
        if len(embeddings) == 0:
            return np.empty((0, 0))
        sim = cosine_similarity(embeddings)
        # Cosine similarity between normalized vectors is in [-1, 1]; clip to [0, 1]
        return np.clip((sim + 1.0) / 2.0, 0.0, 1.0)
