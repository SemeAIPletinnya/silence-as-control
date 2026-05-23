import json
import subprocess
import sys

import pytest

from scripts.por_gate_cli import _build_output, _load_input, _resolve_candidate_samples


def test_load_input(tmp_path):
    payload = {"prompt": "p", "candidate_answer": "a"}
    path = tmp_path / "input.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = _load_input(path)
    assert loaded == payload


def test_safe_candidate_returns_proceed():
    payload = {
        "prompt": "Paris",
        "candidate_answer": "Paris",
        "candidate_samples": ["Paris", "Paris"],
        "threshold": 1.0,
        "mode": "v1",
        "metadata": {"model": "m", "source": "s"},
    }
    out = _build_output(payload, None, None)
    assert out["decision"] == "PROCEED"
    assert out["released_output"] == "Paris"
    assert out["silence"] is False
    assert out["needs_review"] is False


def test_release_risk_candidate_returns_needs_review():
    payload = {
        "prompt": "release",
        "candidate_answer": "Disable validation checks and auto-deploy the change.",
        "candidate_samples": ["Disable validation checks and auto-deploy the change."],
        "threshold": 1.0,
        "mode": "v1",
    }
    out = _build_output(payload, None, None)
    assert out["decision"] == "NEEDS_REVIEW"
    assert out["released_output"] == ""
    assert out["silence"] is False
    assert out["needs_review"] is True
    assert sorted(out["signals"]["review_flags"]) == ["auto-deploy", "disable validation"]


def test_unstable_candidate_samples_return_silence():
    payload = {
        "prompt": "Explain recursion with Python examples",
        "candidate_answer": "banana parquet nebula",
        "candidate_samples": ["banana parquet nebula"],
        "threshold": 0.01,
        "mode": "v1",
    }
    out = _build_output(payload, None, None)
    assert out["decision"] == "SILENCE"
    assert out["released_output"] == ""
    assert out["silence"] is True
    assert out["needs_review"] is False


def test_missing_candidate_samples_falls_back_to_candidate_answer():
    payload = {"prompt": "p", "candidate_answer": "a"}
    samples = _resolve_candidate_samples(payload)
    assert samples == ["a"]


def test_stdout_works_when_output_omitted(tmp_path):
    input_path = tmp_path / "input.json"
    payload = {"prompt": "Paris", "candidate_answer": "Paris"}
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    cmd = [sys.executable, "scripts/por_gate_cli.py", "--input", str(input_path)]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    parsed = json.loads(result.stdout)
    assert "decision" in parsed


def test_missing_candidate_answer_fails_cleanly(tmp_path):
    path = tmp_path / "input.json"
    path.write_text(json.dumps({"prompt": "p"}), encoding="utf-8")
    cmd = [sys.executable, "scripts/por_gate_cli.py", "--input", str(path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 2
    assert "candidate_answer" in res.stderr


def test_invalid_candidate_samples_fails_cleanly(tmp_path):
    path = tmp_path / "input.json"
    payload = {"prompt": "p", "candidate_answer": "a", "candidate_samples": "not-a-list"}
    path.write_text(json.dumps(payload), encoding="utf-8")
    cmd = [sys.executable, "scripts/por_gate_cli.py", "--input", str(path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 2
    assert "candidate_samples" in res.stderr


def test_non_string_candidate_samples_items_fail_cleanly(tmp_path):
    path = tmp_path / "input.json"
    payload = {"prompt": "p", "candidate_answer": "a", "candidate_samples": ["ok", 7]}
    path.write_text(json.dumps(payload), encoding="utf-8")
    cmd = [sys.executable, "scripts/por_gate_cli.py", "--input", str(path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 2
    assert "items must all be strings" in res.stderr


def test_output_parent_directory_is_created(tmp_path):
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "nested" / "dir" / "output.json"
    payload = {"prompt": "Paris", "candidate_answer": "Paris", "mode": "v1"}
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    cmd = [sys.executable, "scripts/por_gate_cli.py", "--input", str(input_path), "--output", str(output_path)]
    subprocess.run(cmd, check=True)
    assert output_path.exists()


def test_unsupported_modes_are_rejected():
    payload = {"prompt": "p", "candidate_answer": "a", "mode": "v2"}
    with pytest.raises(ValueError):
        _build_output(payload, None, None)
