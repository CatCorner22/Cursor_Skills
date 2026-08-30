---
name: seismic-flexibility
disable-model-invocation: true
description: "Insert modular joints (paragraph/section seams) so a later edit does not collapse the whole piece. Use on long docs that will be revised. Scope boundary — warp/weft threads → `weaving-warp-weft`; load-bearing claims stay tagged → `load-bearing-structure`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "seismic flexibility"
      - "modular joints"
      - "edit without collapse"
    minScore: 6
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
