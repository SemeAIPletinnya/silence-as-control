"""Integration tests for API endpoints with deterministic/mocked runtime behavior."""

from fastapi.testclient import TestClient

import api.main as api_main
from api.main import app


client = TestClient(app)


def test_integration_por_evaluate_deterministic_payload():
    response = client.post(
        "/por/evaluate",
        json={
            "prompt": "explain recursion",
            "candidate": "recursion is when a function calls itself",
            "threshold": 0.39,
            "use_adaptive_threshold": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["threshold"] == 0.39
    assert payload["decision"] in {"PROCEED", "SILENCE"}
    assert 0.0 <= payload["instability_score"] <= 1.0


def test_integration_por_complete_with_mocked_generate_candidate(monkeypatch):
    monkeypatch.setattr(api_main, "generate_candidate", lambda **kwargs: "deterministic candidate")

    response = client.post(
        "/por/complete",
        json={
            "prompt": "hello",
            "threshold": 1.0,
            "drift_samples": 1,
            "enable_experimental_short_regen": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] == "PROCEED"
    assert payload["candidate"] == "deterministic candidate"


def test_integration_experimental_margin_applies_only_when_enabled(monkeypatch):
    candidates = ["primary", "regen"]

    def fake_generate_candidate(**kwargs):
        return candidates.pop(0)

    call_index = {"count": 0}

    def fake_score(prompt, candidate, threshold, candidate_samples=None):
        call_index["count"] += 1
        if call_index["count"] == 1:
            return {
                "drift": 0.41,
                "coherence": 0.78,
                "instability_score": 0.405,
                "threshold": threshold,
                "decision": "SILENCE",
                "release_output": None,
                "silence_token": api_main.SILENCE_TOKEN,
                "notes": ["initial_silence"],
            }
        return {
            "drift": 0.1,
            "coherence": 0.95,
            "instability_score": 0.075,
            "threshold": threshold,
            "decision": "PROCEED",
            "release_output": candidate,
            "silence_token": None,
            "notes": ["regen_success"],
        }

    monkeypatch.setenv("POR_EXPERIMENTAL_MARGIN", "0.02")
    monkeypatch.setattr(api_main, "generate_candidate", fake_generate_candidate)
    monkeypatch.setattr(api_main, "score_candidate_runtime", fake_score)

    disabled = client.post(
        "/por/complete",
        json={
            "prompt": "hello",
            "threshold": 0.39,
            "drift_samples": 1,
            "enable_experimental_short_regen": False,
        },
    )
    assert disabled.status_code == 200
    assert disabled.json()["decision"] == "SILENCE"
    assert call_index["count"] == 1

    candidates[:] = ["primary", "regen"]
    call_index["count"] = 0

    enabled = client.post(
        "/por/complete",
        json={
            "prompt": "hello",
            "threshold": 0.39,
            "drift_samples": 1,
            "enable_experimental_short_regen": True,
        },
    )

    assert enabled.status_code == 200
    payload = enabled.json()
    assert payload["decision"] == "PROCEED"
    assert any("experimental_maybe_short_regen_attempted" in n for n in payload["notes"])
    assert call_index["count"] == 2
