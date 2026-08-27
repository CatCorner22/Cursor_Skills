---
name: study-system
disable-model-invocation: true
description: "Plan and execute studying: syllabus to weekly schedule, active recall, spaced repetition prompts, exam prep cadence, and WIP limits on courses. Use when mapping a semester, preparing for exams, or building a study routine. Scope boundary: calendar mechanics → `outlook-email-calendar`; lecture capture → `plaud-lecture-notes`; prioritization loops → `ooda-lean-loop`; week prep → `workspace-mise-en-place`."
metadata:
  priority: 8
  promptSignals:
    phrases:
      - "study plan"
      - "exam prep"
      - "syllabus schedule"
      - "spaced repetition"
      - "how to study"
      - "weekly plan"
    allOf:
      - [study, exam]
      - [syllabus, schedule]
    anyOf:
      - "study system"
      - "study schedule"
    minScore: 6
---
# Study system

**Rule:** The **syllabus is the contract**. Calendar blocks are how you pay it — not motivation, not vibes.

## Semester setup (once)

```
1. workspace-mise-en-place  → School/YYYY-Term/ folders (onedrive-organization)
2. outlook-email-calendar   → import all fixed class times + due dates
3. ooda-lean-loop           → WIP limit: max 2 courses in "crunch" at once
4. Per course: Syllabus PDF in folder; note exam dates in calendar
```

## Weekly OODA (Sunday, 20 min)

| Step | Action |
|---|---|
| **Observe** | LMS + calendar + open assignments |
| **Orient** | List due in next 7 days; flag conflicts |
| **Decide** | One primary course per day + backup slot |
| **Act** | Block 2–3 hr study chunks on calendar |
| **Kaizen** | What wasted time last week? |

## Daily session (50 min default)

```
5 min   mise — files, rubric, materials open
5 min   recall — closed book: write what you remember from last session
30 min  focused work — ONE batch (reading section, problem set, outline)
10 min  review — summarize in own words; flashcard 3–5 items
```

## Spaced repetition (lightweight)

After each session, write **3 cards** (Anki, paper, or markdown):

```
Q: [concept]     A: [definition in your words]
Q: [example]     A: [application]
Q: [connection]  A: [link to another topic]
```

Review: +1 day, +3 days, +7 days before exam.

## Exam prep timeline

| When | Focus |
|---|---|
| **3 weeks out** | Inventory all topics from syllabus + lecture Ask Plaud |
| **2 weeks out** | Practice problems / past prompts; weak list |
| **1 week out** | Timed practice; one-page cheat sheet *from memory* |
| **Night before** | Sleep > cram; light recall only |

Pair **`plaud-ask-queries`**: "All exam hints in [Course] recordings."

## Boundaries

- Does not replace attending class or doing assigned reading
- Pair **`citation-literacy`** and the course AI-use policy for assisted-study limits
- Runtime plugin `pedagogical_sequence` maps here — do not add a second pedagogy skill
