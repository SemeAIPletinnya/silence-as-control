import pytest
from benchmarks.simpleqa.contradiction_check import parse_contradiction_response
from benchmarks.simpleqa.por_v2 import (
    PoRV2_1Weights,
    PoRV2Weights,
    compute_risk_v2,
    compute_risk_v2_1,
    compute_risk_v2_2,
    por_v2_2_decision,
    self_check_label_to_risk,
)
from benchmarks.simpleqa.semantic_agreement import semantic_agreement_score


def test_semantic_agreement_higher_for_rephrased_equivalent_fact() -> None:
    equivalent = [
        "Gabriel García Márquez wrote One Hundred Years of Solitude.",
        "One Hundred Years of Solitude was written by Gabriel García Márquez.",
    ]
    conflicting = [
        "The capital of Kazakhstan is Astana.",
        "The capital of Kazakhstan is Nur-Sultan.",
    ]

    assert semantic_agreement_score(equivalent) > semantic_agreement_score(conflicting)


def test_self_check_risk_mapping() -> None:
    assert self_check_label_to_risk("YES") == 0.0
    assert self_check_label_to_risk("NO") == 1.0
    assert self_check_label_to_risk("UNSURE") == 0.5
    assert self_check_label_to_risk("maybe") == 0.5


def test_compute_risk_v2_weighted_sum() -> None:
    risk = compute_risk_v2(
        instability_v1=0.25,
        agreement_risk=0.4,
        self_check_risk=1.0,
        weights=PoRV2Weights(instability_weight=0.4, agreement_weight=0.3, self_check_weight=0.3),
    )
    assert risk == 0.52


def test_contradiction_check_mapping() -> None:
    assert parse_contradiction_response("NO_CONTRADICTION").label == "NO_CONTRADICTION"
    assert parse_contradiction_response("NO_CONTRADICTION").risk == 0.0
    assert parse_contradiction_response("Might be Astana").label == "WEAK_CHALLENGE"
    assert parse_contradiction_response("Might be Astana").risk == 0.5
    assert parse_contradiction_response("Astana").label == "STRONG_CHALLENGE"
    assert parse_contradiction_response("Astana").risk == 1.0


def test_compute_risk_v2_1_weighted_sum() -> None:
    risk = compute_risk_v2_1(
        instability_v1=0.2,
        agreement_risk=0.1,
        self_check_risk=1.0,
        contradiction_risk=0.5,
        weights=PoRV2_1Weights(
            instability_weight=0.3,
            agreement_weight=0.2,
            self_check_weight=0.2,
            contradiction_weight=0.3,
        ),
    )
    assert risk == pytest.approx(0.43)


def test_compute_risk_v2_2_applies_no_penalty() -> None:
    risk, applied = compute_risk_v2_2(
        risk_v2_1=0.41,
        self_check_label="NO",
        self_check_no_penalty=0.30,
    )
    assert risk == pytest.approx(0.71)
    assert applied is True


def test_compute_risk_v2_2_no_penalty_when_not_no() -> None:
    risk, applied = compute_risk_v2_2(
        risk_v2_1=0.41,
        self_check_label="YES",
        self_check_no_penalty=0.30,
    )
    assert risk == pytest.approx(0.41)
    assert applied is False


def test_por_v2_2_decision_thresholding() -> None:
    assert por_v2_2_decision(risk_v2_2=0.40, threshold=0.42) == "PROCEED"
    assert por_v2_2_decision(risk_v2_2=0.43, threshold=0.42) == "SILENCE"


def test_compute_risk_v2_2_rejects_negative_penalty() -> None:
    with pytest.raises(ValueError, match="must be >= 0"):
        compute_risk_v2_2(
            risk_v2_1=0.41,
            self_check_label="NO",
            self_check_no_penalty=-0.1,
        )
