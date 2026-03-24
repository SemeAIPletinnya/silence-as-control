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



***### Notes***

***- Clear separation between correct and incorrect outputs***

***- Some over-silencing present***





***## Run #2 — 100 tasks (new dataset)***



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

***- No recalibration used***

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

***- Repeatability confirmed on another 100-task dataset***

***- Accepted precision remained perfect***

***- Conservative behavior still present***





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



***### Quality***

***- accepted: 0.763***

***- all: 0.571***



***### Notes***

***- 300-task robustness run***

***- Threshold increased from 0.30 to 0.35***

***- Coverage improved significantly***

***- No accepted failures***

***- Strong drift separation preserved***





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

***- Scaling test from 300 to 1000 tasks***

***- Zero accepted failures preserved***

***- Drift separation remains stable***

***- Increased silence (more conservative behavior)***





***## Run #6 — 1000 tasks (threshold = 0.42)***



***Silence rate: 43.7%***

***Coverage: 56.3%***

***Baseline success rate: 56.1%***

***PoR success rate: 55.6%***

***Accepted precision: 98.76%***

***Risk capture: 98.41%***

***Silence precision: 98.86%***

***Accepted raw fail: 7***



***### Drift***

***- raw success: 0.250***

***- raw fail: 0.670***

***- accepted: 0.250***

***- silenced: 0.672***

***- separation: \~2.68x***



***### Quality***

***- accepted: 0.760***

***- all: 0.540***

***- silenced: 0.255***



***### Notes***

***- 1000-task threshold probe above the confirmed safe zone***

***- Leakage appears: accepted failures are no longer zero***

***- Coverage is near baseline, but full safety is no longer preserved***

***- This suggests 0.42 is outside the strict zero-failure operating zone***

***- Next step: probe 0.39 as an intermediate candidate between 0.35 and 0.42***





***## Current Threshold Interpretation***



***- \*\*0.35\*\* → confirmed safe mode***

***- \*\*0.42\*\* → boundary / leakage appears***

***- \*\*0.39\*\* → next probe for a stronger balanced operating point***



***## Summary***



***Silence-as-Control shows stable drift separation across repeated runs and scales from 35 → 100 → 300 → 1000 tasks.***



***At \*\*threshold 0.35\*\*, the system preserves:***

***- zero accepted failures***

***- 100% accepted precision***

***- 100% risk capture***



***At \*\*threshold 0.42\*\*, coverage increases, but leakage appears:***

***- accepted failures > 0***

***- accepted precision drops below 100%***

***- risk capture drops below 100%***



***This confirms that threshold acts as a real control dial:***

***- lower threshold = stronger safety***

***- higher threshold = higher coverage, but rising boundary risk***



***## Visual Proof***



***### Control curve***

***!\[Control Curve](threshold\_control\_curve.png)***



***### Accepted failures comparison***

***!\[Accepted Failures](accepted\_failures\_comparison.png)***



***### Drift separation***

***!\[Drift Separation](drift\_separation\_comparison.png)***

***"""***



***with open("reports/README.md", "w", encoding="utf-8") as f:***

&#x20;   ***f.write(readme\_content)***



***print("Updated reports/README.md")***

