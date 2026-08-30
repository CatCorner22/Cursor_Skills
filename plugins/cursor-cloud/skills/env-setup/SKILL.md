---
name: env-setup
description: Explain, inspect, configure, and troubleshoot ChatGPT Skills and Codex environments — where skills load, how plugins and marketplaces are registered, and how to test a local install. Use when the user asks about environment setup, skill discovery, ~/.agents/skills, .agents/plugins/marketplace.json, or Codex config.toml.
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# ChatGPT / Codex environment setup

Use this skill to explain how ChatGPT and Codex discover skills, and to inspect or fix this repository's install layout. Match the response to the request: explain a concept, audit configuration, or make a focused patch.

Cursor Cloud Agent `environment.json` / snapshot-build workflows are **out of scope**. If the user is still on Cursor Cloud, point them at the sibling [Cursor_Skills](https://github.com/CatCorner22/Cursor_Skills) repo.

## Where skills load

| Scope | Location | Use |
|---|---|---|
| Repo (cwd and parents) | `.agents/skills/<skill-name>/SKILL.md` | Check in skills for a project or this library |
| Repo marketplace | `.agents/plugins/marketplace.json` + `plugins/<pack>/` | Installable pack list in ChatGPT desktop / Codex |
| User | `~/.agents/skills/` | Personal skills across every repo |
| User plugins | `~/.codex/plugins/<pack>/` | Personal copies of this library's packs |
| User marketplace | `~/.agents/plugins/marketplace.json` | Personal plugin catalog |
| Admin | `/etc/codex/skills` | Machine-wide Codex defaults |
| System | Bundled with Codex (`skill-creator`, `plugin-creator`) | Always present |

Codex scans `.agents/skills` from the current working directory up to the repository root. Duplicate `name` values are not merged; both can appear in selectors.

ChatGPT discovers **plugin-bundled** skills (Chat, Work, desktop, mobile). Standalone skill folders work in the ChatGPT desktop app, Codex CLI, and the IDE extension.

## Invocation

| Surface | Explicit | Implicit |
|---|---|---|
| ChatGPT | `@skill-name` | Allowed only when `agents/openai.yaml` → `policy.allow_implicit_invocation` is `true` (or omitted, default true) |
| Codex CLI / IDE | `$skill-name` or `/skills` | Same policy flag |

In this library only `proactive-agency` sets `allow_implicit_invocation: true`. Everything else is explicit-invoke.

## Mental model

1. **Author** a skill as a folder with `SKILL.md` (`name` + `description` required) plus optional `scripts/`, `references/`, `assets/`, and `agents/openai.yaml`.
2. **Discover** it locally via `.agents/skills` / `~/.agents/skills`, or package it under `plugins/<pack>/skills/` with `.codex-plugin/plugin.json`.
3. **Distribute** by adding the plugin to `.agents/plugins/marketplace.json` (repo) or `~/.agents/plugins/marketplace.json` (personal).
4. **Enable** in ChatGPT desktop (Plugins Directory → this marketplace) or Codex (`codex plugin marketplace add`).
5. **Refresh** ChatGPT desktop or restart Codex after copies. Discovery lists are not hot-reloaded mid-turn.

## Optional skill metadata

Each skill should ship `agents/openai.yaml`:

```yaml
interface:
  display_name: "Human name"
  short_description: "One-line purpose"
  default_prompt: "Use $skill-name for this task."
policy:
  allow_implicit_invocation: false
  products: [CHAT, CODEX]
```

Do not put ChatGPT UI settings in `SKILL.md` `metadata` — that file is ignored for interface. Keep `SKILL.md` metadata to string-to-string keys only.

## This repo's layout

| Path | Role |
|---|---|
| `skills/<pack>/<skill>/` | Canonical skill source |
| `.agents/skills/<skill>` | Symlink flatten for Codex repo discovery |
| `plugins/<pack>/.codex-plugin/plugin.json` | One plugin per pack |
| `.agents/plugins/marketplace.json` | Repo marketplace listing every pack |
| `scripts/load-all.sh` | Copies skills to `~/.agents/skills` and plugins to `~/.codex/plugins` |

After cloning, run:

```bash
./scripts/load-all.sh
```

Then restart ChatGPT desktop or Codex. Add the repo as a marketplace if it is not already:

```bash
codex plugin marketplace add CatCorner22/ChatGPT_Skills
```

## Disable without deleting

In `~/.codex/config.toml`:

```toml
[[skills.config]]
path = "/path/to/skill/SKILL.md"
enabled = false
```

Restart Codex after editing.

## Safety

- Never put tokens, passwords, or private keys in `SKILL.md`, `plugin.json`, marketplace files, or chat output.
- Do not publish a plugin to the universal directory unless the user explicitly asks.
- Prefer instruction-only skills; add scripts only when the step must be deterministic.

## Response

Lead with the outcome. Include only the sections relevant to the request: load path, marketplace entry, invocation policy, or the exact file to edit.
