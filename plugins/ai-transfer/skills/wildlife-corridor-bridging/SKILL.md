---
name: wildlife-corridor-bridging
description: 'Detect topic overlap across sessions; inject bridge summaries connecting isolated context islands. Use for long-term personal agents. Scope boundary: strata layers → `stratigraphy-memory`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: memory bridge; cross session; conceptual corridor. Also /wildlife-corridor-bridging.'
argument-hint: /wildlife-corridor-bridging task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Detect topic overlap across sessions; inject bridge summaries connecting isolated context islands
  host: grok-build
  ported_from: Cursor_Skills
---
# Wildlife corridor memory bridging

**#25** · **Domain:** Conservation biology · **Category:** memory · **Difficulty:** 🔴 High

## Core principle

Habitats need corridors — not isolated pockets.

## AI problem addressed

Each conversation is an island despite conceptual overlap.

## Implementation

1. Detect overlap current ↔ historical sessions
2. Generate bridge: 'Three weeks ago you X; connection to today Y'
3. Inject bridge into active context

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-memory`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `corridor_bridge`
