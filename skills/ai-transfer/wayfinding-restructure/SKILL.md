---
name: wayfinding-restructure
description: "Instrument consumption behavior (scroll-back, re-prompt, abandon) to restructure future outputs. Use for productized AI interfaces with telemetry. Scope boundary: static layout → `stage-blocking-layout`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "wayfinding"
      - "user behavior feedback"
      - "scroll back restructure"
    minScore: 6
---

# Urban wayfinding restructure

**#20** · **Domain:** Urban design · **Category:** adaptive · **Difficulty:** 🔴 High

## Core principle

Adapt signage to how people actually move — not ideal paths.

## AI problem addressed

Linear output assumes logical reading; no behavior feedback.

## Implementation

Track: scroll-back zones → frontload; re-prompt sections → clarify; abandon zones → shorten/restructure.
Feed patterns into next output architecture.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-adaptive`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `urban_wayfinding`
