"""Core primitives for silence-as-control gating."""

from silence_as_control.core import (
    COHERENCE_THRESHOLD,
    CONSENSUS_THRESHOLD,
    DRIFT_THRESHOLD,
    SILENCE,
    consensus_gate,
    gate_output,
    should_silence,
    silence_gate,
)

__all__ = [
    "SILENCE",
    "COHERENCE_THRESHOLD",
    "DRIFT_THRESHOLD",
    "CONSENSUS_THRESHOLD",
    "should_silence",
    "silence_gate",
    "consensus_gate",
    "gate_output",
]
