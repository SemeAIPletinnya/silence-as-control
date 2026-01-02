"""
Multi-Model Orchestration Example
=================================
Consensus gating across multiple models.
"""

# =============================================================================
# CONSTANTS
# =============================================================================

SILENCE = None
CONSENSUS_THRESHOLD = 0.5

# =============================================================================
# CONSENSUS GATE
# =============================================================================

def measure_consensus(responses: list) -> float:
    """Measure agreement across responses."""
    if not responses:
        return 0.0
    unique = set(responses)
    return 1.0 / len(unique)


def consensus_gate(consensus: float) -> bool:
    """Returns True if silence should trigger."""
    return consensus < CONSENSUS_THRESHOLD


# =============================================================================
# ORCHESTRATOR
# =============================================================================

def orchestrate(models: list, query: str) -> str | None:
    """
    Get responses from multiple models.
    Apply consensus gate.
    Return SILENCE if models disagree.
    """
    responses = [model(query) for model in models]

    print(f"Responses: {responses}")

    consensus = measure_consensus(responses)
    print(f"Consensus: {consensus:.2f}")

    if consensus_gate(consensus):
        return SILENCE

    # Return first response if consensus passes
    return responses[0]


# =============================================================================
# EXAMPLE
# =============================================================================

def model_a(query: str) -> str:
    return "42"


def model_b(query: str) -> str:
    return "42"


def model_c(query: str) -> str:
    return "43"  # Disagrees


if __name__ == "__main__":
    # Scenario 1: All agree
    print("\n=== Scenario 1: Agreement ===")
    result = orchestrate([model_a, model_b], "What is the answer?")
    if result is SILENCE:
        print("Result: [SILENCE]")
    else:
        print(f"Result: {result}")

    # Scenario 2: Disagreement
    print("\n=== Scenario 2: Disagreement ===")
    result = orchestrate([model_a, model_c], "What is the answer?")
    if result is SILENCE:
        print("Result: [SILENCE]")
    else:
        print(f"Result: {result}")
