# Core Primitives

This document defines the smallest stable conceptual primitives behind the Silence-as-Control / PoR runtime-governance direction.

The goal is not to maximize scope.
The goal is to preserve the minimal operational boundaries that remain stable across:

- runtime governance
- replay systems
- release-control
- orchestration
- execution mediation
- memory continuity

## Primary primitive

```text
generation != release authority
```

A model or agent may generate a candidate.
A separate runtime layer determines whether that candidate:

- proceeds,
- requires review,
- or is silenced.

## Derived primitives

### Capability != execution authority

```text
capability != execution authority
```

A system being technically capable of an action does not automatically grant permission to execute that action.

## Memory != persistence authority

```text
memory != persistence authority
```

A runtime may generate or mutate memory candidates.
Persistence should remain a separately governed operation.

## Syntax != operational correctness

```text
syntax != operational correctness
```

A syntactically valid output may still be operationally unsafe, misleading, incomplete, or release-ineligible.

## Operational interpretation

The project treats generation as:
- candidate creation

The project treats governance as:
- release mediation
- execution boundaries
- replayability
- runtime evidence
- policy evaluation

## Non-goals

These primitives do not claim:
- AGI
- sentience
- consciousness
- universal AI safety
- autonomous moral reasoning

They define operational runtime boundaries.
