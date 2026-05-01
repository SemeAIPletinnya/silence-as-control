from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from benchmarks.simpleqa.dataset_loader import load_simpleqa_dataset
from benchmarks.simpleqa.metrics import (
    compute_baseline_metrics,
    compute_threshold_metrics,
    is_correct,
)
from benchmarks.simpleqa.contradiction_check import parse_contradiction_response
from benchmarks.simpleqa.model_adapter import ModelAdapterError, build_model_adapter
from benchmarks.simpleqa.por_v2 import (
    agreement_score_to_risk,
    compute_risk_v2,
    compute_risk_v2_1,
    compute_risk_v2_2,
    por_v2_decision,
    por_v2_1_decision,
    por_v2_2_decision,
    self_check_label_to_risk,
)
from benchmarks.simpleqa.por_adapter import evaluate_por_gate
from benchmarks.simpleqa.semantic_agreement import semantic_agreement_score
from benchmarks.simpleqa.audit_rows import (
    ERROR_AUDIT_FIELDNAMES,
    PROBLEM_CASES_FIELDNAMES,
    build_error_audit_rows,
    build_problem_cases_deduped_rows,
)
from benchmarks.simpleqa.reporting import (
    build_artifact_paths,
    build_tradeoff_plot,
    to_csv_value,
    write_csv,
    write_metrics_payload,
    write_threshold_summary,
)


def threshold_to_key(threshold: float) -> str:
    """Non-lossy threshold key for grouping/output labels."""
    return format(threshold, ".17g")


def validate_por_samples(value: int) -> int:
    if value < 2:
        raise ValueError("--por-samples must be >= 2 to compute multi-sample drift.")
    return value


def validate_self_check_no_penalty(value: float) -> float:
    if value < 0:
        raise ValueError("self_check_no_penalty must be >= 0. Negative values invert risk behavior.")
    return value


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SimpleQA PoR benchmark harness.")
    parser.add_argument("--dataset-path", required=True, help="Path to local SimpleQA file (.json/.jsonl/.csv).")
    parser.add_argument("--provider", default="openai", help="Model provider (default: openai).")
    parser.add_argument("--model", default="", help="Model name for the selected provider.")
    parser.add_argument("--ollama-model", default="", help="Ollama model name (e.g. qwen2.5:0.5b).")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama base URL.")
    parser.add_argument("--ollama-timeout", type=float, default=60.0, help="Timeout in seconds for Ollama requests.")
    parser.add_argument("--max-examples", type=int, default=None)
    parser.add_argument("--thresholds", type=float, nargs="+", default=[0.35, 0.39, 0.42, 0.43])
    parser.add_argument("--output-dir", default="results/simpleqa")

    parser.add_argument("--question-field", default="question")
    parser.add_argument("--answer-field", default="answer")
    parser.add_argument("--answers-field", default="answers")
    parser.add_argument("--id-field", default="id")
    parser.add_argument(
        "--por-samples",
        type=int,
        default=3,
        help="Number of PoR candidate samples per prompt (minimum: 2).",
    )
    parser.add_argument(
        "--baseline-temperature",
        type=float,
        default=0.0,
        help="Generation temperature for baseline answer (default: 0.0, deterministic).",
    )
    parser.add_argument(
        "--por-temperature",
        type=float,
        default=0.4,
        help="Generation temperature for PoR candidate sampling (default: 0.4).",
    )

    parser.add_argument(
        "--separate-por-call",
        action="store_true",
        help="If set, PoR samples are all newly generated; otherwise baseline answer is reused as sample[0].",
    )
    parser.add_argument(
        "--por-mode",
        choices=["v1", "v2", "v2_1", "v2_2"],
        default="v1",
        help="PoR gating mode: v1 (default), experimental v2, v2_1, or v2_2.",
    )
    parser.add_argument(
        "--self-check-no-penalty",
        type=float,
        default=0.30,
        help="Additive risk penalty in v2_2 when self_check_label == NO.",
    )
    return parser.parse_args()



