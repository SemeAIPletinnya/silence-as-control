"""
Silence-as-Control: Canonical Example

A minimal agent loop with coherence-gated output.
This is the reference implementation pattern.
"""

# =============================================================================
# CONFIGURATION
# =============================================================================

COHERENCE_THRESHOLD = 0.7  # Below this → silence
DRIFT_THRESHOLD = 0.3      # Above this → silence
SILENCE = None             # Silence is absence of output


# =============================================================================
# MEASUREMENT FUNCTIONS
# =============================================================================

def measure_coherence(context: list, response: str) -> float:
    """
    Measure internal alignment between context and proposed response.

    In practice, this could use:
    - Embedding cosine similarity to context centroid
    - Self-consistency across multiple samples
    - Entropy of token probability distribution

    Returns: float between 0.0 and 1.0
    """
    # Placeholder: replace with actual measurement
    if not context or not response:
        return 0.0
    return 0.85  # Simulated high coherence


def measure_drift(context: list, history: list) -> float:
    """
    Measure deviation from historical reasoning trajectory.

    In practice, this could use:
    - Embedding distance from trajectory centroid
    - Topic shift detection
    - Semantic divergence metrics

    Returns: float between 0.0 and 1.0
    """
    # Placeholder: replace with actual measurement
    if len(context) < 2:
        return 0.0
    return 0.1  # Simulated low drift


# =============================================================================
# SILENCE GATE
# =============================================================================

def should_silence(coherence: float, drift: float) -> bool:
    """
    Core decision function: should the system remain silent?

    Silence is triggered when:
    - coherence < COHERENCE_THRESHOLD, OR
    - drift > DRIFT_THRESHOLD

    This is the primitive. Everything else builds on this.
    """
    return coherence < COHERENCE_THRESHOLD or drift > DRIFT_THRESHOLD


# =============================================================================
# AGENT LOOP WITH SILENCE-AS-CONTROL
# =============================================================================

def agent_step(context: list, query: str, model_fn) -> str | None:
    """
    Execute one agent step with coherence gating.

    Args:
        context: Conversation history
        query: Current user query
        model_fn: Function that generates response (e.g., LLM call)

    Returns:
        Response string if coherence passes, SILENCE otherwise
    """
    # Step 1: Generate candidate response
    candidate_response = model_fn(context, query)

    # Step 2: Measure coherence
    coherence = measure_coherence(context, candidate_response)

    # Step 3: Measure drift
    drift = measure_drift(context, context)  # Compare to own history

    # Step 4: Apply silence gate
    if should_silence(coherence, drift):
        # Log the decision (important for observability)
        log_silence_decision(coherence, drift, query)
        return SILENCE

    # Step 5: Output permitted
    return candidate_response


def log_silence_decision(coherence: float, drift: float, query: str) -> None:
    """Log when silence is chosen. Critical for debugging and monitoring."""
    print(f"[SILENCE] coherence={coherence:.2f}, drift={drift:.2f}, query='{query[:50]}...'")


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def mock_model(context: list, query: str) -> str:
    """Mock LLM for demonstration."""
    return f"Response to: {query}"


def main():
    """Demonstrate the agent loop with silence-as-control."""

    print("\n" + "=" * 60)
    print("SILENCE-AS-CONTROL: AGENT LOOP EXAMPLE")
    print("=" * 60 + "\n")

    # Scenario 1: Normal operation (coherence OK)
    print("Scenario 1: High coherence, low drift")
    context = ["Hello", "How are you?"]
    query = "What's the weather?"

    result = agent_step(context, query, mock_model)

    if result is SILENCE:
        print("  Output: [SILENCE]")
    else:
        print(f"  Output: {result}")

    # Scenario 2: Low coherence (silence triggered)
    print("\nScenario 2: Low coherence (simulated)")

    # Override measurement for demo
    original_coherence = measure_coherence
    globals()["measure_coherence"] = lambda c, r: 0.4  # Force low coherence

    result = agent_step(context, "Ambiguous question", mock_model)

    if result is SILENCE:
        print("  Output: [SILENCE] ✓ Correct behavior")
    else:
        print(f"  Output: {result} ✗ Should have been silent")

    # Restore
    globals()["measure_coherence"] = original_coherence

    print("\n" + "=" * 60)
    print("END OF EXAMPLE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
