# Silence-as-Control

**Silence-as-Control is a release-control layer for LLM reliability.**
It separates **generation** from **release**: a model can generate a candidate, but the PoR gate decides whether that candidate is safe enough to release.

It does **not** improve model weights. It controls release behavior.

**Either correct, or silent.**

**Same model. Different decision.**


## Installation and dependency setup

### From a fresh checkout
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

### API key guidance
- The deterministic core and local tests do not require an OpenAI API key.
- OpenAI-backed demos or live benchmark scripts should read credentials from
  environment variables such as `OPENAI_API_KEY`.
- Do not commit API keys, prompt logs containing secrets, or provider tokens.

## Minimal wrapping example
```python
from silence_as_control import por_control

candidate = "A candidate answer generated upstream"
result = por_control(candidate, coherence=0.82, drift=0.15)

if result["status"] == "ok":
    release_to_user = result["output"]
else:
    release_to_user = None  # silence / abstain
```

## Use / Integration
PoR is useful as:
- a release gate before final LLM output,
- abstention/silence control when output is unstable,
- a reliability layer in agent or API pipelines.

Most relevant for:
- LLM app builders,
- agent developers,
- API/inference layer engineers,
- teams that care more about avoiding accepted wrong outputs than maximizing raw coverage.

**Offer**

I help teams integrate release-control/abstention gating into LLM pipelines, evaluate accepted-wrong-output and threshold behavior, and set up benchmark/audit flows for model release control.

Open a GitHub issue if you want integration help, audit/evaluation support, or benchmark setup.

## What this repo is
- A research-engineering implementation of Proof-of-Resonance (PoR) release control.
- A deterministic core primitive with explicit `PROCEED` / `SILENCE` outcomes.
- A clear separation between core, runtime extensions, and experimental recovery.

## What this repo is not
- Not a new base model.
- Not a training recipe.
- Not a claim of guaranteed truth.
- Not a framework rewrite of inference stacks.

## Core primitive in 30 seconds
PoR uses:
- drift,
- coherence,
- instability score: `I = (drift + (1 - coherence)) / 2`.

Core fixed-threshold release rule:
- `I <= П„` -> `PROCEED`
- `I > П„` -> `SILENCE`

## Architecture split
### 1) Core Primitive (thesis-level)
Deterministic fixed-threshold release control.

Code: `api/core_primitive.py`, `src/silence_as_control/control.py`.

### 2) Runtime Extensions (optional deployment layer)
Adaptive thresholds, environment configuration, embedding-based scoring, multi-sample drift.

Runtime fallback embeddings are lightweight and deterministic (for offline/demo reproducibility), not a claim of state-of-the-art semantics. Production systems can inject stronger embedding backends while keeping the same gate logic.

Code: `api/por_runtime.py`.

### 3) Experimental Features (optional, non-core)
MAYBE_SHORT_REGEN: post-silence boundary-pocket retry.

Code: `api/experimental_recovery.py` + `/por/complete` integration.

## Architecture flow diagram
```text
prompt
  -> candidate generation
  -> PoR gate
       -> PROCEED
       -> NEEDS_REVIEW (where an integration defines a review lane)
       -> SILENCE
```

Generation is not release. The PoR gate is a release-control gate, not a
generation-improvement method. Guardrails may classify or constrain inputs and
outputs; Silence-as-Control gates whether a candidate is released.

## Threshold regimes

Threshold defaults are **not universal**. The core/runtime default of `0.39`,
historical sweep values such as `0.35`, `0.42`, and `0.43`, and benchmark-specific
settings are meaningful only within their signal regime, model/task mix, and
evidence protocol. Calibrate thresholds before using them with a new model, a new
task family, or a new signal source.

The deterministic core rule remains:
- `I <= П„` -> `PROCEED`
- `I > П„` -> `SILENCE`

Some integrations may layer a separate `NEEDS_REVIEW` lane. Do not collapse an
existing tri-state integration into binary behavior unless that integration
explicitly chooses to do so.

## Start here
1. This README (`README.md`)
2. Canonical demo: `python demo/canonical_demo.py`
3. Architecture split: `docs/architecture.md`
4. Runtime extensions: `docs/runtime_extensions.md`
5. Experimental features: `docs/experimental_features.md`
6. Paper/preprint materials: `paper/README.md`, `paper/main.tex`

## Quick API examples
Start API:
```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

`/por/evaluate`:
```bash
curl -s http://127.0.0.1:8000/por/evaluate \
  -H 'content-type: application/json' \
  -d '{"prompt":"Return valid JSON","candidate":"{\"ok\": true}","threshold":0.39}'
