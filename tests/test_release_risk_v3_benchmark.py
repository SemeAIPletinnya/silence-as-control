import json
import subprocess
import sys
from pathlib import Path

from benchmarks.release_risk_v3.generate_candidates_v3 import DEFAULT_OUTPUT_PATH
from benchmarks.release_risk_v3.run_release_risk_v3 import (
    FIXTURE_CANDIDATES_PATH,
    REPLAY_JSONL,
    run,
)

PROMPTS_PATH = Path("benchmarks/release_risk_v3/data/release_risk_prompts_50.jsonl")

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


def _load_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def test_release_risk_v3_fixture_contract() -> None:
    prompts = _load_jsonl(PROMPTS_PATH)
    assert len(prompts) == 50

    fixtures = _load_jsonl(FIXTURE_CANDIDATES_PATH)
    assert len(fixtures) == 50

    result = subprocess.run(
        [
            sys.executable,
            "benchmarks/release_risk_v3/generate_candidates_v3.py",
            "--mode",
            "fixture",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert DEFAULT_OUTPUT_PATH.exists()

    provider_result = subprocess.run(
        [
            sys.executable,
            "benchmarks/release_risk_v3/generate_candidates_v3.py",
            "--mode",
            "provider",
            "--model",
            "placeholder-model",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert provider_result.returncode != 0
    assert "scaffold-only" in provider_result.stderr + provider_result.stdout

    local_result = subprocess.run(
        [
            sys.executable,
            "benchmarks/release_risk_v3/generate_candidates_v3.py",
            "--mode",
            "local",
            "--model",
            "placeholder-local-model",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert local_result.returncode != 0
    assert "scaffold-only" in local_result.stderr + local_result.stdout


def test_release_risk_v3_fixture_rejects_mismatched_prompts(tmp_path: Path) -> None:
    mismatched_prompts = tmp_path / "mismatched_prompts.jsonl"
    fixture_prompts = _load_jsonl(PROMPTS_PATH)
    fixture_prompts[0]["prompt_id"] = "rrv3-mismatch"

    with mismatched_prompts.open("w", encoding="utf-8") as handle:
        for row in fixture_prompts:
            handle.write(json.dumps(row) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "benchmarks/release_risk_v3/generate_candidates_v3.py",
            "--mode",
            "fixture",
            "--prompts",
            str(mismatched_prompts),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Prompt set mismatch" in result.stderr + result.stdout


def test_release_risk_v3_high_risk_disable_cases_stay_needs_review() -> None:
    metrics = run(mode="fixture")
    assert REQUIRED_KEYS.issubset(metrics.keys())

    replay_rows = _load_jsonl(REPLAY_JSONL)
    targets = {"disable_validation", "disable_audit_logs", "auto_deploy"}
    filtered_rows = [
        row
        for row in replay_rows
        if row["risk"] == "high_risk" and row["category"] in targets
    ]

    assert filtered_rows, "expected high-risk disable/auto_deploy fixture rows"
    assert all(row["sac_decision"] == "NEEDS_REVIEW" for row in filtered_rows)


def test_release_risk_v3_run_fixture_outputs_metrics() -> None:
    metrics = run(mode="fixture")
    assert REQUIRED_KEYS.issubset(metrics.keys())
    assert metrics["baseline_released"] == metrics["total_cases"] == 50
    assert metrics["sac_unsafe_released"] < metrics["baseline_unsafe_released"]
    assert metrics["provider"] is None
    assert metrics["model"] == "fixture-generated-candidates-v1"
    assert metrics["num_generation_failures"] == 0

    replay_rows = _load_jsonl(REPLAY_JSONL)
    assert replay_rows, "replay artifact should not be empty"
    first = replay_rows[0]
    assert "baseline_decision" in first
    assert "sac_decision" in first
    assert "provider" in first
    assert "model" in first
    assert "generation_error" in first
