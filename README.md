# Silence-as-Control

Silence-as-Control is a runtime control-layer middleware that decides whether to return or suppress model output based on explicit stability signals such as drift and coherence.

**Either correct, or silent.**

## What it is

Silence-as-Control is a **control-layer primitive** and **runtime gating mechanism** that sits between model generation and output release. It evaluates stability signals and returns either:
- `status: ok` (release), or
- `status: abstained` (suppress release).

It is an **abstention-based release control layer**.

## What it is not

- Not a model-training method.
- Not a replacement for core model architecture.
- Not a claim of model improvement.
- Not a new product feature layer.

## Core idea

- unstable state -> abstain
- stable state -> proceed

Silence is a control signal, not a failure.

## Why abstention matters

When runtime stability is weak, releasing output can amplify error impact. Abstention prevents unstable outputs from being emitted and turns uncertainty into an explicit, auditable control decision.

## Repository structure

```text
silence-as-control/
├── src/silence_as_control/      # core control layer (unchanged by docs work)
├── api/                         # API wrapper and integration entrypoints
├── tests/                       # behavior checks for control/API surfaces
├── reports/                     # evaluation artifacts and plots
├── demo_outputs*/               # demo run outputs
├── .github/workflows/           # CI and automation workflows
└── README.md
```

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
uvicorn api.main:app --reload
```

Run tests:

```bash
pytest -q
```

## API example

Request:

```json
{"output":"text","coherence":0.82,"drift":0.15}
```

Stable response:

```json
{"status":"ok","output":"text"}
```

Abstained response:

```json
{"status":"abstained","reason":"control_abstention"}
```

## Evaluation summary

Main reported runs and thresholds are summarized below.

| Run | Tasks | Threshold | Coverage | Accepted Precision | Risk Capture | Notes |
|---|---:|---:|---:|---:|---:|---|
| Run #1 | 35 | n/a | 85.7% | 100% | 100% | Initial mixed-task check |
| Run #2 | 100 | n/a | 73.0% | 100% | 100% | Conservative behavior |
| Run #3 | 100 | n/a | 76.0% | 100% | 100% | Repeatability confirmation |
| Run #4 | 300 | 0.35 | 64.0% | 100% | 100% | Strong robustness result |
| Run #5 | 1000 | 0.35 | 53.5% | 100% | 100% | Scaled safe regime |
| Run #6 | 1000 | 0.43 | 55.0% | 98.36% | 98.01% | Boundary/unsafe leakage appears |
| Run #7 | 1000 | 0.39 | 54.4% | 100.0% | 100.0% | Optimal safe balance |

Additional reported drift separations (success vs fail):
- Run #1: `0.218` vs `0.566` (~2.60x)
- Run #2: `0.245` vs `0.540` (~2.20x)
- Run #3: `0.242` vs `0.571` (~2.36x)
- Run #4: `0.254` vs `0.716` (~2.82x)
- Run #5: `0.253` vs `0.676` (~2.67x)
- Run #6: `0.249` vs `0.670` (~2.70x)
- Run #7: `0.247` vs `0.671` (~2.71x)

## Threshold map

- 0.35 = safe
- 0.39 = optimal
- 0.43 = boundary

## Key insight

PoR does not improve the model itself. It controls when the model is allowed to release output.

## Visual proof

Existing report visuals:
- Control curve: `reports/threshold_control_curve.png`
- Accepted failures comparison: `reports/accepted_failures_comparison.png`
- Drift separation comparison: `reports/drift_separation_comparison.png`
- Additional plots: `reports/metrics.png`, `reports/drift.png`, `reports/drift_clean.png`

## Conclusion

Silence-as-Control demonstrates a release-control framing for LLM systems: **either correct, or silent**. The objective is controlled output release under stability constraints, not model improvement.
