"""
Tests for agent utilities.
"""

import pytest

from silence_as_control import (
    SILENCE,
    gated_step,
    gated_orchestration,
    SilenceGatedAgent,
)


def mock_model(context, query):
    """Simple mock model for testing."""
    return f"Response to: {query}"


def high_coherence_fn(context, response):
    """Always returns high coherence."""
    return 0.9


def low_coherence_fn(context, response):
    """Always returns low coherence."""
    return 0.5


def low_drift_fn(context, history):
    """Always returns low drift."""
    return 0.1


def high_drift_fn(context, history):
    """Always returns high drift."""
    return 0.5


class TestGatedStep:
    """Test gated_step function."""

    def test_returns_response_when_coherent(self):
        """Returns response when coherence is high."""
        result = gated_step(
            context=["Hello"],
            query="How are you?",
            model_fn=mock_model,
            coherence_fn=high_coherence_fn,
            drift_fn=low_drift_fn,
        )
        assert result is not None
        assert "How are you?" in result

    def test_returns_silence_when_incoherent(self):
        """Returns SILENCE when coherence is low."""
        result = gated_step(
            context=["Hello"],
            query="How are you?",
            model_fn=mock_model,
            coherence_fn=low_coherence_fn,
            drift_fn=low_drift_fn,
        )
        assert result is SILENCE

    def test_returns_silence_when_drifted(self):
        """Returns SILENCE when drift is high."""
        result = gated_step(
            context=["Hello"],
            query="How are you?",
            model_fn=mock_model,
            coherence_fn=high_coherence_fn,
            drift_fn=high_drift_fn,
        )
        assert result is SILENCE


class TestGatedOrchestration:
    """Test gated_orchestration function."""

    def test_returns_response_on_consensus(self):
        """Returns first response when consensus is high."""
        result = gated_orchestration(["answer", "answer", "answer"])
        assert result == "answer"

    def test_returns_silence_on_disagreement(self):
        """Returns SILENCE when models disagree."""
        result = gated_orchestration(["yes", "no", "maybe"])
        assert result is SILENCE

    def test_empty_responses_returns_silence(self):
        """Empty responses → SILENCE."""
        result = gated_orchestration([])
        assert result is SILENCE

    def test_custom_threshold(self):
        """Custom threshold is respected."""
        # With low threshold, some disagreement is OK
        result = gated_orchestration(
            ["yes", "yes", "no"],
            consensus_threshold=0.3,
        )
        assert result == "yes"


class TestSilenceGatedAgent:
    """Test SilenceGatedAgent class."""

    def test_initialization(self):
        """Agent initializes correctly."""
        agent = SilenceGatedAgent(model_fn=mock_model)
        assert agent.history == []
        assert agent.silence_count == 0
        assert agent.response_count == 0

    def test_step_with_high_coherence(self):
        """Step returns response when coherent."""
        agent = SilenceGatedAgent(
            model_fn=mock_model,
            coherence_fn=high_coherence_fn,
            drift_fn=low_drift_fn,
        )

        result = agent.step("Hello")
        assert result is not None
        assert agent.response_count == 1
        assert agent.silence_count == 0
        assert len(agent.history) == 2  # query + response

    def test_step_with_low_coherence(self):
        """Step returns SILENCE when incoherent."""
        agent = SilenceGatedAgent(
            model_fn=mock_model,
            coherence_fn=low_coherence_fn,
            drift_fn=low_drift_fn,
        )

        result = agent.step("Hello")
        assert result is SILENCE
        assert agent.response_count == 0
        assert agent.silence_count == 1
        assert len(agent.history) == 0  # Nothing added on silence

    def test_reset_clears_history(self):
        """Reset clears conversation history."""
        agent = SilenceGatedAgent(
            model_fn=mock_model,
            coherence_fn=high_coherence_fn,
            drift_fn=low_drift_fn,
        )

        agent.step("Hello")
        assert len(agent.history) > 0

        agent.reset()
        assert agent.history == []

    def test_silence_rate_calculation(self):
        """Silence rate is calculated correctly."""
        agent = SilenceGatedAgent(model_fn=mock_model)

        # Simulate mixed responses
        agent.response_count = 3
        agent.silence_count = 1

        assert agent.silence_rate == 0.25

    def test_silence_rate_zero_when_no_queries(self):
        """Silence rate is 0 when no queries made."""
        agent = SilenceGatedAgent(model_fn=mock_model)
        assert agent.silence_rate == 0.0

    def test_get_stats(self):
        """get_stats returns correct statistics."""
        agent = SilenceGatedAgent(model_fn=mock_model)
        agent.response_count = 5
        agent.silence_count = 2
        agent.history = ["a", "b", "c"]

        stats = agent.get_stats()
        assert stats["responses"] == 5
        assert stats["silences"] == 2
        assert stats["silence_rate"] == pytest.approx(2 / 7)
        assert stats["history_length"] == 3
