from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient

import app.main as main
from src.config import Settings
from src.pipeline import HexaSensePipeline


class FakeEmbeddings:
    def embed_documents(self, texts):
        return np.asarray(
            [[1.0, 0.0] if "launch" in text.lower() else [0.0, 1.0] for text in texts],
            dtype=np.float32,
        )

    def embed_query(self, text):
        return np.asarray(
            [1.0, 0.0] if "launch" in text.lower() else [0.0, 1.0],
            dtype=np.float32,
        )


class FakeLLM:
    def configure(self, base_url):
        self.base_url = base_url

    def generate(self, prompt):
        return "The launch is planned for Q3 after user testing."


def test_api_uses_shared_pipeline(tmp_path: Path, monkeypatch):
    config = Settings(
        local_index_dir=str(tmp_path / "index"),
        vector_db_path=str(tmp_path / "index" / "vectors"),
        documents_dir=str(tmp_path / "documents"),
        min_relevance_score=0.1,
    )
    pipeline = HexaSensePipeline(config, FakeEmbeddings(), FakeLLM())
    monkeypatch.setattr(main, "pipeline", pipeline)

    with TestClient(main.app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["app"] == "HexaSense"

        uploaded = client.post(
            "/documents",
            files={
                "file": ("notes.txt", b"The launch is planned for Q3.", "text/plain")
            },
            data={"redact": "false"},
        )
        assert uploaded.status_code == 200
        document = uploaded.json()

        listed = client.get("/documents")
        assert listed.status_code == 200
        assert listed.json()["documents"][0]["file_name"] == "notes.txt"

        answer = client.post(
            "/query",
            json={"question": "What is the launch timeline?"},
        )
        assert answer.status_code == 200
        assert answer.json()["sources"][0]["file_name"] == "notes.txt"

        deleted = client.delete(f"/documents/{document['doc_id']}")
        assert deleted.status_code == 200
        assert deleted.json()["forgotten"] is True
