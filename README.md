# Grok_Skill_Pack

Intended GitHub repo: **[CatCorner22/Grok_Skill_Pack](https://github.com/CatCorner22/Grok_Skill_Pack)**.

Grok Build port of [CatCorner22/Cursor_Skills](https://github.com/CatCorner22/Cursor_Skills). Same 189 skill folders, rewritten for [Grok skills, plugins, and marketplaces](https://docs.x.ai/build/features/skills-plugins-marketplaces).

- **Snapshot:** [skills/](skills/) — 189 `SKILL.md` files across 19 packs
- **AI-transfer reference:** [docs/AI-TRANSFER-SKILLS.md](docs/AI-TRANSFER-SKILLS.md)
- **What changed from Cursor:** [docs/GROK-PORT.md](docs/GROK-PORT.md)
- **Catalog:** [docs/SKILL-PLUGIN-CATALOG.md](docs/SKILL-PLUGIN-CATALOG.md)

**Loaded in this repo.** `.grok/skills/` has one symlink per skill. Plugin wrappers live under `plugins/` with `plugin.json`. The marketplace index is `.grok-plugin/marketplace.json`. To refresh this machine:

```bash
./scripts/load-all.sh
```

Then start a new Grok session (or press `r` in `/plugins`). Add the marketplace if needed:

```bash
grok plugin marketplace add CatCorner22/Grok_Skill_Pack
grok plugin install first-party --trust
grok inspect
```

**Activation:** only [`proactive-agency`](skills/first-party/proactive-agency/SKILL.md) may be invoked implicitly. Every other skill sets `disable-model-invocation: true` — run `/name`. House execution posture is also in [AGENTS.md](AGENTS.md) (Grok reads the AGENTS.md family).

## Packs

| Pack | Skills | What it covers |
|---|---|---|
| [Vercel](skills/vercel/) | 33 | Next.js, deployments, AI SDK/Gateway, auth, storage, sandbox, workflow |
| [Hugging Face](skills/huggingface/) | 26 | Hub, Spaces, training, Gradio, SageMaker |
| [LangChain](skills/langchain/) | 12 | LangChain/LangGraph, RAG, Deep Agents, LangSmith |
| [Adobe App Builder](skills/adobe/) | 10 | Runtime actions, CI/CD, UI, Workfront |
| [GitHub PR kit](skills/cursor-team-kit/) | 8 | Branches, reviews, CI, merge conflicts |
| [Grok host](skills/cursor-cloud/) | 5 | Load paths, artifacts, scheduled waits, marketplaces |
| [First-party](skills/first-party/) | 4 | `proactive-agency`, `skill-library-audit`, `smolagents`, `v0` |
| [Playwright](skills/playwright/) | 3 | Browser automation outside Adobe |
| [Supabase](skills/supabase/) | 2 | Auth, Storage, Edge Functions, Postgres |
| [Programmatic agents](skills/cursor-sdk/) | 1 | xAI / Grok API from code; `@cursor/sdk` only if named |
| [Prompt Optimizer](skills/prompt-optimizer/) | 1 | Prompt text |
| [Pydantic AI](skills/pydantic-ai/) | 1 | Typed Python agents |
| [Coding](skills/coding/) | 7 | Deliverable-first engineering craft |
| [Academic](skills/academic/) | 4 | Coursework, writing, citations, study |
| [Craft](skills/craft/) | 3 | OODA×lean, mise en place |
| [Microsoft 365](skills/microsoft365/) | 7 | Word, Excel, PowerPoint, Outlook, Teams, OneDrive |
| [Plaud](skills/plaud/) | 8 | Recorder workflows |
| [AI Transfer](skills/ai-transfer/) | 53 | Cross-domain techniques + routers |
| [Projects](skills/projects/) | 1 | `nyx` character bible |
| **Total** | **189** | `find skills -name SKILL.md \| wc -l` |

## Invoke

In Grok Build: `/nextjs` `/proactive-agency`. On name collision: `/vercel:nextjs`.

## Provenance

Ported 2026-08-30 from [CatCorner22/Cursor_Skills](https://github.com/CatCorner22/Cursor_Skills) (`main`). See [skills/SOURCE.md](skills/SOURCE.md). Sibling ports: [ChatGPT_Skills](https://github.com/CatCorner22/Cursor_Skills/tree/cursor/chatgpt-skills-a08b), [Claude_Skills_2](https://github.com/CatCorner22/Claude_Skills_2).
