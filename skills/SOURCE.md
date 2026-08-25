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
| First-party (authored here) | `skills/first-party/` | **Not vendored** — written in this repo | n/a | n/a |
| Playwright | `skills/playwright/` | https://github.com/microsoft/playwright (`packages/playwright-core/src/tools/skills/`) | `f46278a` | n/a |
| Cursor SDK | `skills/cursor-sdk/` | https://github.com/cursor/plugins (`cursor-sdk/skills/`) | `bdf7aa355337897f167153e05069aca505dae17c` | n/a |

### Upstream re-sync, 2026-08-25

Three already-pinned upstreams had shipped new skills since they were snapshotted. Verified by cloning each upstream and diffing against the vendored set, not by trusting a summary:

| Pack | New skills pulled in |
|---|---|
| Hugging Face | `hf-mem` (exact memory footprint for Safetensors/GGUF from the Hub) + 6 `hf-cloud-*` SageMaker skills: `sagemaker-deployment-planner`, `aws-context-discovery`, `sagemaker-iam-preflight`, `serving-image-selection`, `sagemaker-production-defaults`, `python-env-setup` |
| Vercel | `create-a-backend` — routes between Functions, Services, containers, Workflow, Queues, and Marketplace databases |
| Adobe | `appbuilder-workfront` umbrella + nested `workfront-actions`, `workfront-ui-extension`, `workfront-local-testing` |

The raw Vercel diff also surfaced `*/upstream` duplicate copies and `benchmark-*` / `release` / `plugin-audit` / `vercel-plugin-eval` maintainer internals — both already covered by the exclusions above, so neither was pulled in. `vercel-agent` appears in that diff only because this repo deliberately removed it.

**Playwright** fills a gap earlier review passes wrongly concluded was unfillable at this repo's provenance bar. `microsoft/playwright` ships three user-facing skills inside the package tree (`playwright-cli` 426 lines + 9 references, `playwright-component-testing` 143 lines + 4 references + 4 templates, `playwright-trace` 174 lines). It also carries four skills under `.claude/skills/` (`playwright-dev`, `playwright-devops`, `playwright-triage`, `playwright-test-results`) — those are maintainer dev-workflow internals and were excluded under the same rule already applied to Vercel's plugin-author skills. This is the repo's first general (non-Adobe) automated-testing coverage.

**Cursor SDK** was added because a whole-tree grep for `@cursor/sdk`, `CURSOR_API_KEY`, `Agent.create`, `Agent.resume`, and `/v1/agents` returned zero hits across all prior skills — it closes the loop between the `cursor-cloud` and `cursor-team-kit` packs by driving Cursor agents from code. Same upstream and same pinned commit already used for `cursor-team-kit`.

Added 2026-08-25 after a gap analysis against the official Cursor Marketplace: `vercel-storage` documents Vercel Postgres/KV as sunset with no replacement guidance, and the pack had no error-tracking, database, or general PR/git-workflow skill at all. Supabase was picked over Neon per user request (their actual DB provider). Cursor Team Kit is curated, not vendored whole — see "What was excluded" below for the 10 skills left out of its 18.

## What was excluded

- Vercel `upstream/` vendored copies (byte-level duplicates of the live skill + references).
- Vercel plugin-author `.claude/skills/` (benchmark/release internals, not user-facing).
- Removed 2026-08-25: `skills/vercel/vercel-agent/` — pure product/pricing reference with no procedural content (no CLI, no code, no workflow steps); its one useful fact ("Vercel Agent: AI code reviews and production investigations. Public beta.") already lived in `knowledge-update/SKILL.md`, so nothing was lost.
- From `cursor-team-kit`'s 18 skills, only 8 directly on-topic for "GitHub PR/workflow" were vendored (`new-branch-and-pr`, `make-pr-easy-to-review`, `get-pr-comments`, `pr-review-canvas`, `fix-merge-conflicts`, `fix-ci`, `loop-on-ci`, `review-and-ship`). Left out as out-of-scope general team-productivity skills, not because of any quality issue: `control-cli`, `control-ui`, `verify-this`, `weekly-review`, `what-did-i-get-done`, `deslop`, `thermo-nuclear-code-quality-review`, `workflow-from-chats`, `run-smoke-tests`, `check-compiler-errors`. Also excluded: the `agents/` (ci-watcher, thermo-nuclear-code-quality-review subagents) and `rules/` components of the source plugin — this repo's convention (per the exclusions above) is to snapshot `skills/` only.

## First-party pack (`skills/first-party/`)

Unlike every other pack, this one has no upstream and no pinned commit — it is authored in this repo, so it carries no vendor-drift risk and no obligation to stay byte-identical to anything.

