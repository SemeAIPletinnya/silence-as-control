## Run #1 — 35 tasks (mixed good / bad / edge cases)

Silence rate: 14.3%  
Coverage: 85.7%

Accepted precision: 100%  
Risk capture: 100%  
Silence precision: 40%

Drift:
- success: 0.218
- fail: 0.566
- separation: ~2.60x

Notes:
- Clear separation between correct and incorrect outputs
- Some over-silencing present


## Run #2 — 100 tasks (new dataset)

Silence rate: 27.0%  
Coverage: 73.0%

Accepted precision: 100%  
Risk capture: 100%  
Silence precision: 22.22%

Drift:
- success: 0.245
- fail: 0.540
- separation: ~2.20x

Quality:
- accepted: 0.802
- all: 0.750

Notes:
- Drift separation stable vs Run #1
- No recalibration used
- Conservative behavior (over-silencing)


## Run #3 — 100 tasks (new dataset)

Silence rate: 24.0%  
Coverage: 76.0%

Accepted precision: 100%  
Risk capture: 100%  
Silence precision: 20.83%

Drift:
- success: 0.242
- fail: 0.571
- separation: ~2.36x

Notes:
- Repeatability confirmed on another 100-task dataset
- Accepted precision remained perfect
- Conservative behavior still present