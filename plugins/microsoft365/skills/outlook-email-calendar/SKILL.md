---
name: outlook-email-calendar
description: 'Professional email and calendar in Microsoft Outlook: syllabus-to-calendar blocking, meeting invites, inbox triage, signatures, and student-professor communication tone. Use when managing Outlook mail, scheduling study blocks, or drafting academic/professional emails. Scope boundary: Teams chat/meetings → `teams-collaboration`; task lists in Planner/To Do → mention only; Gmail → not this pack.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: outlook email; outlook calendar; schedule meeting; email professor; microsoft outlook; Microsoft Outlook; office hours. Also /outlook-email-calendar.'
argument-hint: /outlook-email-calendar task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Professional email and calendar in Microsoft Outlook: syllabus-to-calendar blocking, meeting invites, inbox triage, signatures, and…'
  host: grok-build
  ported_from: Cursor_Skills
---
# Outlook email & calendar

**Rule:** Email is **async** — subject line + first sentence must carry the ask. Calendar is **commitment** — block study time like classes.

## Email to professors / TAs

**Subject:** `[Course CODE] — Brief topic — Your Name`

**Structure:**
```
Greeting (Dr./Prof. Lastname),

One sentence context (who you are / which section).

One sentence specific question or request.

Optional: what you already tried (read syllabus, checked LMS).

Thank you + sign-off,
Full Name | Student ID if required
```

**Tone:** respectful, concise, no emoji unless they use them first. Don't demand instant reply.

## Inbox triage (student)

| Folder/rule | Purpose |
|---|---|
| **Focused Inbox** | Keep school senders focused |
| Flag + due date | Assignments mentioned in email |
| Rules | `[Canvas]` / `[Blackboard]` → course folder |
| Snooze | non-urgent until study block |

## Calendar from syllabus

1. Enter **all fixed classes** as recurring events (location, Teams link if hybrid)
2. Add **assignment due dates** as all-day or deadline events (day before = buffer)
3. Block **study sessions** (2–3 hr chunks) per credit hour guideline
4. Color-code by course
5. Set **reminders:** 1 day for papers, 1 hour for quizzes

Pair with **`study-system`** for weekly planning logic.

## Meeting invites

- **Title:** `[Course] Office hours — Topic` or `Group project sync`
- **Agenda in body:** 3 bullets max
- **Scheduling Assistant:** find overlap for group members
- **Teams meeting:** auto-add if online

## Signatures (keep minimal)

```
Full Name
Major | University
email@school.edu
```

No inspirational quotes for academic mail.

## Copilot in Outlook (where available)

- "Draft a polite email asking for a 48-hour extension citing illness per syllabus"
- "Summarize this thread and list action items"
- "Find three 2-hour slots this week for studying Biology"

## Boundaries

- Does not send email without user review
- Institutional policies on AI-generated mail → follow the course or workplace AI-use policy
