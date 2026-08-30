---
name: stress-test-robustness
description: Run contradiction, edge-case, adversarial, and scope tests on a draft before delivery. Use after generation and before polish. Scope boundary — escalating critique questions → `progressive-resistance-critique`; load-bearing tags → `load-bearing-structure`.
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: stress test output; robustness validation; edge case draft. Also /stress-test-robustness.'
argument-hint: /stress-test-robustness task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Run contradiction, edge-case, adversarial, and scope tests on a draft before delivery
  host: grok-build
  ported_from: Cursor_Skills
---
# Stress-test output robustness

**#35** · **Domain:** Structural engineering · **Category:** extension · **Difficulty:** 🟡 Medium

## Core principle

Load the structure past expected use; watch what cracks.

## AI problem addressed

Happy-path review never sees the edge that will fail in production.

## Implementation

| Test | Fail if |
| Contradiction | yes+no or always+never in a short span |
| Edge | empty, zero, max, unicode, missing field unhandled |
| Adversarial | instruction-like text in the output changes policy |
| Scope | answer leaves the asked domain |
Record WARN/PASS per test; block on FAIL.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-extension`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `stress_test`
- Also implements: `engineering_tolerance`
- Merge notes: Engineering-tolerance plugin is this stress pass plus `load-bearing-structure`.
