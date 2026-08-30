---
name: interaction-table
description: Look up known skill/plugin pairs that fight (context strip vs inject, length vs rhythm, duck vs dual-axis, rewrite vs lock) before loading both. Use when composing an ai-transfer stack. Scope boundary — library routing audit → `skill-library-audit`; compute triage → `emergency-triage-compute`.
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Interaction table for skill conflicts

**#48** · **Domain:** Pharmacology / chemistry · **Category:** advanced · **Difficulty:** 🟡 Medium

## Core principle

Two safe drugs can be unsafe together — check the table, not the labels.

## AI problem addressed

Stacks enable every matching skill and they undo each other's gates.

## Implementation

Pairs: sterile_cockpit×corridor_bridge, token_optimizer×tidal_pacing,
sidechain_duck×score_study, progressive_critique×glass_anneal.
If both would fire, disable one and record why.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-advanced`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `interaction_table`
