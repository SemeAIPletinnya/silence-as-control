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



## Run #2 — 100 tasks (new dataset)

Silence rate: 27.0%  
Coverage: 73.0%

Accepted precision: 100%  
Risk capture: 100%  
Silence precision: 22.22%

Drift:

* success: 0.245
* fail: 0.540
* separation: \~2.20x

Quality:

* accepted: 0.802
* all: 0.750

Notes:

* Drift separation stable vs Run #1
* No recalibration used
* Conservative behavior (over-silencing)



## Run #3 — 100 tasks (new dataset)

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



## Run #5 — 1000 tasks (threshold = 0.43)

Silence rate: 45.0%  
Coverage: 55.0%

Accepted precision: 98.36%  
Risk capture: 98.01% 
Silence precision: 98.44%

Drift:

* success: 0.249
* fail: 0.67
* separation: \~2.7x

Notes:

* Increased coverage vs 0.35
* Slight drop in precision due to boundary overlap
* Drift separation remains stable
* Demonstrates controllable trade-off between safety and coverage



