from pathlib import Path

import numpy as np

from src.config import Settings
from src.pipeline import HexaSensePipeline


class FakeEmbeddings:
    def __init__(self):
        self.document_texts = []

    def embed_documents(self, texts):
        self.document_texts.extend(texts)
        return np.asarray(
            [[1.0, 0.0] if "launch" in text.lower() else [0.0, 1.0] for text in texts],
            dtype=np.float32,
        )

    def embed_query(self, text):
        return np.asarray(
            [1.0, 0.0] if "launch" in text.lower() else [0.0, 1.0], dtype=np.float32
        )


class FakeLLM:
    def configure(self, base_url):
        self.base_url = base_url

    def generate(self, prompt):
        assert "launch timeline" in prompt.lower()
        assert "Source:" in prompt
        return "The client said the launch date is set for Q3 after user testing."


def test_pipeline_indexes_queries_persists_and_forgets(tmp_path: Path):
    config = Settings(
        data_dir=str(tmp_path),
        sample_docs_dir=str(tmp_path / "sample_docs"),
        local_index_dir=str(tmp_path / "index"),
        vector_db_path=str(tmp_path / "index" / "vectors"),
        documents_dir=str(tmp_path / "documents"),
        chunk_size=500,
        chunk_overlap=80,
        max_results=3,
    )
    source = tmp_path / "notes.txt"
    source.write_text("The launch timeline is Q3 after user testing.", encoding="utf-8")

    pipeline = HexaSensePipeline(config, FakeEmbeddings(), FakeLLM())
    document = pipeline.index_file(str(source), redact=False)
    assert document["chunk_count"] == 1
    assert pipeline.vector_store.count() == 1

    result = pipeline.query("What is the launch timeline?")
    assert "Q3" in result.answer
    assert result.sources[0]["file_name"] == "notes.txt"

    restarted = HexaSensePipeline(config, FakeEmbeddings(), FakeLLM())
    assert len(restarted.list_documents()) == 1
    assert restarted.vector_store.count() == 1

    restarted.forget_document(document["doc_id"])
    assert restarted.list_documents() == []
    assert restarted.vector_store.count() == 0
    assert not Path(document["file_path"]).exists()


def test_pipeline_redacts_before_embedding(tmp_path: Path):
    config = Settings(
        local_index_dir=str(tmp_path / "index"),
        vector_db_path=str(tmp_path / "index" / "vectors"),
        documents_dir=str(tmp_path / "documents"),
    )
    source = tmp_path / "sensitive.txt"
    source.write_text("Contact alice@example.com at 555-123-4567.", encoding="utf-8")
    embeddings = FakeEmbeddings()

    pipeline = HexaSensePipeline(config, embeddings, FakeLLM())
    pipeline.index_file(str(source))

    embedded_text = "\n".join(embeddings.document_texts)
    assert "alice@example.com" not in embedded_text
    assert "555-123-4567" not in embedded_text
    assert "[REDACTED]" in embedded_text
