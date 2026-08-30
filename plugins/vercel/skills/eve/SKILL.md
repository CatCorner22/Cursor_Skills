---
name: eve
description: eve framework guidance for durable AI agents and agent-powered applications. Use when creating, editing, or debugging an eve project, when the user explicitly asks for eve, or when the build-agents skill has selected eve as the default framework. Covers eve's filesystem-first runtime, durable sessions, tools, skills, connections, channels, sandboxes, subagents, schedules, evals, frontend clients, and Agent Runs observability. Do not use for incidental agent mentions, generic agent-building prompts, or established non-eve stacks unless the user asks for comparison or migration.
disable-model-invocation: true
user-invocable: true
when-to-use: 'Trigger on: vercel eve; eve framework; eve project; eve agent; eve architecture; eve.dev; useeveagent; npx eve; node_modules/eve/docs; set up eve. Also /eve.'
argument-hint: /eve task
paths:
- .eve/**
- agent/channels/eve.ts
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: eve framework guidance for durable AI agents and agent-powered applications
  host: grok-build
  ported_from: Cursor_Skills
---
# eve

eve is a filesystem-first framework for durable backend AI agents. An agent is
a directory on disk — instructions, skills, tools, connections, channels,
subagents, and schedules are all files — and eve compiles and runs it.

## Vercel Agent Runs

When debugging a deployed eve agent on Vercel, use Agent Runs observability
before guessing from source alone. Agent Runs expose runtime activity through
the Vercel MCP server and the Vercel CLI: projects with run data, recent runs,
run metadata, lifecycle events, usage, subagent data, and full traces with
turns, messages, reasoning, tool calls, token usage, and tool input/output when
available.

To inspect runs through Vercel MCP, list the available Vercel MCP tools and
use the Agent Runs tools exposed by the server. Tool names and schemas can
change, so inspect the tool list/schema before hard-coding a name from memory.

For CLI usage, ask the installed CLI for the current Agent Runs surface:

```bash
vercel agent-runs --help
vercel agent-runs <subcommand> --help
```

Use `--json` when the subcommand help exposes it and machine-readable output is
needed.

If `vercel agent-runs` is missing, check `vercel --version` and upgrade first:

```bash
npm i -g vercel@latest
vercel agent-runs --help
```

## Source of truth

The complete documentation ships inside the `eve` package. Do not rely on this
skill for guidance — always read the bundled docs, which match the installed
version exactly:

```
node_modules/eve/docs/
```

Start with `node_modules/eve/docs/README.md`. It contains the full
index and recommended reading order. Before writing any eve code, read the
relevant guide there first.

If `eve` is not installed yet, install it (`npm install eve`) or scaffold a new
agent with `npx eve init <agent-name>`, then read the bundled docs.
