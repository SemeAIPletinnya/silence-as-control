import json
import subprocess
import sys
from pathlib import Path

from benchmarks.release_risk_v4_capture_candidates import (
    REQUIRED_RECORD_KEYS,
    build_fixture_candidates,
    main,
)
from benchmarks.release_risk_v4_fixture_replay import REPLAY_JSONL, SUMMARY_CSV, SUMMARY_JSON


def _load_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def test_build_fixture_candidates_have_required_shape() -> None:
    rows = build_fixture_candidates()
    assert rows
    for row in rows:
        assert REQUIRED_RECORD_KEYS.issubset(row.keys())
        assert row["candidate_source"] == "fixture"
        assert row["generation_mode"] == "fixture_capture"


def test_fixture_mode_writes_jsonl_to_caller_controlled_output(tmp_path: Path) -> None:
    output = tmp_path / "custom" / "capture.jsonl"
    rc = main(["--mode", "fixture", "--output", str(output)])
    assert rc == 0
    assert output.exists()

    rows = _load_jsonl(output)
    assert rows
    for row in rows:
        assert REQUIRED_RECORD_KEYS.issubset(row.keys())
        assert row["candidate_source"] == "fixture"
        assert row["generation_mode"] == "fixture_capture"


def test_fixture_mode_runs_without_api_key(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    output = tmp_path / "capture_no_key.jsonl"
    rc = main(["--mode", "fixture", "--output", str(output)])
    assert rc == 0
    assert output.exists()


def test_openai_mode_fails_as_unimplemented(tmp_path: Path) -> None:
    output = tmp_path / "openai_capture.jsonl"
    proc = subprocess.run(
        [
            sys.executable,
            "benchmarks/release_risk_v4_capture_candidates.py",
            "--mode",
            "openai",
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode != 0
    assert "not implemented" in proc.stdout.lower()
    assert not output.exists()


def test_capture_scaffold_does_not_overwrite_committed_replay_artifacts(tmp_path: Path) -> None:
    baseline_artifacts = {
        "summary_json": SUMMARY_JSON.read_bytes(),
        "summary_csv": SUMMARY_CSV.read_bytes(),
        "replay_jsonl": REPLAY_JSONL.read_bytes(),
    }

    output = tmp_path / "capture.jsonl"
    rc = main(["--mode", "fixture", "--output", str(output)])
    assert rc == 0
    assert output.exists()

    assert SUMMARY_JSON.read_bytes() == baseline_artifacts["summary_json"]
    assert SUMMARY_CSV.read_bytes() == baseline_artifacts["summary_csv"]
    assert REPLAY_JSONL.read_bytes() == baseline_artifacts["replay_jsonl"]
