---
name: score-study-dual-axis
description: 'Horizontal pass (narrative arc) plus vertical pass (parallel considerations at each step). Synthesize output satisfying both. Use for complex analysis and long-form reasoning. Scope boundary: dependency DAG → `proof-trees-reasoning`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: dual axis; horizontal vertical; score study; narrative arc. Also /score-study-dual-axis.'
argument-hint: /score-study-dual-axis task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Horizontal pass (narrative arc) plus vertical pass (parallel considerations at each step)
  host: grok-build
  ported_from: Cursor_Skills
---
# Score study dual-axis reasoning

**#10** · **Domain:** Classical conducting · **Category:** architecture · **Difficulty:** 🟡 Medium

## Core principle

Read vertically (simultaneous voices) and horizontally (time) before conducting.

## AI problem addressed

Linear prose is organized OR thorough, rarely both.

## Implementation

1. Horizontal: map argument arc start→finish
2. Vertical: at each step list audience, constraints, edge cases, tone
3. Generate satisfying both axes
4. Check: flows horizontally? complete vertically at each step?

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-architecture`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `score_study`
