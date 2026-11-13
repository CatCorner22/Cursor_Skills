---
name: kimi-web-research
description: Kimi web research — Web Search Basic vs Pro, URL fetch, official tools in chat, and cost-aware query design.
type: prompt
whenToUse: When the model needs live web data on Moonshot API, choosing search endpoints, or configuring official web_search tools.
disableModelInvocation: false
---

# Kimi web research

Best practices: https://platform.kimi.ai/docs/guide/best-practices-for-web-search.md

## Choose an API surface

| Need | Option |
| --- | --- |
| Structured titles, snippets, URLs in your code | `POST /v1/tools/search` (Web Search Basic) |
| Ranked chunks, site/time filters | `POST /v1/tools/search_pro` (Web Search Pro) |
| Known URL → Markdown body | `POST /v1/tools/fetch` (URL Fetch) |
| Model-driven research inside chat | Official tools via Chat Completions (Formulas) |

API refs:

- Basic: https://platform.kimi.ai/docs/api/tools-search.md
- Pro: https://platform.kimi.ai/docs/api/tools-search-pro.md
- Fetch: https://platform.kimi.ai/docs/api/tools-fetch.md
- Official tools: https://platform.kimi.ai/docs/guide/use-official-tools.md

Pricing: https://platform.kimi.ai/docs/pricing/websearch.md

## Query design

1. **Be specific** — include entity, time window, and desired artifact (“SEC 10-K 2024 revenue table”).
2. **Prefer Pro** when you need domain or date restriction.
3. **Fetch** after search when you need full page text for quoting.
4. **Deduplicate** — pass prior results in context instead of re-searching identical queries (pairs with `kimi-tool-orchestration` repeat-call fixes).

## In-agent pattern (official tools)

Load Formula URIs such as `moonshot/web-search:latest` and `moonshot/date:latest`; run multi-step tool loop with Preserved Thinking.

Walkthrough: thinking models + tools example in https://platform.kimi.ai/docs/guide/use-thinking-models.md  
Agent starter: `kimi-agent-builder`

## Responses API

OpenAI Responses on Kimi can use server-side web search in some setups — see https://platform.kimi.ai/docs/api/responses.md and Codex guide if the host is Codex.

## Security and compliance

- Treat fetched HTML as untrusted input; sanitize before rendering.
- Log URLs for audit in enterprise settings.

Reference table: ${KIMI_SKILL_DIR}/references/search-choice.md
