#!/bin/bash
# gate.sh <candidate skill folder> <baseline skill folder> [out dir]
# The regression gate every change to the mscd-contracts skill must pass before it replaces the master.
# It fails (exit 1) when the candidate is worse than the baseline on any measured number:
#   1. lint self-test and coverage self-test pass;
#   2. the 3 phrase-variant shares: caught counts do not fall, look-alike hits do not rise;
#   3. every keyed corpus (evals/corpus, corpus3-corpus7): planted issues found by a direct finding do not fall,
#      and traps flagged (false alarms) do not rise;
#   4. the description stays at or under 1,000 characters; JSON data files parse; references rebuild unchanged.
# It also writes, per corpus, the issues found before and not after (a "lost" list), so a reviewer can read why.
set -uo pipefail
C=${1:?candidate skill folder}; B=${2:?baseline skill folder}
S=${MSCD_TEST_ROOT:-/tmp/claude-0/-home-claude/d78606e6-7e6f-59c2-8e58-1a65259e0dbc/scratchpad}
O=${3:-$S/r4/release/gate-$(date +%Y%m%d-%H%M)}; mkdir -p "$O"
FAIL=0; fail() { echo "FAIL: $*"; FAIL=1; }

echo "== 1. self-tests"
python3 "$C/scripts/mscd_lint.py" --self-test > "$O/selftest.txt" 2>&1 || fail "lint self-test"; tail -1 "$O/selftest.txt"
python3 "$C/scripts/coverage.py" --self-test > "$O/coverage.txt" 2>&1 || fail "coverage self-test"; tail -1 "$O/coverage.txt"

echo "== 2. phrase-variant shares"
V=$S/r4/variants
for f in share1-categories share2-phrases share3-numbers-time; do
  b=$(python3 $V/test_variants.py "$B" $V/$f.json --show 0 2>&1 | head -1); c=$(python3 $V/test_variants.py "$C" $V/$f.json --show 0 2>&1 | head -1)
  echo "$f: baseline [$b] candidate [$c]"
  python3 - "$b" "$c" "$f" <<'EOF' || FAIL=1
import re, sys
def nums(s):  # "... caught by a direct finding 316/319 (99.1%); look-alikes flagged 1/91"
    m = re.search(r"finding (\d+)/\d+.*?flagged (\d+)/", s)
    if not m: print(f"FAIL: can't read share line: {s}"); sys.exit(1)
    return int(m.group(1)), int(m.group(2))
b, c = nums(sys.argv[1]), nums(sys.argv[2])
if c[0] < b[0] or c[1] > b[1]:
    print(f"FAIL: {sys.argv[3]} got worse: {sys.argv[1]} -> {sys.argv[2]}"); sys.exit(1)
EOF
done

echo "== 3. keyed corpora"
score() { # $1 skill, $2 corpus root, $3 json out
  python3 "$1/evals/corpus/score.py" lint --root "$2" --json "$3" 2>&1 | grep -E "^Planted|^Traps" ; }
for root in "$C/evals/corpus" $S/corpus3 $S/corpus4 $S/corpus5 $S/corpus6 $S/corpus7; do
  [ -d "$root/keys" ] || continue
  n=$(basename $(dirname "$root"))-$(basename "$root")
  bt=$(score "$B" "${root/$C/$B}" "$O/$n-base.json"); ct=$(score "$C" "$root" "$O/$n-cand.json")
  echo "$n"; echo "  baseline:  $(echo $bt)"; echo "  candidate: $(echo $ct)"
  python3 - "$O/$n-base.json" "$O/$n-cand.json" "$O/$n-lost.txt" "$n" <<'EOF' || FAIL=1
import json, sys
b, c = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
def found(d): return {(r['id'], r['n']) for r in d.get('rows', []) if r.get('direct')}
def traps(d): return {(r['id'], r.get('anchor')) for r in d.get('traps_hit', [])}
lost = sorted(found(b) - found(c)); gained = sorted(found(c) - found(b))
rows = {(r['id'], r['n']): r for r in b.get('rows', [])}
with open(sys.argv[3], 'w') as fh:
    for k in lost: fh.write(f"LOST {k} {rows[k].get('type')} | {rows[k].get('anchor')}\n")
    for k in gained: fh.write(f"GAINED {k}\n")
    for k in sorted(traps(c) - traps(b)): fh.write(f"NEW FALSE ALARM {k}\n")
bad = len(found(c)) < len(found(b)) or len(traps(c)) > len(traps(b))
print(f"  found {len(found(b))} -> {len(found(c))} (lost {len(lost)}, gained {len(gained)}); traps {len(traps(b))} -> {len(traps(c))}")
if bad: print(f"FAIL: {sys.argv[4]} got worse (see {sys.argv[3]})"); sys.exit(1)
EOF
done

echo "== 4. data, description, references"
python3 - "$C" <<'EOF' || FAIL=1
import json, os, re, sys
k = sys.argv[1]
for f in ('house-overrides.json', 'terms-of-art.json', 'phrase-variants.json'):
    json.load(open(os.path.join(k, 'data', f), encoding='utf-8'))
ids = [json.loads(l)['id'] for l in open(os.path.join(k, 'data', 'rules.jsonl'), encoding='utf-8') if l.strip()]
assert len(ids) == len(set(ids)), 'duplicate rule ids'
t = open(os.path.join(k, 'SKILL.md'), encoding='utf-8').read()
m = re.search(r'^description:\s*"(.*)"\s*$', t, re.M); n = len(m.group(1)) if m else 10**6
print(f"data parse ok; {len(ids)} rules; description {n} characters")
if n > 1000: print('FAIL: description over 1,000 characters'); sys.exit(1)
EOF
TMP=$(mktemp -d); cp -r "$C" "$TMP/k"; (cd "$TMP/k" && python3 scripts/build_references.py >/dev/null 2>&1) || fail "build_references"
diff -rq "$C/references" "$TMP/k/references" >/dev/null || fail "references are stale: run scripts/build_references.py"; rm -rf "$TMP"

echo "== result: $([ $FAIL = 0 ] && echo PASS || echo FAIL)   (details in $O)"
exit $FAIL
