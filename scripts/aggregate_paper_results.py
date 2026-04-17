from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunSpec:
    label: str
    path: Path


DEFAULT_SCALE_RUNS = [
    RunSpec("35_tasks_t0.30", Path("reports/eval_35_tasks.jsonl")),
    RunSpec("100_tasks_t0.30", Path("reports/eval_100_tasks.jsonl")),
    RunSpec("300_tasks_t0.35", Path("reports/eval_run4_300_threshold_035.jsonl")),
    RunSpec("1000_tasks_t0.39", Path("reports/eval_run6_1000_threshold_039.jsonl")),
]

DEFAULT_THRESHOLD_SWEEP = [
    RunSpec("1000_tasks_t0.35", Path("reports/eval_run5_1000_threshold_035.jsonl")),
    RunSpec("1000_tasks_t0.39", Path("reports/eval_run6_1000_threshold_039.jsonl")),
    RunSpec("1000_tasks_t0.42", Path("reports/eval_run5_1000_threshold_042.jsonl")),
    RunSpec("1000_tasks_t0.43", Path("reports/eval_run5_1000_threshold_043.jsonl")),
]


FIELDS = [
    "run_label",
    "source_file",
    "task_count",
    "silence_threshold",
    "coverage",
    "silence_rate",
    "accepted_precision",
    "risk_capture",
    "accepted_count",
    "silenced_count",
    "raw_fail_count",
    "silenced_raw_fail_count",
    "silenced_raw_success_count",
    "accepted_raw_success_count",
    "accepted_raw_fail_count",
    "avg_drift_accepted",
    "avg_drift_silenced",
    "drift_separation",
]


def load_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        raise ValueError(f"Input file has no rows: {path}")
    return rows


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def summarize_run(spec: RunSpec) -> dict[str, object]:
    rows = load_rows(spec.path)
    required = {"silence", "raw_success", "semantic_proxy_drift", "silence_threshold"}
    missing = [k for k in required if k not in rows[0]]
    if missing:
        raise KeyError(f"Missing required fields in {spec.path}: {missing}")

    silenced = [r for r in rows if bool(r["silence"])]
    accepted = [r for r in rows if not bool(r["silence"])]
    raw_fails = [r for r in rows if not bool(r["raw_success"])]
    silenced_raw_fails = [r for r in silenced if not bool(r["raw_success"])]
    silenced_raw_success = [r for r in silenced if bool(r["raw_success"])]
    accepted_raw_success = [r for r in accepted if bool(r["raw_success"])]
    accepted_raw_fail = [r for r in accepted if not bool(r["raw_success"])]

    drift_accepted = _avg([float(r["semantic_proxy_drift"]) for r in accepted])
    drift_silenced = _avg([float(r["semantic_proxy_drift"]) for r in silenced])
    drift_separation = _safe_div(drift_silenced, drift_accepted) if drift_accepted else 0.0

    threshold_values = sorted({float(r["silence_threshold"]) for r in rows})
    threshold_repr = str(threshold_values[0]) if len(threshold_values) == 1 else ",".join(map(str, threshold_values))

    return {
        "run_label": spec.label,
        "source_file": str(spec.path),
        "task_count": len(rows),
        "silence_threshold": threshold_repr,
        "coverage": round(_safe_div(len(accepted), len(rows)), 4),
        "silence_rate": round(_safe_div(len(silenced), len(rows)), 4),
        "accepted_precision": round(_safe_div(len(accepted_raw_success), len(accepted)), 4),
        "risk_capture": round(_safe_div(len(silenced_raw_fails), len(raw_fails)), 4),
        "accepted_count": len(accepted),
        "silenced_count": len(silenced),
        "raw_fail_count": len(raw_fails),
        "silenced_raw_fail_count": len(silenced_raw_fails),
        "silenced_raw_success_count": len(silenced_raw_success),
        "accepted_raw_success_count": len(accepted_raw_success),
        "accepted_raw_fail_count": len(accepted_raw_fail),
        "avg_drift_accepted": round(drift_accepted, 4),
        "avg_drift_silenced": round(drift_silenced, 4),
        "drift_separation": round(drift_separation, 4),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Aggregate paper metrics from tracked JSONL artifacts.")
    p.add_argument(
        "--scale-out",
        type=Path,
        default=Path("paper/figures/results_by_run_scale.csv"),
        help="Output CSV for run-scale summary.",
    )
    p.add_argument(
        "--threshold-out",
        type=Path,
        default=Path("paper/figures/results_1000_threshold_sweep.csv"),
        help="Output CSV for 1000-task threshold sweep summary.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    scale_rows = [summarize_run(spec) for spec in DEFAULT_SCALE_RUNS]
    threshold_rows = [summarize_run(spec) for spec in DEFAULT_THRESHOLD_SWEEP]

    write_csv(args.scale_out, scale_rows)
    write_csv(args.threshold_out, threshold_rows)

    print(f"Wrote {len(scale_rows)} rows -> {args.scale_out}")
    print(f"Wrote {len(threshold_rows)} rows -> {args.threshold_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
