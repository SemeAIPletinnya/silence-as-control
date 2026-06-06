# Docs Index

You are here: documentation for architecture boundaries and public-facing guidance.

- [Project navigation map](project_navigation.md) — where to start depending on what you need.
- `architecture.md` — core vs runtime vs experimental split.
- `runtime_extensions.md` — optional runtime deployment helpers.
- `experimental_features.md` — optional non-core MAYBE_SHORT_REGEN behavior.
- `api_walkthrough.md` — broader API walkthrough.
- `runtime_observability.md` — local telemetry smoke walkthrough and report shape.
- [Review/release receipt layer](review_release_receipt_layer.md) — conservative future design note for auditable review/release receipts.
- `first_run_checklist.md` — no-key first-run verification path.
- [Direct reproduction guide](direct_reproduction_guide.md) — local commands to verify the no-key release-control path.
- `provider_configuration.md` — no-key vs provider-backed runtime configuration.
- `threshold_regime_contract.md` — scoped threshold interpretation contract for SimpleQA/Ollama evidence.
- `evidence_map.md` — claim-to-artifact navigation for core/runtime/benchmark surfaces.
- `evidence_graph.md` — compact claim-to-artifact topology companion.
- `release_risk_benchmark_index.md` — recommended entry point for v1/v2/v3 release-risk benchmark evidence, artifact lineage, commands, and interpretation boundaries.
- `release_risk_benchmark_report.md` — first deterministic local release-risk benchmark run report.
- `release_risk_v2_benchmark_report.md` — first local fixture-replay run report for release-risk benchmark v2.
- `release_risk_v3_benchmark_report.md` — first local fixture-generation/replay run report for release-risk benchmark v3.
- [Plain-English pitch](plain_english_pitch.md) — a simple explanation of Silence-as-Control for first-time readers.
- [External reviewer packet](external_reviewer_packet.md) — 5-10 minute technical overview for reviewers and builders.
- [Pilot evaluation packet](pilot_evaluation_packet.md) — bounded protocol for evaluating release-control behavior in a pilot.
- [Pilot evaluation template](pilot_evaluation_template.md) — copyable table/log shape for first pilot evaluations.
- [Pilot outreach examples](pilot_outreach_examples.md) — conservative outreach examples for bounded audit and pilot conversations.
- [Builder integration guide](builder_integration_guide.md) — where to place the release gate in an app, agent, RAG, or coding workflow.
- [Integration decision policy examples](integration_decision_policy_examples.md) — examples for handling PROCEED / NEEDS_REVIEW / SILENCE after the release gate.
- `langchain_openai_action_risk_benchmark.md` — LangChain/OpenAI action-risk benchmark framing and Run 06 hardened v4 progression.
- `action_risk_1000_dataset.md` — Run 06 1000-case synthetic dataset scope and schema.
- `release_control_services.md` — pilot/integration overview for release-control use cases.
- `agentic_release_control.md` — deterministic release-control architecture for agentic workflows.
- [Runtime governance stack](runtime_governance_stack.md) — canonical map of the sandbox and release-control governance layers.
- [Governance stack walkthrough](governance_stack_walkthrough.md) — guided walkthrough of the runtime governance stack.
- [Runtime governance visual map](runtime_governance_visual_map.md) — visual-oriented map of governance and release-control layers.
- [Reverse integration sandbox](reverse_integration_sandbox.md) — controlled intake/evaluation concept for external candidate outputs.
- [Sandbox channel adapters](sandbox_channel_adapters.md) — conceptual intake connectors for sandbox evaluation flows.
- [Intake payload schema](intake_payload_schema.md) — conceptual normalization format for sandbox intake evaluation flows.
- [Deterministic replay architecture](deterministic_replay_architecture.md) — conceptual replay and inspection layer for sandbox evaluation flows.
- [Decision provenance architecture](decision_provenance_architecture.md) — conceptual traceability layer for sandbox release decisions.
- [Sandbox evaluation telemetry](sandbox_evaluation_telemetry.md) — conceptual visibility layer for sandbox governance flows.
- [Policy surface architecture](policy_surface_architecture.md) — conceptual policy-aware interpretation layer for sandbox governance flows.
- [Evidence retention architecture](evidence_retention_architecture.md) — conceptual evidence-continuity layer for sandbox governance flows.
- [Evaluation trace architecture](evaluation_trace_architecture.md) — conceptual inspection and traceability layer for sandbox evaluation flows.
- [Review lane architecture](review_lane_architecture.md) — conceptual governance routing layer for sandbox evaluation flows.
- [Connector sandbox boundary](connector_sandbox_boundary.md) — conceptual governance boundary for external communication surfaces.
- `applied_bridges.md` — bounded notes on compatible applied bridges such as `por-copilot-bridge`.

## Crystallization / provenance index

- [Project chronology](chronology.md)
- [Core primitives](core_primitives.md)
- [Evidence graph](evidence_graph.md)
- [Project crystallization status](project_crystallization_status.md)
- [Runtime evidence linkage](runtime_evidence_linkage.md)
- [Twitter/X archive summary](twitter_archive_summary.md)

For paper/preprint context, see `../paper/README.md`.
