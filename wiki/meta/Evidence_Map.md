# Evidence Map — Detailed Audit Appendix

Primary reader-facing evidence map:
- [../Evidence-Map.md](../Evidence-Map.md)

This appendix preserves deeper repository-scoped audit discipline for stricter technical review.

## 1) Purpose

Use this page as a compact technical appendix:
- to map runs to committed artifacts,
- to clarify field-level interpretation,
- to define support-strength categories,
- and to state explicit evidence boundaries.

## 2) Run-to-artifact mapping

Core mapped runs:
- Run 1 -> `reports/eval_35_tasks.jsonl`
- Run 4 -> `reports/eval_run4_300_threshold_035.jsonl`
- Run 6 -> `reports/eval_run6_1000_threshold_039.jsonl`

Additional 1000-task threshold mapping artifacts:
- `reports/eval_run5_1000_threshold_035.jsonl`
- `reports/eval_run5_1000_threshold_042.jsonl`
- `reports/eval_run5_1000_threshold_043.jsonl`

## 3) Field-level notes

Committed artifacts and run docs commonly rely on these fields:
- `silence`: release was withheld by the gate.
- `raw_success`: outcome label before release-control filtering.
- `with_control_success`: success in the gated path.
- `no_control_success`: success in the ungated comparison path.
- `silence_threshold`: threshold used for silence gating.
- `raw_success_threshold`: threshold used in raw-success labeling.

Interpretation rule:
- aggregate from committed row-level fields first, then state summary metrics.

## 4) Evidence strength / support discipline

- **text-direct**: claim is explicitly stated in docs/wiki text.
- **code-direct**: claim is directly represented in committed implementation.
- **artifact-direct**: claim is directly observable in committed artifacts/fields.
- **mixed-direct**: claim depends on a direct combination of docs + artifacts/code.
- **partial**: directionally supported but missing needed decomposition for stronger inference.

## 5) Known evidence boundaries

- No universal generalization beyond documented runs/artifacts.
- No claim of globally optimal threshold across all domains.
- No claim of complete deployment proof or production hardening.
- No claim that PoR guarantees truth.
- Release-policy improvement does not imply universal capability improvement.

## 6) Maintenance rule

When updating this appendix:
1. Add only claims already present in repository docs/wiki.
2. Map each claim to concrete files/artifacts.
3. State what each claim does **not** establish.
4. Mark support as established vs partial.
5. Do not fill evidence gaps with inference.

## 7) Recent workstream evidence additions (PRs #93-#98)

Use these mappings for current status claims and milestone traceability.

### A) Workstream definition evidence
- Artifact: `docs/silence_rate_roadmap.md`
- Supports: silence-rate optimization is a defined, separate workstream with scoped goals.
- Support class: **text-direct**
- Does **not** establish: solved silence behavior or production validation.

### B) Structured exploratory evidence (borderline pocket)
- Artifact: `docs/borderline_pocket_findings.md`
- Supports: borderline pocket has been analyzed and summarized for practical lane selection.
- Support class: **text-direct** (with artifact references inside the doc)
- Does **not** establish: full silence-band recoverability.

### C) Extension-layer direction evidence
- Artifact: `docs/first_extension_experiment.md`
- Supports: first extension experiment is specified as a conservative next step.
- Support class: **text-direct**
- Does **not** establish: end-to-end runtime gain in external deployment conditions.

### D) Sandbox-level execution signal
- Artifact: `scripts/short_regen_sandbox.py`
- Supports: a committed runner exists for short-regeneration sandbox execution.
- Support class: **code-direct**
- Does **not** establish: broad runtime integration validity by itself.

### E) Sandbox findings evidence
- Artifact: `docs/short_regen_sandbox_findings.md`
- Supports: first sandbox run findings are documented and bounded.
- Support class: **mixed-direct** (documented interpretation of committed sandbox artifacts)
- Does **not** establish: complete production readiness or universal threshold conclusions.
