"""Centralized configuration defaults for Silence-as-Control.

The values here preserve the repository's existing defaults while making the
runtime knobs easier to audit. Environment variables are optional overrides;
invalid values fall back to the same sensible defaults instead of changing gate
semantics implicitly.
"""

from __future__ import annotations

import os

CORE_FIXED_THRESHOLD_DEFAULT = 0.39
CONTROL_MIN_COHERENCE_DEFAULT = 0.7
CONTROL_MAX_DRIFT_DEFAULT = 0.3
RUNTIME_EXTENSION_THRESHOLD_DEFAULT = CORE_FIXED_THRESHOLD_DEFAULT
ADAPTIVE_THRESHOLD_ALPHA_DEFAULT = 0.4
ADAPTIVE_THRESHOLD_MINIMUM_DEFAULT = 0.20
ADAPTIVE_THRESHOLD_MAXIMUM_DEFAULT = 0.80
MAX_EMBEDDING_CHARS_DEFAULT = 4000
LEGACY_GENERATE_COHERENCE_DEFAULT = 0.8

CORE_FIXED_THRESHOLD_ENV_VAR = "POR_CORE_FIXED_THRESHOLD"
CONTROL_MIN_COHERENCE_ENV_VAR = "POR_CONTROL_MIN_COHERENCE"
CONTROL_MAX_DRIFT_ENV_VAR = "POR_CONTROL_MAX_DRIFT"
RUNTIME_GATE_THRESHOLD_ENV_VAR = "POR_RUNTIME_GATE_THRESHOLD"
ADAPTIVE_THRESHOLD_ALPHA_ENV_VAR = "POR_ADAPTIVE_THRESHOLD_ALPHA"
ADAPTIVE_THRESHOLD_MINIMUM_ENV_VAR = "POR_ADAPTIVE_THRESHOLD_MINIMUM"
ADAPTIVE_THRESHOLD_MAXIMUM_ENV_VAR = "POR_ADAPTIVE_THRESHOLD_MAXIMUM"
MAX_EMBEDDING_CHARS_ENV_VAR = "MAX_EMBEDDING_CHARS"
LEGACY_GENERATE_COHERENCE_ENV_VAR = "POR_LEGACY_GENERATE_COHERENCE"


def _get_float(name: str, default: float) -> float:
    """Read a float environment override with default-preserving fallback."""
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _get_int(name: str, default: int) -> int:
    """Read an integer environment override with default-preserving fallback."""
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def clip_unit_interval(value: float) -> float:
    """Clamp a numeric threshold/signal value to the [0, 1] interval."""
    return max(0.0, min(value, 1.0))


def get_core_fixed_threshold() -> float:
    """Resolve the core fixed threshold default without changing its meaning."""
    return clip_unit_interval(
        _get_float(CORE_FIXED_THRESHOLD_ENV_VAR, CORE_FIXED_THRESHOLD_DEFAULT)
    )


def get_control_min_coherence() -> float:
    """Resolve the deterministic control-layer coherence bound."""
    return clip_unit_interval(
        _get_float(CONTROL_MIN_COHERENCE_ENV_VAR, CONTROL_MIN_COHERENCE_DEFAULT)
    )


def get_control_max_drift() -> float:
    """Resolve the deterministic control-layer drift tolerance."""
    return clip_unit_interval(
        _get_float(CONTROL_MAX_DRIFT_ENV_VAR, CONTROL_MAX_DRIFT_DEFAULT)
    )


def get_runtime_gate_threshold(default: float = RUNTIME_EXTENSION_THRESHOLD_DEFAULT) -> float:
    """Resolve the runtime gate threshold override, preserving fixed-threshold semantics."""
    return clip_unit_interval(_get_float(RUNTIME_GATE_THRESHOLD_ENV_VAR, default))


def get_adaptive_threshold_alpha() -> float:
    """Resolve the runtime adaptive-threshold smoothing factor."""
    return clip_unit_interval(
        _get_float(ADAPTIVE_THRESHOLD_ALPHA_ENV_VAR, ADAPTIVE_THRESHOLD_ALPHA_DEFAULT)
    )


def get_adaptive_threshold_minimum() -> float:
    """Resolve the runtime adaptive-threshold lower bound."""
    return clip_unit_interval(
        _get_float(ADAPTIVE_THRESHOLD_MINIMUM_ENV_VAR, ADAPTIVE_THRESHOLD_MINIMUM_DEFAULT)
    )


def get_adaptive_threshold_maximum() -> float:
    """Resolve the runtime adaptive-threshold upper bound."""
    return clip_unit_interval(
        _get_float(ADAPTIVE_THRESHOLD_MAXIMUM_ENV_VAR, ADAPTIVE_THRESHOLD_MAXIMUM_DEFAULT)
    )


def get_max_embedding_chars(default: int = MAX_EMBEDDING_CHARS_DEFAULT) -> int:
    """Resolve local embedding truncation length for runtime/demo estimators."""
    return max(1, _get_int(MAX_EMBEDDING_CHARS_ENV_VAR, default))


def get_legacy_generate_coherence() -> float:
    """Resolve the backward-compatible legacy `/generate` coherence cutoff."""
    return clip_unit_interval(
        _get_float(
            LEGACY_GENERATE_COHERENCE_ENV_VAR,
            LEGACY_GENERATE_COHERENCE_DEFAULT,
        )
    )
