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


def test_generate_candidate_passes_timeout_and_returns_trimmed(monkeypatch):
    completions = _FakeCompletions()
    monkeypatch.setattr(xai_wrapper, "get_client", lambda: _FakeClient(completions))

    result = xai_wrapper.generate_candidate("hello", timeout=12.5)

    assert result == "result"
    assert completions.kwargs["timeout"] == 12.5


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
