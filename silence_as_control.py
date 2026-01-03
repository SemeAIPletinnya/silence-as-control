"""Core helpers for Silence-as-Control examples."""
from __future__ import annotations

from typing import List, Optional

SILENCE: Optional[str] = None
CONSENSUS_THRESHOLD = 0.5


def measure_consensus(responses: List[str]) -> float:
    """Measure agreement across multiple model responses."""
    if not responses:
        return 0.0
    unique = set(responses)
    return 1.0 / len(unique) if unique else 0.0


def consensus_gate(consensus: float, consensus_threshold: float = CONSENSUS_THRESHOLD) -> bool:
    """Return True when silence should be triggered due to conflict."""
    return consensus < consensus_threshold


def gated_orchestration(
    responses: List[str],
    consensus_threshold: float = CONSENSUS_THRESHOLD,
) -> Optional[str]:
    """Aggregate responses only if consensus gate passes."""
    consensus = measure_consensus(responses)
    if consensus_gate(consensus, consensus_threshold):
        return SILENCE
    return responses[0] if responses else SILENCE
