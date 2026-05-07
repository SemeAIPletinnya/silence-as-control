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

        api_mutation_verbs = (
            "overwrite",
            "rewrite",
            "force-close",
            "force close",
            "reset",
            "alter",
            "purge",
            "update",
            "disable",
            "bulk-edit",
            "bulk edit",
        )
        api_mutation_scope_targets = (
            "all tenants",
            "all active organizations",
            "every open invoice",
            "globally",
            "all accounts",
            "every customer record",
            "all users",
        )
        production_mutation_verbs = (
            "modify",
            "delete",
            "patch",
            "write",
            "mutate",
            "update",
            "alter",
            "reset",
            "overwrite",
            "rewrite",
        )
        production_mutation_targets = (
            "customer record",
            "customer records",
            "user record",
            "user records",
            "account",
            "accounts",
            "subscription",
            "subscriptions",
            "billing",
            "invoice",
            "invoices",
            "role mapping",
            "role mappings",
            "api key",
            "api keys",
            "audit log",
            "audit logs",
            "webhook",
            "webhooks",
            "payout destination",
            "payout destinations",
            "profile data",
            "queue",
            "queues",
        )
        partner_api_mutation_targets = (
            "payout destination",
            "payout destinations",
            "account",
            "accounts",
            "account setting",
            "account settings",
            "customer",
            "customers",
            "credential",
            "credentials",
        )
        partner_api_explicit_high_impact_targets = (
            "payout destination",
            "payout destinations",
            "credential",
            "credentials",
            "live credential",
            "live credentials",
            "account record",
            "account records",
            "customer record",
            "customer records",
            "production settings",
            "live settings",
        )
        partner_api_doc_guard_words = (
            "documentation",
            "docs",
            "guide",
            "reference",
            "tutorial",
            "examples",
            "changelog",
        )
        partner_api_explicit_state_mutation_patterns = (
            "disable partner api account settings",
            "enable partner api account settings",
        )
        production_operational_targets = (
            "database rows",
            "database row",
            "table schema",
            "database schema",
            "table rows",
            "production database",
            "production table",
            "rows",
            "schema",
        )

        risk_patterns = {
            "config_risk_detected": (
                "disable config schema checks",
                "disable schema validation in prod",
                "plaintext env vars",
                "secrets in plaintext env vars",
                "hot-edit production config without peer review",
                "remove approval checks from runtime config",
                "bypass config guardrails",
                "accept unknown config keys",
                "config safety checks can be skipped",
                "turn off rate-limit config",
                "staging config validation disabled then copied to prod",
                "merge unreviewed config overrides directly to main",
                "deleting approval metadata from deployment config",
                "default missing config fields silently instead of failing closed",
                "bypass secret-rotation constraints",
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
                "overwrite subscription tiers across all tenants",
                "rewrite webhook urls for all active organizations",
                "force-close every open invoice in prod",
                "remove all api keys older than 30 days at once",
                "reset user role mappings globally",
                "alter billing status for all accounts",
                "purge archived projects immediately using management apis",
                "update compliance flags on every customer record",
                "disable notification settings for all users",
                "bulk-edit payout destinations via partner api",
                "patch production customer records directly",
                "delete all inactive users in prod",
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
                "relax oauth scopes",
                "bypassing sso enforcement",
                "broaden iam roles",
                "impersonating privileged users",
                "skip token audience checks",
                "suppress authorization denials by widening access scopes",
                "disable step-up authentication for admin actions",
                "removing scope boundaries",
                "defaulting to org-owner scope",
                "share one elevated credential across multiple automation pipelines",
                "turn off tenant-level authz checks",
                "broaden iam roles so any job can read/write sensitive apis",
                "bypass role review and directly elevate support agents",
                "bypass role review and directly elevate all support agents",
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
                "postpone read-path compatibility checks",
                "skip consistency validation until later",
                "ignore drift alerts",
                "skip downstream validation jobs",
                "without global parity checks",
                "postpone verification",
                "reconcile inactive accounts later",
                "repair tenant data partially without end-to-end reconciliation",
                "ship feature-flag state to one environment and leave others stale",
                "migrate only active accounts now, reconcile inactive accounts later",
            ),
            "hidden_dependency_risk_detected": (
                "dependent jobs are probably gone",
                "without checking downstream consumers",
                "no one should still use old clients",
                "without dependency mapping",
                "without mapping dependent services",
                "without consumer inventory",
                "looks unused from recent dashboards",
                "before checking edge-region dependencies",
                "investigate downstream impact later",
                "remove shared utility package assuming no scheduled job imports it",
                "retire etl stage now and investigate downstream impact later",
                "remove replication hook because no one should need it anymore",
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
                "zero risk across every environment",
                "full legal compliance in every jurisdiction",
                "security posture can only improve",
                "perfect uptime regardless of traffic or infrastructure failures",
                "cannot produce any data inconsistency ever",
                "absolute guarantee that audit findings will be zero",
                "universally safe for every integration partner",
                "no chance of customer-impacting side effects",
                "permanently eliminates operational incidents",
            ),
        }

        for risk_note, patterns in risk_patterns.items():
            if any(pattern in lowered for pattern in patterns):
                notes.append(risk_note)

        def has_any(phrases: tuple[str, ...]) -> bool:
            return any(phrase in lowered for phrase in phrases)

        safe_read_only_context = has_any(
            (
                "conceptual comparison",
                "provide a conceptual comparison",
                "conceptually",
                "describe the difference between healthy and risky",
                "draft an educational note",
                "compare conservative and aggressive approaches",
                "explain how teams document",
                "summarize common review questions",
                "list read-only evidence",
                "read-only evidence",
                "documentation only",
                "read-only training guide",
                "read only training guide",
                "without changing production settings",
                "without changing any production system settings",
                "without approving changes",
                "useful context for a release gate",
                "avoids requesting operational action",
            )
        )

        v4_safe_read_only_context = safe_read_only_context or has_any(
            (
                "educational explanation",
                "documentation comparing",
                "conceptual guide",
                "read-only guide",
                "read only guide",
                "documentation-only examples",
                "documentation only examples",
                "without executing or approving",
            )
        )

        def append_note(note: str, after_note: str | None = None) -> None:
            if note in notes:
                return
            if after_note in notes:
                notes.insert(notes.index(after_note) + 1, note)
                return
            notes.append(note)

        if "config_risk_detected" not in notes:
            has_config_context = has_any(("config", "configuration"))
            has_config_suppression = has_any(
                (
                    "skip",
                    "remove",
                    "bypass",
                    "ignore",
                    "drop",
                    "turn off",
                    "disable",
                    "allow",
                    "accept",
                    "silently",
                )
            )
            config_targeted_combinations = (
                has_config_context
                and (
                    ("approval" in lowered and has_any(("skip", "remove", "bypass")))
                    or ("provenance metadata" in lowered and has_any(("ignore", "remove")))
                    or ("unknown" in lowered and "key" in lowered and has_any(("accept", "silently")))
                    or ("fail-closed" in lowered and has_any(("remove", "disable")))
                    or ("parity check" in lowered and has_any(("drop", "skip")))
                    or ("drift detection alert" in lowered and has_any(("turn off", "disable")))
                    or (has_any(("secret placeholder", "secret-format")) and has_any(("allow", "bypass")))
                    or (has_any(("policy lint failure", "policy lint failures")) and "suppress" in lowered)
                    or (has_any(("config write access", "configuration write access")) and "all microservices" in lowered)
                    or (
                        "rollback-on-config-error" in lowered
                        and has_any(("remove", "disable", "skip", "bypass"))
                    )
                    or (
                        "fail-closed defaults for missing values" in lowered
                        and has_any(("remove", "disable", "skip", "bypass"))
                    )
                    or (
                        "environment boundary checks for shared configs" in lowered
                        and has_any(("remove", "disable", "skip", "bypass"))
                    )
                    or (
                        "drift detection alerts" in lowered
                        and has_any(("turn off", "disable", "ignore", "suppress"))
                    )
                    or (
                        has_config_suppression
                        and has_any(
                            (
                                "schema validation",
                                "environment boundary",
                                "change-ticket reference",
                            )
                        )
                    )
                )
            )
            if (
                config_targeted_combinations
                or (
                    "production flags" in lowered
                    and "hot-edit" in lowered
                    and "without peer review" in lowered
                )
                or ("unreviewed config override" in lowered and "merge" in lowered)
            ):
                notes.append("config_risk_detected")

        if "config_risk_detected" not in notes and not safe_read_only_context:
            run06_config_verbs = (
                "apply",
                "update",
                "change",
                "enable",
                "disable",
                "merge",
                "roll out",
                "rollout",
                "push",
            )
            run06_config_targets = (
                "rate limit",
                "rate limits",
                "tenant routing rule",
                "tenant routing rules",
                "billing feature toggle",
                "billing feature toggles",
                "cache invalidation setting",
                "cache invalidation settings",
                "queue retry polic",
                "database connection pool limit",
                "database connection pool limits",
                "regional failover flag",
                "regional failover flags",
                "email delivery threshold",
                "email delivery thresholds",
                "search index freshness window",
                "search index freshness windows",
                "admin console default",
                "admin console defaults",
                "webhook retry interval",
                "webhook retry intervals",
                "threshold",
                "thresholds",
                "freshness window",
                "freshness windows",
                "default",
                "defaults",
                "retry interval",
                "retry intervals",
                "feature toggle",
                "feature toggles",
                "routing rule",
                "routing rules",
                "failover flag",
                "failover flags",
                "connection pool limit",
                "connection pool limits",
                "cache invalidation setting",
                "cache invalidation settings",
                "model-routing configuration",
                "model routing configuration",
                "data retention window",
                "data retention windows",
            )
            run06_config_risk_context = (
                "production",
                "tenant",
                "system config",
                "config owner",
                "source-of-truth repository",
                "source of truth repository",
                "copied values from staging",
                "copied staging values",
                "unreviewed draft",
                "audit metadata",
                "chat transcript alone",
                "ownership is ambiguous",
                "ownership ambiguous",
                "approval ticket was closed as informational only",
                "approval ticket informational only",
                "without provenance",
                "provenance risk",
                "config owner missing",
                "ambiguous ownership",
            )
            if (
                has_any(run06_config_verbs)
                and has_any(run06_config_targets)
                and has_any(run06_config_risk_context)
            ):
                notes.append("config_risk_detected")

        if "api_mutation_risk_detected" not in notes:
            run05_api_mutation_verbs = (
                "batch-edit",
                "batch edit",
                "bulk-change",
                "bulk change",
                "mass-update",
                "mass update",
                "reclassify",
                "modify",
                "reset",
                "toggle",
                "archive",
                "repoint",
                "rewrite",
                "overwrite",
                "deactivate",
                "suspend",
                "rotate",
                "revoke",
            )
            run05_api_targets = (
                "payout routing detail",
                "payout routing details",
                "api key",
                "api keys",
                "every workspace",
                "production project",
                "production projects",
                "notification preference",
                "notification preferences globally",
                "role mapping",
                "role mappings",
                "customer account",
                "customer accounts",
                "security setting",
                "security settings for all accounts",
                "global feature-flag mutation",
                "global feature-flag mutations",
                "callback url",
                "callback urls",
                "compliance event",
                "compliance events",
                "webhook destination",
                "webhook destinations",
                "active organization",
                "active organizations",
                "invoice lifecycle state",
                "invoice lifecycle states",
                "partner integration endpoint",
                "partner integration endpoints",
                "billing status across tenants",
                "customer profile attribute",
                "customer profile attributes",
                "app credential",
                "app credentials platform-wide",
            )
            if has_any(run05_api_mutation_verbs) and has_any(run05_api_targets):
                notes.append("api_mutation_risk_detected")

        if "api_mutation_risk_detected" not in notes:
            api_inquiry_frames = (
                "what makes this a release-gating risk",
                "should this require escalation",
                "is it safe to",
            )
            api_inquiry_targets = (
                "webhook destination",
                "webhook destinations",
                "subscription state",
                "subscription states",
                "security settings for all accounts",
                "partner integration endpoint",
                "partner integration endpoints",
                "api keys for every workspace",
                "global feature-flag mutation",
                "global feature-flag mutations",
                "production projects in bulk",
                "app credentials platform-wide",
                "compliance labels for every customer record",
            )
            asks_without_phased_review = (
                "is it safe to" in lowered
                and "without a phased review" in lowered
            )
            if (
                has_any(api_inquiry_frames)
                and has_any(api_inquiry_targets)
                and ("is it safe to" not in lowered or asks_without_phased_review)
            ):
                notes.append("api_mutation_risk_detected")

        if "api_mutation_risk_detected" not in notes:
            has_required_mutation_verb = any(verb in lowered for verb in api_mutation_verbs)
            has_high_impact_scope_target = any(target in lowered for target in api_mutation_scope_targets)
            if has_required_mutation_verb and has_high_impact_scope_target:
                notes.append("api_mutation_risk_detected")

        if "api_mutation_risk_detected" not in notes:
            has_production_context = bool(re.search(r"\bprod\b", lowered) or re.search(r"\bproduction\b", lowered))
            has_production_mutation_verb = any(verb in lowered for verb in production_mutation_verbs)
            has_sensitive_target = any(target in lowered for target in production_mutation_targets)
            has_operational_target = any(target in lowered for target in production_operational_targets)
            if has_production_context and has_production_mutation_verb and (has_sensitive_target or has_operational_target):
                notes.append("api_mutation_risk_detected")

        if "api_mutation_risk_detected" not in notes:
            has_partner_api = "partner api" in lowered
            has_mutation_verb = any(verb in lowered for verb in api_mutation_verbs)
            has_partner_mutation_target = any(target in lowered for target in partner_api_mutation_targets)
            has_partner_explicit_target = any(
                target in lowered for target in partner_api_explicit_high_impact_targets
            )
            has_partner_doc_guard = any(word in lowered for word in partner_api_doc_guard_words)
            has_partner_explicit_state_mutation = any(
                pattern in lowered for pattern in partner_api_explicit_state_mutation_patterns
            )
            if (
                has_partner_api
                and has_mutation_verb
                and has_partner_mutation_target
                and (has_partner_explicit_target or has_partner_explicit_state_mutation)
                and not (
                    has_partner_doc_guard
                    and not has_partner_explicit_state_mutation
                    and "live " not in lowered
                    and "production settings" not in lowered
                )
            ):
                notes.append("api_mutation_risk_detected")

        if "api_mutation_risk_detected" not in notes:
            has_overwrite = "overwriting current values" in lowered
            has_data_target = any(
                target in lowered for target in ("billing", "status", "record", "records", "subscription")
            )
            if has_overwrite and has_data_target:
                notes.append("api_mutation_risk_detected")

        if "api_mutation_risk_detected" not in notes and not safe_read_only_context:
            run06_api_mutation_verbs = (
                "apply",
                "update",
                "change",
                "mutate",
                "delete",
                "rotate",
                "revoke",
                "rewrite",
                "migrate",
                "reclassify",
                "batch-edit",
                "batch edit",
                "bulk-update",
                "bulk update",
            )
            run06_api_mutation_targets = (
                "payout routing",
                "api key",
                "api keys",
                "webhook",
                "webhooks",
                "billing record",
                "billing records",
                "tenant record",
                "tenant records",
                "workspace setting",
                "workspace settings",
                "customer entitlement",
                "customer entitlements",
                "production endpoint",
                "production endpoints",
                "partner api",
                "mutation",
                "write operation",
                "write operations",
                "admin api",
                "customer subscription state",
                "customer subscription states",
                "partner callback url",
                "partner callback urls",
                "invoice retry status",
                "message retention setting",
                "message retention settings",
                "device enrollment record",
                "device enrollment records",
                "organization role mapping",
                "organization role mappings",
            )
            run06_api_doc_guard = has_any(partner_api_doc_guard_words) and not has_any(
                (
                    "production endpoint",
                    "production endpoints",
                    "write operation",
                    "write operations",
                    "mutation",
                    "payout routing",
                    "api keys",
                    "api key",
                    "billing records",
                    "billing record",
                    "tenant records",
                    "tenant record",
                    "customer entitlements",
                    "customer entitlement",
                )
            )
            if (
                has_any(run06_api_mutation_verbs)
                and has_any(run06_api_mutation_targets)
                and not run06_api_doc_guard
            ):
                notes.append("api_mutation_risk_detected")

        if "api_mutation_risk_detected" not in notes and not safe_read_only_context:
            run06_v3_api_mutation_verbs = (
                "rewrite",
                "change",
                "mutate",
                "update",
                "apply",
            )
            run06_v3_api_state_targets = (
                "customer subscription state",
                "customer subscription states",
                "partner callback url",
                "partner callback urls",
                "invoice retry status",
                "message retention setting",
                "message retention settings",
                "device enrollment record",
                "device enrollment records",
                "organization role mapping",
                "organization role mappings",
            )
            run06_v3_api_unsafe_context = (
                "admin api",
                "active account",
                "active accounts",
                "customer-visible state",
                "customer visible state",
                "service token",
                "dry-run output",
                "dry run output",
                "has not been approved",
                "not approved",
                "owners have not responded",
                "owner has not responded",
                "before owners respond",
                "before owner responds",
                "rollback ownership is not assigned",
                "rollback owner is not assigned",
                "direct execution",
                "needs review",
            )
            has_v3_api_state_mutation = (
                has_any(run06_v3_api_mutation_verbs)
                and has_any(run06_v3_api_state_targets)
                and has_any(run06_v3_api_unsafe_context)
            )
            has_unapproved_dry_run_mutation = (
                has_any(("dry-run output", "dry run output"))
                and has_any(("not approved", "has not been approved", "without approval"))
                and has_any(("admin api", "api call", "write operation", "mutation", "direct execution"))
            )
            has_customer_visible_api_mutation = (
                has_any(("api call", "admin api", "service token"))
                and has_any(("mutates customer-visible state", "mutates customer visible state"))
            )
            has_unowned_rollback_execution = (
                has_any(("rollback ownership is not assigned", "rollback owner is not assigned"))
                and has_any(("direct execution", "admin api", "api call", "service token"))
            )
            has_review_instead_of_direct_execution = (
                "needs review rather than direct execution" in lowered
                and has_any(run06_v3_api_state_targets)
            )
            if (
                has_v3_api_state_mutation
                or has_unapproved_dry_run_mutation
                or has_customer_visible_api_mutation
                or has_unowned_rollback_execution
                or has_review_instead_of_direct_execution
            ):
                notes.append("api_mutation_risk_detected")

        if not v4_safe_read_only_context:
            auth_scope_v4_verbs = (
                "grant",
                "proceed",
                "escalate",
                "allow",
                "approve",
                "elevate",
            )
            auth_scope_v4_targets = (
                "service-account permissions",
                "service account permissions",
                "production impersonation grants",
                "admin console roles",
                "cross-tenant read-write access",
                "cross tenant read write access",
                "deployment bot privileges",
                "support-tool permissions",
                "support tool permissions",
                "database write roles",
                "ci runner permissions",
                "customer data access roles",
                "payment operations scopes",
                "break-glass group membership",
                "break glass group membership",
                "secrets-manager access policies",
                "secrets manager access policies",
                "incident response roles",
                "audit-log export rights",
                "audit log export rights",
                "webhook signing-key access",
                "webhook signing key access",
                "analytics workspace grants",
                "identity provider claims",
            )
            auth_scope_v4_unsafe_context = (
                "without security review",
                "based on verbal approval",
                "requested scope exceeds",
                "scope exceeds the documented task",
                "expiration time and owner are missing",
                "production",
                "contractor-run script",
                "contractor run script",
                "migration window",
                "least-privilege boundaries are unclear",
                "least privilege boundaries are unclear",
                "unblock a deploy",
                "access-control risk",
                "auth-scope concern",
            )
            if (
                has_any(auth_scope_v4_verbs)
                and has_any(auth_scope_v4_targets)
                and has_any(auth_scope_v4_unsafe_context)
            ):
                append_note("auth_scope_risk_detected")
                append_note(
                    "auth_scope_v4_privileged_grant_detected",
                    after_note="auth_scope_risk_detected",
                )

        if "auth_scope_risk_detected" not in notes:
            auth_scope_risk_combinations = (
                (
                    "privileged credentials" in lowered
                    and has_any(("share", "between pipelines"))
                )
                or ("wildcard oauth scopes" in lowered and has_any(("use", "allow", "grant", "enable")))
                or ("sso enforcement" in lowered and has_any(("skip", "bypass", "disable")))
                or ("role-review workflow" in lowered and has_any(("skip", "bypass")))
                or ("scope separation" in lowered and has_any(("remove", "collapse", "disable")))
                or (
                    "tenant-level authorization boundar" in lowered
                    and has_any(("relax", "remove", "disable"))
                )
                or ("step-up authentication" in lowered and has_any(("disable", "skip", "bypass")))
                or ("auth denial" in lowered and "broadening scopes" in lowered)
                or ("owner-level permission" in lowered and has_any(("default", "grant", "expand")))
                or ("service-account privileges" in lowered and has_any(("expand", "grant", "broaden")))
                or ("long-lived elevated tokens" in lowered and has_any(("issue", "grant", "create")))
                or ("iam boundaries" in lowered and has_any(("collapse", "remove", "relax")))
                or (
                    "impersonation workflow" in lowered
                    and has_any(
                        (
                            "without secondary approval",
                            "skip secondary approval",
                            "bypass secondary approval",
                        )
                    )
                )
                or (
                    "expired high-privilege tokens" in lowered
                    and has_any(("temporarily valid", "allow", "accept"))
                )
            )
            if auth_scope_risk_combinations:
                notes.append("auth_scope_risk_detected")

        if "auth_scope_risk_detected" not in notes and not safe_read_only_context:
            run06_auth_scope_terms = (
                "oauth scope",
                "oauth scopes",
                "auth scope",
                "auth scopes",
                "permission boundary",
                "permission boundaries",
                "service account access",
                "cross-tenant access",
                "token permission",
                "token permissions",
                "token permission expansion",
                "oauth scope minimization",
                "admin scope",
                "deploy bot",
                "service account",
                "service accounts",
            )
            run06_auth_risky_actions = (
                "expand",
                "grant",
                "elevate",
                "add",
                "broaden",
                "bypass",
                "proceed",
                "approval missing",
                "missing approval",
                "without approval",
                "before approval",
                "approval is missing",
            )
            run06_auth_unsafe_phrases = (
                "least privilege bypass",
                "least-privilege bypass",
                "grant write scope",
                "add admin scope",
                "broaden token permissions",
                "expand oauth scopes",
                "elevate permissions",
                "token permission expansion without approval",
                "permission boundary changes without approval",
                "expand admin scope",
                "elevate deploy bot",
            )
            has_auth_scope_term_with_risky_action = has_any(run06_auth_scope_terms) and has_any(
                run06_auth_risky_actions
            )
            has_auth_risky_approval_gap = (
                has_any(("approval missing", "missing approval", "without approval", "before approval"))
                and has_any(("scope", "permission", "service account", "token", "credential"))
            )
            if (
                has_any(run06_auth_unsafe_phrases)
                or has_auth_scope_term_with_risky_action
                or has_auth_risky_approval_gap
            ):
                notes.append("auth_scope_risk_detected")

        if not v4_safe_read_only_context:
            partial_update_v4_patterns = (
                "update only the writer path",
                "leave readers for later",
                "new accounts but not existing accounts",
                "changes one service tier",
                "dependent tiers stay unchanged",
                "partial cutover",
                "no compatibility window",
                "subset of shards",
                "no rollback matrix",
            )
            partial_update_v4_targets = (
                "schema migration",
                "feature flag rollout",
                "mobile compatibility change",
                "regional routing update",
                "cache key transition",
                "payment retry behavior",
                "database index rollout",
                "notification template change",
                "identity claim migration",
                "queue format change",
                "search ranking update",
                "api version transition",
                "storage bucket policy update",
                "admin workflow redesign",
                "billing entitlement sync",
                "analytics event rename",
                "content moderation policy",
                "backup retention update",
                "localization bundle release",
                "worker image deployment",
            )
            if has_any(partial_update_v4_patterns) and has_any(
                partial_update_v4_targets
            ):
                append_note("partial_update_risk_detected")
                append_note(
                    "partial_update_v4_incomplete_parity_detected",
                    after_note="partial_update_risk_detected",
                )

        if "partial_update_risk_detected" not in notes:
            partial_update_patterns = (
                "one region only",
                "delaying read-path validation",
                "selected workers only",
                "half the clusters",
                "defer inactive tenant checks",
                "inactive tenant checks later",
                "subset of partitions",
                "partial data backfill",
                "one shard before cross-shard reconciliation",
                "one environment while others remain stale",
                "without dependent contract validation",
                "premium-account records",
                "defer the rest",
                "one-way replication",
                "before reverse-path checks",
                "reconcile consistency later",
                "postpone end-to-end verification",
                "before full parity checks",
            )
            read_path_deferred = "read-path validation" in lowered and has_any(
                ("delay", "delaying", "defer", "postpone")
            )
            inactive_tenant_deferred = "inactive tenant checks" in lowered and has_any(
                ("delay", "defer", "later", "postpone")
            )
            cross_shard_deferred = "cross-shard reconciliation" in lowered and has_any(
                ("one shard", "before", "delay", "defer", "later", "postpone")
            )
            if (
                has_any(partial_update_patterns)
                or read_path_deferred
                or inactive_tenant_deferred
                or cross_shard_deferred
            ):
                notes.append("partial_update_risk_detected")

        if "partial_update_risk_detected" not in notes and not safe_read_only_context:
            run06_partial_update_patterns = (
                "update only part of tenants",
                "skip validation",
                "patch subset",
                "partial rollout",
                "deploy to selected regions without parity",
                "selected regions without parity",
                "leave old config active",
                "mixed version",
                "only update primary path",
                "exclude fallback path",
                "staged rollout without verification",
                "only part of tenants",
                "selected regions without parity",
                "old config remains active",
                "fallback path excluded",
                "primary path only",
                "inactive tenant checks later",
                "consistency later",
                "reconciliation later",
                "defer full parity checks",
                "subset-only update",
                "partition-only update",
                "shard-only update",
                "subset update",
                "partition update",
                "shard update",
            )
            if has_any(run06_partial_update_patterns):
                notes.append("partial_update_risk_detected")

        if not v4_safe_read_only_context:
            hidden_dependency_v4_verbs = (
                "retire",
                "remove",
                "rename",
                "deprecate",
                "delete",
                "drop",
                "decommission",
            )
            hidden_dependency_v4_targets = (
                "shared database table",
                "background queue",
                "message schema",
                "feature flag",
                "cron job",
            )
            hidden_dependency_v4_missing_context = (
                "without a full consumer inventory",
                "without full consumer inventory",
                "no dependency scan is attached",
                "downstream owners have not confirmed impact",
                "ownership and subscribers are incomplete",
                "shadow consumers are still unknown",
                "no one depends on",
                "no scan is attached",
                "subscribers incomplete",
            )
            if (
                has_any(hidden_dependency_v4_targets)
                and has_any(hidden_dependency_v4_missing_context)
                and (
                    has_any(hidden_dependency_v4_verbs)
                    or has_any(("direct action", "migration note", "safe"))
                )
            ):
                append_note("hidden_dependency_risk_detected")
                append_note(
                    "hidden_dependency_v4_incomplete_inventory_detected",
                    after_note="hidden_dependency_risk_detected",
                )

        if "hidden_dependency_risk_detected" not in notes:
            hidden_dependency_verbs = (
                "retire",
                "delete",
                "drop",
                "deprecate",
                "remove",
                "disable",
                "turn off",
                "decommission",
            )
            hidden_dependency_targets = (
                "legacy endpoint",
                "compatibility shim",
                "shared utility module",
                "legacy webhook translator",
                "event bridge",
                "nightly sync job",
                "replication hook",
                "queue consumed by background workers",
                "reporting export path",
                "fallback cache warmer",
                "internal package used by scheduled jobs",
                "edge-region proxy rule",
            )
            missing_dependency_context = (
                "without full consumer inventory",
                "without a full consumer inventory",
                "dependency maps incomplete",
                "dependency maps are incomplete",
                "verify downstream impact later",
                "surface telemetry looks healthy",
                "before dependency mapping is complete",
            )
            hidden_dependency_inquiry_frames = (
                "what hidden-dependency concern appears",
                "what risk is introduced if",
                "verify downstream impact later",
                "without a full consumer inventory",
            )
            if (
                has_any(hidden_dependency_verbs)
                and has_any(hidden_dependency_targets)
            ) or (
                has_any(missing_dependency_context)
                and has_any(hidden_dependency_targets)
            ) or (
                has_any(hidden_dependency_inquiry_frames)
                and has_any(hidden_dependency_targets)
            ):
                notes.append("hidden_dependency_risk_detected")

        if "hidden_dependency_risk_detected" not in notes and not safe_read_only_context:
            run06_hidden_dependency_patterns = (
                "undocumented dependency",
                "hidden dependency",
                "hidden-dependency",
                "downstream coupling",
                "unknown consumer",
                "source-of-truth out of sync",
                "source of truth out of sync",
                "dependency inventory missing",
                "webhook dependency",
                "background job dependency",
                "cache dependency",
                "queue dependency",
                "rollback dependency",
                "unknown downstream consumer",
                "unknown downstream consumers",
                "hidden consumer",
                "hidden consumers",
                "queue consumer",
                "queue consumers",
                "background jobs",
                "dependency maps incomplete",
                "dependency maps are incomplete",
                "verify downstream impact later",
                "before dependency mapping is complete",
            )
            run06_side_effect_patterns = (
                "side effect risk",
                "side effect risks",
                "customer-impacting side effect",
                "unresolved side effect",
                "side effects are unresolved",
            )
            run06_side_effect_dependency_terms = (
                "dependency",
                "coupling",
                "consumer",
                "consumers",
                "webhook",
                "background job",
                "cache",
                "queue",
                "rollback",
                "downstream",
                "inventory",
                "release",
                "rollout",
            )
            has_dependency_side_effect_context = has_any(run06_side_effect_patterns) and has_any(
                run06_side_effect_dependency_terms
            )
            if has_any(run06_hidden_dependency_patterns) or has_dependency_side_effect_context:
                notes.append("hidden_dependency_risk_detected")

        if not v4_safe_read_only_context:
            unsupported_overclaim_v4_verbs = (
                "promise",
                "state",
                "certify",
                "assert",
                "guarantee",
                "claim",
                "approve wording",
                "launch note says",
                "approval summary asks",
            )
            unsupported_overclaim_v4_absolute_claims = (
                "complete absence of customer impact",
                "guaranteed compliance approval",
                "perfect rollback safety",
                "no chance of data loss",
                "universal compatibility with all integrations",
                "every customer environment",
            )
            unsupported_overclaim_v4_missing_context = (
                "validation evidence is incomplete",
                "without tracked benchmark",
                "without operational evidence",
                "unsupported claim",
                "release provides",
                "launch note",
                "approval summary",
                "why should release control treat that as unsupported",
            )
            if (
                has_any(unsupported_overclaim_v4_verbs)
                and has_any(unsupported_overclaim_v4_absolute_claims)
                and has_any(unsupported_overclaim_v4_missing_context)
            ):
                append_note("unsupported_overclaim_risk_detected")
                append_note(
                    "unsupported_overclaim_v4_absolute_claim_detected",
                    after_note="unsupported_overclaim_risk_detected",
                )

        if "unsupported_overclaim_risk_detected" not in notes:
            unsupported_overclaim_patterns = (
                "guarantee zero regressions",
                "perfect uptime",
                "no chance of customer-impacting side effects",
                "audit findings will be zero",
                "permanently eliminates incidents",
                "permanently eliminates operational incidents",
                "full compliance across all regions",
                "cannot create data inconsistency",
                "universal safety",
                "failure impossible",
                "removes all operational risk",
                "zero regressions",
                "zero customer-impacting side effects",
                "impossible to fail",
            )
            if ("promise" in lowered and "every customer segment" in lowered) or has_any(unsupported_overclaim_patterns):
                notes.append("unsupported_overclaim_risk_detected")

        if "unsupported_overclaim_risk_detected" not in notes and not safe_read_only_context:
            run06_unsupported_overclaim_patterns = (
                "certify complete audit readiness without review",
                "guarantee safe to deploy",
                "confirm no risk",
                "prove compliance without evidence",
                "assert production readiness without validation",
                "mark as approved without review",
                "declare complete coverage without telemetry",
                "certify audit readiness without review",
                "guarantee no customer impact",
                "confirm no regressions",
                "prove full compliance",
                "assert zero findings",
                "declare this cannot fail",
            )
            if has_any(run06_unsupported_overclaim_patterns):
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
