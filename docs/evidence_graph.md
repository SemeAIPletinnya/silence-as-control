# Evidence Graph

This document maps project claims to the smallest available artifacts that support them.

The goal is not to collect every possible reference.
The goal is to keep the project evidence layer inspectable, minimal, and reproducible.

## Evidence model

Each entry should follow this shape:

```text
claim
→ artifact
→ status
→ next evidence gap
```

## Current graph

### generation != release authority

```text
generation != release authority
→ docs/core_primitives.md
→ stable primitive
→ connect to runtime/replay examples
```

### capability != execution authority

```text
capability != execution authority
→ docs/core_primitives.md
→ stable primitive
→ connect to agent/execution mediation examples
```

### memory != persistence authority

```text
memory != persistence authority
→ docs/core_primitives.md
→ stable primitive
→ future memory-admission prototype needed
```

### syntax != operational correctness

```text
syntax != operational correctness
→ docs/core_primitives.md
→ stable primitive
→ connect to release-risk examples
```

### Project chronology exists as a provenance layer

```text
project chronology
→ docs/chronology.md
→ scaffolded provenance layer
→ add curated public/technical milestones later
```

### Claims should connect to artifacts

```text
claims → artifacts
→ docs/evidence_map.md
→ existing evidence orientation
→ keep this graph as the compact claim map
```

## Artifact types

Useful artifact categories:

- documentation
- GitHub issues
- pull requests
- benchmark outputs
- replay logs
- runtime traces
- deployment artifacts
- research notes
- curated public posts

## Boundary rules

- Do not store raw private archives here.
- Do not add large datasets directly to the repository.
- Prefer curated, sanitized, minimal evidence pointers.
- Keep claims narrower than the artifacts supporting them.
- Mark evidence gaps explicitly instead of overclaiming.

## Non-goals

This evidence graph does not claim:

- AGI
- sentience
- consciousness
- universal AI safety
- complete validation of the architecture

It tracks the relationship between runtime-governance claims and supporting artifacts.
