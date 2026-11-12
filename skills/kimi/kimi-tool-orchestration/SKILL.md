---
name: kimi-tool-orchestration
description: Kimi K3 tool calling at scale — dynamic tool loading, tool_choice, search_tools pattern, prefix cache, and fixing repeated tool calls.
type: prompt
whenToUse: When an agent exposes many tools, uses Kimi tool_calls in streaming, or the model repeats the same tool invocation.
disableModelInvocation: false
---

# Kimi tool orchestration

**Problem:** Declaring every tool on every request burns context and increases wrong-tool picks.

**Pattern:** Start with a small `tools` list + `search_tools`, inject full definitions on demand, tune `tool_choice` and `reasoning_effort`.

Best practices: https://platform.kimi.ai/docs/guide/kimi-k3-tool-calling-best-practice.md

## Minimum viable loop

1. **Declare** only `search_tools` plus a few always-needed tools.
2. **First turn:** `tool_choice: "required"` so the model must call `search_tools` (or another tool) before answering from memory.
3. **After search:** inject matching tool schemas via a `system` message that includes a `tools` field (dynamic loading).
4. **Later turns:** `tool_choice: "auto"`.
5. **Execute** tool calls in your host; append `role: tool` messages with `tool_call_id`.

Implementation guide: https://platform.kimi.ai/docs/guide/use-kimi-api-to-complete-tool-calls.md  
Dynamic loading: https://platform.kimi.ai/docs/guide/use-dynamic-tool-loading.md  
`tool_choice` values: https://platform.kimi.ai/docs/guide/use-tool-choice.md

## search_tools sketch

Advertise domains in the system prompt so the model knows to search the catalog first.

```json
{
  "type": "function",
  "function": {
    "name": "search_tools",
    "description": "Search available tools by keyword; return names and summaries",
    "parameters": {
      "type": "object",
      "properties": {
        "query": { "type": "string", "description": "e.g. github, database, slack" }
      },
      "required": ["query"]
    }
  }
}
```

Backend: implement search over your tool registry; return candidates; then inject full definitions.

## Dynamic injection shape

```json
{
  "role": "system",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "create_github_pr",
        "description": "Create a pull request",
        "parameters": { "type": "object", "properties": {} }
      }
    }
  ]
}
```

Dynamic declarations are per-request on the client history; keep stable prefixes when possible for context caching (see `kimi-context-cost-batch`).

## Prefix cache interaction

- Changing `tool_choice` does **not** invalidate prefix cache.
- Appending dynamic tools at the **end** of `messages` usually preserves cached prefix.
- **Removing or editing** earlier tool declarations can break cache hits after the change point.

## Repeated tool calls

Symptoms: model calls the same tool with identical args in a loop.

Fix checklist: https://platform.kimi.ai/docs/guide/tool-call-repeat.md

1. Verify `tool_calls` / `tool` message pairing and unique `tool_call_id`.
2. Detect repeats client-side and stop or inject a user reminder.
3. System prompt: “Do not call the same tool with identical arguments twice; synthesize from prior results.”

## Reasoning + tools

Use `kimi-reasoning-thinking`: pass complete assistant messages between tool results; prefer streaming and generous `max_tokens`.

## Reference flow diagram

See ${KIMI_SKILL_DIR}/references/tool-flow.md
