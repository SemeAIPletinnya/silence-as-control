from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.core_primitive import CORE_FIXED_THRESHOLD
from api.release_policy import apply_release_policy
from benchmarks.simpleqa.por_adapter import evaluate_por_gate

DEFAULT_MODE = "v1"
ALLOWED_MODES = {"v1"}


def _load_input(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object")
    if "prompt" not in payload:
        raise ValueError("input JSON must include 'prompt'")
    if "candidate_answer" not in payload or not str(payload.get("candidate_answer", "")).strip():
        raise ValueError("input JSON must include non-empty 'candidate_answer'")
    return payload


def _resolve_candidate_samples(payload: dict[str, Any]) -> list[str]:
    samples = payload.get("candidate_samples")
    candidate_answer = str(payload.get("candidate_answer", ""))

    if samples is None:
        return [candidate_answer]
    if not isinstance(samples, list):
        raise ValueError("'candidate_samples' must be a list of strings when provided")
    if any(not isinstance(item, str) for item in samples):
        raise ValueError("'candidate_samples' items must all be strings")
    cleaned = [item.strip() for item in samples if item.strip()]
    if not cleaned:
        raise ValueError("'candidate_samples' must contain at least one non-empty item")
    return cleaned


def _resolve_mode(payload: dict[str, Any], mode_override: str | None) -> str:
    mode = mode_override if mode_override is not None else str(payload.get("mode", DEFAULT_MODE))
    if mode not in ALLOWED_MODES:
        allowed = ", ".join(sorted(ALLOWED_MODES))
        raise ValueError(f"unsupported mode: {mode}. allowed modes: {allowed}")
    return mode


def _build_output(payload: dict[str, Any], threshold_override: float | None, mode_override: str | None) -> dict[str, Any]:
    prompt = str(payload.get("prompt", ""))
    candidate_answer = str(payload.get("candidate_answer", ""))

    threshold = (
        threshold_override
        if threshold_override is not None
        else float(payload.get("threshold", CORE_FIXED_THRESHOLD))
    )
    mode = _resolve_mode(payload, mode_override)

    candidate_samples = _resolve_candidate_samples(payload)

    evaluation = evaluate_por_gate(
        prompt=prompt,
        primary_candidate=candidate_answer,
        candidate_samples=candidate_samples,
        threshold=threshold,
    )

    metadata = payload.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}

    core_decision = evaluation.por_decision
    policy = apply_release_policy(core_decision=core_decision, candidate=candidate_answer)
    decision = policy.decision
    return {
        "decision": decision,
        "released_output": candidate_answer if decision == "PROCEED" else "",
        "silence": decision == "SILENCE",
        "needs_review": decision == "NEEDS_REVIEW",
        "threshold": evaluation.threshold,
        "mode": mode,
        "signals": {
            "drift": evaluation.drift,
            "coherence": evaluation.coherence,
            "instability": evaluation.instability_score,
            "review_flags": policy.review_flags,
        },
        "audit": {
            "reason": policy.reason,
            "core_decision": policy.core_decision,
            "policy_decision": policy.decision,
            "model": metadata.get("model"),
            "source": metadata.get("source"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal external PoR release-gate CLI")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=False, type=Path)
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--mode", default=None)
    args = parser.parse_args()

    try:
        payload = _load_input(args.input)
        result = _build_output(payload, args.threshold, args.mode)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            f.write("\n")
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
