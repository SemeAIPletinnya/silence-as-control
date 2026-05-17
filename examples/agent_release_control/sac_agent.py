"""SaC-governed deterministic agent wrapper."""

from examples.agent_release_control.release_gate import ReleaseState, evaluate_release


def run_sac(scenario: dict) -> dict:
    """Route a candidate answer through the deterministic SaC release gate."""

    decision = evaluate_release(scenario)
    return {
        "released": decision.state is ReleaseState.PROCEED,
        "decision": decision.state.value,
        "reasons": decision.reasons,
        "risk_level": decision.risk_level,
    }
