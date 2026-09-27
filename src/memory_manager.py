from dataclasses import dataclass


@dataclass
class MemoryEntry:
    doc_id: str
    file_name: str
    file_path: str
    redacted: bool = False
    indexed: bool = False


class MemoryManager:
    def __init__(self):
        self.documents = {}

    def add_document(self, doc_id: str, file_name: str, file_path: str):
        self.documents[doc_id] = MemoryEntry(doc_id, file_name, file_path)

    def forget_document(self, doc_id: str):
        if doc_id in self.documents:
            del self.documents[doc_id]

    def list_documents(self):
        return list(self.documents.values())
