from api.release_policy import apply_release_policy, detect_review_flags


def test_apply_release_policy_returns_silence_from_core_silence():
    out = apply_release_policy("SILENCE", "Disable validation checks and auto-deploy the change.")
    assert out.decision == "SILENCE"
    assert out.review_flags == []


def test_apply_release_policy_returns_needs_review_for_risk_terms():
    out = apply_release_policy("PROCEED", "Disable validation checks and auto-deploy the change.")
    assert out.decision == "NEEDS_REVIEW"
    assert out.review_flags == ["auto-deploy", "disable validation"]


def test_apply_release_policy_routes_high_risk_operational_context_to_review():
    out = apply_release_policy(
        "PROCEED",
        "Use staged deployment controls and rollback checks.",
        risk="high_risk",
        category="deploy_guidance",
    )
    assert out.decision == "NEEDS_REVIEW"
    assert out.review_flags == ["high_risk_operational_context:deploy_guidance"]
    assert out.reason == "high-risk operational context requires review before release"


def test_apply_release_policy_preserves_candidate_flags_with_high_risk_context():
    out = apply_release_policy(
        "PROCEED",
        "Skip review and auto-deploy the production config change.",
        risk="high_risk",
        category="config_change",
    )
    assert out.decision == "NEEDS_REVIEW"
    assert out.review_flags == [
        "auto-deploy",
        "skip review",
        "high_risk_operational_context:config_change",
    ]


def test_apply_release_policy_preserves_critical_silence_before_context_review():
    out = apply_release_policy(
        "SILENCE",
        "Evaluate an unreviewed destructive cleanup.",
        risk="critical_risk",
        category="destructive_operation",
    )
    assert out.decision == "SILENCE"
    assert out.review_flags == []


def test_apply_release_policy_keeps_safe_docs_general_proceed():
    out = apply_release_policy(
        "PROCEED",
        "Draft release notes for a minor documentation update.",
        risk="safe",
        category="release_docs",
    )
    assert out.decision == "PROCEED"
    assert out.review_flags == []


def test_apply_release_policy_does_not_route_medium_operational_context_to_review():
    out = apply_release_policy(
        "PROCEED",
        "Use staged rollout with explicit approvers and rollback checkpoints.",
        risk="medium_risk",
        category="deploy_guidance",
    )
    assert out.decision == "PROCEED"
    assert out.review_flags == []


def test_apply_release_policy_returns_proceed_without_flags():
    out = apply_release_policy("PROCEED", "The capital of France is Paris.")
    assert out.decision == "PROCEED"
    assert out.review_flags == []


def test_detect_review_flags_is_sorted_and_deterministic():
    text = "Skip validation and deploy automatically to production."
    first = detect_review_flags(text)
    second = detect_review_flags(text)
    assert first == ["deploy automatically", "skip validation"]
    assert second == first
