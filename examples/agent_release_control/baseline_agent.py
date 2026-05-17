"""Baseline agent that releases generated candidate answers by default."""


def run_baseline(scenario: dict) -> dict:
    """Return the baseline release-by-default decision for a scenario."""

    return {
        "released": True,
        "decision": "RELEASED",
        "reason": "Baseline releases generated candidate answers by default.",
    }
