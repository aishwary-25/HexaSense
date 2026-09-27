import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional


class MemoryStoreError(RuntimeError):
    """Raised when persisted document metadata cannot be trusted."""


@dataclass
class MemoryEntry:
    doc_id: str
    file_name: str
    file_path: str
    redacted: bool = False
    indexed: bool = False
    chunk_count: int = 0
    indexed_at: str = ""


class MemoryManager:
    def __init__(self, metadata_path: str):
        self.metadata_path = Path(metadata_path)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        self.documents = {}
        self._load()

    def _load(self) -> None:
        if not self.metadata_path.exists():
            return
        try:
            values = json.loads(self.metadata_path.read_text(encoding="utf-8"))
            self.documents = {value["doc_id"]: MemoryEntry(**value) for value in values}
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise MemoryStoreError(
                f"Could not load local document metadata from '{self.metadata_path}'. "
                "Repair or remove the malformed metadata before continuing."
            ) from exc

    def _persist(self) -> None:
        self.metadata_path.write_text(
            json.dumps([asdict(entry) for entry in self.documents.values()], indent=2),
            encoding="utf-8",
        )

    def add_document(
        self,
        doc_id: str,
        file_name: str,
        file_path: str,
        redacted: bool = False,
        chunk_count: int = 0,
        indexed_at: str = "",
    ) -> MemoryEntry:
        entry = MemoryEntry(
            doc_id,
            file_name,
            file_path,
            redacted=redacted,
            indexed=True,
            chunk_count=chunk_count,
            indexed_at=indexed_at,
        )
        self.documents[doc_id] = entry
        self._persist()
        return entry

    def forget_document(self, doc_id: str):
        removed = self.documents.pop(doc_id, None)
        if removed is not None:
            self._persist()
        return removed

    def get_document(self, doc_id: str) -> Optional[MemoryEntry]:
        return self.documents.get(doc_id)

    def list_documents(self) -> List[MemoryEntry]:
        return list(self.documents.values())
