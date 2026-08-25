# Skills activation catalog

Generated from all `SKILL.md` frontmatter in `skills/`. Run `./scripts/load-all.sh` once per machine, then **start a new Cursor / Cloud Agent session**.

## Activation types

| Type | Meaning |
|---|---|
| **Auto — every session** | Injected without prompting (`sessionStart: true`) |
| **Auto — prompt match** | Agent loads skill when your message matches its `description` |
| **Auto — Cloud Agent only** | Same as prompt match, but skill marked `environments: [cloud]` |
| **Auto + MCP** | Skill triggers on prompt; tools need MCP connected |

## One-time setup

```bash
git clone <this-repo>
cd Cursor_Skills
./scripts/load-all.sh
```

Optional: Cursor → **Settings → Plugins** → enable packs from `.cursor-plugin/marketplace.json`.

## Debug summary

- **Skills scanned:** 113
- **Unique names:** 113 (no duplicates)
- **YAML/frontmatter errors:** 0
- **Session-start skills:** proactive-agency, knowledge-update
- **Cloud-only skills:** env-setup, migrate-to-builds, subscribe, walkthrough-artifacts

Run full routing audit: `python3 skills/first-party/skill-library-audit/scripts/audit_skill_library.py skills/`

## coding (7 skills)

| Skill | When to use | Activation | How to activate |
|---|---|---|---|
| `clean-minimal-code` | Write clear, minimal code: fewer lines with the same behavior, established naming, SOLID and YAGNI, no premature abstraction. Use when implementing or reviewing... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `coding-ecosystem-primer` | Router for general software engineering in this library: deliverable-first planning, clean minimal code, stable architecture, real-time testing, and UI/UX engin... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `deliverable-first` | Plan and implement features by defining the final deliverable first, then reverse-engineering the smallest code path to it. Use when starting a feature, API, UI... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `real-time-testing` | Test code continuously while writing it: red-green-refactor, watch mode, typecheck and lint after every slice, and never report done without fresh command outpu... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `stable-architecture` | Design code that avoids houses of cards: clear module boundaries, dependency direction, fail-fast invariants, and replaceable adapters. Use when structuring a f... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `ui-engineering` | Modern UI implementation: component composition, design tokens, Tailwind/shadcn/Radix stacks, responsive layout, and accessible markup foundations. Use when bui... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `ux-engineering` | User experience engineering: task flows, Nielsen heuristics, loading/empty/error patterns, accessibility (WCAG-oriented), microcopy, and feedback loops. Use whe... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |

## first-party (4 skills)

| Skill | When to use | Activation | How to activate |
|---|---|---|---|
| `proactive-agency` | Always-on execution posture: do the work instead of describing it. Runs a five-step gate before every response — obtain it yourself rather than asking, reserve ... | Auto — every session | Injected at session start. Run `./scripts/load-all.sh` once. |
| `skill-library-audit` | Audit a multi-vendor agent-skill library for routing pathology — the defect classes that appear only when many packs from different vendors share one router: ve... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `smolagents` | Hugging Face `smolagents`: choosing CodeAgent vs ToolCallingAgent, the model backends (InferenceClientModel, LiteLLMModel, TransformersModel, OpenAIModel), defi... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `v0` | Vercel's v0 app builder — taking v0 output into a production repo, and driving the v0 Platform API (v2, api.v0.dev/v2) from code with the `v0` npm SDK. Use when... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |

## cursor-cloud (5 skills)

| Skill | When to use | Activation | How to activate |
|---|---|---|---|
| `canvas` | Author standalone .canvas.tsx analytical artifacts (charts, tables, audits, metrics) using the cursor/canvas SDK. Use when the deliverable IS structured visual ... | Auto — IDE/Cloud | Prompt match. Publish via cursor-cloud MCP on CLI/sand only. |
| `env-setup` | Explain, inspect, configure, and troubleshoot Cloud Agent development environments. Use when the user asks about environment setup, changing/improving the envir... | Auto — Cloud Agent only | Cloud Agent environment + `./scripts/load-all.sh`. Triggers when prompt matches description. |
| `migrate-to-builds` | Test that a Cloud Agent environment will work with prebuilt environment builds and recommend any required changes. Use when the user wants to migrate to builds,... | Auto — Cloud Agent only | Cloud Agent environment + `./scripts/load-all.sh`. Triggers when prompt matches description. |
| `subscribe` | Wait for external events (GitHub CI results, PR activity, Slack messages, Linear issues) by subscribing with the cursor-subscriptions MCP tools instead of polli... | Auto — Cloud Agent only | Cloud Agent environment + `./scripts/load-all.sh`. Triggers when prompt matches description. |
| `walkthrough-artifacts` | Create walkthrough artifacts (screenshots and screen recordings) that prove code changes work. Use when finishing tested changes and uploading demo evidence for... | Auto — Cloud Agent only | Cloud Agent environment + `./scripts/load-all.sh`. Triggers when prompt matches description. |

## cursor-team-kit (8 skills)

| Skill | When to use | Activation | How to activate |
|---|---|---|---|
| `fix-ci` | Find failing PR checks, inspect logs or external check links, and apply focused fixes | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `fix-merge-conflicts` | Resolve merge conflicts non-interactively, validate build and tests, and finalize conflict resolution | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `get-pr-comments` | Fetch and summarize review comments from the active pull request | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `loop-on-ci` | Monitor PR checks and fix failures until green. Uses gh pr checks as the source of truth for PR-attached checks. | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `make-pr-easy-to-review` | Prepare PRs for review by cleaning noisy history, improving PR descriptions, and adding reviewer guidance without changing code behavior. Use for "make this eas... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `new-branch-and-pr` | Create a fresh branch, complete work, and open a pull request | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `pr-review-canvas` | Generate an interactive PR review walkthrough as an HTML page. Fetches PR data via gh API, categorizes files into core vs mechanical changes, adds reviewer anno... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `review-and-ship` | Review the current branch for bugs, intent fit, and test coverage; run or write tests; commit focused work; open or update a PR. | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |

## cursor-sdk (1 skills)

| Skill | When to use | Activation | How to activate |
|---|---|---|---|
| `cursor-sdk` | Guide users building apps, scripts, CI pipelines, or automations on top of the Cursor TypeScript SDK (`@cursor/sdk`). Use this skill whenever the user mentions ... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |

## vercel (33 skills)

