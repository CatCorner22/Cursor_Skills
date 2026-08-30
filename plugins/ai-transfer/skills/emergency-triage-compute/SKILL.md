---
name: emergency-triage-compute
description: 'Classify tasks Immediate/Delayed/Minor/Deceased before processing; allocate reasoning budget by stakes. Use at router/orchestrator layer. Scope boundary: human prioritization → `ooda-lean-loop`.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Emergency triage compute budgeting

**#17** · **Domain:** Emergency medicine (START) · **Category:** adaptive · **Difficulty:** 🟢 Low

## Core principle

Treat maximum survival — not fairness of equal compute.

## AI problem addressed

Formatting and research questions get same budget.

## Implementation

| Class | Examples | Budget |
| Immediate | Safety, legal, medical | Max |
| Delayed | Research, planning | Standard |
| Minor | Format, rewrite | Minimal |
| Deceased | Out of scope, malformed | Reject early |

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-adaptive`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `start_triage`
- Also implements: `quality_cost_tradeoff`
- Merge notes: Also absorbs `quality_cost_tradeoff` — ROI/budget tier is START classing.
