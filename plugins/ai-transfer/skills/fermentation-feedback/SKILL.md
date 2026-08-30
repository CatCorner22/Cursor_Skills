---
name: fermentation-feedback
description: 'Mid-generation monitoring: user activity, corrections typing, deadlines, confidence — adjust or abort mid-stream. Use for long agent runs and streaming workflows. Scope boundary: post-hoc AAR → `after-action-review`.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Fermentation environmental feedback

**#19** · **Domain:** Biochemistry / food science · **Category:** adaptive · **Difficulty:** 🔴 High

## Core principle

Environment responds to the process continuously — not fire-and-forget.

## AI problem addressed

Batch in/out with no mid-flight sensing.

## Implementation

After each step/paragraph check: user active? correction started? deadline passed? confidence drop?
Adjust: pivot, accelerate, or abort mid-stream.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-adaptive`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `fermentation_loop`
- Also implements: `levain_culture`, `user_model_builder`
- Merge notes: Also absorbs `levain_culture` (persistent style culture) and personalization culture-state.
