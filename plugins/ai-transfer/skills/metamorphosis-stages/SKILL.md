---
name: metamorphosis-stages
description: Force larva (brainstorm) → pupa (structure) → adult (polish) as separate artifacts. Use instead of polishing a first dump. Scope boundary — annealing lock temperatures → `glass-annealing-hardening`; faceting angles → `gemstone-faceting-refinement`.
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: metamorphosis stages; larva pupa adult; staged draft evolution. Also /metamorphosis-stages.'
argument-hint: /metamorphosis-stages task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Force larva (brainstorm) → pupa (structure) → adult (polish) as separate artifacts
  host: grok-build
  ported_from: Cursor_Skills
---
# Metamorphosis staged drafts

**#40** · **Domain:** Developmental biology · **Category:** extension · **Difficulty:** 🟡 Medium

## Core principle

The adult is not a prettier larva — each instar has different work.

## AI problem addressed

One-pass generation tries to invent, outline, and polish together.

## Implementation

Larva: raw points, no headings
Pupa: section the points
Adult: strip scaffolding notes, keep structure
Do not skip a stage on long work.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-extension`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `metamorphosis`
