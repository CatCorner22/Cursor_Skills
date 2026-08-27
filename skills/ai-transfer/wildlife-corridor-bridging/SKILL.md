---
name: wildlife-corridor-bridging
disable-model-invocation: true
description: "Detect topic overlap across sessions; inject bridge summaries connecting isolated context islands. Use for long-term personal agents. Scope boundary: strata layers → `stratigraphy-memory`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "memory bridge"
      - "cross session"
      - "conceptual corridor"
    minScore: 6
---

# Wildlife corridor memory bridging

**#25** · **Domain:** Conservation biology · **Category:** memory · **Difficulty:** 🔴 High

## Core principle

Habitats need corridors — not isolated pockets.

## AI problem addressed

Each conversation is an island despite conceptual overlap.

## Implementation

1. Detect overlap current ↔ historical sessions
2. Generate bridge: 'Three weeks ago you X; connection to today Y'
3. Inject bridge into active context

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-memory`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `corridor_bridge`
