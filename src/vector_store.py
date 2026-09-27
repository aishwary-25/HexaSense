import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np


class VectorStoreError(RuntimeError):
    """Raised when a persistent vector store cannot be read or updated."""


@dataclass
class VectorEntry:
    doc_id: str
    chunk_id: str
    chunk_text: str
    embedding: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    entry: VectorEntry
    score: float

    @property
    def doc_id(self) -> str:
        return self.entry.doc_id

    @property
    def chunk_id(self) -> str:
        return self.entry.chunk_id

    @property
    def chunk_text(self) -> str:
        return self.entry.chunk_text

    @property
    def metadata(self) -> Dict[str, Any]:
        return self.entry.metadata


class LocalVectorStore:
    """Persistent cosine-similarity store using FAISS when available."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.entries: List[VectorEntry] = []
        self._vectors = np.empty((0, 0), dtype=np.float32)
        self._index = None
        self._faiss = None
        self.path.mkdir(parents=True, exist_ok=True)
        try:
            import faiss

            self._faiss = faiss
        except ImportError:
            self._faiss = None
        self._load()

    @property
    def metadata_path(self) -> Path:
        return self.path / "entries.json"

    @property
    def vectors_path(self) -> Path:
        return self.path / "vectors.npy"

    @property
    def faiss_path(self) -> Path:
        return self.path / "index.faiss"

    def _load(self) -> None:
        if not self.metadata_path.exists() or not self.vectors_path.exists():
            return
        try:
            raw_entries = json.loads(self.metadata_path.read_text(encoding="utf-8"))
            vectors = np.load(self.vectors_path, allow_pickle=False).astype(np.float32)
            self.entries = [VectorEntry(**entry) for entry in raw_entries]
            if len(self.entries) != len(vectors):
                raise VectorStoreError(
                    "Vector metadata and vector matrix have different lengths"
                )
            self._vectors = vectors
            self._rebuild_index()
        except VectorStoreError:
            raise
        except Exception as exc:
            raise VectorStoreError(
                f"Could not load vector store from '{self.path}': {exc}"
            ) from exc

    def _rebuild_index(self) -> None:
        self._index = None
        if self._faiss is None or not len(self._vectors):
            return
        dimension = self._vectors.shape[1]
        self._index = self._faiss.IndexFlatIP(dimension)
        self._index.add(self._vectors)

    def _persist(self) -> None:
        self.path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.write_text(
            json.dumps(
                [
                    {
                        "doc_id": entry.doc_id,
                        "chunk_id": entry.chunk_id,
                        "chunk_text": entry.chunk_text,
                        "embedding": entry.embedding,
                        "metadata": entry.metadata,
                    }
                    for entry in self.entries
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        np.save(self.vectors_path, self._vectors)
        if self._faiss is not None and self._index is not None:
            self._faiss.write_index(self._index, str(self.faiss_path))
        elif self.faiss_path.exists():
            self.faiss_path.unlink()

    def add(
        self,
        entries: VectorEntry | Sequence[VectorEntry],
        vectors: Optional[np.ndarray] = None,
    ) -> None:
        values = [entries] if isinstance(entries, VectorEntry) else list(entries)
        if not values:
            return
        matrix = vectors
        if matrix is None:
            matrix = np.asarray([entry.embedding for entry in values], dtype=np.float32)
        matrix = np.asarray(matrix, dtype=np.float32)
        if matrix.ndim != 2 or len(matrix) != len(values) or matrix.shape[1] == 0:
            raise VectorStoreError(
                "Embeddings must be a non-empty two-dimensional matrix"
            )
        if len(self._vectors) and matrix.shape[1] != self._vectors.shape[1]:
            raise VectorStoreError(
                "Embedding dimensions do not match the existing vector store"
            )
        for entry, vector in zip(values, matrix):
            entry.embedding = vector.tolist()
        self.entries.extend(values)
        self._vectors = (
            matrix if not len(self._vectors) else np.vstack([self._vectors, matrix])
        )
        self._rebuild_index()
        self._persist()

    def delete_by_doc_id(self, doc_id: str) -> int:
        keep = [
            index for index, entry in enumerate(self.entries) if entry.doc_id != doc_id
        ]
        removed = len(self.entries) - len(keep)
        if removed == 0:
            return 0
        self.entries = [self.entries[index] for index in keep]
        self._vectors = (
            self._vectors[keep]
            if keep
            else np.empty((0, self.dimension), dtype=np.float32)
        )
        self._rebuild_index()
        self._persist()
        return removed

    @property
    def dimension(self) -> int:
        return (
            self._vectors.shape[1]
            if self._vectors.ndim == 2 and len(self._vectors)
            else 0
        )

    def search(
        self,
        embedding: List[float] | np.ndarray,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> List[SearchResult]:
        if top_k <= 0 or not len(self.entries):
            return []
        query = np.asarray(embedding, dtype=np.float32).reshape(1, -1)
        if self.dimension and query.shape[1] != self.dimension:
            raise VectorStoreError(
                "Query embedding dimension does not match the vector store"
            )
        if self._index is not None:
            scores, indices = self._index.search(query, min(top_k, len(self.entries)))
            ranked = zip(scores[0].tolist(), indices[0].tolist())
        else:
            scores = (self._vectors @ query[0]).tolist()
            ranked = ((score, index) for index, score in enumerate(scores))
            ranked = sorted(ranked, reverse=True)[:top_k]
        return [
            SearchResult(self.entries[index], float(score))
            for score, index in ranked
            if index >= 0 and float(score) >= min_score
        ]

    def count(self) -> int:
        return len(self.entries)
