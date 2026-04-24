"""Deterministic control-layer decision logic.

This module is the tested deterministic library contract.
It is intentionally separate from:
- evidence/eval script semantics (e.g., semantic_proxy_drift at 0.39), and
- runtime/API demo heuristics in api/main.py.
"""

from .abstention import control_abstention


CONTROL_MIN_COHERENCE = 0.7
CONTROL_MAX_DRIFT = 0.3


def por_control(
    output,
    coherence,
    drift,
    threshold=CONTROL_MIN_COHERENCE,
    tolerance=CONTROL_MAX_DRIFT,
):
    """Return output only when deterministic control bounds are satisfied.

    `CONTROL_MIN_COHERENCE` and `CONTROL_MAX_DRIFT` are simplified defaults
    intended for environments that do not run multi-sample drift estimation.
    """
    if drift > tolerance or coherence < threshold:
        return control_abstention()
    return {"status": "ok", "output": output}
