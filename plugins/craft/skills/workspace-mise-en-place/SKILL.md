---
name: workspace-mise-en-place
description: 'Prepare the workspace before execution: files, folders, env, tools, references, and templates in place so work never stops for a missing ingredient. Culinary mise en place applied to repos, OneDrive, and study sessions. Use before starting an assignment, coding session, lecture day, or deploy. Scope boundary: during-task loops → `ooda-lean-loop`; folder taxonomy → `onedrive-organization`; defining done → `deliverable-first`.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: mise en place; prep before starting; get organized first; set up workspace; before I begin; everything in place. Also /workspace-mise-en-place.'
argument-hint: /workspace-mise-en-place task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Prepare the workspace before execution: files, folders, env, tools, references, and templates in place so work never stops for a missing…'
  host: grok-build
  ported_from: Cursor_Skills
---
# Workspace mise en place

**Rule:** No **heat** until the **station** is set. Heat = writing prose, coding features, presenting, submitting. Prep = everything else.

## The three stations

| Station | Question | Failure mode |
|---|---|---|
| **Physical / device** | Is hardware ready? | Dead battery mid-lecture |
| **Digital / files** | Is every file one click away? | Hunt through Downloads |
| **Cognitive / contract** | Do I know what "done" looks like? | Start writing without thesis |

## Universal pre-flight (5 minutes)

```
[ ] Done definition named in one sentence (deliverable-first or syllabus line)
[ ] Primary output location exists and is named (onedrive-organization pattern)
[ ] Reference materials open or linked (syllabus, rubric, starter repo)
[ ] Tooling verified once (test command, Plaud sync, Word template)
[ ] Calendar block reserved for this batch (outlook-email-calendar)
[ ] WIP limit: only ONE in-progress batch for this course/project
```

## Student mise (Sunday or night before)

| Item | Skill / action |
|---|---|
| Week calendar blocked | `outlook-email-calendar` |
| Course folders exist | `onedrive-organization` |
| Word template with styles | `word-documents` |
| Plaud charged + template set | `plaud-recording-capture`, `plaud-autoflow` |
| LMS deadlines copied to calendar | manual + syllabus PDF in `Syllabus/` |

## Developer mise (session start)

| Item | Skill / action |
|---|---|
| Branch checked out | `cursor-team-kit` |
| `.env.local` / deps present | `bootstrap`, `env-vars` |
| Test/lint command known | `real-time-testing` |
| Acceptance checklist from issue | `deliverable-first` |
| Dev server or watch mode ready | narrowest verify command queued |

## Group project mise

```
[ ] OneDrive/Teams folder is source of truth (teams-collaboration)
[ ] Git repo linked in channel description (not zip-in-chat)
[ ] Roles named for this week (editor, presenter, integrator)
[ ] Shared Word/PPT template in Files tab
```

## "Heat" checklist — you may start when

- You can name the **next 25–50 minute batch** without opening new tabs
- Missing items are **explicitly deferred**, not forgotten
- If recording: consent + device sync verified (`plaud-recording-capture`)

## Breakdown (after batch)

- Save/export to canonical path — not Desktop clutter
- One kaizen note: what prep item would have saved time? → feed to **`ooda-lean-loop`**

## Boundaries

- Mise is prep, not procrastination — 5–15 min cap unless greenfield project
- Does not organize email inbox fully — only what's needed for this batch
