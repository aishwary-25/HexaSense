import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class VectorEntry:
    doc_id: str
    chunk_id: str
    chunk_text: str
    embedding: List[float] = field(default_factory=list)


class LocalVectorStore:
    """Thin in-memory vector store scaffold.

    Replace with FAISS or Chroma in the full implementation.
    """
    def __init__(self, path: str):
        self.path = path
        self.entries: List[VectorEntry] = []
        os.makedirs(path, exist_ok=True)

    def add(self, entry: VectorEntry):
        self.entries.append(entry)

    def delete_by_doc_id(self, doc_id: str):
        self.entries = [e for e in self.entries if e.doc_id != doc_id]

    def search(self, embedding: List[float], top_k: int = 5):
        return self.entries[:top_k]

    def count(self) -> int:
        return len(self.entries)
