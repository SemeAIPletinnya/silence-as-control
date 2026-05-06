# Threshold Calibration Guidance

Thresholds in this repository are operating-regime choices, not universal
constants. Calibrate them for each new model, task family, and signal contract.

## Calibrating for a new model

1. Freeze the task set and scoring protocol.
2. Generate candidates without changing the release gate.
3. Compute the model-specific signal distribution.
4. Sweep candidate thresholds and record:
   - coverage / silence rate,
   - accepted wrong outputs,
   - accepted precision,
   - boundary cases near the threshold.
5. Pick a threshold that matches the deployment risk tolerance.
6. Re-run on a holdout slice before treating the threshold as operational.

## Calibrating for a new task

1. Keep generation separate from release.
2. Define what counts as an accepted failure for the task.
3. Verify the signal contract captures task-relevant instability.
4. Run a small pilot sweep, then a larger validation sweep.
5. Document the threshold regime and evidence artifact paths.

## Telemetry-driven hardening workflow

1. Log prompt, candidate metadata, signal values, gate decision, and review
   outcome where policy permits.
2. Audit accepted wrong outputs before optimizing for more coverage.
3. Label boundary pockets separately from clear failures.
4. Adjust detectors or threshold regimes only after evidence review.
5. Preserve old artifacts so threshold changes remain auditable.

## Guardrail boundary

Guardrails classify or constrain. Silence-as-Control gates release. Do not merge
these roles into a single binary decision if tri-state behavior is already part
of a higher-level integration.
