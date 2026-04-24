"""API runtime surface for Silence-as-Control.

Layering in this module:
- CORE decision primitive: imported from `api.core_primitive`.
- RUNTIME extensions: imported from `api.por_runtime`.
- EXPERIMENTAL recovery: imported from `api.experimental_recovery`.
"""

import json
import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from api.core_primitive import (
    CORE_FIXED_THRESHOLD,
    compute_instability_score,
    fixed_threshold_release_decision,
)
from api.experimental_recovery import (
    get_experimental_margin,
    maybe_short_regen,
)
from api.por_runtime import (
    compute_adaptive_threshold,
    estimate_coherence,
    estimate_drift,
    get_runtime_threshold,
)
from api.xai_wrapper import DEFAULT_MODEL, generate_candidate

app = FastAPI(title="silence-as-control")
LOGGER = logging.getLogger(__name__)

# Runtime default threshold used by API endpoints.
# It starts from the core fixed threshold (0.39), but can be overridden by
# runtime configuration (`POR_RUNTIME_GATE_THRESHOLD`).
RUNTIME_DEFAULT_THRESHOLD = get_runtime_threshold(CORE_FIXED_THRESHOLD)
SILENCE_TOKEN = "[SILENCE: UNSTABLE OUTPUT BLOCKED]"


class EvaluateRequest(BaseModel):
    prompt: str
    candidate: str
    threshold: Optional[float] = None
    use_adaptive_threshold: bool = False
    recent_drifts: List[float] = Field(default_factory=list)
    recent_coherences: List[float] = Field(default_factory=list)


class EvaluateResponse(BaseModel):
    drift: float
    coherence: float
    instability_score: float
    threshold: float
    decision: str
    release_output: Optional[str] = None
    silence_token: Optional[str] = None
    notes: List[str]


class CompleteRequest(BaseModel):
    prompt: str
    threshold: Optional[float] = None
    use_adaptive_threshold: bool = False
    recent_drifts: List[float] = Field(default_factory=list)
    recent_coherences: List[float] = Field(default_factory=list)
    model: str = DEFAULT_MODEL
    system_prompt: str = "You are a precise technical assistant."
    temperature: float = 0.0
    drift_samples: int = 3
    enable_experimental_short_regen: bool = True
    # Backward-compatible alias for older clients.
    enable_short_regen: Optional[bool] = None


class CompleteResponse(BaseModel):
    model: str
    candidate: Optional[str] = None
    drift: float
    coherence: float
    instability_score: float
    threshold: float
    decision: str
    release_output: Optional[str] = None
    silence_token: Optional[str] = None
    notes: List[str]


class LegacyGenerateRequest(BaseModel):
    output: str
    coherence: float
    drift: float
    threshold: float = RUNTIME_DEFAULT_THRESHOLD


class LegacyGenerateResponse(BaseModel):
    status: str
    output: Optional[str] = None
    reason: Optional[str] = None


def check_json_validity(prompt: str, candidate: str) -> dict:
    """[RUNTIME] Enforce JSON validity when prompt explicitly asks for JSON."""
    prompt_lower = prompt.lower()
    notes: List[str] = []

    expects_json = "json" in prompt_lower

    if not expects_json:
        return {
            "expects_json": False,
            "is_valid_json": None,
            "parsed_json": None,
            "notes": notes,
        }

    try:
        parsed = json.loads(candidate)
        notes.append("valid_json")
        return {
            "expects_json": True,
            "is_valid_json": True,
            "parsed_json": parsed,
            "notes": notes,
        }
    except Exception:
        notes.append("invalid_json")
        return {
            "expects_json": True,
            "is_valid_json": False,
            "parsed_json": None,
            "notes": notes,
        }


def resolve_runtime_threshold(
    request_threshold: Optional[float],
    use_adaptive_threshold: bool,
    recent_drifts: List[float],
    recent_coherences: List[float],
) -> float:
    """[RUNTIME] Resolve the threshold used by API runtime decisions.

    - default mode: fixed threshold.
    - optional mode: adaptive threshold from recent history.
    """
    fixed_threshold = (
        request_threshold if request_threshold is not None else RUNTIME_DEFAULT_THRESHOLD
    )
    fixed_threshold = max(0.0, min(fixed_threshold, 1.0))
    if not use_adaptive_threshold:
        return fixed_threshold
    return compute_adaptive_threshold(
        base_threshold=fixed_threshold,
        recent_drifts=recent_drifts,
        recent_coherences=recent_coherences,
    )


def score_candidate_runtime(
    prompt: str,
    candidate: str,
    threshold: float,
    candidate_samples: Optional[List[str]] = None,
) -> dict:
    """[RUNTIME] Score one candidate and apply the core release decision."""
    samples = candidate_samples or [candidate]
    drift, drift_notes = estimate_drift(samples)
    coherence, coherence_notes = estimate_coherence(prompt, candidate)
    instability = compute_instability_score(drift=drift, coherence=coherence)
    json_check = check_json_validity(prompt, candidate)

    decision = fixed_threshold_release_decision(instability, threshold)
    notes = drift_notes + coherence_notes + json_check["notes"]

    if json_check["expects_json"] and json_check["is_valid_json"] is False:
        decision = "SILENCE"
        notes.append("forced_silence_invalid_json")

    LOGGER.info(
        "por_runtime_scoring drift=%.4f coherence=%.4f instability=%.4f threshold=%.4f decision=%s",
        drift,
        coherence,
        instability,
        threshold,
        decision,
    )

    return {
        "drift": round(drift, 4),
        "coherence": round(coherence, 4),
        "instability_score": round(instability, 4),
        "threshold": threshold,
        "decision": decision,
        "release_output": candidate if decision == "PROCEED" else None,
        "silence_token": SILENCE_TOKEN if decision == "SILENCE" else None,
        "notes": notes,
    }


