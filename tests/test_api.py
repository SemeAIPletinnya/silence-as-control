"""API tests across legacy, runtime, and experimental lanes."""

from pathlib import Path

from fastapi.testclient import TestClient

import api.main as api_main
from api.main import app

client = TestClient(app)


# ------------------------------
# Runtime provider configuration docs
# ------------------------------

def test_docker_compose_passes_runtime_environment():
    compose = Path("docker-compose.yml").read_text()

    assert "XAI_API_KEY: ${XAI_API_KEY:-}" in compose
    assert "XAI_MODEL: ${XAI_MODEL:-}" in compose
    assert "POR_RUNTIME_GATE_THRESHOLD: ${POR_RUNTIME_GATE_THRESHOLD:-0.39}" in compose
    assert "POR_TELEMETRY_ENABLED: ${POR_TELEMETRY_ENABLED:-0}" in compose
    assert (
        "POR_TELEMETRY_LOG_PATH: "
        "${POR_TELEMETRY_LOG_PATH:-runtime_logs/por_runtime_events.jsonl}"
    ) in compose
    assert "OPENAI_API_KEY: ${OPENAI_API_KEY:-}" not in compose
    assert "OPENAI_MODEL: ${OPENAI_MODEL:-}" not in compose


def test_readme_documents_xai_provider_completion_guidance():
    readme = Path("README.md").read_text(encoding="utf-8-sig")
    normalized_readme = " ".join(readme.split())

    assert "Provider-backed `/por/complete`" in readme
    assert "requires `XAI_API_KEY`" in readme
    assert "Docker Compose maps `XAI_*`, `POR_RUNTIME_GATE_THRESHOLD`, and" in readme
    assert "`POR_TELEMETRY_*` into the API container" in readme
    assert "demo/canonical_runtime_demo.py" in readme
    assert "do not require provider API keys" in normalized_readme


# ------------------------------
# Legacy compatibility endpoint
# ------------------------------

def test_api_legacy_generate_returns_ok_for_high_coherence():
    response = client.post(
        "/generate",
        json={"output": "text", "coherence": 0.82, "drift": 0.15},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "output": "text"}


def test_api_legacy_generate_returns_abstained_for_low_coherence():
    response = client.post(
        "/generate",
        json={"output": "text", "coherence": 0.6, "drift": 0.1},
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "abstained",
        "reason": "control_abstention",
    }


# ------------------------------
# Runtime threshold behavior
# ------------------------------

