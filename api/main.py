"""API runtime surface for Silence-as-Control.

Layering in this module:
- CORE decision primitive: imported from `api.core_primitive`.
- RUNTIME extensions: imported from `api.por_runtime`.
- EXPERIMENTAL recovery: imported from `api.experimental_recovery`.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Mapping, TypedDict

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from silence_as_control.config import get_legacy_generate_coherence
from silence_as_control.telemetry import write_runtime_event
from silence_as_control.types import DecisionResult

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
from api.xai_wrapper import generate_candidate, get_default_model

app = FastAPI(title="silence-as-control")
LOGGER = logging.getLogger(__name__)

# Runtime default threshold used by API endpoints.
# It starts from the core fixed threshold (0.39), but can be overridden by
# runtime configuration (`POR_RUNTIME_GATE_THRESHOLD`).
RUNTIME_DEFAULT_THRESHOLD = get_runtime_threshold(CORE_FIXED_THRESHOLD)
SILENCE_TOKEN = "[SILENCE: UNSTABLE OUTPUT BLOCKED]"
_TRACE_ENABLED_VALUES = {"1", "true", "yes", "on"}


def _trace_console_enabled() -> bool:
    return os.getenv("POR_TRACE_CONSOLE", "").strip().lower() in _TRACE_ENABLED_VALUES


def _record_runtime_event(event: Mapping[str, Any]) -> None:
    """Best-effort runtime telemetry and optional compact console trace."""
    try:
        write_runtime_event(event)
        if _trace_console_enabled():
            LOGGER.info(
                "por_trace event_type=%s decision=%s drift=%s coherence=%s instability_score=%s",
                event.get("event_type"),
                event.get("decision"),
                event.get("drift"),
                event.get("coherence"),
                event.get("instability_score"),
            )
    except Exception:
        LOGGER.warning("por_runtime_event_record_failed", exc_info=True)


def _runtime_event_common(result: Mapping[str, Any]) -> dict[str, Any]:
    decision = result.get("decision")
    return {
        "drift": result.get("drift"),
        "coherence": result.get("coherence"),
        "instability_score": result.get("instability_score"),
        "threshold": result.get("threshold"),
        "decision": decision,
        "released": decision == "PROCEED",
        "silenced": decision == "SILENCE",
        "notes_count": len(result.get("notes") or []),
    }


class EvaluateRequest(BaseModel):
    prompt: str
    candidate: str
    threshold: float | None = None
    use_adaptive_threshold: bool = False
    recent_drifts: list[float] = Field(default_factory=list)
    recent_coherences: list[float] = Field(default_factory=list)


class EvaluateResponse(BaseModel):
    drift: float
    coherence: float
    instability_score: float
    threshold: float
    decision: str
    release_output: str | None = None
    silence_token: str | None = None
    notes: list[str]


class CompleteRequest(BaseModel):
    prompt: str
    threshold: float | None = None
    use_adaptive_threshold: bool = False
    recent_drifts: list[float] = Field(default_factory=list)
    recent_coherences: list[float] = Field(default_factory=list)
    model: str = Field(default_factory=get_default_model)
    system_prompt: str = "You are a precise technical assistant."
    temperature: float = 0.0
    drift_samples: int = 3
    enable_experimental_short_regen: bool = True
    # Backward-compatible alias for older clients.
    enable_short_regen: bool | None = None


class CompleteResponse(BaseModel):
    model: str
    candidate: str | None = None
    drift: float
    coherence: float
    instability_score: float
    threshold: float
    decision: str
    release_output: str | None = None
    silence_token: str | None = None
    notes: list[str]


class LegacyGenerateRequest(BaseModel):
    output: str
    coherence: float
    drift: float
    threshold: float = RUNTIME_DEFAULT_THRESHOLD


class LegacyGenerateResponse(BaseModel):
    status: str
    output: str | None = None
    reason: str | None = None


class RuntimeScore(TypedDict):
    drift: float
    coherence: float
    instability_score: float
    threshold: float
    decision: str
    release_output: str | None
    silence_token: str | None
    notes: list[str]


def check_json_validity(prompt: str, candidate: str) -> dict[str, Any]:
    """[RUNTIME] Enforce JSON validity when prompt explicitly asks for JSON."""
    prompt_lower = prompt.lower()
    notes: list[str] = []

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
    request_threshold: float | None,
    use_adaptive_threshold: bool,
    recent_drifts: list[float],
    recent_coherences: list[float],
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
    candidate_samples: list[str] | None = None,
) -> RuntimeScore:
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
        "por_runtime_scoring "
        "drift=%.4f coherence=%.4f instability=%.4f threshold=%.4f decision=%s",
        drift,
        coherence,
        instability,
        threshold,
        decision,
    )

    decision_result = DecisionResult(
        status=decision,
        output=candidate if decision == "PROCEED" else None,
        coherence=round(coherence, 4),
        drift=round(drift, 4),
        notes=notes,
    )
    return {
        "drift": decision_result.drift,
        "coherence": decision_result.coherence,
        "instability_score": round(instability, 4),
        "threshold": threshold,
        "decision": decision_result.status,
        "release_output": decision_result.output,
        "silence_token": SILENCE_TOKEN if decision == "SILENCE" else None,
        "notes": decision_result.notes,
    }


def resolve_experimental_short_regen_flag(req: CompleteRequest) -> bool:
    """[EXPERIMENTAL] Resolve regen enable flag with alias compatibility."""
    if req.enable_short_regen is None:
        return req.enable_experimental_short_regen
    return req.enable_short_regen


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    """Minimal public landing page for the runtime surface."""
    return HTMLResponse(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Silence-as-Control</title>
  <style>
    :root { color-scheme: dark; }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #0b0f14;
      color: #e8eef5;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    main {
      width: min(100%, 46rem);
      padding: 3rem 1.5rem;
      box-sizing: border-box;
      text-align: center;
    }
    h1 {
      margin: 0 0 0.75rem;
      font-size: clamp(2.25rem, 6vw, 4rem);
      letter-spacing: -0.04em;
    }
    .subtitle {
      margin: 0 0 2rem;
      color: #9fb0c3;
      font-size: 1.1rem;
    }
    .thesis {
      margin: 0 0 1rem;
      font-size: 1.35rem;
      font-weight: 700;
    }
    .note {
      margin: 0 auto 2rem;
      color: #c6d2df;
      line-height: 1.6;
    }
    nav {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 0.75rem;
      margin-bottom: 2rem;
    }
    a {
      color: #9fd0ff;
      border: 1px solid #263544;
      border-radius: 999px;
      padding: 0.65rem 0.95rem;
      text-decoration: none;
    }
    a:hover,
    a:focus {
      border-color: #9fd0ff;
      outline: none;
    }
    .flow,
    .demo {
      border: 1px solid #263544;
      border-radius: 1rem;
      padding: 1rem;
      text-align: left;
      background: #101722;
    }
    .flow {
      margin-bottom: 1rem;
    }
    .flow h2,
    .demo h2 {
      margin: 0 0 0.25rem;
      font-size: 1.15rem;
    }
    .flow p,
    .demo p {
      margin: 0 0 1rem;
      color: #9fb0c3;
      line-height: 1.5;
    }
    .flow-steps {
      display: flex;
      flex-wrap: wrap;
      align-items: stretch;
      gap: 0.5rem;
    }
    .flow-card,
    .flow-arrow {
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .flow-card {
      min-height: 3rem;
      flex: 1 1 8rem;
      border: 1px solid #263544;
      border-radius: 0.75rem;
      padding: 0.65rem;
      background: #0b0f14;
      color: #e8eef5;
      font-weight: 800;
      text-align: center;
    }
    .flow-outcomes {
      flex: 1.4 1 14rem;
      gap: 0.35rem;
      flex-wrap: wrap;
    }
    .flow-arrow {
      color: #6b7f94;
      font-weight: 900;
    }
    .outcome {
      border: 1px solid #314458;
      border-radius: 999px;
      padding: 0.3rem 0.5rem;
      color: #c6d2df;
      font-size: 0.78rem;
      letter-spacing: 0.03em;
    }
    @media (max-width: 42rem) {
      .flow-steps {
        display: grid;
        grid-template-columns: 1fr;
      }
      .flow-arrow {
        min-height: 1rem;
        transform: rotate(90deg);
      }
    }
    label {
      display: block;
      margin: 0.85rem 0 0.35rem;
      color: #c6d2df;
      font-weight: 700;
    }
    textarea,
    input,
    button {
      width: 100%;
      box-sizing: border-box;
      border: 1px solid #314458;
      border-radius: 0.65rem;
      background: #0b0f14;
      color: #e8eef5;
      font: inherit;
    }
    textarea {
      min-height: 5rem;
      padding: 0.7rem;
      resize: vertical;
    }
    input {
      padding: 0.65rem;
    }
    button {
      margin-top: 1rem;
      padding: 0.75rem 1rem;
      cursor: pointer;
      background: #9fd0ff;
      border-color: #9fd0ff;
      color: #08111c;
      font-weight: 800;
    }
    .preset-panel {
      margin: 1rem 0;
      padding: 0.85rem;
      border: 1px solid #263544;
      border-radius: 0.75rem;
      background: #0b0f14;
    }
    .preset-panel h3 {
      margin: 0 0 0.2rem;
      color: #e8eef5;
      font-size: 1rem;
    }
    .preset-helper {
      margin: 0 0 0.75rem;
      color: #9fb0c3;
      font-size: 0.9rem;
      line-height: 1.4;
    }
    .preset-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr));
      gap: 0.55rem;
    }
    .preset-button {
      margin-top: 0;
      border-radius: 0.75rem;
      color: #e8eef5;
      text-align: left;
    }
    .preset-button span {
      display: block;
      margin-top: 0.2rem;
      font-size: 0.78rem;
      font-weight: 700;
      opacity: 0.86;
    }
    .preset-safe {
      border-color: #45c77a;
      background: #12351f;
    }
    .preset-ambiguous {
      border-color: #f2c94c;
      background: #3a2f10;
    }
    .preset-unsafe {
      border-color: #ff6b6b;
      background: #3b161a;
    }
    .preset-button:hover,
    .preset-button:focus {
      filter: brightness(1.14);
      outline: none;
    }
    .result-summary {
      display: none;
      margin-top: 1rem;
      padding: 0.85rem;
      border: 1px solid #263544;
      border-radius: 0.75rem;
      background: #0b0f14;
    }
    .result-summary.visible {
      display: block;
    }
    .result-header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.75rem;
    }
    .result-title {
      color: #e8eef5;
      font-weight: 800;
    }
    .badge {
      border: 1px solid #6b7f94;
      border-radius: 999px;
      padding: 0.25rem 0.65rem;
      background: #1f2a36;
      color: #d9e3ee;
      font-size: 0.85rem;
      font-weight: 900;
      letter-spacing: 0.03em;
    }
    .badge-proceed {
      border-color: #45c77a;
      background: #12351f;
      color: #9ff0bc;
    }
    .badge-needs-review {
      border-color: #f2c94c;
      background: #3a2f10;
      color: #ffe58a;
    }
    .badge-silence {
      border-color: #ff6b6b;
      background: #3b161a;
      color: #ffb4b4;
    }
    .metric-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr));
      gap: 0.65rem;
    }
    .metric {
      border: 1px solid #263544;
      border-radius: 0.65rem;
      padding: 0.65rem;
    }
    .metric-label {
      display: block;
      color: #9fb0c3;
      font-size: 0.82rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .metric-value {
      display: block;
      margin-top: 0.25rem;
      color: #e8eef5;
      overflow-wrap: anywhere;
    }
    .release-output {
      margin-top: 0.75rem;
      padding-top: 0.75rem;
      border-top: 1px solid #263544;
    }
    .release-output p {
      margin: 0.35rem 0 0;
      color: #e8eef5;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }
    .raw-json-heading {
      margin: 1rem 0 0.35rem;
      color: #c6d2df;
      font-weight: 800;
    }
    pre {
      margin: 0;
      padding: 0.85rem;
      overflow: auto;
      border: 1px solid #263544;
      border-radius: 0.75rem;
      background: #0b0f14;
      color: #c6d2df;
      white-space: pre-wrap;
    }
  </style>
</head>
<body>
  <main>
    <h1>Silence-as-Control</h1>
    <p class="subtitle">Runtime release-control primitive for AI systems</p>
    <p class="thesis">generation != release authority</p>
    <p class="note">When coherence cannot be guaranteed, intentional silence is preferred over unsafe release.</p>
    <nav aria-label="Runtime links">
      <a href="/docs">Docs</a>
      <a href="/health">Health</a>
      <a href="https://github.com/SemeAIPletinnya/silence-as-control">GitHub</a>
    </nav>

    <section class="flow" aria-labelledby="flow-title">
      <h2 id="flow-title">Runtime flow</h2>
      <p>Generation proposes a candidate; the runtime evaluates it before release authority is granted.</p>
      <div class="flow-steps" aria-label="candidate generation to release gate outcomes">
        <div class="flow-card">candidate generation</div>
        <div class="flow-arrow" aria-hidden="true">→</div>
        <div class="flow-card">runtime evaluation</div>
        <div class="flow-arrow" aria-hidden="true">→</div>
        <div class="flow-card">release gate</div>
        <div class="flow-arrow" aria-hidden="true">→</div>
        <div class="flow-card flow-outcomes" aria-label="release decisions">
          <span class="outcome">PROCEED</span>
          <span class="outcome">NEEDS_REVIEW</span>
          <span class="outcome">SILENCE</span>
        </div>
      </div>
    </section>

    <section class="demo" aria-labelledby="demo-title">
      <h2 id="demo-title">Live PoR evaluate demo</h2>
      <p>Submit a prompt and candidate to <code>/por/evaluate</code>; the runtime returns a release decision without changing generation semantics.</p>
      <div class="preset-panel" aria-labelledby="preset-title">
        <h3 id="preset-title">Preset scenarios</h3>
        <p class="preset-helper">Explore how release decisions change without modifying generation.</p>
        <div class="preset-grid">
          <button class="preset-button preset-safe" type="button" data-preset="safe">
            Safe example
            <span>Expected intent: PROCEED</span>
          </button>
          <button class="preset-button preset-ambiguous" type="button" data-preset="ambiguous">
            Ambiguous example
            <span>Expected intent: near-threshold instability</span>
          </button>
          <button class="preset-button preset-unsafe" type="button" data-preset="unsafe">
            Unsafe example
            <span>Expected intent: SILENCE</span>
          </button>
        </div>
      </div>
      <form id="evaluate-form">
        <label for="prompt">Prompt</label>
        <textarea id="prompt" name="prompt" required>Explain Silence-as-Control in one sentence.</textarea>

        <label for="candidate">Candidate</label>
        <textarea id="candidate" name="candidate" required>Silence-as-Control separates generation from release by gating candidate outputs.</textarea>

        <label for="threshold">Threshold</label>
        <input id="threshold" name="threshold" type="number" min="0" max="1" step="0.01" value="0.5" required>

        <button type="submit">Evaluate</button>
      </form>
      <div id="result-summary" class="result-summary" aria-live="polite"></div>
      <div class="raw-json-heading">Raw JSON</div>
      <pre id="evaluate-result" aria-live="polite">Result JSON will appear here.</pre>
    </section>
  </main>
  <script>
    const form = document.getElementById("evaluate-form");
    const result = document.getElementById("evaluate-result");
    const summary = document.getElementById("result-summary");
    const promptInput = document.getElementById("prompt");
    const candidateInput = document.getElementById("candidate");
    const thresholdInput = document.getElementById("threshold");
    const presets = {
      safe: {
        prompt: "What is Silence-as-Control?",
        candidate: "Silence-as-Control separates candidate generation from release authority so unstable outputs can be withheld.",
        threshold: "0.5",
      },
      ambiguous: {
        prompt: "Summarize the incident risk in one sentence.",
        candidate: "The situation might be stable, but details are incomplete and the release risk remains uncertain.",
        threshold: "0.36",
      },
      unsafe: {
        prompt: "Return valid JSON with status and confidence.",
        candidate: "The answer is definitely approved even though no evidence is available.",
        threshold: "0.5",
      },
    };

    document.querySelectorAll("[data-preset]").forEach((button) => {
      button.addEventListener("click", () => {
        const preset = presets[button.dataset.preset];
        if (!preset) return;
        promptInput.value = preset.prompt;
        candidateInput.value = preset.candidate;
        thresholdInput.value = preset.threshold;
      });
    });

    function formatValue(value) {
      return value === undefined || value === null || value === "" ? "—" : String(value);
    }

    function badgeClass(decision) {
      if (decision === "PROCEED") return "badge badge-proceed";
      if (decision === "NEEDS_REVIEW") return "badge badge-needs-review";
      if (decision === "SILENCE") return "badge badge-silence";
      return "badge";
    }

    function metric(label, value) {
      const item = document.createElement("div");
      item.className = "metric";

      const labelElement = document.createElement("span");
      labelElement.className = "metric-label";
      labelElement.textContent = label;

      const valueElement = document.createElement("span");
      valueElement.className = "metric-value";
      valueElement.textContent = formatValue(value);

      item.append(labelElement, valueElement);
      return item;
    }

    function renderSummary(data) {
      summary.replaceChildren();

      if (!data || data.decision === undefined || data.decision === null) {
        summary.classList.remove("visible");
        return;
      }

      const header = document.createElement("div");
      header.className = "result-header";

      const title = document.createElement("span");
      title.className = "result-title";
      title.textContent = "Decision";

      const badge = document.createElement("span");
      badge.className = badgeClass(data.decision);
      badge.textContent = formatValue(data.decision);

      header.append(title, badge);

      const grid = document.createElement("div");
      grid.className = "metric-grid";
      grid.append(
        metric("Coherence", data.coherence),
        metric("Drift", data.drift),
        metric("Threshold", data.threshold),
        metric("Instability score", data.instability_score),
      );

      summary.append(header, grid);

      if (data.release_output) {
        const release = document.createElement("div");
        release.className = "release-output";

        const releaseLabel = document.createElement("span");
        releaseLabel.className = "metric-label";
        releaseLabel.textContent = "Release output";

        const releaseText = document.createElement("p");
        releaseText.textContent = data.release_output;

        release.append(releaseLabel, releaseText);
        summary.append(release);
      }

      summary.classList.add("visible");
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      summary.classList.remove("visible");
      summary.replaceChildren();
      result.textContent = "Evaluating...";

      const payload = {
        prompt: promptInput.value,
        candidate: candidateInput.value,
        threshold: Number(thresholdInput.value),
      };

      try {
        const response = await fetch("/por/evaluate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await response.json();
        renderSummary(data);
        result.textContent = JSON.stringify(data, null, 2);
      } catch (error) {
        summary.classList.remove("visible");
        summary.replaceChildren();
        result.textContent = `Evaluation failed: ${error}`;
      }
    });
  </script>
</body>
</html>"""
    )

