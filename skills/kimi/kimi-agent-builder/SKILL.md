---
name: kimi-agent-builder
description: Build a runnable Kimi K3 agent — streaming tool loop, official and custom tools, structured output, and integration hygiene.
type: prompt
whenToUse: When implementing an agent on Moonshot API with kimi-k3.1-pro, combining web search and custom functions.
disableModelInvocation: true
---

# Kimi K3 agent builder

**Deliverable:** A loop that streams model output, executes tools, preserves `reasoning_content`, and stops with a user-visible answer.

Starter guide: https://platform.kimi.ai/docs/guide/use-kimi-k3-to-setup-agent.md

## Architecture

```
User message
    -> Chat Completions (stream=True, tools=[...])
    -> Assistant message (maybe tool_calls)
    -> Host executes tools
    -> tool role messages
    -> repeat until no tool_calls
    -> final content to user
```

## Implementation checklist

### Client setup

- `base_url`: `https://api.moonshot.ai/v1`
- `model`: `kimi-k3.1-pro` (or `kimi-k3.1-pro-highspeed` for latency)
- `MOONSHOT_API_KEY` from environment

### Required behaviors

- [ ] `stream=True`
- [ ] `max_tokens` ≥ 16000 for multi-step tools
- [ ] No `temperature`; use `reasoning_effort` intentionally
- [ ] Append **full** assistant `message` objects to `messages`
- [ ] Unique `tool_call_id` on every tool result

Skills: `kimi-reasoning-thinking`, `kimi-tool-orchestration`

### Tools

| Type | Source |
| --- | --- |
| Custom functions | Your `tools[]` JSON schema |
| Official (web, date, …) | Formula URIs — see `kimi-web-research` |
| Large inventory | `search_tools` + dynamic loading |

### Structured output

When the final answer must be JSON:

- `response_format` with JSON Schema (Structured Output), or
- JSON Mode for valid JSON without strict schema

https://platform.kimi.ai/docs/guide/response_format.md

Validate in your host before side effects.

### Stop conditions

- No `tool_calls` on assistant message
- Max iteration cap (e.g. 10) with user-visible error
- Client-disconnect handling: https://platform.kimi.ai/docs/guide/auto-reconnect.md

### Debugging

- MoonPalace: https://platform.kimi.ai/docs/guide/use-moonpalace.md
- Playground reproduce: https://platform.kimi.ai/docs/guide/use-playground-to-debug-the-model.md

## Minimal loop (pseudocode)

```python
messages = [system, user]
for _ in range(MAX_ITER):
    stream = client.chat.completions.create(
        model="kimi-k3.1-pro",
        messages=messages,
        tools=tools,
        stream=True,
        max_tokens=32_000,
        reasoning_effort="high",
    )
    message = accumulate_stream(stream)  # keep reasoning_content + content
    messages.append(message)
    if not message.tool_calls:
        break
    for call in message.tool_calls:
        result = run_tool(call)
        messages.append(tool_message(call.id, result))
```

Replace `accumulate_stream` with your SDK’s pattern; never drop `reasoning_content` when rebuilding the message object.

## Ship criteria

- [ ] One happy-path demo script or test
- [ ] Tool errors surfaced to the model as tool content
- [ ] Token/cost notes for longest expected run (`kimi-context-cost-batch`)
