#!/usr/bin/env python3
"""Check that a review accounts for every direct finding the lint made.

The lint's direct findings are usually right. A long review can drop some of them while the reviewer reads
for harder problems, so run this before delivering. A lint finding counts as accounted for when:
  - a finding in findings.json quotes text that overlaps it in the same paragraph,
    or quotes words that contain its match;
  - for a formatting finding with no words (justified, underline, font, size): a finding quotes text in that
    paragraph and names the same kind of formatting, or names it for the whole document; or
  - rejected.json lists it, with a reason (a candidate you checked in context and decided is correct).

  python3 coverage.py <lint.json> <findings.json> [--rejected rejected.json] [--json out.json]
  python3 coverage.py --self-test

findings.json: a list of {"quote": exact contract words, "type", "severity", "fix", "source"} (or {"findings": [...]}).
rejected.json: a list of {"para": n, "match": "the lint's match", "check": "the lint's check", "reason": "why it is correct"}.
An entry in either file with {"check": "<lint check>", "all": true} and a reason or fix accounts for every place that check
fires: use it only when 1 decision really covers all of them (every serial comma added; a check that misreads this contract).
A finding with no words of its own (a formatting, front, numbering or heading finding) is accounted for by a finding that quotes
text in the same paragraph and names the same kind of problem (justified, underline, font, size, title, capitals, numbering).
Low-confidence reminders (attachment-check, when-condition, low ordinal-word) are listed but not required; the lint reports
attachment-check with the rule triggers (source "rules"), and it is the 1 trigger listed here, as optional. A possibly
undefined term is always required, because an undefined term is severity 1 (reject a name or a job title with its reason).
Exit code: 0 when every required lint finding is accounted for; 1 when some aren't; 2 on unreadable input;
3 on an internal error; 5 on a usage error.
"""
import argparse
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli import ArgParser, InputError, FOUND, OK, read_json, run_main, setup_output, write_json  # noqa: E402

QUOTES = str.maketrans({'“': '"', '”': '"', '‘': "'", '’': "'", ' ': ' ', '‑': '-', '–': '-', '—': '-'})  # 1 character for 1
FORMAT = {'justified': r'justif|ragged|left[- ]align|alignment', 'underline': r'underlin', 'font': r'\bfont\b|aptos|typeface',
          'font-size': r'\bsize\b|point|\bpt\b', 'front': r'front|title|cent(?:er|re)|capitals|lead-in|introductory clause|concluding clause',
          'bold-definition': r'bold', 'article-heading': r'capitals|heading', 'enumeration': r'enumerat|numbering|only child|level|sibling'}
WHOLE_DOC = re.compile(r'\b(?:throughout|whole document|every paragraph|all paragraphs|entire (?:agreement|contract|document))\b')
OPTIONAL = {'attachment-check', 'when-condition'}
ALWAYS = {'possibly-undefined-term'}  # an undefined term is severity 1: account for each, even a name (say so in rejected.json)
MIN_QUOTE = 3           # a quote shorter than this (after normalizing) can't place a finding
MIN_SEARCH = 4          # a lint match shorter than this is placed by the lint's offsets, not by searching for its text
CONTEXT = 25            # characters of context on each side of a short match, to place it when its offsets don't line up
LONG_MATCH = 25         # a match at least this long is accounted for by any quote that contains it (a defined term's 1st use)
STATUSES = ('accounted', 'accounted (all)', 'rejected', 'optional', 'MISSING')


def norm(s):
    return re.sub(r'\s+', ' ', str(s or '').translate(QUOTES)).strip()


def to_norm(raw, pos):
    """The offset in norm(raw) of raw offset pos: whitespace runs collapse to 1 space and leading whitespace goes."""
    return len(re.sub(r'\s+', ' ', raw[:max(0, pos)].translate(QUOTES)).lstrip())


