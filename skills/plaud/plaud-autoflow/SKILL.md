---
name: plaud-autoflow
disable-model-invocation: true
description: "Configure Plaud AutoFlow: automatic device-to-app transfer, auto-transcription, auto-summary with chosen template and LLM, and email delivery. Use when automating repetitive Plaud pipelines for lectures or recurring meetings. Scope boundary: one-off summary edits → `plaud-summary-templates`; export destinations → `plaud-export-integrate`."
metadata:
  priority: 6
  promptSignals:
    phrases:
      - "plaud autoflow"
      - "automatic transcription"
      - "auto summarize"
      - "email summary plaud"
    allOf:
      - [plaud, auto]
      - [autoflow, plaud]
    anyOf:
      - "AutoFlow"
      - "auto generation"
    minScore: 6
---
# Plaud AutoFlow

**Rule:** Automate **stable** pipelines only — same course, same template, same delivery. Re-tune each semester.

## AutoFlow stages

```
Device record → auto sync to app → auto transcribe → auto summarize → deliver (email / app notification)
```

Configure in **Plaud App / Web → AutoFlow** (exact UI labels may vary by version).

## Recommended presets

### Lecture pipeline (student)

| Setting | Value |
|---|---|
| Trigger | On sync from device |
| Language | Course primary language |
| Template | Custom `Lecture-study` (see `plaud-summary-templates`) |
| LLM | Default or Pro tier if subscribed |
| Delivery | Email to self + keep in app |

### Weekly meeting pipeline (work)

| Setting | Value |
|---|---|
| Template | Meeting / Action items |
| Multidimensional | Enable action-item view |
| Delivery | Email + forward to team rules manually (no secret recordings) |

## Guardrails

- **Review before forward** — AutoFlow can mis-hear names/dates; don't auto-forward to professors/clients without scan
- **Quota burn:** auto-transcribe every hallway test clip → exhaust 300 min/month
- **Template lock:** wrong template on AutoFlow is expensive to undo at scale — test once manually first

## Failure handling

| Symptom | Check |
|---|---|
| No summary after sync | WiFi, app background refresh, minutes quota |
| Wrong language | Disable auto-detect; set fixed language |
| Generic summary | Switch template or add custom vocabulary first |
| Missing email | Spam folder; reconnect mail in Plaud settings |

## When NOT to use AutoFlow

- Sensitive conversations needing manual consent log
- Recordings you'll delete unprocessed
- One-off interviews where template varies

## Boundaries

- Automation ≠ approval to record without consent
- Pair with **`plaud-export-integrate`** for Word/OneDrive archival after email
