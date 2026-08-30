---
name: library-taxonomy-retrieval
description: 'Dual retrieval: embedding similarity PLUS taxonomic adjacency in task ontology. Use when related concepts use different wording. Scope boundary: triangulation for facts → `survey-triangulation`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: taxonomy retrieval; ontology browse; dual retrieval. Also /library-taxonomy-retrieval.'
argument-hint: /library-taxonomy-retrieval task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Dual retrieval: embedding similarity PLUS taxonomic adjacency in task ontology'
  host: grok-build
  ported_from: Cursor_Skills
---
# Library taxonomy retrieval

**#24** · **Domain:** Library science · **Category:** memory · **Difficulty:** 🟡 Medium

## Core principle

Classification maps relationships — not just keyword proximity.

## AI problem addressed

Embedding-only misses structurally related but differently worded concepts.

## Implementation

1. Semantic search (embeddings)
2. Taxonomic browse (adjacent ontology nodes)
Merge results; dedupe; rank by task relevance.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-memory`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `catalog_retrieval`
- Also implements: `memory_palace`
- Merge notes: Also absorbs `memory_palace`: spatial room-walk as one retrieval mode.
