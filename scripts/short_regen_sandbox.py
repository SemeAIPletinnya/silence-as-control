from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI

# Support both `python scripts/...` and module import paths.
sys.path.append(str(Path(__file__).resolve().parent))
from scoring_utils import compute_proxy_metrics, tokenize

DEFAULT_INPUT = Path("reports/borderline_maybe_short_regen.csv")
DEFAULT_OUTPUT = Path("reports/short_regen_sandbox_results.jsonl")
DEFAULT_REPORT = Path("reports/short_regen_sandbox_report.md")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")
RETRY_GUIDANCE_VERSION = "short_regen_v1"

# Extension-layer retry scoring threshold.
# This is sandbox-only and does not change primitive gating semantics.
RETRY_RAW_SUCCESS_QUALITY_THRESHOLD = 0.55

REQUIRED_INPUT_COLUMNS = {
    "task_id",
    "prompt",
    "output",
    "manual_label",
    "semantic_proxy_drift",
    "length_ratio_drift",
    "raw_quality_score",
}

RETRY_GUIDANCE = (
    "Answer briefly and directly. "
    "Use no more than 2-4 sentences. "
    "Do not add optional elaboration, frameworks, or extra branches. "
    "Do not include long philosophical digressions. "
    "Prefer a compact, semantically useful answer."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the MAYBE_SHORT_REGEN sandbox retry on a curated lane. "
            "This is extension-layer reproducibility tooling and does not change primitive thresholds or runtime behavior."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help=f"Input CSV (default: {DEFAULT_INPUT})")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help=f"Output JSONL (default: {DEFAULT_OUTPUT})")
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help=f"Markdown report path (default: {DEFAULT_REPORT})",
    )
    parser.add_argument("--no-report", action="store_true", help="Skip writing markdown report.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenAI model name (default: {DEFAULT_MODEL})")
    parser.add_argument(
        "--run-id",
        default="",
        help="Optional run identifier for reproducibility records. If omitted, a timestamped run id is generated.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Validate CSV schema and row integrity only. "
            "Dry-run does not call external APIs and does not fabricate retry outputs."
        ),
    )
    parser.add_argument(
        "--score-retries",
        action="store_true",
        help=(
            "Optionally compute retry-side proxy metrics for sandbox rows with retry output. "
            "These metrics are extension-layer measurements only, not primitive gating."
        ),
    )
    return parser.parse_args()


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"short-regen-{stamp}"


def get_git_sha() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        return ""


def build_retry_prompt(original_prompt: str) -> str:
    return f"{RETRY_GUIDANCE}\n\nOriginal prompt:\n{original_prompt.strip()}"


def truncate_one_line(text: str, max_len: int = 90) -> str:
    clean = " ".join((text or "").splitlines()).strip()
    if len(clean) <= max_len:
        return clean
    return clean[: max_len - 1].rstrip() + "…"


def call_short_retry(client: OpenAI, *, model: str, original_prompt: str) -> tuple[str, str]:
    retry_prompt = build_retry_prompt(original_prompt)
    response = client.responses.create(model=model, input=retry_prompt)
    retry_output = (getattr(response, "output_text", "") or "").strip()
    return retry_prompt, retry_output


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def validate_input_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    if not rows:
        errors.append("input contains zero rows")
        return errors

    columns = set(rows[0].keys())
    missing_columns = sorted(REQUIRED_INPUT_COLUMNS - columns)
    if missing_columns:
        errors.append(f"missing required columns: {missing_columns}")

    for idx, row in enumerate(rows, start=1):
        if not (row.get("task_id") or "").strip():
            errors.append(f"row {idx}: missing task_id")
        if not (row.get("prompt") or "").strip():
            errors.append(f"row {idx}: missing prompt")

    return errors


