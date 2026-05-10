# Provider configuration

This page separates deterministic local runtime paths from provider-backed
candidate generation so local setup does not conflate PoR evaluation with API key
configuration.

## No-key deterministic path

These paths work without any provider/API key:

- `python demo/canonical_runtime_demo.py`
- `GET /health`
- `POST /por/evaluate`
- local telemetry smoke walkthroughs that call `/por/evaluate`
- tests

The deterministic path evaluates already-supplied candidate text and signals. It
does not need a provider to generate candidate output.

## Provider-backed completion path

`POST /por/complete` requires provider configuration when it needs to generate a
candidate via the provider before applying the runtime gate.

Configure:

- `XAI_API_KEY` — provider key for candidate generation.
- `XAI_MODEL` — provider model name. The local template uses `grok-4` as the
  default example.

Use the root `.env.example` file as a local template:

PowerShell/Windows:

```powershell
copy .env.example .env
```

Bash/macOS/Linux:

```bash
cp .env.example .env
```

## Environment variables

- `XAI_API_KEY` — required only for provider-backed candidate generation in
  `/por/complete`.
- `XAI_MODEL` — optional provider model override for `/por/complete`.
- `POR_RUNTIME_GATE_THRESHOLD` — optional runtime gate threshold. The practical
  safe anchor documented in current evidence is `0.39`; threshold behavior is
  scoped and should be calibrated for new settings.
- `POR_TELEMETRY_ENABLED` — optional local JSONL telemetry switch. It is disabled
  by default; set to `1` to write compact local runtime decision events.
- `POR_TELEMETRY_LOG_PATH` — optional path for local JSONL telemetry events.

## Docker/local notes

For a local Python runtime, export the variables in your shell or load them from
`.env` with your usual local workflow before starting the API.

For Docker Compose, use the repo-local template after copying it to `.env`:

```bash
docker compose --env-file .env up --build
```

Docker Compose maps `XAI_*`, `POR_RUNTIME_GATE_THRESHOLD`, and
`POR_TELEMETRY_*` into the API container when using `--env-file .env`. No
provider key is needed for `/health`, `/por/evaluate`, or the canonical runtime
demo.

## Scope boundaries

- Provider configuration is only for candidate generation in `/por/complete`.
- Provider configuration does not change PoR core.
- Provider configuration does not change threshold logic.
- This does not make the runtime production monitoring.
- Telemetry remains opt-in and local.
