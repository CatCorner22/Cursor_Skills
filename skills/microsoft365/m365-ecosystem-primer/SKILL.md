---
name: m365-ecosystem-primer
description: "Router for Microsoft 365 work in this library: Word documents, Excel workbooks, PowerPoint decks, Outlook email/calendar, Teams collaboration, and OneDrive organization. Use when the user mentions Microsoft 365, Office, Word, Excel, PowerPoint, Outlook, Teams, OneDrive, SharePoint, or Copilot in Office apps. Scope boundary: Google Workspace → not covered; general academic writing craft → `academic-writing`; slide narrative without Office still uses `powerpoint-decks` for structure; coding assignments → `coding-ecosystem-primer`."
metadata:
  priority: 8
  promptSignals:
    phrases:
      - "microsoft 365"
      - "microsoft office"
      - "word document"
      - "excel spreadsheet"
      - "powerpoint"
      - "outlook"
      - "teams meeting"
      - "onedrive"
    allOf:
      - [word, document]
      - [excel, formula]
      - [powerpoint, slide]
      - [outlook, calendar]
    anyOf:
      - "Microsoft 365"
      - "Office 365"
      - "Copilot in Word"
      - "Copilot in Excel"
    minScore: 6
---

# Microsoft 365 ecosystem primer

Pick the **smallest skill** for the app the user is actually in. M365 skills assume **desktop or web** Office apps with a Microsoft 365 subscription unless stated otherwise.

## Decision table

| User intent | Load next |
|---|---|
| Essay, report, formatting, styles, track changes in Word | **`word-documents`** |
| Formulas, tables, charts, pivot basics in Excel | **`excel-workbooks`** |
| Slides, deck structure, speaker notes in PowerPoint | **`powerpoint-decks`** |
| Email tone, calendar, syllabus blocking in Outlook | **`outlook-email-calendar`** |
| Group project chat, meetings, channels in Teams | **`teams-collaboration`** |
| File naming, sharing links, version history | **`onedrive-organization`** |
| Academic argument/citations (app-agnostic) | **`academic-writing`** / **`citation-literacy`** |
| College assignment routing (any tool) | **`academic-ecosystem-primer`** |

## Copilot in Office (2026+)

Microsoft 365 Copilot supports **custom skills** via `SKILL.md` in OneDrive (Word, Excel, PowerPoint). Skills in this pack are **Cursor-compatible** and follow the same frontmatter + body format Copilot expects:

- Folder name **must match** `name` in frontmatter
- `description` drives when Copilot/Cursor activates the skill
- Body = step-by-step procedure

To use in Copilot: upload skill folder to your OneDrive **Copilot Skills** location or **Manage skills** in the app.

## Default workflows

**Written assignment in Word:**
```
onedrive-organization → word-documents → citation-literacy (if references)
```

**Data assignment in Excel:**
```
excel-workbooks → academic-writing (interpret results in prose) + citation-literacy
```

**Group presentation:**
```
teams-collaboration → powerpoint-decks
```

## Boundaries

| Topic | Owner |
|---|---|
| Google Docs/Sheets/Slides | Not this pack |
| LaTeX / show-your-work problem sets | `study-system` + `academic-writing` |
| Python/R data analysis code | `coding-ecosystem-primer` |
