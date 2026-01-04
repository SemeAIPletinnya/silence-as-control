"""
Silence-as-Control: Core Test Suite

Three canonical tests:
1. Happy path — coherence OK → output permitted
2. Silence on ambiguity — coherence low → silence
3. Silence on conflict — multi-model disagreement → silence
"""

from silence_as_control import (
    SILENCE,
    gated_orchestration,
    gated_step,
)


def test_happy_path():
    """When coherence is above threshold, output is permitted."""
    state = {
        "coherence": 0.85,
        "drift": 0.1,
    }

    result = gated_step(state, "proceed", lambda query: f"executed:{query}")

    assert result is not SILENCE, "Expected output, got silence"
    assert result == "executed:proceed"


def test_silence_on_ambiguity():
    """When coherence is below threshold, silence is triggered."""
    state = {
        "coherence": 0.45,  # Below 0.7 threshold
        "drift": 0.1,
    }

    result = gated_step(state, "proceed", lambda query: f"executed:{query}")

    assert result is SILENCE, f"Expected silence, got {result}"


def test_silence_on_drift():
    """When drift exceeds threshold, silence is triggered."""
    state = {
        "coherence": 0.85,
        "drift": 0.5,  # Above 0.3 threshold
    }

    result = gated_step(state, "proceed", lambda query: f"executed:{query}")

    assert result is SILENCE, f"Expected silence, got {result}"


def test_silence_on_conflict():
    """When models disagree, silence is triggered."""
    responses = ["answer_A", "answer_B", "answer_C"]

    result = gated_orchestration(responses)

    assert result is SILENCE, f"Expected silence, got {result}"


def test_consensus_permits_output():
    """When models agree, output is permitted."""
    responses = ["answer_A", "answer_A", "answer_A"]

    result = gated_orchestration(responses)

    assert result is not SILENCE, "Expected output, got silence"
    assert result == "answer_A"
