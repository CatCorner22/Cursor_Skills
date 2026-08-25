# Cursor_Skills

Versioned snapshot of every skill loaded in the Cloud Agent session that reviewed them, plus a line-by-line review, plus a loader that activates them as Cursor project skills and local plugins.

- **Snapshot:** [skills/](skills/) — 63 `SKILL.md` files (Cursor Cloud, Vercel, Hugging Face, Adobe). Provenance in [skills/SOURCE.md](skills/SOURCE.md).
- **Review:** [REVIEW.md](REVIEW.md) — findings after reading each skill file. P0 bugs are patched in this tree.
- **Project skills:** [.cursor/skills/](.cursor/skills/) — one symlink per skill so Cursor / Cloud Agents load the patched snapshot.
- **Plugins:** [plugins/](plugins/) — Cursor plugin wrappers (Vercel, Hugging Face, Adobe App Builder, Cursor Cloud) with a [marketplace manifest](.cursor-plugin/marketplace.json).

## Load everything

From the repo root:

```bash
./scripts/load-all.sh
```

That script:

1. Flattens all 63 patched skills into `.cursor/skills/` and `~/.cursor/skills/`.
2. Downloads the pinned plugin commits (Vercel, Hugging Face, Adobe) when the network is available.
3. Installs full plugins into `~/.cursor/plugins/local/` and overlays the patched `SKILL.md` files.

A new Cursor window or Cloud Agent session picks them up. This chat’s already-injected catalog does not reload mid-turn.
