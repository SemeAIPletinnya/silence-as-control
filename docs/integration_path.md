# Integration Path (Main Demo + API Entry Points)

This repository has one canonical first-run path:

```powershell
python demo/canonical_demo.py
```

Use that command first. It is the canonical local proof that your environment and core demo flow are working.

## Entry points and how they relate

- `demo/canonical_demo.py`  
  Thin wrapper for first contact. Start here for local proof-of-run.

- `demo/por_agent_demo.py`  
  Underlying local demo logic used by the canonical wrapper.

- `demo/por_api_demo.py`  
  API-oriented demo path. Useful after local proof, but not ideal as first contact because it adds setup/friction.

- `api/main.py`  
  Runtime API server surface (application entrypoint for serving).

## Mental model

- **Canonical demo** = first local proof.
- **Agent demo** = core local demo logic.
- **API demo** = API-oriented exploration path.
- **`api/main.py`** = runtime server entrypoint.

## Suggested newcomer path

1. Run `python demo/canonical_demo.py`.
2. Inspect `demo/por_agent_demo.py`.
3. Inspect `demo/por_api_demo.py`.
4. Inspect or run `api/main.py` via:

   ```powershell
   uvicorn api.main:app --reload
   ```