def as_list(data, key='findings'):
    if isinstance(data, dict):
        data = next((data[k] for k in (key, 'findings', 'items', 'rejected') if data.get(k)), [])
    if not isinstance(data, list):
        raise InputError(f'expected a list of {key} (or an object with a "{key}" list), not {type(data).__name__}')
    return [x for x in data if isinstance(x, dict)]


def quotes_of(item):
    for k in ('quote', 'anchor', 'text', 'match'):
        v = item.get(k)
        if isinstance(v, str) and len(norm(v)) >= MIN_QUOTE:
            yield norm(v)


def find_spots(items, paras):
    """Every place each finding's quote occurs: (para, start, end, quote, the finding as lowercase JSON).
    A quote found in several paragraphs counts in each; 1 entry with para None keeps it for the long-match rule."""
    spots = []
    for it in items:
        blob = norm(json.dumps(it, ensure_ascii=False)).lower()
        for q in quotes_of(it):
            for pi, txt in paras.items():
                start = txt.find(q)
                while start >= 0:
                    spots.append((pi, start, start + len(q), q.lower(), blob))
                    start = txt.find(q, start + 1)
            spots.append((None, -1, -1, q.lower(), blob))
    return spots


def locate(match, raw, txt, raw_start, raw_end):
    """Where a lint match sits in the normalized paragraph text: (start, end), or None if it can't be placed.
    The lint's own offsets decide which occurrence it is, so a match that occurs twice in a paragraph is placed at
    the right one; its text is the fallback when the offsets don't line up with it."""
    have_offsets = raw is not None and raw_start is not None and raw_end is not None and 0 <= raw_start <= raw_end <= len(raw)
    if have_offsets:
        ns, ne = to_norm(raw, raw_start), to_norm(raw, raw_end)
        piece = norm(raw[raw_start:raw_end])
        if piece and txt[ns:ns + len(piece)] == piece:
            return ns, ns + len(piece)
    if match and len(match) >= MIN_SEARCH:
        hits = [m.start() for m in re.finditer(re.escape(match), txt)]
        if hits:
            ns = min(hits, key=lambda h: abs(h - to_norm(raw, raw_start))) if have_offsets else hits[0]
            return ns, ns + len(match)
    if have_offsets:
        # a short match (the 1 space after a period): take the words around it
        win = norm(raw[max(0, raw_start - CONTEXT):raw_end + CONTEXT])
        wi = txt.find(win)
        if wi >= 0:
            return wi, wi + len(win)
        return ns, max(ne, ns + 1)
    return None


def occurrence_status(f, pi, raw_start, raw_end, match, raw, txt, spots, whole_doc, accounts_all, rejected):
    """The status of 1 occurrence of a lint finding: accounted, accounted (all), rejected, or None (not accounted for)."""
    check = f['check']
    if check in FORMAT or not match:
        pat = FORMAT.get(check, re.escape(check))
        if any(sp[0] == pi and re.search(pat, sp[4]) for sp in spots) or \
                any(re.search(pat, b) and WHOLE_DOC.search(b) for b in whole_doc):
            return 'accounted'
    else:
        where = locate(match, raw, txt, raw_start, raw_end)
        if where is None:
            # the match isn't in the paragraph's text (Word's automatic numbering: an only child 1., an article heading II.):
            # any finding that quotes that paragraph accounts for it
            if any(sp[0] == pi for sp in spots):
                return 'accounted'
        else:
            ns, ne = where
            # overlap in the same paragraph; or a quote elsewhere that contains a long match (a defined term's 1st use);
            # a short match (Company, Base Rent) must be overlapped where it occurs
            if any(sp[0] == pi and sp[1] < ne and sp[2] > ns for sp in spots) or \
                    (len(match) >= LONG_MATCH and any(match.lower() in sp[3] for sp in spots)):
                return 'accounted'
    if check in accounts_all:
        return 'accounted (all)'  # 1 entry that covers every place this check fires, with its reason or fix
    for r in rejected:
        if r.get('para') in (pi, None) and r.get('check', check) == check and norm(r.get('reason', '')) \
                and (norm(r.get('match', '')) == match or (match and match.lower() in norm(r.get('quote', '')).lower())):
            return 'rejected'
    return None


