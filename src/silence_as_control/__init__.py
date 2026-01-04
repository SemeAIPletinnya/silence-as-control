"""
Silence-as-Control
==================
Control-layer primitive for AI systems: when coherence cannot be guaranteed,
intentional silence is preferred over misleading output.

Usage:
    from silence_as_control import should_silence, SILENCE

    if should_silence(coherence=0.65, drift=0.2):
        response = SILENCE
"""

from .core import (
    SILENCE,
    COHERENCE_THRESHOLD,
    DRIFT_THRESHOLD,
    CONSENSUS_THRESHOLD,
    should_silence,
    silence_gate,
    consensus_gate,
)

from .metrics import (
    measure_coherence,
    measure_drift,
    measure_consensus,
)

from .agent import (
    gated_step,
    gated_orchestration,
    SilenceGatedAgent,
)

__version__ = "0.1.0"
__all__ = [
    "SILENCE",
    "COHERENCE_THRESHOLD",
    "DRIFT_THRESHOLD",
    "CONSENSUS_THRESHOLD",
    "should_silence",
    "silence_gate",
    "consensus_gate",
    "measure_coherence",
    "measure_drift",
    "measure_consensus",
    "gated_step",
    "gated_orchestration",
    "SilenceGatedAgent",
]
