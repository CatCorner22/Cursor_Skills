---
name: migrate-to-builds
description: Migrate an ad-hoc ChatGPT/Codex skill install into a checked-in .agents layout plus a plugin marketplace. Use when the user wants skills to travel with the repo, to stop relying on ~/.agents/skills copies, or to follow a marketplace setup flow.
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Migrate to a checked-in marketplace

Use this skill when the user wants this machine's local skills to become a **repo-scoped ChatGPT/Codex marketplace**, or asks whether their current install will survive a fresh clone.

Cursor Cloud "environment builds" / `environment.json` snapshots are **out of scope**. That workflow lives in [Cursor_Skills](https://github.com/CatCorner22/Cursor_Skills).

Do not publish to the universal plugin directory unless the user explicitly asks.

## Mental model

| Layer | Ad-hoc (before) | Checked-in (after) |
|---|---|---|
| Skills | Loose folders in `~/.agents/skills` | `skills/<pack>/<skill>/` in git, flattened by `scripts/load-all.sh` into `.agents/skills` |
| Packs | None | `plugins/<pack>/.codex-plugin/plugin.json` |
| Catalog | Memory / desktop UI only | `.agents/plugins/marketplace.json` |
| Teammates | Cannot see your local copies | Clone + `./scripts/load-all.sh` + restart |

Per-boot user copies (`~/.agents/skills`, `~/.codex/plugins`) are **derived**. Canonical files are the ones in git.

## Workflow

1. Inventory local skills: `find ~/.agents/skills .agents/skills skills -name SKILL.md`.
2. For each skill that is not already under `skills/<pack>/`, move it into the right pack (or `first-party/` if it is original).
3. Ensure each `SKILL.md` has `name` + `description` and an `agents/openai.yaml` with `interface` + `policy`.
4. Run `./scripts/load-all.sh` so `.agents/skills` symlinks and `plugins/*` wrappers refresh.
5. Confirm `.agents/plugins/marketplace.json` lists every pack with `source.path` starting with `./`.
6. Restart ChatGPT desktop or Codex. In Codex: `codex plugin marketplace add .` from the repo root if the marketplace is not already attached.
7. Invoke one skill explicitly (`@proactive-agency` or `$nextjs`) to prove discovery.

## Safety

- Never commit tokens or private keys.
- Do not enable implicit invocation on a skill just to make it "easier to find."
- Do not delete `~/.agents/skills` until the git copy is proven.

## Response

Lead with: which skills were only local, which pack they landed in, and the one command the user needs next (usually restart + one explicit invoke).
