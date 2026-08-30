#!/usr/bin/env bash
# Flatten every skill into Grok discovery paths and refresh plugin wrappers.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
USER_SKILLS="${HOME}/.grok/skills"
PROJECT_SKILLS="${ROOT}/.grok/skills"
USER_PLUGINS="${HOME}/.grok/plugins"

log() { printf '%s\n' "$*"; }

pack_description() {
  case "$1" in
    academic) printf '%s' "College coursework: writing, citations, study system." ;;
    adobe) printf '%s' "Adobe App Builder and Workfront." ;;
    ai-transfer) printf '%s' "Cross-domain AI quality gates." ;;
    coding) printf '%s' "Software craft: deliverable-first, architecture, UI/UX." ;;
    craft) printf '%s' "Operational craft: mise en place and OODA×lean." ;;
    cursor-cloud) printf '%s' "Grok host: load paths, slash commands, artifacts." ;;
    cursor-sdk) printf '%s' "Drive the xAI / Grok API from code." ;;
    cursor-team-kit) printf '%s' "GitHub PR workflow." ;;
    first-party) printf '%s' "proactive-agency may invoke implicitly; others are slash-only." ;;
    huggingface) printf '%s' "Hugging Face Hub." ;;
    langchain) printf '%s' "LangChain/LangGraph." ;;
    microsoft365) printf '%s' "Microsoft 365." ;;
    plaud) printf '%s' "Plaud recorder." ;;
    playwright) printf '%s' "Playwright (non-Adobe)." ;;
    projects) printf '%s' "Project reference (nyx)." ;;
    prompt-optimizer) printf '%s' "Author and optimize prompt text." ;;
    pydantic-ai) printf '%s' "Pydantic AI typed Python agents." ;;
    supabase) printf '%s' "Supabase / Postgres." ;;
    vercel) printf '%s' "Vercel and Next.js." ;;
    *) printf '%s' "Skill pack ${1}." ;;
  esac
}

write_plugin_manifest() {
  local name="$1" dest="$2" description="$3"
  mkdir -p "${dest}" "${dest}/.grok-plugin"
  cat > "${dest}/plugin.json" <<EOF
{
  "name": "${name}",
  "version": "1.0.0",
  "description": "${description}",
  "author": { "name": "CatCorner22" }
}
EOF
  cp "${dest}/plugin.json" "${dest}/.grok-plugin/plugin.json"
}

log "Loading skills from ${ROOT}/skills"
mkdir -p "$PROJECT_SKILLS" "$USER_SKILLS" "${ROOT}/plugins" "$USER_PLUGINS" "${ROOT}/.grok-plugin"
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

{
  echo '{'
  echo '  "name": "grok-skill-pack",'
  echo '  "description": "Grok Build port of Cursor_Skills.",'
  echo '  "owner": { "name": "CatCorner22" },'
  echo '  "plugins": ['
} > "${ROOT}/.grok-plugin/marketplace.json"

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
    echo ',' >> "${ROOT}/.grok-plugin/marketplace.json"
  fi
  cat >> "${ROOT}/.grok-plugin/marketplace.json" <<EOF
    {
      "name": "${pack}",
      "description": "${desc}",
      "source": { "type": "local", "path": "./plugins/${pack}" }
    }
EOF
done
echo '  ]' >> "${ROOT}/.grok-plugin/marketplace.json"
echo '}' >> "${ROOT}/.grok-plugin/marketplace.json"

log "Project skills: $(find -L "${PROJECT_SKILLS}" -name SKILL.md | wc -l | tr -d ' ')"
log "User skills:    $(find -L "${USER_SKILLS}" -name SKILL.md | wc -l | tr -d ' ')"
log "Local plugins:"
ls -1 "$USER_PLUGINS"
log "Done. Start a new Grok session or press r in /plugins. Invoke with /skill-name."
