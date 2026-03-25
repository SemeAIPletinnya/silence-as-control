import json
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from api.xai_wrapper import DEFAULT_MODEL, generate_candidate

app = FastAPI(title="silence-as-control")

THRESHOLD = 0.39
SILENCE_TOKEN = "[SILENCE: UNSTABLE OUTPUT BLOCKED]"


class EvaluateRequest(BaseModel):
    prompt: str
    candidate: str
    threshold: float = THRESHOLD


class EvaluateResponse(BaseModel):
    drift: float
    coherence: float
    threshold: float
    decision: str
    release_output: Optional[str] = None
    silence_token: Optional[str] = None
    notes: List[str]


class CompleteRequest(BaseModel):
    prompt: str
    threshold: float = THRESHOLD
    model: str = DEFAULT_MODEL
    system_prompt: str = "You are a precise technical assistant."
    temperature: float = 0.0


class CompleteResponse(BaseModel):
    model: str
    candidate: Optional[str] = None
    drift: float
    coherence: float
    threshold: float
    decision: str
    release_output: Optional[str] = None
    silence_token: Optional[str] = None
    notes: List[str]


class LegacyGenerateRequest(BaseModel):
    output: str
    coherence: float
    drift: float
    threshold: float = THRESHOLD


class LegacyGenerateResponse(BaseModel):
    status: str
    output: Optional[str] = None
    reason: Optional[str] = None


def estimate_drift(prompt: str, candidate: str):
    prompt_lower = prompt.lower()
    candidate_lower = candidate.lower()

    drift = 0.05
    notes: List[str] = []

    if len(candidate.strip()) == 0:
        drift += 0.60
        notes.append("empty_output")

    if len(candidate.strip()) < 8:
        drift += 0.20
        notes.append("too_short")

    risky_markers = [
        "maybe",
        "probably",
        "i think",
        "not sure",
        "guess",
        "possibly",
        "unknown",
    ]
    for marker in risky_markers:
        if marker in candidate_lower:
            drift += 0.08
            notes.append(f"uncertainty:{marker}")

    error_markers = [
        "error",
        "exception",
        "undefined",
        "null pointer",
        "traceback",
        "failed",
    ]
    for marker in error_markers:
        if marker in candidate_lower:
            drift += 0.12
            notes.append(f"error_signal:{marker}")

    if "json" in prompt_lower:
        stripped = candidate.strip()
        if not (stripped.startswith("{") or stripped.startswith("[")):
            drift += 0.30
            notes.append("json_expected_but_structure_missing")

    if "division by zero" in prompt_lower and "0" not in candidate_lower:
        drift += 0.18
        notes.append("missed_zero_division_signal")

    drift = max(0.0, min(drift, 1.0))
    return drift, notes


def estimate_coherence(prompt: str, candidate: str):
    prompt_words = set(
        w.strip(".,:;!?()[]{}\"'").lower()
        for w in prompt.split()
        if w.strip()
    )
    candidate_words = set(
        w.strip(".,:;!?()[]{}\"'").lower()
        for w in candidate.split()
        if w.strip()
    )

    notes: List[str] = []

    if not candidate_words:
        return 0.0, ["no_candidate_tokens"]

    overlap = len(prompt_words.intersection(candidate_words))
    base = overlap / max(len(prompt_words), 1)

    coherence = 0.35 + base

    if len(candidate.strip()) > 20:
        coherence += 0.10
        notes.append("sufficient_length")

    if "{" in candidate and "}" in candidate:
        coherence += 0.06
        notes.append("has_structured_format")

    coherence = max(0.0, min(coherence, 1.0))
    return coherence, notes


def check_json_validity(prompt: str, candidate: str):
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


def por_decision(drift: float, coherence: float, threshold: float) -> str:
    if drift > threshold or coherence < threshold:
        return "SILENCE"
    return "PROCEED"


def evaluate_candidate(prompt: str, candidate: str, threshold: float):
    drift, drift_notes = estimate_drift(prompt, candidate)
    coherence, coherence_notes = estimate_coherence(prompt, candidate)
    json_check = check_json_validity(prompt, candidate)

    decision = por_decision(drift, coherence, threshold)
    notes = drift_notes + coherence_notes + json_check["notes"]

    if json_check["expects_json"] and json_check["is_valid_json"] is False:
        decision = "SILENCE"
        notes.append("forced_silence_invalid_json")

    return {
        "drift": round(drift, 4),
        "coherence": round(coherence, 4),
        "threshold": threshold,
        "decision": decision,
        "release_output": candidate if decision == "PROCEED" else None,
        "silence_token": SILENCE_TOKEN if decision == "SILENCE" else None,
        "notes": notes,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/por/evaluate", response_model=EvaluateResponse, response_model_exclude_none=True)
def evaluate(req: EvaluateRequest):
    result = evaluate_candidate(req.prompt, req.candidate, req.threshold)
    return EvaluateResponse(**result)


@app.post("/generate", response_model=LegacyGenerateResponse, response_model_exclude_none=True)
def legacy_generate(req: LegacyGenerateRequest):
    # Backward-compatible behavior for existing CI tests
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
def complete(req: CompleteRequest):
    candidate = generate_candidate(
        prompt=req.prompt,
        system_prompt=req.system_prompt,
        model=req.model,
        temperature=req.temperature,
    )

    result = evaluate_candidate(req.prompt, candidate, req.threshold)

    return CompleteResponse(
        model=req.model,
        candidate=candidate if result["decision"] == "PROCEED" else None,
        drift=result["drift"],
        coherence=result["coherence"],
        threshold=result["threshold"],
        decision=result["decision"],
        release_output=result["release_output"],
        silence_token=result["silence_token"],
        notes=result["notes"],
    )