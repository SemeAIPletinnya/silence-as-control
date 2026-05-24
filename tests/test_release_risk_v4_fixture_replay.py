import json
from pathlib import Path

from benchmarks.release_risk_v4_fixture_replay import (
    FIXTURE_PATH,
    REPLAY_JSONL,
    SUMMARY_CSV,
    SUMMARY_JSON,
    run,
    main,
)

REQUIRED_KEYS = {
    "total_cases",
    "baseline_released",
    "baseline_unsafe_released",
    "sac_proceed",
    "sac_needs_review",
    "sac_silence",
    "sac_unsafe_released",
    "unsafe_release_reduction_percent",
    "safe_proceed_rate",
    "candidate_source",
    "generation_mode",
    "provider",
    "model",
    "num_generation_failures",
    "num_empty_candidates",
    "num_replayed_candidates",
}

REQUIRED_RECORD_KEYS = {
    "prompt_id",
    "risk",
    "category",
    "prompt",
    "generated_candidate",
    "candidate_source",
    "generation_mode",
    "provider",
    "model",
    "generation_error",
    "expected_behavior",
    "metadata",
}


def _load_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def test_v4_fixture_contains_required_generated_candidate_metadata() -> None:
    rows = _load_jsonl(FIXTURE_PATH)
    assert rows
    for row in rows:
        assert REQUIRED_RECORD_KEYS.issubset(row.keys())
        assert row["candidate_source"] == "fixture"
        assert row["generation_mode"] == "fixture_replay"


def test_v4_fixture_replay_runs_without_provider_keys_and_has_stable_summary_shape() -> None:
    metrics = run()
    assert REQUIRED_KEYS.issubset(metrics.keys())
    assert metrics["candidate_source"] == "fixture"
    assert metrics["generation_mode"] == "fixture_replay"
    assert metrics["provider"] is None

    assert metrics["baseline_released"] == metrics["total_cases"] == metrics["num_replayed_candidates"]


def test_v4_replay_artifact_contains_decisions_and_metadata() -> None:
    run()
    replay_rows = _load_jsonl(REPLAY_JSONL)
    assert replay_rows
    first = replay_rows[0]
    assert "baseline_decision" in first
    assert "sac_decision" in first
    assert "review_flags" in first
    assert "metadata" in first


def test_v4_fixture_replay_treats_null_generated_candidate_as_empty(tmp_path: Path) -> None:
    fixture_path = tmp_path / "fixture.jsonl"
    fixture_path.write_text(
        json.dumps(
            {
                "prompt_id": "null-candidate",
                "risk": "safe",
                "category": "other",
                "prompt": "say hello",
                "generated_candidate": None,
                "candidate_source": "fixture",
                "generation_mode": "fixture_replay",
                "provider": None,
                "model": None,
                "generation_error": None,
                "expected_behavior": "PROCEED",
                "metadata": {},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    baseline_artifacts = {
        "summary_json": SUMMARY_JSON.read_bytes(),
        "summary_csv": SUMMARY_CSV.read_bytes(),
        "replay_jsonl": REPLAY_JSONL.read_bytes(),
    }

    metrics = run(fixture_path=fixture_path, results_dir=tmp_path / "results")
    assert metrics["total_cases"] == 1
    assert metrics["num_empty_candidates"] == 1
    assert metrics["provider"] is None

    assert SUMMARY_JSON.read_bytes() == baseline_artifacts["summary_json"]
    assert SUMMARY_CSV.read_bytes() == baseline_artifacts["summary_csv"]
    assert REPLAY_JSONL.read_bytes() == baseline_artifacts["replay_jsonl"]


def test_v4_fixture_replay_main_defaults_to_fixture_path(tmp_path: Path) -> None:
    results_dir = tmp_path / "default-results"
    exit_code = main(["--results-dir", str(results_dir)])
    assert exit_code == 0
    assert (results_dir / "release_risk_v4_summary.json").exists()
    summary = json.loads((results_dir / "release_risk_v4_summary.json").read_text(encoding="utf-8"))
    assert summary["candidate_source"] == "fixture"
    assert summary["generation_mode"] == "fixture_replay"


def test_v4_fixture_replay_main_honors_custom_input_and_results_dir(tmp_path: Path) -> None:
    tmp_input = tmp_path / "capture.jsonl"
    tmp_results = tmp_path / "custom-results"
    tmp_input.write_text(
        json.dumps(
            {
                "prompt_id": "capture-1",
                "risk": "safe",
                "category": "other",
                "prompt": "ping",
                "generated_candidate": "pong",
                "candidate_source": "generated",
                "generation_mode": "fixture_capture",
                "provider": None,
                "model": "custom-test-model",
                "generation_error": None,
                "expected_behavior": "PROCEED",
                "metadata": {},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    baseline_summary = SUMMARY_JSON.read_bytes()
    baseline_csv = SUMMARY_CSV.read_bytes()
    baseline_replay = REPLAY_JSONL.read_bytes()

    exit_code = main(["--input", str(tmp_input), "--results-dir", str(tmp_results)])
    assert exit_code == 0

    summary_path = tmp_results / "release_risk_v4_summary.json"
    replay_path = tmp_results / "release_risk_v4_replay.jsonl"
    assert summary_path.exists()
    assert replay_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["generation_mode"] == "fixture_capture"
    assert summary["model"] == "custom-test-model"

    assert SUMMARY_JSON.read_bytes() == baseline_summary
    assert SUMMARY_CSV.read_bytes() == baseline_csv
    assert REPLAY_JSONL.read_bytes() == baseline_replay
