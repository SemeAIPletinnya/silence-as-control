from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PoRV2Weights:
    instability_weight: float = 0.4
    agreement_weight: float = 0.3
    self_check_weight: float = 0.3


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
