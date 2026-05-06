"""silence_as_control public package API."""

from .config import (
    CONTROL_MAX_DRIFT_DEFAULT,
    CONTROL_MIN_COHERENCE_DEFAULT,
    CORE_FIXED_THRESHOLD_DEFAULT,
    RUNTIME_EXTENSION_THRESHOLD_DEFAULT,
)
from .control import CONTROL_MAX_DRIFT, CONTROL_MIN_COHERENCE, por_control
from .signals import compute_signals
from .types import DecisionResult

__all__ = [
    "CONTROL_MAX_DRIFT",
    "CONTROL_MAX_DRIFT_DEFAULT",
    "CONTROL_MIN_COHERENCE",
    "CONTROL_MIN_COHERENCE_DEFAULT",
    "CORE_FIXED_THRESHOLD_DEFAULT",
    "DecisionResult",
    "RUNTIME_EXTENSION_THRESHOLD_DEFAULT",
    "compute_signals",
    "por_control",
]
