#!/usr/bin/env python3
"""Look up MSCD rules in data/rules.jsonl, with Blake's house overrides applied.

Examples:
  python3 scripts/rules_query.py --id R-3.89-shall-duty   (or --id 3.89, or --id R-3.89)
  python3 scripts/rules_query.py --word "and/or"
  python3 scripts/rules_query.py --para 3.324
  python3 scripts/rules_query.py --topic ambiguity --kind ambiguity-cause --brief
  python3 scripts/rules_query.py --key verbs --severity 1 --brief
"""
import argparse, json, os, re, signal, sys

if hasattr(signal, 'SIGPIPE'):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # piping into head ends quietly

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load():
    recs = [json.loads(l) for l in open(os.path.join(ROOT, 'data', 'rules.jsonl'), encoding='utf-8') if l.strip()]
    ov = json.load(open(os.path.join(ROOT, 'data', 'house-overrides.json'), encoding='utf-8'))
    house = {}
    for o in ov['overrides']:
        for rid in o['rule_ids']:
            house[rid] = ('PARTLY SUPERSEDED. ' if o.get('partial') else 'SUPERSEDED. ') + o['replacement']
    for a in ov.get('additions', []):
        for rid in a['applies_with']:
            house[rid] = (house.get(rid, '') + ' ' if rid in house else '') + 'ADDITION. ' + a['statement']
    return recs, house


def fmt(r, house, brief):
    lines = [f"{r['id']}  [severity {r['severity']}; {r['kind']}; {r['status']}; review of other side's draft: {r['counterparty_review']} (house rule: flag)]",
             f"  Rule: {r['statement']}",
             f"  MSCD: {', '.join(r['paras']) or 'Introduction'}" + (f"; PDF p. {', '.join(map(str, r['pdf_pages'][:4]))}" if r['pdf_pages'] else '') + f"; {r['section']}"]
    if r['id'] in house:
        lines.append(f"  HOUSE: {house[r['id']]}")
    if brief:
        return '\n'.join(lines)
    t = r['trigger']
    if t.get('words') or t.get('signal'):
        lines.append(f"  Look for: {', '.join(t.get('words') or [])}{'; ' if t.get('words') and t.get('signal') else ''}{t.get('signal','')}")
    for k, lab in (('test', 'Test'), ('fix', 'Fix')):
        if r.get(k):
            lines.append(f"  {lab}: {r[k]}")
    for e in r['exceptions']:
        lines.append(f"  Exception: {e}")
    for e in r['examples']:
        if isinstance(e, dict) and (e.get('before') or e.get('after')):
            tag = 'book example' if e.get('verified') else 'example (unverified wording)'
            lines.append(f"  {tag}: {e.get('before') or '(none)'}  ->  {e.get('after') or '(see fix)'}")
    if r['cross_refs']:
        lines.append(f"  See also: {', '.join(r['cross_refs'][:12])}")
    if r['notes']:
        lines.append(f"  Notes: {r['notes'][:900]}")
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--id', action='append', default=[])
    ap.add_argument('--word', help='case-insensitive plain-text search (not a regex) in trigger words, statement and section')
    ap.add_argument('--para', help='MSCD paragraph, e.g. 3.324')
    ap.add_argument('--topic'); ap.add_argument('--key'); ap.add_argument('--kind')
    ap.add_argument('--severity', type=int, help='maximum severity to include (1, 2 or 3)')
    ap.add_argument('--status', help='book, rider, proposal or elaboration')
    ap.add_argument('--brief', action='store_true'); ap.add_argument('--json', action='store_true')
    ap.add_argument('--limit', type=int, default=40)
    a = ap.parse_args()
    recs, house = load()
    out = recs
    if a.id:
        want = set(a.id); exact = [r for r in out if r['id'] in want]
        missing = want - {r['id'] for r in exact}
        # a partial id (R-3.358, 3.358, R-3.358-conditional) finds every rule whose id starts with it or that cites that paragraph
        loose = []
        for w in missing:
            stem = w if w.startswith('R-') else 'R-' + w
            para = re.match(r"R-(\d+\.\d+)", stem)
            loose += [r for r in out if r not in exact and r not in loose and (r['id'].startswith(stem) or (para and para.group(1) in r.get('paras', [])))]
        if loose:
            print(f"(no exact id for {', '.join(sorted(missing))}; showing rules that start with it or cite that paragraph)", file=sys.stderr)
        out = exact + loose
    if a.word:
        w = a.word.lower()
        out = [r for r in out if w in ' '.join(r['trigger'].get('words') or []).lower() or w in r['statement'].lower() or w in r['section'].lower()]
    if a.para:
        out = [r for r in out if a.para in r['paras'] or a.para in r['cross_refs']]
    for f in ('topic', 'kind', 'status'):
        v = getattr(a, f)
        if v: out = [r for r in out if r[f] == v]
    if a.key: out = [r for r in out if a.key in r['key_items']]
    if a.severity: out = [r for r in out if r['severity'] <= a.severity]
    if not out:
        print('No matching rules.'); return 1
    shown = out[:a.limit]
    if a.json:
        for r in shown:
            r = dict(r); r['house'] = house.get(r['id'], ''); print(json.dumps(r, ensure_ascii=False))
    else:
        print('\n\n'.join(fmt(r, house, a.brief) for r in shown))
    if len(out) > a.limit:
        # in JSON mode keep stdout pure JSON lines; the notice goes to stderr
        print(f'\n({len(out) - a.limit} more; raise --limit or narrow the search)', file=sys.stderr if a.json else sys.stdout)
    return 0


if __name__ == '__main__':
    sys.exit(main())
