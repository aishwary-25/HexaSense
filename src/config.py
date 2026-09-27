from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    project_name: str = "HexaSense"
    offline_mode: bool = True
    data_dir: str = "data"
    sample_docs_dir: str = "data/sample_docs"
    local_index_dir: str = "data/local_index"
    vector_db_path: str = "data/local_index/vector_store"
    model_name: str = "phi3"
    chunk_size: int = 500
    chunk_overlap: int = 80
    pii_redaction_enabled: bool = True
    max_results: int = 5


settings = Settings()


DATA_DIR = Path(settings.data_dir)
LOCAL_INDEX_DIR = Path(settings.local_index_dir)
