---
name: plaud-transcription
description: 'Improve Plaud transcripts: language selection, speaker diarization, custom vocabulary, formatting, and fixing common ASR errors before summarizing. Use after a Plaud recording syncs or when transcript accuracy is poor. Scope boundary: summary templates → `plaud-summary-templates`; querying transcripts → `plaud-ask-queries`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: plaud transcript; transcription accuracy; speaker labels; custom vocabulary; fix transcript; diarization; 112 languages. Also /plaud-transcription.'
argument-hint: /plaud-transcription task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Improve Plaud transcripts: language selection, speaker diarization, custom vocabulary, formatting, and fixing common ASR errors before…'
  host: grok-build
  ported_from: Cursor_Skills
---
# Plaud transcription

**Rule:** **Fix the transcript before the summary** — garbage in propagates to every template and Ask Plaud answer.

## Auto-generation settings

- **Auto Generation** detects language + speakers on upload — good default for monolingual lectures
- Mixed-language meetings: set primary language manually before re-transcribing
- Re-run transcription after changing language or vocabulary (uses quota)

## Speaker diarization

- Review **Speaker 1 / Speaker 2** labels on multi-person recordings
- Rename speakers in app (Professor, Student A) for readable exports
- Solo lecture: single speaker is fine — disable over-splitting if available

## Custom vocabulary

Add to **Settings → Custom vocabulary** (wording may vary by app version):

- Course codes, professor names, technical terms (`CRISPR`, `eigenvalue`)
- Company/product names for internships
- Abbreviations your field uses (`IMRaD`, `ANOVA`)

Update each semester — stale vocab wastes corrections.

## Correction workflow

```
1. Scan first 2 minutes for systematic errors (name, jargon)
2. Add custom vocabulary → re-transcribe if errors are global
3. Line-edit critical sections (definitions, exam hints, numbers)
4. Use highlights to mark corrected must-know segments
5. Lock transcript mentally as "source" before summarizing
```

**Numbers and formulas:** ASR often garbles — verify against slides/book; don't trust raw transcript for math.

## Formatting tips

- Break long monologues with paragraph edits where topic shifts
- Mark `[inaudible]` yourself rather than leaving nonsense words
- Timestamp navigation: use built-in audio scrub with text follow

## Quota management

- Starter: **300 min/month** transcription — budget ~5 hr lecture/week = tight; prioritize must-record sessions
- Download/archive important transcripts outside Plaud if retention policy unclear

## Boundaries

- Not real-time captioning — post-session workflow
- Medical/legal verbatim → human review required; don't rely on ASR alone
