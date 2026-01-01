"""
SemeAi Policy Layer
====================
Core rules that govern all agent behavior.
"""

# =============================================================================
# THRESHOLDS
# =============================================================================

COHERENCE_THRESHOLD = 0.7   # Below this → silence
DRIFT_THRESHOLD = 0.3       # Above this → silence
CONSENSUS_THRESHOLD = 0.5   # Below this → silence (multi-model)

# =============================================================================
# CORE RULES
# =============================================================================

RULES = {
    1: "Control ≠ response",
    2: "Silence is allowed and meaningful",
    3: "Drift is a signal, not an error",
    4: "Hallucination is a state, not a bug",
    5: "Decisions explained AFTER execution",
    6: "If coherence is low — do NOT respond",
    7: "Preserve longitudinal consistency",
}

# =============================================================================
# ROLE HIERARCHY
# =============================================================================

ROLES = {
    "Script-Bot-Creator": {"weight": 0.45, "function": "Primary Kernel"},
    "App-Creator": {"weight": 0.30, "function": "Context Signal Adapter"},
    "GPT-5.1": {"weight": 0.19, "function": "Executor"},
    "Grok-4": {"weight": 0.06, "function": "External Stress-Tester"},
}

# =============================================================================
# KEY PRINCIPLE
# =============================================================================

PRINCIPLE = "If continuity cannot be guaranteed, no output is preferable to a wrong one."


def validate_role(role: str) -> bool:
    """Check if role is authorized."""
    return role in ROLES


def get_role_weight(role: str) -> float:
    """Get decision weight for a role."""
    return ROLES.get(role, {}).get("weight", 0.0)
