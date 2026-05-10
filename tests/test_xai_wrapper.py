from types import SimpleNamespace

import pytest

from api import xai_wrapper


class _FakeCompletions:
    def __init__(self):
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="  result  "))]
        )


class _FakeClient:
    def __init__(self, completions):
        self.chat = SimpleNamespace(completions=completions)


def test_get_default_model_returns_fallback_when_xai_model_unset(monkeypatch):
    monkeypatch.delenv("XAI_MODEL", raising=False)

    assert xai_wrapper.get_default_model() == "grok-4"


def test_get_default_model_returns_env_value(monkeypatch):
    monkeypatch.setenv("XAI_MODEL", "grok-test")

    assert xai_wrapper.get_default_model() == "grok-test"


def test_get_default_model_returns_fallback_when_xai_model_empty(monkeypatch):
    monkeypatch.setenv("XAI_MODEL", "")

    assert xai_wrapper.get_default_model() == "grok-4"


def test_get_client_raises_when_xai_api_key_missing(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="XAI_API_KEY is not set"):
        xai_wrapper.get_client()


def test_generate_candidate_passes_timeout_and_returns_trimmed(monkeypatch):
    completions = _FakeCompletions()
    monkeypatch.setattr(xai_wrapper, "get_client", lambda: _FakeClient(completions))

    result = xai_wrapper.generate_candidate("hello", timeout=12.5)

    assert result == "result"
    assert completions.kwargs["timeout"] == 12.5


def test_generate_candidate_uses_explicit_model_over_xai_model(monkeypatch):
    completions = _FakeCompletions()
    monkeypatch.setenv("XAI_MODEL", "env-model")
    monkeypatch.setattr(xai_wrapper, "get_client", lambda: _FakeClient(completions))

    result = xai_wrapper.generate_candidate("hello", model="explicit-model")

    assert result == "result"
    assert completions.kwargs["model"] == "explicit-model"


def test_generate_candidate_uses_xai_model_when_model_not_provided(monkeypatch):
    completions = _FakeCompletions()
    monkeypatch.setenv("XAI_MODEL", "env-model")
    monkeypatch.setattr(xai_wrapper, "get_client", lambda: _FakeClient(completions))

    result = xai_wrapper.generate_candidate("hello")

    assert result == "result"
    assert completions.kwargs["model"] == "env-model"


def test_generate_candidate_logs_and_raises_runtime_error_on_failure(monkeypatch):
    class _BrokenCompletions:
        def create(self, **kwargs):
            raise ValueError("boom")

    monkeypatch.setattr(
        xai_wrapper,
        "get_client",
        lambda: _FakeClient(_BrokenCompletions()),
    )

    with pytest.raises(RuntimeError, match="xai_generation_failed"):
        xai_wrapper.generate_candidate("hello")
