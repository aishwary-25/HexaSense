from src.llm_client import LocalLLMClient


def test_default_local_model_is_llama():
    assert LocalLLMClient().model_name == "llama3.2"


def test_ollama_health_failure_is_human_readable():
    client = LocalLLMClient("llama3.2")
    client.configure("http://127.0.0.1:9")

    status = client.health_check()

    assert status["ready"] is False
    assert "Ollama" in status["message"]
