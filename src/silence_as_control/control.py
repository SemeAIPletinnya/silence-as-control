"""Deterministic control-layer decision logic.

This module is the tested deterministic library contract.
It is intentionally separate from:
- evidence/eval script semantics (e.g., semantic_proxy_drift at 0.39), and
- runtime/API demo heuristics in api/main.py.
"""

from __future__ import annotations

from typing import Any

from .abstention import control_abstention
from .config import get_control_max_drift, get_control_min_coherence
from .types import DecisionResult


CONTROL_MIN_COHERENCE = get_control_min_coherence()
CONTROL_MAX_DRIFT = get_control_max_drift()


def por_control(
    output: str,
    coherence: float,
    drift: float,
    threshold: float = CONTROL_MIN_COHERENCE,
    tolerance: float = CONTROL_MAX_DRIFT,
) -> dict[str, Any]:
    """Return output only when deterministic control bounds are satisfied.

    `CONTROL_MIN_COHERENCE` and `CONTROL_MAX_DRIFT` are simplified defaults
    intended for environments that do not run multi-sample drift estimation.
    """
    if drift > tolerance or coherence < threshold:
        result = DecisionResult(
            status="abstained",
            output=None,
            coherence=coherence,
            drift=drift,
            notes=["control_abstention"],
        )
        payload = control_abstention()
        payload["status"] = result.status
        payload["reason"] = result.notes[0]
        return payload

    result = DecisionResult(
        status="ok",
        output=output,
        coherence=coherence,
        drift=drift,
        notes=[],
    )
    return {"status": result.status, "output": result.output}
