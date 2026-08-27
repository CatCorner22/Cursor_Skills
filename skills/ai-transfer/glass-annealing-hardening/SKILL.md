---
name: glass-annealing-hardening
description: "Staged delivery: high temp (everything flexible) → medium (structure locked) → cool (typos only). Use for long documents and multi-pass review. Scope boundary: faceting angles → `gemstone-faceting-refinement`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "annealing"
      - "staged delivery"
      - "cooling phases"
      - "lock structure"
    minScore: 6
---

# Glass annealing output hardening

**#21** · **Domain:** Glassblowing · **Category:** adaptive · **Difficulty:** 🟡 Medium

## Core principle

Gradual cooling resolves internal stress — fast cool shatters.

## AI problem addressed

Hot delivery commits to flawed structure early.

## Implementation

| Temp | Locked | Flexible |
| High | Nothing | Structure, content |
| Medium | Major structure | Wording, examples |
| Cool | All content | Typos, format only |

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-adaptive`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `glass_anneal`
