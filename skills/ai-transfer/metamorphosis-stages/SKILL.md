---
name: metamorphosis-stages
description: "Force larva (brainstorm) → pupa (structure) → adult (polish) as separate artifacts. Use instead of polishing a first dump. Scope boundary — annealing lock temperatures → `glass-annealing-hardening`; faceting angles → `gemstone-faceting-refinement`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "metamorphosis stages"
      - "larva pupa adult"
      - "staged draft evolution"
    minScore: 6
---

# Metamorphosis staged drafts

**#40** · **Domain:** Developmental biology · **Category:** extension · **Difficulty:** 🟡 Medium

## Core principle

The adult is not a prettier larva — each instar has different work.

## AI problem addressed

One-pass generation tries to invent, outline, and polish together.

## Implementation

Larva: raw points, no headings
Pupa: section the points
Adult: strip scaffolding notes, keep structure
Do not skip a stage on long work.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-extension`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `metamorphosis`
