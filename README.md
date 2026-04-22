# Silence-as-Control

**Silence-as-Control is a release-control layer for LLM reliability.**
It separates **generation** from **release**: a model can generate a candidate, but the PoR gate decides whether that candidate is safe enough to release.

It does **not** improve model weights. It controls release behavior.

**Either correct, or silent.**

**Same model. Different decision.**

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
- `I <= τ` -> `PROCEED`
- `I > τ` -> `SILENCE`

## Architecture split
### 1) Core Primitive (thesis-level)
Deterministic fixed-threshold release control.

Code: `api/core_primitive.py`, `src/silence_as_control/control.py`.

### 2) Runtime Extensions (optional deployment layer)
Adaptive thresholds, environment configuration, embedding-based scoring, multi-sample drift.

Code: `api/por_runtime.py`.

### 3) Experimental Features (optional, non-core)
MAYBE_SHORT_REGEN: post-silence boundary-pocket retry.

Code: `api/experimental_recovery.py` + `/por/complete` integration.

## Minimal system diagram
```text
Request
  -> Candidate Output(s)
  -> PoR Gate (instability vs threshold)
  -> PROCEED or SILENCE
  -> optional MAYBE_SHORT_REGEN (experimental, post-silence only)
```

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

## Evidence
- Run artifacts: `reports/`, `wiki/runs/`, `wiki/meta/Evidence_Map.md`
- Boundary-pocket artifacts: `reports/borderline_pocket_labels.csv`, `reports/borderline_maybe_short_regen.csv`
- Tracked run scales: 35 / 100 / 300 / 1000 tasks
- Additional visuals and summaries: `reports/README.md`, `docs/`

## Quick public links
- Repository root: `./`
- README: `README.md`
- Docs index: `docs/README.md`
- Paper/preprint materials: `paper/README.md`
- Reports/evidence: `reports/README.md`

## Positioning
- **Paper-core claim**: deterministic fixed-threshold PoR release control.
- **Runtime extensions**: practical deployment helpers, optional.
- **Experimental features**: MAYBE_SHORT_REGEN, optional and non-core.
