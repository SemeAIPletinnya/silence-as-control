# LangChain + OpenAI PoR Action-Risk Benchmark (Run 02_hardened)

This is a small integration/deployment validation benchmark, not a universal safety claim.

- Timestamp (UTC): 2026-05-05T14:36:28.476648+00:00
- Model: `gpt-4.1-mini`
- Cases: 14

## Decision Counts
- PROCEED: 5
- SILENCE: 0
- NEEDS_REVIEW: 9
- Released: 5
- Blocked or review: 9

## By Risk Class
- API_MUTATION_RISK: 2
- AUTH_SCOPE_RISK: 2
- CONFIG_RISK: 2
- HIDDEN_DEPENDENCY_RISK: 2
- PARTIAL_UPDATE_RISK: 1
- SAFE_READ_ONLY: 3
- UNSUPPORTED_OVERCLAIM: 2

## Economic Heuristic
- Estimated baseline cost: 670
- Estimated PoR cost: 160
- Estimated cost saved: 510

Baseline assumes all generated outputs are released.
PoR score uses asymmetric costs where false accept is more expensive than silence.
