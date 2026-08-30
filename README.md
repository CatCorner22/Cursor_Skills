# ChatGPT_Skills

Intended GitHub repo: **[CatCorner22/ChatGPT_Skills](https://github.com/CatCorner22/ChatGPT_Skills)**.

ChatGPT and Codex port of [CatCorner22/Cursor_Skills](https://github.com/CatCorner22/Cursor_Skills). Same 189 skill folders, rewritten for the [open Agent Skills](https://agentskills.io/specification) format that ChatGPT and Codex load.

- **Snapshot:** [skills/](skills/) — 189 `SKILL.md` files across 19 packs
- **AI-transfer reference:** [docs/AI-TRANSFER-SKILLS.md](docs/AI-TRANSFER-SKILLS.md) — 45 loadable cross-domain techniques plus `scripts/ai_plugin_bundle.py`
- **Coding pack gap analysis:** [docs/CODING-PACK-GAP-ANALYSIS.md](docs/CODING-PACK-GAP-ANALYSIS.md)
- **What changed from Cursor:** [docs/CHATGPT-PORT.md](docs/CHATGPT-PORT.md)
- **Reviews of the upstream snapshot:** [REVIEW.md](REVIEW.md), [REVIEW-2.md](REVIEW-2.md)

**Loaded in this repo.** `.agents/skills/` has one symlink per skill so Codex picks up the snapshot. Plugin wrappers live under `plugins/` with `.codex-plugin/plugin.json`. The repo marketplace is `.agents/plugins/marketplace.json`. To refresh this machine (project skills, `~/.agents/skills`, and `~/.codex/plugins`):

```bash
./scripts/load-all.sh
```

Then restart ChatGPT desktop or Codex. Add the marketplace if needed:

```bash
codex plugin marketplace add CatCorner22/ChatGPT_Skills
```

**Activation:** only [`proactive-agency`](skills/first-party/proactive-agency/SKILL.md) may be invoked implicitly (`agents/openai.yaml` → `policy.allow_implicit_invocation: true`). Every other skill sets that flag to `false` — mention it with `@name` in ChatGPT or `$name` in Codex. Full inventory: [docs/SKILL-PLUGIN-CATALOG.md](docs/SKILL-PLUGIN-CATALOG.md). House execution posture is also summarized in [AGENTS.md](AGENTS.md) so Codex loads it on every session in this repo.

## Packs

| Pack | Skills | What it covers |
|---|---|---|
| [Vercel](skills/vercel/) | 33 | Next.js, deployments, AI SDK/Gateway, auth, storage, sandbox, workflow |
| [Hugging Face](skills/huggingface/) | 26 | Model/dataset Hub, Spaces, training (LLM/vision/sentence-transformers), Gradio, SageMaker |
| [LangChain](skills/langchain/) | 12 | LangChain/LangGraph agents, RAG, persistence, human-in-the-loop, LangSmith online evals, Deep Agents |
| [Adobe App Builder](skills/adobe/) | 10 | Runtime actions, CI/CD, project scaffolding, UI, E2E testing, Workfront |
| [GitHub PR kit](skills/cursor-team-kit/) | 8 | GitHub PR/branch workflow: new-branch-and-pr, PR review, CI fixes, merge conflicts |
| [ChatGPT / Codex host](skills/cursor-cloud/) | 5 | Skill load paths, Canvas/artifacts, scheduled waits, checked-in marketplaces |
| [First-party](skills/first-party/) | 4 | `proactive-agency` — implicit execution posture; `skill-library-audit`; `smolagents`; `v0` |
| [Playwright](skills/playwright/) | 3 | General (non-Adobe) browser automation, component testing, trace inspection |
| [Supabase](skills/supabase/) | 2 | Postgres best practices, general Supabase (Auth/Storage/Edge Functions/RLS) |
| [Programmatic agents](skills/cursor-sdk/) | 1 | Codex CLI + OpenAI Agents SDK from code; `@cursor/sdk` only if named |
| [Prompt Optimizer](skills/prompt-optimizer/) | 1 | Authoring and optimizing prompt text itself |
| [Pydantic AI](skills/pydantic-ai/) | 1 | Python agent framework — typed deps/outputs, tools, streaming |
| [Coding](skills/coding/) | 7 | Deliverable-first, clean minimal code, stable architecture, real-time testing, UI/UX engineering |
| [Academic](skills/academic/) | 4 | College coursework router, writing, citations, study system |
| [Craft](skills/craft/) | 3 | OODA×lean loops, mise en place, operational craft router |
| [Microsoft 365](skills/microsoft365/) | 7 | Word, Excel, PowerPoint, Outlook, Teams, OneDrive |
| [Plaud](skills/plaud/) | 8 | AI voice recorder: capture, transcription, summaries, Ask Plaud, AutoFlow, lecture notes, export |
| [AI Transfer](skills/ai-transfer/) | 53 | 45 loadable techniques + 7 category routers + ecosystem primer |
| [Projects](skills/projects/) | 1 | Project reference material — `nyx` character bible |
| **Total** | **189** | reconciles with `find skills -name SKILL.md | wc -l` |

## Invoke

| Surface | Example |
|---|---|
| ChatGPT | `@nextjs` `@proactive-agency` |
| Codex CLI / IDE | `$nextjs` `$skill-creator` `/skills` |

## Provenance

Ported 2026-08-30 from [CatCorner22/Cursor_Skills](https://github.com/CatCorner22/Cursor_Skills) (`main`). Upstream skill authorship is unchanged — see [skills/SOURCE.md](skills/SOURCE.md). Host-specific Cursor Cloud / Cursor SDK instructions were rewritten for ChatGPT and Codex; domain packs (Vercel, Hugging Face, LangChain, …) keep their procedures.
