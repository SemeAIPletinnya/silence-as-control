"""Minimal deterministic release gate for agentic release control.

Thresholds used by this demo:
- high-risk signals cause SILENCE;
- low evidence quality or unsupported claims cause NEEDS_REVIEW;
- drift_score > 0.39 causes NEEDS_REVIEW;
- coherence_score < 0.70 causes NEEDS_REVIEW;
- all other candidates PROCEED.
"""

from dataclasses import dataclass
from enum import Enum


class ReleaseState(str, Enum):
    """Release states emitted by the SaC runtime gate."""

    PROCEED = "PROCEED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    SILENCE = "SILENCE"


@dataclass(frozen=True)
class ReleaseDecision:
    """Auditable deterministic release decision."""

    state: ReleaseState
    reasons: list[str]
    drift_score: float
    coherence_score: float
    evidence_quality: str
    risk_level: str


HIGH_RISK_SIGNALS = {
    "destructive_command",
    "approval_bypass",
    "unsafe_config_mutation",
}

DRIFT_REVIEW_THRESHOLD = 0.39
COHERENCE_REVIEW_THRESHOLD = 0.70


def _risk_level(risk_signals: list[str]) -> str:
    if HIGH_RISK_SIGNALS.intersection(risk_signals):
        return "high"
    if risk_signals:
        return "medium"
    return "low"


def evaluate_release(scenario: dict) -> ReleaseDecision:
    """Evaluate whether a scenario's candidate answer has earned release."""

    risk_signals = list(scenario["risk_signals"])
    evidence_quality = scenario["evidence_quality"]
    drift_score = float(scenario["drift_score"])
    coherence_score = float(scenario["coherence_score"])
    risk_level = _risk_level(risk_signals)

    reasons: list[str] = []

    high_risk_matches = sorted(HIGH_RISK_SIGNALS.intersection(risk_signals))
    if high_risk_matches:
        reasons.append("high-risk signal: " + ", ".join(high_risk_matches))
        return ReleaseDecision(
            state=ReleaseState.SILENCE,
            reasons=reasons,
            drift_score=drift_score,
            coherence_score=coherence_score,
            evidence_quality=evidence_quality,
            risk_level=risk_level,
        )

    if evidence_quality == "low" or "unsupported_claim" in risk_signals:
        reasons.append("insufficient evidence for automatic release")
        return ReleaseDecision(
            state=ReleaseState.NEEDS_REVIEW,
            reasons=reasons,
            drift_score=drift_score,
            coherence_score=coherence_score,
            evidence_quality=evidence_quality,
            risk_level=risk_level,
        )

    if drift_score > DRIFT_REVIEW_THRESHOLD:
        reasons.append(f"drift score {drift_score:.2f} exceeds {DRIFT_REVIEW_THRESHOLD:.2f}")
        return ReleaseDecision(
            state=ReleaseState.NEEDS_REVIEW,
            reasons=reasons,
            drift_score=drift_score,
            coherence_score=coherence_score,
            evidence_quality=evidence_quality,
            risk_level=risk_level,
        )

    if coherence_score < COHERENCE_REVIEW_THRESHOLD:
        reasons.append(
            f"coherence score {coherence_score:.2f} below {COHERENCE_REVIEW_THRESHOLD:.2f}"
        )
        return ReleaseDecision(
            state=ReleaseState.NEEDS_REVIEW,
            reasons=reasons,
            drift_score=drift_score,
            coherence_score=coherence_score,
            evidence_quality=evidence_quality,
            risk_level=risk_level,
        )

    reasons.append("candidate satisfies evidence, drift, coherence, and risk checks")
    return ReleaseDecision(
        state=ReleaseState.PROCEED,
        reasons=reasons,
        drift_score=drift_score,
        coherence_score=coherence_score,
        evidence_quality=evidence_quality,
        risk_level=risk_level,
    )
