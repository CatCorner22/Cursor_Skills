#!/usr/bin/env bash
# Package each skill under skills/kimi/*/ as its own Kimi Code CLI plugin ZIP.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${ROOT}/skills/kimi"
OUT="${ROOT}/dist/kimi"
TMP="${TMPDIR:-/tmp}/kimi-skill-pack-$$"

mkdir -p "$OUT"
trap 'rm -rf "$TMP"' EXIT

log() { printf '%s\n' "$*"; }

title_from_id() {
  # kimi-api-fundamentals -> Kimi Api Fundamentals
  local id="$1" word out=""
  id="${id#kimi-}"
  for word in ${id//-/ }; do
  out="${out}${word^} "
  done
  printf '%s' "${out% }"
}

count=0
while IFS= read -r skill_md; do
  skill_dir="$(dirname "$skill_md")"
  skill_id="$(basename "$skill_dir")"
  display="$(title_from_id "$skill_id")"

  rm -rf "$TMP"
  mkdir -p "$TMP/skills/${skill_id}"
  cp -a "${skill_dir}/." "$TMP/skills/${skill_id}/"

  cat > "$TMP/kimi.plugin.json" <<EOF
{
  "name": "${skill_id}",
  "version": "1.0.0",
  "description": "Moonshot Kimi skill: ${skill_id} (from Cursor_Skills)",
  "skills": "./skills/",
  "interface": {
    "displayName": "${display}",
    "shortDescription": "Kimi platform skill — ${skill_id}"
  }
}
EOF

  zip_path="${OUT}/${skill_id}.zip"
  rm -f "$zip_path"
  (cd "$TMP" && zip -qr "$zip_path" .)

  log "Wrote ${zip_path}"
  log "  Install: /plugins install ${zip_path}"
  count=$((count + 1))
done < <(find "$SRC" -mindepth 2 -maxdepth 2 -name SKILL.md | sort)

log "Packaged ${count} Kimi plugin ZIP(s) into ${OUT}"
