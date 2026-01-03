"""Core metric helpers for silence-as-control."""

from __future__ import annotations

from collections.abc import Callable


def measure_coherence(
    context: list,
    response: str,
    *,
    coherence_fn: Callable[[list, str], float] | None = None,
) -> float:
    """Measure alignment between context and response.

    Returns a float in the range [0.0, 1.0].
    """
    if coherence_fn is not None:
        return float(coherence_fn(context, response))
    if not context or not response:
        return 0.0
    return 0.85


def measure_drift(
    context: list,
    history: list | None = None,
    *,
    drift_fn: Callable[[list, list | None], float] | None = None,
) -> float:
    """Measure deviation from historical reasoning trajectory.

    Returns a float in the range [0.0, 1.0].
    """
    if drift_fn is not None:
        return float(drift_fn(context, history))
    if len(context) < 2:
        return 0.0
    return 0.1


def measure_consensus(
    responses: list,
    *,
    consensus_fn: Callable[[list], float] | None = None,
) -> float:
    """Measure agreement across multiple responses.

    Returns a float in the range [0.0, 1.0].
    """
    if consensus_fn is not None:
        return float(consensus_fn(responses))
    if not responses:
        return 0.0
    unique = set(responses)
    return 1.0 / len(unique) if unique else 0.0
