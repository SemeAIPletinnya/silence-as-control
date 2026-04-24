"""Experimental post-silence recovery helpers (non-core).

This module isolates MAYBE_SHORT_REGEN so it cannot be confused with the
thesis-level deterministic primitive.
"""

from __future__ import annotations

import os
from typing import Callable

EXPERIMENTAL_BORDERLINE_MARGIN = 0.02
EXPERIMENTAL_MARGIN_ENV_VAR = "POR_EXPERIMENTAL_MARGIN"


def get_experimental_margin(default: float = EXPERIMENTAL_BORDERLINE_MARGIN) -> float:
    """[EXPERIMENTAL] Resolve borderline margin from env with safe fallback."""
    raw = os.getenv(EXPERIMENTAL_MARGIN_ENV_VAR)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return max(0.0, min(value, 0.5))


def is_borderline_silence(
    instability_score: float,
    threshold: float,
    margin: float | None = None,
) -> bool:
    """[EXPERIMENTAL] Return True for boundary-pocket silences."""
    if margin is None:
        margin = get_experimental_margin()
    return abs(instability_score - threshold) <= margin


def maybe_short_regen(
    *,
    enabled: bool,
    instability_score: float,
    threshold: float,
    run_regen: Callable[[], dict],
) -> tuple[bool, dict | None]:
    """[EXPERIMENTAL] Optionally run MAYBE_SHORT_REGEN.

    The regen callback runs only when:
    - experimental mode is enabled, and
    - instability lies in the boundary pocket.

    Returns `(attempted, regen_result)`.
    """
    if not enabled:
        return False, None

    if not is_borderline_silence(instability_score=instability_score, threshold=threshold):
        return False, None

    return True, run_regen()
