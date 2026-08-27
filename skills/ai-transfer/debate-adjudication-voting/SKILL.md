---
name: debate-adjudication-voting
disable-model-invocation: true
description: "Independent agents score rubric dimensions with written ballots; synthesis agent explains weighting. Use for high-stakes evaluation. Scope boundary: counterpoint generation → `counterpoint-perspectives`; wine blend → `wine-blending-fusion`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "debate adjudication"
      - "multi agent scoring"
      - "rubric voting"
    minScore: 6
---
# Debate adjudication multi-agent voting

**#27** · **Domain:** Competitive debate · **Category:** refinement · **Difficulty:** 🔴 High

## Core principle

Discrete criteria scored separately with ballot justification.

## AI problem addressed

Single-pass 'sounds good' evaluation hides tradeoffs.

## Implementation

Agent A: logic 1–10 + justification
Agent B: evidence 1–10 + justification
Agent C: completeness 1–10 + justification
Synthesis: final score + which dimension drove decision and why

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-refinement`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `debate_judging`
