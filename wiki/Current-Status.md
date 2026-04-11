# Current Status

## Completed

- Repeated evaluation runs are committed across multiple task sizes and thresholds (`reports/eval_*.jsonl`, `wiki/runs/`).
- Threshold regimes are mapped and compared (0.35, 0.39, 0.42, 0.43 artifacts).
- Baseline vs PoR framing is explicit in docs and wiki (`docs/baseline_vs_por_quick_guide.md`, `wiki/comparisons/Baseline_vs_PoR.md`).
- Artifact trail/report surface is established (`reports/` JSONL + plots + run pages).
- Proof surface maturity improved: claims are connected to artifacts and run summaries.
- Repo surface / onboarding layer has been strengthened (README + wiki + docs cross-navigation updates already merged).
- Silence-rate optimization is now a separate documented workstream (`docs/silence_rate_roadmap.md`).
- Borderline pocket findings are documented (`docs/borderline_pocket_findings.md`).
- First extension experiment is documented (`docs/first_extension_experiment.md`).
- First short-regeneration sandbox runner exists (`scripts/short_regen_sandbox.py`).
- Sandbox CSV BOM/task_id micro-fix has been applied (loader robustness fix merged in PR #97).
- First short-regeneration sandbox findings are documented (`docs/short_regen_sandbox_findings.md`).

## In Progress

- Applied API/runtime surface is becoming clearer (`docs/api_walkthrough.md`, `api/main.py`).
- Controlled follow-up work on extension-layer behavior after first sandbox-level signal.
- Conservative lane selection for next experiment step using documented borderline-pocket and sandbox evidence.

## Next

- Run disciplined follow-up sandbox passes (same harness class, tighter lane controls, explicit acceptance criteria).
- Refine extension-layer direction based on measured sandbox-level signal (not broad runtime retuning).
- Keep evidence map strict: separate what is documented from what is only suggested by early exploratory results.
