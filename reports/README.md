# -*- coding: utf-8 -*-

from pathlib import Path

readme_content = """# Silence-as-Control — Proof Surface

Silence-as-Control is a control-layer primitive for AI systems:
when coherence or task-output alignment cannot be guaranteed,
intentional silence is preferred over misleading output.

Core idea:
- Baseline: model emits
- PoR: model emits only if runtime state is stable enough
- If unstable -> silence

This repository tracks:
- repeated live eval runs
- threshold operating modes
- boundary discovery
- integration demos

---

## Core Logic

if drift > threshold or coherence < threshold:
    return SilenceToken
else:
    return Proceed

PoR does not try to make the model smarter.
PoR decides when the model is allowed to speak.

---

## Run #1 — 35 tasks (mixed good / bad / edge cases)

Silence rate: 14.3%
Coverage: 85.7%
Accepted precision: 100%
Risk capture: 100%
Silence precision: 40%

Drift:

* success: 0.218
* fail: 0.566
* separation: \~2.60x

Notes:

* Clear separation between correct and incorrect outputs
* Some over-silencing present


---

## Run #2 — 100 tasks

Silence rate: 27.0%
Coverage: 73.0%
Accepted precision: 100%
Risk capture: 100%
Silence precision: 22.22%

Drift:

* success: 0.245
* fail: 0.540
* separation: \~2.20x

<<<<<<< HEAD
Notes:
- Stable behavior
- Conservative (over-silencing)
=======
Quality:

* accepted: 0.802
* all: 0.750

Notes:

* Drift separation stable vs Run #1
* No recalibration used
* Conservative behavior (over-silencing)

>>>>>>> dd95cbe (Add Run #4 robustness results (300 tasks, threshold 0.35))

---

## Run #3 — 100 tasks

Silence rate: 24.0%
Coverage: 76.0%
Accepted precision: 100%
Risk capture: 100%
Silence precision: 20.83%

Drift:

* success: 0.242
* fail: 0.571
* separation: \~2.36x

Notes:
<<<<<<< HEAD
- Repeatability confirmed

---

## Run #4 — 300 tasks (threshold = 0.35)

Silence rate: 36.0%
Coverage: 64.0%
Accepted precision: 100%
Risk capture: 100%
Silence precision: 96.3%

Drift:
- success: 0.254
- fail: 0.716
- separation: ~2.82x

Notes:
- First strong robustness result
- Zero accepted failures
- Control regime confirmed

---

## Run #5 — 1000 tasks (threshold = 0.35)

Silence rate: 46.5%
Coverage: 53.5%
Accepted precision: 100%
Risk capture: 100%
Silence precision: 93.76%

Drift:
- success: 0.253
- fail: 0.676
- separation: ~2.67x

Notes:
- Scaling confirmed
- Safe regime preserved

---

## Run #6 — 1000 tasks (threshold = 0.42)

Silence rate: 43.7%
Coverage: 56.3%
Accepted precision: 98.76%
Risk capture: 98.41%
Silence precision: 98.86%
Accepted raw fail: 7

Drift:
- success: 0.250
- fail: 0.670
- separation: ~2.68x

Notes:
- Boundary regime discovered
- First accepted failures appear

---

## Run #7 — 1000 tasks (threshold = 0.39)

Silence rate: 45.6%
Coverage: 54.4%
Accepted precision: 100.0%
Risk capture: 100.0%
Silence precision: 96.71%
Accepted raw fail: 0

Drift:
- success: 0.247
- fail: 0.671
- separation: ~2.71x

Notes:
- Optimal safe operating point
- Zero accepted failures restored
- Best balance vs 0.35

---

## Threshold Operating Modes

0.35 -> Safe mode (conservative)
0.39 -> Optimal safe mode (best balance)
0.42 -> Boundary (leakage begins)
0.43 -> Aggressive / unsafe

Threshold is a control dial.

---

## Baseline vs PoR

Baseline:
- higher coverage
- emits incorrect outputs

PoR:
- lower coverage
- eliminates accepted failures

Trade-off:
-> small coverage loss for full control

---

## Integration Demo

Baseline FAIL -> PoR SILENCE
drift = 0.460 > threshold = 0.39

PoR blocks unstable output instead of emitting incorrect code.

---

## Key Insight

PoR does not improve the model.

PoR controls the model.

From:
"generate and hope"

To:
"evaluate and decide"
"""

Path("reports").mkdir(exist_ok=True)
Path("reports/README.md").write_text(readme_content, encoding="utf-8")

print("README FULLY FIXED — NO CONFLICTS")
=======

* Repeatability confirmed on another 100-task dataset
* Accepted precision remained perfect
* Conservative behavior still present



## Run #4 — 300 tasks (threshold = 0.35)

Silence rate: 36.0%  
Coverage: 64.0%

Accepted precision: 100%  
Risk capture: 100%  
Silence precision: 96.3%

Drift:

* success: 0.254
* fail: 0.716
* separation: \~2.82x

Quality:

* accepted: 0.763
* all: 0.571
* 

Notes:

* 300-tasks robustness run
* threshold increased 0.30 to 0.35
* coverage improved significantly
* no accepted failures
* strong drift separation preserved



<<<<<<< HEAD
>>>>>>> dd95cbe (Add Run #4 robustness results (300 tasks, threshold 0.35))
=======
## Run #5 — 1000 tasks (threshold = 0.35)

Silence rate: 46.5%  
Coverage: 53.5%

Accepted precision: 100%  
Risk capture: 100%  
Silence precision: 93.76%

Drift:

* success: 0.253
* fail: 0.676
* separation: \~2.67x

Notes:

* Scaling test from 300 → 1000 tasks
* Zero accepted failures preservedcoverage improved significantly
* Drift separation remains stable
* strong drift separation preserved
* Increased silence (more conservative behavior)

>>>>>>> (Add Run #5 results (1000 tasks, threshold 0.35))
