---
name: plaud-export-integrate
disable-model-invocation: true
description: "Export Plaud transcripts and summaries to Word, PDF, mind maps, and integrate with OneDrive, Teams, Notion, or email workflows. Use when moving Plaud output into school or work tools. Scope boundary: Word formatting → `word-documents`; OneDrive structure → `onedrive-organization`; Teams sharing → `teams-collaboration`."
metadata:
  priority: 6
  promptSignals:
    phrases:
      - "export plaud"
      - "plaud to word"
      - "mind map plaud"
      - "download transcript"
    allOf:
      - [plaud, export]
      - [plaud, word]
    anyOf:
      - "export transcript"
    minScore: 6
---
# Plaud export & integrate

**Rule:** Export **edited** artifacts — transcript + your summary pass + highlights — not raw first drafts for submission.

## Export formats

Plaud's documented export matrix: audio as MP3/WAV; transcripts as TXT/SRT/DOCX/PDF; summaries as TXT/Markdown/DOCX/PDF; mind maps as PNG/Markdown only (not editable).

| Format | Best for |
|---|---|
| **PDF** | Archive, print, submit where formatting fixed |
| **Word (.docx)** | Further editing → **`word-documents`** |
| **TXT / Markdown** | Git notes, Obsidian, dev workflows |
| **Mind map (PNG/Markdown)** | Concept overview before exam |
| **Audio clip (MP3/WAV)** | Cite exact moment in presentation |

Pick format in app **Share / Export** menu (wording varies by platform).

## Word handoff workflow

```
1. Export summary as DOCX
2. word-documents → apply Heading styles, page numbers
3. citation-literacy → if quoting professor or readings mentioned
4. onedrive-organization → save to Course/Assignments path
```

## Microsoft 365 integration path

| Destination | Steps |
|---|---|
| **OneDrive** | Export → save to synced folder or Upload in browser |
| **Word Online** | Open DOCX from OneDrive; co-edit for group study guides |
| **Outlook** | AutoFlow email → drag attachment to course folder |
| **Teams** | Post PDF to channel Files; link in meeting recap message |
| **OneNote** | Paste summary + insert audio link if exported |

Full M365 routing → **`m365-ecosystem-primer`**.

## Third-party (manual)

- **Notion:** Markdown export → import page; attach audio separately
- **Obsidian:** Markdown + wikilinks to `[[Course/Lecture-05]]`
- **Google Docs:** Upload DOCX or paste — formatting may need cleanup

No native Plaud API documented here — use official export/share buttons.

## Mind maps for review

- Generate after **final** summary edit
- Use as **review scaffold**, not sole study source
- Hand-annotate printed mind map for retention

## Retention & backup

- Plaud cloud storage marketed as unlimited — still **export critical finals** locally each term
- End-of-semester: zip `School/2026-Fall/` including Plaud exports

## Programmatic path (Cursor agents)

A Cursor agent cannot press Plaud's Share menu. Once the user drops an exported file into the workspace:

1. Identify the artifact: transcript (TXT/SRT/DOCX), summary (MD/DOCX/PDF), mind map (PNG/MD), or audio (MP3/WAV).
2. Convert as needed: `pandoc notes.docx -t markdown -o notes.md` or the reverse for Word (`word-documents`); `libreoffice --headless --convert-to pdf` for submission.
3. File into the semester folder from `onedrive-organization` / `workspace-mise-en-place` (`School/<term>/<course>/Plaud/`).
4. For lecture exports, hand off to `plaud-lecture-notes` (Cornell refinement) then `study-system`.

## Boundaries

- Respect export restrictions on others' voices
- LMS upload: check file size limits; PDF often safest
