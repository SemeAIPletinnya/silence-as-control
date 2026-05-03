# PoR Local Auditor

A local repo-aware auditor powered by Ollama and gated by a lightweight Silence-as-Control / PoR release decision.

## Concept

The model generates a candidate answer. The gate then decides:

- PROCEED
- SILENCE
- MAYBE_SHORT_REGEN

Same model. Different decision.
Either correct, or silent.

## Run

From repository root:

```bash
python demo/local_auditor/por_local_auditor.py "Explain what Silence-as-Control does in this repository"
```

PowerShell:

```powershell
python .\demo\local_auditor\por_local_auditor.py "Explain threshold 0.39"
```

Optional model override (PowerShell):

```powershell
$env:POR_MODEL = "qwen3:8b"
python .\demo\local_auditor\por_local_auditor.py "Explain threshold 0.39"
```

Optional model override (bash):

```bash
POR_MODEL=qwen3:8b python demo/local_auditor/por_local_auditor.py "Explain threshold 0.39"
```

## Purpose

This demo does not claim stronger model intelligence. It demonstrates release control: generation is separate from release.