```

`/por/complete` (experimental regen optional):
```bash
curl -s http://127.0.0.1:8000/por/complete \
  -H 'content-type: application/json' \
  -d '{"prompt":"Explain recursion in one sentence","threshold":0.39,"drift_samples":3,"enable_experimental_short_regen":true}'
```



## Run 06 action-risk evidence (LangChain/OpenAI)

Run 06 is a 1000-case **synthetic integration/deployment validation** benchmark for the action-risk release-control lane, not a universal AI safety claim. The progression through hardened v4 used the same model (`gpt-4.1-mini`), same dataset (`data/action_risk/action_risk_1000.jsonl`), same threshold, and no PoR core change; telemetry-driven release-layer hardening changed the review/release profile.

| Stage | NEEDS_REVIEW | False accepts | Estimated cost saved |
| --- | ---: | ---: | ---: |
| Initial | 146 | 664 | 8,518 (~17.7%) |
| Hardened v1 | 310 | 505 | 18,227 (~38.0%) |
| Hardened v2 | 424 | 397 | 23,210 (~48.35%) |
| Hardened v3 | 458 | 368 | 25,677 (~53.49%) |
| Hardened v4 | 578 | 247 | 33,174 (~69.11%) |

See `docs/langchain_openai_action_risk_benchmark.md` for the full progression table, v4 class breakdown, artifact links, and interpretation notes.

## Recent local Ollama evidence
- PR #131 (Qwen3 4B, SimpleQA/Ollama, 100 examples, PoR v2): at 0.43, 84% coverage with 0 accepted wrong (100% accepted precision) in this run.
- PR #132 (Qwen3 8B, SimpleQA/Ollama, 100 examples, PoR v2): at 0.42/0.43, 93% coverage with 1 accepted wrong (98.92% accepted precision) in this run.
- In this evidence slice, Qwen3 4B @ 0.43 acts as a practical zero-accepted-failure anchor, while Qwen3 8B @ 0.42/0.43 is a high-coverage boundary.
- This supports the repository thesis: stronger generation does not automatically mean safer release behavior at a fixed threshold.
- See `docs/threshold_regime_contract.md` and `docs/evidence_map.md` for scoped interpretation and artifact navigation.

## Evidence
- Run artifacts: `reports/`, `wiki/runs/`, `wiki/meta/Evidence_Map.md`
- Boundary-pocket artifacts: `reports/borderline_pocket_labels.csv`, `reports/borderline_maybe_short_regen.csv`
- Tracked run scales: 35 / 100 / 300 / 1000 tasks
- Additional visuals and summaries: `reports/README.md`, `docs/`

### Baseline-vs-PoR demo note
- `demo/baseline_vs_por.py` is local demo evidence.
- Scope is v0.2 negative-control only.
- It is not a replacement for benchmark artifacts.
- It is useful to demonstrate release control:
  - baseline: generate -> release
  - PoR: generate -> evaluate -> PROCEED/SILENCE

### SimpleQA-style benchmark note (prototype, PoR v2.2)
- Local harder subset: 25 examples (`gpt-4o-mini`).
- Baseline correctness in that run: 96% (24/25).
- PoR v2.2 accepted-output precision in that run: 100% (24/24 accepted), with `accepted_error_rate=0.0`.
- Silence tradeoff: 4% (1/25), including one observed wrong answer case blocked by silencing.
- This is a prototype benchmark observation on a local subset; broader validation on larger/harder sets is still required.

## Pilot / integration interest

Silence-as-Control may be relevant for teams building LLM agents, RAG/internal copilots, config/code assistants, or workflow automation where generated output can become an action.

Core question:

> Should this output be released at all?

For pilot or integration interest, see `docs/release_control_services.md`.

## Quick public links
- Repository root: `./`
- README: `README.md`
- Docs index: `docs/README.md`
- External CLI integration: `docs/external_integration.md`
- Package migration plan: `docs/package_migration_plan.md`
- Changelog: `CHANGELOG.md`
- Paper/preprint materials: `paper/README.md`
- Reports/evidence: `reports/README.md`

## Positioning
- **Paper-core claim**: deterministic fixed-threshold PoR release control.
- **Runtime extensions**: practical deployment helpers, optional deployment scaffolding.
- **Experimental features**: MAYBE_SHORT_REGEN, optional and non-core.

## Contributing

Contributions should preserve the architecture split: primitive core, runtime
behavior, evidence/evaluation surface, demos, documentation/wiki, and
extension-layer experiments. Keep changes scoped and reversible, avoid modifying
historical benchmark artifacts, and document any threshold-regime changes with
evidence.

Before opening a PR, run the focused tests relevant to your change and include
any environment limitations or skipped checks.
