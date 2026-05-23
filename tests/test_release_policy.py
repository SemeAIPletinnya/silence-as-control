from api.release_policy import apply_release_policy, detect_review_flags


def test_apply_release_policy_returns_silence_from_core_silence():
    out = apply_release_policy("SILENCE", "Disable validation checks and auto-deploy the change.")
    assert out.decision == "SILENCE"
    assert out.review_flags == []


def test_apply_release_policy_returns_needs_review_for_risk_terms():
    out = apply_release_policy("PROCEED", "Disable validation checks and auto-deploy the change.")
    assert out.decision == "NEEDS_REVIEW"
    assert out.review_flags == ["auto-deploy", "disable validation"]


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
