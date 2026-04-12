from __future__ import annotations

import csv
import json
from pathlib import Path

SOURCE_JSONL = Path("reports/eval_run6_1000_threshold_039.jsonl")
MAYBE_SHORT_REGEN_CSV = Path("reports/borderline_maybe_short_regen.csv")
POCKET_LABELS_CSV = Path("reports/borderline_pocket_labels.csv")

FULL_BORDERLINE_POCKET_LABELS: list[tuple[str, str, str]] = [
    ("edge_946", "RECOVERABLE", "Near-boundary recoverable case."),
    ("edge_913", "RECOVERABLE", "Near-boundary recoverable case."),
    ("good_213", "RECOVERABLE", "Near-boundary recoverable case."),
    ("good_141", "RECOVERABLE", "Near-boundary recoverable case."),
    ("good_62", "RECOVERABLE", "Near-boundary recoverable case."),
    (
        "edge_729",
        "MAYBE_SHORT_REGEN",
        "Boundary pocket lane; short-regeneration sandbox input.",
    ),
    (
        "edge_788",
        "MAYBE_SHORT_REGEN",
        "Boundary pocket lane; short-regeneration sandbox input.",
    ),
    (
        "edge_822",
        "MAYBE_SHORT_REGEN",
        "Boundary pocket lane; short-regeneration sandbox input.",
    ),
    (
        "edge_863",
        "MAYBE_SHORT_REGEN",
        "Boundary pocket lane; short-regeneration sandbox input.",
    ),
    (
        "edge_870",
        "MAYBE_SHORT_REGEN",
        "Boundary pocket lane; short-regeneration sandbox input.",
    ),
    (
        "edge_903",
        "MAYBE_SHORT_REGEN",
        "Boundary pocket lane; short-regeneration sandbox input.",
    ),
    (
        "edge_920",
        "MAYBE_SHORT_REGEN",
        "Boundary pocket lane; short-regeneration sandbox input.",
    ),
    (
        "edge_948",
        "MAYBE_SHORT_REGEN",
        "Boundary pocket lane; short-regeneration sandbox input.",
    ),
    ("bad_474", "KEEP_SILENCE", "Near-boundary case that should remain silenced."),
    ("bad_572", "KEEP_SILENCE", "Near-boundary case that should remain silenced."),
    ("bad_457", "KEEP_SILENCE", "Near-boundary case that should remain silenced."),
]

MAYBE_SHORT_REGEN_TASK_IDS = [
    "edge_729",
    "edge_788",
    "edge_822",
    "edge_863",
    "edge_870",
    "edge_903",
    "edge_920",
    "edge_948",
]

LANE_COLUMNS = [
    "task_id",
    "category",
    "prompt",
    "output",
    "semantic_proxy_drift",
    "length_ratio_drift",
    "raw_quality_score",
    "raw_success",
    "silence",
    "manual_label",
    "manual_notes",
]


def load_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def verify_expected_ids_exist(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    rows_by_id = {str(row.get("task_id", "")): row for row in rows}
    expected_ids = {task_id for task_id, _, _ in FULL_BORDERLINE_POCKET_LABELS}
    missing_ids = sorted(expected_ids - set(rows_by_id))
    if missing_ids:
        raise ValueError(f"Missing expected borderline-pocket task_ids: {missing_ids}")
    return rows_by_id


def build_lane_rows(rows_by_id: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    notes_by_id = {
        task_id: note
        for task_id, label, note in FULL_BORDERLINE_POCKET_LABELS
        if label == "MAYBE_SHORT_REGEN"
    }
    lane_rows: list[dict[str, object]] = []
    for task_id in MAYBE_SHORT_REGEN_TASK_IDS:
        row = rows_by_id[task_id]
        lane_rows.append(
            {
                "task_id": row.get("task_id", ""),
                "category": row.get("category", ""),
                "prompt": row.get("prompt", ""),
                "output": row.get("output", ""),
                "semantic_proxy_drift": row.get("semantic_proxy_drift", ""),
                "length_ratio_drift": row.get("length_ratio_drift", ""),
                "raw_quality_score": row.get("raw_quality_score", ""),
                "raw_success": row.get("raw_success", ""),
                "silence": row.get("silence", ""),
                "manual_label": "MAYBE_SHORT_REGEN",
                "manual_notes": notes_by_id[task_id],
            }
        )
    return lane_rows


def build_pocket_label_rows() -> list[dict[str, str]]:
    return [
        {
            "task_id": task_id,
            "manual_label": manual_label,
            "manual_notes": manual_notes,
        }
        for task_id, manual_label, manual_notes in FULL_BORDERLINE_POCKET_LABELS
    ]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    rows = load_rows(SOURCE_JSONL)
    rows_by_id = verify_expected_ids_exist(rows)

    lane_rows = build_lane_rows(rows_by_id)
    pocket_rows = build_pocket_label_rows()

    write_csv(MAYBE_SHORT_REGEN_CSV, LANE_COLUMNS, lane_rows)
    write_csv(POCKET_LABELS_CSV, ["task_id", "manual_label", "manual_notes"], pocket_rows)

    print(f"Wrote {len(lane_rows)} rows -> {MAYBE_SHORT_REGEN_CSV}")
    print(f"Wrote {len(pocket_rows)} rows -> {POCKET_LABELS_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
