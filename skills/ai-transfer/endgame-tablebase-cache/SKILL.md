---
name: endgame-tablebase-cache
disable-model-invocation: true
description: "Pre-compute and cache known-correct answers for recurring boundary conditions; check tablebase before reasoning. Use for boilerplate code, legal clauses, lookup math. Scope boundary: live reasoning → `proof-trees-reasoning`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "tablebase cache"
      - "boundary cache"
      - "known correct cache"
    minScore: 6
---

# Chess endgame tablebase cache

**#23** · **Domain:** Chess computing · **Category:** memory · **Difficulty:** 🟡 Medium

## Core principle

Exhaustive pre-computation for fixed configurations — reuse perfect answers.

## AI problem addressed

Recomputing known-correct edge cases every call.

## Implementation

Maintain tablebase: auth patterns, CRUD, standard clauses, timezone math.
Lookup FIRST; invoke reasoning only on cache miss with parameter match.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-memory`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `tablebase_cache`
- Also implements: `opening_theory`
- Merge notes: Also absorbs `opening_theory`: opening-book templates before a tablebase miss.
