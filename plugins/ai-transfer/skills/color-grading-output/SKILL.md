---
name: color-grading-output
description: 'Grade pass on luminance (information density), chroma (emotional intensity), hue (stance consistency). Use for tone/ clarity review of drafts. Scope boundary: faceting passes → `gemstone-faceting-refinement`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: color grading; three axis review; tone clarity framing. Also /color-grading-output.'
argument-hint: /color-grading-output task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Grade pass on luminance (information density), chroma (emotional intensity), hue (stance consistency)
  host: grok-build
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
