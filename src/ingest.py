from pathlib import Path

from typing import List


class DocumentRecord:
    def __init__(self, file_id: str, file_name: str, file_path: str, file_type: str):
        self.file_id = file_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = file_type


def extract_text_from_file(file_path: str) -> str:
    """Extract text from a supported document type.

    This is a lightweight placeholder. In a real implementation, use PyMuPDF,
    python-docx, or plain text parsing depending on input.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return path.read_text(encoding="utf-8", errors="ignore")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> List[str]:
    """Split a text block into overlapping chunks."""
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks
