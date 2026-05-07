# LangChain + OpenAI PoR Action-Risk Benchmark (Run 06_1000case_hardened_v3)

This is a small integration/deployment validation benchmark, not a universal safety claim.

- Timestamp (UTC): 2026-05-07T06:35:23.239722+00:00
- Model: `gpt-4.1-mini`
- Dataset source: `data/action_risk/action_risk_1000.jsonl`
- Cases: 1000

## Decision Counts
- PROCEED: 542
- SILENCE: 0
- NEEDS_REVIEW: 458
- Released: 542
- Blocked or review: 458

## By Risk Class
- API_MUTATION_RISK: 160
- AUTH_SCOPE_RISK: 140
- CONFIG_RISK: 160
- HIDDEN_DEPENDENCY_RISK: 120
- PARTIAL_UPDATE_RISK: 120
- SAFE_READ_ONLY: 200
- UNSUPPORTED_OVERCLAIM: 100

## Economic Heuristic
- Estimated baseline cost: 48000
- Estimated PoR cost: 22323
- Estimated cost saved: 25677

Baseline assumes all generated outputs are released.
PoR score uses asymmetric costs where false accept is more expensive than silence.
