# Package Organization Migration Plan

This repository intentionally keeps the current package layout stable for this
cleanup pass. A forced move into `core/`, `runtime/`, and `experimental/`
subpackages would risk breaking benchmark scripts, historical import paths, and
report reproduction workflows.

## Current safe mapping

- Deterministic control logic:
  - `src/silence_as_control/control.py`
  - `api/core_primitive.py`
- Runtime/adaptive extensions:
  - `api/por_runtime.py`
  - `src/silence_as_control/signals.py` for shared runtime/demo estimators
- Experimental recovery:
  - `api/experimental_recovery.py`
  - `scripts/short_regen_sandbox.py`

## Future migration approach

1. Add compatibility re-export modules first, for example
   `silence_as_control.core`, `silence_as_control.runtime`, and
   `silence_as_control.experimental`.
2. Move one layer at a time while keeping old imports alive.
3. Run benchmark-path tests before and after each move.
4. Do not migrate historical artifacts or reports.
5. Only remove compatibility imports in a documented major-version change.
