# MAYBE_SHORT_REGEN Formalization Criteria (Conservative)

This document defines a conservative, extension-layer formalization surface for the 8-case MAYBE_SHORT_REGEN lane.

## Fixed constraints

- Primitive core remains unchanged.
- Evidence anchor `0.39` remains unchanged.
- One retry only.
- Lane-bound only (MAYBE_SHORT_REGEN, 8 known task IDs).
- Extension-layer only (no primitive-state expansion, no runtime policy broadening).

## Required evidence before stronger claims

Before making stronger extension claims, all of the following should exist:

1. Reproducible local sandbox run (`scripts/short_regen_sandbox.py`) with run metadata.
2. Optional retry-side proxy scoring available (`--score-retries`) for rows with retry output.
3. Manual scoring completed in `reports/short_regen_manual_scoring_template.csv`.
4. No evidence of policy broadening beyond the curated lane.
5. Lane boundaries remain explicit and unchanged.

## Suggested conservative acceptance logic

For lane-level acceptance (not primitive acceptance), use conservative checks:

- Retry output is materially shorter than original output.
- Usefulness remains acceptable in manual review.
- Factuality/clarity does not collapse in manual review.
- `policy_ok` remains yes for reviewed rows.
- Evidence remains lane-scoped and reproducible, not generalized to all silenced outputs.

## Explicit non-claims

This formalization surface does **not** imply:

- General silence-band recoverability.
- Threshold retuning justification.
- Primitive contract changes.
- Production policy readiness.

## Boundary reminder

Retry-side scoring in the sandbox is extension-layer measurement only. It is not primitive scoring and does not alter PoR gate semantics.
