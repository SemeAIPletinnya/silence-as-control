from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from scripts import short_regen_sandbox as sandbox


class _FakeResponse:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class _FakeClient:
    class _Responses:
        def create(self, *, model: str, input: str):
            return _FakeResponse("Compact retry answer")

    def __init__(self) -> None:
        self.responses = self._Responses()


def test_load_rows_handles_utf8_bom(tmp_path: Path) -> None:
    csv_path = tmp_path / "lane.csv"
    csv_path.write_text("\ufefftask_id,prompt,output\nedge_1,What is truth?,Original\n", encoding="utf-8")

    rows = sandbox.load_rows(csv_path)
    assert rows[0]["task_id"] == "edge_1"


def test_build_retry_prompt_includes_guidance_and_original_prompt() -> None:
    prompt = sandbox.build_retry_prompt("What is truth?")
    assert sandbox.RETRY_GUIDANCE in prompt
    assert "Original prompt:" in prompt
    assert "What is truth?" in prompt


def test_truncate_one_line_predictable() -> None:
    assert sandbox.truncate_one_line("hello\nworld", max_len=20) == "hello world"
    assert sandbox.truncate_one_line("abcdefghij", max_len=6).endswith("…")


def test_dry_run_mode_without_external_api(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    input_csv = tmp_path / "lane.csv"
    output_jsonl = tmp_path / "out.jsonl"
    report_md = tmp_path / "report.md"

    with input_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(sandbox.REQUIRED_INPUT_COLUMNS))
        writer.writeheader()
        writer.writerow(
            {
                "task_id": "edge_729",
                "prompt": "What is truth?",
                "output": "Original",
                "manual_label": "MAYBE_SHORT_REGEN",
                "semantic_proxy_drift": "0.397",
                "length_ratio_drift": "1.0",
                "raw_quality_score": "0.641",
            }
        )

    monkeypatch.setattr(
        "sys.argv",
        [
            "short_regen_sandbox.py",
            "--input",
            str(input_csv),
            "--output",
            str(output_jsonl),
            "--report",
            str(report_md),
            "--dry-run",
        ],
    )

    rc = sandbox.main()
    assert rc == 0
    assert not output_jsonl.exists()
    assert report_md.exists()


def test_make_result_row_schema_includes_required_fields() -> None:
    metadata = {
        "run_id": "run-1",
        "run_timestamp_utc": "2026-01-01T00:00:00Z",
        "model": "gpt-test",
        "input_csv_path": "reports/lane.csv",
        "output_jsonl_path": "reports/out.jsonl",
        "report_path": "reports/report.md",
        "retry_guidance_version": "short_regen_v1",
        "git_sha": "abc123",
        "dry_run": False,
        "score_retries": False,
    }
    row = {
        "task_id": "edge_729",
        "prompt": "What is truth?",
        "output": "Original",
        "manual_label": "MAYBE_SHORT_REGEN",
        "semantic_proxy_drift": "0.397",
        "length_ratio_drift": "1.0",
        "raw_quality_score": "0.641",
    }

    result = sandbox.make_result_row(row, metadata)
    required = {
        "run_id",
        "run_timestamp_utc",
        "model",
        "input_csv_path",
        "output_jsonl_path",
        "report_path",
        "retry_guidance_version",
        "git_sha",
        "dry_run",
        "task_id",
        "original_prompt",
        "original_output",
        "retry_prompt",
        "retry_output",
        "status",
        "error_note",
        "manual_label",
        "semantic_proxy_drift",
        "length_ratio_drift",
        "raw_quality_score",
    }
    assert required.issubset(set(result))


def test_validate_input_rows_missing_task_id_or_prompt() -> None:
    rows = [
        {
            "task_id": "",
            "prompt": "",
            "output": "x",
            "manual_label": "MAYBE_SHORT_REGEN",
            "semantic_proxy_drift": "0.4",
            "length_ratio_drift": "1.0",
            "raw_quality_score": "0.6",
        }
    ]

    errors = sandbox.validate_input_rows(rows)
    assert any("missing task_id" in err for err in errors)
    assert any("missing prompt" in err for err in errors)


def test_write_report_stable_table_structure(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    metadata = {
        "run_id": "run-1",
        "run_timestamp_utc": "2026-01-01T00:00:00Z",
        "model": "gpt-test",
        "input_csv_path": "in.csv",
        "output_jsonl_path": "out.jsonl",
        "report_path": str(report),
        "retry_guidance_version": "short_regen_v1",
        "git_sha": "abc123",
        "dry_run": False,
        "score_retries": False,
    }
    rows = [{"task_id": "edge_729", "status": "retry_succeeded", "retry_output": "one line"}]

    sandbox.write_report(report, rows, total=1, succeeded=1, metadata=metadata, validation_errors=[])

    content = report.read_text(encoding="utf-8")
    assert "| task_id | status | retry_output (first line) |" in content
    assert "|---|---|---|" in content
    assert "| edge_729 | retry_succeeded | one line |" in content


def test_retry_scoring_fields_present_when_enabled() -> None:
    metadata = {
        "run_id": "run-1",
        "run_timestamp_utc": "2026-01-01T00:00:00Z",
        "model": "gpt-test",
        "input_csv_path": "reports/lane.csv",
        "output_jsonl_path": "reports/out.jsonl",
        "report_path": "reports/report.md",
        "retry_guidance_version": "short_regen_v1",
        "git_sha": "abc123",
        "dry_run": False,
        "score_retries": True,
    }
    row = {
        "task_id": "edge_729",
        "prompt": "What is truth?",
        "output": "Original",
        "manual_label": "MAYBE_SHORT_REGEN",
        "semantic_proxy_drift": "0.397",
        "length_ratio_drift": "1.0",
        "raw_quality_score": "0.641",
    }
    result = sandbox.make_result_row(row, metadata)
    result["retry_output"] = "Truth is what matches reality."

    sandbox.maybe_add_retry_scoring(result)

    assert "retry_semantic_proxy_drift" in result
    assert "retry_raw_quality_score" in result
    assert "retry_raw_success" in result


def test_retry_scoring_fields_absent_when_disabled() -> None:
    metadata = {
        "run_id": "run-1",
        "run_timestamp_utc": "2026-01-01T00:00:00Z",
        "model": "gpt-test",
        "input_csv_path": "reports/lane.csv",
        "output_jsonl_path": "reports/out.jsonl",
        "report_path": "reports/report.md",
        "retry_guidance_version": "short_regen_v1",
        "git_sha": "abc123",
        "dry_run": False,
        "score_retries": False,
    }
    row = {
        "task_id": "edge_729",
        "prompt": "What is truth?",
        "output": "Original",
        "manual_label": "MAYBE_SHORT_REGEN",
        "semantic_proxy_drift": "0.397",
        "length_ratio_drift": "1.0",
        "raw_quality_score": "0.641",
    }
    result = sandbox.make_result_row(row, metadata)
    result["retry_output"] = "Truth is what matches reality."

    # Disabled path means scoring helper is not invoked.
    assert "retry_semantic_proxy_drift" not in result
    assert "retry_raw_quality_score" not in result
    assert "retry_raw_success" not in result