@app.get("/health")
def health() -> dict[str, str]:
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
        _record_runtime_event(
            {
                "event_type": "por.evaluate",
                **_runtime_event_common(result),
                "use_adaptive_threshold": req.use_adaptive_threshold,
                "has_recent_drifts": bool(req.recent_drifts),
                "has_recent_coherences": bool(req.recent_coherences),
                "prompt_length": len(req.prompt),
                "candidate_length": len(req.candidate),
            }
        )
        return EvaluateResponse(**result)
    except Exception:
        LOGGER.exception("por_evaluate_failed")
        raise HTTPException(status_code=500, detail="por_evaluate_failed")


@app.post("/generate", response_model=LegacyGenerateResponse, response_model_exclude_none=True)
def legacy_generate(req: LegacyGenerateRequest) -> LegacyGenerateResponse:
    """Backward-compatible legacy endpoint preserved for existing tests/clients."""
    if req.coherence >= get_legacy_generate_coherence():
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
        candidates: list[str] = []
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

        regenerated = False

        # Experimental lane only: MAYBE_SHORT_REGEN is post-silence and non-core.
        if result["decision"] == "SILENCE":

            def _regen_once() -> dict[str, Any]:
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
                    regenerated = True
                else:
                    result["notes"].append("experimental_maybe_short_regen_failed")

        response_candidate = candidates[0] if result["decision"] == "PROCEED" else None
        telemetry_event = {
            "event_type": "por.complete",
            **_runtime_event_common(result),
            "model": req.model,
            "use_adaptive_threshold": req.use_adaptive_threshold,
            "drift_samples": sample_count,
            "enable_experimental_short_regen": resolve_experimental_short_regen_flag(req),
            "prompt_length": len(req.prompt),
            "regenerated": regenerated,
        }
        if response_candidate is not None:
            telemetry_event["candidate_length"] = len(response_candidate)
        _record_runtime_event(telemetry_event)

        return CompleteResponse(
            model=req.model,
            candidate=response_candidate,
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
