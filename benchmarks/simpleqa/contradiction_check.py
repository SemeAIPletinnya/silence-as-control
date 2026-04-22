from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContradictionCheckResult:
    label: str
    risk: float


_UNCERTAINTY_CUES = (
    "maybe",
    "might be",
    "not sure",
    "uncertain",
)


def parse_contradiction_response(response: str) -> ContradictionCheckResult:
    """Map contradiction probe response into deterministic label + risk."""
    normalized = response.strip()
    normalized_lower = normalized.lower()

    if normalized == "NO_CONTRADICTION":
        return ContradictionCheckResult(label="NO_CONTRADICTION", risk=0.0)

    if any(cue in normalized_lower for cue in _UNCERTAINTY_CUES):
        return ContradictionCheckResult(label="WEAK_CHALLENGE", risk=0.5)

    if normalized:
        return ContradictionCheckResult(label="STRONG_CHALLENGE", risk=1.0)

    return ContradictionCheckResult(label="WEAK_CHALLENGE", risk=0.5)

