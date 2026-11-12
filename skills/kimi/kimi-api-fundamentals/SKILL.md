---
name: kimi-api-fundamentals
description: Moonshot Kimi API bootstrap — API keys, base URLs, model choice, OpenAI/Anthropic compatibility, and common errors.
type: prompt
whenToUse: When setting up Kimi API calls, choosing kimi-k3.1-pro vs highspeed vs kimi-k3, or debugging auth and HTTP errors on api.moonshot.ai.
disableModelInvocation: false
---

# Kimi API fundamentals

**Gate:** Before writing integration code, confirm key, `base_url`, model id, and which API surface (Chat Completions, Responses, or Messages) the stack expects.

## Quick bootstrap

1. Store the key in the environment — do not commit it:

```bash
export MOONSHOT_API_KEY="YOUR_KEY"
```

2. Point an OpenAI-compatible client at Moonshot:

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["MOONSHOT_API_KEY"],
    base_url="https://api.moonshot.ai/v1",
)
```

3. Call a flagship model:

```python
completion = client.chat.completions.create(
    model="kimi-k3.1-pro",
    messages=[{"role": "user", "content": "Hello"}],
)
```

Official quickstart: https://platform.kimi.ai/docs/get-your-api-key.md

## Model selection

| Model | Use when |
| --- | --- |
| `kimi-k3.1-pro` | Default for coding, agents, deep reasoning, 1M context |
| `kimi-k3.1-pro-highspeed` | Same capabilities, ~2–3× faster output |
| `kimi-k3` | Long-horizon coding, vision, 1M context, same thinking family |

Full list and deprecations: https://platform.kimi.ai/docs/models.md  
Parameter defaults per model: ${KIMI_SKILL_DIR}/references/models-and-params.md

## API formats (pick one)

| Format | `base_url` | Typical consumers |
| --- | --- | --- |
| OpenAI Chat Completions | `https://api.moonshot.ai/v1` | OpenAI SDK, LangChain, most agents |
| OpenAI Responses | `https://api.moonshot.ai/v1` | Codex, tool + server web search |
| Anthropic Messages | `https://api.moonshot.ai/anthropic` | Anthropic SDK, Claude Code |

Overview: https://platform.kimi.ai/docs/api/overview.md

## K3.1 constraints that break migrations

- Do **not** pass `thinking` on `kimi-k3.1-pro` or `kimi-k3` — use top-level `reasoning_effort` instead (`low` / `high` / `max`, default `max`).
- Do **not** set `temperature` — K3 series fixes it at `1.0`.
- For tool-heavy flows, use `max_tokens` large enough (often ≥ 16000) so `reasoning_content` + `content` are not truncated.

See skill `kimi-reasoning-thinking` for preserved reasoning across turns.

## Operational checks

- **Estimate tokens** before large payloads: `POST /v1/tokenizers/estimate-token-count`
- **Balance:** `GET /v1/users/me/balance`
- **Errors:** map HTTP status using https://platform.kimi.ai/docs/api/errors.md

## Codex / Claude Code on Kimi

- Codex: https://platform.kimi.ai/docs/guide/codex-kimi.md  
- Claude Code: https://platform.kimi.ai/docs/guide/claude-code-kimi.md  

Only change `base_url` and API key when migrating from OpenAI or Anthropic unless the host documents extra fields.

## Related skills in this pack

- Reasoning and `reasoning_content` → `kimi-reasoning-thinking`
- Tool loops → `kimi-tool-orchestration` or `kimi-agent-builder`
- Cost → `kimi-context-cost-batch`
