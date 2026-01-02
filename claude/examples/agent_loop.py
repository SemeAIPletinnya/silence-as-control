"""
Agent Loop Example
==================
Complete agent loop with silence gating.
"""

from typing import Callable

# =============================================================================
# CONSTANTS
# =============================================================================

SILENCE = None
COHERENCE_THRESHOLD = 0.7
DRIFT_THRESHOLD = 0.3

# =============================================================================
# CORE FUNCTIONS
# =============================================================================


def should_silence(coherence: float, drift: float) -> bool:
    return coherence < COHERENCE_THRESHOLD or drift > DRIFT_THRESHOLD


def measure_coherence(context: list, response: str) -> float:
    """Placeholder: implement actual coherence measurement."""
    if not response:
        return 0.0
    return 0.85


def measure_drift(history: list) -> float:
    """Placeholder: implement actual drift measurement."""
    if len(history) < 2:
        return 0.0
    return 0.1


# =============================================================================
# AGENT LOOP
# =============================================================================


def agent_step(
    context: list,
    query: str,
    model_fn: Callable[[list, str], str],
) -> str | None:
    """
    Execute one agent step with silence gate.

    Returns response or SILENCE.
    """
    # Generate candidate
    candidate = model_fn(context, query)

    # Measure state
    coherence = measure_coherence(context, candidate)
    drift = measure_drift(context)

    # Gate decision
    if should_silence(coherence, drift):
        return SILENCE

    return candidate


def run_agent_loop(queries: list, model_fn: Callable) -> None:
    """Run agent over multiple queries."""
    context = []

    for query in queries:
        print(f"\nQuery: {query}")

        response = agent_step(context, query, model_fn)

        if response is SILENCE:
            print("Response: [SILENCE]")
        else:
            print(f"Response: {response}")
            context.append({"query": query, "response": response})


# =============================================================================
# EXAMPLE
# =============================================================================


def mock_model(context: list, query: str) -> str:
    """Mock model for demonstration."""
    return f"Answer to: {query}"


if __name__ == "__main__":
    queries = [
        "What is 2+2?",
        "Explain quantum computing",
        "Write a poem about silence",
    ]

    run_agent_loop(queries, mock_model)
