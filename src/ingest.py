from dataclasses import dataclass
from pathlib import Path
from typing import List

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


class DocumentIngestionError(ValueError):
    """Raised when a document cannot be safely extracted or processed."""


@dataclass
class DocumentRecord:
    file_id: str
    file_name: str
    file_path: str
    file_type: str


def extract_text_from_file(file_path: str) -> str:
    """Extract text from TXT, Markdown, PDF, or DOCX files."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise DocumentIngestionError(
            f"Unsupported file type '{suffix or '[no extension]'}'. Supported types: {supported}."
        )

    try:
        if suffix in {".txt", ".md"}:
            return path.read_text(encoding="utf-8", errors="ignore")

        if suffix == ".pdf":
            import fitz

            with fitz.open(path) as document:
                return "\n".join(page.get_text("text") for page in document)

        if suffix == ".docx":
            from docx import Document

            document = Document(path)
            paragraphs = [paragraph.text for paragraph in document.paragraphs]
            for table in document.tables:
                for row in table.rows:
                    paragraphs.append(" | ".join(cell.text for cell in row.cells))
            return "\n".join(paragraphs)
    except DocumentIngestionError:
        raise
    except Exception as exc:
        raise DocumentIngestionError(
            f"Could not extract text from '{path.name}': {exc}"
        ) from exc

    raise DocumentIngestionError(f"Could not extract text from '{path.name}'.")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> List[str]:
    """Split a text block into overlapping chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    if not text.strip():
        return []

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
