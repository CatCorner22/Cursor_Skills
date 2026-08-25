# Skill snapshot provenance

Copied 2026-08-25T10:16:01Z from this Cloud Agent environment so plugin updates cannot silently change the reviewed text.

| Pack | Path in this repo | Upstream | Resolved commit | Artifact digest |
|---|---|---|---|---|
| Cursor Cloud Agent | `skills/cursor-cloud/` | Cursor-managed (`~/.cursor/skills-cursor/`) | n/a (runtime install) | n/a |
| Vercel | `skills/vercel/` | https://github.com/vercel/vercel-plugin | `11c32588786a9d49791372657433b88d49561874` | `fcaf04110b2291a8ad2a4183c526418b` |
| Hugging Face | `skills/huggingface/` | https://github.com/huggingface/skills | `d7223848c3895fbd447faf2aec73e0a6cdd7fdcd` | `b2b203ceadbed932379b52d14298da23` |
| Hugging Face MCP router | `skills/huggingface/hf-mcp/` | Same plugin, `hf-mcp/skills/hf-mcp/` | same | same |
| Adobe App Builder | `skills/adobe/` | https://github.com/adobe/skills (`plugins/app-builder`) | `253f56901e058800ccb97ffd5bf1e3329d5f2e00` | `310a33933970fc5f1e1bc6abc0037542` |

## What was excluded

- Vercel `upstream/` vendored copies (byte-level duplicates of the live skill + references).
- Vercel plugin-author `.claude/skills/` (benchmark/release internals, not user-facing).

## Layout

Canonical copies live under `skills/`. They are also activated as project skills via `.cursor/skills/` (one symlink per skill) and as local plugins via `plugins/` + `./scripts/load-all.sh` → `~/.cursor/plugins/local/`. Marketplace plugins already installed for this user still load from `~/.cursor/plugins/cache/`; the local copies are the patched snapshot.
