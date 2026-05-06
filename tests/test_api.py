"""API tests across legacy, runtime, and experimental lanes."""

from fastapi.testclient import TestClient

import api.main as api_main
from api.main import app

client = TestClient(app)


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


def test_api_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

