from functools import lru_cache
from typing import Iterable

import numpy as np


class EmbeddingError(RuntimeError):
    """Raised when the local embedding model cannot be loaded or used."""


@lru_cache(maxsize=4)
def _load_sentence_transformer(model_name: str):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise EmbeddingError(
            "sentence-transformers is not installed. Install requirements.txt before indexing documents."
        ) from exc

    try:
        return SentenceTransformer(model_name)
    except Exception as exc:
        raise EmbeddingError(
            f"Could not load embedding model '{model_name}'. "
            "The first run may need local model-cache access."
        ) from exc


class SentenceTransformerEmbeddings:
    """Reusable local embeddings backed by a cached sentence-transformer."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    @property
    def model(self):
        return _load_sentence_transformer(self.model_name)

    def embed_documents(self, texts: Iterable[str]) -> np.ndarray:
        values = list(texts)
        if not values:
            return np.empty((0, 0), dtype=np.float32)
        try:
            vectors = self.model.encode(
                values,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
        except Exception as exc:
            raise EmbeddingError(f"Could not embed document text: {exc}") from exc
        return np.asarray(vectors, dtype=np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        vectors = self.embed_documents([text])
        return vectors[0]
