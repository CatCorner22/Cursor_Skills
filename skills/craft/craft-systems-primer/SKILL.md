---
name: craft-systems-primer
disable-model-invocation: true
description: "Router for operational craft frameworks in this library: OODA decision tempo, Toyota-style lean loops (small batches, andon, kaizen), and mise en place workspace prep. Use when prioritizing work, eliminating waste, preparing before execution, or when the user mentions OODA, lean, kaizen, kanban, mise en place, or getting organized before starting. Scope boundary: domain execution → academic/coding/m365/plaud packs; raw execution posture → `proactive-agency`."
metadata:
  priority: 8
  promptSignals:
    phrases:
      - "OODA loop"
      - "mise en place"
      - "lean workflow"
      - "kaizen"
      - "what should I do next"
      - "prioritize my work"
      - "eliminate waste"
    allOf:
      - [ooda, loop]
      - [mise, place]
      - [lean, waste]
    anyOf:
      - "Toyota Production System"
      - "small batches"
      - "stop the line"
    minScore: 6
---
# Craft systems primer

Meta-layer for **how to work**, not **what to build**. Three frameworks in this pack compose with every domain pack:

| Framework | Skill | One-line job |
|---|---|---|
| **Mise en place** | **`workspace-mise-en-place`** | Everything in reach *before* "heat" |
| **OODA × Lean** | **`ooda-lean-loop`** | Fast cycles + small batches + stop on failure |
| **Execution** | **`proactive-agency`** | Do the work; confirm only irreversible steps |

## When to load which

| Situation | Start here |
|---|---|
| About to start a task; files/env scattered | **`workspace-mise-en-place`** |
| Stuck, overwhelmed, or prioritizing | **`ooda-lean-loop`** |
| Both — new week or new project | **Mise first**, then OODA loop on first batch |
| Already mid-task with clear next step | Domain primer only (skip meta) |

## Fused loop (OODA × TPS)

Use for messy, multi-step work (semester, sprint, group project):

```
MISE     → workspace-mise-en-place (prep station)
OBSERVE  → raw signal only (syllabus, CI log, transcript, git status)
ORIENT   → current-state map: due dates, failures, unknowns
DECIDE   → one smallest batch with deliverable-first done definition
ACT      → domain skills execute the batch
ANDON    → if check fails, stop next work until fixed (real-time-testing / fix-ci)
KAIZEN   → one line: what waste do we remove next time?
```

**Coding stack:** `workspace-mise-en-place` → `deliverable-first` → `real-time-testing` → `loop-on-ci` → `clean-minimal-code`

**College stack:** `workspace-mise-en-place` → `outlook-email-calendar` → `onedrive-organization` → domain academic/plaud/m365 skills

## Mise en place × file organization

Mise is the **philosophy**; file organization is the **implementation**.

| Phase | Skills |
|---|---|
| **Prep (no heat)** | `onedrive-organization`, `outlook-email-calendar`, `env-setup`/`bootstrap`, Word styles before draft |
| **Service (execution)** | Domain pack for the task |
| **Breakdown (cleanup)** | Archive to `_Admin/Submitted/`, export via `plaud-export-integrate` |

## Domain routers

| Context | Router |
|---|---|
| College | `academic-ecosystem-primer` |
| Code | `coding-ecosystem-primer` |
| Office | `m365-ecosystem-primer` |
| Lectures | `plaud-ecosystem-primer` |
| AI pipeline hardening | `ai-transfer-ecosystem-primer` |

## Boundaries

- Does not teach TPS certification, military doctrine, or culinary technique history
- Does not replace domain expertise — only sequences existing skills
