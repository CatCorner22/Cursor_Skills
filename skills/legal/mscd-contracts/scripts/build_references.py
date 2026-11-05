#!/usr/bin/env python3
"""Rebuild the generated reference files from data/rules.jsonl and data/house-overrides.json.

Run after any change to the rule database (for example, after adding a new rider):
    python3 scripts/build_references.py

Each generated file starts from a hand-written header in scripts/ref_headers/<name>.md
(if present) and lists every relevant rule, one entry per rule, ordered by MSCD paragraph.
Rules that a house rule supersedes are marked HOUSE so the reader applies Blake's rule instead.
"""
import json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = os.path.join(ROOT, 'data', 'rules.jsonl')
OVER = os.path.join(ROOT, 'data', 'house-overrides.json')
REFS = os.path.join(ROOT, 'references')
HEADERS = os.path.join(ROOT, 'scripts', 'ref_headers')


def load():
    recs = [json.loads(l) for l in open(RULES, encoding='utf-8') if l.strip()]
    ov = json.load(open(OVER, encoding='utf-8'))
    house = {}
    for o in ov['overrides']:
        for rid in o['rule_ids']:
            house[rid] = ('partly superseded: ' if o.get('partial') else '') + o['replacement']
    for a in ov.get('additions', []):
        for rid in a['applies_with']:
            house[rid] = (house.get(rid, '') + ' ' if rid in house else '') + 'House addition: ' + a['statement']
    return recs, house


def sort_key(r):
    p = r['paras'][0] if r['paras'] else '0.0'
    a, b = (p.split('.') + ['0'])[:2]
    try:
        return (int(a), int(b), r['id'])
    except ValueError:
        return (99, 0, r['id'])


def cite(r):
    ps = r['paras']
    c = ', '.join(ps[:3]) + ('...' if len(ps) > 3 else '') if ps else 'Introduction'
    if r['pdf_pages']:
        c += f"; PDF p. {r['pdf_pages'][0]}"
    if r['status'] != 'book':
        c += f"; {r['status']}"
    return c


def entry(r, house, detail):
    s = f"- **{r['id']}** [sev {r['severity']}] {r['statement'].strip()} ({cite(r)})"
    if r['id'] in house:
        s += f"\n  - HOUSE: {house[r['id']]}"
    if detail:
        if r['trigger'].get('signal'):
            s += f"\n  - Look for: {r['trigger']['signal']}"
        if r['test']:
            s += f"\n  - Test: {r['test']}"
        if r['fix']:
            s += f"\n  - Fix: {r['fix']}"
        if r['exceptions']:
            s += "\n  - Exceptions: " + ' | '.join(r['exceptions'])
        ex = [e for e in r['examples'] if isinstance(e, dict) and e.get('verified') and (e.get('before') or e.get('after'))][:2]
        for e in ex:
            s += f"\n  - Book example: {e.get('before','') or '(none)'} → {e.get('after','') or '(see fix)'}"
    return s


SPECS = [
    # name, title, selector, detail selector
    ('verbs', 'Verb structures: shall, will, may, must and the categories of contract language',
     lambda r: r['topic'] == 'verbs', lambda r: True),
    ('active-voice', 'Active voice', lambda r: r['topic'] == 'active-voice' or 'active-voice' in r['key_items'], lambda r: True),
    ('words-to-avoid', 'Words to avoid and selected usages',
     lambda r: r['topic'] == 'usage' or 'words-to-avoid' in r['key_items'], lambda r: r['severity'] == 1),
    ('attachments', 'Attachments: schedules and exhibits',
     lambda r: r['topic'] == 'attachments' or 'attachments' in r['key_items'], lambda r: True),
    ('ambiguity-catalog', 'Ambiguity catalog', lambda r: r['topic'] == 'ambiguity' or r['kind'] == 'ambiguity-cause', lambda r: True),
    ('vagueness', 'Vagueness', lambda r: r['topic'] == 'vagueness' or 'vagueness' in r['key_items'], lambda r: True),
    ('defined-terms', 'Defined terms', lambda r: r['topic'] == 'defined-terms', lambda r: r['severity'] <= 2),
    ('efforts-material', 'Efforts standards, material and MAC', lambda r: r['topic'] == 'efforts-material', lambda r: r['severity'] <= 2),
    ('time-and-numbers', 'References to time, numbers and formulas', lambda r: r['topic'] in ('time', 'numbers'), lambda r: r['severity'] <= 2),
    ('standard-english', 'Standard English, writing and typography',
     lambda r: r['topic'] in ('standard-english', 'typography') or 'standard-english' in r['key_items'], lambda r: r['severity'] <= 2),
    ('structure', 'Structure: front and back of the contract, layout, amendments, letter agreements, internal rules',
     lambda r: r['topic'] in ('front', 'back', 'layout', 'structure', 'amendments', 'letter-agreements', 'interpretation'), lambda r: r['severity'] <= 2),
    ('practice', 'Drafting and review practice (method)', lambda r: r['topic'] == 'method' and r['status'] != 'proposal', lambda r: False),
]


