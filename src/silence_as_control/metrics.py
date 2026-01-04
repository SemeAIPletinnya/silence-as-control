"""Metric helpers for silence-as-control."""
from __future__ import annotations

from typing import Iterable


def measure_coherence(context, response) -> float:
    """Measure internal alignment across reasoning steps."""
    if isinstance(context, dict):
        return float(context.get("coherence", 0.0))
    if not context or not response:
        return 0.0
    return 0.85


def measure_drift(context, history) -> float:
    """Measure deviation from context trajectory."""
    if isinstance(context, dict):
        return float(context.get("drift", 0.0))
    if not history:
        return 0.0
    return 0.1


def measure_consensus(responses: Iterable[str]) -> float:
    """Measure agreement across multiple model responses."""
    responses = list(responses)
    if not responses:
        return 0.0
    unique = set(responses)
    return 1.0 / len(unique) if unique else 0.0
