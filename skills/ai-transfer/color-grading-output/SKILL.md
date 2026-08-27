---
name: color-grading-output
description: "Grade pass on luminance (information density), chroma (emotional intensity), hue (stance consistency). Use for tone/ clarity review of drafts. Scope boundary: faceting passes → `gemstone-faceting-refinement`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "color grading"
      - "three axis review"
      - "tone clarity framing"
    minScore: 6
---

# Color grading three-axis refinement

**#26** · **Domain:** Film post-production · **Category:** refinement · **Difficulty:** 🟡 Medium

## Core principle

Adjust density, intensity, and framing independently before final grade.

## AI problem addressed

Fuzzy single-judgment 'sounds good' reviews.

## Implementation

| Axis | Check |
| Luminance / density | Key sections clear; rest appropriately summarized? |
| Chroma / intensity | Energy matched to audience? |
| Hue / stance | Worldview framing consistent? |
Flag imbalances with specific section refs.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-refinement`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `color_grading`
