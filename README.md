# Silence-as-Control

Silence-as-Control is a runtime control-layer primitive for LLM systems that gates output release using stability signals.

**Either correct, or silent.**

PoR does not improve the model itself. It controls when the model is allowed to produce output.

**Same model. Different decision.**

## Core idea

- Unstable output -> **silence**
- Stable output -> **proceed**
- Silence is **not** failure; it is an explicit control signal

This repository implements Proof-of-Resonance (PoR) as a release gate between model generation and user-visible output.

## API surface

Current endpoints:

- `GET /health`
- `POST /por/evaluate`
- `POST /generate`
- `POST /por/complete`

## Quickstart (Windows / PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
uvicorn api.main:app --reload
```

Optional test run:

```powershell
pytest -q
```

## Demo entry points

Run this first:

python demo/canonical_demo.py

No API key required. Shows the baseline vs PoR contrast in one local run.

```powershell
python demo/por_api_demo.py
python demo/por_agent_demo.py
```

## Evaluation highlights

Selected tracked operating points:

- **Run #4 — 300 tasks (threshold 0.35):** robust safe behavior at medium scale.
- **Run #5 — 1000 tasks (threshold 0.35):** scaled conservative safe regime.
- **Run #5 — 1000 tasks (threshold 0.43):** aggressive boundary setting where leakage risk increases.
- **Run #6 — 1000 tasks (threshold 0.39):** current safe operating point (recommended).

Interpretation: threshold is a control dial; lower values are more conservative, while higher values increase release aggressiveness.

## Visual proof

Existing report visuals:

![PoR threshold control curve](reports/threshold_control_curve.png)
![Accepted failures comparison](reports/accepted_failures_comparison.png)
![Drift separation comparison](reports/drift_separation_comparison.png)
![Run metrics](reports/metrics.png)

Additional tracked plots:

- `reports/drift.png`
- `reports/drift_clean.png`

## Reports and tracked artifacts

Tracked JSONL artifacts in `reports/`:

- `reports/eval_35_tasks.jsonl`
- `reports/eval_100_tasks.jsonl`
- `reports/eval_run2_100_tasks.jsonl`
- `reports/eval_run3.jsonl`
- `reports/eval_run4_300_threshold_035.jsonl`
- `reports/eval_run5_1000_threshold_035.jsonl`
- `reports/eval_run5_1000_threshold_042.jsonl`
- `reports/eval_run5_1000_threshold_043.jsonl`
- `reports/eval_run6_1000_threshold_039.jsonl`

---

Silence-as-Control keeps architecture and model weights unchanged; it enforces runtime release decisions under stability constraints.
