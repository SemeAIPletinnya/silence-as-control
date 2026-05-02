# External PoR gate integration (minimal CLI)

This interface is a **release-control integration point**, not a generation-improvement mechanism.
It evaluates a candidate answer against the existing PoR gate logic and returns a release decision.

The first CLI version supports mode `v1` only. v2-family modes require additional external signals and will be added after the external contract is stable.

## CLI usage

```bash
python scripts/por_gate_cli.py \
  --input examples/por_gate_input.json \
  --output /tmp/por_gate_output.json
```

Optional overrides:

- `--threshold 0.39` (overrides JSON threshold)
- `--mode v1` (overrides JSON mode)

## Required input fields

Input JSON must include:

- `prompt` (string)
- `candidate_answer` (string)

`candidate_samples` is recommended for drift estimation; if missing or empty, the CLI safely falls back to `[candidate_answer]`.

## Optional metadata

`metadata` is optional and audit-facing. Common fields include:

- `model`
- `source`
- generation settings like `temperature`, `top_p`, `top_k`

Only `model` and `source` are forwarded into the output audit block by this minimal interface.

## Decision semantics

- `PROCEED`: candidate is releasable under the configured threshold.
- `SILENCE`: candidate is withheld by release control.

Output includes:

- `decision`
- `released_output` (string for `PROCEED`, `null` for `SILENCE`)
- `silence` boolean
- `signals` (`drift`, `coherence`, `instability`)
- `audit` metadata

## Threshold and scope

Thresholds are **scoped configuration values** and should be calibrated per model/dataset/pipeline/mode.

This interface does **not** make universal safety claims.
