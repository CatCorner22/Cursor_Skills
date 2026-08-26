---
name: survey-triangulation
description: "Require three independent retrieval paths per factual claim; score agreement 3/3, 2/3, or contested. Use when single-source RAG is insufficient. Scope boundary: double-entry gate → `double-entry-claims`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "triangulation"
      - "cross validate sources"
      - "three sources"
    minScore: 6
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
