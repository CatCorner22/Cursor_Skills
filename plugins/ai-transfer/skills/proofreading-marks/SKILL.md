---
name: proofreading-marks
description: 'Granular annotation layer between draft and delivery: QUERY, DELETE, STET, TRANSPOSE, INSERT — not wholesale rewrite. Use for AI self-review and human-in-the-loop edit. Scope boundary: full rewrite → domain writing skills.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: proofreading marks; annotation layer; QUERY DELETE STET. Also /proofreading-marks.'
argument-hint: /proofreading-marks task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Granular annotation layer between draft and delivery: QUERY, DELETE, STET, TRANSPOSE, INSERT — not wholesale rewrite'
  host: grok-build
  ported_from: Cursor_Skills
---
# Editorial proofreading marks

**#9** · **Domain:** Publishing · **Category:** quality-control · **Difficulty:** 🟢 Low

## Core principle

Mark specific errors without destroying the original.

## AI problem addressed

Review is accept-all or total rewrite — no middle ground.

## Implementation

Tags: `[QUERY]` verify | `[DELETE]` remove | `[STET]` keep | `[TRANSPOSE]` move | `[INSERT]` add
Apply marks; accept/reject individually before delivery.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-quality-control`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `proof_marks`
