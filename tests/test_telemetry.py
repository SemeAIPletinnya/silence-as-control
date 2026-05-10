"""Tests for local runtime telemetry and API integration."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

import api.main as api_main
from api.main import app
from silence_as_control.telemetry import write_runtime_event

client = TestClient(app)


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_telemetry_disabled_by_default_returns_false_and_does_not_create_file(
    monkeypatch, tmp_path
):
    log_path = tmp_path / "events.jsonl"
    monkeypatch.delenv("POR_TELEMETRY_ENABLED", raising=False)
    monkeypatch.setenv("POR_TELEMETRY_LOG_PATH", str(log_path))

    assert write_runtime_event({"event_type": "unit"}) is False
    assert not log_path.exists()


def test_telemetry_enabled_writes_one_jsonl_event_with_defaults(monkeypatch, tmp_path):
    log_path = tmp_path / "nested" / "events.jsonl"
    monkeypatch.setenv("POR_TELEMETRY_ENABLED", "true")
    monkeypatch.setenv("POR_TELEMETRY_LOG_PATH", str(log_path))

    assert write_runtime_event({"event_type": "unit", "drift": 0.1}) is True

    events = _read_jsonl(log_path)
    assert len(events) == 1
    assert events[0]["event_type"] == "unit"
    assert events[0]["drift"] == 0.1
    assert events[0]["schema_version"] == "1"
    assert "timestamp_utc" in events[0]


def test_telemetry_parent_directory_is_created(monkeypatch, tmp_path):
    log_path = tmp_path / "a" / "b" / "events.jsonl"
    monkeypatch.setenv("POR_TELEMETRY_ENABLED", "1")
    monkeypatch.setenv("POR_TELEMETRY_LOG_PATH", str(log_path))

    assert write_runtime_event({"event_type": "unit"}) is True
    assert log_path.exists()


def test_telemetry_failed_write_returns_false_and_does_not_raise(monkeypatch, tmp_path):
    log_path = tmp_path / "events_as_directory"
    log_path.mkdir()
    monkeypatch.setenv("POR_TELEMETRY_ENABLED", "yes")
    monkeypatch.setenv("POR_TELEMETRY_LOG_PATH", str(log_path))

    assert write_runtime_event({"event_type": "unit"}) is False


def test_api_evaluate_writes_telemetry_without_prompt_or_candidate_text(monkeypatch, tmp_path):
    log_path = tmp_path / "events.jsonl"
    prompt = "secret prompt text should not be logged"
    candidate = "secret candidate text should not be logged"
    monkeypatch.setenv("POR_TELEMETRY_ENABLED", "on")
    monkeypatch.setenv("POR_TELEMETRY_LOG_PATH", str(log_path))

    response = client.post(
        "/por/evaluate",
        json={
            "prompt": prompt,
            "candidate": candidate,
            "threshold": 0.39,
            "use_adaptive_threshold": False,
        },
    )

    assert response.status_code == 200
    event = _read_jsonl(log_path)[0]
    serialized_event = json.dumps(event, sort_keys=True)
    assert event["event_type"] == "por.evaluate"
    assert "drift" in event
    assert "coherence" in event
    assert "instability_score" in event
    assert event["threshold"] == 0.39
    assert event["decision"] == response.json()["decision"]
    assert event["prompt_length"] == len(prompt)
    assert event["candidate_length"] == len(candidate)
    assert prompt not in serialized_event
    assert candidate not in serialized_event


def test_api_complete_writes_telemetry_without_prompt_or_candidate_text(monkeypatch, tmp_path):
    log_path = tmp_path / "events.jsonl"
    prompt = "complete secret prompt"
    candidate = "complete secret candidate"
    monkeypatch.setenv("POR_TELEMETRY_ENABLED", "1")
    monkeypatch.setenv("POR_TELEMETRY_LOG_PATH", str(log_path))

    def fake_generate_candidate(*args, **kwargs):
        return candidate

    def fake_score_candidate_runtime(prompt, candidate, threshold, candidate_samples=None):
        return {
            "drift": 0.10,
            "coherence": 0.95,
            "instability_score": 0.075,
            "threshold": threshold,
            "decision": "PROCEED",
            "release_output": candidate,
            "silence_token": None,
            "notes": ["stable"],
        }

    monkeypatch.setattr(api_main, "generate_candidate", fake_generate_candidate)
    monkeypatch.setattr(api_main, "score_candidate_runtime", fake_score_candidate_runtime)

    response = client.post(
        "/por/complete",
        json={"prompt": prompt, "threshold": 0.39, "drift_samples": 1},
    )

    assert response.status_code == 200
    event = _read_jsonl(log_path)[0]
    serialized_event = json.dumps(event, sort_keys=True)
    assert event["event_type"] == "por.complete"
    assert event["model"] == response.json()["model"]
    assert event["decision"] == "PROCEED"
    assert event["candidate_length"] == len(candidate)
    assert event["regenerated"] is False
    assert prompt not in serialized_event
    assert candidate not in serialized_event


def test_api_evaluate_telemetry_failure_does_not_break_endpoint(monkeypatch):
    def broken_write_runtime_event(event):
        raise RuntimeError("telemetry boom")

    monkeypatch.setattr(api_main, "write_runtime_event", broken_write_runtime_event)

    response = client.post(
        "/por/evaluate",
        json={"prompt": "Explain recursion", "candidate": "A function calls itself."},
    )

    assert response.status_code == 200
    assert "decision" in response.json()


def test_api_complete_omits_candidate_length_for_silenced_candidate(monkeypatch, tmp_path):
    log_path = tmp_path / "events.jsonl"
    prompt = "complete silenced prompt"
    candidate = "silenced candidate text should not be logged"
    monkeypatch.setenv("POR_TELEMETRY_ENABLED", "1")
    monkeypatch.setenv("POR_TELEMETRY_LOG_PATH", str(log_path))

    def fake_generate_candidate(*args, **kwargs):
        return candidate

    def fake_score_candidate_runtime(prompt, candidate, threshold, candidate_samples=None):
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
            "prompt": prompt,
            "threshold": 0.39,
            "drift_samples": 1,
            "enable_experimental_short_regen": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "SILENCE"
    event = _read_jsonl(log_path)[0]
    serialized_event = json.dumps(event, sort_keys=True)
    assert event["event_type"] == "por.complete"
    assert event["silenced"] is True
    assert "candidate_length" not in event
    assert prompt not in serialized_event
    assert candidate not in serialized_event
