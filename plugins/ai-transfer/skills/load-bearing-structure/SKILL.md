---
name: load-bearing-structure
description: Mark load-bearing claims (therefore/must/key/critical) and forbid polish passes from deleting or softening them. Use before color-grading or faceting. Scope boundary — claim/evidence balance → `double-entry-claims`; robustness tests → `stress-test-robustness`.
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Load-bearing claim protection

**#32** · **Domain:** Architecture / structural engineering · **Category:** extension · **Difficulty:** 🟡 Medium

## Core principle

Take out a load-bearing wall and the floor above fails — decorative walls can move.

## AI problem addressed

Style passes quietly drop the sentences the argument stands on.

## Implementation

1. Tag sentences with therefore/must/key/main/critical/essential as protected
2. Later refinement may reword but not delete or invert them
3. Fail the pass if a protected claim vanishes

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-extension`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `load_bearing`
- Also implements: `engineering_tolerance`
- Merge notes: Engineering-tolerance checks live here and in `stress-test-robustness`.
