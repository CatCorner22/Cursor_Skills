---
name: counterpoint-perspectives
description: "Generate 2–3 independent analytical voices with own logic, then harmonize into interwoven output — not pros/cons list. Use for multi-stakeholder or multi-framework analysis. Scope boundary: debate scoring → `debate-adjudication-voting`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "counterpoint"
      - "multiple perspectives"
      - "interwoven arguments"
    minScore: 6
---

# Musical counterpoint perspectives

**#13** · **Domain:** Music theory · **Category:** architecture · **Difficulty:** 🔴 High

## Core principle

Independent voices complete alone yet richer in harmony.

## AI problem addressed

Single voice or appended 'on the other hand' hedging.

## Implementation

1. Voice 1: coherent framework A argument
2. Voice 2: framework B argument
3. Voice 3 (optional): framework C
4. Compose interaction — resolve intersections, not juxtaposition

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-architecture`**
- Catalog: **`ai-transfer-ecosystem-primer`**
