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
  - Applied examples exist and the runtime/API path is repository-visible, but most proof remains local/repo-scoped.
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
  - `reports/accepted_failures_comparison.png`
  - `reports/drift_separation_comparison.png`
- **Partial evidence**
  - Regime naming (conservative / safe anchor / transitional / boundary) is repository-scoped interpretation, not universal calibration.
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
  - Drift and metrics plots in `reports/`, including:
    - `reports/metrics.png`
    - `reports/drift.png`
    - `reports/drift_clean.png`
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
  - Artifact fields such as `no_control_success`, `with_control_success`, `silence`
- **Partial evidence**
  - Current comparison is strongest inside tracked datasets and runs.
- **Future evidence needed**
  - Additional out-of-distribution and integration-level comparisons.
- **Does not establish**
  - That PoR dominates baseline on every objective; the evidence is policy- and dataset-scoped.

## Applied API / Runtime Evidence

### Claim

A structured applied API/runtime path exists in the repository.

- **Established evidence**
  - `docs/api_walkthrough.md`
  - `wiki/API-Walkthrough.md`
  - `api/main.py` endpoints (`/health`, `/por/evaluate`, `/generate`, `/por/complete`)
  - `demo/por_api_demo.py`
- **Partial evidence**
  - Path is clear for local application but not yet a complete external integration proof.
- **Future evidence needed**
  - End-to-end external integration demo with audited runtime outcomes.
- **Does not establish**
  - Production-hardening completeness (SLOs, incident behavior, governance controls).

## Visual Evidence Surface

### Claim

Tracked plots improve proof readability and help connect summaries to repository artifacts.

- **Established evidence**
  - `reports/threshold_control_curve.png`
  - `reports/accepted_failures_comparison.png`
  - `reports/drift_separation_comparison.png`
  - `reports/metrics.png`
  - `reports/drift.png`
  - `reports/drift_clean.png`
- **Partial evidence**
  - Visual summaries make interpretation easier, but the strongest proof still lives in raw run artifacts and run summaries.
- **Future evidence needed**
  - More benchmark-specific visualizations and integration-level runtime traces.
- **Does not establish**
  - Claims beyond the underlying recorded artifacts.

## Open Proof Gaps

- External integration proof remains pending.
- Public compact narrative should continue tightening around claim boundaries.
- Additional applied use-cases would improve transfer confidence.
- Production-hardening should not be inferred from repository clarity alone.

## Reader checklist

Use this page to answer:

1. What is already demonstrated?
2. Where does the proof live?
3. What is partially established versus fully established?
4. What is still pending before stronger external claims are justified?
