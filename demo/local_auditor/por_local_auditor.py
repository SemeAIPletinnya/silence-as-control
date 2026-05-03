# -*- coding: utf-8 -*-
"""
PoR Local Auditor v0.1

Local repo-aware AI auditor for silence-as-control.

What it does:
1. Reads selected repository files.
2. Sends repo context + user question to local Ollama model.
3. Gets candidate answer.
4. Applies a lightweight PoR-style release gate.
5. Returns PROCEED / SILENCE / MAYBE_SHORT_REGEN.

Default model:
    qwen3:4b

Run:
    python demo/local_auditor/por_local_auditor.py "Explain threshold 0.39"
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[2]

MODEL = os.environ.get("POR_MODEL", "qwen3:4b")

MAX_FILE_CHARS = 8_000
MAX_CONTEXT_CHARS = 28_000

DEFAULT_THRESHOLD = 0.39

IMPORTANT_PATHS = [
    "README.md",
    "docs/api_walkthrough.md",
    "docs/baseline_vs_por_quick_guide.md",
    "docs/integration_path.md",
    "wiki/Home.md",
    "wiki/Threshold-Regimes.md",
    "wiki/Evaluation-Summary.md",
    "wiki/Evidence-Map.md",
    "wiki/Reading-Order.md",
    "api/main.py",
    "demo/canonical_demo.py",
    "por_agent_demo.py",
    "scripts/short_regen_sandbox.py",
    "reports/eval_run4_300_threshold_035.jsonl",
    "reports/eval_run5_1000_threshold_039.jsonl",
    "reports/eval_run5_1000_threshold_042.jsonl",
    "reports/eval_run5_1000_threshold_043.jsonl",
    "reports/borderline_maybe_short_regen.csv",
]


def safe_read(path: Path, max_chars: int = MAX_FILE_CHARS) -> str:
    try:
        if not path.exists() or not path.is_file():
            return ""
        text = path.read_text(encoding="utf-8", errors="replace")
        return text[:max_chars]
    except Exception as exc:
        return f"[READ_ERROR: {exc}]"


def collect_repo_context(question: str) -> Tuple[str, List[str]]:
    """
    Lightweight repo context collector.

    v0.1 is intentionally simple:
    - Always reads key docs/source/report files if present.
    - Adds files whose path or text appears relevant to the question.
    """
    question_l = question.lower()
    chunks: List[str] = []
    used: List[str] = []

    for rel in IMPORTANT_PATHS:
        path = ROOT / rel
        text = safe_read(path)
        if not text:
            continue

        rel_l = rel.lower()
        should_include = False

        always_core = [
            "readme.md",
            "evidence-map",
            "threshold-regimes",
            "evaluation-summary",
            "api/main.py",
            "baseline_vs_por",
            "integration_path",
        ]

        if any(key in rel_l for key in always_core):
            should_include = True

        if any(token in rel_l for token in question_l.split() if len(token) > 3):
            should_include = True

        if "threshold" in question_l and ("threshold" in rel_l or "eval_run" in rel_l):
            should_include = True

        if "api" in question_l and ("api" in rel_l or "main.py" in rel_l):
            should_include = True

        if "short" in question_l or "regen" in question_l or "maybe" in question_l:
            if "short_regen" in rel_l or "borderline" in rel_l:
                should_include = True

        if should_include:
            chunks.append(f"\n\n--- FILE: {rel} ---\n{text}")
            used.append(rel)

        current_len = sum(len(c) for c in chunks)
        if current_len >= MAX_CONTEXT_CHARS:
            break

    context = "".join(chunks)[:MAX_CONTEXT_CHARS]
    return context, used


def ollama_generate(prompt: str, model: str = MODEL) -> str:
    """
    Calls Ollama CLI.

    This avoids extra Python dependencies and works on Windows PowerShell
    as long as `ollama` is available in PATH.
    """
    cmd = ["ollama", "run", model, prompt]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
    except FileNotFoundError:
        raise RuntimeError("Ollama executable not found. Check that Ollama is installed and in PATH.")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Ollama call timed out after 180 seconds.")

    if result.returncode != 0:
        raise RuntimeError(f"Ollama error:\n{result.stderr}")

    return result.stdout.strip()


def strip_thinking(text: str) -> str:
    """
    Removes Qwen/Ollama thinking traces from demo output when present.

    This keeps the local demo output clean and easier to compare in
    Baseline vs PoR screenshots / artifacts.
    """
    markers = [
        "...done thinking.",
        "</think>",
    ]

    cleaned = text.strip()

    for marker in markers:
        if marker in cleaned:
            cleaned = cleaned.split(marker, 1)[1].strip()

    return cleaned


def tokenize(text: str) -> List[str]:
    cleaned = []
    for ch in text.lower():
        if ch.isalnum() or ch in "-_":
            cleaned.append(ch)
        else:
            cleaned.append(" ")
    return [t for t in "".join(cleaned).split() if len(t) > 2]


def lexical_overlap(a: str, b: str) -> float:
    ta = set(tokenize(a))
    tb = set(tokenize(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(1, len(ta | tb))


def estimate_drift(question: str, answer: str, context: str) -> float:
    """
    Lightweight heuristic drift proxy.

    It is NOT the final scientific metric.
    It is a practical local gate for v0.1.

    High drift when:
    - answer has weak overlap with repo context;
    - answer makes exaggerated claims;
    - answer contains unsupported proof/AGI/world-changing wording.
    """
    overlap_context = lexical_overlap(answer, context)
    overlap_question = lexical_overlap(answer, question)

    unsupported_terms = [
        "agi",
        "guaranteed",
        "proves consciousness",
        "solves all",
        "world first",
        "100% universal",
        "cannot fail",
        "definitely",
        "undeniable proof",
    ]

    risky = 0
    answer_l = answer.lower()
    for term in unsupported_terms:
        if term in answer_l:
            risky += 1

    base_drift = 1.0 - min(1.0, (0.75 * overlap_context + 0.25 * overlap_question) * 8.0)
    risk_penalty = min(0.35, risky * 0.07)

    drift = max(0.0, min(1.0, base_drift + risk_penalty))
    return drift


def estimate_coherence(answer: str) -> float:
    """
    Lightweight coherence proxy.

    Rewards answers that are not empty, not broken, and have structured content.
    """
    if not answer.strip():
        return 0.0

    length = len(answer)
    length_score = min(1.0, length / 1200)

    has_structure = any(marker in answer for marker in ["\n-", "\n1.", ":", "##", "```"])
    structure_score = 0.15 if has_structure else 0.0

    broken_signals = [" ", "Traceback", "Error:", "I cannot access", "I don't have access"]
    broken_penalty = 0.0
    for signal in broken_signals:
        if signal.lower() in answer.lower():
            broken_penalty += 0.12

    coherence = max(0.0, min(1.0, 0.55 + length_score * 0.3 + structure_score - broken_penalty))
    return coherence


def por_gate(question: str, answer: str, context: str, threshold: float = DEFAULT_THRESHOLD) -> Dict[str, object]:
    drift = estimate_drift(question, answer, context)
    coherence = estimate_coherence(answer)

    if drift > threshold or coherence < 0.55:
        decision = "SILENCE"
    elif threshold * 0.82 < drift <= threshold:
        decision = "MAYBE_SHORT_REGEN"
    else:
        decision = "PROCEED"

    return {
        "decision": decision,
        "drift": round(drift, 4),
        "coherence": round(coherence, 4),
        "threshold": threshold,
    }


def build_prompt(question: str, context: str, used_files: List[str]) -> str:
    return f"""
