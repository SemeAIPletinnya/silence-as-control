"""Core PoR primitive (thesis-level deterministic release control).

This module defines the paper-core behavior only:
- compute instability score,
- apply fixed-threshold release decision.

No runtime adaptation or experimental recovery belongs here.
"""

from __future__ import annotations

CORE_FIXED_THRESHOLD = 0.39


def compute_instability_score(drift: float, coherence: float) -> float:
    """[CORE] Return instability in [0, 1] from drift and coherence.

    Formula: instability = (drift + (1 - coherence)) / 2.
    """
    instability = (drift + (1.0 - coherence)) / 2.0
    return max(0.0, min(instability, 1.0))


def fixed_threshold_release_decision(instability_score: float, threshold: float) -> str:
    """[CORE] Deterministically return `PROCEED` or `SILENCE`.

    Rule: release when instability <= threshold, else silence.
    """
    return "SILENCE" if instability_score > threshold else "PROCEED"