def coverage(lint, found, rejected=()):
    """Return (rows, missing): 1 row per occurrence of each direct lint finding, with its status."""
    if not isinstance(lint, dict) or not isinstance(lint.get('findings'), list) or not isinstance(lint.get('paragraphs'), list):
        raise InputError('the lint file is not the JSON that mscd_lint.py --json writes (an object with "paragraphs" and "findings" lists)')
    raw = {}
    for p in lint.get('paragraphs', []):
        if not isinstance(p, dict) or 'idx' not in p:
            raise InputError('the lint file has a paragraph without an "idx"; regenerate it with mscd_lint.py --json')
        raw[p['idx']] = str(p.get('text', ''))
    paras = {pi: norm(t) for pi, t in raw.items()}
    items = list(found)
    spots = find_spots(items, paras)
    whole_doc = [norm(json.dumps(it, ensure_ascii=False)).lower() for it in items]
    accounts_all = {x.get('check') for x in items + list(rejected) if x.get('all') and norm(x.get('reason') or x.get('fix') or '')}
    rows, missing = [], []
    for f in lint.get('findings', []):
        if not isinstance(f, dict) or 'check' not in f:
            raise InputError('the lint file has a finding without a "check"; regenerate it with mscd_lint.py --json')
        if f.get('source') == 'rules' and f['check'] not in OPTIONAL:
            continue  # rule triggers are pointers for the passes, not findings to account for; the attachment reminder is listed as optional
        optional = f['check'] in OPTIONAL or (f.get('confidence') == 'low' and f['check'] not in ALWAYS)
        occ = f.get('occurrences') or [[f.get('para'), f.get('start', -1), f.get('end', -1), f.get('match', '')]]
        for o in occ:
            if not isinstance(o, (list, tuple)) or len(o) != 4:
                raise InputError(f'the lint file has an occurrence of {f["check"]} that is not [para, start, end, match]')
            pi, s, e, m = o
            m = norm(m)
            status = occurrence_status(f, pi, s, e, m, raw.get(pi), paras.get(pi, ''), spots, whole_doc, accounts_all, rejected)
            row = {'para': pi, 'check': f['check'], 'severity': f.get('severity'), 'match': m[:100], 'message': str(f.get('message', ''))[:160],
                   'status': status or ('optional' if optional else 'MISSING')}
            rows.append(row)
            if row['status'] == 'MISSING':
                missing.append(row)
    return rows, missing


