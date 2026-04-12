# Current Status

## Completed

- Repeated evaluation runs are committed across multiple task sizes and thresholds (`reports/eval_*.jsonl`, `wiki/runs/`).
- Threshold regimes are mapped and compared across repository-tracked operating points (`0.35`, `0.39`, `0.42`, `0.43`).
- Baseline vs PoR framing is explicit in docs and wiki (`docs/baseline_vs_por_quick_guide.md`, `wiki/comparisons/Baseline_vs_PoR.md`).
- Artifact trail and report surface are established (`reports/` JSONL + plots + run pages).
- Repo onboarding and navigation have been strengthened (README + wiki + docs cross-navigation).
- API walkthrough exists (`docs/api_walkthrough.md`, `wiki/API-Walkthrough.md`).
- A structured runtime endpoint surface exists in `api/main.py` (`/health`, `/por/evaluate`, `/generate`, `/por/complete`).
- Selected evidence plots are tracked in `reports/`, including threshold, accepted-failure, drift, and metrics summaries.

## In Progress

- Stronger integration-facing proof surface beyond local/demo-oriented runtime application.
- Clearer public proof boundaries: keeping repository-demonstrated claims separate from broader external claims.
- Additional applied runtime examples that improve readability without overstating production-hardening.
- Extension-layer exploration remains secondary to the main repo-facing proof surface and should stay evidence-bounded.

## Next

- External integration proof under real runtime constraints.
- Broader benchmark and domain-transfer testing.
- Stronger applied demo surface for outsiders evaluating the release-control framing.
- Continue strict claim-to-evidence discipline: separate what is demonstrated, partially established, and still pending.
