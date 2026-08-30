---
name: onedrive-organization
description: 'Organize files in Microsoft OneDrive and SharePoint: folder structure for semesters, sharing links, permissions, version history, and sync. Use when storing coursework, sharing group files, or recovering previous document versions. Scope boundary: in-app editing → word/excel/powerpoint skills; Google Drive → not this pack.'
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: onedrive; sharepoint; share link; version history; sync files; OneDrive; SharePoint. Also /onedrive-organization.'
argument-hint: /onedrive-organization task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: 'Organize files in Microsoft OneDrive and SharePoint: folder structure for semesters, sharing links, permissions, version history, and sync'
  host: grok-build
  ported_from: Cursor_Skills
---
# OneDrive organization

**Rule:** **One source of truth** per file. No `essay_final_FINAL2.docx` — use version history instead.

**Mise en place:** This skill is the **file-station** half of prep — run **`workspace-mise-en-place`** before creating new work; use this skill to define *where* things live.

## Semester folder template

```
OneDrive/
  School/
    2026-Fall/
      BIOL-101/
        Syllabus/
        Lectures/
        Assignments/
        Exams/
      ENG-201/
        ...
      _Admin/          ← financial aid scans, registration PDFs
```

**File naming:** `YYYY-MM-DD_CourseCode_AssignmentShort_v01.ext`

## Sharing & permissions

| Need | Setting |
|---|---|
| Classmate edit one file | Share → People → Can edit |
| Submit link to LMS | Share → Copy link → **Anyone with link** only if policy allows; prefer **Specific people** |
| View-only feedback | Can view |
| Stop sharing | Manage access → remove link |

**Never** put graded submissions in public links unless syllabus permits.

## Version history

- Right-click file → **Version history** → restore or compare
- Use instead of duplicate filenames
- Word/Excel/PPT auto-save when signed in

## Sync client

- Install OneDrive app; choose **Backup** for Desktop/Documents if desired
- **Files On-Demand:** cloud-only until opened (saves laptop space)
- Conflict copies: merge manually; pick newer version in version history

## SharePoint (team sites)

- Instructor may host course materials on SharePoint — **sync read-only** to local for offline
- Don't edit instructor files in place unless collaboration enabled

## Backup habit

- Critical work: also export PDF to `_Admin/Submitted/` after each upload
- End of semester: zip `2026-Fall/` to external drive

## Copilot context

Files in OneDrive are reachable by Copilot in Office when signed in — keep sensitive personal docs in a separate non-synced folder if needed.

## Boundaries

- LMS (Canvas/Blackboard) upload mechanics vary by school — follow portal UI
- Large media projects → consider separate storage; OneDrive quotas apply
