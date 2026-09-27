from typing import Any, Dict, List, Sequence

from .config import settings


class LocalLLMError(RuntimeError):
    """Raised when the configured local Ollama model cannot answer."""


class LocalAIStatus(Dict[str, Any]):
    """Serializable local Ollama readiness information for the UI and API."""


class LocalLLMClient:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.model_name
        self.base_url = "http://127.0.0.1:11434"

    def configure(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def health_check(self) -> LocalAIStatus:
        """Check Ollama reachability and whether the configured model is installed."""
        try:
            import ollama
        except ImportError:
            return LocalAIStatus(
                reachable=False,
                model_available=False,
                ready=False,
                model=self.model_name,
                message="The Ollama Python package is not installed.",
                models=[],
            )

        try:
            response = ollama.Client(host=self.base_url).list()
            raw_models = (
                response.get("models", [])
                if isinstance(response, dict)
                else getattr(response, "models", [])
            )
            models = []
            for model in raw_models:
                name = (
                    model.get("name") or model.get("model")
                    if isinstance(model, dict)
                    else getattr(model, "model", None) or getattr(model, "name", None)
                )
                if name:
                    models.append(name)
            model_available = any(
                name == self.model_name or name.startswith(f"{self.model_name}:")
                for name in models
            )
            if model_available:
                message = f"Ollama connected. {self.model_name} is ready locally."
            else:
                message = (
                    f"Ollama is connected, but {self.model_name} is not installed. "
                    f"Run 'ollama pull {self.model_name}'."
                )
            return LocalAIStatus(
                reachable=True,
                model_available=model_available,
                ready=model_available,
                model=self.model_name,
                message=message,
                models=models,
            )
        except Exception as exc:
            return LocalAIStatus(
                reachable=False,
                model_available=False,
                ready=False,
                model=self.model_name,
                message=(
                    f"Ollama is unavailable at {self.base_url}. "
                    "Start Ollama to enable local answers."
                ),
                models=[],
                detail=str(exc),
            )

    def generate(self, prompt: str) -> str:
        """Generate text through the local Ollama service."""
        try:
            import ollama
        except ImportError as exc:
            raise LocalLLMError(
                "The Ollama Python package is not installed. Install requirements.txt."
            ) from exc

        try:
            client = ollama.Client(host=self.base_url)
            response = client.generate(
                model=self.model_name, prompt=prompt, options={"temperature": 0}
            )
        except Exception as exc:
            raise LocalLLMError(
                f"Could not reach Ollama at {self.base_url} or load model '{self.model_name}'. "
                f"Start Ollama and run 'ollama pull {self.model_name}'. Details: {exc}"
            ) from exc

        answer = (
            response.get("response", "")
            if isinstance(response, dict)
            else getattr(response, "response", "")
        )
        if not answer.strip():
            raise LocalLLMError(
                f"Ollama returned an empty response for model '{self.model_name}'."
            )
        return answer.strip()


class AnswerGenerator:
    def __init__(self, llm_client: LocalLLMClient):
        self.llm_client = llm_client

    def answer(self, question: str, context_chunks: Sequence[object]) -> str:
        context = "\n\n".join(
            f"[Source: {getattr(chunk, 'metadata', {}).get('file_name', 'unknown')}\n"
            f"Chunk: {getattr(chunk, 'chunk_id', 'unknown')}]\n"
            f"{getattr(chunk, 'chunk_text', str(chunk))}"
            for chunk in context_chunks
        )
        prompt = (
            "You are HexaSense, a private document assistant. Answer only from the supplied context. "
            "If the context does not support the answer, reply exactly: "
            "The answer was not found in the indexed documents. Do not use outside knowledge, "
            "do not guess, and do not combine the context with general knowledge. Include the "
            "relevant source file names in your answer when answering.\n\n"
            f"Question: {question}\n\nContext:\n{context}"
        )
        return self.llm_client.generate(prompt)
