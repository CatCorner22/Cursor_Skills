# Grok port notes

Copied from [CatCorner22/Cursor_Skills](https://github.com/CatCorner22/Cursor_Skills) on 2026-08-30 and rewritten so [Grok Build](https://docs.x.ai/build/features/skills-plugins-marketplaces) can load the library.

## Format

| Cursor_Skills | Grok_Skill_Pack |
|---|---|
| `.cursor/skills/` flatten | `.grok/skills/` flatten |
| `.cursor-plugin/plugin.json` | `plugins/<pack>/plugin.json` + `.grok-plugin/plugin.json` |
| `.cursor-plugin/marketplace.json` | `.grok-plugin/marketplace.json` (`source.type: local`) |
| `~/.cursor/skills` + `~/.cursor/plugins/local` | `~/.grok/skills` + `~/.grok/plugins` |
| `disable-model-invocation: true` | Kept — Grok native. Slash-only except `proactive-agency` |
| `metadata.sessionStart` | Dropped. `proactive-agency` omits `disable-model-invocation`; `AGENTS.md` loads the posture |
| `pathPatterns` | Grok `paths` (gitignore globs; hidden until a matching file is touched) |
| `promptSignals` | Grok `when-to-use` |
| Nested YAML `metadata` | String map: `author`, `short-description`, `host`, `ported_from` |
| `overlay.yaml` / `validate` | Dropped |

## Host rewrites

| Skill | Cursor original | Grok rewrite |
|---|---|---|
| `env-setup` | Cloud Agent `environment.json` | `.grok` load paths, `grok inspect`, `grok plugin marketplace add` |
| `canvas` | `.canvas.tsx` + `cursor/canvas` | Standalone `artifacts/` files |
| `walkthrough-artifacts` | `RecordScreen` | Host-agnostic screenshots/recordings |
| `subscribe` | `cursor-subscriptions-*` | Bounded waits; MCP tools only if present |
| `migrate-to-builds` | Environment builds | Checked-in `.grok` + marketplace migration |
| `cursor-sdk` | `@cursor/sdk` only | xAI / Grok API first; Cursor SDK if named |

## Invoke

Grok Build: `/skill-name`. Collision: `/pack:skill`.
