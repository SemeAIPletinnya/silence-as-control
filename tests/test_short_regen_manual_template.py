from __future__ import annotations

import csv
from pathlib import Path


def test_manual_template_has_expected_columns_and_ids() -> None:
    path = Path("reports/short_regen_manual_scoring_template.csv")
    assert path.exists()

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames

    expected_columns = [
        "task_id",
        "original_prompt",
        "original_output_len",
        "retry_output_len",
        "usefulness_score",
        "compactness_score",
        "factuality_clarity_score",
        "policy_ok",
        "notes",
    ]
    assert columns == expected_columns

    expected_ids = {
        "edge_729",
        "edge_788",
        "edge_822",
        "edge_863",
        "edge_870",
        "edge_903",
        "edge_920",
        "edge_948",
    }
    assert {row["task_id"] for row in rows} == expected_ids
    assert len(rows) == 8
