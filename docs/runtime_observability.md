# Runtime observability smoke walkthrough

This walkthrough verifies the local runtime telemetry path for `/por/evaluate` in
about two minutes. Telemetry is disabled by default and must be enabled
explicitly with `POR_TELEMETRY_ENABLED`.

## Windows / PowerShell

Start from a clean local telemetry file, enable telemetry, and run the API:

```powershell
Remove-Item -Recurse -Force runtime_logs -ErrorAction SilentlyContinue
$env:POR_TELEMETRY_ENABLED="1"
$env:POR_TELEMETRY_LOG_PATH="runtime_logs/por_runtime_events.jsonl"
uvicorn api.main:app --reload
```

In another terminal, send one deterministic evaluation request and print the
local report:

```powershell
curl.exe -s http://127.0.0.1:8000/por/evaluate `
  -H "content-type: application/json" `
  -d "{\"prompt\":\"Return valid JSON\",\"candidate\":\"not json\",\"threshold\":0.39}"

python scripts/runtime_observability_report.py
```

## Bash / macOS / Linux

Start from a clean local telemetry file, enable telemetry, and run the API:

```bash
rm -rf runtime_logs
POR_TELEMETRY_ENABLED=1 POR_TELEMETRY_LOG_PATH=runtime_logs/por_runtime_events.jsonl uvicorn api.main:app --reload
```

In another terminal, send one deterministic evaluation request and print the
local report:

```bash
curl -s http://127.0.0.1:8000/por/evaluate \
  -H 'content-type: application/json' \
  -d '{"prompt":"Return valid JSON","candidate":"not json","threshold":0.39}'

python scripts/runtime_observability_report.py
```

## Expected report shape

The exact decision and numeric values depend on the evaluation result, so treat
floating-point fields as approximate. After one request, the report should have
this shape:

```text
path: runtime_logs/por_runtime_events.jsonl
total_events: 1
malformed_lines: 0
events_by_type: {"por.evaluate": 1}
decisions_by_type: ...
release_count: ...
silence_count: ...
average_drift: ...
average_coherence: ...
average_instability_score: ...
```

## Privacy and scope

- Telemetry writes to a local JSONL file only.
- Telemetry is disabled by default.
- Events record compact metadata and numeric signals.
- Events do not log full prompt or candidate text by default.
- This smoke walkthrough is not production monitoring.
- This smoke walkthrough is not a universal safety claim.
