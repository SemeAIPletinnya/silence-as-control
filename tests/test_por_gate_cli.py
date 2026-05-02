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


def test_output_shape_proceed():
    payload = {
        "prompt": "Paris",
        "candidate_answer": "Paris",
        "candidate_samples": ["Paris", "Paris"],
        "threshold": 0.39,
        "mode": "v1",
        "metadata": {"model": "m", "source": "s"},
    }
    out = _build_output(payload, None, None)
    assert out["decision"] == "PROCEED"
    assert out["released_output"] == "Paris"
    assert out["silence"] is False
    assert out["mode"] == "v1"
    assert set(out["signals"].keys()) == {"drift", "coherence", "instability"}


def test_output_shape_silence():
    payload = {
        "prompt": "Explain recursion with Python examples",
        "candidate_answer": "banana parquet nebula",
        "candidate_samples": ["banana parquet nebula"],
        "threshold": 0.01,
        "mode": "v1",
        "metadata": {"model": "m", "source": "s"},
    }
    out = _build_output(payload, None, None)
    assert out["decision"] == "SILENCE"
    assert out["released_output"] is None
    assert out["silence"] is True


def test_missing_candidate_samples_falls_back_to_candidate_answer():
    payload = {"prompt": "p", "candidate_answer": "a"}
    samples = _resolve_candidate_samples(payload)
    assert samples == ["a"]


def test_cli_writes_output_json(tmp_path):
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.json"
    payload = {
        "prompt": "Paris",
        "candidate_answer": "Paris",
        "threshold": 0.39,
        "mode": "v1",
        "metadata": {"model": "m", "source": "s"},
    }
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    cmd = [
        sys.executable,
        "scripts/por_gate_cli.py",
        "--input",
        str(input_path),
        "--output",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)
    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert "decision" in result
    assert "signals" in result


def test_unsupported_modes_are_rejected():
    payload = {"prompt": "p", "candidate_answer": "a", "mode": "v2"}
    with pytest.raises(ValueError):
        _build_output(payload, None, None)



def test_load_input_rejects_missing_required_fields(tmp_path):
    path = tmp_path / "input.json"
    path.write_text(json.dumps({"prompt": "p"}), encoding="utf-8")
    with pytest.raises(ValueError, match="input JSON must include 'prompt' and 'candidate_answer'"):
        _load_input(path)

