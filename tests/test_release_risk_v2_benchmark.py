import json
from pathlib import Path

from benchmarks.release_risk_v2.run_release_risk_v2 import FIXTURE_CANDIDATES_PATH, run

PROMPTS_PATH = Path("benchmarks/release_risk_v2/data/release_risk_prompts_50.jsonl")
REPLAY_PATH = Path("benchmarks/release_risk_v2/results/release_risk_v2_replay.jsonl")

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
    "num_generation_failures",
    "num_empty_candidates",
    "num_replayed_candidates",
}


def _load_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def test_release_risk_v2_fixture_contract() -> None:
    prompts = _load_jsonl(PROMPTS_PATH)
    assert len(prompts) == 50

    fixtures = _load_jsonl(FIXTURE_CANDIDATES_PATH)
    assert len(fixtures) == 50

    metrics = run(mode="fixture")
    assert REQUIRED_KEYS.issubset(metrics.keys())

    assert metrics["baseline_released"] == metrics["total_cases"] == 50
    assert metrics["sac_unsafe_released"] < metrics["baseline_unsafe_released"]
    assert metrics["generation_mode"] == "fixture"
    assert metrics["candidate_source"] == "fixture"
    assert metrics["num_generation_failures"] == 0

    replay_rows = _load_jsonl(REPLAY_PATH)
    assert replay_rows, "replay artifact should not be empty"
    assert "baseline_decision" in replay_rows[0]
    assert "sac_decision" in replay_rows[0]
