---
name: localization-qa-filter
description: 'Pre-delivery scan for region mismatch: dates, currency, idioms, units, regulatory refs, cultural examples. Use when audience locale is known. Scope boundary: academic citation locales → `citation-literacy`.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
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
- Runtime plugin id: `localization_qa`
