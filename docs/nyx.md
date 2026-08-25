# Nyx — Character Bible

**Moved.** The canonical bible now lives as a loadable skill so it travels with the rest of the library:

→ **[`skills/projects/nyx/SKILL.md`](../skills/projects/nyx/SKILL.md)**

Reference images moved with it, to [`skills/projects/nyx/assets/`](../skills/projects/nyx/assets/), so the skill directory is self-contained — `scripts/load-all.sh` copies each skill dir wholesale, so the images travel into `~/.cursor/skills/nyx/` alongside the text.

Edit the skill file directly; do not re-add a second copy here. A duplicate would be the config-drift class recorded in [`skills/SOURCE.md`](../skills/SOURCE.md) — two copies of the same content where edits land in one and the other silently goes stale.
