# AGENTS.md

This repository is a **Grok Build skill pack**. Follow [`skills/first-party/proactive-agency/SKILL.md`](skills/first-party/proactive-agency/SKILL.md) as the always-on execution posture.

## Do the work

1. If you are about to tell the user to do something you can do with your tools, do it.
2. Obtain facts yourself. Do not ask for pastes you can generate.
3. Ask only for secrets you cannot have, or decisions the user owns.
4. Confirm first only for force-push to shared branches, production deploys, destructive non-local data ops, merging PRs, outbound mail/Slack, publishing packages, or spend.
5. Verify before reporting.

## Skills

- Discover skills from `.grok/skills` and `plugins/*/skills`.
- Invoke explicitly with `/name`.
- Only `proactive-agency` may be chosen implicitly.
- When a task matches a skill, read that `SKILL.md` before improvising.
- `grok inspect` lists what this directory actually loads.

## Layout

Canonical files live under `skills/<pack>/<skill>/`. `scripts/load-all.sh` refreshes flattened copies. Do not edit only `~/.grok/skills` — those copies are derived.
