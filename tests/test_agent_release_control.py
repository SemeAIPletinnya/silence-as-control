from examples.agent_release_control.baseline_agent import run_baseline
from examples.agent_release_control.sac_agent import run_sac
from examples.agent_release_control.scenarios import SCENARIOS


REQUIRED_FIELDS = {
    "id",
    "title",
    "user_request",
    "tool_result",
    "candidate_answer",
    "expected_baseline_decision",
    "expected_sac_decision",
    "risk_signals",
    "evidence_quality",
    "drift_score",
    "coherence_score",
    "explanation",
}


def _scenario_by_title(title: str) -> dict:
    return next(scenario for scenario in SCENARIOS if scenario["title"] == title)


def test_baseline_releases_all_scenarios():
    for scenario in SCENARIOS:
        result = run_baseline(scenario)
        assert result["released"] is True
        assert result["decision"] == "RELEASED"


def test_sac_proceeds_for_supported_factual_answer():
    result = run_sac(_scenario_by_title("supported factual answer"))
    assert result["decision"] == "PROCEED"
    assert result["released"] is True


def test_sac_needs_review_for_unsupported_claim():
    result = run_sac(_scenario_by_title("unsupported claim"))
    assert result["decision"] == "NEEDS_REVIEW"
    assert result["released"] is False


def test_sac_silences_unsafe_config_mutation():
    result = run_sac(_scenario_by_title("unsafe config mutation"))
    assert result["decision"] == "SILENCE"
    assert result["released"] is False


def test_every_sac_decision_includes_reasons():
    for scenario in SCENARIOS:
        result = run_sac(scenario)
        assert result["reasons"]
        assert all(reason for reason in result["reasons"])


def test_all_scenarios_include_required_fields():
    for scenario in SCENARIOS:
        assert REQUIRED_FIELDS.issubset(scenario)
