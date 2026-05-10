# Applied bridges

Applied bridges are small integration-layer examples that reuse the Silence-as-Control separation between generation and release without changing the primitive core, runtime thresholds, or evaluation claims.

## por-copilot-bridge

[`por-copilot-bridge`](https://github.com/SemeAIPletinnya/por-copilot-bridge) is a small deterministic release-governance bridge for AI coding-agent outputs. It treats coding-agent output as a release candidate rather than an automatically releasable artifact.

The bridge demonstrates the same core separation used here: generation is not release. It maps candidates to `PROCEED` / `NEEDS_REVIEW` / `SILENCE` so a downstream workflow can decide whether to release, route for review, or abstain.

The bridge is dependency-free and compatible by state/schema. It is not a direct dependency of Silence-as-Control, and it does not imply a universal safety guarantee, automatic correctness, model improvement, or autonomous release authority.
