#!/usr/bin/env python3
"""Score the mscd-contracts skill against the contract corpus and its answer keys.

Each contract in contracts/ has an answer key in keys/ that lists planted issues and traps
(correct text that looks wrong). Each issue and trap has an `anchor`: a short exact substring
that occurs once in the contract.

  score.py lint [--json out.json]                 score scripts/mscd_lint.py on every contract
  score.py findings <runs-dir> [--json out.json]  score skill runs: <runs-dir>/<id>/findings.json
  score.py check                                  validate the keys (anchors occur exactly once)

findings.json is a list of {"quote": exact contract text, "type": label, "severity": 1-3,
"fix": proposed wording or "keep", "source": citation}. A planted issue counts as found when a
finding's quote contains its anchor, or when the quote's location in the contract overlaps the
anchor. A trap counts as a false alarm when a finding overlaps it and doesn't say to keep it.
"""
import argparse, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(SKILL, 'scripts'))
import mscd_lint as L  # noqa: E402
import signal  # noqa: E402
if hasattr(signal, 'SIGPIPE'):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # piping into head ends quietly

QUOTES = str.maketrans({'“': '"', '”': '"', '‘': "'", '’': "'", ' ': ' '})
FORMAT_WORDS = {'font': r'font|aptos|times new roman|arial|cambria|calibri', 'size': r'\bsize\b|point|\bpt\b',
                'justified': r'justif', 'underline': r'underlin', 'numbering': r'numbering|only child|enumerat'}
# lint checks that answer each catalog type (direct findings only; rule triggers are scored separately)
LINT_TYPES = {
    'category-should': {'should'}, 'negative-subject-shall': {'negative-subject-shall'}, 'and-or': {'and-or'},
    'efforts': {'efforts', 'efforts-mixed'}, 'represents-warrants': {'represents-warrants'}, 'agrees-to': {'agrees-to'},
    'sole-discretion': {'sole-discretion'}, 'time-is-of-the-essence': {'time-is-of-the-essence'}, 'doublet': {'doublet'},
    'arising-out-of': {'arising-out-of'}, 'throat-clearing': {'throat-clearing'}, 'successors-assigns': {'successors-assigns'},
    'survival': {'survival'}, 'usage': {'usage'}, 'category-will': {'category-will'}, 'category-must': {'category-must'},
    'shall-in-condition': {'shall-in-condition'}, 'passive-voice': {'passive-voice'},
    'reduced-passive': {'reduced-passive'}, 'number-words': {'number-word', 'words-and-digits'},
    'ordinal': {'ordinal-word'}, 'date-format': {'date-format', 'day-month-year', 'numeric-date', 'this-day'},
    'provided-that': {'provided-that'}, 'cross-reference-number': {'numbered-cross-reference', 'relative-cross-reference'},
    'headings-clause': {'headings-clause'}, 'attachment-label': {'attachment-scheme', 'generic-attachment-label', 'attachment-capitals', 'attachment-lowercase'},
    'attachment-language': {'attachment-hereto', 'attachment-part-of', 'attachment-on', 'attachment-quotes'}, 'spacing': {'spacing'},
    'party-article': {'party-article'}, 'term-of-art': {'term-of-art'}, 'knowledge-standard': {'should'},
    'enumeration': {'enumeration'}, 'formatting': {'justified', 'underline', 'font', 'font-size', 'bold-definition', 'front'},
}


NON_SPAN = {'font', 'font-size', 'justified', 'underline', 'attachment-check', 'defined-unused', 'bold-definition', 'front'}


def norm(s):
    return re.sub(r'\s+', ' ', (s or '').translate(QUOTES)).strip()


def raw(s):
    return (s or '').translate(QUOTES)


def load_keys(root):
    keys = []
    for p in sorted(glob.glob(os.path.join(root, 'keys', '*.json'))):
        k = json.load(open(p, encoding='utf-8'))
        k['_path'] = os.path.join(root, k['file']) if not os.path.isabs(k['file']) else k['file']
        keys.append(k)
    return keys


def header_footer_paras(path):
    # Header and footer text, which the lint doesn't read; appended after the body so the lint's paragraph numbers still line up
    if not path.lower().endswith('.docx'):
        return []
    import docx
    from docx.oxml.ns import qn
    out, seen = [], set()
    for sec in docx.Document(path).sections:
        for part, where in ((sec.header, 'header'), (sec.footer, 'footer'), (sec.first_page_header, 'header'), (sec.first_page_footer, 'footer')):
            try:
                el = part._element
            except Exception:
                continue
            if id(el) in seen or part.is_linked_to_previous and out:
                continue
            seen.add(id(el))
            for p_el in el.iter(qn('w:p')):
                t = ''.join(x.text or '' for x in p_el.iter(qn('w:t')))
                if t.strip():
                    out.append({'idx': -1, 'text': t, 'where': where, 'fmt': {}})
    return out


