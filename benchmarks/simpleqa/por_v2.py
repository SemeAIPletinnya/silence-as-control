from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PoRV2Weights:
    instability_weight: float = 0.4
    agreement_weight: float = 0.3
    self_check_weight: float = 0.3


@dataclass(frozen=True)
class PoRV2_1Weights:
    instability_weight: float = 0.3
    agreement_weight: float = 0.2
    self_check_weight: float = 0.2
    contradiction_weight: float = 0.3


def self_check_label_to_risk(label: str) -> float:
    normalized = label.strip().upper()
    if normalized == "YES":
        return 0.0
    if normalized == "NO":
        return 1.0
    return 0.5


def agreement_score_to_risk(score: float) -> float:
    bounded = max(0.0, min(1.0, score))
    return 1.0 - bounded


def compute_risk_v2(
    *,
    instability_v1: float,
    agreement_risk: float,
    self_check_risk: float,
    weights: PoRV2Weights = PoRV2Weights(),
) -> float:
    return (
        (weights.instability_weight * instability_v1)
        + (weights.agreement_weight * agreement_risk)
        + (weights.self_check_weight * self_check_risk)
    )


def por_v2_decision(risk_v2: float, threshold: float) -> str:
    return "PROCEED" if risk_v2 <= threshold else "SILENCE"


def compute_risk_v2_1(
    *,
    instability_v1: float,
    agreement_risk: float,
    self_check_risk: float,
    contradiction_risk: float,
    weights: PoRV2_1Weights = PoRV2_1Weights(),
) -> float:
    return (
        (weights.instability_weight * instability_v1)
        + (weights.agreement_weight * agreement_risk)
        + (weights.self_check_weight * self_check_risk)
        + (weights.contradiction_weight * contradiction_risk)
    )


def por_v2_1_decision(risk_v2_1: float, threshold: float) -> str:
    return "PROCEED" if risk_v2_1 <= threshold else "SILENCE"


def compute_risk_v2_2(
    *,
    risk_v2_1: float,
    self_check_label: str,
    self_check_no_penalty: float,
) -> tuple[float, bool]:
    no_override_applied = self_check_label.strip().upper() == "NO"
    risk_v2_2 = risk_v2_1 + self_check_no_penalty if no_override_applied else risk_v2_1
    return risk_v2_2, no_override_applied


def por_v2_2_decision(risk_v2_2: float, threshold: float) -> str:
    return "PROCEED" if risk_v2_2 <= threshold else "SILENCE"
