# Kimi (Moonshot) skill pack

Eight platform-native Agent Skills for the [Kimi Open Platform](https://platform.kimi.ai/docs/features.md) and [Kimi Code CLI](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html).

| Skill | Focus |
| --- | --- |
| `kimi-api-fundamentals` | Keys, models, API surfaces, migration |
| `kimi-reasoning-thinking` | `reasoning_effort`, `reasoning_content`, Preserved Thinking |
| `kimi-tool-orchestration` | Dynamic tools, `tool_choice`, repeat-call fixes |
| `kimi-context-cost-batch` | Context caching, token estimate, Batch API |
| `kimi-files-vision` | Files API, vision inputs, multi-file Q&A |
| `kimi-web-research` | Web Search Basic/Pro, fetch, official tools |
| `kimi-agent-builder` | End-to-end K3 agent loop |
| `kimi-code-plugin-authoring` | `kimi.plugin.json`, ZIP packaging |

## Kimi Code CLI install (one skill per ZIP)

```bash
./scripts/package-kimi-skills.sh
# In Kimi Code CLI:
# /plugins install /path/to/dist/kimi/kimi-tool-orchestration.zip
# /reload
# /skill:kimi-tool-orchestration:kimi-tool-orchestration
```

Frontmatter uses Kimi field names (`whenToUse`, `disableModelInvocation`). Cursor loads this pack via `plugins/kimi/` like other packs.
