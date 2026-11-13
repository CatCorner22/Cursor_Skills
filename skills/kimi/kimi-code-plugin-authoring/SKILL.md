---
name: kimi-code-plugin-authoring
description: Author Kimi Code CLI plugins and Agent Skills — kimi.plugin.json, SKILL.md frontmatter, ZIP packaging, sessionStart, and MCP hooks.
type: prompt
whenToUse: When creating or distributing skills for Kimi Code CLI, packaging ZIP plugins, or adapting Cursor-style skills to Kimi.
disableModelInvocation: true
---

# Kimi Code plugin authoring

Docs:

- Plugins: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/plugins.html
- Skills: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html

## Plugin layout

```
my-plugin/
  kimi.plugin.json
  skills/
  my-skill/
    SKILL.md
    references/
```

ZIP install: `/plugins install /path/to/my-plugin.zip` then `/reload`.

## kimi.plugin.json (minimal)

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "One-line summary",
  "skills": "./skills/",
  "interface": {
    "displayName": "My Plugin",
    "shortDescription": "Shown in /plugins"
  }
}
```

Optional:

- `sessionStart.skill` — load a skill at session start (skill `name` from frontmatter)
- `skillInstructions` — extra text whenever any skill from this plugin loads
- `mcpServers` — declare MCP servers
- `systemPromptPath` — append static instructions while plugin enabled

Plugin skill invoke: `/skill:my-plugin:my-skill`  
If a command and skill share a name, use the explicit `/skill:` form.

## SKILL.md frontmatter (directory form)

**Required:** `name`, `description`

```yaml
---
name: my-skill
description: One-line summary for discovery
type: prompt
whenToUse: When the user asks for X
disableModelInvocation: true
---
```

| Field | Notes |
| --- | --- |
| `type` | `prompt` (default), `flow` (manual only) |
| `whenToUse` | Kimi uses this for invocation timing |
| `disableModelInvocation` | `true` = manual/mention only |
| `arguments` | Optional `$arg` placeholders in body |

Supporting files: reference with `${KIMI_SKILL_DIR}/references/foo.md`

## sessionStart posture (optional)

Adapt execution discipline without Cursor `metadata.sessionStart`:

1. Create skill `kimi-session-posture` with concise gates (confirm destructive actions, do not hand off reversible work).
2. Set in manifest: `"sessionStart": { "skill": "kimi-session-posture" }`.

Do not execute code from sessionStart — text injection only.

## Packaging this repository’s skills

From repo root:

```bash
./scripts/package-kimi-skills.sh
```

Produces `dist/kimi/<skill-id>.zip` — one plugin per skill for minimal installs.

## Cursor → Kimi porting

| Cursor | Kimi |
| --- | --- |
| `disable-model-invocation` | `disableModelInvocation` |
| `metadata.pathPatterns` | Not used by Kimi; keep as comments or drop |
| `.cursor-plugin/plugin.json` | `kimi.plugin.json` |
| `metadata.sessionStart` | `sessionStart.skill` in kimi manifest |

## Marketplace JSON (team distribution)

Custom catalog: set `KIMI_CODE_PLUGIN_MARKETPLACE_URL` or pass URL to `/plugins marketplace`.

```json
{
  "version": "2",
  "plugins": [
    {
      "id": "kimi-tool-orchestration",
      "displayName": "Kimi Tool Orchestration",
      "source": "https://example.com/kimi-tool-orchestration.zip"
    }
  ]
}
```

## Verify after install

1. `/plugins list` shows the plugin
2. `/skill:<plugin>:<skill>` loads content
3. `/plugins info <plugin>` shows diagnostics
