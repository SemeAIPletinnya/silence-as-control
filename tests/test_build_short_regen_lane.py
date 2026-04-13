from __future__ import annotations

import pytest

from scripts import build_short_regen_lane as lane


def _sample_row(task_id: str) -> dict[str, object]:
    return {
        "task_id": task_id,
        "category": "edge",
        "prompt": "What is truth?",
        "output": "sample",
        "semantic_proxy_drift": 0.39,
        "length_ratio_drift": 1.0,
        "raw_quality_score": 0.64,
        "raw_success": True,
        "silence": True,
    }


def test_expected_borderline_pocket_count_and_maybe_ids_count() -> None:
    assert len(lane.FULL_BORDERLINE_POCKET_LABELS) == 16
    assert len(lane.MAYBE_SHORT_REGEN_TASK_IDS) == 8


def test_verify_expected_ids_exist_fails_when_missing() -> None:
    expected_ids = [task_id for task_id, _, _ in lane.FULL_BORDERLINE_POCKET_LABELS]
    rows = [_sample_row(task_id) for task_id in expected_ids[:-1]]

    with pytest.raises(ValueError, match="Missing expected borderline-pocket task_ids"):
        lane.verify_expected_ids_exist(rows)


def test_build_lane_rows_structure() -> None:
    rows_by_id = {
        task_id: _sample_row(task_id)
        for task_id, _, _ in lane.FULL_BORDERLINE_POCKET_LABELS
    }

    lane_rows = lane.build_lane_rows(rows_by_id)
    assert len(lane_rows) == 8

    for row in lane_rows:
        assert set(row.keys()) == set(lane.LANE_COLUMNS)
        assert row["manual_label"] == "MAYBE_SHORT_REGEN"
        assert row["task_id"] in lane.MAYBE_SHORT_REGEN_TASK_IDS


def test_build_pocket_label_rows_structure() -> None:
    pocket_rows = lane.build_pocket_label_rows()

    assert len(pocket_rows) == 16
    for row in pocket_rows:
        assert set(row.keys()) == {"task_id", "manual_label", "manual_notes"}

    maybe_ids = {row["task_id"] for row in pocket_rows if row["manual_label"] == "MAYBE_SHORT_REGEN"}
    assert maybe_ids == set(lane.MAYBE_SHORT_REGEN_TASK_IDS)
