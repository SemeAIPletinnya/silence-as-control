# LangChain + OpenAI PoR Action-Risk Benchmark (Run 03_50case_hardened)

This is a small integration/deployment validation benchmark, not a universal safety claim.

- Timestamp (UTC): 2026-05-05T15:24:28.077426+00:00
- Model: `gpt-4.1-mini`
- Dataset source: `data\action_risk\action_risk_50.jsonl`
- Cases: 50

## Decision Counts
- PROCEED: 18
- SILENCE: 3
- NEEDS_REVIEW: 29
- Released: 18
- Blocked or review: 32

## By Risk Class
- API_MUTATION_RISK: 8
- AUTH_SCOPE_RISK: 7
- CONFIG_RISK: 8
- HIDDEN_DEPENDENCY_RISK: 6
- PARTIAL_UPDATE_RISK: 6
- SAFE_READ_ONLY: 10
- UNSUPPORTED_OVERCLAIM: 5

## Economic Heuristic
- Estimated baseline cost: 2531
- Estimated PoR cost: 726
- Estimated cost saved: 1805

Baseline assumes all generated outputs are released.
PoR score uses asymmetric costs where false accept is more expensive than silence.
