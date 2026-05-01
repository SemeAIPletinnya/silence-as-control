# Threshold Regime Contract

This document defines how to interpret threshold results in this repository.

## Core contract

Thresholds are **behavior-control dials**, not universal constants.

A threshold observation is only valid inside its exact evaluation scope:

- model variant,
- dataset slice,
- benchmark path,
- PoR mode/runtime configuration.

Changing any of those can change coverage, silence, and accepted-wrong behavior.

## Regime language (conservative)

Use these terms as operational labels, not universal guarantees:

- **Conservative regime**: lower coverage, stronger release caution.
- **Practical regime**: useful coverage with controlled accepted-wrong risk in a specific run.
- **Transitional regime**: near a behavior shift; monitor accepted-wrong and false-silence balance closely.
- **High-coverage boundary**: aggressive coverage edge in a specific run; may still carry accepted wrong outputs.

## Interpreting 0.35 / 0.39 / 0.42 / 0.43 in current local SimpleQA/Ollama runs

Scope for this section:

- dataset: 100-example local SimpleQA batch,
- benchmark path: repository SimpleQA/Ollama evaluation flow,
- mode: PoR v2,
- model families: Qwen3 4B and Qwen3 8B local Ollama runs from PR #131 and PR #132.

Interpretation guidance:

- **0.35**: conservative-to-practical transition in these runs; lower coverage with stronger abstention.
- **0.39**: practical coverage increase while still keeping accepted-wrong tightly controlled in these runs.
- **0.42**: practical/high-coverage transition; strong coverage, but model-specific risk profile matters.
- **0.43**: high-coverage boundary in these runs; should be read with accepted-wrong counts, not coverage alone.

Do not transfer these labels outside this exact scope without rerunning evidence.

## Qwen3 4B anchor (this run only)

In the PR #131 run (Qwen3 4B, 100-example SimpleQA/Ollama, PoR v2), threshold **0.43** produced:

- 84% answer coverage,
- 16% silence,
- 84 accepted correct,
- 0 accepted wrong,
- 100% accepted precision.

Therefore, **Qwen3 4B @ 0.43** is a **practical zero-accepted-failure anchor for this specific run**.
It is not a universal safety claim across datasets, prompts, or deployment modes.

## Qwen3 8B boundary (this run only)

In the PR #132 run (Qwen3 8B, 100-example SimpleQA/Ollama, PoR v2), thresholds **0.42/0.43** produced:

- 93% answer coverage,
- 7% silence,
- 92 accepted correct,
- 1 accepted wrong,
- 98.92% accepted precision.

Therefore, **Qwen3 8B @ 0.42/0.43** is a **high-coverage boundary**, not a zero-accepted-failure anchor, in this run.

## Non-claim reminder

A stronger generation model does **not** automatically imply safer release behavior at a fixed threshold.
Release safety is an observed property of **model + gate + threshold + benchmark scope**.
