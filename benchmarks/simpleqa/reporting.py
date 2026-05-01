from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from benchmarks.simpleqa.plot_results import build_threshold_tradeoff_plot

PER_EXAMPLE_CSV_FILENAME = "simpleqa_por_results.csv"
ERROR_AUDIT_CSV_FILENAME = "simpleqa_error_audit.csv"
PROBLEM_CASES_CSV_FILENAME = "simpleqa_problem_cases_deduped.csv"
THRESHOLD_SUMMARY_CSV_FILENAME = "simpleqa_threshold_summary.csv"
METRICS_JSON_FILENAME = "simpleqa_por_metrics.json"
TRADEOFF_PLOT_FILENAME = "simpleqa_threshold_tradeoff.png"

THRESHOLD_SUMMARY_FIELDNAMES = [
    "threshold",
    "total_examples",
    "answered_count",
    "silence_count",
    "answer_rate",
    "silence_rate",
    "accepted_correct_count",
    "accepted_wrong_count",
    "accepted_precision",
    "accepted_error_rate",
    "false_silence_count",
    "false_silence_rate",
]


def to_csv_value(v: Any) -> str:
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    if v is None:
        return ""
    return str(v)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: to_csv_value(v) for k, v in row.items()})


def build_artifact_paths(output_dir: Path) -> dict[str, Path]:
    return {
        "per_example_csv": output_dir / PER_EXAMPLE_CSV_FILENAME,
        "metrics_json": output_dir / METRICS_JSON_FILENAME,
        "threshold_summary_csv": output_dir / THRESHOLD_SUMMARY_CSV_FILENAME,
        "error_audit_csv": output_dir / ERROR_AUDIT_CSV_FILENAME,
        "problem_cases_deduped_csv": output_dir / PROBLEM_CASES_CSV_FILENAME,
        "tradeoff_plot": output_dir / TRADEOFF_PLOT_FILENAME,
    }


def write_threshold_summary(path: Path, threshold_metrics: list[Any]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=THRESHOLD_SUMMARY_FIELDNAMES)
        writer.writeheader()
        for tm in threshold_metrics:
            writer.writerow(asdict(tm))


def write_metrics_payload(path: Path, args: Any, por_samples: int, self_check_no_penalty: float, baseline_metrics: Any, threshold_metrics: list[Any], artifact_paths: dict[str, Path], plot_path: Path) -> None:
    payload = {
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "config": {
            "dataset_path": str(args.dataset_path),
            "provider": args.provider,
            "model": args.model,
            "max_examples": args.max_examples,
            "thresholds": args.thresholds,
            "question_field": args.question_field,
            "answer_field": args.answer_field,
            "answers_field": args.answers_field,
            "id_field": args.id_field,
            "separate_por_call": args.separate_por_call,
            "por_samples": por_samples,
            "baseline_temperature": args.baseline_temperature,
            "por_temperature": args.por_temperature,
            "por_mode": args.por_mode,
            "self_check_no_penalty": self_check_no_penalty,
            "experimental_short_regen_enabled": False,
        },
        "baseline": asdict(baseline_metrics),
        "thresholds": [asdict(tm) for tm in threshold_metrics],
        "artifacts": {
            "per_example_csv": str(artifact_paths["per_example_csv"]),
            "error_audit_csv": str(artifact_paths["error_audit_csv"]),
            "problem_cases_deduped_csv": str(artifact_paths["problem_cases_deduped_csv"]),
            "threshold_summary_csv": str(artifact_paths["threshold_summary_csv"]),
            "tradeoff_plot": str(plot_path),
        },
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_tradeoff_plot(threshold_summary_csv: Path, tradeoff_plot: Path) -> Path:
    return build_threshold_tradeoff_plot(threshold_summary_csv, tradeoff_plot)
