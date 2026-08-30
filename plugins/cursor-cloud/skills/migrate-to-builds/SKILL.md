---
name: migrate-to-builds
description: Migrate an ad-hoc Grok skill install into a checked-in .grok layout plus a .grok-plugin marketplace. Use when the user wants skills to travel with the repo or to stop relying on ~/.grok/skills copies.
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: checked-in marketplace; migrate local skills; .grok-plugin; grok plugin marketplace. Also /migrate-to-builds.'
argument-hint: /migrate-to-builds task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Migrate an ad-hoc Grok skill install into a checked-in .grok layout plus a .grok-plugin marketplace
  host: grok-build
  ported_from: Cursor_Skills
---
# Migrate to a checked-in marketplace

Cursor Cloud "environment builds" are **out of scope**. That workflow lives in [Cursor_Skills](https://github.com/CatCorner22/Cursor_Skills).

Do not publish to the xAI official marketplace unless the user explicitly asks.

| Layer | Ad-hoc (before) | Checked-in (after) |
|---|---|---|
| Skills | Loose folders in `~/.grok/skills` | `skills/<pack>/<skill>/` in git, flattened by `scripts/load-all.sh` into `.grok/skills` |
| Packs | None | `plugins/<pack>/plugin.json` |
| Catalog | Memory / TUI only | `.grok-plugin/marketplace.json` |
| Teammates | Cannot see your local copies | Clone + `./scripts/load-all.sh` + `grok inspect` |

## Workflow

1. Inventory: `find ~/.grok/skills .grok/skills skills -name SKILL.md`.
2. Move orphans into the right pack (or `first-party/`).
3. Ensure each `SKILL.md` has `name` + `description`. Explicit skills keep `disable-model-invocation: true`.
4. Run `./scripts/load-all.sh`.
5. Confirm `.grok-plugin/marketplace.json` lists every pack with a `./plugins/<pack>` source.
6. `grok plugin marketplace add .` from the repo root if needed, then `grok inspect`.
7. Invoke one skill (`/proactive-agency` or `/nextjs`) to prove discovery.

Never commit tokens. Do not delete `~/.grok/skills` until the git copy is proven.
