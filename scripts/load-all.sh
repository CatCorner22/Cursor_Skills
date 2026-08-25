#!/usr/bin/env bash
# Download (if needed) and load every snapshotted skill plus the Vercel,
# Hugging Face, and Adobe App Builder plugins.
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

copy_tree() {
  local src="$1" dest="$2"
  mkdir -p "$dest"
  # Portable recursive copy (rsync is not always installed).
  tar -C "$src" \
    --exclude '.git' \
    --exclude 'upstream' \
    --exclude '.claude' \
    --exclude '.claude-plugin' \
    --exclude '.kimi-plugin' \
    -cf - . | tar -C "$dest" -xf -
}

# --- project + user skills (patched snapshot) --------------------------------
log "Loading 63 patched skills into ${PROJECT_SKILLS} and ${USER_SKILLS}"
mkdir -p "$PROJECT_SKILLS" "$USER_SKILLS"
# Remove stale flatten entries but keep the directory.
find "$PROJECT_SKILLS" -mindepth 1 -maxdepth 1 -exec rm -rf {} +

while IFS= read -r skill_md; do
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"
  rel="$(realpath --relative-to="$PROJECT_SKILLS" "$skill_dir")"
  ln -sfn "$rel" "${PROJECT_SKILLS}/${name}"
  rm -rf "${USER_SKILLS}/${name}"
  mkdir -p "${USER_SKILLS}/${name}"
  tar -C "${skill_dir}" -cf - . | tar -C "${USER_SKILLS}/${name}" -xf -
done < <(find "${ROOT}/skills" -name SKILL.md | sort)

# --- repo plugin wrappers (skills -> snapshot) --------------------------------
ln -sfn ../../skills/cursor-cloud "${ROOT}/plugins/cursor-cloud/skills"
ln -sfn ../../skills/vercel "${ROOT}/plugins/vercel/skills"
ln -sfn ../../skills/huggingface "${ROOT}/plugins/huggingface-skills/skills"
ln -sfn ../../skills/adobe "${ROOT}/plugins/app-builder/skills"

# --- download upstream plugin repos (extras: agents, commands, MCP) -----------
mkdir -p "$DOWNLOADS"
log "Downloading plugin sources into ${DOWNLOADS}"
clone_at "https://github.com/vercel/vercel-plugin.git" "$VERCEL_SHA" "${DOWNLOADS}/vercel-plugin" \
  || log "WARN: vercel-plugin clone failed; will fall back to cache"
clone_at "https://github.com/huggingface/skills.git" "$HF_SHA" "${DOWNLOADS}/huggingface-skills" \
  || log "WARN: huggingface/skills clone failed; will fall back to cache"
clone_at "https://github.com/adobe/skills.git" "$ADOBE_SHA" "${DOWNLOADS}/adobe-skills" \
  || log "WARN: adobe/skills clone failed; will fall back to cache"

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

# --- install full plugins to ~/.cursor/plugins/local --------------------------
log "Installing plugins into ${LOCAL}"
mkdir -p "$LOCAL"

vercel_src="$(pick_src "${DOWNLOADS}/vercel-plugin" "${CACHE}/649/${VERCEL_SHA}")"
hf_src="$(pick_src "${DOWNLOADS}/huggingface-skills" "${CACHE}/735/${HF_SHA}")"
adobe_src="$(pick_src "${DOWNLOADS}/adobe-skills/plugins/app-builder" "${CACHE}/21002971/${ADOBE_SHA}")"
adobe_src="${adobe_src:-$(pick_src "${DOWNLOADS}/adobe-skills" "${CACHE}/21002971/${ADOBE_SHA}")}"

copy_tree "$vercel_src" "${LOCAL}/vercel"
copy_tree "${ROOT}/skills/vercel" "${LOCAL}/vercel/skills"

copy_tree "$hf_src" "${LOCAL}/huggingface-skills"
copy_tree "${ROOT}/skills/huggingface" "${LOCAL}/huggingface-skills/skills"
if [[ -d "${ROOT}/skills/huggingface/hf-mcp" ]]; then
  copy_tree "${ROOT}/skills/huggingface/hf-mcp" "${LOCAL}/huggingface-skills/hf-mcp/skills/hf-mcp"
fi

copy_tree "$adobe_src" "${LOCAL}/app-builder"
copy_tree "${ROOT}/skills/adobe" "${LOCAL}/app-builder/skills"

# Cursor Cloud pack (not a marketplace plugin; load as a local plugin)
mkdir -p "${LOCAL}/cursor-cloud/.cursor-plugin" "${LOCAL}/cursor-cloud/skills"
cp "${ROOT}/plugins/cursor-cloud/.cursor-plugin/plugin.json" "${LOCAL}/cursor-cloud/.cursor-plugin/plugin.json"
copy_tree "${ROOT}/skills/cursor-cloud" "${LOCAL}/cursor-cloud/skills"

# Also symlink repo wrappers for discovery
ln -sfn "${ROOT}/plugins/cursor-cloud" "${LOCAL}/cursor-cloud-repo" || true
ln -sfn "${ROOT}/plugins/vercel" "${LOCAL}/vercel-snapshot" || true
ln -sfn "${ROOT}/plugins/huggingface-skills" "${LOCAL}/huggingface-skills-snapshot" || true
ln -sfn "${ROOT}/plugins/app-builder" "${LOCAL}/app-builder-snapshot" || true

# --- inventory ----------------------------------------------------------------
skill_count="$(find -L "${PROJECT_SKILLS}" -name SKILL.md | wc -l | tr -d ' ')"
user_count="$(find -L "${USER_SKILLS}" -name SKILL.md | wc -l | tr -d ' ')"
log "Project skills: ${skill_count}  User skills: ${user_count}"
log "Local plugins:"
ls -1 "$LOCAL"
log "Done. New Cloud Agent / Cursor sessions pick these up; this chat's already-injected catalog does not reload mid-turn."
