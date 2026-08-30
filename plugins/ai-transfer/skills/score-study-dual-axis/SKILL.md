---
name: score-study-dual-axis
description: 'Horizontal pass (narrative arc) plus vertical pass (parallel considerations at each step). Synthesize output satisfying both. Use for complex analysis and long-form reasoning. Scope boundary: dependency DAG → `proof-trees-reasoning`.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
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
