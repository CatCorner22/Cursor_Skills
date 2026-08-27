---
name: ooda-lean-loop
disable-model-invocation: true
description: "Run fused OODA and lean loops: observe raw signal, orient with current-state map, decide one small batch, act with standard work, andon on failure, kaizen one improvement. Use when stuck, prioritizing, fighting thrash, or reducing rework. Scope boundary: prep before loop → `workspace-mise-en-place`; coding batches → `deliverable-first` + `real-time-testing`; meta routing → `craft-systems-primer`."
metadata:
  priority: 8
  promptSignals:
    phrases:
      - "OODA"
      - "OODA loop"
      - "what should I do next"
      - "prioritize"
      - "kaizen"
      - "small batch"
      - "stop the line"
      - "too much WIP"
    allOf:
      - [prioritize, work]
      - [stuck, next]
    anyOf:
      - "OODA loop"
      - "lean loop"
      - "andon"
    minScore: 6
---
# OODA × lean loop

**Rule:** **Tempo beats perfection.** One complete small batch beats a perfect plan you never start.

## The loop (one pass = 15–90 minutes)

### 1. OBSERVE — raw signal only

Gather facts without interpreting yet:

| Domain | Observe via |
|---|---|
| Code | `git status`, CI (`loop-on-ci`), test output, logs |
| College | syllabus, LMS, `plaud-ask-queries`, calendar |
| Product | user report, metrics, `verification` |

**Anti-pattern:** deciding while still fetching data.

### 2. ORIENT — current-state map

Answer in writing (3–7 bullets):

- What is **due** and when?
- What is **broken** or failing checks?
- What is **unknown** (needs question to professor/PM)?
- What is **WIP** already in flight? (count — if >1, finish or kill one)

Pair with **`deliverable-first`** for coding or **`academic-ecosystem-primer`** for coursework.

### 3. DECIDE — one smallest batch

Pick **one** batch that:

- Has a **done definition** checkable today
- **Unblocks** the most downstream work
- Fits in the time box you have

**TPS constraint:** WIP limit = **1** active batch per course/project unless explicitly paired (e.g., lecture record + commute — different stations).

### 4. ACT — standard work

Execute using domain skills — do not invent a new process mid-batch.

| Batch type | Standard work stack |
|---|---|
| Code slice | `real-time-testing` RED→GREEN→REFACTOR |
| Essay section | `academic-writing` TEAL paragraph |
| Lecture | `plaud-lecture-notes` post-class routine |
| PR | `cursor-team-kit` → `review-and-ship` |

### 5. ANDON — stop the line

If a **quality check fails**, freeze new work on this stream:

| Signal | Andon action |
|---|---|
| Test red | Fix before next feature (`real-time-testing`) |
| CI red | `fix-ci` before new commits |
| No source for claim | Stop writing; `[NEED SOURCE]` |
| Recording policy unclear | Stop record; ask instructor |

**Do not** start the next batch with a red andon.

### 6. KAIZEN — one improvement

End every loop with exactly **one** line:

> "Next time, remove ___ waste by ___."

**Seven wastes (quick scan):**

| Waste | Student example | Dev example |
|---|---|---|
| Waiting | No rubric before draft | Blocked on env |
| Overprocessing | 10 summary templates | Gold-plating API |
| Rework | Wrong citation style | Fix in prod |
| Motion | File hunt | Context switching |
| Defects | Submit without spellcheck | Skip tests |
| Inventory | 5 draft essays open | 8 open PRs |
| Overproduction | Notes before lecture ends | Features no user asked for |

## When stuck (60-second version)

```
1. List everything on your mind (brain dump)
2. Circle ONE due date within 72h
3. Name smallest done for that item
4. Mise if missing files/tools (workspace-mise-en-place)
5. Act one batch; andon on failure
```

## Combine with mise en place

```
New week/project  → workspace-mise-en-place (once)
Each work session  → OODA loop (repeat)
Session end        → kaizen line + breakdown mise
```

## Boundaries

- Not a substitute for **`proactive-agency`** — still do the work, don't narrate loops endlessly
- Not for irreversible decisions without confirm-first list in proactive-agency
