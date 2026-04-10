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
