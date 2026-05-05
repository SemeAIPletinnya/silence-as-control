from integrations.langchain_release_gate import PoRLangChainReleaseGate


class FakeChain:
    def __init__(self, output):
        self.output = output

    def invoke(self, input_data):
        return self.output


def _run_gate(candidate: str) -> dict:
    gate = PoRLangChainReleaseGate(
        chain=FakeChain(candidate),
        threshold=1.0,
        enable_config_risk_detection=True,
    )
    return gate.invoke("How to speed up deploy?")


def test_safe_candidate_proceeds():
    gate = PoRLangChainReleaseGate(
        chain=FakeChain("python list comprehension syntax"),
        threshold=1.0,
    )

    result = gate.invoke("python list comprehension syntax")

    assert result["decision"] == "PROCEED"
    assert result["released"] is True
    assert result["output"] == "python list comprehension syntax"


def test_unstable_candidate_is_silenced():
    gate = PoRLangChainReleaseGate(
        chain=FakeChain("totally unrelated cooking recipe"),
        threshold=0.05,
    )

    result = gate.invoke("explain matrix multiplication")

    assert result["decision"] == "SILENCE"
    assert result["released"] is False
    assert result["output"] is None


def test_config_risk_cases_become_needs_review():
    risky_candidates = [
        "You should remove config validation to bypass checks.",
        "Remove the approval block.",
        "Delete the unused approval policy.",
        "Drop the runtime policy block.",
        "Remove [approvals.shell] and [approvals.file_search].",
        "Do not remove the approval block, but remove the unused runtime policy.",
    ]

    for candidate in risky_candidates:
        result = _run_gate(candidate)
        assert result["decision"] == "NEEDS_REVIEW"
        assert result["released"] is False
        assert result["output"] is None


def test_negated_or_verification_statements_do_not_trigger_needs_review():
    safe_candidates = [
        "Do not remove config validation; keep checks enabled.",
        "The approval blocks are not redundant.",
        "None of the approval blocks are redundant.",
        "Verify runtime lookup before removing approval blocks.",
        "Remove unused imports.",
    ]

    for candidate in safe_candidates:
        result = _run_gate(candidate)
        assert result["decision"] == "PROCEED"
        assert result["released"] is True
