from pathlib import Path

import numpy as np

from src.vector_store import LocalVectorStore, VectorEntry


def test_similarity_persistence_and_deletion(tmp_path: Path):
    store_path = tmp_path / "vector_store"
    store = LocalVectorStore(str(store_path))
    entries = [
        VectorEntry("doc-a", "a:0", "launch timeline", metadata={"file_name": "a.txt"}),
        VectorEntry("doc-b", "b:0", "payment terms", metadata={"file_name": "b.txt"}),
    ]
    store.add(entries, np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32))

    assert store.search([0.9, 0.1], top_k=1)[0].doc_id == "doc-a"
    assert store.count() == 2

    reloaded = LocalVectorStore(str(store_path))
    assert reloaded.count() == 2
    assert reloaded.search([0.1, 0.9], top_k=1)[0].doc_id == "doc-b"
    assert reloaded.delete_by_doc_id("doc-a") == 1
    assert reloaded.count() == 1
    assert reloaded.search([1.0, 0.0], top_k=3)[0].doc_id == "doc-b"
