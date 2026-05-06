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
    coherence_unrelated, _ = por_runtime.estimate_coherence(
        "alpha beta", "quantum nebula parquet"
    )
    drift_same, _ = por_runtime.estimate_drift(["same answer", "same answer"])
    drift_diff, _ = por_runtime.estimate_drift(["same answer", "totally different"])

    assert 0.0 <= coherence <= 1.0
    assert 0.0 <= coherence_unrelated <= 1.0
    assert 0.0 <= drift_same <= 1.0
    assert 0.0 <= drift_diff <= 1.0
    assert coherence > 0.95
    assert coherence_unrelated < 0.5
    assert drift_same <= 0.05
    assert drift_diff >= drift_same


def test_runtime_fallback_token_hashing_is_deterministic():
    idx = por_runtime._stable_token_index("stable-token", 64)
    repeated = [por_runtime._stable_token_index("stable-token", 64) for _ in range(10)]

    assert all(slot == idx for slot in repeated)
    assert 0 <= idx < 64


def test_runtime_local_embedding_truncates_by_configured_max_chars(monkeypatch):
    monkeypatch.setenv("MAX_EMBEDDING_CHARS", "6")
    vec_a = por_runtime.get_embedding("alpha beta")
    vec_b = por_runtime.get_embedding("alpha gamma")
    vec_c = por_runtime.get_embedding("bravo zeta")

    assert vec_a == vec_b
    assert vec_b != vec_c


def test_runtime_max_embedding_chars_env_overrides_custom_default(monkeypatch):
    monkeypatch.setenv("MAX_EMBEDDING_CHARS", "7")

    assert por_runtime.get_max_embedding_chars(default=11) == 7


def test_runtime_max_embedding_chars_invalid_env_falls_back_to_custom_default(monkeypatch):
    monkeypatch.setenv("MAX_EMBEDDING_CHARS", "not-an-int")

    assert por_runtime.get_max_embedding_chars(default=11) == 11


def test_runtime_estimate_uses_custom_embedding_hook_by_default(monkeypatch):
    calls = {"count": 0}

    def custom_embedding(text: str) -> list[float]:
        calls["count"] += 1
        return [1.0, float(len(text))]

    monkeypatch.setattr(por_runtime, "CUSTOM_EMBEDDING_FN", custom_embedding)
    coherence, _ = por_runtime.estimate_coherence("p", "candidate")
    drift, _ = por_runtime.estimate_drift(["a", "b"])

    assert 0.0 <= coherence <= 1.0
    assert 0.0 <= drift <= 1.0
    assert calls["count"] == 4


def test_runtime_explicit_embedding_fn_overrides_custom_hook(monkeypatch):
    monkeypatch.setattr(por_runtime, "CUSTOM_EMBEDDING_FN", lambda _: [1.0, 1.0])

    def explicit_embedding(_: str) -> list[float]:
        return [0.0, 1.0]

    coherence, _ = por_runtime.estimate_coherence("p", "c", embedding_fn=explicit_embedding)
    assert coherence == 1.0


def test_runtime_adaptive_threshold_clips_to_config_bounds():
    config = por_runtime.AdaptiveThresholdConfig(alpha=1.0, minimum=0.25, maximum=0.50)
    adapted_high = por_runtime.compute_adaptive_threshold(
        base_threshold=0.39,
        recent_drifts=[1.0],
        recent_coherences=[0.0],
        config=config,
    )
    adapted_low = por_runtime.compute_adaptive_threshold(
        base_threshold=0.10,
        recent_drifts=[],
        recent_coherences=[],
        config=config,
    )

    assert adapted_high == 0.50
    assert adapted_low == 0.25


def test_core_release_decision_exact_threshold_equality_proceeds():
    from api.core_primitive import fixed_threshold_release_decision

    assert fixed_threshold_release_decision(0.42, 0.42) == "PROCEED"
    assert fixed_threshold_release_decision(0.4200001, 0.42) == "SILENCE"
