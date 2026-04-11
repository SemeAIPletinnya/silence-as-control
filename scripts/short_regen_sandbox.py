from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

DEFAULT_INPUT = Path("reports/borderline_maybe_short_regen.csv")
DEFAULT_OUTPUT = Path("reports/short_regen_sandbox_results.jsonl")
DEFAULT_REPORT = Path("reports/short_regen_sandbox_report.md")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")

RETRY_GUIDANCE = (
    "Answer briefly and directly. "
    "Use no more than 2-4 sentences. "
    "Do not add optional elaboration, frameworks, or extra branches. "
    "Do not include long philosophical digressions. "
    "Prefer a compact, semantically useful answer."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a sandbox short-regeneration experiment on borderline MAYBE_SHORT_REGEN rows."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help=f"Input CSV (default: {DEFAULT_INPUT})")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help=f"Output JSONL (default: {DEFAULT_OUTPUT})")
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help=f"Optional markdown report path (default: {DEFAULT_REPORT})",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip writing markdown report.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"OpenAI model name (default: {DEFAULT_MODEL})",
    )
    return parser.parse_args()


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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_report(path: Path, rows: list[dict[str, Any]], total: int, succeeded: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "# Short Regen Sandbox Report",
        "",
        "This is a sandbox experiment artifact only. It is not a primitive-core change.",
        "",
        f"- Total cases processed: **{total}**",
        f"- Retry calls succeeded: **{succeeded}**",
        "",
        "| task_id | retry_output (first line) |",
        "|---|---|",
    ]

    for row in rows:
        task_id = row.get("task_id", "")
        retry_output = truncate_one_line(str(row.get("retry_output", "")))
        lines.append(f"| {task_id} | {retry_output} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_result_row(row: dict[str, str]) -> dict[str, Any]:
    return {
        "task_id": row.get("task_id", ""),
        "original_prompt": row.get("prompt", ""),
        "original_output": row.get("output", ""),
        "retry_output": "",
        "retry_prompt": "",
        "manual_label": row.get("manual_label", ""),
        "semantic_proxy_drift": row.get("semantic_proxy_drift", ""),
        "length_ratio_drift": row.get("length_ratio_drift", ""),
        "raw_quality_score": row.get("raw_quality_score", ""),
        "notes": "",
    }


def main() -> int:
    args = parse_args()

    if not args.input.exists():
        print(f"ERROR: Input CSV not found: {args.input}")
        return 1

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY is not set.")
        return 1

    try:
        rows = load_rows(args.input)
    except Exception as exc:
        print(f"ERROR: Failed to read CSV {args.input}: {exc}")
        return 1

    client = OpenAI(api_key=api_key)

    results: list[dict[str, Any]] = []
    succeeded = 0

    for idx, row in enumerate(rows, start=1):
        result = make_result_row(row)
        try:
            original_prompt = result["original_prompt"]
            if not original_prompt:
                raise ValueError("missing prompt")

            retry_prompt, retry_output = call_short_retry(
                client,
                model=args.model,
                original_prompt=original_prompt,
            )

            result["retry_prompt"] = retry_prompt
            result["retry_output"] = retry_output
            succeeded += 1
        except Exception as exc:
            result["notes"] = f"retry_failed: {exc}"

        if not result["task_id"]:
            result["notes"] = (result.get("notes", "") + "; missing task_id").strip("; ")

        results.append(result)
        print(f"[{idx}/{len(rows)}] task_id={result.get('task_id', '')} done")

    try:
        write_jsonl(args.output, results)
    except Exception as exc:
        print(f"ERROR: Failed to write JSONL {args.output}: {exc}")
        return 1

    if not args.no_report:
        try:
            write_report(args.report, results, total=len(rows), succeeded=succeeded)
        except Exception as exc:
            print(f"WARNING: Failed to write report {args.report}: {exc}")

    print("\n=== short_regen_sandbox summary ===")
    print(f"Rows loaded: {len(rows)}")
    print(f"Retry attempts succeeded: {succeeded}")
    print(f"Output written: {args.output}")
    if not args.no_report:
        print(f"Report written: {args.report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