**`proactive-agency`** — an always-on execution posture: do the work rather than describe it. It is delivered via `metadata.sessionStart: true` + `priority: 10`, the same mechanism `vercel/knowledge-update` uses, which means it is *injected* rather than trigger-matched. That choice is deliberate: this repo's documented dominant defect class is over-triggering and cross-pack trigger collision, and a session-start skill adds **zero** trigger surface. Its `pathPatterns`/`bashPatterns`/`importPatterns` are explicitly empty for the same reason.

Design notes worth preserving if this file is ever edited:

- The load-bearing content is the five-step gate at the top. Everything below it is a branch of that gate; deleting the gate guts the skill.
- The **confirm-first table is deliberately narrow** and paired — each row names both the action needing confirmation and its permitted near-twin (e.g. *deploy to production* vs *preview deploys*; *destructive DB ops* vs *writing and locally applying migrations*). Widening this table is the main way to break the skill: every extra row is a pre-authorized excuse to hand work back to the user, which is exactly what it exists to prevent. The catch-all reversibility test (`git checkout` / `git revert` / delete a file / local rollback ⇒ just do it) is what keeps unlisted cases defaulting to action.
- Clarifying questions are explicitly *unlimited* — the user's request was to minimize handoffs, not questions. The Legitimate/Illegitimate table encodes that split; do not "tighten" it into a general discouragement of asking.
- It was drafted three ways (rule-system, anti-pattern catalog, decision-procedure) and scored by three judges — one scoring specifically for whether lines are self-detectable mid-response rather than exhortation, one for whether the safety boundary could be abused as a laziness loophole, one for context density. It is injected into every session, so any future edit should hold the same bar: no line that a model would nominally agree with but not act on.

## Deconfliction applied to the 2026-08-25 re-sync

Newly vendored skills were checked for trigger collision against the existing set *before* landing, rather than after — the failure mode that caused the two defects recorded below. Four needed narrowing:

| Skill | Problem | Fix |
|---|---|---|
| `hf-cloud-python-env-setup` | Claimed **all** Python work — "whenever Python code will be executed… when about to run `pip install`… when the user asks to 'set up the environment'". Three existing HF skills (`huggingface-llm-trainer`, `huggingface-community-evals`, `huggingface-vision-trainer`) run Python/uv, so it would have hijacked every training task with AWS-specific advice. | Scoped to AWS/SageMaker only, with an explicit hand-off naming the four HF skills that own their own uv / PEP-723 environments. |
| `playwright-cli` | Shipped with a bare 12-word description and **no** scoping metadata at all, so it matched on the word "Playwright" — colliding with `appbuilder-e2e-testing` (which explicitly claims "Playwright", "browser test", "headless browser test") and `vercel-sandbox` (headless Chrome automation). | Added a scope boundary: Adobe ExC/AEM E2E → `appbuilder-e2e-testing`; Vercel Sandbox headless Chrome → `vercel-sandbox`; this skill owns local and CI Playwright everywhere else. |
| `playwright-component-testing` | Milder overlap with `appbuilder-testing` (Jest + React Testing Library) on "test React components in isolation". | Added a one-line boundary pointing Adobe Jest/RTL work at `appbuilder-testing`. |
| `cursor-sdk` | Its description claimed agent-automation prompts "even if they don't explicitly name the package", which would steal generic "build me an agent" prompts from `build-agents` / `eve`. | Replaced that clause with an explicit boundary: this skill is only for driving Cursor's own coding agent from code. |

**Security note on the vendored `hf-cloud-*` scripts.** All 11 Python scripts were scanned before landing: no `eval`/`exec`, no `shell=True` (every `subprocess.run` uses list-form arguments), no pickle loads, no hardcoded credentials. One upstream design decision worth knowing about rather than discovering later — `hf-cloud-sagemaker-iam-preflight/scripts/create_role.py:33,89` attaches the AWS managed policy `AmazonSageMakerFullAccess` to the execution role it creates. That is a broad grant. It is Hugging Face's upstream default and is left unmodified here (narrowing it would change what the skill actually does), but anyone running it against a production AWS account should scope the role down.

`hf-cloud-aws-context-discovery` is greedy *within AWS* ("before any other AWS work") but was left as-is — the repo has no other AWS content, so there is nothing for it to collide with. `create-a-backend` needed no change: it already ships paired `allOf` signals and `minScore: 6`. `hf-mem` got a non-collision cross-reference clarifying its relationship to `huggingface-best` (which solves the inverse problem: memory budget → which models fit).

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
