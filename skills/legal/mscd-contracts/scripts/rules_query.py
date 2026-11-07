#!/usr/bin/env python3
"""Look up MSCD rules in data/rules.jsonl, with Blake's house overrides applied.

Examples:
  python3 scripts/rules_query.py --id R-3.89-shall-duty   (or --id 3.89, or --id R-3.89)
  python3 scripts/rules_query.py --word "and/or"
  python3 scripts/rules_query.py --para 3.324
  python3 scripts/rules_query.py --topic ambiguity --kind ambiguity-cause --brief
  python3 scripts/rules_query.py --key verbs --severity 1 --brief
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli import ArgParser, FOUND, OK, run_main, setup_output  # noqa: E402
from _rules_data import house_notes, load_overrides, load_records  # noqa: E402


def load():
    ov = load_overrides()
    return load_records(), house_notes(ov), ov.get('counterparty_review_default', 'flag')


def fmt(r, house, brief, counterparty='flag'):
    """1 rule as text. A field a record lacks reads as empty (record_problem allows a missing optional field)."""
    paras, pages = r.get('paras') or [], r.get('pdf_pages') or []
    # the house rule on the other side's drafts supersedes the record's own counterparty verdict, so only the house rule is shown
    review = f"review of other side's draft: {counterparty} (house rule)" if counterparty else f"review of other side's draft: {r.get('counterparty_review') or 'flag'}"
    lines = [f"{r['id']}  [severity {r['severity']}; {r['kind']}; {r['status']}; {review}]",
             f"  Rule: {r['statement']}",
             f"  MSCD: {', '.join(paras) or 'Introduction'}" + (f"; PDF p. {', '.join(map(str, pages[:4]))}" if pages else '') + f"; {r.get('section') or ''}"]
    if r['id'] in house:
        lines.append(f"  HOUSE: {house[r['id']]}")
    if brief:
        return '\n'.join(lines)
    t = r.get('trigger') or {}
    if t.get('words') or t.get('signal'):
        lines.append(f"  Look for: {', '.join(t.get('words') or [])}{'; ' if t.get('words') and t.get('signal') else ''}{t.get('signal','')}")
    for k, lab in (('test', 'Test'), ('fix', 'Fix')):
        if r.get(k):
            lines.append(f"  {lab}: {r[k]}")
    for e in r.get('exceptions') or []:
        lines.append(f"  Exception: {e}")
    for e in r.get('examples') or []:
        if isinstance(e, dict) and (e.get('before') or e.get('after')):
            tag = 'book example' if e.get('verified') else 'example (unverified wording)'
            lines.append(f"  {tag}: {e.get('before') or '(none)'}  ->  {e.get('after') or '(see fix)'}")
    if r.get('cross_refs'):
        lines.append(f"  See also: {', '.join(r['cross_refs'][:12])}")
    if r.get('notes'):
        lines.append(f"  Notes: {r['notes'][:900]}")
    return '\n'.join(lines)


def main():
    setup_output()
    ap = ArgParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--id', action='append', default=[])
    ap.add_argument('--word', help='case-insensitive plain-text search (not a regex) in trigger words, statement and section')
    ap.add_argument('--para', help='MSCD paragraph, e.g. 3.324')
    ap.add_argument('--topic')
    ap.add_argument('--key')
    ap.add_argument('--kind')
    ap.add_argument('--severity', type=int, help='maximum severity to include (1, 2 or 3)')
    ap.add_argument('--status', help='book, rider, proposal or elaboration')
    ap.add_argument('--brief', action='store_true')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--limit', type=int, default=40)
    a = ap.parse_args()
    if a.severity is not None and a.severity not in (1, 2, 3):
        ap.error('--severity must be 1, 2 or 3')
    if a.limit is not None and a.limit < 1:
        ap.error('--limit must be 1 or more')
    recs, house, counterparty = load()
    out, notes = recs, []  # notes: what the reader must know before the results (an inexact match)
    if a.id:
        want = set(a.id)
        exact = [r for r in out if r['id'] in want]
        missing = want - {r['id'] for r in exact}
        # a partial id (R-3.358, 3.358, R-3.358-conditional) finds every rule whose id starts with it or that cites that paragraph
        loose = []
        for w in missing:
            stem = w if w.startswith('R-') else 'R-' + w
            para = re.match(r"R-(\d+\.\d+)", stem)
            # whole id parts only: 13.5 finds R-13.5-... and rules citing 13.5, never R-13.50 or 13.55
            loose += [r for r in out if r not in exact and r not in loose and (r['id'] == stem or r['id'].startswith(stem + '-')
                      or (para and para.group(1) in r.get('paras', [])))]
        if loose:
            notes.append(f"No exact match for {', '.join(sorted(missing))}; showing the rules whose id starts with it or that cite that paragraph.")
        out = exact + loose
    if a.word:
        w = a.word.lower()
        out = [r for r in out if w in ' '.join((r.get('trigger') or {}).get('words') or []).lower() or w in r['statement'].lower() or w in (r.get('section') or '').lower()]
    if a.para:
        stated = [r for r in out if a.para in (r.get('paras') or [])]
        cited = [r for r in out if r not in stated and a.para in (r.get('cross_refs') or [])]
        if not stated and cited:
            notes.append(f"No exact match: no rule states MSCD {a.para}; showing the rules that cite it under See also, which may be about something else.")
        out = stated + cited
    for f in ('topic', 'kind', 'status'):
        v = getattr(a, f)
        if v:
            out = [r for r in out if r.get(f) == v]
    if a.key:
        out = [r for r in out if a.key in (r.get('key_items') or [])]
    if a.severity is not None:
        out = [r for r in out if r['severity'] <= a.severity]
    if not out:
        # in JSON mode stdout stays pure JSON lines; the notice goes to stderr
        print('No matching rules.', file=sys.stderr if a.json else sys.stdout)
        return FOUND
    shown = out[:a.limit]
    for n in notes:
        print(f'({n})', file=sys.stderr if a.json else sys.stdout)  # before the results, so a near match is never read as the rule asked for
    if a.json:
        for r in shown:
            print(json.dumps(dict(r, house=house.get(r['id'], '')), ensure_ascii=False))
    else:
        print('\n\n'.join(fmt(r, house, a.brief, counterparty) for r in shown))
    if len(out) > a.limit:
        # in JSON mode keep stdout pure JSON lines; the notice goes to stderr
        print(f'\n({len(out) - a.limit} more; raise --limit or narrow the search)', file=sys.stderr if a.json else sys.stdout)
    return OK


if __name__ == '__main__':
    sys.exit(run_main('rules_query.py', main))
