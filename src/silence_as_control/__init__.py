"""Silence-as-Control SDK"""

# Core constants
SILENCE = None
COHERENCE_THRESHOLD = 0.7
DRIFT_THRESHOLD = 0.3
CONSENSUS_THRESHOLD = 0.5

# Core function
def should_silence(coherence: float, drift: float) -> bool:
    """Returns True if silence should be triggered."""
    return coherence < COHERENCE_THRESHOLD or drift > DRIFT_THRESHOLD


def silence_gate(coherence: float, drift: float) -> bool:
    """Alias for should_silence."""
    return should_silence(coherence, drift)


def consensus_gate(consensus: float, threshold: float = CONSENSUS_THRESHOLD) -> bool:
    """Returns True if silence due to low consensus."""
    return consensus < threshold


__version__ = "0.1.0"
__all__ = [
    "SILENCE",
    "COHERENCE_THRESHOLD",
    "DRIFT_THRESHOLD",
    "CONSENSUS_THRESHOLD",
    "should_silence",
    "silence_gate",
    "consensus_gate",
]