| Skill | When to use | Activation | How to activate |
|---|---|---|---|
| `access-protected-vercel-deployment` | Access and test Vercel deployments protected by Vercel Authentication, SSO, or Deployment Protection. Use when curl, agent-browser, Playwright, or another autom... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `ai-gateway` | Vercel AI Gateway expert guidance. Use when configuring model routing, provider failover, cost tracking, or managing multiple AI providers through a unified API... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `ai-sdk` | Vercel AI SDK expert guidance. Use when building AI-powered features — chat interfaces, text generation, structured output, tool calling, agents, MCP integratio... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `auth` | Authentication integration guidance — Clerk (native Vercel Marketplace, recommended for greenfield), Descope, Auth0, and Auth.js (NextAuth v5) for Next.js. Cove... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `bootstrap` | Project bootstrapping orchestrator for repos that depend on Vercel-linked resources (databases, auth, and managed integrations). Use when setting up or repairin... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `build-agents` | Default guidance for building AI agents when no framework has been chosen, or when the target is Vercel-native. Use for generic requests to build, create, scaff... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `cdn-caching` | Debug Vercel CDN caching — cache hit rate, stale content, revalidation behavior, ISR + PPR, per-request cache reasons (cacheReason) and PPR state (ppr_state), a... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `chat-sdk` | Vercel Chat SDK expert guidance. Use when building multi-platform chat bots — Slack, Telegram, Microsoft Teams, Discord, Google Chat, GitHub, Linear — with a si... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `create-a-backend` | Backend architecture guidance. Use when planning, building, or migrating an API or backend; choosing between Functions, Services, containers, Workflow, Queues, ... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `deployments-cicd` | Vercel deployment and CI/CD expert guidance. Use when deploying, promoting, rolling back, inspecting deployments, building with --prebuilt, or configuring CI wo... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `env-vars` | Vercel environment variable expert guidance. Use when working with .env files, vercel env commands, OIDC tokens, or managing environment-specific configuration. | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `eve` | eve framework guidance for durable AI agents and agent-powered applications. Use when creating, editing, or debugging an eve project, when the user explicitly a... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `knowledge-update` | Corrects outdated LLM knowledge about the Vercel platform and introduces new products. Injected at session start. | Auto — every session | Injected at session start. Run `./scripts/load-all.sh` once. |
| `marketplace` | Vercel Marketplace expert guidance — discovering, installing, and managing third-party integrations via the `vercel integration` CLI. Use when building any app ... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `microfrontends` | Guide for building, configuring, and deploying microfrontends on Vercel. Use this skill when the user mentions microfrontends, multi-zones, splitting an app acr... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `next-cache-components` | Next.js 16 Cache Components guidance — PPR, use cache directive, cacheLife, cacheTag, updateTag, and migration from unstable_cache. Use when implementing partia... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `next-forge` | next-forge expert guidance — production-grade Turborepo monorepo SaaS starter by Vercel. Use when working in a next-forge project, scaffolding with `npx next-fo... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `next-upgrade` | Upgrade Next.js to the latest version following official migration guides and codemods. Use when upgrading Next.js versions, running codemods, or migrating betw... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `nextjs` | Next.js App Router expert guidance. Use when building, debugging, or architecting Next.js applications — routing, Server Components, Server Actions, Cache Compo... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `react-best-practices` | React performance best-practices for TSX files — 64 Vercel rules across 8 impact tiers (waterfalls, bundle size, server/client fetching, re-renders). Use when o... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `routing-middleware` | Vercel Routing Middleware guidance — request interception before cache, rewrites, redirects, personalization. Works with any framework. Supports Edge, Node.js, ... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `runtime-cache` | Vercel Runtime Cache API guidance — ephemeral per-region key-value cache with tag-based invalidation. Shared across Functions, Routing Middleware, and Builds. U... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `shadcn` | shadcn/ui expert guidance — CLI, component installation, composition patterns, custom registries, theming, Tailwind CSS integration, and high-quality interface ... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `turbopack` | Turbopack expert guidance. Use when configuring the Next.js bundler, optimizing HMR, debugging build issues, or understanding the Turbopack vs Webpack differenc... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `vercel-cli` | Vercel CLI expert guidance. Use when deploying, managing environment variables, linking projects, viewing logs, querying metrics, managing domains, or interacti... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `vercel-connect` | Vercel Connect expert guidance — securely obtain scoped OAuth tokens for third-party services (Slack, GitHub, MCP servers, OAuth, Snowflake) on behalf of apps o... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `vercel-firewall` | Vercel Firewall expert guidance — automatic DDoS mitigation, the Vercel WAF (custom rules, IP blocking, managed rulesets, rate limiting), Attack Mode, system by... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `vercel-functions` | Vercel Functions expert guidance — Serverless Functions, Edge Functions, Fluid Compute, streaming, Cron Jobs, and runtime configuration. Use when configuring, d... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `vercel-sandbox` | Vercel Sandbox + agent-browser guidance — run headless Chrome in Firecracker microVMs for screenshots, accessibility snapshots, and browser automation. Use when... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `vercel-services` | Configure and troubleshoot Vercel Services for multiple frontends and backends in one project. Use when composing a polyglot or multi-service application on one... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `vercel-storage` | Vercel storage expert guidance — Blob, Edge Config, and Marketplace storage (Neon Postgres, Upstash Redis). Use when choosing, configuring, or using data storag... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `verification` | Full-story verification — infers what the user is building, then verifies the complete flow end-to-end: browser → API → data → response. Use when the user asks ... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `workflow` | Vercel Workflow SDK expert guidance. Use when building durable workflows, long-running tasks, API routes or agents that need pause/resume, retries, step-based e... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |

## huggingface (26 skills)

| Skill | When to use | Activation | How to activate |
|---|---|---|---|
| `hf-cli` | Hugging Face Hub CLI (`hf`) for auth, repos, models, datasets, spaces, papers, jobs, buckets, cache, and endpoints. Use when the user needs a terminal/CLI workf... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `hf-cloud-aws-context-discovery` | Discover the user's local AWS context (active profile, region, account ID, caller identity) at the start of any AWS task. Use this skill before any other AWS wo... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `hf-cloud-python-env-setup` | Set up an isolated Python environment for SageMaker / AWS work, with the right Python version and current boto3. Use this skill whenever Python code will be exe... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `hf-cloud-sagemaker-deployment-planner` | Plan and coordinate the deployment of a model to Amazon SageMaker AI. Use this skill whenever the user wants to deploy, host, serve, or expose a model on SageMa... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `hf-cloud-sagemaker-iam-preflight` | Ensure a usable SageMaker execution role exists before deploying or training. Use this skill whenever about to create a SageMaker endpoint, model, training job,... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `hf-cloud-sagemaker-production-defaults` | Create a SageMaker endpoint (real-time, real-time scale-to-zero, or async) with autoscaling, CloudWatch alarms, and tagging enabled by default. Use this skill w... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `hf-cloud-serving-image-selection` | Pick the right serving container for a SageMaker model deployment and find its current image URI. Use this skill whenever about to deploy a model to a SageMaker... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `hf-mcp` | Use Hugging Face Hub via MCP server tools when the Huggingface-skills (or equivalent) MCP namespace is connected. Search models, datasets, Spaces, and papers; i... | Auto + MCP | Prompt match + connect **Huggingface-skills** MCP (huggingface.co/settings/mcp). |
| `hf-mem` | Hugging Face CLI to estimate the required memory to load Safetensors or GGUF model weights for inference from the Hugging Face Hub. Use when you have a specific... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-best` | Use when the user asks about finding the best, top, or recommended model for a task, wants to know what AI model to use, or wants to compare models by benchmark... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-community-evals` | Run evaluations for Hugging Face Hub models using inspect-ai and lighteval on local hardware. Use for backend selection, local GPU evals, and choosing between v... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-datasets` | Use this skill for Hugging Face Dataset Viewer API workflows that fetch subset/split metadata, paginate rows, search text, apply filters, download parquet URLs,... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-gradio` | Build Gradio web UIs and demos in Python. Use when creating or editing Gradio apps, components, event listeners, layouts, or chatbots. | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-llm-trainer` | Train or fine-tune language and vision models using TRL (Transformer Reinforcement Learning) or Unsloth with Hugging Face Jobs infrastructure. Covers SFT, DPO, ... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-local-models` | Use to select models to run locally with llama.cpp and GGUF on CPU, Mac Metal, CUDA, or ROCm. Covers finding GGUFs, quant selection, running servers, exact GGUF... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-lora-space-builder` | Build and publish a Gradio demo on Hugging Face Spaces for a user-provided LoRA. Use when someone asks to create, generate, ship, or publish a Space, demo, Grad... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-paper-publisher` | Publish and manage research papers on Hugging Face Hub. Use to create markdown research-article drafts, check or GET-index a paper page, link arXiv IDs into mod... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-papers` | Look up and read Hugging Face paper pages in markdown, and use the papers API for structured metadata such as authors, linked models/datasets/spaces, Github rep... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-spaces` | Build, deploy, and maintain applications on Hugging Face Spaces — Gradio / Docker / Static SDKs, ZeroGPU and dedicated hardware, model loading, debugging, bucke... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-tool-builder` | Use this skill when the user wants to build tool/scripts or achieve a task where using data from the Hugging Face API would help. This is especially useful when... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-trackio` | Track and visualize ML training experiments with Trackio. Use when logging metrics during training (Python API), firing alerts for training diagnostics, or retr... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-vision-trainer` | Trains and fine-tunes vision models for object detection (D-FINE, RT-DETR v2, DETR, YOLOS), image classification (timm models — MobileNetV3, MobileViT, ResNet, ... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `huggingface-zerogpu` | AI demos and GPU compute with Gradio Spaces and Hugging Face Spaces ZeroGPU. Use when writing or reviewing code that uses `@spaces.GPU`, configuring `python_ver... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `train-sentence-transformers` | Train or fine-tune sentence-transformers models across `SentenceTransformer` (bi-encoder; dense or static embedding model; for retrieval, similarity, clustering... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `transformers-js` | Use Transformers.js to run state-of-the-art machine learning models directly in JavaScript/TypeScript. Supports NLP (text classification, translation, summariza... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `trl-training` | Train and fine-tune transformer language models locally with the TRL CLI (SFT, DPO, GRPO, KTO, RLOO, Reward Model). For managed Hugging Face Jobs, use huggingfa... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |

## langchain (12 skills)

| Skill | When to use | Activation | How to activate |
|---|---|---|---|
| `deep-agents-core` | Configure the `deepagents` harness: `create_deep_agent()` / `createDeepAgent()`, middleware selection, built-in filesystem and planning tools, the agent SKILL.m... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `deep-agents-orchestration` | Subagent delegation, task planning, and approval gates inside the `deepagents` harness: SubAgentMiddleware and the `task` tool, TodoListMiddleware and `write_to... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `ecosystem-primer` | Router for the LangChain ecosystem: choose between LangChain, LangGraph, and Deep Agents, set the LANGSMITH_* env vars, find the right docs.langchain.com page, ... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `langchain-dependencies` | Package versions, installs, and dependency management for the LangChain stack in Python and TypeScript: required packages, minimum versions, environment require... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `langchain-fundamentals` | Create LangChain agents with `create_agent` / `createAgent`: model and tool wiring, the agent loop, and where middleware attaches. Use when the code imports `la... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `langchain-middleware` | Middleware on a LangChain `create_agent` / `createAgent` agent: `HumanInTheLoopMiddleware` to approve dangerous tool calls, writing custom middleware hooks, `Co... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `langchain-rag` | Build a retrieval pipeline with LangChain: document loaders, RecursiveCharacterTextSplitter, embeddings, and the LangChain vector store wrappers (Chroma, FAISS,... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `langgraph-cli` | The `langgraph` / `langgraphjs` CLI: `new`, `dev`, `build`, `up`, `deploy`, `dockerfile`, deployment logs, and the `langgraph.json` config schema. Use when runn... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `langgraph-fundamentals` | Write LangGraph graphs in Python or TypeScript: StateGraph, state schemas and reducers, nodes, normal and conditional edges, Command, Send fan-out, invoke/strea... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `langgraph-human-in-the-loop` | Pause a LangGraph graph for a human: `interrupt()`, `Command(resume=...)`, approval and validation workflows, resuming multiple concurrent interrupts by id, kee... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `langgraph-persistence` | Persist LangGraph state: checkpointers, `thread_id`, time travel over checkpoint history, the cross-thread `Store`, and subgraph checkpointer scoping. Use when ... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `langsmith-online-eval-engineering` | Create LangSmith online evaluators one at a time: inspect recent traces in a tracing project, interview the user, propose grounded criteria, then build, test, a... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |

## adobe (10 skills)

| Skill | When to use | Activation | How to activate |
|---|---|---|---|
| `appbuilder-action-scaffolder` | Create, implement, deploy, and debug Adobe Runtime actions with consistent layout, validation, and error handling. Use this skill whenever the user needs to add... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `appbuilder-cicd-pipeline` | Set up CI/CD pipelines for Adobe App Builder projects. Generates GitHub Actions workflows using adobe/aio-cli-setup-action@3 and adobe/aio-apps-action@3.3.0, pl... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `appbuilder-e2e-testing` | Use this skill whenever the user wants browser-based end-to-end tests for an Adobe App Builder application. Covers Playwright E2E testing for ExC Shell SPAs, AE... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `appbuilder-project-init` | Initialize an Adobe App Builder project end-to-end without Developer Console UI clicks. Creates the Console project and workspace, subscribes APIs (including th... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `appbuilder-testing` | Generate and run tests for Adobe App Builder actions and UI components. Scaffolds Jest unit tests, integration tests against deployed actions, contract tests fo... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `appbuilder-ui-scaffolder` | Generate React Spectrum UI components for Adobe Experience Cloud Shell SPAs and AEM UI Extensions. Provides patterns for pages, forms, data tables, dialogs, and... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `appbuilder-workfront` | Use when orienting, onboarding, or planning before a concrete task — the entry point for building a customized Workfront UI on Adobe App Builder. Reach for this... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `workfront-actions` | Use when writing or fixing the server-side code of a Workfront App Builder extension — the Adobe I/O Runtime action the React SPA calls to do work the browser c... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `workfront-local-testing` | Use when making Workfront load your locally running App Builder extension, or when a local extension that worked before has stopped appearing. Reach for this wh... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `workfront-ui-extension` | Use when building or editing the React/Spectrum front-end SPA of a Workfront App Builder extension. Reach for this whenever the user is: registering or changing... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |

## supabase (2 skills)

| Skill | When to use | Activation | How to activate |
|---|---|---|---|
| `supabase` | Canonical source for Supabase development work. Triggers: Supabase products (Database, Auth, Edge Functions, Realtime, Storage, Vectors, Cron, Queues); client l... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `supabase-postgres-best-practices` | Postgres performance optimization and best practices from Supabase. Use this skill when writing, reviewing, or optimizing Postgres queries, schema designs, or d... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |

## playwright (3 skills)

| Skill | When to use | Activation | How to activate |
|---|---|---|---|
| `playwright-cli` | Automate browser interactions, test web pages and work with Playwright tests — the general-purpose Playwright skill for this repo (web apps, Next.js, any non-Ad... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `playwright-component-testing` | Set up component testing with Playwright using a story gallery — scaffold stories and a gallery dev page driven by the built-in mount fixture, no dedicated comp... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
| `playwright-trace` | Inspect Playwright trace files from the command line — list actions, view requests, console, errors, snapshots and screenshots. | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |

## pydantic-ai (1 skills)

| Skill | When to use | Activation | How to activate |
|---|---|---|---|
| `building-pydantic-ai-agents` | Build agents in Python with Pydantic AI — tools, capabilities (including on-demand loading), structured output, streaming, testing, and multi-agent patterns. Us... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |

## prompt-optimizer (1 skills)

| Skill | When to use | Activation | How to activate |
|---|---|---|---|
| `prompt-optimizer` | Creates, optimizes, and iteratively refines agent prompts, system prompts, developer prompts, and reusable prompt templates. Use when asked to improve a prompt,... | Auto — prompt match | Run `./scripts/load-all.sh` (or enable **coding**/**vercel**/etc. plugin). Ask using words from the skill description. |
