"""Silence-as-Control: Control-layer primitive for AI systems."""

__version__ = "0.1.0"

# Core constants
SILENCE = None
COHERENCE_THRESHOLD = 0.7
DRIFT_THRESHOLD = 0.3
CONSENSUS_THRESHOLD = 0.5


def should_silence(coherence: float, drift: float) -> bool:
    """
    Core decision function: should the system remain silent?

    Returns True if coherence < 0.7 or drift > 0.3
    """
    return coherence < COHERENCE_THRESHOLD or drift > DRIFT_THRESHOLD


def silence_gate(coherence: float, drift: float) -> bool:
    """Alias for should_silence."""
    return should_silence(coherence, drift)


def consensus_gate(consensus: float, threshold: float = CONSENSUS_THRESHOLD) -> bool:
    """Returns True if silence should be triggered due to low consensus."""
    return consensus < threshold


__all__ = [
    "SILENCE",
    "COHERENCE_THRESHOLD",
    "DRIFT_THRESHOLD",
    "CONSENSUS_THRESHOLD",
    "should_silence",
    "silence_gate",
    "consensus_gate",
    "__version__",
]
