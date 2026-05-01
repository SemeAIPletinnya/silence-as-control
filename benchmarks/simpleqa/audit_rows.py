from __future__ import annotations

from typing import Any

from benchmarks.simpleqa.metrics import normalize_text


ERROR_AUDIT_FIELDNAMES = [
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

PROBLEM_CASES_FIELDNAMES = [
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


def normalized_references(references: Any) -> list[str]:
    if not isinstance(references, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for ref in references:
        norm_ref = normalize_text(str(ref))
        if norm_ref and norm_ref not in seen:
            seen.add(norm_ref)
            normalized.append(norm_ref)
    return normalized


def effective_answer_for_problem_case(row: dict[str, Any]) -> str:
    final_output = str(row.get("final_output", "") or "").strip()
    if final_output:
        return final_output
    primary_candidate = str(row.get("por_primary_candidate", "") or "").strip()
    if primary_candidate:
        return primary_candidate
    return str(row.get("baseline_answer", "") or "").strip()


def build_error_audit_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    audit_rows: list[dict[str, Any]] = []
    for row in rows:
        if row.get("threshold_label") == "baseline":
            continue
        effective_answer = effective_answer_for_problem_case(row)
        audit_rows.append(
            {
                "example_id": row.get("example_id", ""),
                "threshold": row.get("threshold", ""),
                "question": row.get("question", ""),
                "reference_answers": row.get("reference_answers", []),
                "baseline_answer": row.get("baseline_answer", ""),
                "primary_candidate": row.get("por_primary_candidate", ""),
                "final_answer_or_effective_answer": effective_answer,
                "normalized_reference_answers": normalized_references(row.get("reference_answers", [])),
                "normalized_final_answer": normalize_text(str(effective_answer)),
                "correctness_label": row.get("correctness_label", ""),
                "silence_flag": row.get("silence_flag", ""),
                "false_silence_flag": row.get("false_silence_flag", ""),
                "self_check_label": row.get("self_check_label", ""),
                "contradiction_label": row.get("contradiction_label", ""),
                "semantic_agreement_score": row.get("semantic_agreement_score", ""),
                "drift": row.get("drift", ""),
                "coherence": row.get("coherence", ""),
                "instability_v1": row.get("instability_score", ""),
                "risk_v2": row.get("risk_v2", ""),
                "risk_v2_1": row.get("risk_v2_1", ""),
                "risk_v2_2": row.get("risk_v2_2", ""),
                "self_check_no_override_applied": row.get("self_check_no_override_applied", ""),
                "decision_v1": row.get("por_decision", ""),
                "decision_v2": row.get("decision_v2", ""),
                "decision_v2_1": row.get("decision_v2_1", ""),
                "decision_v2_2": row.get("decision_v2_2", ""),
                "effective_decision": row.get("effective_decision", ""),
            }
        )
    return audit_rows


def build_problem_cases_deduped_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    problem_rows = [
        row
        for row in rows
        if row.get("threshold_label")
        not in {"baseline", "por_candidate_error", "self_check_error", "contradiction_check_error"}
        and (
            row.get("false_silence_flag", False)
            or (row.get("effective_decision") == "PROCEED" and row.get("correctness_label") == "wrong")
        )
    ]
    problem_rows.sort(key=lambda r: (str(r.get("example_id", "")), str(r.get("threshold", ""))))

    deduped: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for row in problem_rows:
        example_id = str(row.get("example_id", ""))
        if example_id in seen_ids:
            continue
        seen_ids.add(example_id)
        deduped.append(
            {
                "example_id": example_id,
                "question": row.get("question", ""),
                "reference_answers": row.get("reference_answers", []),
                "baseline_answer": row.get("baseline_answer", ""),
                "primary_candidate": row.get("por_primary_candidate", ""),
                "final_answer_or_effective_answer": effective_answer_for_problem_case(row),
                "correctness_label": row.get("correctness_label", ""),
                "silence_flag": row.get("silence_flag", ""),
                "false_silence_flag": row.get("false_silence_flag", ""),
                "self_check_label": row.get("self_check_label", ""),
                "risk_v2_2": row.get("risk_v2_2", ""),
                "effective_decision": row.get("effective_decision", ""),
            }
        )
    return deduped
