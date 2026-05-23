# External reviewer packet

Silence-as-Control is a release-control layer for LLM reliability. It separates generation from release, so output creation and output release are treated as different runtime responsibilities.

In this architecture, a model or agent creates a candidate output first. The candidate then passes through PoR/SaC release control to determine whether it should be released, routed for review, or withheld.

This project is not model training and does not claim the model became smarter. It is a runtime decision layer focused on controlled release behavior.

## 1. One-sentence thesis

Generation creates a candidate. Release is a separate runtime decision.

Same model. Different decision.
Either correct, or silent.

## 2. What problem this addresses

Many LLM systems release generated text or actions by default.

In higher-risk contexts, the key question is not only “can the model answer?” but also “should this specific candidate be released?”

Silence-as-Control introduces a post-generation release-control decision so release can be governed independently of generation. This is a scoped control pattern, not a universal safety guarantee.

## 3. Architecture at a glance

```text
external generator / model / agent
  -> candidate output
  -> PoR core signal layer
       -> PROCEED / SILENCE
  -> release policy layer
       -> PROCEED / NEEDS_REVIEW / SILENCE
  -> audit metadata
```

PoR core primitive remains binary: `PROCEED` / `SILENCE`.
The release policy layer exposes the external three-state contract.
`NEEDS_REVIEW` is for stable-looking outputs that still carry operational release risk.
`SILENCE` is for candidates that exceed instability threshold.

## 4. What to run first

No-key path:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
python demo/canonical_runtime_demo.py
```

External CLI path:

```bash
python scripts/por_gate_cli.py --input examples/por_gate_input.json
```

Optional output path:

```bash
python scripts/por_gate_cli.py --input examples/por_gate_input.json --output outputs/por_gate_decision.json
```

Deterministic paths do not require provider credentials.

## 5. What evidence to inspect

- [docs/evidence_map.md](evidence_map.md)
- [docs/release_risk_benchmark_index.md](release_risk_benchmark_index.md)
- [docs/external_integration.md](external_integration.md)
- [docs/applied_bridges.md](applied_bridges.md)
- [README.md](../README.md)

Evidence is scoped to specific tasks, thresholds, datasets, and signal regimes.
Thresholds are not universal.
Benchmark artifacts are evidence surfaces, not universal guarantees.

## 6. External integration path

JSON/CLI integration is organized around candidate-plus-decision I/O.

Input fields:

- `prompt`
- `candidate_answer`
- optional `candidate_samples`
- optional `threshold`
- optional `mode`
- optional `metadata`

Output fields:

- `decision`
- `released_output`
- `silence`
- `needs_review`
- `threshold`
- `mode`
- `signals`
- `audit`

Decision meanings:

- `PROCEED`: release candidate.
- `NEEDS_REVIEW`: do not auto-release; route for review.
- `SILENCE`: withhold candidate.

See [docs/external_integration.md](external_integration.md).

## 7. Applied bridge: por-copilot-bridge

`por-copilot-bridge` is an applied bridge for coding-agent outputs.
It is not a direct dependency of `silence-as-control`.
It is architecturally connected by the same generation-vs-release separation.
It uses compatible state/schema ideas: `PROCEED` / `NEEDS_REVIEW` / `SILENCE`.

- https://github.com/SemeAIPletinnya/por-copilot-bridge

## 8. Current limitations

- Not a universal hallucination detector.
- Not a guarantee of truth.
- Not production-grade safety proof.
- Thresholds must be calibrated per task/model/signal regime.
- `NEEDS_REVIEW` review flags are deterministic and intentionally scoped.
- Provider-backed generation paths require separate configuration.
- Real pilots should define their own release policy and failure criteria.

## 9. Good first pilot use cases

Conservative first pilots:

- coding-agent output review
- config-change recommendations
- internal RAG/coprocessor answers
- workflow/action candidates before release
- agent plans before execution

Avoid:

- medical/legal/financial autonomous decisioning
- fully automated high-stakes actions
- public production claims without deployment evidence

## 10. What this project does not claim

- It does not make a model correct.
- It does not train a model.
- It does not replace evaluation.
- It does not guarantee safety.
- It does not remove the need for human review in high-risk workflows.
- It does not claim universal threshold transfer.

## 11. Best reading order

1. [README.md](../README.md)
2. [docs/plain_english_pitch.md](plain_english_pitch.md)
3. [docs/external_reviewer_packet.md](external_reviewer_packet.md)
4. [docs/external_integration.md](external_integration.md)
5. [docs/evidence_map.md](evidence_map.md)
6. [docs/release_risk_benchmark_index.md](release_risk_benchmark_index.md)
7. [docs/applied_bridges.md](applied_bridges.md)
