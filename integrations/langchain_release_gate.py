"""LangChain-compatible PoR release gate adapter.

Integration-layer utility: generation creates a candidate; PoR decides release.
"""

from __future__ import annotations

import re

from api.core_primitive import compute_instability_score, fixed_threshold_release_decision
from api.main import SILENCE_TOKEN
from api.por_runtime import estimate_coherence, estimate_drift


class PoRLangChainReleaseGate:
    """Wrap a chain-like object with `.invoke(input)` behind PoR release control."""

    def __init__(self, chain, threshold: float = 0.39, enable_config_risk_detection: bool = True):
        self.chain = chain
        self.threshold = max(0.0, min(float(threshold), 1.0))
        self.enable_config_risk_detection = enable_config_risk_detection

    def invoke(self, input_data):
        candidate = self.chain.invoke(input_data)
        prompt_text = self._stringify(input_data)
        candidate_text = self._stringify(candidate)

        drift, drift_notes = estimate_drift([candidate_text])
        coherence, coherence_notes = estimate_coherence(prompt_text, candidate_text)
        instability = compute_instability_score(drift=drift, coherence=coherence)
        decision = fixed_threshold_release_decision(instability, self.threshold)

        notes = drift_notes + coherence_notes
        if decision == "SILENCE":
            return {
                "decision": "SILENCE",
                "released": False,
                "output": None,
                "silence_token": SILENCE_TOKEN,
                "threshold": self.threshold,
                "instability_score": round(instability, 4),
                "drift": round(drift, 4),
                "coherence": round(coherence, 4),
                "notes": notes,
            }

        if self.enable_config_risk_detection and self._has_config_removal_risk(candidate_text):
            return {
                "decision": "NEEDS_REVIEW",
                "released": False,
                "output": None,
                "silence_token": None,
                "threshold": self.threshold,
                "instability_score": round(instability, 4),
                "drift": round(drift, 4),
                "coherence": round(coherence, 4),
                "notes": notes + ["config_risk_detected"],
            }

        return {
            "decision": "PROCEED",
            "released": True,
            "output": candidate,
            "silence_token": None,
            "threshold": self.threshold,
            "instability_score": round(instability, 4),
            "drift": round(drift, 4),
            "coherence": round(coherence, 4),
            "notes": notes,
        }

    @staticmethod
    def _stringify(value) -> str:
        if isinstance(value, str):
            return value
        return str(value)

    @staticmethod
    def _has_config_removal_risk(text: str) -> bool:
        lowered = text.lower()
        clauses = [c.strip() for c in re.split(r"[.;]|\bbut\b|\bhowever\b", lowered) if c.strip()]

        removal_verbs = (
            "remove",
            "delete",
            "drop",
            "disable",
            "strip",
            "omit",
            "eliminate",
            "discard",
            "clean up",
            "cleanup",
        )
        config_terms = (
            "config",
            "configuration",
            "approval",
            "approvals",
            "policy",
            "policies",
            "runtime",
            "tool",
            "tools",
            "yaml",
            "toml",
            "ini",
            "block",
            "section",
        )
        negated_removal_phrases = (
            "do not remove",
            "don't remove",
            "should not remove",
            "must not remove",
            "never remove",
            "avoid removing",
            "not safe to remove",
            "not recommended to remove",
            "not advisable to remove",
        )
        verify_terms = ("verify", "check", "confirm", "test", "ensure", "validate")

        implicit_cleanup_patterns = (
            "redundant approval block",
            "unused approval policy",
            "orphaned config section",
            "safe to remove approvals",
        )
        implicit_negations = (
            "not redundant",
            "not unused",
            "no redundant blocks",
            "none are redundant",
            "none of the approval blocks are redundant",
            "not safe to remove",
        )

        for clause in clauses:
            has_removal_verb = any(verb in clause for verb in removal_verbs)
            has_config_term = any(term in clause for term in config_terms)

            if has_removal_verb and has_config_term:
                if any(phrase in clause for phrase in negated_removal_phrases):
                    continue
                if any(re.search(rf"\b{re.escape(term)}\b", clause) for term in verify_terms):
                    continue
                return True

            if any(pattern in clause for pattern in implicit_cleanup_patterns):
                if any(neg in clause for neg in implicit_negations):
                    continue
                return True

        return False
