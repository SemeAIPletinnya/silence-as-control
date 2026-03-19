Silence-as-Control is a control-layer middleware that decides whether to return or suppress AI output based on explicit stability signals.

## What it is
A minimal Python middleware layer with deterministic gating logic:
- Accepts an output candidate plus stability signals (`coherence`, `drift`)
- Returns output when signals are within bounds
- Returns an explicit abstention state when signals are unstable

## Why abstention is a valid state
Abstention is a first-class response that prevents unstable output from being returned. The middleware returns:
- `{"status": "ok", "output": ...}` for stable conditions
- `{"status": "abstained", "reason": "control_abstention"}` when thresholds are violated

## Repository structure
```text
silence-as-control/
├── src/silence_as_control/
│   ├── __init__.py
│   ├── control.py
│   ├── abstention.py
│   ├── schema.py
│   └── logging_utils.py
├── api/main.py
├── tests/
│   ├── test_control.py
│   └── test_api.py
├── .github/workflows/ci.yml
├── .gitignore
├── README.md
├── requirements.txt
├── pyproject.toml
└── Dockerfile
```

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

uvicorn api.main:app --reload
```

## API example
Request:
```json
{
  "output": "text",
  "coherence": 0.82,
  "drift": 0.15
}
```

Response (stable):
```json
{
  "status": "ok",
  "output": "text"
}
```

Response (abstained):
```json
{
  "status": "abstained",
  "reason": "control_abstention"
}
```

## Test command
```bash
pytest
```
## PoR Demo – First Results

Setup:
- Runs: 30
- Signal: drift-based threshold
- Control: Silence-as-Control (abstention)

Results:
- Silence rate: 20%
- No control success rate: 70%
- With control success rate: 70%

Observations:
- Avg drift (success): 0.144
- Avg drift (fail): 0.386

Conclusion:
Drift shows strong separation between successful and failed runs.
A moderate silence threshold (drift > 0.35) maintains stability without degrading performance.