You are PoR Local Auditor, a local repo-aware AI assistant for the project
"silence-as-control".

Your job:
- Answer using only the repository context below.
- Be precise and engineering-focused.
- Do not overclaim.
- If evidence is insufficient, say what is known and what is not established.
- Use the project's framing:
  "Same model. Different decision."
  "Either correct, or silent."
- Prefer concrete files, thresholds, metrics, and next steps.

Repository files used:
{json.dumps(used_files, ensure_ascii=False, indent=2)}

Repository context:
{context}

User question:
{question}

Answer:
""".strip()


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage:")
        print('  python demo/local_auditor/por_local_auditor.py "Explain threshold 0.39"')
        return 1

    question = " ".join(sys.argv[1:]).strip()

    context, used_files = collect_repo_context(question)

    if not context:
        print("SILENCE")
        print("Reason: no repository context found.")
        return 2

    prompt = build_prompt(question, context, used_files)

    print("\n[PoR Local Auditor]")
    print(f"Model: {MODEL}")
    print(f"Repo: {ROOT}")
    print(f"Files used: {len(used_files)}")
    for f in used_files:
        print(f" - {f}")

    print("\nGenerating candidate answer with Ollama...\n")

    try:
        candidate = strip_thinking(ollama_generate(prompt))
    except Exception as exc:
        print("SILENCE")
        print(f"Reason: {exc}")
        return 3

    gate = por_gate(question, candidate, context)

    print("=" * 80)
    print("PoR Gate")
    print("=" * 80)
    print(f"Decision:  {gate['decision']}")
    print(f"Drift:     {gate['drift']}")
    print(f"Coherence: {gate['coherence']}")
    print(f"Threshold: {gate['threshold']}")
    print("=" * 80)

    if gate["decision"] == "SILENCE":
        print("\nSILENCE")
        print("Reason: candidate answer did not earn release under the local PoR gate.")
        print("\nSuggested safer question:")
        print("Explain what the repository evidence supports, without making claims beyond the artifacts.")
        return 0

    if gate["decision"] == "MAYBE_SHORT_REGEN":
        print("\nMAYBE_SHORT_REGEN")
        print("The answer is near the release boundary. Showing candidate with caution.\n")

    print(candidate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())