"""Tests for experimental MAYBE_SHORT_REGEN helpers."""

from api.experimental_recovery import is_borderline_silence, maybe_short_regen


def test_experimental_borderline_check_uses_configured_margin():
    assert is_borderline_silence(0.40, 0.39)
    assert not is_borderline_silence(0.45, 0.39)


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
