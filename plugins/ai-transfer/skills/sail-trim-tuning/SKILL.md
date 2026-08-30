---
name: sail-trim-tuning
description: Read user confusion/satisfaction signals and trim the next beat (more examples vs hold course). Use on multi-turn work. Scope boundary — mid-stream environment loop → `fermentation-feedback`; human OODA → `ooda-lean-loop`.
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: sail trim; telltales; mid response adjust. Also /sail-trim-tuning.'
argument-hint: /sail-trim-tuning task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Read user confusion/satisfaction signals and trim the next beat (more examples vs hold course)
  host: grok-build
  ported_from: Cursor_Skills
---
# Sail trim mid-response tuning

**#47** · **Domain:** Sailing · **Category:** advanced · **Difficulty:** 🟢 Low

## Core principle

Ease or sheet based on the telltales — not on the last weather report.

## AI problem addressed

The agent keeps the same verbosity after the user says they are lost or done.

## Implementation

confused/don't understand → add examples, simplify
thanks/great/perfect → hold course
else → no trim
Log the trim; do not rewrite history.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-advanced`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `sail_trim`
