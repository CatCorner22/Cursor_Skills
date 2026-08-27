---
name: academic-ecosystem-primer
description: "Router for college and academic work in this library: writing, citations, study planning, source attribution, lecture notes, and presentations. Use when the user is a student, mentions college/school/coursework, or asks how to approach an assignment, paper, exam prep, or lab. Scope boundary: CS/software implementation → `coding-ecosystem-primer`; AI/ML engineering → huggingface/langchain packs; GitHub PR workflow for group code projects → `cursor-team-kit`; general execution posture → `proactive-agency`."
metadata:
  priority: 8
  promptSignals:
    phrases:
      - "college"
      - "coursework"
      - "assignment"
      - "homework"
      - "syllabus"
      - "study for"
      - "write my essay"
      - "research paper"
      - "lab report"
      - "problem set"
      - "cite this"
      - "going back to school"
    allOf:
      - [college, assignment]
      - [school, essay]
      - [course, study]
      - [research, paper]
    anyOf:
      - "back to college"
      - "back to school"
      - "academic writing"
      - "literature review"
    minScore: 6
---

# Academic ecosystem primer

Pick the **smallest set of skills** for the assignment type. This pack is **discipline-agnostic** — it governs *how to succeed in coursework*, not which major you chose.

## Decision table

| User intent | Load next |
|---|---|
| Essay, argument, revision, thesis statement, lab IMRaD | **`academic-writing`** |
| APA/MLA/Chicago, bibliography, in-text citations | **`citation-literacy`** |
| "What do these stats mean?", p-values, polls, study results | **`academic-writing`** (interpret in prose) + **`citation-literacy`** (name the source) |
| Syllabus → schedule, exam prep, note-taking, spaced repetition, problem-set cadence | **`study-system`** |
| Find sources, evaluate credibility, literature review | **`citation-literacy`** + **`journalistic-attribution`**; CS/AI papers → **`huggingface-papers`** |
| Slides, poster, oral presentation | **`powerpoint-decks`** |
| Course AI-use / plagiarism / when to ask the professor | **`citation-literacy`** + **`journalistic-attribution`** (do not invent sources) |
| Build an app for class (CS) | **`coding-ecosystem-primer`** → then domain skills |
| Word / Excel / PowerPoint / Teams / Outlook | **`m365-ecosystem-primer`** |
| Lecture recording → study notes (Plaud) | **`plaud-ecosystem-primer`** |
| Summarize an AI/CS arXiv paper | **`huggingface-papers`** |
| Group project git/PR workflow | **`cursor-team-kit`** |
| Stuck, prioritizing, weekly planning | **`craft-systems-primer`** → `ooda-lean-loop` |
| Prep before starting (files, week setup) | **`workspace-mise-en-place`** |

## Systems combinations

**Sunday mise (student):** `workspace-mise-en-place` → `outlook-email-calendar` → `onedrive-organization` → `study-system` weekly OODA.

**Assignment OODA:** `ooda-lean-loop` → confirm course AI-use rules → domain skill (act) → `citation-literacy` (andon if missing sources).

## Default workflow (most written assignments)

```
1. citation-literacy + course syllabus → confirm what help and sources are allowed
2. journalistic-attribution / huggingface-papers → gather real sources if research is required
3. academic-writing    → draft with thesis and structure
4. citation-literacy   → format references and in-text cites
5. study-system        → if exam or multi-week project, map deadlines first
```

## Returning-student note

Pair **`study-system`** with **`proactive-agency`**: the syllabus is the contract; the agent executes slices without waiting for permission on reversible steps (outlines, flashcards, draft sections) while **`citation-literacy`** and **`journalistic-attribution`** govern what must stay sourced.

## Boundaries

| Topic | Owner |
|---|---|
| Software feature implementation | `coding-ecosystem-primer` |
| Next.js / deployment | `vercel` pack |
| ML model training | `huggingface` pack |
| Character reference (Nyx) | `nyx` (projects) |
| AI pipeline quality / cross-domain techniques | **`ai-transfer-ecosystem-primer`** |
