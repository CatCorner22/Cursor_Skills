---
name: glass-annealing-hardening
description: 'Staged delivery: high temp (everything flexible) → medium (structure locked) → cool (typos only). Use for long documents and multi-pass review. Scope boundary: faceting angles → `gemstone-faceting-refinement`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: annealing; staged delivery; cooling phases; lock structure. Also /glass-annealing-hardening.'
argument-hint: /glass-annealing-hardening task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Staged delivery: high temp (everything flexible) → medium (structure locked) → cool (typos only)'
  host: grok-build
  ported_from: Cursor_Skills
---
# Glass annealing output hardening

**#21** · **Domain:** Glassblowing · **Category:** adaptive · **Difficulty:** 🟡 Medium

## Core principle

Gradual cooling resolves internal stress — fast cool shatters.

## AI problem addressed

Hot delivery commits to flawed structure early.

## Implementation

| Temp | Locked | Flexible |
| High | Nothing | Structure, content |
| Medium | Major structure | Wording, examples |
| Cool | All content | Typos, format only |

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-adaptive`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `glass_anneal`
