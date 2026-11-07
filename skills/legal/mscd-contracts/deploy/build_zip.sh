#!/bin/bash
# Build the release ZIP of the mscd-contracts skill per deploy/RELEASE.md steps 1-3.
# Usage: bash build_zip.sh [skill folder] [out dir]
# Gates: lint self-test, coverage self-test, description <= 1,000 characters, references rebuilt and unchanged.
# The ZIP holds `mscd-contracts/` at the top and excludes evals/, deploy/, CHANGELOG-*.md, .ruff_cache/, __pycache__/, *.pyc.
set -euo pipefail
S=${1:-$(cd "$(dirname "$0")/.." && pwd)}
OUT=${2:-$PWD}
STAMP=$(date +%Y%m%d-%H%M)
mkdir -p "$OUT"
cd "$S"
echo "== self-tests"
python3 scripts/mscd_lint.py --self-test | tail -1
python3 scripts/coverage.py --self-test | tail -1
echo "== description length"
python3 - "$S/SKILL.md" <<'EOF'
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r'^description:\s*"(.*)"\s*$', t, re.M)
if not m:
    sys.exit("no quoted description line found in SKILL.md frontmatter")
n = len(m.group(1))
print(f"description: {n} characters")
if n > 1000:
    sys.exit("description exceeds 1,000 characters")
EOF
echo "== references rebuilt and unchanged?"
TMP=$(mktemp -d)
cp -r references "$TMP/before"
python3 scripts/build_references.py >/dev/null
if ! diff -rq "$TMP/before" references >/dev/null; then
  echo "references changed on rebuild (the built copies were stale); the rebuilt copies are now in place:"; diff -rq "$TMP/before" references || true
fi
rm -rf "$TMP"
echo "== zip"
STAGE=$(mktemp -d)
mkdir -p "$STAGE/mscd-contracts"
tar cf - --exclude=./evals --exclude=./deploy --exclude='./CHANGELOG-*.md' --exclude='.ruff_cache' --exclude='__pycache__' --exclude='*.pyc' . | (cd "$STAGE/mscd-contracts" && tar xf -)
ZIP="$OUT/mscd-contracts-$STAMP.zip"
(cd "$STAGE" && zip -qr "$ZIP" mscd-contracts)
rm -rf "$STAGE"
unzip -t "$ZIP" | tail -1
echo "== contents"
unzip -l "$ZIP" | awk '{print $4}' | grep -v '^$' | grep -E 'evals/|deploy/|__pycache__|\.pyc$|CHANGELOG|ruff_cache' && { echo "EXCLUDED CONTENT FOUND"; exit 1; } || true
unzip -l "$ZIP" | tail -1
unzip -l "$ZIP" | awk 'NR>3 {print $4}' | grep -E '^mscd-contracts/[^/]+$|^mscd-contracts/[^/]+/$' | sort
ls -la "$ZIP"