def run() -> None:
    args = _parse_args()
    provider = args.provider.strip().lower()
    selected_model = args.model.strip()
    if provider == "ollama":
        selected_model = args.ollama_model.strip() or selected_model
    if not selected_model:
        raise SystemExit("A model is required. Use --model (or --ollama-model for --provider ollama).")
    try:
        por_samples = validate_por_samples(args.por_samples)
        validated_self_check_no_penalty = validate_self_check_no_penalty(args.self_check_no_penalty)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    artifact_paths = build_artifact_paths(out_dir)
    per_example_csv = artifact_paths["per_example_csv"]
    metrics_json = artifact_paths["metrics_json"]
    threshold_summary_csv = artifact_paths["threshold_summary_csv"]
    error_audit_csv = artifact_paths["error_audit_csv"]
    deduped_problem_cases_csv = artifact_paths["problem_cases_deduped_csv"]
    tradeoff_plot = artifact_paths["tradeoff_plot"]

    examples = load_simpleqa_dataset(
        dataset_path=args.dataset_path,
        question_field=args.question_field,
        answer_field=args.answer_field,
        answers_field=args.answers_field,
        id_field=args.id_field,
        max_examples=args.max_examples,
    )

    adapter = build_model_adapter(
        provider=args.provider,
        model=selected_model,
        ollama_url=args.ollama_url,
        ollama_timeout=args.ollama_timeout,
    )

    rows: list[dict[str, Any]] = []
    fieldnames = [
        "example_id",
        "question",
        "reference_answers",
        "baseline_answer",
        "por_candidate",
        "por_candidates_json",
        "por_primary_candidate",
        "por_sample_count",
        "por_mode",
        "threshold",
        "threshold_label",
        "threshold_value",
        "drift",
        "coherence",
        "instability_score",
        "semantic_agreement_score",
        "semantic_agreement_risk",
        "self_check_label",
        "self_check_risk",
        "risk_v2",
        "decision_v2",
        "contradiction_label",
        "contradiction_risk",
        "risk_v2_1",
        "decision_v2_1",
        "self_check_no_penalty",
        "self_check_no_override_applied",
        "risk_v2_2",
        "decision_v2_2",
        "effective_decision",
        "por_decision",
        "final_output",
        "correctness_label",
        "silence_flag",
        "false_silence_flag",
        "accepted_error_flag",
        "error",
    ]

    with per_example_csv.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for idx, ex in enumerate(examples, start=1):
            print(f"[{idx}/{len(examples)}] {ex.example_id}")
            try:
                baseline_answer = adapter.answer(
                    ex.question,
                    temperature=args.baseline_temperature,
                )
            except ModelAdapterError as exc:
                err = str(exc)
                baseline_answer = ""
                # record baseline failure and skip threshold rows because no candidate exists
                fail_row = {
                    "example_id": ex.example_id,
                    "question": ex.question,
                    "reference_answers": ex.reference_answers,
                    "baseline_answer": baseline_answer,
                    "por_candidate": "",
                    "por_candidates_json": [],
                    "por_primary_candidate": "",
                    "por_sample_count": 0,
                    "por_mode": args.por_mode,
                    "threshold": "",
                    "threshold_label": "baseline",
                    "threshold_value": "",
                    "drift": "",
                    "coherence": "",
                    "instability_score": "",
                    "semantic_agreement_score": "",
                    "semantic_agreement_risk": "",
                    "self_check_label": "",
                    "self_check_risk": "",
                    "risk_v2": "",
                    "decision_v2": "",
                    "contradiction_label": "",
                    "contradiction_risk": "",
                    "risk_v2_1": "",
                    "decision_v2_1": "",
                    "self_check_no_penalty": "",
                    "self_check_no_override_applied": "",
                    "risk_v2_2": "",
                    "decision_v2_2": "",
                    "effective_decision": "ERROR",
                    "por_decision": "ERROR",
                    "final_output": "",
                    "correctness_label": "wrong",
                    "silence_flag": False,
                    "false_silence_flag": False,
                    "accepted_error_flag": True,
                    "error": err,
                }
                rows.append(fail_row)
                writer.writerow({k: to_csv_value(v) for k, v in fail_row.items()})
                csv_file.flush()
                continue

            baseline_correct = is_correct(baseline_answer, ex.reference_answers)
            baseline_row = {
                "example_id": ex.example_id,
                "question": ex.question,
                "reference_answers": ex.reference_answers,
                "baseline_answer": baseline_answer,
                "por_candidate": baseline_answer,
                "por_candidates_json": [baseline_answer],
                "por_primary_candidate": baseline_answer,
                "por_sample_count": 1,
                "por_mode": args.por_mode,
                "threshold": "",
                "threshold_label": "baseline",
                "threshold_value": "",
                "drift": "",
                "coherence": "",
                "instability_score": "",
                "semantic_agreement_score": "",
                "semantic_agreement_risk": "",
                "self_check_label": "",
                "self_check_risk": "",
                "risk_v2": "",
                "decision_v2": "",
                "contradiction_label": "",
                "contradiction_risk": "",
                "risk_v2_1": "",
                "decision_v2_1": "",
                "self_check_no_penalty": "",
                "self_check_no_override_applied": "",
                "risk_v2_2": "",
                "decision_v2_2": "",
                "effective_decision": "PROCEED",
                "por_decision": "PROCEED",
                "final_output": baseline_answer,
                "correctness_label": "correct" if baseline_correct else "wrong",
                "silence_flag": False,
                "false_silence_flag": False,
                "accepted_error_flag": not baseline_correct,
                "error": "",
            }
            rows.append(baseline_row)
            writer.writerow({k: to_csv_value(v) for k, v in baseline_row.items()})

            por_candidates: list[str] = []
            if not args.separate_por_call:
                por_candidates.append(baseline_answer)
            try:
                while len(por_candidates) < por_samples:
                    por_candidates.append(
                        adapter.answer(
                            ex.question,
                            temperature=args.por_temperature,
                        )
                    )
            except ModelAdapterError as exc:
                err_row = {
                    "example_id": ex.example_id,
                    "question": ex.question,
                    "reference_answers": ex.reference_answers,
                    "baseline_answer": baseline_answer,
                    "por_candidate": "",
                    "por_candidates_json": por_candidates,
                    "por_primary_candidate": "",
                    "por_sample_count": len(por_candidates),
                    "por_mode": args.por_mode,
                    "threshold": "",
                    "threshold_label": "por_candidate_error",
                    "threshold_value": "",
                    "drift": "",
                    "coherence": "",
                    "instability_score": "",
                    "semantic_agreement_score": "",
                    "semantic_agreement_risk": "",
                    "self_check_label": "",
                    "self_check_risk": "",
                    "risk_v2": "",
                    "decision_v2": "",
                    "contradiction_label": "",
                    "contradiction_risk": "",
                    "risk_v2_1": "",
                    "decision_v2_1": "",
                    "self_check_no_penalty": "",
                    "self_check_no_override_applied": "",
                    "risk_v2_2": "",
                    "decision_v2_2": "",
                    "effective_decision": "ERROR",
                    "por_decision": "ERROR",
                    "final_output": "",
                    "correctness_label": "wrong",
                    "silence_flag": True,
                    "false_silence_flag": False,
                    "accepted_error_flag": False,
                    "error": str(exc),
                }
                rows.append(err_row)
                writer.writerow({k: to_csv_value(v) for k, v in err_row.items()})
                csv_file.flush()
                continue

            if len(por_candidates) < 2:
                err_row = {
                    "example_id": ex.example_id,
                    "question": ex.question,
                    "reference_answers": ex.reference_answers,
                    "baseline_answer": baseline_answer,
                    "por_candidate": "",
                    "por_candidates_json": por_candidates,
                    "por_primary_candidate": "",
                    "por_sample_count": len(por_candidates),
                    "por_mode": args.por_mode,
                    "threshold": "",
                    "threshold_label": "por_candidate_error",
                    "threshold_value": "",
                    "drift": "",
                    "coherence": "",
                    "instability_score": "",
                    "semantic_agreement_score": "",
                    "semantic_agreement_risk": "",
                    "self_check_label": "",
                    "self_check_risk": "",
                    "risk_v2": "",
                    "decision_v2": "",
                    "contradiction_label": "",
                    "contradiction_risk": "",
                    "risk_v2_1": "",
                    "decision_v2_1": "",
                    "self_check_no_penalty": "",
                    "self_check_no_override_applied": "",
                    "risk_v2_2": "",
                    "decision_v2_2": "",
                    "effective_decision": "ERROR",
                    "por_decision": "ERROR",
                    "final_output": "",
                    "correctness_label": "wrong",
                    "silence_flag": True,
                    "false_silence_flag": False,
                    "accepted_error_flag": False,
                    "error": "Insufficient PoR candidate samples to compute drift.",
                }
                rows.append(err_row)
                writer.writerow({k: to_csv_value(v) for k, v in err_row.items()})
                csv_file.flush()
                continue

            por_candidate = por_candidates[0]
            candidate_correct = is_correct(por_candidate, ex.reference_answers)
            agreement_score = semantic_agreement_score(por_candidates)
            agreement_risk = agreement_score_to_risk(agreement_score)
            self_check_label = ""
            self_check_risk = ""
            contradiction_label = ""
            contradiction_risk = ""
            if args.por_mode in ("v2", "v2_1", "v2_2"):
                try:
                    self_check_label = adapter.self_check(ex.question, por_candidate)
                except ModelAdapterError as exc:
                    err_row = {
                        "example_id": ex.example_id,
                        "question": ex.question,
                        "reference_answers": ex.reference_answers,
                        "baseline_answer": baseline_answer,
                        "por_candidate": por_candidate,
                        "por_candidates_json": por_candidates,
                        "por_primary_candidate": por_candidate,
                        "por_sample_count": len(por_candidates),
                        "por_mode": args.por_mode,
                        "threshold": "",
                        "threshold_label": "self_check_error",
                        "threshold_value": "",
                        "drift": "",
                        "coherence": "",
                        "instability_score": "",
                        "semantic_agreement_score": agreement_score,
                        "semantic_agreement_risk": agreement_risk,
                        "self_check_label": "",
                        "self_check_risk": "",
                        "risk_v2": "",
                        "decision_v2": "",
                        "contradiction_label": "",
                        "contradiction_risk": "",
                        "risk_v2_1": "",
                        "decision_v2_1": "",
                        "self_check_no_penalty": "",
                        "self_check_no_override_applied": "",
                        "risk_v2_2": "",
                        "decision_v2_2": "",
                        "effective_decision": "ERROR",
                        "por_decision": "ERROR",
                        "final_output": "",
                        "correctness_label": "wrong",
                        "silence_flag": True,
                        "false_silence_flag": False,
                        "accepted_error_flag": False,
                        "error": str(exc),
                    }
                    rows.append(err_row)
                    writer.writerow({k: to_csv_value(v) for k, v in err_row.items()})
                    csv_file.flush()
                    continue
                self_check_risk = self_check_label_to_risk(self_check_label)

            if args.por_mode in ("v2_1", "v2_2"):
                try:
                    contradiction_text = adapter.contradiction_check(ex.question, por_candidate)
                    contradiction_result = parse_contradiction_response(contradiction_text)
                    contradiction_label = contradiction_result.label
                    contradiction_risk = contradiction_result.risk
                except ModelAdapterError as exc:
                    err_row = {
                        "example_id": ex.example_id,
                        "question": ex.question,
                        "reference_answers": ex.reference_answers,
                        "baseline_answer": baseline_answer,
                        "por_candidate": por_candidate,
                        "por_candidates_json": por_candidates,
                        "por_primary_candidate": por_candidate,
                        "por_sample_count": len(por_candidates),
                        "por_mode": args.por_mode,
                        "threshold": "",
                        "threshold_label": "contradiction_check_error",
                        "threshold_value": "",
                        "drift": "",
                        "coherence": "",
                        "instability_score": "",
                        "semantic_agreement_score": agreement_score,
                        "semantic_agreement_risk": agreement_risk,
                        "self_check_label": self_check_label,
                        "self_check_risk": self_check_risk,
                        "risk_v2": "",
                        "decision_v2": "",
                        "contradiction_label": "",
                        "contradiction_risk": "",
                        "risk_v2_1": "",
                        "decision_v2_1": "",
                        "self_check_no_penalty": "",
                        "self_check_no_override_applied": "",
                        "risk_v2_2": "",
                        "decision_v2_2": "",
                        "effective_decision": "ERROR",
                        "por_decision": "ERROR",
                        "final_output": "",
                        "correctness_label": "wrong",
                        "silence_flag": True,
                        "false_silence_flag": False,
                        "accepted_error_flag": False,
                        "error": str(exc),
                    }
                    rows.append(err_row)
                    writer.writerow({k: to_csv_value(v) for k, v in err_row.items()})
                    csv_file.flush()
                    continue

            for threshold in args.thresholds:
                threshold_key = threshold_to_key(threshold)
                eval_result = evaluate_por_gate(
                    prompt=ex.question,
                    primary_candidate=por_candidate,
                    candidate_samples=por_candidates,
                    threshold=threshold,
                )
                risk_v2 = ""
                decision_v2 = ""
                risk_v2_1 = ""
                decision_v2_1 = ""
                self_check_no_penalty = ""
                self_check_no_override_applied = ""
                risk_v2_2 = ""
                decision_v2_2 = ""
                effective_decision = eval_result.por_decision
                if args.por_mode == "v2":
                    risk_v2 = compute_risk_v2(
                        instability_v1=eval_result.instability_score,
                        agreement_risk=agreement_risk,
                        self_check_risk=float(self_check_risk),
                    )
                    decision_v2 = por_v2_decision(risk_v2=risk_v2, threshold=threshold)
                    effective_decision = decision_v2
                if args.por_mode in ("v2_1", "v2_2"):
                    risk_v2_1 = compute_risk_v2_1(
                        instability_v1=eval_result.instability_score,
                        agreement_risk=agreement_risk,
                        self_check_risk=float(self_check_risk),
                        contradiction_risk=float(contradiction_risk),
                    )
                    decision_v2_1 = por_v2_1_decision(risk_v2_1=risk_v2_1, threshold=threshold)
                    effective_decision = decision_v2_1
                if args.por_mode == "v2_2":
                    self_check_no_penalty = validated_self_check_no_penalty
                    risk_v2_2, no_override_applied = compute_risk_v2_2(
                        risk_v2_1=float(risk_v2_1),
                        self_check_label=str(self_check_label),
                        self_check_no_penalty=self_check_no_penalty,
                    )
                    self_check_no_override_applied = no_override_applied
                    decision_v2_2 = por_v2_2_decision(risk_v2_2=risk_v2_2, threshold=threshold)
                    effective_decision = decision_v2_2
                silence_flag = effective_decision == "SILENCE"
                final_output = "" if silence_flag else por_candidate
                correctness_label = "wrong" if silence_flag else ("correct" if candidate_correct else "wrong")
                false_silence_flag = silence_flag and candidate_correct
                accepted_error_flag = (not silence_flag) and (not candidate_correct)

                row = {
                    "example_id": ex.example_id,
                    "question": ex.question,
                    "reference_answers": ex.reference_answers,
                    "baseline_answer": baseline_answer,
                    "por_candidate": por_candidate,
                    "por_candidates_json": por_candidates,
                    "por_primary_candidate": por_candidate,
                    "por_sample_count": len(por_candidates),
                    "por_mode": args.por_mode,
                    "threshold": threshold_key,
                    "threshold_label": threshold_key,
                    "threshold_value": threshold,
                    "drift": eval_result.drift,
                    "coherence": eval_result.coherence,
                    "instability_score": eval_result.instability_score,
                    "semantic_agreement_score": agreement_score,
                    "semantic_agreement_risk": agreement_risk,
                    "self_check_label": self_check_label,
                    "self_check_risk": self_check_risk,
                    "risk_v2": risk_v2,
                    "decision_v2": decision_v2,
                    "contradiction_label": contradiction_label,
                    "contradiction_risk": contradiction_risk,
                    "risk_v2_1": risk_v2_1,
                    "decision_v2_1": decision_v2_1,
                    "self_check_no_penalty": self_check_no_penalty,
                    "self_check_no_override_applied": self_check_no_override_applied,
                    "risk_v2_2": risk_v2_2,
                    "decision_v2_2": decision_v2_2,
                    "effective_decision": effective_decision,
                    "por_decision": eval_result.por_decision,
                    "final_output": final_output,
                    "correctness_label": correctness_label,
                    "silence_flag": silence_flag,
                    "false_silence_flag": false_silence_flag,
                    "accepted_error_flag": accepted_error_flag,
                    "error": "",
                }
                rows.append(row)
                writer.writerow({k: to_csv_value(v) for k, v in row.items()})

            csv_file.flush()

    error_audit_rows = build_error_audit_rows(rows)
    write_csv(
        error_audit_csv,
        fieldnames=ERROR_AUDIT_FIELDNAMES,
        rows=error_audit_rows,
    )
    deduped_problem_rows = build_problem_cases_deduped_rows(rows)
    write_csv(
        deduped_problem_cases_csv,
        fieldnames=PROBLEM_CASES_FIELDNAMES,
        rows=deduped_problem_rows,
    )

    baseline_metrics = compute_baseline_metrics(rows)
    threshold_metrics = [compute_threshold_metrics(rows, t) for t in args.thresholds]

    write_threshold_summary(threshold_summary_csv, threshold_metrics)

    plot_path = build_tradeoff_plot(threshold_summary_csv, tradeoff_plot)

    write_metrics_payload(
        metrics_json,
        args,
        por_samples,
        validated_self_check_no_penalty,
        baseline_metrics,
        threshold_metrics,
        artifact_paths,
        plot_path,
    )

    print("Done.")
    print(f"- {per_example_csv}")
    print(f"- {error_audit_csv}")
    print(f"- {deduped_problem_cases_csv}")
    print(f"- {threshold_summary_csv}")
    print(f"- {metrics_json}")
    print(f"- {plot_path}")


if __name__ == "__main__":
    run()
