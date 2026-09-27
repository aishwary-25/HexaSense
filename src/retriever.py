from typing import List

from .embeddings import SentenceTransformerEmbeddings
from .vector_store import LocalVectorStore, SearchResult


class Retriever:
    def __init__(
        self, vector_store: LocalVectorStore, embeddings: SentenceTransformerEmbeddings
    ):
        self.vector_store = vector_store
        self.embeddings = embeddings

    def retrieve(
        self, query: str, top_k: int = 5, min_score: float = 0.0
    ) -> List[SearchResult]:
        """Embed a query and return the most similar local chunks."""
        if not query.strip():
            return []
        query_embedding = self.embeddings.embed_query(query)
        return self.vector_store.search(
            query_embedding,
            top_k=top_k,
            min_score=min_score,
        )
