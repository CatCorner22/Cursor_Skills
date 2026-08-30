---
name: plaud-ask-queries
description: 'Query Plaud recordings with Ask Plaud: cross-file search, cited answers linked to audio timestamps, and follow-up questions. Use when the user wants to find what was said across lectures or meetings in Plaud. Scope boundary: writing new prose from answers → `academic-writing`; naming sources in those answers → `citation-literacy`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: ask plaud; what did they say about; find in my recordings; plaud query; Ask Plaud; across recordings. Also /plaud-ask-queries.'
argument-hint: /plaud-ask-queries task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Query Plaud recordings with Ask Plaud: cross-file search, cited answers linked to audio timestamps, and follow-up questions'
  host: grok-build
  ported_from: Cursor_Skills
---
# Ask Plaud queries

**Rule:** Ask **specific, scoped questions** with **time/course context** — vague prompts return vague synthesis.

## Question patterns that work

| Weak | Strong |
|---|---|
| "Summarize everything" | "List all due dates mentioned in BIOL101 recordings from March" |
| "What is mitosis?" | "How did Prof. Smith define mitosis in the Feb 12 lecture recording?" |
| "Investor stuff" | "What timeline did investors give for Series A in Q1 call recordings?" |

Include: **who, when (date range), topic, desired format** (list, table, yes/no).

## Cross-file search

Ask Plaud can span **multiple recordings** when indexed in your library:

- Filter mentally by folder/naming (`2026-Fall/ECON-`)
- Run series of narrow queries rather than one mega-prompt
- Verify each cited timestamp — open audio at that moment

## Citation workflow

1. Read answer + timestamp links
2. **Spot-check** 1–2 citations (model can over-merge similar lectures)
3. Save critical answers as **notes** attached to the file (Plaud feature)
4. Export snippet if submitting study material to group → **`teams-collaboration`**

## Study-session prompts (examples)

```
"What definitions of [term] appeared across all [Course] lectures?"
"List every homework assignment number and due date mentioned."
"What examples did the professor use for [concept]?"
"Compare what was said about [topic] in lecture 3 vs lecture 7."
"What questions did students ask about the midterm?"
```

## Limits

- Answers only reflect **what was recorded** — absent discussion = no data
- Conflicting statements across weeks: Ask for both cites, reconcile manually
- Privacy: don't query shared devices with others' recordings without permission

## Boundaries

- Not a replacement for LMS or syllabus — verify deadlines officially
- For essay arguments, use Ask output as **research notes**, not paste-ready paragraphs
