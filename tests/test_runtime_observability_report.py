"""Tests for the local runtime observability report."""

from __future__ import annotations

import json

from scripts import runtime_observability_report as report


def test_runtime_observability_report_summarizes_events(tmp_path, capsys):
    log_path = tmp_path / "events.jsonl"
    rows = [
        {
            "event_type": "por.evaluate",
            "decision": "PROCEED",
            "released": True,
            "silenced": False,
            "drift": 0.1,
            "coherence": 0.9,
            "instability_score": 0.1,
        },
        {
            "event_type": "por.complete",
            "decision": "SILENCE",
            "released": False,
            "silenced": True,
            "drift": 0.7,
            "coherence": 0.2,
            "instability_score": 0.75,
        },
    ]
    log_path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

    assert report.main(["--path", str(log_path)]) == 0

    output = capsys.readouterr().out
    assert "total_events: 2" in output
    assert 'events_by_type: {"por.complete": 1, "por.evaluate": 1}' in output
    assert "release_count: 1" in output
    assert "silence_count: 1" in output
    assert "average_drift: 0.4000" in output
    assert "average_coherence: 0.5500" in output
    assert "average_instability_score: 0.4250" in output


def test_runtime_observability_report_handles_missing_file(tmp_path, capsys):
    missing_path = tmp_path / "missing.jsonl"

    assert report.main(["--path", str(missing_path)]) == 0

    output = capsys.readouterr().out
    assert "total_events: 0" in output
    assert "release_count: 0" in output
    assert "silence_count: 0" in output


def test_runtime_observability_report_handles_malformed_jsonl(tmp_path, capsys):
    log_path = tmp_path / "events.jsonl"
    log_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "event_type": "por.evaluate",
                        "decision": "PROCEED",
                        "released": True,
                        "silenced": False,
                    }
                ),
                "not-json",
            ]
        ),
        encoding="utf-8",
    )

    assert report.main(["--path", str(log_path)]) == 0

    output = capsys.readouterr().out
    assert "total_events: 1" in output
    assert "malformed_lines: 1" in output


def test_runtime_observability_report_uses_env_path_when_no_cli_path(
    monkeypatch, tmp_path, capsys
):
    log_path = tmp_path / "env-events.jsonl"
    log_path.write_text(
        json.dumps(
            {
                "event_type": "por.evaluate",
                "decision": "PROCEED",
                "released": True,
                "silenced": False,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("POR_TELEMETRY_LOG_PATH", str(log_path))

    assert report.main([]) == 0

    output = capsys.readouterr().out
    assert f"path: {log_path}" in output
    assert "total_events: 1" in output