def main():
    recs, house = load()
    active = [r for r in recs if r['status'] != 'proposal']
    sizes = {}
    for name, title, sel, det in SPECS:
        rows = sorted([r for r in active if sel(r)], key=sort_key)
        hdr_path = os.path.join(HEADERS, name + '.md')
        head = open(hdr_path, encoding='utf-8').read().rstrip() + '\n' if os.path.exists(hdr_path) else f'# {title}\n'
        head += ('\n> **Book examples are in MSCD5\'s style, not house style.** They may use lowercase *schedule*, *1 January 2024*, '
                 'spelled-out numbers, 1.1 numbering, *the* before party names, or a passive that MSCD accepts. '
                 'Restate any example in house style (`house-style.md`) before you put it in a contract or a comment. '
                 'For the other side\'s drafts, the house rule is to flag everything, whatever a rule\'s "let-pass" or "style-only" label says.\n')
        out = [head,
               f"\n## Rules ({len(rows)}, generated from `data/rules.jsonl`)\n",
               "Format: id, severity (1 = ambiguity or meaning-changing; 2 = vagueness or dispute risk; 3 = style), the rule, and its MSCD paragraphs and PDF page. "
               "`HOUSE` marks a rule that Blake's house style changes: apply the house rule. For a rule's full record (test, fix, exceptions, verified book examples), run "
               "`python3 scripts/rules_query.py --id <id>`.\n"]
        if name == 'words-to-avoid':
            verd = [r for r in rows if r['kind'] == 'usage-verdict']
            rows = [r for r in rows if r['kind'] != 'usage-verdict']
            out.append(f"\n### Usage verdicts ({len(verd)})\n")
            out.append('| Usage | Rule | Fix | Sev | MSCD | id |')
            out.append('|---|---|---|---|---|---|')
            for r in sorted(verd, key=lambda r: r['section'].split(' > ')[-1].lower()):
                cell = lambda t: (t or '').replace('|', '/').replace('\n', ' ').strip()
                h = ' HOUSE: ' + house[r['id']] if r['id'] in house else ''
                out.append(f"| {cell(r['section'].split(' > ')[-1])} | {cell(r['statement'])}{cell(h)} | {cell(r['fix'])} | {r['severity']} | {cell(cite(r))} | {r['id']} |")
            out.append(f"\n### Other usage rules and exceptions ({len(rows)})\n")
        bysec = collections.OrderedDict()
        for r in rows:
            sec = r['section'].split(' > ')[0] if r['section'] else 'General'
            bysec.setdefault(f"Chapter {r['chapter']}: {sec}" if r['chapter'] else sec, []).append(r)
        for sec, rs in bysec.items():
            out.append(f"\n### {sec}\n")
            out += [entry(r, house, det(r)) for r in rs]
        text = '\n'.join(out) + '\n'
        heads = [l[4:] for l in text.splitlines() if l.startswith('### ')]
        if len(text.splitlines()) > 300 and heads:
            toc = '\n## Contents of the rules list\n\n' + '\n'.join(f'- {h}' for h in heads) + '\n'
            text = text.replace('\n## Rules (', toc + '\n## Rules (', 1)
        open(os.path.join(REFS, name + '.md'), 'w', encoding='utf-8').write(text)
        sizes[name] = (len(rows), len(text))
    for k, (n, c) in sizes.items():
        print(f'{k:20} rules {n:4}  chars {c:7}')


if __name__ == '__main__':
    main()
