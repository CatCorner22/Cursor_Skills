#!/usr/bin/env bash
# Download (when possible) and load every skill pack in this repo, plus the
# Vercel / Hugging Face / Adobe marketplace plugins.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE="${HOME}/.cursor/plugins/cache/cursor-public"
LOCAL="${HOME}/.cursor/plugins/local"
USER_SKILLS="${HOME}/.cursor/skills"
PROJECT_SKILLS="${ROOT}/.cursor/skills"
DOWNLOADS="${DOWNLOADS:-/tmp/cursor-skills-plugin-downloads}"

VERCEL_SHA="${VERCEL_SHA:-11c32588786a9d49791372657433b88d49561874}"
HF_SHA="${HF_SHA:-d7223848c3895fbd447faf2aec73e0a6cdd7fdcd}"
ADOBE_SHA="${ADOBE_SHA:-253f56901e058800ccb97ffd5bf1e3329d5f2e00}"

log() { printf '%s\n' "$*"; }

copy_tree() {
  local src="$1" dest="$2"
  mkdir -p "$dest"
  tar -C "$src" \
    --exclude '.git' \
    --exclude 'upstream' \
    --exclude '.claude' \
    --exclude '.claude-plugin' \
    --exclude '.kimi-plugin' \
    --exclude 'AGENTS.md' \
    -cf - . | tar -C "$dest" -xf -
}

clone_at() {
  local url="$1" sha="$2" dest="$3"
  if [[ -d "$dest/.git" ]]; then
    git -C "$dest" fetch --depth 1 origin "$sha" >/dev/null 2>&1 || git -C "$dest" fetch origin "$sha"
    git -C "$dest" checkout --detach "$sha" >/dev/null
    return
  fi
  rm -rf "$dest"
  git clone --filter=blob:none "$url" "$dest"
  git -C "$dest" checkout --detach "$sha" >/dev/null
}

pick_src() {
  local downloaded="$1" cache_glob="$2"
  if [[ -d "$downloaded" ]]; then
    printf '%s' "$downloaded"
    return
  fi
  local hit
  hit="$(ls -d ${cache_glob} 2>/dev/null | head -1 || true)"
  if [[ -n "$hit" && -d "$hit" ]]; then
    printf '%s' "$hit"
    return
  fi
  return 1
}

pack_description() {
  case "$1" in
    academic) printf '%s' "College coursework: writing, citations, study system. Skills are manual." ;;
    adobe) printf '%s' "Adobe App Builder and Workfront: actions, UI, CI/CD, testing. Skills are manual." ;;
    ai-transfer) printf '%s' "Cross-domain AI quality gates. Skills are manual; mention a technique by name." ;;
    coding) printf '%s' "Software craft: deliverable-first, architecture, UI/UX, test-while-coding. Skills are manual." ;;
    craft) printf '%s' "Operational craft: mise en place and OODA×lean. Skills are manual." ;;
    cursor-cloud) printf '%s' "Cursor Cloud Agent environment, snapshots, subscriptions, canvases. Skills are manual." ;;
    cursor-sdk) printf '%s' "Drive Cursor agents from code via @cursor/sdk. Skill is manual." ;;
    cursor-team-kit) printf '%s' "GitHub PR workflow: branches, reviews, CI, conflicts, shipping. Skills are manual." ;;
    first-party) printf '%s' "proactive-agency is always on. skill-library-audit, smolagents, and v0 are manual." ;;
    huggingface) printf '%s' "Hugging Face Hub: models, Spaces, training, Gradio, SageMaker. Skills are manual." ;;
    langchain) printf '%s' "LangChain/LangGraph agents, RAG, persistence, Deep Agents. Skills are manual." ;;
    microsoft365) printf '%s' "Microsoft 365: Word, Excel, PowerPoint, Outlook, Teams, OneDrive. Skills are manual." ;;
    plaud) printf '%s' "Plaud recorder: capture, transcription, summaries, AutoFlow, export. Skills are manual." ;;
    playwright) printf '%s' "Playwright browser automation, component tests, traces (non-Adobe). Skills are manual." ;;
    projects) printf '%s' "Project reference material (nyx). Skill is manual." ;;
    prompt-optimizer) printf '%s' "Author and optimize prompt text. Skill is manual." ;;
    pydantic-ai) printf '%s' "Pydantic AI typed Python agents. Skill is manual." ;;
    supabase) printf '%s' "Supabase Auth, Storage, Edge Functions, Postgres. Skills are manual." ;;
    vercel) printf '%s' "Vercel and Next.js platform skills. Manual except they do not include proactive-agency." ;;
    *) printf '%s' "Skill pack ${1}. Skills are manual unless named proactive-agency." ;;
  esac
}

write_plugin_manifest() {
  local name="$1" dest="$2" description="$3"
  mkdir -p "${dest}/.cursor-plugin"
  cat > "${dest}/.cursor-plugin/plugin.json" <<EOF
{
  "name": "${name}",
  "version": "1.0.0-snapshot",
  "description": "${description}",
  "skills": "skills"
}
EOF
}

# --- flatten every SKILL.md into project + user skill dirs --------------------
log "Loading skills from ${ROOT}/skills"
mkdir -p "$PROJECT_SKILLS" "$USER_SKILLS" "${ROOT}/plugins"
find "$PROJECT_SKILLS" -mindepth 1 -maxdepth 1 -exec rm -rf {} +

