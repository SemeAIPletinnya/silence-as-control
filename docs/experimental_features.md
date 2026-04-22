# Experimental Features

You are here: optional experiment lane documentation.

## MAYBE_SHORT_REGEN (experimental)

MAYBE_SHORT_REGEN is a post-silence recovery attempt for boundary-pocket cases near threshold.

Properties:
- optional (`enable_experimental_short_regen`),
- only after initial `SILENCE`,
- only within a narrow instability margin,
- second pass is re-evaluated by the same gate.

Implementation: `api/experimental_recovery.py` + `/por/complete` wiring in `api/main.py`.

## Interpretation

This lane may reduce false silences near decision boundaries, but remains exploratory and non-core.
