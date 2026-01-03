"""Minimal gating helpers for silence-as-control."""

from __future__ import annotations

SILENCE = None

COHERENCE_THRESHOLD = 0.7
DRIFT_THRESHOLD = 0.3
CONSENSUS_THRESHOLD = 0.5


def should_silence(
    coherence: float,
    drift: float,
    *,
    coherence_threshold: float = COHERENCE_THRESHOLD,
    drift_threshold: float = DRIFT_THRESHOLD,
) -> bool:
    """Return True when output should be suppressed."""
    return coherence < coherence_threshold or drift > drift_threshold


def silence_gate(
    coherence: float,
    drift: float,
    *,
    coherence_threshold: float = COHERENCE_THRESHOLD,
    drift_threshold: float = DRIFT_THRESHOLD,
) -> bool:
    """Alias for should_silence."""
    return should_silence(
        coherence,
        drift,
        coherence_threshold=coherence_threshold,
        drift_threshold=drift_threshold,
    )


def consensus_gate(consensus: float, *, threshold: float = CONSENSUS_THRESHOLD) -> bool:
    """Return True when consensus is too low and output should be silenced."""
    return consensus < threshold


def gate_output(
    response: str,
    *,
    coherence: float,
    drift: float,
    coherence_threshold: float = COHERENCE_THRESHOLD,
    drift_threshold: float = DRIFT_THRESHOLD,
) -> str | None:
    """Return response if gate passes, otherwise SILENCE."""
    if should_silence(
        coherence,
        drift,
        coherence_threshold=coherence_threshold,
        drift_threshold=drift_threshold,
    ):
        return SILENCE
    return response
