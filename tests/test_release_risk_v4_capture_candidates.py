import json
import subprocess
import sys
from pathlib import Path

import benchmarks.release_risk_v4_capture_candidates as capture
from benchmarks.release_risk_v4_capture_candidates import (
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_URL,
    REQUIRED_RECORD_KEYS,
    OllamaGenerationResult,
    OllamaUnavailableError,
    build_fixture_candidates,
    build_ollama_candidates,
    generate_with_ollama,
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


class _FakeOllamaResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def test_generate_with_ollama_posts_expected_payload(monkeypatch) -> None:
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        seen["payload"] = json.loads(request.data.decode("utf-8"))
        seen["content_type"] = request.headers["Content-type"]
        return _FakeOllamaResponse(b'{"response": "generated text"}')

    monkeypatch.setattr(capture, "urlopen", fake_urlopen)

    result = generate_with_ollama(
        "Prompt text",
        model="qwen3:4b",
        ollama_url="http://localhost:11434/",
        timeout=12.5,
    )

    assert result == OllamaGenerationResult(candidate="generated text", generation_error=None)
    assert seen["url"] == "http://localhost:11434/api/generate"
    assert seen["timeout"] == 12.5
    assert seen["payload"] == {"model": "qwen3:4b", "prompt": "Prompt text", "stream": False}
    assert seen["content_type"] == "application/json"


def test_build_ollama_candidates_uses_fixture_prompts_and_replay_schema(monkeypatch) -> None:
    prompts = []

    def fake_generate(prompt: str, *, model: str, ollama_url: str, timeout: float):
        prompts.append((prompt, model, ollama_url, timeout))
        return OllamaGenerationResult(candidate=f"generated for {len(prompts)}", generation_error=None)

    monkeypatch.setattr(capture, "generate_with_ollama", fake_generate)

    rows = build_ollama_candidates(model="custom-model", ollama_url="http://ollama.test", timeout=3)
    fixtures = build_fixture_candidates()

    assert [seen[0] for seen in prompts] == [str(row["prompt"]) for row in fixtures]
    assert all(seen[1:] == ("custom-model", "http://ollama.test", 3) for seen in prompts)
    assert len(rows) == len(fixtures)
    for row, fixture in zip(rows, fixtures):
        assert REQUIRED_RECORD_KEYS.issubset(row.keys())
        assert row["prompt_id"] == fixture["prompt_id"]
        assert row["risk"] == fixture["risk"]
        assert row["category"] == fixture["category"]
        assert row["prompt"] == fixture["prompt"]
        assert row["candidate_answer"] == row["generated_candidate"]
        assert row["candidate_source"] == "ollama"
        assert row["generation_mode"] == "ollama_capture"
        assert row["provider"] == "ollama"
        assert row["model"] == "custom-model"
        assert row["generation_error"] is None
        assert row["generation_failure"] is False
        assert row["empty_candidate"] is False
        assert row["expected_behavior"] == fixture["expected_behavior"]


def test_ollama_mode_writes_jsonl_with_default_model(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "ollama_capture.jsonl"

    def fake_generate(prompt: str, *, model: str, ollama_url: str, timeout: float):
        assert model == DEFAULT_OLLAMA_MODEL
        assert ollama_url == DEFAULT_OLLAMA_URL
        assert timeout == 60.0
        return OllamaGenerationResult(candidate="generated candidate", generation_error=None)

    monkeypatch.setattr(capture, "generate_with_ollama", fake_generate)

    rc = main(["--mode", "ollama", "--output", str(output)])

    assert rc == 0
    rows = _load_jsonl(output)
    assert rows
    assert all(row["candidate_source"] == "ollama" for row in rows)
    assert all(row["generation_mode"] == "ollama_capture" for row in rows)
    assert all(row["model"] == DEFAULT_OLLAMA_MODEL for row in rows)


def test_ollama_generation_failure_records_empty_candidate(monkeypatch) -> None:
    def fake_generate(prompt: str, *, model: str, ollama_url: str, timeout: float):
        return OllamaGenerationResult(candidate="", generation_error="ollama_http_error_500")

    monkeypatch.setattr(capture, "generate_with_ollama", fake_generate)

    rows = build_ollama_candidates()

    assert rows
    assert all(row["generation_error"] == "ollama_http_error_500" for row in rows)
    assert all(row["generation_failure"] is True for row in rows)
    assert all(row["empty_candidate"] is True for row in rows)


def test_ollama_mode_unavailable_fails_without_output(tmp_path: Path, monkeypatch, capsys) -> None:
    output = tmp_path / "ollama_unavailable.jsonl"

    def fake_generate(prompt: str, *, model: str, ollama_url: str, timeout: float):
        raise OllamaUnavailableError("Unable to reach Ollama at http://localhost:11434/api/generate")

    monkeypatch.setattr(capture, "generate_with_ollama", fake_generate)

    rc = main(["--mode", "ollama", "--output", str(output)])

    assert rc == 2
    assert not output.exists()
    assert "unable to reach ollama" in capsys.readouterr().out.lower()
