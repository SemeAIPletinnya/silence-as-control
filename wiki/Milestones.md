# Milestones

## Timeline (project evolution)

1. **Core thesis established**
   - Silence-as-Control defined as release control (not generation improvement).

2. **Initial proof runs committed**
   - Early repeated evaluations showed release gating behavior and baseline contrast.

3. **Threshold map established**
   - Operating regimes around 0.35 / 0.39 / 0.42 / 0.43 became explicit in artifacts.

4. **Safe-mode behavior confirmed at scale**
   - 1000-task runs in safe anchors retained strong accepted-output control characteristics.

5. **Applied API/runtime path clarified (latest upgrade)**
   - `docs/api_walkthrough.md` + runtime endpoints provide a clearer applied path:
     request -> candidate -> gate -> proceed/silence.

6. **Silence-rate optimization workstream documented**
   - `docs/silence_rate_roadmap.md` defines the workstream and discipline boundaries.

7. **Borderline pocket findings documented**
   - `docs/borderline_pocket_findings.md` captures structured exploratory evidence for lane selection.

8. **First extension experiment specified**
   - `docs/first_extension_experiment.md` documents the first extension-layer direction and conservative next step.

9. **First short-regeneration sandbox runner added**
   - `scripts/short_regen_sandbox.py` added as a controlled sandbox execution surface.

10. **Sandbox loader micro-fix merged**
   - BOM/task_id CSV loader fix applied (PR #97), reducing avoidable ingest noise in sandbox runs.

11. **First short-regeneration sandbox findings documented**
   - `docs/short_regen_sandbox_findings.md` records first sandbox-level signal and limits of interpretation.

12. **Current stage**
   - Post-proof + post-workstream-documentation + first sandbox signal captured; now in controlled follow-up mode, not basic documentation mode.

## Next milestone targets

- Controlled follow-up sandbox run(s) with explicit lane and stopping criteria.
- Extension-layer direction refinement based on sandbox-level signal.
- Conservative bridge from sandbox evidence to stronger applied demonstrations.
