---
name: stratigraphy-memory
description: 'Layer memory by session strata plus disturbance markers; retrieve with integrity confidence. Use for long-horizon agents. Scope boundary: flat RAG → `library-taxonomy-retrieval`; cross-session bridges → `wildlife-corridor-bridging`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: stratigraphy memory; temporal layers; session strata. Also /stratigraphy-memory.'
argument-hint: /stratigraphy-memory task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Layer memory by session strata plus disturbance markers; retrieve with integrity confidence
  host: grok-build
  ported_from: Cursor_Skills
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
