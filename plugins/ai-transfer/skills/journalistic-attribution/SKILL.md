---
name: journalistic-attribution
description: 'Source-first generation: retrieve evidence per claim before prose, inline attribution, strip unattributable claims. Use for factual writing and RAG outputs. Scope boundary: bibliography formatting → `citation-literacy`; triple-path check → `survey-triangulation`.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Journalistic attribution (verify then write)

**#7** · **Domain:** Journalism · **Category:** quality-control · **Difficulty:** 🟡 Medium

## Core principle

Every claim maps to a named on-record source at claim level — not bolted-on endnotes.

## AI problem addressed

Write-then-cite order produces decorative citations.

## Implementation

1. Parse query for claims needed
2. Retrieve source per claim BEFORE generating
3. Generate with inline attribution
4. Verify sources exist and were consulted
5. Strip unattributed claims

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-quality-control`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `attribution_standard`