def build_run_metadata(args: argparse.Namespace, row_count: int) -> dict[str, Any]:
    run_id = args.run_id.strip() or default_run_id()
    return {
        "run_id": run_id,
        "run_timestamp_utc": now_utc_iso(),
        "model": args.model,
        "input_csv_path": str(args.input),
        "output_jsonl_path": str(args.output),
        "report_path": str(args.report),
        "retry_guidance_version": RETRY_GUIDANCE_VERSION,
        "git_sha": get_git_sha(),
        "dry_run": bool(args.dry_run),
        "score_retries": bool(args.score_retries),
        "input_row_count": row_count,
    }


def infer_expected_keywords_from_prompt(prompt: str, max_terms: int = 6) -> list[str]:
    """Build a small prompt-token keyword set for retry-side sandbox scoring."""
    tokens: list[str] = []
    for tok in tokenize(prompt):
        if tok not in tokens:
            tokens.append(tok)
    return tokens[:max_terms]


def maybe_add_retry_scoring(result: dict[str, Any]) -> None:
    original_prompt = str(result.get("original_prompt", ""))
    retry_output = str(result.get("retry_output", ""))
    if not retry_output.strip():
        return

    expected_keywords = infer_expected_keywords_from_prompt(original_prompt)
    metrics = compute_proxy_metrics(original_prompt, retry_output, expected_keywords)

    result["retry_task_integrity"] = metrics["task_integrity"]
    result["retry_hedging_score"] = metrics["hedging_score"]
    result["retry_contradiction_score"] = metrics["contradiction_score"]
    result["retry_token_overlap"] = metrics["token_overlap"]
    result["retry_length_ratio_drift"] = metrics["length_ratio_drift"]
    result["retry_semantic_proxy_drift"] = metrics["semantic_proxy_drift"]
    result["retry_raw_quality_score"] = metrics["raw_quality_score"]
    result["retry_raw_success"] = metrics["raw_quality_score"] >= RETRY_RAW_SUCCESS_QUALITY_THRESHOLD


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_report(
    path: Path,
    rows: list[dict[str, Any]],
    total: int,
    succeeded: int,
    metadata: dict[str, Any],
    validation_errors: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# Short Regen Sandbox Report",
        "",
        "This is sandbox reproducibility output only. It is not primitive-core evidence by itself.",
        "",
        "## Run metadata",
        "",
        f"- run_id: `{metadata.get('run_id', '')}`",
        f"- run_timestamp_utc: `{metadata.get('run_timestamp_utc', '')}`",
        f"- model: `{metadata.get('model', '')}`",
        f"- input_csv_path: `{metadata.get('input_csv_path', '')}`",
        f"- output_jsonl_path: `{metadata.get('output_jsonl_path', '')}`",
        f"- report_path: `{metadata.get('report_path', '')}`",
        f"- retry_guidance_version: `{metadata.get('retry_guidance_version', '')}`",
        f"- git_sha: `{metadata.get('git_sha', '')}`",
        f"- dry_run: `{metadata.get('dry_run', False)}`",
        f"- score_retries: `{metadata.get('score_retries', False)}`",
        "",
        "## Validation summary",
        "",
        f"- Total rows loaded: **{total}**",
        f"- Retry calls succeeded: **{succeeded}**",
        f"- Validation errors: **{len(validation_errors)}**",
    ]

    if metadata.get("score_retries"):
        scored_count = sum(1 for row in rows if "retry_raw_quality_score" in row)
        lines.append(f"- Retry rows with proxy scoring: **{scored_count}**")

    if validation_errors:
        lines.extend(["", "### Validation errors", ""])
        for err in validation_errors:
            lines.append(f"- {err}")

    lines.extend([
        "",
        "## Row results",
        "",
        "| task_id | status | retry_output (first line) |",
        "|---|---|---|",
    ])

    for row in rows:
        task_id = row.get("task_id", "")
        status = row.get("status", "")
        retry_output = truncate_one_line(str(row.get("retry_output", "")))
        lines.append(f"| {task_id} | {status} | {retry_output} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_result_row(row: dict[str, str], metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": metadata["run_id"],
        "run_timestamp_utc": metadata["run_timestamp_utc"],
        "model": metadata["model"],
        "input_csv_path": metadata["input_csv_path"],
        "output_jsonl_path": metadata["output_jsonl_path"],
        "report_path": metadata["report_path"],
        "retry_guidance_version": metadata["retry_guidance_version"],
        "git_sha": metadata["git_sha"],
        "dry_run": metadata["dry_run"],
        "score_retries": metadata["score_retries"],
        "task_id": row.get("task_id", "").strip(),
        "original_prompt": row.get("prompt", ""),
        "original_output": row.get("output", ""),
        "retry_prompt": "",
        "retry_output": "",
        "status": "pending",
        "error_note": "",
        "manual_label": row.get("manual_label", ""),
        "semantic_proxy_drift": row.get("semantic_proxy_drift", ""),
        "length_ratio_drift": row.get("length_ratio_drift", ""),
        "raw_quality_score": row.get("raw_quality_score", ""),
    }


