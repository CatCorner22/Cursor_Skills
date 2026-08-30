---
name: canvas
description: Author standalone Grok artifacts (charts, tables, audits, metrics). Use when the deliverable IS structured visual output — not code fixes, PRs, or external dashboards. Skip for short answers and intermediate tool queries.
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: standalone artifact; analysis canvas; metrics table; audit report. Also /canvas.'
argument-hint: /canvas task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Author standalone Grok artifacts (charts, tables, audits, metrics)
  host: grok-build
  ported_from: Cursor_Skills
---
# Standalone artifacts

A canvas here means a **standalone artifact** the user can keep — not Cursor `.canvas.tsx`. If they explicitly want that format, point them at [Cursor_Skills](https://github.com/CatCorner22/Cursor_Skills) `skills/cursor-cloud/canvas`.

## 1. Decide whether to write one

Would the user benefit from viewing this output as its **own file**, separate from the chat?

**Yes:** quantitative analyses, audits, structured findings, large tables, financial decompositions.

**No:** work that belongs in another tool, a PR, a code fix, a short factual answer, or intermediate tool results.

## 2. Write the artifact

Write a real file in the workspace, typically `artifacts/<descriptive-name>.md` (or `.html` / `.csv` when that is the natural format). Link the path in the reply.

**Rules:**
- One primary artifact per analysis.
- Embed data inline. No live `fetch()`.
- Never render empty states. If a section has no data, omit it.
- No placeholder copy ("TODO", "Example", "No data").

## 3. After you write it

Cite the file path. Do not paste the entire artifact back into the chat unless asked. Do not publish or share-link unless asked.
