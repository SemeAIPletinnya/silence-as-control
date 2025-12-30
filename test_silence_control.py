"""
Silence-as-Control: Core Test Suite

Three canonical tests:
1. Happy path — coherence OK → output permitted
2. Silence on ambiguity — coherence low → silence
3. Silence on conflict — multi-model disagreement → silence
"""

# Constants
COHERENCE_THRESHOLD = 0.7
DRIFT_THRESHOLD = 0.3
CONSENSUS_THRESHOLD = 0.5
SILENCE = None


def measure_coherence(state: dict) -> float:
    """Measure internal alignment across reasoning steps."""
    return state.get("coherence", 0.0)


def measure_drift(state: dict) -> float:
    """Measure deviation from context trajectory."""
    return state.get("drift", 0.0)


def measure_consensus(responses: list) -> float:
    """Measure agreement across multiple model responses."""
    if not responses:
        return 0.0
    # Simple: if all responses are equal, consensus = 1.0
    unique = set(responses)
    return 1.0 / len(unique) if unique else 0.0


def silence_gate(coherence: float, drift: float) -> bool:
    """Returns True if silence should be triggered."""
    return coherence < COHERENCE_THRESHOLD or drift > DRIFT_THRESHOLD


def consensus_gate(consensus: float) -> bool:
    """Returns True if silence should be triggered due to conflict."""
    return consensus < CONSENSUS_THRESHOLD


def agent_step(state: dict, action: str) -> str | None:
    """Execute action only if coherence gate passes."""
    coherence = measure_coherence(state)
    drift = measure_drift(state)

    if silence_gate(coherence, drift):
        return SILENCE

    return f"executed:{action}"


def orchestrate(responses: list) -> str | None:
    """Aggregate responses only if consensus gate passes."""
    consensus = measure_consensus(responses)

    if consensus_gate(consensus):
        return SILENCE

    return f"consensus:{responses[0]}"


# =============================================================================
# TEST 1: Happy Path — coherence OK → output permitted
# =============================================================================

def test_happy_path():
    """When coherence is above threshold, output is permitted."""
    state = {
        "coherence": 0.85,
        "drift": 0.1
    }

    result = agent_step(state, "proceed")

    assert result is not SILENCE, "Expected output, got silence"
    assert result == "executed:proceed"
    print("✓ TEST 1 PASSED: Happy path — output permitted")


# =============================================================================
# TEST 2: Silence on Ambiguity — coherence low → silence
# =============================================================================

def test_silence_on_ambiguity():
    """When coherence is below threshold, silence is triggered."""
    state = {
        "coherence": 0.45,  # Below 0.7 threshold
        "drift": 0.1
    }

    result = agent_step(state, "proceed")

    assert result is SILENCE, f"Expected silence, got {result}"
    print("✓ TEST 2 PASSED: Silence on ambiguity — low coherence")


def test_silence_on_drift():
    """When drift exceeds threshold, silence is triggered."""
    state = {
        "coherence": 0.85,
        "drift": 0.5  # Above 0.3 threshold
    }

    result = agent_step(state, "proceed")

    assert result is SILENCE, f"Expected silence, got {result}"
    print("✓ TEST 2b PASSED: Silence on drift — trajectory deviation")


# =============================================================================
# TEST 3: Silence on Conflict — multi-model disagreement → silence
# =============================================================================

def test_silence_on_conflict():
    """When models disagree, silence is triggered."""
    responses = ["answer_A", "answer_B", "answer_C"]

    result = orchestrate(responses)

    assert result is SILENCE, f"Expected silence, got {result}"
    print("✓ TEST 3 PASSED: Silence on conflict — no consensus")


def test_consensus_permits_output():
    """When models agree, output is permitted."""
    responses = ["answer_A", "answer_A", "answer_A"]

    result = orchestrate(responses)

    assert result is not SILENCE, "Expected output, got silence"
    assert result == "consensus:answer_A"
    print("✓ TEST 3b PASSED: Consensus reached — output permitted")


# =============================================================================
# RUN ALL TESTS
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SILENCE-AS-CONTROL: CORE TEST SUITE")
    print("=" * 60 + "\n")

    test_happy_path()
    test_silence_on_ambiguity()
    test_silence_on_drift()
    test_silence_on_conflict()
    test_consensus_permits_output()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60 + "\n")
