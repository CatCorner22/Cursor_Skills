# Kimi K3 family — parameter notes

Source: https://platform.kimi.ai/docs/api/models-overview.md

## reasoning_effort (kimi-k3.1-pro, kimi-k3)

| Value | Tradeoff |
| --- | --- |
| `low` | Faster, fewer reasoning tokens |
| `high` | Deeper reasoning, more latency |
| `max` | Default; deepest reasoning |

Set at request top level, not inside `messages`.

## Models vs latency

| Model id | Notes |
| --- | --- |
| `kimi-k3.1-pro` | Flagship; Preserved Thinking always on |
| `kimi-k3.1-pro-highspeed` | Same capability tier, higher throughput |
| `kimi-k3` | 1M context; vision; same thinking behavior as K3.1 Pro family |

## Do not send

- `temperature` (fixed at 1.0 for K3 / K3.1 Pro)
- `thinking` object on K3.1 Pro / K3 (use `reasoning_effort`)

## Docs index for agents

Fetch https://platform.kimi.ai/docs/llms.txt before deep dives so links stay current.
