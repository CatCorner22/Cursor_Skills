---
name: walkthrough-artifacts
description: Create walkthrough artifacts (screenshots, recordings, and Codex file proofs) that show code changes work. Use when finishing tested changes and attaching demo evidence for the user.
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Walkthrough artifacts

When changes are complete and testing is done, demonstrate that the work works. If the user asked for specific manual testing, demonstrate that too.

Use **walkthrough artifacts** — real screenshots, recordings, or command output from the change you made. Embed images in the reply with markdown (`![label](path)`) or HTML when the host supports it.

Cursor `RecordScreen` / `computerUse` / `/opt/cursor/artifacts` paths are optional leftovers. Prefer the tools actually in this session (browser, shell, ChatGPT file attach, Codex workspace files).

## When to use

Use walkthrough artifacts to (1) show the code change works and (2) show any user-requested manual test was completed.

## What makes a good artifact

Good: a screenshot of the implemented UI; a short recording of the happy path; a recording or screenshot of the exact test the user asked for.

Bad — do not attach:
- A recording of a test that failed (fix it and retry)
- Setup tourism, failed attempts, or redundant near-duplicates
- Toy or fake examples

**Rule:** upload the minimal set that proves the change and the requested tests. Videos often cover an end-to-end path with fewer files.

## Creating an artifact

### Screenshots

Drive the UI with the browser or desktop tools you have. Keep only the frames that prove the change.

### Video

For GUI work, a short recording is usually the best proof.

1. Set up the test (open the UI, reach the feature).
2. Start recording with the available recorder (ChatGPT desktop capture, Codex/browser recorder, or `RecordScreen` if present).
3. Exercise the working change.
4. Stop immediately after the proof. Save only if it succeeded; discard, fix, and retry if it failed.

Start the recording right before the test. Split unrelated tests into separate recordings.

## Saving

- ChatGPT: attach the files to the turn or place them where the product asks for uploads.
- Codex: write keepers under `artifacts/` in the workspace (`screenshot_button_color_after.png`, `demo_checkout_flow.mp4`) and link those paths.
- Snake_case, descriptive names. Video names must describe the whole clip.
- Do not overwrite an already-shared file; add a new unique name.

Before citing a video, actually review it. Describe only what you confirmed.
