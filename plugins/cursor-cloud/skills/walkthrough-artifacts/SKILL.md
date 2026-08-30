---
name: walkthrough-artifacts
description: Create walkthrough artifacts (screenshots, recordings, and file proofs) that show code changes work. Use when finishing tested changes and attaching demo evidence for the user.
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: demo screenshot; walkthrough video; prove the change works. Also /walkthrough-artifacts.'
argument-hint: /walkthrough-artifacts task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Create walkthrough artifacts (screenshots, recordings, and file proofs) that show code changes work
  host: grok-build
  ported_from: Cursor_Skills
---
# Walkthrough artifacts

When changes are complete and testing is done, demonstrate that the work works.

Cursor `RecordScreen` / `/opt/cursor/artifacts` paths are optional leftovers. Prefer the tools actually in this session (browser, shell, Grok file attach).

## What to keep

Good: a screenshot of the implemented UI; a short recording of the happy path; proof of the exact test the user asked for.

Bad — do not attach: failed tests, setup tourism, redundant near-duplicates, toy examples.

**Rule:** the minimal set that proves the change and the requested tests.

## Creating

1. Set up the test.
2. Capture with the available recorder or screenshot tool.
3. Exercise the working change.
4. Stop immediately after the proof. Discard, fix, and retry on failure.

Write keepers under `artifacts/` (`screenshot_button_color_after.png`, `demo_checkout_flow.mp4`) and link those paths. Snake_case, descriptive names. Review a video before citing it.
