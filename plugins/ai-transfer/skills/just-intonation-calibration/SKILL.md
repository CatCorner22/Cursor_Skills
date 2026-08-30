---
name: just-intonation-calibration
description: Calibrate generation parameters as just-intonation ratios by task type (factual, creative, code) instead of one global temperature. Use when the same model is too loose on facts or too stiff on drafts. Scope boundary — prompt wording itself → `prompt-optimizer`; compute budget class → `emergency-triage-compute`.
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: just intonation; generation parameter ratios; temperature by task. Also /just-intonation-calibration.'
argument-hint: /just-intonation-calibration task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Calibrate generation parameters as just-intonation ratios by task type (factual, creative, code) instead of one global temperature
  host: grok-build
  ported_from: Cursor_Skills
---
# Just intonation parameter calibration

**#31** · **Domain:** Music theory (tuning) · **Category:** extension · **Difficulty:** 🟡 Medium

## Core principle

Simple-integer frequency ratios stay consonant; arbitrary detune beats.

## AI problem addressed

One temperature/top-p for every task type produces mush or rigidity.

## Implementation

| Task | Temp | top_p | Cap |
| Factual | 0.3 | 0.85 | short |
| Code | 0.2 | 0.9 | medium |
| Creative | 0.8 | 0.95 | long |
Set the ratio table before generate; do not retune mid-sentence.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-extension`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `just_intonation`
