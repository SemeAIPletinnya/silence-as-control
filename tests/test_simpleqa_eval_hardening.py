from pathlib import Path

from benchmarks.simpleqa.dataset_loader import load_simpleqa_dataset
from benchmarks.simpleqa.metrics import is_correct
from benchmarks.simpleqa.run_simpleqa_por import (
    _build_error_audit_rows,
    _build_problem_cases_deduped_rows,
)


def test_is_correct_supports_formula_and_unit_normalization() -> None:
    assert is_correct("Water is H₂O.", ["H2O"])
    assert is_correct("carbon dioxide is CO₂", ["CO2"])
    assert is_correct("100 degrees Celsius", ["100°C"])
    assert is_correct("0 degrees Celsius", ["0°C"])
    assert is_correct("The symbol is Au.", ["Au"])
    assert is_correct("The capital of France is Paris.", ["Paris"])


def test_is_correct_does_not_overmatch_short_symbol_inside_word() -> None:
    assert not is_correct("August is often hot.", ["Au"])


def test_is_correct_requires_celsius_unit_not_just_number() -> None:
    assert not is_correct("100", ["100°C"])


def test_is_correct_does_not_map_co2_to_carbon_monoxide() -> None:
    assert not is_correct("carbon monoxide", ["CO2"])


def test_is_correct_single_letter_symbol_does_not_expand_to_word() -> None:
    # Conservative benchmark behavior: symbol references require token-level symbol match.
    assert not is_correct("oxygen", ["O"])


def test_is_correct_normalizes_number_words_for_short_numeric_references() -> None:
    assert is_correct("There are seven continents on Earth.", ["7"])
    assert is_correct("A triangle has three sides.", ["3"])
    assert is_correct("A hexagon has six sides.", ["6"])


def test_is_correct_number_word_normalization_is_not_overly_permissive() -> None:
    assert not is_correct("There are seven continents on Earth.", ["8"])


def test_error_audit_rows_include_expected_fields() -> None:
    rows = [
        {
            "example_id": "q001",
            "threshold_label": "0.4",
            "threshold": "0.4",
            "question": "Boiling point of water in celsius?",
            "reference_answers": ["100°C"],
            "baseline_answer": "100°C",
            "por_primary_candidate": "100 degrees Celsius",
            "final_output": "100 degrees Celsius",
            "correctness_label": "correct",
            "silence_flag": False,
            "false_silence_flag": False,
            "self_check_label": "YES",
            "contradiction_label": "NO_CONTRADICTION",
            "semantic_agreement_score": 1.0,
            "drift": 0.0,
            "coherence": 1.0,
            "instability_score": 0.0,
            "risk_v2": 0.0,
            "risk_v2_1": 0.0,
            "risk_v2_2": 0.0,
            "self_check_no_override_applied": False,
            "por_decision": "PROCEED",
            "decision_v2": "PROCEED",
            "decision_v2_1": "PROCEED",
            "decision_v2_2": "PROCEED",
            "effective_decision": "PROCEED",
        }
    ]
    audit_rows = _build_error_audit_rows(rows)
    assert len(audit_rows) == 1
    assert "normalized_reference_answers" in audit_rows[0]
    assert "normalized_final_answer" in audit_rows[0]
    assert audit_rows[0]["normalized_final_answer"] == "100 celsius"


def test_error_audit_rows_use_effective_answer_fallback() -> None:
    rows = [
        {
            "example_id": "q060",
            "threshold_label": "0.42",
            "threshold": "0.42",
            "question": "Q",
            "reference_answers": ["A"],
            "baseline_answer": "baseline-ans",
            "por_primary_candidate": "candidate-ans",
            "final_output": "",
            "correctness_label": "wrong",
            "silence_flag": True,
            "false_silence_flag": True,
            "self_check_label": "NO",
            "effective_decision": "SILENCE",
        }
    ]
    audit_rows = _build_error_audit_rows(rows)
    assert len(audit_rows) == 1
    assert audit_rows[0]["final_answer_or_effective_answer"] == "candidate-ans"
    assert audit_rows[0]["normalized_final_answer"] == "candidate ans"


def test_problem_cases_dedupes_example_ids() -> None:
    rows = [
        {
            "example_id": "q021",
            "threshold_label": "0.35",
            "threshold": "0.35",
            "question": "Q",
            "reference_answers": ["A"],
            "baseline_answer": "B0",
            "por_primary_candidate": "B",
            "final_output": "B",
            "correctness_label": "wrong",
            "silence_flag": False,
            "false_silence_flag": False,
            "self_check_label": "YES",
            "risk_v2_2": 0.2,
            "effective_decision": "PROCEED",
        },
        {
            "example_id": "q021",
            "threshold_label": "0.43",
            "threshold": "0.43",
            "question": "Q",
            "reference_answers": ["A"],
            "baseline_answer": "B0",
            "por_primary_candidate": "B",
            "final_output": "B",
            "correctness_label": "wrong",
            "silence_flag": False,
            "false_silence_flag": False,
            "self_check_label": "YES",
            "risk_v2_2": 0.2,
            "effective_decision": "PROCEED",
        },
    ]
    deduped_rows = _build_problem_cases_deduped_rows(rows)
    assert len(deduped_rows) == 1
    assert deduped_rows[0]["example_id"] == "q021"
    assert deduped_rows[0]["primary_candidate"] == "B"


def test_problem_cases_use_fallback_answer_fields_for_silence_rows() -> None:
    rows = [
        {
            "example_id": "q060",
            "threshold_label": "0.42",
            "threshold": "0.42",
            "question": "Q1",
            "reference_answers": ["A1"],
            "baseline_answer": "baseline-1",
            "por_primary_candidate": "candidate-1",
            "final_output": "",
            "correctness_label": "wrong",
            "silence_flag": True,
            "false_silence_flag": True,
            "self_check_label": "NO",
            "risk_v2_2": 0.9,
            "effective_decision": "SILENCE",
        },
        {
            "example_id": "q061",
            "threshold_label": "0.42",
            "threshold": "0.42",
            "question": "Q2",
            "reference_answers": ["A2"],
            "baseline_answer": "baseline-2",
            "por_primary_candidate": "",
            "final_output": "",
            "correctness_label": "wrong",
            "silence_flag": True,
            "false_silence_flag": True,
            "self_check_label": "NO",
            "risk_v2_2": 0.9,
            "effective_decision": "SILENCE",
        },
    ]
    deduped_rows = _build_problem_cases_deduped_rows(rows)
    assert len(deduped_rows) == 2
    by_id = {row["example_id"]: row for row in deduped_rows}
    assert by_id["q060"]["final_answer_or_effective_answer"] == "candidate-1"
    assert by_id["q061"]["final_answer_or_effective_answer"] == "baseline-2"


def test_clean_dataset_loads_with_expected_schema_and_size() -> None:
    dataset_path = Path("data/simpleqa_clean_100.jsonl")
    examples = load_simpleqa_dataset(dataset_path)
    assert len(examples) == 100
    assert examples[0].example_id
    assert examples[0].question
    assert examples[0].reference_answers


def test_clean_dataset_q057_supports_canonical_gravity_alternatives() -> None:
    dataset_path = Path("data/simpleqa_clean_100.jsonl")
    examples = load_simpleqa_dataset(dataset_path)
    q057 = next(example for example in examples if example.example_id == "q057")
    assert "Gravity" in q057.reference_answers
    assert "gravitational force" in q057.reference_answers
