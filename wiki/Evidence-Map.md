# Evidence Map

Purpose: claim-to-evidence index for what is established, partially established, and pending.

## Core Thesis Evidence

### Claim
PoR / Silence-as-Control is a runtime **release-control layer**, not a generation method.

- **Established evidence**
  - `README.md`
  - `wiki/concepts/PoR.md`
  - `wiki/architecture/Release_Control_Layer.md`
- **Partial evidence**
  - Applied examples exist but are still local/demo-oriented.
- **Future evidence needed**
  - External integration case showing the same release-control framing under real constraints.
- **Does not establish**
  - That PoR improves underlying model capability or truthfulness by itself.

## Threshold Evidence

### Claim
Threshold behaves as an operational dial with identifiable regimes.

- **Established evidence**
  - `reports/eval_run5_1000_threshold_035.jsonl`
  - `reports/eval_run6_1000_threshold_039.jsonl`
  - `reports/eval_run5_1000_threshold_042.jsonl`
  - `reports/eval_run5_1000_threshold_043.jsonl`
  - `reports/threshold_control_curve.png`
- **Partial evidence**
  - Regime naming (safe/transition/boundary) is repository-scoped interpretation, not universal calibration.
- **Future evidence needed**
  - Cross-domain threshold transfer or recalibration studies.
- **Does not establish**
  - A globally optimal threshold that transfers unchanged across domains.

## Evaluation Evidence

### Claim
Repeated runs support non-trivial gating behavior and safety/coverage tradeoffs.

- **Established evidence**
  - Run artifacts in `reports/eval_*.jsonl`
  - Run summaries in `wiki/runs/Run_1.md`, `wiki/runs/Run_4_300_tasks.md`, `wiki/runs/Run_6_1000_tasks.md`
  - Drift/metrics plots in `reports/`
- **Partial evidence**
  - Some run summaries are stronger than others; not every run has identical depth of decomposition.
- **Future evidence needed**
  - Broader benchmark sets and more detailed error-taxonomy analysis.
- **Does not establish**
  - Universal robustness outside the recorded datasets and metric definitions.

## Baseline vs PoR Evidence

### Claim
Baseline and PoR differ materially at the release-policy layer.

- **Established evidence**
  - `wiki/comparisons/Baseline_vs_PoR.md`
  - `docs/baseline_vs_por_quick_guide.md`
  - Artifact fields: `no_control_success`, `with_control_success`, `silence`
- **Partial evidence**
  - Current comparison is strongest inside tracked datasets/runs.
- **Future evidence needed**
  - Additional out-of-distribution and integration-level comparisons.
- **Does not establish**
  - That PoR dominates baseline on every objective; the evidence is policy- and dataset-scoped.

## Applied API / Runtime Evidence

### Claim
A clearer applied API/runtime path now exists.

- **Established evidence**
  - `docs/api_walkthrough.md`
  - `api/main.py` endpoints (`/health`, `/por/evaluate`, `/generate`, `/por/complete`)
  - `demo/por_api_demo.py`, `demo_outputs_api/`
- **Partial evidence**
  - Path is clear for local application but not yet a complete external integration proof.
- **Future evidence needed**
  - End-to-end external integration demo with audited runtime outcomes.
- **Does not establish**
  - Production-hardening completeness (SLOs, incident behavior, governance controls).

## Open Proof Gaps

- External integration proof remains pending.
- Public compact narrative should be tightened around claim boundaries.
- Additional applied use-cases would improve transfer confidence.

## Reader checklist

Use this page to answer:
1. What is already demonstrated?
2. Where does the proof live?
3. What is still pending before stronger external claims are justified?
