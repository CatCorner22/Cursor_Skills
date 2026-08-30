---
name: wayfinding-restructure
description: 'Instrument consumption behavior (scroll-back, re-prompt, abandon) to restructure future outputs. Use for productized AI interfaces with telemetry. Scope boundary: static layout → `stage-blocking-layout`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: wayfinding; user behavior feedback; scroll back restructure. Also /wayfinding-restructure.'
argument-hint: /wayfinding-restructure task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Instrument consumption behavior (scroll-back, re-prompt, abandon) to restructure future outputs
  host: grok-build
  ported_from: Cursor_Skills
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
