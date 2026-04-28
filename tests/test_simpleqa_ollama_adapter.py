from __future__ import annotations

import httpx

from benchmarks.simpleqa.model_adapter import ModelAdapterError, build_model_adapter


class _DummyResponse:
    def __init__(self, payload: dict[str, str]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, str]:
        return self._payload


class _DummyClient:
    def __init__(self, response_payload: dict[str, str]) -> None:
        self.response_payload = response_payload
        self.last_url = ""
        self.last_json: dict[str, object] = {}

    def __enter__(self) -> "_DummyClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def post(self, url: str, json: dict[str, object]) -> _DummyResponse:
        self.last_url = url
        self.last_json = json
        return _DummyResponse(self.response_payload)


class _TimeoutClient:
    def __enter__(self) -> "_TimeoutClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def post(self, url: str, json: dict[str, object]) -> _DummyResponse:
        raise httpx.TimeoutException("timed out")


def test_ollama_adapter_answer_uses_generate_endpoint(monkeypatch) -> None:
    dummy_client = _DummyClient({"response": "Paris"})

    def _client_factory(*args, **kwargs):
        return dummy_client

    monkeypatch.setattr("benchmarks.simpleqa.model_adapter.httpx.Client", _client_factory)

    adapter = build_model_adapter(
        provider="ollama",
        model="qwen2.5:0.5b",
        ollama_url="http://localhost:11434",
        ollama_timeout=5.0,
    )
    answer = adapter.answer("What is the capital of France?")

    assert answer == "Paris"
    assert dummy_client.last_url == "http://localhost:11434/api/generate"
    assert dummy_client.last_json["model"] == "qwen2.5:0.5b"
    assert dummy_client.last_json["stream"] is False


def test_ollama_adapter_timeout_is_clear(monkeypatch) -> None:
    def _client_factory(*args, **kwargs):
        return _TimeoutClient()

    monkeypatch.setattr("benchmarks.simpleqa.model_adapter.httpx.Client", _client_factory)

    adapter = build_model_adapter(
        provider="ollama",
        model="qwen2.5:0.5b",
        ollama_url="http://localhost:11434",
        ollama_timeout=1.5,
    )

    try:
        adapter.answer("Any question")
    except ModelAdapterError as exc:
        assert "timed out" in str(exc).lower()
        assert "1.5s" in str(exc)
    else:
        raise AssertionError("Expected timeout ModelAdapterError")
