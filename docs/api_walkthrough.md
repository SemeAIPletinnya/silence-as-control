# API Walkthrough (Applied Runtime Path)

This walkthrough is a compact, code-grounded path for understanding the runtime API surface in `api/main.py`.

It is **not** a production-readiness claim. It is an applied local path to see how request inputs become PoR decisions and outputs.

## Run the server

```powershell
uvicorn api.main:app --reload
```

## API entrypoints (current)

From `api/main.py`, the active HTTP entrypoints are:

- `GET /health`
  - Minimal liveness check.

- `POST /por/evaluate`
  - Evaluates a provided `prompt` + `candidate` against PoR scoring/decision logic.
  - Returns decision metadata (`drift`, `coherence`, `decision`, etc.).

- `POST /generate`
  - Legacy compatibility endpoint.
  - Uses provided `coherence` to return either `status: ok` with output or `status: abstained`.

- `POST /por/complete`
  - Generates a candidate via model wrapper, then runs PoR evaluation.
  - Returns a gated completion result with decision fields.

## Minimal request/response walkthrough

A clear first call is `POST /por/evaluate`, because it isolates evaluation behavior without requiring model generation.

Example request (PowerShell):

```powershell
$body = @{
  prompt = "Return valid JSON with key answer."
  candidate = "{\"answer\":\"ok\"}"
  threshold = 0.39
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/por/evaluate" -ContentType "application/json" -Body $body
```

Representative response shape:

```json
{
  "drift": 0.05,
  "coherence": 0.76,
  "threshold": 0.39,
  "decision": "PROCEED",
  "release_output": "{\"answer\":\"ok\"}",
  "notes": ["sufficient_length", "has_structured_format", "valid_json"]
}
```

Notes:
- Exact numeric values and notes depend on the input text.
- If decision becomes `SILENCE`, output fields are gated and a silence token is returned.

## Mental model

- **Canonical demo** = first local proof.
- **API walkthrough** = applied runtime path.
- **README / quick guides** = orientation layer.

## Suggested order for a newcomer

1. `python demo/canonical_demo.py`
2. Read `docs/integration_path.md`
3. Use this walkthrough (`docs/api_walkthrough.md`)
4. Optional: inspect `api/main.py`
