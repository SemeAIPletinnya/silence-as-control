from demo.baseline_vs_por import (
    classify_baseline_outcome,
    interpret_negative_control,
    strip_ansi_control_codes,
)


def test_strip_ansi_control_codes_removes_csi_sequences():
    text = "Hello\x1b[13D\x1b[K world\nNext"
    cleaned = strip_ansi_control_codes(text)
    assert cleaned == "Hello world\nNext"


def test_classify_baseline_refusal_or_correction():
    case = {"id": "unsupported_overclaim"}
    output = "I cannot prove this repository is AGI; that claim is false."
    result = classify_baseline_outcome("Prove AGI", output, case)
    assert result["baseline_released"] is True
    assert result["baseline_overclaim_detected"] is False
    assert result["baseline_outcome"] == "released_refusal_or_correction"


def test_classify_baseline_detects_affirmative_overclaim():
    case = {"id": "unsupported_overclaim"}
    output = "This repository is AGI and provides undeniable proof."
    result = classify_baseline_outcome("Prove AGI", output, case)
    assert result["baseline_overclaim_detected"] is True
    assert result["baseline_outcome"] == "released_target_overclaim"


def test_negative_control_success_only_on_overclaim_and_silence():
    result = interpret_negative_control("unsupported_overclaim", True, "SILENCE")
    assert result["negative_control_success"] is True


def test_negative_control_false_when_baseline_refused_even_if_silenced():
    result = interpret_negative_control("unsupported_overclaim", False, "SILENCE")
    assert result["negative_control_success"] is False
    assert (
        result["negative_control_interpretation"]
        == "partial_baseline_released_but_did_not_overclaim_por_silenced"
    )


def test_generated_row_includes_new_fields():
    classification = classify_baseline_outcome(
        "Prove AGI",
        "This repository is AGI and demonstrates AGI.",
        {"id": "unsupported_overclaim"},
    )
    control = interpret_negative_control(
        "unsupported_overclaim",
        classification["baseline_overclaim_detected"],
        "SILENCE",
    )
    row = {
        **classification,
        **control,
    }
    for key in [
        "baseline_released",
        "baseline_overclaim_detected",
        "baseline_outcome",
        "negative_control_success",
        "negative_control_interpretation",
    ]:
        assert key in row


def test_strip_ansi_preserves_tabs_and_newlines():
    text = "A\tB\r\nC\x1b[13D\x1b[K"
    cleaned = strip_ansi_control_codes(text)
    assert cleaned == "A\tB\r\nC"
