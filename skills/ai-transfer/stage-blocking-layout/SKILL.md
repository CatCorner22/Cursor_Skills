---
name: stage-blocking-layout
disable-model-invocation: true
description: "Spatial emphasis: center stage = core message; flanks = evidence; opposing entrances = dialectic; center curtain = synthesis. Use for reports, docs, and structured responses. Scope boundary: warp/weft structure → `weaving-warp-weft`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "stage blocking"
      - "information layout"
      - "spatial emphasis"
    minScore: 6
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
