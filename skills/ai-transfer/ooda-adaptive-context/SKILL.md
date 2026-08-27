---
name: ooda-adaptive-context
description: "Four-phase AI pipeline with logged Orient step: observe raw context, orient (filter/prioritize with inspectable log), decide approach, act. Use when debugging why context was ignored. Scope boundary: human OODA → `ooda-lean-loop`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "OODA pipeline"
      - "orient log"
      - "context filter AI"
    minScore: 6
---

# OODA adaptive context (AI pipeline)

**#11** · **Domain:** Combat aviation (Boyd) · **Category:** architecture · **Difficulty:** 🔴 High

## Core principle

Orient is explicit filtering — inspectable, not collapsed into embedding lookup.

## AI problem addressed

Observe+orient merged; no log of what was discarded.

## Implementation

1. Observe: gather all context
2. Orient: filter by task; LOG kept/discarded + why
3. Decide: select method
4. Act: generate
Debug 'ignored file' → read orient log.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-architecture`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `ooda_loop`
