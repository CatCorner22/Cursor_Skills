---
name: pipeline-preflight
description: 'Pre-execution audit before AI generation: required inputs, files, constraints, tools, and prior outputs present. Halt instead of running cold. Use before agent runs, RAG pipelines, or multi-step chains. Scope boundary: human/study prep → `workspace-mise-en-place`; craft routing → `craft-systems-primer`.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# AI pipeline pre-flight (mise en place)

**#2** · **Domain:** Culinary arts · **Category:** quality-control · **Difficulty:** 🟢 Low

## Core principle

No heat until ingredients are prepped, measured, and in place.

## AI problem addressed

Pipelines run with missing context then backfill assumptions.

## Implementation

Checklist before generate:
- [ ] Required input variables present and non-empty
- [ ] Referenced prior outputs exist in context
- [ ] Uploaded files attached and parsed
- [ ] System constraints loaded
- [ ] Required tools authenticated
HALT and report gaps if any fail.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-quality-control`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `mise_en_place`