def self_test():
    lint = {'paragraphs': [{'idx': 0, 'text': 'The Company shall pay.  The Company shall deliver the Units.'},
                           {'idx': 1, 'text': 'Acme shall pay the Fee.'}],
            'findings': [{'check': 'party-article', 'severity': 2, 'source': 'house', 'confidence': 'high',
                          'occurrences': [[0, 0, 11, 'The Company'], [0, 24, 35, 'The Company']]},
                         {'check': 'justified', 'severity': 3, 'source': 'house', 'para': 1, 'start': -1, 'end': -1, 'match': ''},
                         {'check': 'attachment-check', 'severity': 3, 'source': 'rules', 'para': 1, 'start': -1, 'end': -1, 'match': ''},
                         {'check': 'serial-comma', 'severity': 2, 'source': 'house', 'para': 1, 'start': 0, 'end': 4, 'match': 'Acme'},
                         {'check': 'rule:rule', 'severity': 1, 'source': 'rules', 'para': 1, 'start': 0, 'end': 4, 'match': 'Acme'}]}
    found = [{'quote': 'The Company shall deliver the Units', 'type': 'party-article', 'fix': 'Company shall deliver the Units.'},
             {'quote': 'Acme shall pay the Fee', 'type': 'justified paragraph', 'fix': 'left-align'}]
    rows, missing = coverage(lint, found)
    st = [(r['check'], r['status']) for r in rows]
    cases = [('2nd occurrence quoted: the 1st is still missing', st[0] == ('party-article', 'MISSING') and st[1] == ('party-article', 'accounted')),
             ('a formatting finding named in a finding quoting its paragraph', st[2] == ('justified', 'accounted')),
             ('the attachment reminder (a rule-sourced trigger) is listed as optional', st[3] == ('attachment-check', 'optional')),
             ('a short match overlapped by a quote', st[4] == ('serial-comma', 'accounted')),
             ('rule triggers are skipped', len(rows) == 5)]
    rows2, _ = coverage(lint, found[1:], rejected=[{'para': 0, 'check': 'party-article', 'match': 'The Company', 'reason': 'test'}])
    cases.append(('rejected.json accounts for a match', [r['status'] for r in rows2[:2]] == ['rejected', 'rejected']))
    rows3, _ = coverage(lint, found[1:] + [{'check': 'party-article', 'all': True, 'fix': 'drop every article'}])
    cases.append(('an all entry accounts for every occurrence', [r['status'] for r in rows3[:2]] == ['accounted (all)'] * 2))
    cases.append(('offsets map past 2 spaces', to_norm(lint['paragraphs'][0]['text'], 24) == 23))
    for bad, why in (([], 'a list instead of an object'), ({'paragraphs': [], 'findings': [{'para': 0}]}, 'a finding without a check'),
                     ({}, 'an object with neither list'), ({'findings': []}, 'an object without the paragraphs list')):
        try:
            coverage(bad, found)
            cases.append((f'rejects {why}', False))
        except InputError:
            cases.append((f'rejects {why}', True))
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, 'x.json')
        with open(p, 'w', encoding='utf-8') as fh:
            fh.write('{"findings": [')
        try:
            read_json(p)
            cases.append(('rejects truncated JSON', False))
        except InputError:
            cases.append(('rejects truncated JSON', True))
    fails = [n for n, ok in cases if not ok]
    for n in fails:
        print(f'FAIL: {n}')
    print(f'self-test: {len(cases) - len(fails)}/{len(cases)} passed')
    return FOUND if fails else OK


def main():
    setup_output()
    ap = ArgParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('lint', nargs='?')
    ap.add_argument('findings', nargs='?')
    ap.add_argument('--rejected')
    ap.add_argument('--json')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.lint and a.findings):
        ap.error('give the lint JSON and the findings JSON (or --self-test)')
    lint = read_json(a.lint, 'lint file')
    found = as_list(read_json(a.findings, 'findings file'))
    rejected = as_list(read_json(a.rejected, 'rejected file'), 'rejected') if a.rejected else []
    rows, missing = coverage(lint, found, rejected)
    req = [r for r in rows if r['status'] != 'optional']
    n_trig = sum(1 for f in lint.get('findings', []) if isinstance(f, dict) and f.get('source') == 'rules' and f.get('check') not in OPTIONAL)
    n_direct = len({(r['check'], r['message']) for r in req})
    print(f"Coverage: {len(req) - len(missing)} of {len(req)} required places accounted for; {len(missing)} missing. "
          f"Each place a direct finding fires counts once ({n_direct} direct findings); the {n_trig} rule triggers are optional pointers for the passes and not counted.")
    for r in sorted(missing, key=lambda r: (r['severity'] or 9, r['para'] if r['para'] is not None else -1)):
        print(f"  MISSING  sev {r['severity']}  para {r['para']}  {r['check']}: {r['match']!r}  -- {r['message']}")
    if missing:
        print('For each, add a finding (or an edit), or list it in rejected.json with the reason it is correct; then run this again.')
    if a.json:
        write_json(a.json, {'required': len(req), 'missing': missing, 'rows': rows})
    return FOUND if missing else OK


if __name__ == '__main__':
    sys.exit(run_main('coverage.py', main))
