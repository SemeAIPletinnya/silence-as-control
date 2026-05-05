# LangChain + OpenAI PoR Action-Risk Benchmark (Run 04_100case_hardened_v5)

This is a small integration/deployment validation benchmark, not a universal safety claim.

- Timestamp (UTC): 2026-05-05T17:35:48.870627+00:00
- Model: `gpt-4.1-mini`
- Dataset source: `data\action_risk\action_risk_100.jsonl`
- Cases: 100

## Decision Counts
- PROCEED: 48
- SILENCE: 3
- NEEDS_REVIEW: 49
- Released: 48
- Blocked or review: 52

## By Risk Class
- API_MUTATION_RISK: 16
- AUTH_SCOPE_RISK: 14
- CONFIG_RISK: 16
- HIDDEN_DEPENDENCY_RISK: 12
- PARTIAL_UPDATE_RISK: 12
- SAFE_READ_ONLY: 20
- UNSUPPORTED_OVERCLAIM: 10

## Economic Heuristic
- Estimated baseline cost: 4800
- Estimated PoR cost: 1769
- Estimated cost saved: 3031

Baseline assumes all generated outputs are released.
PoR score uses asymmetric costs where false accept is more expensive than silence.
