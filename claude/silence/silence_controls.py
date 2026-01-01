"""
Silence Controls
================
Core implementation of the silence-as-control primitive.
"""

from typing import Callable

# =============================================================================
# CONSTANTS
# =============================================================================

SILENCE = None
COHERENCE_THRESHOLD = 0.7
DRIFT_THRESHOLD = 0.3
CONSENSUS_THRESHOLD = 0.5

# =============================================================================
# GATE FUNCTIONS
# =============================================================================

def should_silence(coherence: float, drift: float) -> bool:
    """
    Core decision function: should the system remain silent?

    This is the primitive. Everything else builds on this.

    Args:
        coherence: Internal alignment score (0.0 to 1.0)
        drift: Trajectory deviation score (0.0 to 1.0)

    Returns:
        True if silence should be triggered
    """
    return coherence < COHERENCE_THRESHOLD or drift > DRIFT_THRESHOLD


def consensus_gate(consensus: float) -> bool:
    """
    Returns True if silence should be triggered due to model conflict.

    Args:
        consensus: Agreement score across multiple models (0.0 to 1.0)

    Returns:
        True if silence should be triggered
    """
    return consensus < CONSENSUS_THRESHOLD


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
    if not context or not response:
        return 0.0
    # Placeholder: implement actual measurement
    return 0.85


def measure_drift(context: list, history: list) -> float:
    """
    Measure deviation from historical reasoning trajectory.

    In practice, this could use:
    - Embedding distance from trajectory centroid
    - Topic shift detection
    - Semantic divergence metrics

    Returns: float between 0.0 and 1.0
    """
    if len(context) < 2:
        return 0.0
    # Placeholder: implement actual measurement
    return 0.1


def measure_consensus(responses: list) -> float:
    """
    Measure agreement across multiple model responses.

    Args:
        responses: List of response strings from different models

    Returns: float between 0.0 and 1.0
    """
    if not responses:
        return 0.0
    unique = set(responses)
    return 1.0 / len(unique) if unique else 0.0


# =============================================================================
# AGENT STEP WITH SILENCE GATE
# =============================================================================

def gated_step(
    context: list,
    query: str,
    model_fn: Callable[[list, str], str],
) -> str | None:
    """
    Execute one agent step with coherence gating.

    Args:
        context: Conversation history
        query: Current user query
        model_fn: Function that generates response (e.g., LLM call)

    Returns:
        Response string if coherence passes, SILENCE otherwise
    """
    # Generate candidate
    candidate = model_fn(context, query)

    # Measure state
    coherence = measure_coherence(context, candidate)
    drift = measure_drift(context, context)

    # Apply gate
    if should_silence(coherence, drift):
        return SILENCE

    return candidate


def gated_orchestration(responses: list) -> str | None:
    """
    Aggregate multi-model responses with consensus gating.

    Args:
        responses: List of responses from different models

    Returns:
        Aggregated response if consensus passes, SILENCE otherwise
    """
    consensus = measure_consensus(responses)

    if consensus_gate(consensus):
        return SILENCE

    return responses[0] if responses else SILENCE
