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
from benchmarks.simpleqa.por_adapter import evaluate_por_gate

DEFAULT_MODE = "v1"
ALLOWED_MODES = {"v1"}


def _load_input(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object")
    if "prompt" not in payload or "candidate_answer" not in payload:
        raise ValueError("input JSON must include 'prompt' and 'candidate_answer'")
    return payload


def _resolve_candidate_samples(payload: dict[str, Any]) -> list[str]:
    samples = payload.get("candidate_samples")
    candidate_answer = str(payload.get("candidate_answer", ""))

    if isinstance(samples, list):
        cleaned = [str(item) for item in samples if str(item).strip()]
        if cleaned:
            return cleaned
    return [candidate_answer]


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

    decision = evaluation.por_decision
    return {
        "decision": decision,
        "released_output": candidate_answer if decision == "PROCEED" else None,
        "silence": decision == "SILENCE",
        "threshold": evaluation.threshold,
        "mode": mode,
        "signals": {
            "drift": evaluation.drift,
            "coherence": evaluation.coherence,
            "instability": evaluation.instability_score,
        },
        "audit": {
            "reason": (
                "candidate below instability threshold"
                if decision == "PROCEED"
                else "candidate exceeded instability threshold"
            ),
            "model": metadata.get("model"),
            "source": metadata.get("source"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal external PoR release-gate CLI")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--mode", default=None)
    args = parser.parse_args()

    payload = _load_input(args.input)
    result = _build_output(payload, args.threshold, args.mode)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
