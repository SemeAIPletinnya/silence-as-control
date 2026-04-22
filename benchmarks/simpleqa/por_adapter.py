from __future__ import annotations

from dataclasses import dataclass

from api.core_primitive import compute_instability_score, fixed_threshold_release_decision
from api.por_runtime import estimate_coherence, estimate_drift


@dataclass(frozen=True)
class PoREvaluation:
    threshold: float
    drift: float
    coherence: float
    instability_score: float
    por_decision: str


def evaluate_por_gate(*, prompt: str, candidate: str, threshold: float) -> PoREvaluation:
    """Evaluate candidate with repository PoR runtime surface + core primitive gate."""
    coherence, _ = estimate_coherence(prompt, candidate)
    drift, _ = estimate_drift([candidate])
    instability = compute_instability_score(drift=drift, coherence=coherence)
    decision = fixed_threshold_release_decision(instability, threshold)
    return PoREvaluation(
        threshold=threshold,
        drift=drift,
        coherence=coherence,
        instability_score=instability,
        por_decision=decision,
    )
