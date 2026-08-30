---
name: journalistic-attribution
description: 'Source-first generation: retrieve evidence per claim before prose, inline attribution, strip unattributable claims. Use for factual writing and RAG outputs. Scope boundary: bibliography formatting → `citation-literacy`; triple-path check → `survey-triangulation`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: inline citation; verify then write; source first; attribution. Also /journalistic-attribution.'
argument-hint: /journalistic-attribution task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Source-first generation: retrieve evidence per claim before prose, inline attribution, strip unattributable claims'
  host: grok-build
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
