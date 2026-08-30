# ChatGPT port notes

Copied from [CatCorner22/Cursor_Skills](https://github.com/CatCorner22/Cursor_Skills) on 2026-08-30 and rewritten so ChatGPT and Codex can load the library.

## Format

| Cursor_Skills | ChatGPT_Skills |
|---|---|
| `.cursor/skills/` flatten | `.agents/skills/` flatten |
| `.cursor-plugin/plugin.json` | `.codex-plugin/plugin.json` |
| `.cursor-plugin/marketplace.json` | `.agents/plugins/marketplace.json` |
| `~/.cursor/skills` + `~/.cursor/plugins/local` | `~/.agents/skills` + `~/.codex/plugins` |
| `disable-model-invocation: true` | `agents/openai.yaml` → `policy.allow_implicit_invocation: false` |
| `metadata.sessionStart` on `proactive-agency` | `allow_implicit_invocation: true` plus repo `AGENTS.md` |
| Cursor `pathPatterns` / `promptSignals` / `overlay.yaml` / `validate` | Dropped (ChatGPT does not use them). Triggering is `description` + explicit `@`/`$` |
| Nested YAML `metadata` | String-to-string only, plus `host: chatgpt-codex` |

Each skill has `agents/openai.yaml` with `interface.display_name`, `short_description`, `default_prompt`, and `policy.products: [CHAT, CODEX]`.

## Host rewrites

Domain packs (Vercel, Hugging Face, LangChain, Adobe, Microsoft 365, …) keep their procedures. These host packs were rewritten:

| Skill | Cursor original | ChatGPT/Codex rewrite |
|---|---|---|
| `env-setup` | Cursor Cloud `environment.json` / snapshot builds | Skill load paths, marketplaces, `codex plugin marketplace add` |
| `canvas` | `.canvas.tsx` + `cursor/canvas` SDK | ChatGPT Canvas + Codex `artifacts/` files |
| `walkthrough-artifacts` | `RecordScreen` + `/opt/cursor/artifacts` | Host-agnostic screenshots/recordings + `artifacts/` |
| `subscribe` | `cursor-subscriptions-*` MCP | Scheduled tasks / timers; MCP tools only if present |
| `migrate-to-builds` | Cloud Agent environment builds | Checked-in `.agents` + plugin marketplace migration |
| `cursor-sdk` | `@cursor/sdk` only | Codex CLI + OpenAI Agents SDK first; Cursor SDK if named |

Legacy Cursor Cloud reference files under `skills/cursor-cloud/**/references/` were left in place as historical material. The `SKILL.md` files no longer send the agent through those Cursor MCP tools.

## What was not rewritten

- Review documents (`REVIEW.md`, `REVIEW-2.md`) still describe the Cursor snapshot they audited.
- Python runtime `scripts/ai_plugin_bundle.py` is unchanged; it is not a ChatGPT skill folder.
- Skill *bodies* for vendor platforms still mention their own CLIs and APIs.

## Invoke

ChatGPT: `@skill-name`. Codex: `$skill-name`.