skill_count=0
while IFS= read -r skill_md; do
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"
  rel="$(realpath --relative-to="$PROJECT_SKILLS" "$skill_dir")"
  ln -sfn "$rel" "${PROJECT_SKILLS}/${name}"
  rm -rf "${USER_SKILLS}/${name}"
  mkdir -p "${USER_SKILLS}/${name}"
  tar -C "${skill_dir}" --exclude 'AGENTS.md' -cf - . | tar -C "${USER_SKILLS}/${name}" -xf -
  skill_count=$((skill_count + 1))
done < <(find "${ROOT}/skills" -name SKILL.md | sort)
log "Flattened ${skill_count} skills into ${PROJECT_SKILLS} and ${USER_SKILLS}"

# --- one Cursor plugin wrapper per pack ---------------------------------------
mkdir -p "${ROOT}/.cursor-plugin"
{
  echo '{'
  echo '  "name": "cursor-skills-snapshot",'
  echo '  "owner": { "name": "CatCorner22" },'
  echo '  "metadata": {'
  echo '    "description": "All vendored skill packs from this repo, loaded as Cursor plugins.",'
  echo '    "version": "1.0.0"'
  echo '  },'
  echo '  "plugins": ['
} > "${ROOT}/.cursor-plugin/marketplace.json"

first=1
for pack_dir in "${ROOT}/skills"/*/; do
  pack="$(basename "$pack_dir")"
  [[ "$pack" == .* ]] && continue
  wrapper="${ROOT}/plugins/${pack}"
  desc="$(pack_description "$pack")"
  mkdir -p "${wrapper}/.cursor-plugin"
  ln -sfn "$(realpath --relative-to="$wrapper" "$pack_dir")" "${wrapper}/skills"
  write_plugin_manifest "$pack" "$wrapper" "$desc"
  if [[ "$first" -eq 1 ]]; then
    first=0
  else
    echo ',' >> "${ROOT}/.cursor-plugin/marketplace.json"
  fi
  cat >> "${ROOT}/.cursor-plugin/marketplace.json" <<EOF
    {
      "name": "${pack}",
      "source": "./plugins/${pack}",
      "skills": "skills",
      "description": "${desc}"
    }
EOF
done
echo '  ]' >> "${ROOT}/.cursor-plugin/marketplace.json"
echo '}' >> "${ROOT}/.cursor-plugin/marketplace.json"

# --- download marketplace plugin sources --------------------------------------
mkdir -p "$DOWNLOADS" "$LOCAL"
log "Downloading Vercel / Hugging Face / Adobe plugins into ${DOWNLOADS}"
clone_at "https://github.com/vercel/vercel-plugin.git" "$VERCEL_SHA" "${DOWNLOADS}/vercel-plugin" \
  || log "WARN: vercel-plugin clone failed; will fall back to cache"
clone_at "https://github.com/huggingface/skills.git" "$HF_SHA" "${DOWNLOADS}/huggingface-skills" \
  || log "WARN: huggingface/skills clone failed; will fall back to cache"
clone_at "https://github.com/adobe/skills.git" "$ADOBE_SHA" "${DOWNLOADS}/adobe-skills" \
  || log "WARN: adobe/skills clone failed; will fall back to cache"

if vercel_src="$(pick_src "${DOWNLOADS}/vercel-plugin" "${CACHE}/649/${VERCEL_SHA}")"; then
  copy_tree "$vercel_src" "${LOCAL}/vercel"
  copy_tree "${ROOT}/skills/vercel" "${LOCAL}/vercel/skills"
fi
if hf_src="$(pick_src "${DOWNLOADS}/huggingface-skills" "${CACHE}/735/${HF_SHA}")"; then
  copy_tree "$hf_src" "${LOCAL}/huggingface-skills"
  copy_tree "${ROOT}/skills/huggingface" "${LOCAL}/huggingface-skills/skills"
  if [[ -d "${ROOT}/skills/huggingface/hf-mcp" ]]; then
    copy_tree "${ROOT}/skills/huggingface/hf-mcp" "${LOCAL}/huggingface-skills/hf-mcp/skills/hf-mcp"
  fi
fi
if adobe_src="$(pick_src "${DOWNLOADS}/adobe-skills/plugins/app-builder" "${CACHE}/21002971/${ADOBE_SHA}")" \
   || adobe_src="$(pick_src "${DOWNLOADS}/adobe-skills" "${CACHE}/21002971/${ADOBE_SHA}")"; then
  copy_tree "$adobe_src" "${LOCAL}/app-builder"
  copy_tree "${ROOT}/skills/adobe" "${LOCAL}/app-builder/skills"
fi

# Every pack also lands as a local plugin pointing at the snapshot.
for pack_dir in "${ROOT}/skills"/*/; do
  pack="$(basename "$pack_dir")"
  dest="${LOCAL}/${pack}"
  write_plugin_manifest "$pack" "$dest" "$(pack_description "$pack")"
  copy_tree "$pack_dir" "${dest}/skills"
done

log "Project skills: $(find -L "${PROJECT_SKILLS}" -name SKILL.md | wc -l | tr -d ' ')"
log "User skills:    $(find -L "${USER_SKILLS}" -name SKILL.md | wc -l | tr -d ' ')"
log "Local plugins:"
ls -1 "$LOCAL"
log "Done. A new Cursor window or Cloud Agent session loads these. This chat's injected catalog does not reload mid-turn."
