---
name: just-intonation-calibration
disable-model-invocation: true
description: "Calibrate generation parameters as just-intonation ratios by task type (factual, creative, code) instead of one global temperature. Use when the same model is too loose on facts or too stiff on drafts. Scope boundary — prompt wording itself → `prompt-optimizer`; compute budget class → `emergency-triage-compute`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "just intonation"
      - "generation parameter ratios"
      - "temperature by task"
    minScore: 6
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
