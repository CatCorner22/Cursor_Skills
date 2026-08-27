---
name: interaction-table
disable-model-invocation: true
description: "Look up known skill/plugin pairs that fight (context strip vs inject, length vs rhythm, duck vs dual-axis, rewrite vs lock) before loading both. Use when composing an ai-transfer stack. Scope boundary — library routing audit → `skill-library-audit`; compute triage → `emergency-triage-compute`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "interaction table"
      - "plugin conflict"
      - "skill pair contraindication"
    minScore: 6
---

# Interaction table for skill conflicts

**#48** · **Domain:** Pharmacology / chemistry · **Category:** advanced · **Difficulty:** 🟡 Medium

## Core principle

Two safe drugs can be unsafe together — check the table, not the labels.

## AI problem addressed

Stacks enable every matching skill and they undo each other's gates.

## Implementation

Known conflicting pairs (skill names; runtime plugin ids in parentheses):
`sterile-cockpit-context` × `wildlife-corridor-bridging` (sterile_cockpit×corridor_bridge),
`prompt-optimizer` × `tidal-pacing-rhythm` (token_optimizer×tidal_pacing — token_optimizer has no
standalone skill; it is absorbed by prompt-optimizer),
`sidechain-priority` × `score-study-dual-axis` (sidechain_duck×score_study),
`progressive-resistance-critique` × `glass-annealing-hardening` (progressive_critique×glass_anneal).
If both would fire, disable one and record why.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-advanced`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `interaction_table`
