---
name: canvas
description: Author standalone ChatGPT Canvas or Codex file artifacts (charts, tables, audits, metrics). Use when the deliverable IS structured visual output — not code fixes, PRs, or external dashboards. Skip for short answers and intermediate tool queries.
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Canvas and standalone artifacts

A canvas is a **standalone artifact** the user can keep viewing beside the chat. Follow this workflow in order.

Cursor `.canvas.tsx` / `cursor/canvas` SDK files are **out of scope**. If the user explicitly wants that format, point them at [Cursor_Skills](https://github.com/CatCorner22/Cursor_Skills) `skills/cursor-cloud/canvas`.

## 1. Decide whether to use a canvas

The trigger is **user intent**, not response shape. Ask: would the user benefit from viewing this output as its **own standalone artifact**, separate from the chat?

**Use a canvas when the agent produces new standalone analytical output:**
- Quantitative analyses and metrics breakdowns
- Billing or account investigations with structured findings
- Security audits or architecture reviews with categorized findings
- Cross-system data analyses and overlap reports
- Tables with more than a handful of rows the user asked to see
- Financial analyses, margin decompositions, usage trend reports

**Do NOT use a canvas when:**
- The user asks for work in a **specific tool** (give them that tool's artifact)
- The user has a **specific deliverable** — draft a message, fix code, open a PR
- The user is **working within an existing file**
- Targeted debugging or short factual answers
- Tool results are an **intermediate step** for a different deliverable

## 2. Write the artifact

**ChatGPT (Chat / Work / desktop):** use **Canvas**. Put the full deliverable in the canvas — narrative, tables, and mermaid/code blocks the product supports. Do not leave the real content only in the chat.

**Codex (CLI / IDE):** write a real file in the workspace, typically `artifacts/<descriptive-name>.md` (or `.html` / `.csv` when that is the natural format). Link the path in the reply.

**Rules:**
- One primary artifact per analysis. Do not spray helper files.
- Embed data inline. No `fetch()`, no live network calls inside the artifact.
- **Never render empty states.** If a section has no data, omit it. If the whole artifact would be empty, do not create it — say what is missing.
- No placeholder copy ("Add header here", "TODO", "Example", "No data").
- Default-export is not required; ChatGPT Canvas is not a React component.

## 3. After you write it

- In ChatGPT, leave the canvas open as the deliverable and keep the chat to a short summary plus next actions.
- In Codex, cite the file path. Do not paste the entire artifact back into the chat unless the user asked to see it inline.
- Do not publish, share-link, or email the artifact unless the user asked.

## Voice

The artifact is the product. The chat is the caption. No congratulatory lede.
