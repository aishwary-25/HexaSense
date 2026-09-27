import hashlib
import shutil
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .config import Settings, settings
from .embeddings import SentenceTransformerEmbeddings
from .ingest import SUPPORTED_EXTENSIONS, chunk_text, extract_text_from_file
from .llm_client import AnswerGenerator, LocalLLMClient
from .memory_manager import MemoryManager
from .redactor import redact_pii
from .retriever import Retriever
from .vector_store import LocalVectorStore, VectorEntry


class PipelineError(RuntimeError):
    """Raised for a user-facing indexing, retrieval, or forgetting error."""


@dataclass
class QueryResult:
    answer: str
    sources: List[Dict[str, Any]]


ProgressCallback = Callable[[str], None]


class HexaSensePipeline:
    """Shared document indexing, retrieval, answering, and forgetting service."""

    def __init__(
        self,
        config: Settings = settings,
        embeddings: Optional[object] = None,
        llm_client: Optional[LocalLLMClient] = None,
    ):
        self.config = config
        self.vector_store = LocalVectorStore(config.vector_db_path)
        self.memory_manager = MemoryManager(
            str(Path(config.local_index_dir) / "documents.json")
        )
        self.embeddings = embeddings or SentenceTransformerEmbeddings(
            config.embedding_model_name
        )
        self.retriever = Retriever(self.vector_store, self.embeddings)
        self.llm_client = llm_client or LocalLLMClient(config.model_name)
        if hasattr(self.llm_client, "configure"):
            self.llm_client.configure(config.ollama_base_url)
        self.answer_generator = AnswerGenerator(self.llm_client)
        self.documents_dir = Path(config.documents_dir)
        self.documents_dir.mkdir(parents=True, exist_ok=True)

    def index_file(
        self,
        file_path: str,
        file_name: Optional[str] = None,
        redact: Optional[bool] = None,
        progress: Optional[ProgressCallback] = None,
    ) -> Dict[str, Any]:
        path = Path(file_path)
        display_name = file_name or path.name
        suffix = Path(display_name).suffix.lower() or path.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
            raise PipelineError(
                f"Unsupported file type for '{display_name}'. Supported types: {supported}."
            )

        self._notify(progress, "extracting")
        try:
            file_bytes = path.read_bytes()
        except OSError as exc:
            raise PipelineError(f"Could not read '{display_name}': {exc}") from exc

        try:
            text = extract_text_from_file(str(path))
        except Exception as exc:
            raise PipelineError(str(exc)) from exc
        if not text.strip():
            raise PipelineError(f"'{display_name}' does not contain extractable text.")

        should_redact = self.config.pii_redaction_enabled if redact is None else redact
        self._notify(progress, "redacting" if should_redact else "redaction disabled")
        processed_text = redact_pii(text) if should_redact else text
        self._notify(progress, "chunking")
        chunks = chunk_text(
            processed_text,
            chunk_size=self.config.chunk_size,
            overlap=self.config.chunk_overlap,
        )
        if not chunks:
            raise PipelineError(f"'{display_name}' did not produce any text chunks.")

        self._notify(progress, "embedding")
        try:
            vectors = self.embeddings.embed_documents(chunks)
        except Exception as exc:
            raise PipelineError(f"Could not create local embeddings: {exc}") from exc

        digest = hashlib.sha256(
            file_bytes + b"\0" + display_name.encode("utf-8")
        ).hexdigest()
        doc_id = digest[:24]
        stored_path = self.documents_dir / f"{doc_id}{suffix}"

        existing = self.memory_manager.get_document(doc_id)
        if existing is not None:
            self.vector_store.delete_by_doc_id(doc_id)
            self._remove_stored_file(existing.file_path)
            self.memory_manager.forget_document(doc_id)

        try:
            shutil.copyfile(path, stored_path)
        except OSError as exc:
            raise PipelineError(
                f"Could not store '{display_name}' locally: {exc}"
            ) from exc

        indexed_at = datetime.now(timezone.utc).isoformat()
        entries = [
            VectorEntry(
                doc_id=doc_id,
                chunk_id=f"{doc_id}:{index}",
                chunk_text=chunk,
                metadata={
                    "file_name": display_name,
                    "file_path": str(stored_path),
                    "file_type": suffix,
                    "redacted": should_redact,
                    "indexed_at": indexed_at,
                },
            )
            for index, chunk in enumerate(chunks)
        ]

        self._notify(progress, "saving")
        try:
            self.vector_store.add(entries, vectors=vectors)
            document = self.memory_manager.add_document(
                doc_id=doc_id,
                file_name=display_name,
                file_path=str(stored_path),
                redacted=should_redact,
                chunk_count=len(chunks),
                indexed_at=indexed_at,
            )
        except Exception as exc:
            self.vector_store.delete_by_doc_id(doc_id)
            self._remove_stored_file(str(stored_path))
            raise PipelineError(
                f"Could not persist '{display_name}' in the local index: {exc}"
            ) from exc

        result = asdict(document)
        result["updated"] = existing is not None
        self._notify(progress, "indexed")
        return result

    def index_bytes(
        self,
        content: bytes,
        file_name: str,
        redact: Optional[bool] = None,
        progress: Optional[ProgressCallback] = None,
    ) -> Dict[str, Any]:
        suffix = Path(file_name).suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise PipelineError(
                f"Unsupported file type for '{file_name}'. Supported types: "
                f"{', '.join(sorted(SUPPORTED_EXTENSIONS))}."
            )
        temporary_path: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temporary:
                temporary.write(content)
                temporary_path = temporary.name
            return self.index_file(
                temporary_path,
                file_name=file_name,
                redact=redact,
                progress=progress,
            )
        finally:
            if temporary_path:
                Path(temporary_path).unlink(missing_ok=True)

    def list_documents(self) -> List[Dict[str, Any]]:
        return [asdict(document) for document in self.memory_manager.list_documents()]

    def forget_document(self, doc_id: str) -> Dict[str, Any]:
        document = self.memory_manager.get_document(doc_id)
        if document is None:
            raise PipelineError(f"Document '{doc_id}' is not indexed.")

        self.vector_store.delete_by_doc_id(doc_id)
        try:
            self._remove_stored_file(document.file_path)
        except OSError as exc:
            raise PipelineError(
                f"Vectors were removed, but the stored document could not be deleted: {exc}"
            ) from exc
        self.memory_manager.forget_document(doc_id)
        return {"doc_id": doc_id, "forgotten": True}

    def query(self, question: str, top_k: Optional[int] = None) -> QueryResult:
        if not question.strip():
            raise PipelineError("Enter a question before searching.")

        results = self.retriever.retrieve(
            question,
            top_k=top_k or self.config.max_results,
            min_score=self.config.min_relevance_score,
        )
        if not results:
            return QueryResult(
                answer="The answer was not found in the indexed documents.",
                sources=[],
            )

        try:
            answer = self.answer_generator.answer(question, results)
        except Exception as exc:
            raise PipelineError(str(exc)) from exc

        sources = [
            {
                "doc_id": result.doc_id,
                "chunk_id": result.chunk_id,
                "file_name": result.metadata.get("file_name", "unknown"),
                "file_type": result.metadata.get("file_type", ""),
                "score": round(result.score, 4),
                "text": result.chunk_text,
                "redacted": result.metadata.get("redacted", False),
            }
            for result in results
        ]
        return QueryResult(answer=answer, sources=sources)

    def _remove_stored_file(self, file_path: str) -> None:
        candidate = Path(file_path)
        storage_root = self.documents_dir.resolve()
        try:
            is_internal = candidate.resolve().is_relative_to(storage_root)
        except FileNotFoundError:
            is_internal = False
        if is_internal:
            candidate.unlink(missing_ok=True)

    @staticmethod
    def _notify(progress: Optional[ProgressCallback], stage: str) -> None:
        if progress is not None:
            progress(stage)
