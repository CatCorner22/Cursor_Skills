---
name: seismic-flexibility
description: Insert modular joints (paragraph/section seams) so a later edit does not collapse the whole piece. Use on long docs that will be revised. Scope boundary — warp/weft threads → `weaving-warp-weft`; load-bearing claims stay tagged → `load-bearing-structure`.
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: seismic flexibility; modular joints; edit without collapse. Also /seismic-flexibility.'
argument-hint: /seismic-flexibility task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Insert modular joints (paragraph/section seams) so a later edit does not collapse the whole piece
  host: grok-build
  ported_from: Cursor_Skills
---
# Seismic flexibility joints

**#43** · **Domain:** Earthquake engineering · **Category:** advanced · **Difficulty:** 🟡 Medium

## Core principle

Buildings that sway at the joints survive; rigid boxes crack.

## AI problem addressed

Tightly coupled prose means one paragraph rewrite breaks five others.

## Implementation

Split on blank lines. Each module must stand if neighbors are deleted.
Prefer more short modules over one welded block. Score flexibility by module count.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-advanced`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `seismic_flexibility`
