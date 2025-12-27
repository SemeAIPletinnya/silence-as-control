from dataclasses import dataclass

@dataclass
class Signals:
    coherence: float
    drift: float
    conflict: float
    ambiguity: float
    continuity: bool

@dataclass
class Thresholds:
    coherence_min: float = 0.7
    drift_max: float = 0.3
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
