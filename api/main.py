"""FastAPI application for silence-as-control middleware."""

from fastapi import FastAPI

from silence_as_control.control import por_control
from silence_as_control.logging_utils import log_decision
from silence_as_control.schema import GenerateRequest, GenerateResponse

app = FastAPI(title="silence-as-control")


@app.post("/generate", response_model=GenerateResponse)
def generate(payload: GenerateRequest):
    result = por_control(
        output=payload.output,
        coherence=payload.coherence,
        drift=payload.drift,
        threshold=payload.threshold,
        tolerance=payload.tolerance,
    )
    log_decision(
        coherence=payload.coherence,
        drift=payload.drift,
        threshold=payload.threshold,
        tolerance=payload.tolerance,
        decision=result["status"],
    )
    return result
