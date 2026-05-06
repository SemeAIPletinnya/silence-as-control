"""Tests for shared runtime/demo signal utilities."""

from silence_as_control.signals import compute_signals


def test_compute_signals_returns_bounded_coherence_and_drift():
    coherence, drift = compute_signals(
        candidate="recursion is when a function calls itself",
        reference="explain recursion function calls itself",
    )

    assert 0.0 <= coherence <= 1.0
    assert 0.0 <= drift <= 1.0
    assert drift == 1.0 - coherence


def test_compute_signals_identical_text_has_high_coherence_low_drift():
    coherence, drift = compute_signals("alpha beta", "alpha beta")

    assert coherence > 0.95
    assert drift < 0.05


def test_compute_signals_empty_candidate_is_maximally_unstable():
    coherence, drift = compute_signals("   ", "alpha beta")

    assert coherence == 0.0
    assert drift == 1.0