def contract_text(path, collapse=True):
    paras, meta = L.read_paragraphs(path)
    if not any(p.get('where') in ('header', 'footer') for p in paras):
        paras = paras + header_footer_paras(path)  # older lint versions don't read them
    starts, pos, chunks = [], 0, []
    for p in paras:
        t = norm(p['text']) if collapse else raw(p['text'])
        starts.append(pos); chunks.append(t); pos += len(t) + 1
    return '\n'.join(chunks), starts, paras, meta


def span(text, anchor, collapse=True):
    a = norm(anchor) if collapse else raw(anchor)
    i = text.find(a)
    return (i, i + len(a)) if i >= 0 else None


def inside(s, sp):
    """Share of the finding's span that lies inside the anchor's span."""
    if not s or not sp:
        return 0.0
    return max(0, min(s[1], sp[1]) - max(s[0], sp[0])) / max(1, s[1] - s[0])


def overlaps(a, b, slack=0):
    return a and b and a[0] < b[1] + slack and b[0] < a[1] + slack


def cmd_check(root):
    bad = 0
    for k in load_keys(root):
        text = contract_text(k['_path'])[0]
        for kind, items in (('issue', k.get('issues', [])), ('trap', k.get('traps', []))):
            for it in items:
                a = it.get('anchor', '')
                if a == '[format]':
                    continue
                n = text.count(norm(a))
                if n != 1:
                    bad += 1; print(f"{k['id']}: {kind} anchor occurs {n} times: {a!r}")
    print('keys ok' if not bad else f'{bad} anchor problems')
    return 1 if bad else 0


def cmd_lint(root, out_json=None):
    rows, traps_hit, per_type = [], [], {}
    for k in load_keys(root):
        text, starts, paras, meta = contract_text(k['_path'], collapse=False)
        L.WHOSE = k.get('whose_draft') if k.get('whose_draft') in ('blake', 'other-side') else None
        _, meta2, fs, broad, inv = L.run(k['_path'], True)
        fspans = []
        for f in fs:
            for para, st, en, mt in f.get('occurrences') or [(f['para'], f.get('start', -1), f.get('end', -1), f.get('match', ''))]:
                if para < 0 or para >= len(paras) or f['check'] in NON_SPAN:
                    fspans.append((f, None)); continue
                ptxt = raw(paras[para]['text'])
                off = starts[para]
                if st >= 0:
                    fspans.append((f, (off + st, off + en))); continue
                m = raw(mt)
                i = ptxt.find(m) if m else -1
                fspans.append((f, (off + i, off + i + max(len(m), 1)) if i >= 0 else (off, off + len(ptxt))))
        for it in k.get('issues', []):
            t = it['type']
            if it.get('anchor') == '[format]':
                pat = '|'.join(v for kk, v in FORMAT_WORDS.items() if re.search(v, it.get('why', ''), re.I)) or 'font'
                direct = any(f['source'] != 'rules' and re.search(pat, f['message'] + f['check'], re.I) for f, _ in fspans)
                trig = direct
            else:
                sp = span(text, it['anchor'], collapse=False)
                near = [f for f, s in fspans if overlaps(s, sp, 25)]
                want = LINT_TYPES.get(t)
                if want:  # a mapped type counts only when a check that answers it fires near the anchor
                    direct = any(f['source'] != 'rules' and f['check'] in want for f in near)
                else:     # an unmapped type counts only when a direct finding overlaps the anchor itself
                    direct = any(f['source'] != 'rules' and overlaps(s, sp) for f, s in fspans)
                trig = any(f['source'] == 'rules' for f in near)
            rows.append({'id': k['id'], 'n': it['n'], 'type': t, 'anchor': it['anchor'], 'direct': direct, 'trigger': trig})
            d = per_type.setdefault(t, {'planted': 0, 'direct': 0, 'trigger_only': 0, 'lint_type': t in LINT_TYPES})
            d['planted'] += 1; d['direct'] += direct; d['trigger_only'] += (trig and not direct)
        for tr in k.get('traps', []):
            sp = span(text, tr['anchor'], collapse=False)
            hit = [f for f, s in fspans if f['source'] != 'rules' and s and sp and inside(s, sp) >= 0.6
                   and not f['message'].startswith('Keep')]
            if hit:
                traps_hit.append({'id': k['id'], 'anchor': tr['anchor'], 'checks': sorted({f['check'] for f in hit}),
                                  'messages': [f['message'][:120] for f in hit][:2]})
    n = len(rows); nd = sum(r['direct'] for r in rows)
    lint_rows = [r for r in rows if r['type'] in LINT_TYPES]
    print(f'Planted issues: {n}; found by a direct lint finding: {nd} ({nd / max(n, 1):.0%}); '
          f'lint-detectable types: {sum(r["direct"] for r in lint_rows)}/{len(lint_rows)}')
    print(f'Traps flagged by a direct finding (false alarms): {len(traps_hit)} of {sum(len(k.get("traps", [])) for k in load_keys(root))}')
    print('\n| type | planted | direct | trigger only | lint should catch |\n|---|---|---|---|---|')
    for t, d in sorted(per_type.items(), key=lambda x: -x[1]['planted']):
        print(f"| {t} | {d['planted']} | {d['direct']} | {d['trigger_only']} | {'yes' if d['lint_type'] else 'no'} |")
    if out_json:
        json.dump({'rows': rows, 'traps_hit': traps_hit, 'per_type': per_type}, open(out_json, 'w'), indent=1)
    return 0


