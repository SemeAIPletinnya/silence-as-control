# Evidence Map

_Back to [index](../index.md)_

Purpose: provide an audit surface that connects wiki claims to committed repository evidence.

## Core claims and support status

| Claim (as stated in wiki/docs) | Supporting files | Support type (taxonomy) | What this does **not** establish |
|---|---|---|---|
| PoR is a **release control layer**, not a generation method. | `wiki/concepts/PoR.md`, `wiki/architecture/Release_Control_Layer.md`, `README.md` | **Text-direct** (explicit text statement) | Does not establish model-quality improvement by itself. |
| Current gate behavior is operationally **proceed/release vs silence**. | `wiki/architecture/PoR_Gate.md`, `wiki/concepts/Silence_as_Control.md`, `api/main.py` (`por_decision`, `evaluate_candidate`) | **Code-direct** (implemented decision path) | Does not establish additional active states (e.g., hold) in current implementation. |
| Silence is treated as a control outcome (not automatically failure). | `wiki/concepts/Silence_as_Control.md`, `README.md` core idea section, run pages with non-zero `silence` counts | **Mixed-direct** (definition + observed artifact fields) | Does not prove silence is optimal in all contexts. |
| Baseline-vs-gated comparison is available via artifact outcome fields. | `wiki/comparisons/Baseline_vs_PoR.md`, run pages, JSONL fields `no_control_success` and `with_control_success` | **Artifact-direct** (comparison fields present in JSONL) | Does not prove universal causal superiority outside recorded runs. |
| Run pages summarize committed evidence for Run 1 / Run 4 / Run 6. | `wiki/runs/Run_1.md`, `wiki/runs/Run_4_300_tasks.md`, `wiki/runs/Run_6_1000_tasks.md`, corresponding JSONL files | **Artifact-direct** (explicit run-file mapping) | Does not cover all runs or provide full per-class evaluation where absent. |

## Run-to-artifact mapping

- **Run 1** -> `reports/eval_35_tasks.jsonl`.
- **Run 4 (300 tasks)** -> `reports/eval_run4_300_threshold_035.jsonl`.
- **Run 6 (1000 tasks)** -> `reports/eval_run6_1000_threshold_039.jsonl`.

Repository cross-reference:

- `README.md` lists these artifacts in “Reports and tracked artifacts”.
- `README.md` names Run #4 (threshold 0.35) and Run #6 (threshold 0.39) in “Evaluation highlights”.

## Field-level notes (JSONL)

The run pages rely on these committed per-record fields:

- `silence`: whether output was silenced.
- `raw_success`: task judged successful before release-control filtering.
- `with_control_success`: success under the control/evaluated path.
- `no_control_success`: success under the no-control comparison path.
- `silence_threshold`: threshold value used for silence gating.
- `raw_success_threshold`: threshold used in raw-success labeling.

Interpretation discipline used in wiki run pages:

- Rates/counts are aggregates of committed row-level fields.
- “Accepted failures under control” is computed as rows with `silence=false` and `raw_success=false`.

## Supporting artifacts index

Primary documentation:

- `README.md`
- `wiki/index.md`
- `wiki/SCHEMA.md`
- `wiki/concepts/PoR.md`
- `wiki/concepts/Silence_as_Control.md`
- `wiki/architecture/PoR_Gate.md`
- `wiki/architecture/Release_Control_Layer.md`
- `wiki/comparisons/Baseline_vs_PoR.md`
- `wiki/runs/Run_1.md`
- `wiki/runs/Run_4_300_tasks.md`
- `wiki/runs/Run_6_1000_tasks.md`

Primary run artifacts:

- `reports/eval_35_tasks.jsonl`
- `reports/eval_run4_300_threshold_035.jsonl`
- `reports/eval_run6_1000_threshold_039.jsonl`

Implementation references (only for decision-path grounding):

- `api/main.py` (`por_decision`, `evaluate_candidate`)

## Evidence strength

- **Text-direct**: claim is explicitly stated in committed docs/wiki text.
- **Code-direct**: claim is explicitly represented in committed implementation logic.
- **Artifact-direct**: claim is directly observable in committed artifact fields/files.
- **Mixed-direct**: claim depends on both explicit documentation and artifact observation.
- **Partial**: claim is directionally supported but missing decomposition needed for stronger inference.

For the current wiki set, core claims listed above are supported directly at repository scope; extrapolations remain out of scope.

## Known evidence boundaries

- No claim of universal generalization beyond documented runs.
- No claim of global threshold optimality across all distributions.
- No claim that one metric family is universally sufficient for deployment safety.
- No claim of complete per-class/per-domain analysis where such summaries are not committed.
- No claim that PoR guarantees truth; it changes release policy.

## Maintenance rule

When updating this map:

1. Add only claims already present in repository docs/wiki.
2. Link each claim to concrete files.
3. Mark support as direct vs partial.
4. State what each claim does not establish.
5. If evidence is missing, record that explicitly instead of filling gaps.
