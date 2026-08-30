---
name: parallax-depth
description: Estimate reasoning depth from the shift between the current query and recent history (deep/medium/shallow). Use to set budget before a long answer. Scope boundary — START classes → `emergency-triage-compute`; zoom level → `cartographic-zoom`.
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: parallax depth; query history shift; reasoning budget depth. Also /parallax-depth.'
argument-hint: /parallax-depth task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Estimate reasoning depth from the shift between the current query and recent history (deep/medium/shallow)
  host: grok-build
  ported_from: Cursor_Skills
---
# Parallax depth of query vs history

**#50** · **Domain:** Photography / surveying · **Category:** advanced · **Difficulty:** 🟡 Medium

## Core principle

Apparent motion against the background tells you distance.

## AI problem addressed

Follow-ups get a full treatise or a shrug with no read on how deep the thread is.

## Implementation

Overlap current query tokens with last 3 turns.
>0.4 → deep (high budget); <0.1 → shallow (standard); else medium.
Set reasoning_budget; do not invent history.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-advanced`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `parallax_depth`
