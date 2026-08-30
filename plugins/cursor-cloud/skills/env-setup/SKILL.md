---
name: env-setup
description: Explain, inspect, configure, and troubleshoot Grok Build skill environments — where skills load, how plugins and marketplaces are registered, and how to test a local install. Use when the user asks about ~/.grok, .grok/skills, marketplace.json, grok inspect, or this library's install paths.
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: grok inspect; ~/.grok; .grok/skills; marketplace.json; grok plugin; skill discovery. Also /env-setup.'
argument-hint: /env-setup task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Explain, inspect, configure, and troubleshoot Grok Build skill environments — where skills load, how plugins and marketplaces are…
  host: grok-build
  ported_from: Cursor_Skills
---
# Grok Build environment setup

Use this skill to explain how Grok discovers skills and plugins, and to inspect or fix this repository's install layout.

Cursor Cloud Agent `environment.json` / snapshot-build workflows are **out of scope**. That material lives in [Cursor_Skills](https://github.com/CatCorner22/Cursor_Skills).

## Where skills load

| Scope | Location | Use |
|---|---|---|
| CWD / repo | `.grok/skills/<skill>/SKILL.md` | Check in skills for a project or this library |
| Repo marketplace | `.grok-plugin/marketplace.json` + `plugins/<pack>/` | Installable pack list |
| User | `~/.grok/skills/` | Personal skills across every repo |
| User plugins | `~/.grok/plugins/<pack>/` | Trusted personal copies |
| Extra | `[skills] paths` in `~/.grok/config.toml` | Extra roots |
| Compat | `.agents/skills`, `.claude/skills`, `.cursor/skills` | Grok reads these too |

Grok walks `.grok/skills` from the current working directory up to the repository root. Same-name skills: higher-priority scope wins. Plugin collisions stay available as `/plugin:skill`.

## Invocation

| Mode | How |
|---|---|
| Explicit | `/skill-name` (slash menu). Qualified form `/pack:skill` on collision. |
| Implicit | Only when `disable-model-invocation` is absent/false. In this library that is **only** `proactive-agency`. |

## This repo's layout

| Path | Role |
|---|---|
| `skills/<pack>/<skill>/` | Canonical skill source |
| `.grok/skills/<skill>` | Symlink flatten for Grok discovery |
| `plugins/<pack>/plugin.json` | One plugin per pack |
| `.grok-plugin/marketplace.json` | Marketplace index |
| `.grok-plugin/plugin-index.json` | Pre-install component catalog |
| `scripts/load-all.sh` | Copies to `~/.grok/skills` and `~/.grok/plugins` |

After cloning:

```bash
./scripts/load-all.sh
grok plugin marketplace add CatCorner22/Grok_Skill_Pack
grok plugin install vercel --trust
grok inspect
```

Start a new Grok session (or press `r` in `/plugins`) so newly copied skills appear.

## Disable without deleting

In `~/.grok/config.toml`:

```toml
[skills]
disabled = ["nyx"]
```

## Safety

- Never put tokens in `SKILL.md`, `plugin.json`, marketplace files, or chat output.
- Project plugins under `.grok/plugins/` require trust. User plugins under `~/.grok/plugins/` are auto-trusted.
- Do not publish to the xAI official marketplace unless the user explicitly asks.

## Response

Lead with the outcome. Include only the load path, marketplace entry, or file to edit.
