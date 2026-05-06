# LangChain + OpenAI PoR Action-Risk Benchmark (Run 05_300case_hardened_v2)

This is a small integration/deployment validation benchmark, not a universal safety claim.

- Timestamp (UTC): 2026-05-06T07:11:16.274078+00:00
- Model: `gpt-4.1-mini`
- Dataset source: `data\action_risk\action_risk_300.jsonl`
- Cases: 300

## Decision Counts
- PROCEED: 90
- SILENCE: 0
- NEEDS_REVIEW: 210
- Released: 90
- Blocked or review: 210

## By Risk Class
- API_MUTATION_RISK: 48
- AUTH_SCOPE_RISK: 42
- CONFIG_RISK: 48
- HIDDEN_DEPENDENCY_RISK: 36
- PARTIAL_UPDATE_RISK: 36
- SAFE_READ_ONLY: 60
- UNSUPPORTED_OVERCLAIM: 30

## Economic Heuristic
- Estimated baseline cost: 14400
- Estimated PoR cost: 2117
- Estimated cost saved: 12283

Baseline assumes all generated outputs are released.
PoR score uses asymmetric costs where false accept is more expensive than silence.
