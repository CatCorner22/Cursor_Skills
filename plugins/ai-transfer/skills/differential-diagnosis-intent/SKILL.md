---
name: differential-diagnosis-intent
description: Rank 2–3 interpretations of the user query (literal, examples, comparison) with probabilities before answering. Use when the ask is ambiguous. Scope boundary — this is query triage, not medical advice (high-stakes domains → `underwriting-risk-gate`); OODA orient log → `ooda-adaptive-context`.
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: differential diagnosis intent; query hypotheses; ambiguous ask. Also /differential-diagnosis-intent.'
argument-hint: /differential-diagnosis-intent task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Rank 2–3 interpretations of the user query (literal, examples, comparison) with probabilities before answering
  host: grok-build
  ported_from: Cursor_Skills
---
# Differential diagnosis of query intent

**#34** · **Domain:** Clinical reasoning (method only) · **Category:** extension · **Difficulty:** 🟡 Medium

## Core principle

List competing hypotheses, then pick — do not treat the first reading as the disease.

## AI problem addressed

The model answers the most common parse and misses the intended one.

## Implementation

1. Literal reading
2. Deeper intent (examples / how-to)
3. Alternative (compare / decide)
Assign rough probabilities; answer the top hypothesis; name the runners-up if close.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-extension`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `differential_diag`
