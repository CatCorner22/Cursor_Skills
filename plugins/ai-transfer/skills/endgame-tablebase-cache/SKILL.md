---
name: endgame-tablebase-cache
description: 'Pre-compute and cache known-correct answers for recurring boundary conditions; check tablebase before reasoning. Use for boilerplate code, legal clauses, lookup math. Scope boundary: live reasoning → `proof-trees-reasoning`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: tablebase cache; boundary cache; known correct cache. Also /endgame-tablebase-cache.'
argument-hint: /endgame-tablebase-cache task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Pre-compute and cache known-correct answers for recurring boundary conditions; check tablebase before reasoning
  host: grok-build
  ported_from: Cursor_Skills
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
