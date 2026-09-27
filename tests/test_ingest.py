from pathlib import Path

import pytest

from src.ingest import DocumentIngestionError, chunk_text, extract_text_from_file


def test_extract_text_and_chunking(tmp_path: Path):
    path = tmp_path / "notes.txt"
    path.write_text("abcdefghij", encoding="utf-8")

    assert extract_text_from_file(str(path)) == "abcdefghij"
    assert chunk_text("abcdefghij", chunk_size=6, overlap=2) == [
        "abcdef",
        "efghij",
    ]


def test_extract_docx(tmp_path: Path):
    document_module = pytest.importorskip("docx")
    document = document_module.Document()
    document.add_paragraph("A DOCX paragraph")
    path = tmp_path / "notes.docx"
    document.save(path)

    assert "A DOCX paragraph" in extract_text_from_file(str(path))


def test_extract_pdf(tmp_path: Path):
    fitz = pytest.importorskip("fitz")
    path = tmp_path / "notes.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "A PDF paragraph")
    document.save(path)
    document.close()

    assert "A PDF paragraph" in extract_text_from_file(str(path))


def test_rejects_unsupported_file(tmp_path: Path):
    path = tmp_path / "archive.zip"
    path.write_bytes(b"not supported")

    with pytest.raises(DocumentIngestionError):
        extract_text_from_file(str(path))


def test_chunk_validation():
    with pytest.raises(ValueError):
        chunk_text("text", chunk_size=0)
    with pytest.raises(ValueError):
        chunk_text("text", chunk_size=5, overlap=5)