def cmd_findings(root, runs, out_json=None):
    tot = found = traps = trap_bad = 0
    per_type, misses, false_alarms, per_contract = {}, [], [], []
    for k in load_keys(root):
        fpath = os.path.join(runs, k['id'], 'findings.json')
        if not os.path.exists(fpath):
            continue
        try:
            fs = json.load(open(fpath, encoding='utf-8'))
            fs = fs.get('findings', fs) if isinstance(fs, dict) else fs
        except Exception as e:
            print(f"{k['id']}: unreadable findings.json ({e})"); continue
        text = contract_text(k['_path'])[0]
        low = text.lower()
        fsp = []
        for f in fs:
            q = norm(f.get('quote', ''))
            i = low.find(q.lower()) if len(q) >= 3 else -1
            fsp.append((f, (i, i + len(q)) if i >= 0 else None, q.lower(), norm(str(f.get('fix', ''))).lower()))
        # a fix that only keeps the text; "keep only if ..., otherwise X" and "keep or delete (decision needed)" propose a change
        keep = lambda fx: re.match(r'\s*(keep|no change|leave|none|n/a)\b', fx) is not None and not re.search(r'\botherwise\b|\bor delete\b|\bdecision needed\b', fx)
        c_found = 0
        for it in k.get('issues', []):
            tot += 1
            if it.get('anchor') == '[format]':
                pat = '|'.join(v for kk, v in FORMAT_WORDS.items() if re.search(v, it.get('why', ''), re.I)) or 'font'
                ok = any(re.search(pat, json.dumps(f), re.I) for f in fs)
            else:
                located = []
                for anc in [it['anchor']] + it.get('alt_anchors', []):  # a conflict can be flagged at either end
                    a = norm(anc).lower(); sp = span(low, a)
                    located += [(f, fx) for f, s, q, fx in fsp if a in q or overlaps(s, sp)]
                # found: a finding at that spot proposes a change, or flags and keeps where keeping is the answer
                ok = any(not keep(fx) or it['type'] in ('knowledge-standard',) for f, fx in located)
                if not ok and it['type'] == 'enumeration':  # a document-wide numbering problem can be reported at any heading
                    ok = any(re.search(r'enumerat|numbering', str(f.get('type', '')), re.I) and not keep(fx) for f, s, q, fx in fsp)
            found += ok; c_found += ok
            d = per_type.setdefault(it['type'], [0, 0]); d[0] += 1; d[1] += ok
            if not ok:
                misses.append({'id': k['id'], 'n': it['n'], 'type': it['type'], 'severity': it.get('severity'), 'anchor': it['anchor']})
        for tr in k.get('traps', []):
            traps += 1
            a = norm(tr['anchor']).lower(); sp = span(low, a)
            # a false alarm is a finding aimed at the trap itself (the trap is at least half of what it quotes)
            # whose proposed wording drops or changes the trap's words
            hit = [f for f, s, q, fx in fsp if (a in q or overlaps(s, sp)) and len(a) >= 0.5 * max(len(q), 1)
                   and not keep(fx) and a not in fx and fx.strip()]
            if hit:
                trap_bad += 1
                false_alarms.append({'id': k['id'], 'anchor': tr['anchor'], 'finding': {kk: str(v)[:160] for kk, v in hit[0].items()}})
        per_contract.append({'id': k['id'], 'tier': k['tier'], 'planted': len(k.get('issues', [])), 'found': c_found,
                             'findings': len(fs), 'traps': len(k.get('traps', []))})
    print(f'Planted issues found: {found}/{tot} ({found / max(tot, 1):.0%}); traps wrongly flagged: {trap_bad}/{traps}')
    print('\n| contract | tier | found/planted | findings | traps |\n|---|---|---|---|---|')
    for c in per_contract:
        print(f"| {c['id']} | {c['tier']} | {c['found']}/{c['planted']} | {c['findings']} | {c['traps']} |")
    print('\n| type | found/planted |\n|---|---|')
    for t, (n, ok) in sorted(per_type.items(), key=lambda x: (x[1][1] / x[1][0], -x[1][0])):
        print(f'| {t} | {ok}/{n} |')
    if out_json:
        json.dump({'misses': misses, 'false_alarms': false_alarms, 'per_contract': per_contract, 'per_type': per_type},
                  open(out_json, 'w'), indent=1)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=['lint', 'findings', 'check'])
    ap.add_argument('runs', nargs='?')
    ap.add_argument('--root', default=HERE)
    ap.add_argument('--json')
    a = ap.parse_args()
    if a.cmd == 'check':
        return cmd_check(a.root)
    if a.cmd == 'lint':
        return cmd_lint(a.root, a.json)
    if not a.runs:
        ap.error('findings needs the runs directory')
    return cmd_findings(a.root, a.runs, a.json)


if __name__ == '__main__':
    sys.exit(main())
