---
name: kimi-context-cost-batch
description: Kimi API cost control — context caching TTL, stable prefixes, token estimation, and Batch API for async bulk inference.
type: prompt
whenToUse: When optimizing Kimi spend, improving cache hit rate, or running large offline inference jobs.
disableModelInvocation: false
---

# Kimi context, cost, and batch

## Context caching

Guide: https://platform.kimi.ai/docs/guide/context-caching.md

**Use when:** The same long prefix repeats across requests (system prompt, RAG corpus header, stable tool core).

**Practices:**

1. Put **static content first** in `messages` (system instructions, long docs, shared tool defs).
2. Put **variable content last** (user question, per-turn dynamic tools if appended at end).
3. Choose TTL: **5m** vs **1h** based on session length and retry patterns (see platform pricing for cache-hit discounts).
4. Partial blocks that do not fill a cache block may miss cache — avoid tiny churn at prefix boundaries.

Inspect cache usage fields in API responses per the caching guide.

## Token estimation

Before sending huge payloads:

```bash
curl https://api.moonshot.ai/v1/tokenizers/estimate-token-count \
  -H "Authorization: Bearer $MOONSHOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "kimi-k3.1-pro", "messages": [...]}'
```

Docs: https://platform.kimi.ai/docs/api/estimate.md

## reasoning_effort vs cost

Higher `reasoning_effort` increases reasoning tokens. Pair with `kimi-reasoning-thinking`:

| Workload | Effort |
| --- | --- |
| Bulk classification | `low` |
| Interactive coding | `high` |
| Agent with many tools | `max` (unless latency budget forbids) |

## Batch API

For large offline sets (evals, labeling, backfills):

1. Build JSONL of chat completion requests (one per line).
2. `POST /v1/batches` with input file id.
3. Poll batch status; download output file.

Guide: https://platform.kimi.ai/docs/guide/use-batch-api.md  
Pricing: https://platform.kimi.ai/docs/pricing/batch.md

Console alternative (no code): https://platform.kimi.ai/docs/guide/use-batch-inference.md

## Rate limits and tiers

Recharge, RPM/TPM/TPD: https://platform.kimi.ai/docs/pricing/limits.md

## Checklist before production

- [ ] Stable prefix designed for caching
- [ ] Token estimate on worst-case prompt
- [ ] `reasoning_effort` matched to SLA
- [ ] Batch for non-interactive volume
- [ ] Balance monitoring via `/v1/users/me/balance`
