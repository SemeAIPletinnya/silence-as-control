# Direct reproduction guide

This guide gives external reviewers a minimal local path to verify baseline Silence-as-Control behavior.

It focuses on deterministic, no-key execution paths that can be run from a fresh local checkout.

It does not reproduce every benchmark artifact in the repository and does not make universal safety claims.

Provider-backed generation paths are separate and require additional configuration; they are intentionally out of scope for this guide.

## 1. What this guide verifies

This guide verifies that:

- the repository installs locally;
- the canonical deterministic demo runs;
- the external CLI gate can evaluate a candidate JSON input;
- selected focused tests pass;
- release decisions are exposed as structured outputs.

This guide does **not** verify:

- universal model correctness;
- production safety;
- threshold transfer across tasks or models;
- provider-backed generation behavior;
- #238 v4 benchmark track.

## 2. Environment

Assumptions:

- Python 3.11+ is recommended.
- Works on Windows PowerShell, macOS, or Linux shell.
- Provider keys are not required for this reproduction path.

Windows note: if pytest temp-folder permissions or file locks cause failures, use a unique `--basetemp` path (shown below).

## 3. Fresh checkout setup

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

Windows PowerShell activation hint:

```powershell
.venv\Scripts\activate
```

Bash/macOS/Linux activation hint:

```bash
source .venv/bin/activate
```

## 4. Run the canonical deterministic demo

```bash
python demo/canonical_runtime_demo.py
```

Expected result:

- command exits successfully;
- local runtime/release-control behavior is shown;
- no provider key is required.

## 5. Run the external CLI gate

```bash
python scripts/por_gate_cli.py --input examples/por_gate_input.json
```

Optional file output:

```bash
python scripts/por_gate_cli.py --input examples/por_gate_input.json --output outputs/por_gate_decision.json
```

Expected structured output fields include:

- `decision`
- `released_output`
- `silence`
- `needs_review`
- `threshold`
- `mode`
- `signals`
- `audit`

Possible decision values:

- `PROCEED`
- `NEEDS_REVIEW`
- `SILENCE`

## 6. Run focused tests

Cross-platform command:

```bash
python -m pytest tests/test_por_gate_cli.py tests/test_release_policy.py tests/test_api.py -q
```

Windows PowerShell safer variant:

```powershell
$bt = "C:\Users\User\pytest-sac-repro-" + (Get-Date -Format "yyyyMMdd-HHmmss")
python -m pytest tests/test_por_gate_cli.py tests/test_release_policy.py tests/test_api.py -q --basetemp="$bt"
```

This focused smoke/reproduction path checks the external CLI contract, release policy behavior, and API tests. It is not the full benchmark suite.

## 7. Evidence surfaces to inspect after running

- [Evidence map](evidence_map.md)
- [Release-risk benchmark index](release_risk_benchmark_index.md)
- [External integration CLI](external_integration.md)
- [External reviewer packet](external_reviewer_packet.md)
- [Applied bridges](applied_bridges.md)

Use these to interpret what was demonstrated:

- the evidence map connects claims to artifacts;
- the benchmark index explains v1/v2/v3 release-risk benchmark lineage;
- the external integration document explains the CLI input/output contract;
- the reviewer packet provides a high-level technical overview.

## 8. Reading the results correctly

A successful local run shows that the deterministic local path works on your machine.

It does **not** prove universal AI safety, does **not** prove all model outputs are correct, and does **not** prove threshold transfer to new tasks or models.

Interpret results within the specific task, signal, threshold, and dataset regime used.

## 9. Where #238 fits

Issue #238 is future work for provider/local generated-candidate capture and replay.

This guide intentionally does not implement or require #238.

The current path is scoped to stable, no-key verification.

## 10. Troubleshooting

- If pytest temp permissions fail on Windows, run pytest with a unique `--basetemp` path.
- If provider-backed `/por/complete` fails, check provider configuration; it is not required for this guide.
- If an output path does not exist, the CLI should create parent directories for `--output`.
- If imports fail, run `python -m pip install -e .`.
