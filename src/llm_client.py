from typing import List


class LocalLLMClient:
    def __init__(self, model_name: str = "phi3"):
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        """Generate an answer grounded in retrieved context.

        In production this calls a local model such as Ollama or llama.cpp.
        """
        return (
            "This is a scaffolded local answer. Connect to a local model such as "
            "Ollama or llama.cpp to generate grounded responses."
        )


class AnswerGenerator:
    def __init__(self, llm_client: LocalLLMClient):
        self.llm_client = llm_client

    def answer(self, question: str, context_chunks: List[str]) -> str:
        context = "\n\n".join(context_chunks)
        prompt = (
            "Use the following context to answer the user's question. "
            "Only answer using the supplied context. Cite source snippets.\n\n"
            f"Question: {question}\n\nContext:\n{context}"
        )
        return self.llm_client.generate(prompt)
