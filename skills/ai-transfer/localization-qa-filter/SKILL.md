---
name: localization-qa-filter
description: "Pre-delivery scan for region mismatch: dates, currency, idioms, units, regulatory refs, cultural examples. Use when audience locale is known. Scope boundary: academic citation locales → `citation-literacy`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "localization QA"
      - "region aware"
      - "locale filter"
      - "cultural mismatch"
    minScore: 6
---

# Localization QA filter

**#30** · **Domain:** Software localization · **Category:** refinement · **Difficulty:** 🟡 Medium

## Core principle

Test for cultural mismatch — not translation alone.

## AI problem addressed

Universal reader assumption slips US defaults globally.

## Implementation

Check: date format, currency, idioms, regulations (GDPR/HIPAA), units, cultural refs
Fix during generation for target locale profile.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-refinement`**
- Catalog: **`ai-transfer-ecosystem-primer`**
