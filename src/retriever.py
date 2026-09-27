from typing import List


class Retriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def retrieve(self, query_embedding: List[float], top_k: int = 5):
        """Return the top matching chunks based on local vector similarity.

        This is intentionally simple so it can be replaced with FAISS/Chroma logic.
        """
        return self.vector_store.search(query_embedding, top_k=top_k)
