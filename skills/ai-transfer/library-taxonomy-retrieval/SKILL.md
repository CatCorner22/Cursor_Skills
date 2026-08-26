---
name: library-taxonomy-retrieval
description: "Dual retrieval: embedding similarity PLUS taxonomic adjacency in task ontology. Use when related concepts use different wording. Scope boundary: triangulation for facts → `survey-triangulation`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "taxonomy retrieval"
      - "ontology browse"
      - "dual retrieval"
    minScore: 6
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
