# Cursor_Skills

Versioned snapshot of every skill loaded in the Cloud Agent session that reviewed them, plus a line-by-line review.

- **Snapshot:** [skills/](skills/) — 132 `SKILL.md` files across 17 packs (Cursor Cloud, Vercel, Hugging Face, LangChain, Adobe, Supabase, Cursor Team Kit, Playwright, Cursor SDK, Pydantic AI, Prompt Optimizer, **Coding**, **Academic**, **Microsoft 365**, **Plaud**, **Projects**, plus four first-party skills authored here). Provenance in [skills/SOURCE.md](skills/SOURCE.md).
- **Coding pack gap analysis:** [docs/CODING-PACK-GAP-ANALYSIS.md](docs/CODING-PACK-GAP-ANALYSIS.md)
- **Review:** [REVIEW.md](REVIEW.md) — findings after reading each skill file (original pass). A follow-up independent re-verification against all 63 original skills — confirming most findings, correcting some, and surfacing additional security issues and a router-config drift bug — is summarized in the PR that added Supabase/Cursor Team Kit and applied fixes for both passes.

**Loaded in this repo.** `.cursor/skills/` has one symlink per skill so Cursor / Cloud Agents pick up the snapshot. Plugin wrappers live under `plugins/`. To refresh this machine (project skills, `~/.cursor/skills/`, and `~/.cursor/plugins/local/`):

```bash
./scripts/load-all.sh
```

## Packs

| Pack | Skills | What it covers |
|---|---|---|
| [Vercel](skills/vercel/) | 33 | Next.js, deployments, AI SDK/Gateway, auth, storage, sandbox, workflow |
| [Hugging Face](skills/huggingface/) | 26 | Model/dataset Hub, Spaces, training (LLM/vision/sentence-transformers), Gradio, SageMaker |
| [LangChain](skills/langchain/) | 12 | LangChain/LangGraph agents, RAG, persistence, human-in-the-loop, LangSmith online evals, Deep Agents |
| [Adobe App Builder](skills/adobe/) | 10 | Runtime actions, CI/CD, project scaffolding, UI, E2E testing, Workfront |
| [Cursor Team Kit](skills/cursor-team-kit/) | 8 | GitHub PR/branch workflow: new-branch-and-pr, PR review, CI fixes, merge conflicts |
| [Cursor Cloud Agent](skills/cursor-cloud/) | 5 | Cloud Agent environment setup, canvas artifacts, event subscriptions |
| [First-party](skills/first-party/) | 4 | `proactive-agency` — always-on execution posture; `skill-library-audit` — audits this library's own routing metadata, ships a runnable analyzer; `smolagents` — Hugging Face's agent framework; `v0` — Vercel's v0 Platform/Model API |
| [Playwright](skills/playwright/) | 3 | General (non-Adobe) browser automation, component testing, trace inspection |
| [Supabase](skills/supabase/) | 2 | Postgres best practices, general Supabase (Auth/Storage/Edge Functions/RLS) |
| [Cursor SDK](skills/cursor-sdk/) | 1 | Driving Cursor agents from code (`@cursor/sdk`) — CI, scripts, backends |
| [Prompt Optimizer](skills/prompt-optimizer/) | 1 | Authoring and optimizing prompt text itself — layering, few-shot, eval slices |
| [Pydantic AI](skills/pydantic-ai/) | 1 | Python agent framework — typed deps/outputs, tools, streaming |
| [Coding](skills/coding/) | 7 | Deliverable-first, clean minimal code, stable architecture, real-time testing, UI/UX engineering |
| [Academic](skills/academic/) | 3 | College coursework router, academic writing, citation literacy (pack expanding) |
| [Microsoft 365](skills/microsoft365/) | 7 | Word, Excel, PowerPoint, Outlook, Teams, OneDrive — Copilot-compatible SKILL.md format |
| [Plaud](skills/plaud/) | 8 | AI voice recorder: capture, transcription, summaries, Ask Plaud, AutoFlow, lecture notes, export |
| [Projects](skills/projects/) | 1 | Project reference material, not capability skills — `nyx` character bible with reference sheets |
| **Total** | **132** | reconciles with `find skills -name SKILL.md \| wc -l` |

`vercel-agent` (pure product/pricing reference, no procedure) was removed from the Vercel pack. The LangChain pack is 12 of 22 upstream skills, and Cursor Team Kit 8 of 18 — see [skills/SOURCE.md](skills/SOURCE.md) for what was cut and why, and for the cross-pack trigger deconfliction applied to `vercel/ai-sdk` and `vercel/build-agents` so they stop steering off other packs' frameworks.
