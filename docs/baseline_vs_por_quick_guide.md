# Baseline vs PoR (Quick Guide)

## Thesis (30 seconds)
- **Baseline:** emits an answer by default.
- **PoR:** applies release control before output is shown; if output is unstable, it may intentionally return silence.

In short: **same generator, different release decision.**

## Comparison

| Aspect | Baseline | PoR-gated |
|---|---|---|
| Default behavior | Emit response | Evaluate stability, then release or silence |
| On unstable output | Still emits | May withhold output (silence) |
| Control objective | Always answer | Avoid releasing low-stability output |

## Compact example (same task)
Task: *"Give a deployment command for service X."*

- **Baseline path:** returns a command string immediately, even if parameters are inconsistent.
- **PoR path:** detects instability in the candidate output and returns **silence** instead of releasing a risky command.

## Live demo
Run the canonical side-by-side demo:

```powershell
python demo/canonical_demo.py
```
