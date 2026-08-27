---
name: teams-collaboration
disable-model-invocation: true
description: "Collaborate in Microsoft Teams for school and work: channels, chat threads, meetings, screen share, file tabs, and group project norms. Use when setting up Teams for a group project, running class meetings, or coordinating async work. Scope boundary: email → `outlook-email-calendar`; file storage policy → `onedrive-organization`; Slack/Discord → not this pack."
metadata:
  priority: 7
  promptSignals:
    phrases:
      - "microsoft teams"
      - "teams meeting"
      - "teams channel"
      - "group project teams"
    allOf:
      - [teams, meeting]
      - [teams, channel]
    anyOf:
      - "Microsoft Teams"
      - "Teams chat"
    minScore: 6
---
# Teams collaboration

**Rule:** **One channel per topic**, not one giant chat. Decisions live in **Posts** (threaded); quick pings in **Chat**.

## Group project setup

1. **Team name:** `CourseCode-ProjectName-Semester`
2. **Channels:**
   - `General` — announcements, meeting links
   - `Research` — sources, shared docs
   - `Drafts` — work in progress
   - `Deliverables` — final exports only
3. **Files tab:** pin master Word/PPT; enable **version history**
4. **Roles:** assign note-taker, editor, presenter rotation in first meeting

## Meeting hygiene

| Before | During | After |
|---|---|---|
| Agenda in invite | Record only if all consent | Post notes in channel thread |
| Test mic/camera | Mute when not speaking | List action items + owners |
| Share slides early | Timebox sections | Link recording in Files if allowed |

## Chat norms

- `@mention` only when you need that person's input
- Reply **in thread** to keep channel readable
- Don't paste full essays in chat — link OneDrive file

## Integrations (class context)

- **Assignments** tab if instructor uses Teams for LMS
- **OneNote** class notebook if provided
- **Planner** tab for task board (optional for groups)

## Screen share & whiteboard

- Share **window** not full screen (notification privacy)
- Whiteboard for brainstorming; export snapshot to Files when done

## Copilot in Teams (where licensed)

- "Summarize what I missed in this channel this week"
- "Draft meeting notes from the transcript"
- "List open action items from yesterday's call"

## Boundaries

- Git/code collaboration for CS projects → **`cursor-team-kit`** + repo, not Teams files as source of truth
- Group-work honesty and citation rules → **`citation-literacy`** plus the course AI-use policy