def test_api_evaluate_allows_optional_adaptive_threshold():
    response = client.post(
        "/por/evaluate",
        json={
            "prompt": "Explain recursion",
            "candidate": "Recursion is when a function calls itself.",
            "threshold": 0.39,
            "use_adaptive_threshold": True,
            "recent_drifts": [0.7, 0.8],
            "recent_coherences": [0.5, 0.6],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["threshold"] > 0.39
    assert 0.0 <= payload["instability_score"] <= 1.0


def test_api_evaluate_stays_fixed_when_adaptive_disabled():
    response = client.post(
        "/por/evaluate",
        json={
            "prompt": "Explain recursion",
            "candidate": "Recursion is when a function calls itself.",
            "threshold": 0.39,
            "use_adaptive_threshold": False,
            "recent_drifts": [0.9, 0.95],
            "recent_coherences": [0.1, 0.2],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["threshold"] == 0.39


def test_api_evaluate_can_silence_on_low_coherence_runtime_signal():
    response = client.post(
        "/por/evaluate",
        json={
            "prompt": "Explain recursion with code examples",
            "candidate": "bananas orbit silently over parquet",
            "threshold": 0.39,
            "use_adaptive_threshold": False,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["drift"] == 0.0
    assert payload["coherence"] < 0.25
    assert payload["decision"] == "SILENCE"


def test_api_complete_uses_runtime_xai_model_default(monkeypatch):
    monkeypatch.setenv("XAI_MODEL", "runtime-env-model")
    captured = {}

    def fake_generate_candidate(*args, **kwargs):
        captured["model"] = kwargs["model"]
        return "first candidate"

    def fake_score_candidate_runtime(prompt, candidate, threshold, candidate_samples=None):
        return {
            "drift": 0.10,
            "coherence": 0.95,
            "instability_score": 0.075,
            "threshold": threshold,
            "decision": "PROCEED",
            "release_output": candidate,
            "silence_token": None,
            "notes": ["runtime_env_model"],
        }

    monkeypatch.setattr(api_main, "generate_candidate", fake_generate_candidate)
    monkeypatch.setattr(api_main, "score_candidate_runtime", fake_score_candidate_runtime)

    response = client.post(
        "/por/complete",
        json={
            "prompt": "Say hello",
            "threshold": 0.39,
            "drift_samples": 1,
        },
    )

    assert response.status_code == 200
    assert captured["model"] == "runtime-env-model"
    assert response.json()["model"] == "runtime-env-model"


# ---------------------------------
# Experimental MAYBE_SHORT_REGEN
# ---------------------------------

def test_api_complete_runs_experimental_short_regen_for_borderline_silence(monkeypatch):
    generated = ["first candidate", "regen candidate"]

    def fake_generate_candidate(*args, **kwargs):
        return generated.pop(0)

    calls = {"count": 0}

    def fake_score_candidate_runtime(prompt, candidate, threshold, candidate_samples=None):
        calls["count"] += 1
        if calls["count"] == 1:
            return {
                "drift": 0.40,
                "coherence": 0.80,
                "instability_score": 0.40,
                "threshold": threshold,
                "decision": "SILENCE",
                "release_output": None,
                "silence_token": api_main.SILENCE_TOKEN,
                "notes": ["initial_silence"],
            }
        return {
            "drift": 0.10,
            "coherence": 0.95,
            "instability_score": 0.075,
            "threshold": threshold,
            "decision": "PROCEED",
            "release_output": candidate,
            "silence_token": None,
            "notes": ["regen_success"],
        }

    monkeypatch.setattr(api_main, "generate_candidate", fake_generate_candidate)
    monkeypatch.setattr(api_main, "score_candidate_runtime", fake_score_candidate_runtime)

    response = client.post(
        "/por/complete",
        json={
            "prompt": "Say hello",
            "threshold": 0.39,
            "drift_samples": 1,
            "enable_experimental_short_regen": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] == "PROCEED"
    assert payload["candidate"] == "regen candidate"
    assert any("experimental_maybe_short_regen_attempted" in note for note in payload["notes"])


def test_api_complete_skips_experimental_short_regen_for_non_borderline_silence(monkeypatch):
    def fake_generate_candidate(*args, **kwargs):
        return "first candidate"

    calls = {"count": 0}

    def fake_score_candidate_runtime(prompt, candidate, threshold, candidate_samples=None):
        calls["count"] += 1
        return {
            "drift": 0.80,
            "coherence": 0.20,
            "instability_score": 0.80,
            "threshold": threshold,
            "decision": "SILENCE",
            "release_output": None,
            "silence_token": api_main.SILENCE_TOKEN,
            "notes": ["initial_silence"],
        }

    monkeypatch.setattr(api_main, "generate_candidate", fake_generate_candidate)
    monkeypatch.setattr(api_main, "score_candidate_runtime", fake_score_candidate_runtime)

    response = client.post(
        "/por/complete",
        json={
            "prompt": "Say hello",
            "threshold": 0.39,
            "drift_samples": 1,
            "enable_experimental_short_regen": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] == "SILENCE"
    assert calls["count"] == 1


def test_api_complete_skips_experimental_short_regen_when_disabled(monkeypatch):
    def fake_generate_candidate(*args, **kwargs):
        return "first candidate"

    calls = {"count": 0}

    def fake_score_candidate_runtime(prompt, candidate, threshold, candidate_samples=None):
        calls["count"] += 1
        return {
            "drift": 0.40,
            "coherence": 0.80,
            "instability_score": 0.40,
            "threshold": threshold,
            "decision": "SILENCE",
            "release_output": None,
            "silence_token": api_main.SILENCE_TOKEN,
            "notes": ["initial_silence"],
        }

    monkeypatch.setattr(api_main, "generate_candidate", fake_generate_candidate)
    monkeypatch.setattr(api_main, "score_candidate_runtime", fake_score_candidate_runtime)

    response = client.post(
        "/por/complete",
        json={
            "prompt": "Say hello",
            "threshold": 0.39,
            "drift_samples": 1,
            "enable_experimental_short_regen": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] == "SILENCE"
    assert calls["count"] == 1


def test_api_complete_honors_backward_compatibility_alias_for_short_regen(monkeypatch):
    def fake_generate_candidate(*args, **kwargs):
        return "first candidate"

    calls = {"count": 0}

    def fake_score_candidate_runtime(prompt, candidate, threshold, candidate_samples=None):
        calls["count"] += 1
        return {
            "drift": 0.80,
            "coherence": 0.20,
            "instability_score": 0.80,
            "threshold": threshold,
            "decision": "SILENCE",
            "release_output": None,
            "silence_token": api_main.SILENCE_TOKEN,
            "notes": ["initial_silence"],
        }

    monkeypatch.setattr(api_main, "generate_candidate", fake_generate_candidate)
    monkeypatch.setattr(api_main, "score_candidate_runtime", fake_score_candidate_runtime)

    # Alias false should override primary flag true.
    response = client.post(
        "/por/complete",
        json={
            "prompt": "Say hello",
            "threshold": 0.39,
            "drift_samples": 1,
            "enable_experimental_short_regen": True,
            "enable_short_regen": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] == "SILENCE"
    assert calls["count"] == 1


def test_api_evaluate_returns_500_on_internal_failure(monkeypatch):
    def broken_score(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(api_main, "score_candidate_runtime", broken_score)

    response = client.post(
        "/por/evaluate",
        json={"prompt": "p", "candidate": "c"},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "por_evaluate_failed"


def test_api_complete_returns_500_on_internal_failure(monkeypatch):
    def broken_generate(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(api_main, "generate_candidate", broken_generate)

    response = client.post(
        "/por/complete",
        json={"prompt": "p"},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "por_complete_failed"


def test_api_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Silence-as-Control" in response.text
    assert "generation != release authority" in response.text
    assert "/por/evaluate" in response.text
    assert "Evaluate" in response.text
    assert "Decision" in response.text
    assert "Coherence" in response.text
    assert "Raw JSON" in response.text


def test_api_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

