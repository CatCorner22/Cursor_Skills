# ChatGPT compatibility adaptation — v1.0.0

Completed 2026-09-24 from source commit `6f3febcd0490107ad7b300743b385f3db3f1169c`.

## Delivered

- All 189 skills across all 19 packs have ChatGPT instruction adapters, full workflow bodies, runtime compatibility constraints, source metadata, and OpenAI invocation metadata.
- All 673 exported source-file hashes were verified. The original source scripts were not executed.
- 188 skills remain explicit-only. `proactive-agency` is the only implicit-eligible posture; it has no automatic startup hook and grants no additional permissions.
- 31 targeted change records cover 19 AI-transfer rewrites, the proactive-agency rewrite, known content corrections, and formatting repairs.
- 16 structural and regression tests passed. These are package tests, not live tests of 189 external integrations.
- Searchable Markdown copies of all 19 packs, the loader, inventory, compatibility rules, validation report, and complete/plugin/local-marketplace archives were saved in the requesting user's ChatGPT Library. Retrieval of the loader and an adapted coding workflow succeeded.

**Native ChatGPT account-wide plugin installation was not performed or verified.** Library storage and instruction use do not register a native @menu entry. A supported product installation surface is still required.

The generated plugin is distributed in the ChatGPT delivery and the user's Library, not as a full generated tree in this branch. This branch contains the isolated source-export workflow and these adaptation notes. It does not replace or modify the original `skills/` files, Cursor configuration, or `main`.

## Delivered archives

| File | SHA-256 |
|---|---|
| Cursor_Skills_ChatGPT_Complete_v1.0.0.zip | `f08237bc10c2e5066b043eb405fdd51a4ab8adf4d201742be02cd0852e2b22c1` |
| Cursor_Skills_ChatGPT_Plugin_v1.0.0.zip | `c1c3e142fd38a27871db2e72bb8b11a09a2db079812b4fd64c3b0ad1ee5dd18f` |
| Cursor_Skills_ChatGPT_Local_Marketplace_v1.0.0.zip | `fec1128c0db8b3039909c9f0553dae097987e4811d8700ef58411489e5ec57a8` |

The complete archive includes the adapter toolkit, tests, source inventory, per-file checksums, and the 19 searchable Library packs. The plugin-only archive has one plugin root. The local-marketplace archive has `.agents/plugins/marketplace.json` pointing at `./plugins/cursor-skills-chatgpt`.

## Important revisions

The compatibility contract requires genuine tool discovery, connected-data reads before personalized conclusions, authority checks independent of reversibility, safe credential handling, current primary-source verification, and honest differentiation between static review, simulation, and executed tests. It does not assume Cursor tools, hidden model settings, telemetry, independent agents, persistent memory, or background execution exist in ChatGPT.

Known source corrections include the LangChain InMemoryVectorStore import, APA guidance for unpaginated quotations, an unsupported Plaud export count, a future-dated serving-image assertion, a runtime-enabled-count overclaim, and a local-runtime restriction-bypass passage. Vendor defaults are not universal recommendations.

All 189 skills are retained. Twenty-seven large Nyx reference images remain pinned source references instead of being embedded in the shared plugin. Source metadata and available notices are retained. The separate 100-plugin Python runtime is not installed or started.

## Use and installation boundaries

Reference use: ask to use a named skill or the relevant Cursor Skills pack. Retrieve the adapted workflow and apply only the relevant skills. Do not inject all 189 workflows into every response.

Native use: consult the current official OpenAI local-marketplace/plugin documentation and use the supported desktop product surface. A metadata policy permitting implicit invocation is not proof of account installation, startup execution, or broader authority.

Official references checked 2026-09-24:
- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins/build/skills
- https://developers.openai.com/codex/build-skills
- https://developers.openai.com/plugins/deploy/submission-errors

Do not publish this multi-vendor collection to a public directory without verifying redistribution rights and completing the host's submission validation.

## Source-export workflow

The export workflow is restricted to this compatibility branch and changes to its own workflow file. It reads the public source pinned to the commit above, skips symlinks and fonts, checks file-size limits and skill count, and exports a hash inventory. It has read-only repository permissions, a short timeout and three-day artifact retention. It does not run repository code, install dependencies, read secrets, deploy services, or configure a ChatGPT account.

The source-export run completed successfully: GitHub Actions run `36058476528`.
