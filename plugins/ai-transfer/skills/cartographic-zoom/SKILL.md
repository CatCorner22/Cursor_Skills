---
name: cartographic-zoom
description: 'Generate country/city/street zoom levels: 1–2 sentences, 1–2 paragraphs, full deep-dive. Detect from query or offer zoom-in. Use when verbosity mismatch hurts UX. Scope boundary: stage layout → `stage-blocking-layout`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: zoom level; TLDR depth; summary vs deep dive. Also /cartographic-zoom.'
argument-hint: /cartographic-zoom task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Generate country/city/street zoom levels: 1–2 sentences, 1–2 paragraphs, full deep-dive'
  host: grok-build
  ported_from: Cursor_Skills
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
