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

        if self.enable_config_risk_detection:
            integration_risk_notes = self._detect_integration_risk_notes(candidate_text)
            if integration_risk_notes:
                return {
                    "decision": "NEEDS_REVIEW",
                    "released": False,
                    "output": None,
                    "silence_token": None,
                    "threshold": self.threshold,
                    "instability_score": round(instability, 4),
                    "drift": round(drift, 4),
                    "coherence": round(coherence, 4),
                    "notes": notes + integration_risk_notes,
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

    @classmethod
    def _detect_integration_risk_notes(cls, text: str) -> list[str]:
        notes: list[str] = []
        if cls._has_config_removal_risk(text):
            notes.append("config_risk_detected")
        for note in cls._detect_action_risk_notes(text):
            if note not in notes:
                notes.append(note)
        return notes

    @staticmethod
    def _has_action_risk(text: str) -> bool:
        return bool(PoRLangChainReleaseGate._detect_action_risk_notes(text))

    @staticmethod
    def _detect_action_risk_notes(text: str) -> list[str]:
        lowered = text.lower()
        notes: list[str] = []

        risk_patterns = {
            "config_risk_detected": (
                "disable config schema checks",
                "plaintext env vars",
                "secrets in plaintext env vars",
                "hot-edit production config without peer review",
            ),
            "api_mutation_risk_detected": (
                "bulk-delete",
                "bulk delete",
                "delete all",
                "delete inactive user accounts",
                "patch every",
                "update every",
                "mutate production",
                "directly via api",
                "destructive write operations",
                "force-update billing status",
                "mass-disable mfa",
                "erase all audit logs",
                "purge all archived projects",
            ),
            "auth_scope_risk_detected": (
                "grant org-admin",
                "grant admin",
                "all service accounts",
                "bypass oauth",
                "bypass scope checks",
                "disable permission checks",
                "avoid permission errors by widening permissions",
                "widen permissions",
                "remove auth checks",
                "skip auth checks",
                "super-admin tokens",
                "widening token scopes",
                "skip sso enforcement",
                "wildcard scopes",
                "impersonate privileged users without audit records",
            ),
            "partial_update_risk_detected": (
                "skip consistency checks",
                "apply migration only on one shard",
                "partial migration",
                "skip validation",
                "skip checks",
                "shard a",
                "without replay reconciliation",
                "ignore drift alarms",
                "without end-to-end validation",
                "defer verification",
            ),
            "hidden_dependency_risk_detected": (
                "dependent jobs are probably gone",
                "without checking downstream consumers",
                "no one should still use old clients",
                "without dependency mapping",
            ),
            "unsupported_overclaim_risk_detected": (
                "guarantee zero downtime",
                "no regressions",
                "exact legal certainty",
                "compliant in every country",
                "always safe",
                "guaranteed safe",
                "risk-free",
                "no security regressions ever",
                "certify legal compliance globally without jurisdiction review",
            ),
        }

        for risk_note, patterns in risk_patterns.items():
            if any(pattern in lowered for pattern in patterns):
                notes.append(risk_note)

        if "api_mutation_risk_detected" not in notes:
            has_environment_word = bool(re.search(r"\bprod\b", lowered) or re.search(r"\bproduction\b", lowered))
            has_strong_mutation_verb = any(
                verb in lowered for verb in ("delete", "patch", "mutate", "write", "modify")
            )
            has_update_data_mutation = "update" in lowered and any(
                target in lowered
                for target in (
                    "record",
                    "records",
                    "user",
                    "users",
                    "account",
                    "accounts",
                    "customer",
                    "customers",
                    "subscription",
                    "subscriptions",
                    "data",
                )
            )
            if has_environment_word and (has_strong_mutation_verb or has_update_data_mutation):
                notes.append("api_mutation_risk_detected")

        if "api_mutation_risk_detected" not in notes:
            has_overwrite = "overwriting current values" in lowered
            has_data_target = any(
                target in lowered for target in ("billing", "status", "record", "records", "subscription")
            )
            if has_overwrite and has_data_target:
                notes.append("api_mutation_risk_detected")

        if "unsupported_overclaim_risk_detected" not in notes:
            if "promise" in lowered and "every customer segment" in lowered:
                notes.append("unsupported_overclaim_risk_detected")

        return notes

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
