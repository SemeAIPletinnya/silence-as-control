from __future__ import annotations

from scripts.scoring_utils import compute_proxy_metrics


def test_compute_proxy_metrics_deterministic_example() -> None:
    prompt = "What is truth?"
    output = "Truth matches reality and facts."
    expected_keywords = ["truth", "reality", "facts"]

    metrics = compute_proxy_metrics(prompt, output, expected_keywords)

    assert set(metrics) == {
        "task_integrity",
        "hedging_score",
        "contradiction_score",
        "token_overlap",
        "length_ratio_drift",
        "semantic_proxy_drift",
        "raw_quality_score",
    }
    assert 0.0 <= metrics["semantic_proxy_drift"] <= 1.0
    assert 0.0 <= metrics["raw_quality_score"] <= 1.0
    assert metrics["task_integrity"] >= 0.66
