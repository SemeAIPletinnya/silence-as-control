import json
from pathlib import Path

from benchmarks.release_risk_v4_fixture_replay import FIXTURE_PATH, REPLAY_JSONL, run

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
