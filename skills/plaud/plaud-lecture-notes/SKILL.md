---
name: plaud-lecture-notes
disable-model-invocation: true
description: "Turn Plaud lecture recordings into study materials: capture setup, summary templates for classes, Cornell-style refinement, exam prep loops, and pairing with spaced repetition. Use when a student records classes with Plaud for coursework. Scope boundary: general Plaud routing → `plaud-ecosystem-primer`; study scheduling → `study-system`; prep → `workspace-mise-en-place`; essay writing → `academic-writing`."
metadata:
  priority: 8
  promptSignals:
    phrases:
      - "lecture notes"
      - "record class"
      - "study from recording"
      - "plaud lecture"
      - "exam prep from lecture"
    allOf:
      - [lecture, plaud]
      - [lecture, recording]
      - [class, transcript]
    anyOf:
      - "record lecture"
      - "professor lecture"
    minScore: 6
---
# Plaud lecture notes (student workflow)

**Rule:** Plaud produces **raw intelligence** — you produce **learning**. Every session ends with a human edit pass.

## Mise en place (before class)

Run **`workspace-mise-en-place`** lecture station:

```
[ ] Recording policy confirmed
[ ] Device charged; mode set (plaud-recording-capture)
[ ] Course folder exists in OneDrive (onedrive-organization)
[ ] Calendar block for post-class 30-min review (study-system)
```

## Before class

1. Confirm **recording policy** (syllabus / ask instructor)
2. Charge device; set mode (in-person)
3. Verbal tag: *"History 204, March 5, World War I causes"*
4. Open slide deck on laptop if allowed — Plaud won't capture board-only content

## During class

- **Highlight** when professor says: "this will be on the exam", "remember", due dates, numbered lists
- Don't fidget with device — one start, occasional highlights only

## After class (30-minute routine)

```
1. plaud-recording-capture  → verify sync
2. plaud-transcription      → fix names/terms; add custom vocabulary for next time
3. plaud-summary-templates  → run Lecture-study + Assignment-extract summaries
4. Manual add: slide gaps, board photos, textbook page refs
5. study-system             → schedule review slot within 24h
6. ooda-lean-loop           → one kaizen line: what prep/highlight would help next time?
```

## Cornell refinement (from summary)

| Section | Source |
|---|---|
| **Cues** | Headings + Ask Plaud "list key terms" |
| **Notes** | Edited summary bullets |
| **Summary** | 3-sentence own words (no paste-only) |

## Exam prep loop (2 weeks out)

1. **Ask Plaud:** "All exam hints across [Course] recordings"
2. **Ask Plaud:** "Definitions of [term list from syllabus]"
3. Build one-page **constraint sheet** — hand-write formulas (muscle memory)
4. Cross-check with textbook — transcript may omit nuance

## Group study

- Share **your edited summary**, not raw transcript, unless all consented to record
- Compare Ask Plaud outputs — discrepancies = review those timestamps together

## Academic integrity

- Recording policy ≠ permission to upload transcripts to public sites
- AI summary ≠ submitted work — keep the course AI-use policy in view
- Cite lecture ideas appropriately in papers → **`citation-literacy`**

## Boundaries

- Attendance and participation still matter
- STEM proofs/diagrams: supplement with problem-set workflow when added
