---
name: after-action-review
description: 'Post-generation debrief: intended vs actual vs gap vs prescription. Log for recurring pattern fixes. Use after agent tasks complete. Scope boundary: five whys on hard failures → `five-whys-failure-recovery`.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# After-action review (AAR)

**#18** · **Domain:** Military · **Category:** adaptive · **Difficulty:** 🟡 Medium

## Core principle

What was supposed to happen? What did? Why the gap? Sustain or improve?

## AI problem addressed

Generate, deliver, move on — no systematic debrief.

## Implementation

1. Original intent (parsed from prompt)
2. Actual output
3. Delta (gap)
4. Prescription for next time
Aggregate logs → recurring failure patterns.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-adaptive`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `aar_debrief`
- Also implements: `self_evaluation`, `metacognitive_monitor`
- Merge notes: Post-delivery debrief owns the same loop the meta-cognition plugins sketched.
