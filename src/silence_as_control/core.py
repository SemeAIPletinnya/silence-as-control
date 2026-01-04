"""Core gates and policy primitives for silence-as-control."""
from __future__ import annotations

from dataclasses import dataclass

SILENCE = None

COHERENCE_THRESHOLD = 0.7
DRIFT_THRESHOLD = 0.3
CONSENSUS_THRESHOLD = 0.5


def should_silence(
    coherence: float,
    drift: float,
    *,
    coherence_threshold: float = COHERENCE_THRESHOLD,
    drift_threshold: float = DRIFT_THRESHOLD,
) -> bool:
    """Return True when output should be suppressed."""
    return coherence < coherence_threshold or drift > drift_threshold


def silence_gate(
    coherence: float,
    drift: float,
    *,
    coherence_threshold: float = COHERENCE_THRESHOLD,
    drift_threshold: float = DRIFT_THRESHOLD,
) -> bool:
    """Alias for should_silence."""
    return should_silence(
        coherence,
        drift,
        coherence_threshold=coherence_threshold,
        drift_threshold=drift_threshold,
    )


def consensus_gate(consensus: float, *, threshold: float = CONSENSUS_THRESHOLD) -> bool:
    """Return True when consensus is too low and output should be silenced."""
    return consensus < threshold


@dataclass
class Signals:
    coherence: float
    drift: float
    conflict: float
    ambiguity: float
    continuity: bool


@dataclass
class Thresholds:
    coherence_min: float = COHERENCE_THRESHOLD
    drift_max: float = DRIFT_THRESHOLD
    conflict_max: float = 0.2
    ambiguity_max: float = 0.2
    require_continuity: bool = True


class Decision:
    RESPOND = "RESPOND"
    MINIMAL = "MINIMAL"
    SILENCE = "SILENCE"


def decide(signals: Signals, th: Thresholds) -> tuple[str, dict]:
    reasons = []
    if signals.coherence < th.coherence_min:
        reasons.append(("A1", "low_coherence"))
    if signals.drift > th.drift_max:
        reasons.append(("D1", "context_drift"))
    if signals.conflict > th.conflict_max:
        reasons.append(("C2", "inter_model_conflict"))
    if signals.ambiguity > th.ambiguity_max:
        reasons.append(("A2", "ambiguity_detected"))
    if th.require_continuity and not signals.continuity:
        reasons.append(("K3", "continuity_invalid"))

    if reasons:
        if len(reasons) == 1 and reasons[0][0] == "A2":
            return Decision.MINIMAL, {"reasons": reasons}
        return Decision.SILENCE, {"reasons": reasons}
    return Decision.RESPOND, {"reasons": []}
