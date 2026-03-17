"""Tests for silence-as-control core functionality."""

import pytest
from silence_as_control import (
    SILENCE,
    COHERENCE_THRESHOLD,
    DRIFT_THRESHOLD,
    CONSENSUS_THRESHOLD,
    should_silence,
    silence_gate,
    consensus_gate,
)


class TestConstants:
    def test_silence_is_none(self):
        assert SILENCE is None

    def test_thresholds(self):
        assert COHERENCE_THRESHOLD == 0.7
        assert DRIFT_THRESHOLD == 0.3
        assert CONSENSUS_THRESHOLD == 0.5


class TestShouldSilence:
    def test_high_coherence_low_drift_allows_output(self):
        # Good state -> no silence
        assert should_silence(0.9, 0.1) is False

    def test_low_coherence_triggers_silence(self):
        # Low coherence -> silence
        assert should_silence(0.5, 0.1) is True

    def test_high_drift_triggers_silence(self):
        # High drift -> silence
        assert should_silence(0.9, 0.5) is True

    def test_boundary_coherence(self):
        assert should_silence(0.7, 0.1) is False  # At threshold
        assert should_silence(0.69, 0.1) is True  # Below threshold

    def test_boundary_drift(self):
        assert should_silence(0.9, 0.3) is False  # At threshold
        assert should_silence(0.9, 0.31) is True  # Above threshold


class TestSilenceGate:
    def test_is_alias(self):
        assert silence_gate(0.9, 0.1) == should_silence(0.9, 0.1)
        assert silence_gate(0.5, 0.5) == should_silence(0.5, 0.5)


class TestConsensusGate:
    def test_high_consensus_allows_output(self):
        assert consensus_gate(0.8) is False

    def test_low_consensus_triggers_silence(self):
        assert consensus_gate(0.3) is True

    def test_boundary(self):
        assert consensus_gate(0.5) is False
        assert consensus_gate(0.49) is True
