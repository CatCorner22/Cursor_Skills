---
name: gemstone-faceting-refinement
disable-model-invocation: true
description: "Rotate refinement through clarity, precision, resonance, durability passes — flaws visible from new angles. Use instead of linear draft→revise→done. Scope boundary: annealing phases → `glass-annealing-hardening`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "faceting refinement"
      - "multi angle review"
      - "rotate refinement"
    minScore: 6
---

# Gemstone faceting multi-angle refinement

**#29** · **Domain:** Gemology · **Category:** refinement · **Difficulty:** 🟡 Medium

## Core principle

Each facet angle reveals flaws invisible from the prior view.

## AI problem addressed

Linear refinement misses angle-specific defects.

## Implementation

Pass 1 Clarity: audience understands?
Pass 2 Precision: every word load-bearing?
Pass 3 Resonance: meets actual needs?
Pass 4 Durability: survives scrutiny?
Rotate output between passes.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-refinement`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `gemstone_faceting`
