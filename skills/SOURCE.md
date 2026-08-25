# Skill snapshot provenance

Copied 2026-08-25T10:16:01Z from this Cloud Agent environment so plugin updates cannot silently change the reviewed text.

| Pack | Path in this repo | Upstream | Resolved commit | Artifact digest |
|---|---|---|---|---|
| Cursor Cloud Agent | `skills/cursor-cloud/` | Cursor-managed (`~/.cursor/skills-cursor/`) | n/a (runtime install) | n/a |
| Vercel | `skills/vercel/` | https://github.com/vercel/vercel-plugin | `11c32588786a9d49791372657433b88d49561874` | `fcaf04110b2291a8ad2a4183c526418b` |
| Hugging Face | `skills/huggingface/` | https://github.com/huggingface/skills | `d7223848c3895fbd447faf2aec73e0a6cdd7fdcd` | `b2b203ceadbed932379b52d14298da23` |
| Hugging Face MCP router | `skills/huggingface/hf-mcp/` | Same plugin, `hf-mcp/skills/hf-mcp/` | same | same |
| Adobe App Builder | `skills/adobe/` | https://github.com/adobe/skills (`plugins/app-builder`) | `253f56901e058800ccb97ffd5bf1e3329d5f2e00` | `310a33933970fc5f1e1bc6abc0037542` |
| Supabase | `skills/supabase/` | https://github.com/supabase/agent-skills (via `supabase-community/cursor-plugin`) | `e5f7a7cfd697765848ffd6a4505f3c02e1ee17ee` | n/a |
| Cursor Team Kit (curated) | `skills/cursor-team-kit/` | https://github.com/cursor/plugins (`cursor-team-kit/skills/`) | `bdf7aa355337897f167153e05069aca505dae17c` | n/a |

Added 2026-08-25 after a gap analysis against the official Cursor Marketplace: `vercel-storage` documents Vercel Postgres/KV as sunset with no replacement guidance, and the pack had no error-tracking, database, or general PR/git-workflow skill at all. Supabase was picked over Neon per user request (their actual DB provider). Cursor Team Kit is curated, not vendored whole — see "What was excluded" below for the 10 skills left out of its 18.

## What was excluded

- Vercel `upstream/` vendored copies (byte-level duplicates of the live skill + references).
- Vercel plugin-author `.claude/skills/` (benchmark/release internals, not user-facing).
- Removed 2026-08-25: `skills/vercel/vercel-agent/` — pure product/pricing reference with no procedural content (no CLI, no code, no workflow steps); its one useful fact ("Vercel Agent: AI code reviews and production investigations. Public beta.") already lived in `knowledge-update/SKILL.md`, so nothing was lost.
- From `cursor-team-kit`'s 18 skills, only 8 directly on-topic for "GitHub PR/workflow" were vendored (`new-branch-and-pr`, `make-pr-easy-to-review`, `get-pr-comments`, `pr-review-canvas`, `fix-merge-conflicts`, `fix-ci`, `loop-on-ci`, `review-and-ship`). Left out as out-of-scope general team-productivity skills, not because of any quality issue: `control-cli`, `control-ui`, `verify-this`, `weekly-review`, `what-did-i-get-done`, `deslop`, `thermo-nuclear-code-quality-review`, `workflow-from-chats`, `run-smoke-tests`, `check-compiler-errors`. Also excluded: the `agents/` (ci-watcher, thermo-nuclear-code-quality-review subagents) and `rules/` components of the source plugin — this repo's convention (per the exclusions above) is to snapshot `skills/` only.

## Cross-pack trigger deconfliction (2026-08-25)

Adding the Supabase pack created a routing conflict with the Vercel pack, because Vercel's plugin treats Supabase as a **competitor to migrate off**, not as a provider in use. On any project importing `@supabase/supabase-js`, the Vercel skills would:

- pitch "Marketplace-native Neon Postgres + Upstash Redis **alternatives**" (`vercel-storage` chainTo), and
- pitch "**Clerk** as the recommended managed auth provider" for Supabase Auth (`vercel-storage` chainTo → `auth`),

while `vercel-storage` also claimed `supabase/**`, `lib/supabase.*`, and every `@supabase/{supabase-js,ssr}` install command as its own path/bash triggers — so three skills fired at once and two of them argued against the user's chosen stack.

That is correct behavior inside Vercel's own single-vendor plugin and wrong in a curated multi-vendor snapshot where Supabase is the deliberate choice. Patched (snapshot only; upstream packs unchanged):

| File | Change |
|---|---|
| `vercel/vercel-storage/SKILL.md` | Dropped `supabase/**` + `lib/supabase.*` pathPatterns, 8 `@supabase/*` bashPatterns, and the `@supabase/supabase-js` retrieval entity. Repointed both Supabase chainTo rules from `vercel-storage`/`auth` to `supabase`. Kept the "Supabase (Marketplace Native)" body section (provisioning on Vercel is legitimately its topic) and added an explicit handoff plus "do not propose migrating an existing Supabase project" note. |
| `vercel/marketplace/SKILL.md` | Pulled `@supabase/` out of the generic database chainTo and gave it a dedicated rule ahead of it targeting `supabase`. |
| `supabase/supabase/SKILL.md` | Narrowed the greedy `"Use when doing ANY task involving Supabase"` opener to a scoped "canonical source for Supabase development work", with explicit hand-offs to `vercel-storage`/`marketplace` for provisioning and to `supabase-postgres-best-practices` for generic Postgres tuning. |

**Ownership boundary now:** Supabase development (RLS, Auth, Edge Functions, SSR cookies, migrations) → `supabase`. Provisioning Supabase on Vercel, or comparing storage providers → `vercel-storage` / `marketplace`. Generic Postgres query/index tuning → `supabase-postgres-best-practices`.

## Layout

These files live under `skills/` rather than `.cursor/skills/` so this snapshot does not double-load alongside the installed plugins. To pin a Cloud Agent to this snapshot, copy or symlink a pack into `.cursor/skills/`.
