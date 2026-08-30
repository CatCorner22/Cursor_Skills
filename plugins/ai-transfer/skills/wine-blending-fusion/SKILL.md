---
name: wine-blending-fusion
description: 'Run prompt on models with different strengths; fusion pass extracts best elements selectively — not averaging. Use when models complement (reasoning + phrasing + facts). Scope boundary: single-model routing → `emergency-triage-compute`.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Wine blending multi-model fusion

**#28** · **Domain:** Enology · **Category:** refinement · **Difficulty:** 🔴 High

## Core principle

Selective composition — each varietal covers others' weaknesses.

## AI problem addressed

Route-to-one or average ensembles lose complementary strengths.

## Implementation

Model A: structure/skeleton
Model B: phrasing/metaphor
Model C: citations/facts
Fusion: compose strengths; cover weaknesses — do not average.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-refinement`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `wine_blending`
