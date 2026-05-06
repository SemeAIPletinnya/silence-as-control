"""Shared public result types for Silence-as-Control."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DecisionResult:
    """Normalized release-control decision result.

    This type is additive: existing dict/Pydantic response shapes remain stable
    for backward compatibility.
    """

    status: str
    output: str | None
    coherence: float
    drift: float
    notes: list[str]
