---
name: stratigraphy-memory
disable-model-invocation: true
description: "Layer memory by session strata plus disturbance markers; retrieve with integrity confidence. Use for long-horizon agents. Scope boundary: flat RAG → `library-taxonomy-retrieval`; cross-session bridges → `wildlife-corridor-bridging`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "stratigraphy memory"
      - "temporal layers"
      - "session strata"
    minScore: 6
---
# Archaeological stratigraphy memory

**#22** · **Domain:** Archaeology · **Category:** memory · **Difficulty:** 🔴 High

## Core principle

Deeper layers older; disturbances mix strata — cross-reference before trusting.

## AI problem addressed

Flat embedding loses temporal depth and context shifts.

## Implementation

1. Identify relevant stratum (session cluster)
2. Check disturbance markers (tool break, constraint change)
3. Cross-reference adjacent strata
4. Return memory with confidence from stratigraphic integrity

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-memory`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `stratigraphy`
- Also implements: `paleontology`
- Merge notes: Also absorbs `paleontology`: fossil snapshots of retired configs.
