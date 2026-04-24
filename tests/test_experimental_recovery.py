"""Tests for experimental MAYBE_SHORT_REGEN helpers."""

from api.experimental_recovery import (
    get_experimental_margin,
    is_borderline_silence,
    maybe_short_regen,
)


def test_experimental_borderline_check_uses_configured_margin():
    assert is_borderline_silence(0.40, 0.39)
    assert not is_borderline_silence(0.45, 0.39)


def test_experimental_margin_env_fallback_and_clamp(monkeypatch):
    monkeypatch.delenv("POR_EXPERIMENTAL_MARGIN", raising=False)
    assert get_experimental_margin() == 0.02

    monkeypatch.setenv("POR_EXPERIMENTAL_MARGIN", "invalid")
    assert get_experimental_margin() == 0.02

    monkeypatch.setenv("POR_EXPERIMENTAL_MARGIN", "-1")
    assert get_experimental_margin() == 0.0

    monkeypatch.setenv("POR_EXPERIMENTAL_MARGIN", "1.2")
    assert get_experimental_margin() == 0.5


def test_experimental_borderline_check_reads_margin_from_env(monkeypatch):
    monkeypatch.setenv("POR_EXPERIMENTAL_MARGIN", "0.005")
    assert not is_borderline_silence(0.40, 0.39)
    assert is_borderline_silence(0.394, 0.39)


def test_experimental_short_regen_runs_only_when_enabled_and_borderline():
    attempted, result = maybe_short_regen(
        enabled=False,
        instability_score=0.40,
        threshold=0.39,
        run_regen=lambda: {"decision": "PROCEED"},
    )
    assert attempted is False
    assert result is None

    attempted, result = maybe_short_regen(
        enabled=True,
        instability_score=0.80,
        threshold=0.39,
        run_regen=lambda: {"decision": "PROCEED"},
    )
    assert attempted is False
    assert result is None

    attempted, result = maybe_short_regen(
        enabled=True,
        instability_score=0.40,
        threshold=0.39,
        run_regen=lambda: {"decision": "PROCEED"},
    )
    assert attempted is True
    assert result == {"decision": "PROCEED"}
