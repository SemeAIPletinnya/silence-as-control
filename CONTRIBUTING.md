# Contributing

Thanks for contributing to Silence-as-Control.

## How to contribute

- Open an issue for bugs, documentation gaps, or clarification requests.
- Keep issue descriptions concrete (expected behavior, observed behavior, and reproduction steps).
- For documentation or presentation fixes, submit focused pull requests with clear before/after notes.

## Scope guidance

This repository separates:
- **Architecture/runtime behavior changes** (control logic, API behavior, thresholds, evaluation logic), and
- **Documentation/presentation changes** (README, reports, hygiene files).

Please keep these in separate pull requests whenever possible.

## Local workflow (Phase 2)

### Recommended local environment

- Python 3.13.x
- A project-local virtual environment in `.venv`

### Minimal setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Run this first (canonical local demo)

```powershell
python demo/canonical_demo.py
```

Use this as the first-run local sanity check. It is the canonical demo path and does **not** require an API key.

### Optional API run

```powershell
uvicorn api.main:app --reload
```

### Optional tests

```powershell
pytest -q
```

### Branch discipline

Start new feature work from a fresh `main` branch:

```powershell
git checkout main
git pull
git checkout -b feature-name
```

### Artifact hygiene

Do not accidentally include generated outputs in unrelated pull requests. Keep them out of normal feature PRs unless the PR is explicitly about tracked artifacts.

Common examples:
- `demo_outputs/`
- `demo_outputs_api/`
- generated `.jsonl` files
- generated demo reports

### Before opening a pull request

- Check `git status`.
- Confirm you are on the correct branch.
- Confirm no unrelated generated files are staged.
- Run `python demo/canonical_demo.py` when your change affects the local demo path.
- Run `pytest -q` when relevant and low-friction.

### Scope discipline for PRs

Keep pull requests focused. Avoid unrelated cleanup and noise-only diffs.

## Pull request expectations

- Explain what changed and why.
- State whether architecture or runtime behavior was touched.
- State whether metrics/results changed.
- Include tests/checks run locally when applicable.
