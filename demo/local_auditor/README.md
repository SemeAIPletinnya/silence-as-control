***# PoR Local Auditor***



***A local repo-aware AI auditor powered by Ollama + Qwen 4B and controlled by a lightweight Silence-as-Control / PoR release gate.***



***## Concept***



***The base model generates a candidate answer.***



***The PoR gate decides whether the answer earns release:***



***- PROCEED***

***- SILENCE***

***- MAYBE\_SHORT\_REGEN***



***This demonstrates the core principle:***



***> Same model. Different decision.***



***> Either correct, or silent.***



***## Run***



***From the repository root:***



***```powershell***

***python demo\\local\_auditor\\por\_local\_auditor.py "Explain what Silence-as-Control does in this repository"
Default model:***

***qwen3:4b***

***Override model:***

***$env:POR\_MODEL="qwen3:8b"***

***python demo\\local\_auditor\\por\_local\_auditor.py "Explain threshold 0.39"***

***Purpose***



***This is not a claim that the local model is more intelligent.***



***It shows that a local model can be wrapped with a release-control layer that decides when output should be released and when silence is safer.***

