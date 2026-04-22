"""Tests for thesis-level core primitive behavior."""

from api.core_primitive import compute_instability_score, fixed_threshold_release_decision


def test_core_instability_score_formula_midpoint_case():
    score = compute_instability_score(drift=0.4, coherence=0.8)
    assert score == 0.3
    assert 0.0 <= score <= 1.0


def test_core_fixed_threshold_decision_is_deterministic_at_boundary():
    assert fixed_threshold_release_decision(instability_score=0.39, threshold=0.39) == "PROCEED"
    assert fixed_threshold_release_decision(instability_score=0.3901, threshold=0.39) == "SILENCE"
