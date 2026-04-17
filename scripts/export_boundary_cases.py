"""Export curated boundary-pocket evidence for paper packaging."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

DEFAULT_INPUT = Path("reports/borderline_maybe_short_regen.csv")
DEFAULT_OUTPUT_CSV = Path("paper/cases/borderline_maybe_short_regen.csv")
DEFAULT_OUTPUT_JSON = Path("paper/cases/borderline_maybe_short_regen_summary.json")

REQUIRED_COLUMNS = {
    "task_id",
    "prompt",
    "semantic_proxy_drift",
    "raw_quality_score",
    "raw_success",
    "silence",
    "manual_label",
    "manual_notes",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Export boundary MAYBE_SHORT_REGEN cases for paper packaging.")
    p.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    p.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    p.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    return p.parse_args()


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing source CSV: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"Source CSV has no rows: {path}")
    missing = sorted(REQUIRED_COLUMNS - set(rows[0].keys()))
    if missing:
        raise KeyError(f"Source CSV missing required columns: {missing}")
    return rows


def str_to_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def compute_summary(rows: list[dict[str, str]], source: Path) -> dict[str, object]:
    drifts = [float(r["semantic_proxy_drift"]) for r in rows]
    quality = [float(r["raw_quality_score"]) for r in rows]
    raw_success_true = sum(1 for r in rows if str_to_bool(r["raw_success"]))
    silence_true = sum(1 for r in rows if str_to_bool(r["silence"]))
    labels = sorted({r["manual_label"] for r in rows})

    return {
        "source_csv": str(source),
        "case_count": len(rows),
        "drift_min": round(min(drifts), 3),
        "drift_max": round(max(drifts), 3),
        "raw_quality_min": round(min(quality), 3),
        "raw_quality_max": round(max(quality), 3),
        "raw_success_true": raw_success_true,
        "silence_true": silence_true,
        "manual_labels": labels,
        "all_raw_success_and_silenced": raw_success_true == len(rows) and silence_true == len(rows),
    }


def write_outputs(csv_path: Path, json_path: Path, rows: list[dict[str, str]], summary: dict[str, object]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        rows = load_rows(args.input)
        summary = compute_summary(rows, args.input)
        write_outputs(args.output_csv, args.output_json, rows, summary)
    except Exception as exc:
        print(f"ERROR: failed to export boundary cases: {exc}")
        return 1

    print(f"Wrote {len(rows)} boundary rows -> {args.output_csv}")
    print(f"Wrote summary -> {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
