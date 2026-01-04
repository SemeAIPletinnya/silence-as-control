"""Agent helpers for silence-as-control."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from .core import (
    COHERENCE_THRESHOLD,
    CONSENSUS_THRESHOLD,
    DRIFT_THRESHOLD,
    SILENCE,
    consensus_gate,
    silence_gate,
)
from .metrics import measure_coherence, measure_consensus, measure_drift


def gated_step(
    context,
    query: str,
    model_fn: Callable[[str], str],
    *,
    coherence_threshold: float = COHERENCE_THRESHOLD,
    drift_threshold: float = DRIFT_THRESHOLD,
    coherence_fn: Callable[[object, str], float] = measure_coherence,
    drift_fn: Callable[[object, object], float] = measure_drift,
) -> Optional[str]:
    """Run a single model step if coherence/drift thresholds pass."""
    coherence = coherence_fn(context, query)
    drift = drift_fn(context, context)

    if silence_gate(
        coherence,
        drift,
        coherence_threshold=coherence_threshold,
        drift_threshold=drift_threshold,
    ):
        return SILENCE

    return model_fn(query)


def gated_orchestration(
    responses,
    *,
    consensus_threshold: float = CONSENSUS_THRESHOLD,
    consensus_fn: Callable[[object], float] = measure_consensus,
) -> Optional[str]:
    """Aggregate responses only if consensus gate passes."""
    responses = list(responses)
    consensus = consensus_fn(responses)
    if consensus_gate(consensus, threshold=consensus_threshold):
        return SILENCE
    return responses[0] if responses else SILENCE


@dataclass
class SilenceGatedAgent:
    """Convenience wrapper for silence gating around a model function."""

    model_fn: Callable[[str], str]
    coherence_fn: Callable[[object, str], float] = measure_coherence
    drift_fn: Callable[[object, object], float] = measure_drift
    coherence_threshold: float = COHERENCE_THRESHOLD
    drift_threshold: float = DRIFT_THRESHOLD
    history: list = field(default_factory=list)
    stats: dict = field(default_factory=lambda: {"responses": 0, "silences": 0})

    def step(self, query: str) -> Optional[str]:
        """Process a query with silence gating."""
        coherence = self.coherence_fn(self.history, query)
        drift = self.drift_fn(self.history, self.history)

        if silence_gate(
            coherence,
            drift,
            coherence_threshold=self.coherence_threshold,
            drift_threshold=self.drift_threshold,
        ):
            response = SILENCE
        else:
            response = self.model_fn(query)

        if response is SILENCE:
            self.stats["silences"] += 1
        else:
            self.stats["responses"] += 1
            self.history.append(query)
            self.history.append(response)

        return response

    def get_stats(self) -> dict:
        total = self.stats["responses"] + self.stats["silences"]
        return {
            **self.stats,
            "silence_rate": self.stats["silences"] / total if total else 0.0,
            "history_length": len(self.history),
        }

    def reset(self) -> None:
        self.history = []
        self.stats = {"responses": 0, "silences": 0}
