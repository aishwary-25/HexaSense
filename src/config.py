import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except (
    ImportError
):  # pragma: no cover - the dependency is declared but optional at import time
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


@dataclass
class Settings:
    project_name: str = "HexaSense"
    offline_mode: bool = os.getenv("HEXASENSE_OFFLINE_MODE", "true").lower() not in {
        "0",
        "false",
        "no",
    }
    data_dir: str = os.getenv("HEXASENSE_DATA_DIR", "data")
    sample_docs_dir: str = os.getenv("HEXASENSE_SAMPLE_DOCS_DIR", "data/sample_docs")
    local_index_dir: str = os.getenv("HEXASENSE_INDEX_DIR", "data/local_index")
    vector_db_path: str = os.getenv(
        "HEXASENSE_VECTOR_STORE_PATH", "data/local_index/vector_store"
    )
    documents_dir: str = os.getenv("HEXASENSE_DOCUMENTS_DIR", "data/documents")
    model_name: str = os.getenv("HEXASENSE_LLM_MODEL", "llama3.2")
    embedding_model_name: str = os.getenv(
        "HEXASENSE_EMBEDDING_MODEL", "all-MiniLM-L6-v2"
    )
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    chunk_size: int = int(os.getenv("HEXASENSE_CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("HEXASENSE_CHUNK_OVERLAP", "80"))
    pii_redaction_enabled: bool = os.getenv(
        "HEXASENSE_REDACT_PII", "true"
    ).lower() not in {
        "0",
        "false",
        "no",
    }
    max_results: int = int(os.getenv("HEXASENSE_MAX_RESULTS", "5"))
    min_relevance_score: float = float(
        os.getenv("HEXASENSE_MIN_RELEVANCE_SCORE", "0.25")
    )

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return (".txt", ".md", ".pdf", ".docx")


settings = Settings()


DATA_DIR = Path(settings.data_dir)
LOCAL_INDEX_DIR = Path(settings.local_index_dir)