def resolve_experimental_short_regen_flag(req: CompleteRequest) -> bool:
    """[EXPERIMENTAL] Resolve regen enable flag with alias compatibility."""
    if req.enable_short_regen is None:
        return req.enable_experimental_short_regen
    return req.enable_short_regen


@app.get("/health")
def health() -> dict:
    """Health endpoint for API runtime checks."""
    return {"status": "healthy"}


@app.post("/por/evaluate", response_model=EvaluateResponse, response_model_exclude_none=True)
def evaluate(req: EvaluateRequest) -> EvaluateResponse:
    """Evaluate a provided candidate with core gate + runtime estimators."""
    try:
        threshold = resolve_runtime_threshold(
            request_threshold=req.threshold,
            use_adaptive_threshold=req.use_adaptive_threshold,
            recent_drifts=req.recent_drifts,
            recent_coherences=req.recent_coherences,
        )
        result = score_candidate_runtime(req.prompt, req.candidate, threshold)
        return EvaluateResponse(**result)
    except Exception:
        LOGGER.exception("por_evaluate_failed")
        raise HTTPException(status_code=500, detail="por_evaluate_failed")


@app.post("/generate", response_model=LegacyGenerateResponse, response_model_exclude_none=True)
def legacy_generate(req: LegacyGenerateRequest) -> LegacyGenerateResponse:
    """Backward-compatible legacy endpoint preserved for existing tests/clients."""
    if req.coherence >= 0.8:
        return LegacyGenerateResponse(
            status="ok",
            output=req.output,
        )

    return LegacyGenerateResponse(
        status="abstained",
        reason="control_abstention",
    )


@app.post("/por/complete", response_model=CompleteResponse, response_model_exclude_none=True)
def complete(req: CompleteRequest) -> CompleteResponse:
    """Generate candidate(s), score with PoR gate, then optionally run experimental recovery."""
    try:
        threshold = resolve_runtime_threshold(
            request_threshold=req.threshold,
            use_adaptive_threshold=req.use_adaptive_threshold,
            recent_drifts=req.recent_drifts,
            recent_coherences=req.recent_coherences,
        )

        sample_count = max(1, req.drift_samples)
        candidates: List[str] = []
        for _ in range(sample_count):
            candidates.append(
                generate_candidate(
                    prompt=req.prompt,
                    model=req.model,
                    system_prompt=req.system_prompt,
                    temperature=req.temperature,
                )
            )

        primary_candidate = candidates[0]
        result = score_candidate_runtime(
            prompt=req.prompt,
            candidate=primary_candidate,
            threshold=threshold,
            candidate_samples=candidates,
        )

        # Experimental lane only: MAYBE_SHORT_REGEN is post-silence and non-core.
        if result["decision"] == "SILENCE":

            def _regen_once() -> dict:
                regen_candidate = generate_candidate(
                    prompt=(
                        "Answer briefly and directly in <= 80 tokens. "
                        "Avoid uncertainty wording.\n\n"
                        f"Prompt: {req.prompt}"
                    ),
                    model=req.model,
                    system_prompt=req.system_prompt,
                    temperature=min(req.temperature, 0.2),
                )
                regen_result = score_candidate_runtime(
                    prompt=req.prompt,
                    candidate=regen_candidate,
                    threshold=threshold,
                    candidate_samples=[regen_candidate],
                )
                regen_result["release_output"] = (
                    regen_candidate if regen_result["decision"] == "PROCEED" else None
                )
                regen_result["_regen_candidate"] = regen_candidate
                return regen_result

            attempted, regen_result = maybe_short_regen(
                enabled=resolve_experimental_short_regen_flag(req),
                instability_score=result["instability_score"],
                threshold=threshold,
                run_regen=_regen_once,
            )

            if attempted and regen_result is not None:
                regen_result["notes"] = regen_result["notes"] + [
                    (
                        "experimental_maybe_short_regen_attempted"
                        f":margin={get_experimental_margin():.2f}"
                    )
                ]
                if regen_result["decision"] == "PROCEED":
                    result = regen_result
                    candidates[0] = regen_result["_regen_candidate"]
                else:
                    result["notes"].append("experimental_maybe_short_regen_failed")

        return CompleteResponse(
            model=req.model,
            candidate=candidates[0] if result["decision"] == "PROCEED" else None,
            drift=result["drift"],
            coherence=result["coherence"],
            instability_score=result["instability_score"],
            threshold=result["threshold"],
            decision=result["decision"],
            release_output=result["release_output"],
            silence_token=result["silence_token"],
            notes=result["notes"],
        )
    except Exception:
        LOGGER.exception("por_complete_failed")
        raise HTTPException(status_code=500, detail="por_complete_failed")
