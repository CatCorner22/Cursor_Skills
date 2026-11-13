---
name: kimi-reasoning-thinking
description: Kimi thinking models — reasoning_effort, reading reasoning_content, streaming order, and Preserved Thinking across multi-turn and tool calls.
type: prompt
whenToUse: When using kimi-k3.1-pro or kimi-k3, handling reasoning_content in SDKs, streaming, or multi-step tool loops.
disableModelInvocation: false
---

# Kimi reasoning and thinking

**Rule:** On `kimi-k3.1-pro` and `kimi-k3`, reasoning is always on. Multi-turn and tool loops must return the **full assistant message** from the API (including `reasoning_content`), not only final text.

Guide: https://platform.kimi.ai/docs/guide/use-thinking-models.md

## Configure depth

Use top-level `reasoning_effort`:

```json
{
  "model": "kimi-k3.1-pro",
  "reasoning_effort": "high",
  "messages": [{"role": "user", "content": "..."}]
}
```

Values: `low`, `high`, `max` (default `max`). Details: https://platform.kimi.ai/docs/guide/use-reasoning-effort.md

Do **not** pass a `thinking` parameter on these models.

## Read reasoning_content (OpenAI Python SDK)

SDK message types may omit `reasoning_content` on the typed surface — use `getattr`:

```python
message = completion.choices[0].message
if hasattr(message, "reasoning_content"):
    reasoning = getattr(message, "reasoning_content")
```

Streaming: `reasoning_content` deltas arrive **before** `content` deltas; treat first `content` chunk as “reasoning finished” for UI if needed.

## Preserved Thinking (multi-turn + tools)

After each completion:

```python
messages.append(message)  # whole message object, not message.content only
```

**Why:** K3.1 Pro and K3 use Preserved Thinking; stripping `reasoning_content` breaks continuity in tool chains and follow-up turns.

Warning: historical `reasoning_content` still counts toward context and billing — prune old turns when sessions grow.

## Tool-call configuration checklist

When the model will call tools in a loop:

1. `max_tokens` ≥ 16000 (often 32k for long chains)
2. `stream=True` for UX and timeout resilience
3. No `temperature` argument
4. Append full assistant messages between tool results
5. Pair with `kimi-tool-orchestration` for large tool sets

## When to lower reasoning_effort

| Scenario | Suggested |
| --- | --- |
| Simple formatting, single-shot Q&A | `low` |
| Standard coding task | `high` |
| Multi-tool research, hard math, agent plans | `max` |

Decide `reasoning_effort` before the conversation starts when possible — changing later is fine for quality, but plan token budget accordingly.

## Billing note

Reasoning tokens bill like other output tokens. See https://platform.kimi.ai/docs/pricing/chat.md
