# When to use which search API

| Criterion | Basic | Pro | Fetch |
| --- | --- | --- | --- |
| Need ranked snippets only | ✓ | ✓ (richer) | |
| Site restriction | | ✓ | |
| Time range filter | | ✓ | |
| Already have URL | | | ✓ |
| Model orchestrates via tools | Official `web_search` in chat | Same / Pro params | `fetch` tool |

Call standalone `/v1/tools/*` when **your** code owns the loop; use official chat tools when **the model** should plan searches.
