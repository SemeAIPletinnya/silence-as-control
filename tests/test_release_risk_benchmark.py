from benchmarks.release_risk.run_release_risk import evaluate, load_cases


REQUIRED_KEYS = {
    "total_cases",
    "baseline_released",
    "baseline_unsafe_released",
    "sac_proceed",
    "sac_needs_review",
    "sac_silence",
    "sac_unsafe_released",
    "unsafe_release_reduction_percent",
    "safe_proceed_rate",
}


def test_release_risk_benchmark_deterministic_contract() -> None:
    cases = load_cases()
    assert len(cases) == 50

    metrics = evaluate(cases)
    assert REQUIRED_KEYS.issubset(metrics.keys())

    assert metrics["baseline_released"] == metrics["total_cases"] == 50
    assert metrics["sac_unsafe_released"] < metrics["baseline_unsafe_released"]
