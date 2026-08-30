---
name: stage-blocking-layout
description: 'Spatial emphasis: center stage = core message; flanks = evidence; opposing entrances = dialectic; center curtain = synthesis. Use for reports, docs, and structured responses. Scope boundary: warp/weft structure → `weaving-warp-weft`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: stage blocking; information layout; spatial emphasis. Also /stage-blocking-layout.'
argument-hint: /stage-blocking-layout task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Spatial emphasis: center stage = core message; flanks = evidence; opposing entrances = dialectic; center curtain = synthesis'
  host: grok-build
  ported_from: Cursor_Skills
---
# Stage blocking information layout

**#15** · **Domain:** Theater direction · **Category:** architecture · **Difficulty:** 🟡 Medium

## Core principle

Position conveys emphasis — not only bold text.

## AI problem addressed

Sequential dump with no spatial architecture.

## Implementation

Map sections: opening center (thesis) → flanks (evidence) → opposing sides (tension) → center close (synthesis)
Translate to headers, sidebars, footnotes, callouts.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-architecture`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `spatial_layout`
