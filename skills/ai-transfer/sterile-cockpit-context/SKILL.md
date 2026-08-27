---
name: sterile-cockpit-context
disable-model-invocation: true
description: "Phase-gated context: takeoff (parse inputs only), cruise (full history), landing (validation rules only). Strip distraction during critical phases. Use for high-stakes generation steps. Scope boundary: human prioritization → `ooda-lean-loop`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "sterile cockpit"
      - "context gating"
      - "phase context"
    minScore: 6
---
# Sterile cockpit context gating

**#5** · **Domain:** Aviation · **Category:** quality-control · **Difficulty:** 🟡 Medium

## Core principle

Below 10,000 feet — flight ops only. No idle chatter at critical moments.

## AI problem addressed

Irrelevant context dilutes focus during parse/validate phases.

## Implementation

| Phase | Active context |
| Takeoff (parse) | Input variables + explicit constraints only |
| Cruise (generate) | Accumulated history allowed |
| Landing (validate) | Validation rules + quality checks only |
Restore full context between phases as needed.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-quality-control`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `sterile_cockpit`
