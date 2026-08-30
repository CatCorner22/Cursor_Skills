---
name: plaud-summary-templates
description: 'Generate Plaud AI summaries: built-in templates, custom templates, multidimensional summaries, action items, and meeting vs lecture formats. Use when summarizing a Plaud transcript or designing a reusable template. Scope boundary: cross-file Q&A → `plaud-ask-queries`; turning summary into essay → `academic-writing`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: plaud summary; summary template; action items; multidimensional summary; meeting minutes plaud; 360 view; Auto Generation. Also /plaud-summary-templates.'
argument-hint: /plaud-summary-templates task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Generate Plaud AI summaries: built-in templates, custom templates, multidimensional summaries, action items, and meeting vs lecture formats'
  host: grok-build
  ported_from: Cursor_Skills
---
# Plaud summary templates

**Rule:** **Template = job to be done.** Pick (or design) the output shape before generating — one recording can hold **multiple summaries** without replacing the original.

## Built-in template families

| Use case | Template style | Output focus |
|---|---|---|
| **University lecture** | Lecture / Education | Concepts, definitions, readings mentioned |
| **Team standup** | Meeting | Blockers, owners, dates |
| **Interview / research** | Interview | Quotes, themes, follow-ups |
| **Sales / client** | Call summary | Needs, objections, next steps |
| **Strategic** | Executive overview | Decisions, risks, open questions |

Browse Plaud's template library (10,000+ marketed) — star favorites for one-tap reuse.

## Multidimensional summaries (360° View)

From **one** recording, generate **parallel** summaries:

- Action items (tasks + owners)
- Key decisions
- Open questions
- Strategic overview

Each view is additive — original transcript and prior summaries stay intact. Use when one lecture serves both **study notes** and **group project** extraction.

## Custom template workflow

1. Describe output in plain language *or* photo of an example format
2. Plaud converts to reusable template
3. Test on one recording; refine section headings
4. Save named: `BIOL101-Lecture`, `Advisor-Meeting`

**Custom template skeleton (lecture):**

```markdown
## Topic & learning objectives
## Core concepts (definition → example)
## Diagrams / processes mentioned
## Assignments & due dates
## Exam hints / "will be on the test"
## Readings & page numbers
## Open questions to clarify
```

## Post-generation edit pass

- Verify **dates and numbers** against transcript timestamps
- Deduplicate bullets Auto-summary repeats
- Merge with **highlights** you pressed during recording
- Add slide references manually where ASR missed board content

## Multiple summaries strategy (student)

| Summary type | Purpose |
|---|---|
| `Lecture-study` | Exam prep |
| `Assignment-extract` | Problem set hints only |
| `Reading-bridge` | Tie lecture to textbook chapter |

## Boundaries

- Summary ≠ submitted essay — run through **`academic-writing`** in your own voice and the course AI-use policy
- Templates can't invent content not in audio — flag gaps explicitly
