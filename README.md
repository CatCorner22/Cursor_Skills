# Cursor_Skills

Versioned snapshot of every skill loaded in the Cloud Agent session that reviewed them, plus a line-by-line review.

- **Snapshot:** [skills/](skills/) — 90 `SKILL.md` files (Cursor Cloud, Vercel, Hugging Face, Adobe, Supabase, Cursor Team Kit, Playwright, Cursor SDK, plus two first-party skills authored here). Provenance in [skills/SOURCE.md](skills/SOURCE.md).
- **Review:** [REVIEW.md](REVIEW.md) — findings after reading each skill file (original pass). A follow-up independent re-verification against all 63 original skills — confirming most findings, correcting some, and surfacing additional security issues and a router-config drift bug — is summarized in the PR that added Supabase/Cursor Team Kit and applied fixes for both passes.

These copies are for stability and review. They are not installed as project skills unless you copy them into `.cursor/skills/`.

## Packs

| Pack | Skills | What it covers |
|---|---|---|
| [Vercel](skills/vercel/) | 33 | Next.js, deployments, AI SDK/Gateway, auth, storage, sandbox, workflow |
| [Hugging Face](skills/huggingface/) | 26 | Model/dataset Hub, Spaces, training (LLM/vision/sentence-transformers), Gradio |
| [Adobe App Builder](skills/adobe/) | 10 | Runtime actions, CI/CD, project scaffolding, UI, E2E testing |
| [Cursor Cloud Agent](skills/cursor-cloud/) | 5 | Cloud Agent environment setup, canvas artifacts, event subscriptions |
| [Cursor Team Kit](skills/cursor-team-kit/) | 8 | GitHub PR/branch workflow: new-branch-and-pr, PR review, CI fixes, merge conflicts |
| [Supabase](skills/supabase/) | 2 | Postgres best practices, general Supabase (Auth/Storage/Edge Functions/RLS) |
| [Playwright](skills/playwright/) | 3 | General (non-Adobe) browser automation, component testing, trace inspection |
| [Cursor SDK](skills/cursor-sdk/) | 1 | Driving Cursor agents from code (`@cursor/sdk`) — CI, scripts, backends |
| [First-party](skills/first-party/) | 2 | `proactive-agency` — always-on execution posture; `skill-library-audit` — audits this library's own routing metadata, ships a runnable analyzer |

`vercel-agent` (pure product/pricing reference, no procedure) was removed from the Vercel pack — see [skills/SOURCE.md](skills/SOURCE.md) for what was cut and why.
