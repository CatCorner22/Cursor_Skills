---
name: survey-triangulation
description: 'Require three independent retrieval paths per factual claim; score agreement 3/3, 2/3, or contested. Use when single-source RAG is insufficient. Scope boundary: double-entry gate → `double-entry-claims`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: triangulation; cross validate sources; three sources. Also /survey-triangulation.'
argument-hint: /survey-triangulation task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Require three independent retrieval paths per factual claim; score agreement 3/3, 2/3, or contested
  host: grok-build
  ported_from: Cursor_Skills
---
# Survey triangulation validation

**#8** · **Domain:** Land surveying · **Category:** quality-control · **Difficulty:** 🟡 Medium

## Core principle

Never trust one measurement — intersect from three known positions.

## AI problem addressed

Top-ranked single source and echo chambers create false confidence.

## Implementation

| Agreement | Action |
| 3/3 | Include, cite all three |
| 2/3 | Include with caveat, flag outlier |
| Contested | Label disputed explicitly |
Use different queries, source types, and time snapshots.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-quality-control`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `triangulation_validator`
- Also implements: `fact_check_deep`
- Merge notes: Deep fact-check is this skill plus `double-entry-claims`, not a third skill.
