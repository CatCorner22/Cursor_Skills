#!/usr/bin/env bash
# Flatten every skill into Codex/ChatGPT discovery paths and refresh
# plugin wrappers + the repo marketplace.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
USER_SKILLS="${HOME}/.agents/skills"
PROJECT_SKILLS="${ROOT}/.agents/skills"
USER_PLUGINS="${HOME}/.codex/plugins"
USER_MARKET="${HOME}/.agents/plugins/marketplace.json"

log() { printf '%s\n' "$*"; }

pack_description() {
  case "$1" in
    academic) printf '%s' "College coursework: writing, citations, study system." ;;
    adobe) printf '%s' "Adobe App Builder and Workfront: actions, UI, CI/CD, testing." ;;
    ai-transfer) printf '%s' "Cross-domain AI quality gates. Mention a technique by name." ;;
    coding) printf '%s' "Software craft: deliverable-first, architecture, UI/UX, test-while-coding." ;;
    craft) printf '%s' "Operational craft: mise en place and OODA×lean." ;;
    cursor-cloud) printf '%s' "ChatGPT/Codex host: skill load paths, Canvas, artifacts, scheduled waits." ;;
    cursor-sdk) printf '%s' "Drive Codex or OpenAI Agents SDK from code." ;;
    cursor-team-kit) printf '%s' "GitHub PR workflow: branches, reviews, CI, conflicts, shipping." ;;
    first-party) printf '%s' "proactive-agency may invoke implicitly; other first-party skills are explicit." ;;
    huggingface) printf '%s' "Hugging Face Hub: models, Spaces, training, Gradio, SageMaker." ;;
    langchain) printf '%s' "LangChain/LangGraph agents, RAG, persistence, Deep Agents." ;;
    microsoft365) printf '%s' "Microsoft 365: Word, Excel, PowerPoint, Outlook, Teams, OneDrive." ;;
    plaud) printf '%s' "Plaud recorder: capture, transcription, summaries, AutoFlow, export." ;;
    playwright) printf '%s' "Playwright browser automation, component tests, traces (non-Adobe)." ;;
    projects) printf '%s' "Project reference material (nyx)." ;;
    prompt-optimizer) printf '%s' "Author and optimize prompt text." ;;
    pydantic-ai) printf '%s' "Pydantic AI typed Python agents." ;;
    supabase) printf '%s' "Supabase Auth, Storage, Edge Functions, Postgres." ;;
    vercel) printf '%s' "Vercel and Next.js platform skills." ;;
    *) printf '%s' "Skill pack ${1}." ;;
  esac
}

write_plugin_manifest() {
  local name="$1" dest="$2" description="$3"
  mkdir -p "${dest}/.codex-plugin"
  cat > "${dest}/.codex-plugin/plugin.json" <<EOF
{
  "name": "${name}",
  "version": "1.0.0",
  "description": "${description}",
  "author": { "name": "CatCorner22" },
  "skills": "./skills/"
}
EOF
}

log "Loading skills from ${ROOT}/skills"
mkdir -p "$PROJECT_SKILLS" "$USER_SKILLS" "${ROOT}/plugins" "${USER_PLUGINS}" "$(dirname "$USER_MARKET")"
find "$PROJECT_SKILLS" -mindepth 1 -maxdepth 1 -exec rm -rf {} +

skill_count=0
while IFS= read -r skill_md; do
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"
  rel="$(realpath --relative-to="$PROJECT_SKILLS" "$skill_dir")"
  ln -sfn "$rel" "${PROJECT_SKILLS}/${name}"
  rm -rf "${USER_SKILLS}/${name}"
  mkdir -p "${USER_SKILLS}/${name}"
  tar -C "${skill_dir}" -cf - . | tar -C "${USER_SKILLS}/${name}" -xf -
  skill_count=$((skill_count + 1))
done < <(find "${ROOT}/skills" -name SKILL.md | sort)
log "Flattened ${skill_count} skills into ${PROJECT_SKILLS} and ${USER_SKILLS}"

mkdir -p "${ROOT}/.agents/plugins" "${ROOT}/.codex-plugin"
{
  echo '{'
  echo '  "name": "chatgpt-skills",'
  echo '  "interface": { "displayName": "ChatGPT_Skills" },'
  echo '  "plugins": ['
} > "${ROOT}/.agents/plugins/marketplace.json"

first=1
for pack_dir in "${ROOT}/skills"/*/; do
  pack="$(basename "$pack_dir")"
  [[ "$pack" == .* ]] && continue
  wrapper="${ROOT}/plugins/${pack}"
  desc="$(pack_description "$pack")"
  mkdir -p "${wrapper}"
  rm -rf "${wrapper}/skills"
  ln -sfn "$(realpath --relative-to="$wrapper" "$pack_dir")" "${wrapper}/skills"
  write_plugin_manifest "$pack" "$wrapper" "$desc"
  copy_dest="${USER_PLUGINS}/${pack}"
  mkdir -p "$copy_dest"
  write_plugin_manifest "$pack" "$copy_dest" "$desc"
  rm -rf "${copy_dest}/skills"
  mkdir -p "${copy_dest}/skills"
  tar -C "$pack_dir" --exclude '.git' -cf - . | tar -C "${copy_dest}/skills" -xf -
  if [[ "$first" -eq 1 ]]; then
    first=0
  else
    echo ',' >> "${ROOT}/.agents/plugins/marketplace.json"
  fi
  cat >> "${ROOT}/.agents/plugins/marketplace.json" <<EOF
    {
      "name": "${pack}",
      "source": { "source": "local", "path": "./plugins/${pack}" },
      "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" }
    }
EOF
done
echo '  ]' >> "${ROOT}/.agents/plugins/marketplace.json"
echo '}' >> "${ROOT}/.agents/plugins/marketplace.json"

python3 - <<PY
import json
from pathlib import Path
src = Path("${ROOT}/.agents/plugins/marketplace.json")
dest = Path("${USER_MARKET}")
data = json.loads(src.read_text())
data["name"] = "personal-chatgpt-skills"
data["interface"] = {"displayName": "Personal ChatGPT_Skills"}
for plugin in data.get("plugins", []):
    plugin["source"] = {
        "source": "local",
        "path": "./.codex/plugins/" + plugin["name"],
    }
dest.write_text(json.dumps(data, indent=2) + "\n")
PY

log "Project skills: $(find -L "${PROJECT_SKILLS}" -name SKILL.md | wc -l | tr -d ' ')"
log "User skills:    $(find -L "${USER_SKILLS}" -name SKILL.md | wc -l | tr -d ' ')"
log "Local plugins:"
ls -1 "$USER_PLUGINS"
log "Done. Restart ChatGPT desktop or Codex so newly copied skills appear. Invoke with @skill in ChatGPT or \$skill in Codex."
