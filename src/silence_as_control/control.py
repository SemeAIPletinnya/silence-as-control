"""Deterministic control-layer decision logic."""

from .abstention import control_abstention


def por_control(output, coherence, drift, threshold=0.7, tolerance=0.3):
    """Return output only when coherence and drift stay within limits."""
    if drift > tolerance or coherence < threshold:
        return control_abstention()
    return {"status": "ok", "output": output}
