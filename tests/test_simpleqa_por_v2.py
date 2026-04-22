from benchmarks.simpleqa.por_v2 import (
    PoRV2Weights,
    compute_risk_v2,
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
