from benchmarks.simpleqa.audit_rows import ERROR_AUDIT_FIELDNAMES, PROBLEM_CASES_FIELDNAMES
from benchmarks.simpleqa.reporting import (
    ERROR_AUDIT_CSV_FILENAME,
    METRICS_JSON_FILENAME,
    PER_EXAMPLE_CSV_FILENAME,
    PROBLEM_CASES_CSV_FILENAME,
    THRESHOLD_SUMMARY_CSV_FILENAME,
    THRESHOLD_SUMMARY_FIELDNAMES,
    TRADEOFF_PLOT_FILENAME,
)


def test_output_artifact_filenames_unchanged() -> None:
    assert PER_EXAMPLE_CSV_FILENAME == "simpleqa_por_results.csv"
    assert ERROR_AUDIT_CSV_FILENAME == "simpleqa_error_audit.csv"
    assert PROBLEM_CASES_CSV_FILENAME == "simpleqa_problem_cases_deduped.csv"
    assert THRESHOLD_SUMMARY_CSV_FILENAME == "simpleqa_threshold_summary.csv"
    assert METRICS_JSON_FILENAME == "simpleqa_por_metrics.json"
    assert TRADEOFF_PLOT_FILENAME == "simpleqa_threshold_tradeoff.png"


def test_threshold_summary_fieldnames_unchanged() -> None:
    assert THRESHOLD_SUMMARY_FIELDNAMES == [
        "threshold",
        "total_examples",
        "answered_count",
        "silence_count",
        "answer_rate",
        "silence_rate",
        "accepted_correct_count",
        "accepted_wrong_count",
        "accepted_precision",
        "accepted_error_rate",
        "false_silence_count",
        "false_silence_rate",
    ]


def test_error_audit_fieldnames_unchanged() -> None:
    assert ERROR_AUDIT_FIELDNAMES == [
        "example_id",
        "threshold",
        "question",
        "reference_answers",
        "baseline_answer",
        "primary_candidate",
        "final_answer_or_effective_answer",
        "normalized_reference_answers",
        "normalized_final_answer",
        "correctness_label",
        "silence_flag",
        "false_silence_flag",
        "self_check_label",
        "contradiction_label",
        "semantic_agreement_score",
        "drift",
        "coherence",
        "instability_v1",
        "risk_v2",
        "risk_v2_1",
        "risk_v2_2",
        "self_check_no_override_applied",
        "decision_v1",
        "decision_v2",
        "decision_v2_1",
        "decision_v2_2",
        "effective_decision",
    ]


def test_problem_case_fieldnames_unchanged() -> None:
    assert PROBLEM_CASES_FIELDNAMES == [
        "example_id",
        "question",
        "reference_answers",
        "baseline_answer",
        "primary_candidate",
        "final_answer_or_effective_answer",
        "correctness_label",
        "silence_flag",
        "false_silence_flag",
        "self_check_label",
        "risk_v2_2",
        "effective_decision",
    ]
