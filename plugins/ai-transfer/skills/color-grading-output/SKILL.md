---
name: color-grading-output
description: 'Grade pass on luminance (information density), chroma (emotional intensity), hue (stance consistency). Use for tone/ clarity review of drafts. Scope boundary: faceting passes → `gemstone-faceting-refinement`.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
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
