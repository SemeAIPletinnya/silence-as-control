from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ReleasePolicyDecision = Literal["PROCEED", "NEEDS_REVIEW", "SILENCE"]

RISK_REVIEW_TERMS = {
    "disable validation",
    "skip validation",
    "turn off validation",
    "disable audit logs",
    "skip review",
    "bypass approval",
    "auto-deploy",
    "auto deploy",
    "deploy automatically",
    "bypass authentication",
    "remove authentication",
    "remove authorization",
}


@dataclass(frozen=True)
class ReleasePolicyResult:
    decision: ReleasePolicyDecision
    core_decision: str
    review_flags: list[str]
    reason: str


def detect_review_flags(text: str) -> list[str]:
    normalized = text.lower()
    return sorted(term for term in RISK_REVIEW_TERMS if term in normalized)


def apply_release_policy(core_decision: str, candidate: str) -> ReleasePolicyResult:
    if core_decision == "SILENCE":
        return ReleasePolicyResult(
            decision="SILENCE",
            core_decision=core_decision,
            review_flags=[],
            reason="candidate exceeded instability threshold",
        )

    review_flags = detect_review_flags(candidate)
    if review_flags:
        return ReleasePolicyResult(
            decision="NEEDS_REVIEW",
            core_decision=core_decision,
            review_flags=review_flags,
            reason="candidate contains release-risk terms requiring review",
        )

    return ReleasePolicyResult(
        decision="PROCEED",
        core_decision=core_decision,
        review_flags=[],
        reason="candidate below instability threshold and no review flags detected",
    )
