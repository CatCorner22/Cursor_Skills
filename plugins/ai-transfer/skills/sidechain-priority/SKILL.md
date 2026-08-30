---
name: sidechain-priority
description: When the answer/solution/result arrives, duck the supporting intro so the signal sits on top. Use when preambles bury the payload. Scope boundary — zoom compression → `cartographic-zoom`; dual-axis completeness → `score-study-dual-axis`.
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: sidechain duck; sidechain priority; duck the intro. Also /sidechain-priority.'
argument-hint: /sidechain-priority task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: When the answer/solution/result arrives, duck the supporting intro so the signal sits on top
  host: grok-build
  ported_from: Cursor_Skills
---
# Sidechain priority ducking

**#44** · **Domain:** Audio engineering · **Category:** advanced · **Difficulty:** 🟡 Medium

## Core principle

The kick ducks the bass — the lead signal gets the mask.

## AI problem addressed

Throat-clearing occupies the first screen and the answer is below the fold.

## Implementation

If the draft contains Answer:/Solution:/Result:/Conclusion: after a lead-in,
promote that block and shrink the intro. Do not delete evidence flanks.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-advanced`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `sidechain_duck`
