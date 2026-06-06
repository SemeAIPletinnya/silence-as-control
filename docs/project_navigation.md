# Project Navigation Map

## Purpose

This file helps readers choose the right entry point without mixing the roles of the README, docs, issues, evidence, roadmap, and integration material.

## High-level map

```text
README
  ├─ Quick entry / project thesis
  ├─ Plain-English pitch
  ├─ Start here
  └─ Quick public links

docs/
  ├─ plain_english_pitch.md          ← explain simply
  ├─ first_run_checklist.md          ← verify locally
  ├─ architecture.md                 ← core/runtime/experimental split
  ├─ agentic_release_control.md      ← agentic release-control layer
  ├─ evidence_map.md                 ← claims → artifacts
  ├─ evidence_graph.md               ← compact claim topology
  ├─ chronology.md                   ← project evolution timeline
  ├─ runtime_evidence_linkage.md     ← runtime/replay evidence links
  ├─ release_risk_benchmark_index.md ← release-risk benchmark lineage
  ├─ release_risk_v4_capture_to_replay.md ← v4 no-key capture/replay path
  ├─ external_reviewer_packet.md     ← external technical review packet
  ├─ reviewer_console_guide.md       ← standalone reviewer console usage
  ├─ builder_integration_guide.md    ← app/agent/workflow integration guide
  ├─ pilot_evaluation_packet.md      ← bounded pilot evaluation path
  ├─ pilot_case_log_template.md       ← bounded pilot case logging
  ├─ runtime_observability.md        ← telemetry verification
  ├─ review_release_receipt_layer.md ← future receipt/audit design note
  ├─ provider_configuration.md       ← API/provider setup
  ├─ release_control_services.md     ← pilot/integration interest
  └─ roadmap_2026.md                 ← milestone planning

issues/
  ├─ #202 memory capsule
  └─ #203 roadmap/progress/dependency capsule
```

## Start depending on what you need

| Need | Start here |
| --- | --- |
| Understand the idea simply | [Plain-English pitch](plain_english_pitch.md) |
| Verify the project locally without keys | [First-run checklist](first_run_checklist.md) |
| Understand the architecture split | [Architecture](architecture.md) |
| Understand agentic release-control | [Agentic release-control](agentic_release_control.md) |
| Check claims and artifacts | [Evidence map](evidence_map.md) |
| Follow release-risk benchmark lineage | [Release-risk benchmark index](release_risk_benchmark_index.md) |
| Reproduce the v4 no-key capture/replay path | [Release-risk v4 capture-to-replay](release_risk_v4_capture_to_replay.md) |
| Review as an external technical reader | [External reviewer packet](external_reviewer_packet.md) |
| Try the standalone reviewer console | [Reviewer console guide](reviewer_console_guide.md) and [../examples/sac_reviewer_console.html](../examples/sac_reviewer_console.html) |
| Integrate the release gate into an app/agent/workflow | [Builder integration guide](builder_integration_guide.md) |
| Evaluate a bounded pilot | [Pilot evaluation packet](pilot_evaluation_packet.md) |
| Log pilot cases | [Pilot case log template](pilot_case_log_template.md) |
| Follow project chronology | [Project chronology](chronology.md) |
| Inspect runtime telemetry | [Runtime observability](runtime_observability.md) |
| Understand future review/release receipts | [Review/release receipt layer](review_release_receipt_layer.md) |
| Configure provider-backed completion | [Provider configuration](provider_configuration.md) |
| Understand pilot/integration fit | [Release-control services](release_control_services.md) |
| See milestone planning | [Roadmap 2026](roadmap_2026.md) |
| Recover current project memory | [Issue #202](https://github.com/SemeAIPletinnya/silence-as-control/issues/202) |
| Track roadmap/progress/dependencies | [Issue #203](https://github.com/SemeAIPletinnya/silence-as-control/issues/203) |

## Crystallization / provenance / evidence topology

- [Project chronology](chronology.md)
- [Core primitives](core_primitives.md)
- [Evidence graph](evidence_graph.md)
- [Project crystallization status](project_crystallization_status.md)
- [Runtime evidence linkage](runtime_evidence_linkage.md)
- [Twitter/X archive summary](twitter_archive_summary.md)

## Boundary rules

- README is the front door, not the full documentation.
- Plain-English pitch explains the idea simply.
- First-run checklist verifies the no-key path.
- Evidence map connects claims to artifacts.
- Project chronology tracks evolution over time without replacing evidence docs.
- Roadmap docs and issue #203 track development direction.
- Issue #202 preserves current project state.
- Pilot/integration docs should stay separate from research/evidence docs.
- Do not duplicate large explanations across files.

## Archive / Provenance Layer

- `docs/twitter_archive_summary.md`
  - Curated chronology/provenance summary derived from the long-term Twitter/X archive.
  - Used as a continuity and terminology-evolution reference layer.
