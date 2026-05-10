# First-run checklist

This checklist verifies the no-key local path first. It does not require provider credentials.

## What this checks

- package/import path works
- API tests pass
- canonical runtime demo runs
- deterministic /por/evaluate path is available
- telemetry can be enabled and summarized locally
- provider-backed /por/complete remains separate and requires provider configuration

## 1. Install

Run:

    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    python -m pip install -e .

## 2. Run no-key tests

Run:

    python -m pytest tests/test_api.py -q

Expected:

    passed

## 3. Run canonical runtime demo

Run:

    python demo/canonical_runtime_demo.py

Expected:
- the demo prints baseline release behavior
- the PoR gate returns PROCEED / NEEDS_REVIEW / SILENCE examples
- no provider key is required

## 4. Start local API

Run:

    uvicorn api.main:app --reload

In another terminal, run:

    curl http://127.0.0.1:8000/health

Expected:
- HTTP response from the local API
- no provider key required

## 5. Optional telemetry smoke check

For local telemetry verification, see:

    docs/runtime_observability.md

Keep this section short. Do not duplicate the full telemetry guide.

## 6. Provider-backed completion

For provider-backed completion setup, see:

    docs/provider_configuration.md

State clearly:
- /por/complete may require XAI_API_KEY when generating candidate output
- deterministic checks above do not require a provider key

## Scope boundaries

- This checklist verifies local onboarding only.
- This is not a production deployment guide.
- This is not a benchmark result.
- This is not a universal AI safety claim.
