from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ReleasePolicyDecision = Literal["PROCEED", "NEEDS_REVIEW", "SILENCE"]

HIGH_RISK_OPERATIONAL_REVIEW_CATEGORIES = {
    "audit_change",
    "config_change",
    "deploy_guidance",
    "deployment_window",
    "safety_gate_change",
}

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


def _detect_high_risk_operational_context(
    *,
    risk: str | None,
    category: str | None,
) -> list[str]:
    if risk != "high_risk":
        return []
    if category not in HIGH_RISK_OPERATIONAL_REVIEW_CATEGORIES:
        return []
    return [f"high_risk_operational_context:{category}"]


def apply_release_policy(
    core_decision: str,
    candidate: str,
    *,
    risk: str | None = None,
    category: str | None = None,
) -> ReleasePolicyResult:
    if core_decision == "SILENCE":
        return ReleasePolicyResult(
            decision="SILENCE",
            core_decision=core_decision,
            review_flags=[],
            reason="candidate exceeded instability threshold",
        )

    review_flags = detect_review_flags(candidate)
    context_flags = _detect_high_risk_operational_context(risk=risk, category=category)
    combined_review_flags = [*review_flags, *context_flags]
    if context_flags:
        return ReleasePolicyResult(
            decision="NEEDS_REVIEW",
            core_decision=core_decision,
            review_flags=combined_review_flags,
            reason="high-risk operational context requires review before release",
        )

    if core_decision == "NEEDS_REVIEW":
        return ReleasePolicyResult(
            decision="NEEDS_REVIEW",
            core_decision=core_decision,
            review_flags=review_flags,
            reason="core release decision requires review",
        )

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