def main() -> int:
    args = parse_args()

    if not args.input.exists():
        print(f"ERROR: Input CSV not found: {args.input}")
        return 1

    try:
        rows = load_rows(args.input)
    except Exception as exc:
        print(f"ERROR: Failed to read CSV {args.input}: {exc}")
        return 1

    validation_errors = validate_input_rows(rows)
    metadata = build_run_metadata(args, row_count=len(rows))

    if args.dry_run:
        print("DRY_RUN: validation-only mode (no external API calls).")
        print(f"Rows loaded: {len(rows)}")
        if validation_errors:
            print("Validation errors:")
            for err in validation_errors:
                print(f"- {err}")
        if not args.no_report:
            write_report(args.report, [], total=len(rows), succeeded=0, metadata=metadata, validation_errors=validation_errors)
            print(f"Dry-run report written: {args.report}")
        return 1 if validation_errors else 0

    if validation_errors:
        print("ERROR: Input validation failed.")
        for err in validation_errors:
            print(f"- {err}")
        return 1

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY is not set.")
        return 1

    client = OpenAI(api_key=api_key)

    results: list[dict[str, Any]] = []
    succeeded = 0

    for idx, row in enumerate(rows, start=1):
        result = make_result_row(row, metadata)
        missing_fields: list[str] = []
        if not result["task_id"]:
            missing_fields.append("task_id")
        if not str(result["original_prompt"]).strip():
            missing_fields.append("prompt")

        if missing_fields:
            result["status"] = "validation_error"
            result["error_note"] = f"missing required field(s): {', '.join(missing_fields)}"
            results.append(result)
            print(f"[{idx}/{len(rows)}] task_id={result.get('task_id', '')} validation_error")
            continue

        try:
            retry_prompt, retry_output = call_short_retry(
                client,
                model=args.model,
                original_prompt=str(result["original_prompt"]),
            )
            result["retry_prompt"] = retry_prompt
            result["retry_output"] = retry_output
            result["status"] = "retry_succeeded"
            if args.score_retries:
                maybe_add_retry_scoring(result)
            succeeded += 1
        except Exception as exc:
            result["status"] = "retry_failed"
            result["error_note"] = str(exc)

        results.append(result)
        print(f"[{idx}/{len(rows)}] task_id={result.get('task_id', '')} {result['status']}")

    try:
        write_jsonl(args.output, results)
    except Exception as exc:
        print(f"ERROR: Failed to write JSONL {args.output}: {exc}")
        return 1

    if not args.no_report:
        try:
            write_report(args.report, results, total=len(rows), succeeded=succeeded, metadata=metadata, validation_errors=[])
        except Exception as exc:
            print(f"WARNING: Failed to write report {args.report}: {exc}")

    print("\n=== short_regen_sandbox summary ===")
    print(f"Rows loaded: {len(rows)}")
    print(f"Retry attempts succeeded: {succeeded}")
    if args.score_retries:
        print("Retry-side proxy scoring: enabled (extension-layer only)")
    print(f"Output written: {args.output}")
    if not args.no_report:
        print(f"Report written: {args.report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
