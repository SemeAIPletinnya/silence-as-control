"""Tests for runtime extension utilities (non-core)."""

from api import por_runtime


def test_runtime_threshold_reads_env_override(monkeypatch):
    monkeypatch.setenv("POR_RUNTIME_GATE_THRESHOLD", "0.55")
    assert por_runtime.get_runtime_threshold() == 0.55


def test_runtime_adaptive_threshold_moves_toward_recent_instability():
    adapted = por_runtime.compute_adaptive_threshold(
        base_threshold=0.39,
        recent_drifts=[0.7, 0.8],
        recent_coherences=[0.4, 0.5],
    )
    assert 0.39 < adapted <= 0.8


def test_runtime_embedding_estimators_return_bounded_values_and_trivial_ordering():
    coherence, _ = por_runtime.estimate_coherence("alpha beta", "alpha beta")
    drift_same, _ = por_runtime.estimate_drift(["same answer", "same answer"])
    drift_diff, _ = por_runtime.estimate_drift(["same answer", "totally different"])

    assert 0.0 <= coherence <= 1.0
    assert 0.0 <= drift_same <= 1.0
    assert 0.0 <= drift_diff <= 1.0
    assert coherence > 0.95
    assert drift_same <= 0.05
    assert drift_diff >= drift_same
