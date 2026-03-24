***# -\*- coding: utf-8 -\*-***



***readme\_content = """## Run #1 — 35 tasks (mixed good / bad / edge cases)***



***Silence rate: 14.3%***

***Coverage: 85.7%***

***Accepted precision: 100%***

***Risk capture: 100%***

***Silence precision: 40%***



***### Drift***

***- success: 0.218***

***- fail: 0.566***

***- separation: \~2.60x***


***- Some over-silencing present***

***### Notes***

***- Clear separation between correct and incorrect outputs***

***- Some over-silencing present***





***## Run #2 — 100 tasks (new dataset)***

***Coverage: 73.0%***  

***Accepted precision: 100%***  

***Silence rate: 27.0%***

***Coverage: 73.0%***

***Accepted precision: 100%***

***Risk capture: 100%***

***Silence precision: 22.22%***



***### Drift***

***- success: 0.245***

***- fail: 0.540***

***- separation: \~2.20x***



***### Quality***

***- accepted: 0.802***

***- all: 0.750***



***### Notes***

***- Drift separation stable vs Run #1***

***- Conservative behavior (over-silencing)***





***## Run #3 — 100 tasks (new dataset)***



***Silence rate: 24.0%***

***Coverage: 76.0%***

***Accepted precision: 100%***

***Risk capture: 100%***

***Silence precision: 20.83%***



***### Drift***

***- success: 0.242***

***- fail: 0.571***

***- separation: \~2.36x***



***### Notes***

***- Repeatability confirmed***

***- Accepted precision remained perfect***





***## Run #4 — 300 tasks (threshold = 0.35)***



***Silence rate: 36.0%***

***Coverage: 64.0%***

***Accepted precision: 100%***

***Risk capture: 100%***

***Silence precision: 96.3%***



***### Drift***

***- success: 0.254***

***- fail: 0.716***

***- separation: \~2.82x***



***### Notes***

***- First strong robustness result***

***- Zero accepted failures***

***- Control regime confirmed***





***## Run #5 — 1000 tasks (threshold = 0.35)***



***Silence rate: 46.5%***

***Coverage: 53.5%***

***Accepted precision: 100%***

***Risk capture: 100%***

***Silence precision: 93.76%***



***### Drift***

***- success: 0.253***

***- fail: 0.676***

***- separation: \~2.67x***



***### Notes***

***- Scaling from 300 → 1000 tasks***

***- Zero accepted failures preserved***

***- Strong safety regime***





***## Run #6 — 1000 tasks (threshold = 0.42)***



***Silence rate: 43.7%***

***Coverage: 56.3%***

***Accepted precision: 98.76%***

***Risk capture: 98.41%***

***Silence precision: 98.86%***

***Accepted raw fail: 7***



***### Drift***

***- success: 0.250***

***- fail: 0.670***

***- separation: \~2.68x***



***### Notes***

***- Boundary regime discovered***

***- First accepted failures appear***

***- Confirms leakage beyond safe zone***





***## Run #7 — 1000 tasks (threshold = 0.39)***



***Silence rate: 45.6%***

***Coverage: 54.4%***

***Accepted precision: 100.0%***

***Risk capture: 100.0%***

***Silence precision: 96.71%***

***Accepted raw fail: 0***



***### Drift***

***- success: 0.247***

***- fail: 0.671***

***- separation: \~2.71x***



***### Notes***

***- Optimal safe operating point***

***- Zero accepted failures restored at 1000-task scale***

***- Better balance vs 0.35***

***- Strongest practical deployment candidate***





***## Threshold Operating Modes***



***- \*\*0.35 → Safe mode (conservative)\*\****

***- \*\*0.39 → Optimal safe mode (best balance)\*\****

***- \*\*0.42 → Boundary (leakage begins)\*\****

***- \*\*0.43 → Aggressive / unsafe zone\*\****



***Threshold is not a parameter — it is a control dial.***





***## Baseline vs PoR***



***Baseline:***

***- higher coverage***

***- emits incorrect outputs***



***PoR:***

***- slightly lower coverage***

***- eliminates accepted failures***



***Core trade-off:***

***→ small coverage loss for full control***





***## Integration Demo — PoR-Gated Code Suggestions***



***A minimal demonstration of PoR as a runtime control layer.***



***### Result:***

***- Baseline: emits incorrect outputs***

***- PoR: either correct or silent***



***### Example:***



***Baseline FAIL → PoR SILENCE***  

***drift = 0.460 > threshold = 0.39***  



***PoR suppressed unstable output instead of emitting an incorrect suggestion.***





***## Key Insight***



***PoR does not improve the model.***



***PoR controls the model.***



***From:***

***"generate and hope"***



***To:***

***"evaluate and decide"***

***"""***



***with open("reports/README.md", "w", encoding="utf-8") as f:***

&#x20;   ***f.write(readme\_content)***



***print("README fully updated")***

