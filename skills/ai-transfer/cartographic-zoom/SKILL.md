---
name: cartographic-zoom
description: "Generate country/city/street zoom levels: 1–2 sentences, 1–2 paragraphs, full deep-dive. Detect from query or offer zoom-in. Use when verbosity mismatch hurts UX. Scope boundary: stage layout → `stage-blocking-layout`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "zoom level"
      - "TLDR depth"
      - "summary vs deep dive"
    minScore: 6
---

# Cartographic zoom levels

**#14** · **Domain:** Cartography · **Category:** architecture · **Difficulty:** 🟡 Medium

## Core principle

Detail adapts to viewer scale — same data, different generalization.

## AI problem addressed

Single-zoom outputs guess wrong depth.

## Implementation

| Zoom | Format | When |
| Country | 1–2 sentences | Urgent / glance |
| City | 1–2 paragraphs | Standard |
| Street | Full analysis | Follow-up / deep |
Detect from urgency, format hints, or prior context.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-architecture`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `cartographic_zoom`
