---
name: plaud-recording-capture
description: 'Capture audio with Plaud devices and app: in-person vs phone-call mode, press-to-highlight, placement, battery, consent, and recording hygiene. Use when starting a Plaud recording, choosing Note vs NotePin, or improving capture quality. Scope boundary: post-capture transcription → `plaud-transcription`; legal advice → remind user of local consent laws only.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Plaud recording & capture

**Rule:** **Consent first**, then **placement**, then **highlights** for anything you'll need later.

## Consent & ethics

- **Many jurisdictions require all-party consent** to record conversations — especially phone calls and classrooms
- Ask instructor before recording lectures if policy is unclear
- Inform meeting participants when recording starts
- Do not publish transcripts of others without permission

## Device selection

| Device | Best for |
|---|---|
| **Plaud Note** | Table meetings, phone calls (dual-mode), interviews |
| **Plaud NotePin / NotePin S** | All-day wear, quick hallway/coffee captures |
| **Plaud Note Pro** | Larger rooms, longer battery, pro audio pickup |

## Dual-mode (Note)

- **In-person:** device on table, mic toward speakers, minimize rustling
- **Phone call:** attach per device instructions; hold steady near phone mic/speaker path
- Same one-touch workflow — summaries work identically after sync

## Press to highlight (Intelligence 3.0+)

- **Short press** on device or **tap in app** when you hear: exam hint, due date, key definition, action item
- Highlights signal Plaud Intelligence what matters → better summaries and Ask Plaud citations
- Habits: highlight **sparingly** (5–10 per hour max) or noise drowns signal

## Capture hygiene

| Do | Don't |
|---|---|
| Start recording before content begins | Start mid-sentence after missing setup |
| State context verbally ("Biology 101, lecture 7, mitosis") | Assume title auto-detection is enough |
| Keep device charged; know ~30hr spec is marketing max | Let battery die mid-exam review session |
| Minimize bag rustle, keyboard, open drinks | Cover mic with hand/finger |

## Sync path

1. Record on device → WiFi/Bluetooth sync to **Plaud App**
2. Verify file appears before leaving venue (no sync = no backup)
3. Optional: **AutoFlow** for hands-off transcribe + summarize → **`plaud-autoflow`**

## Naming & organization (app)

Rename files early: `YYYY-MM-DD_Course_LectureTopic` — matches **`onedrive-organization`** if exporting later.

## Boundaries

- Not a substitute for attending class — transcript lags and misses board work
- Online Zoom/Teams native bots → different tools; Plaud can still capture room audio if legal
