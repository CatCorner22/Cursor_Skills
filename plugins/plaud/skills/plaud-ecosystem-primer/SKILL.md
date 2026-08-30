---
name: plaud-ecosystem-primer
description: 'Router for Plaud AI voice recorder workflows: device capture, transcription, summary templates, Ask Plaud queries, AutoFlow automation, and export. Use when the user mentions Plaud, Plaud Note, Plaud NotePin, voice recorder transcripts, or turning lectures/meetings into notes. Scope boundary: writing essays from scratch → `academic-writing`; Word/Outlook delivery → `m365-ecosystem-primer`; live Teams recording → `teams-collaboration`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: plaud; plaud note; voice recorder transcript; lecture recording; ask plaud; plaud summary; Plaud Note; Plaud NotePin; AutoFlow. Also /plaud-ecosystem-primer.'
argument-hint: /plaud-ecosystem-primer task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Router for Plaud AI voice recorder workflows: device capture, transcription, summary templates, Ask Plaud queries, AutoFlow automation,…'
  host: grok-build
  ported_from: Cursor_Skills
---
# Plaud ecosystem primer

**Plaud** = hardware recorder (Note, NotePin, Note Pro) + **Plaud App / Web / Desktop** + **Plaud Intelligence** (transcription, summaries, Ask Plaud).

Pick the skill for the stage you're in:

| Stage | Skill |
|---|---|
| Recording setup, highlights, dual-mode (call + in-person) | **`plaud-recording-capture`** |
| Transcript quality, languages, speakers, custom vocabulary | **`plaud-transcription`** |
| Summary templates, multidimensional views, action items | **`plaud-summary-templates`** |
| Query across recordings with timestamp citations | **`plaud-ask-queries`** |
| Auto-transfer, auto-summarize, email delivery | **`plaud-autoflow`** |
| Lectures → study notes, exam prep | **`plaud-lecture-notes`** |
| Export PDF/Mind map → Word/OneNote | **`plaud-export-integrate`** |

## Typical pipeline

```
Record → sync to app → transcribe → summarize (template) → review highlights → export / Ask Plaud
```

Enable **AutoFlow** when the same pipeline repeats every lecture or standup.

## Plans (reference)

| Plan | Transcription quota | Notes |
|---|---|---|
| Starter | 300 min/month | Included with device |
| Pro / Unlimited | Higher limits | Advanced models (GPT, Claude, Gemini tiers per Plaud marketing) |

Track monthly minutes before long exam-week recording blocks.

## Cross-pack links

| After Plaud produces notes… | Use |
|---|---|
| Polish essay from transcript | `academic-writing` |
| Format references | `citation-literacy` |
| Flashcards / exam schedule | `study-system` (when added) |
| Final doc in Word | `word-documents` |
| Share with group | `teams-collaboration` + `onedrive-organization` |

## Boundaries

- Plaud skills guide **workflow in Plaud products** — not reverse-engineering proprietary APIs
- Recording laws vary by region — consent required for others' voices; see **`plaud-recording-capture`**
