---
name: proof-trees-reasoning
description: 'Declare reasoning DAG before prose: premises, claims, dependencies. Flag downstream if upstream fails. Use for multi-step arguments and agent plans. Scope boundary: dual-axis → `score-study-dual-axis`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: proof tree; reasoning DAG; dependency graph. Also /proof-trees-reasoning.'
argument-hint: /proof-trees-reasoning task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Declare reasoning DAG before prose: premises, claims, dependencies'
  host: grok-build
  ported_from: Cursor_Skills
---
# Proof trees (reasoning DAG)

**#12** · **Domain:** Mathematics · **Category:** architecture · **Difficulty:** 🔴 High

## Core principle

Explicit dependencies — if a premise fails, downstream collapses visibly.

## AI problem addressed

Prose hides dependencies; step 3 error poisons 4–9 invisibly.

## Implementation

Declare: Premise P1, P2 → Claim A(P1,P2) → Claim B(A,P3) → Conclusion C(B)
Generate prose following DAG only.
Self-check: weakest premise? Downstream auto-flag if premise fails.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-architecture`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `proof_trees`
- Also implements: `scientific_method`
- Merge notes: Scientific-method plugin is this DAG, not a separate skill.
