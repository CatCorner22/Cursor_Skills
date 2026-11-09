#!/usr/bin/env python3
"""Rebuild the generated reference files from data/rules.jsonl and data/house-overrides.json.

Run after any change to the rule database (for example, after adding a new rider):
    python3 scripts/build_references.py

Each generated file starts from a hand-written header in scripts/ref_headers/<name>.md
(required) and lists every relevant rule, one entry per rule, ordered by MSCD paragraph.
Rules that a house rule supersedes are marked HOUSE so the reader applies Blake's rule instead.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli import ArgParser, InputError, OK, run_main, setup_output, write_text  # noqa: E402
from _rules_data import ROOT, house_notes, load_overrides, load_records  # noqa: E402

REFS = os.path.join(ROOT, 'references')
HEADERS = os.path.join(ROOT, 'scripts', 'ref_headers')


def load():
    ov = load_overrides()
    return load_records(), house_notes(ov, superseded='', partial='partly superseded: ', addition='House addition: '), ov.get('counterparty_review_default', 'flag')


def cell(t):
    """Text safe for 1 Markdown table cell."""
    return (t or '').replace('|', '/').replace('\n', ' ').strip()


def sort_key(r):
    p = r['paras'][0] if r.get('paras') else '0.0'
    a, b = [*p.split('.'), '0'][:2]
    try:
        return (int(a), int(b), r['id'])
    except ValueError:
        return (99, 0, r['id'])


def cite(r):
    ps = r.get('paras') or []
    c = ', '.join(ps[:3]) + ('...' if len(ps) > 3 else '') if ps else 'Introduction'
    if r.get('pdf_pages'):
        c += f"; PDF p. {r['pdf_pages'][0]}"
    if r['status'] != 'book':
        c += f"; {r['status']}"
    return c


def usage_label(r):
    """The Usage cell of a verdict row: the word. The book's section line reads Selected Usages > WORD > Sub-heading for some chapter-13
    entries (INDEMNIFY > Function) and Topic > Sub-heading outside chapter 13 (Reasonable Efforts > Components), so the sub-heading
    alone would hide the word and sort the row under F or C. The word comes first (the entry heading, else the 1st trigger word), and
    the sub-heading follows in parentheses: INDEMNIFY (function), SUFFER (intransitive), COMMERCIALLY REASONABLE EFFORTS (components)."""
    parts = [x.strip() for x in (r.get('section') or '').split(' > ') if x.strip()]
    if not parts:
        return ''
    last = parts[-1]
    if last == last.upper() or len(parts) == 1:
        return last
    words = [w for w in (r.get('trigger') or {}).get('words') or [] if re.fullmatch(r"[A-Za-z][\w'/ -]*", w)]
    word = parts[1] if len(parts) >= 3 else words[0].upper() if words else parts[0]
    return f"{word} ({re.sub(r'\s*\(\d+\.\d+\)$', '', last).lower()})"


def entry(r, house, detail):
    s = f"- **{r['id']}** [sev {r['severity']}] {r['statement'].strip()} ({cite(r)})"
    if r['id'] in house:
        s += f"\n  - HOUSE: {house[r['id']]}"
    if detail:  # a field a record lacks reads as empty (record_problem allows a missing optional field)
        if (r.get('trigger') or {}).get('signal'):
            s += f"\n  - Look for: {r['trigger']['signal']}"
        if r.get('test'):
            s += f"\n  - Test: {r['test']}"
        if r.get('fix'):
            s += f"\n  - Fix: {r['fix']}"
        if r.get('exceptions'):
            s += "\n  - Exceptions: " + ' | '.join(r['exceptions'])
        ex = [e for e in r.get('examples') or [] if isinstance(e, dict) and e.get('verified') and (e.get('before') or e.get('after'))][:2]
        for e in ex:
            s += f"\n  - Book example: {e.get('before','') or '(none)'} → {e.get('after','') or '(see fix)'}"
    return s


SPECS = [
    # name, title, selector, detail selector
    ('verbs', 'Verb structures: shall, will, may, must and the categories of contract language',
     lambda r: r.get('topic') == 'verbs', lambda r: True),
    ('active-voice', 'Active voice', lambda r: r.get('topic') == 'active-voice' or 'active-voice' in (r.get('key_items') or []), lambda r: True),
    ('words-to-avoid', 'Words to avoid and selected usages',
     lambda r: r.get('topic') == 'usage' or 'words-to-avoid' in (r.get('key_items') or []), lambda r: r['severity'] == 1),
    ('attachments', 'Attachments: schedules and exhibits',
     lambda r: r.get('topic') == 'attachments' or 'attachments' in (r.get('key_items') or []), lambda r: True),
    ('ambiguity-catalog', 'Ambiguity catalog', lambda r: r.get('topic') == 'ambiguity' or r['kind'] == 'ambiguity-cause', lambda r: True),
    ('vagueness', 'Vagueness', lambda r: r.get('topic') == 'vagueness' or 'vagueness' in (r.get('key_items') or []), lambda r: True),
    ('defined-terms', 'Defined terms', lambda r: r.get('topic') == 'defined-terms', lambda r: r['severity'] <= 2),
    ('efforts-material', 'Efforts standards, material and MAC', lambda r: r.get('topic') == 'efforts-material', lambda r: r['severity'] <= 2),
    ('time-and-numbers', 'References to time, numbers and formulas', lambda r: r.get('topic') in ('time', 'numbers'), lambda r: r['severity'] <= 2),
    ('standard-english', 'Standard English, writing and typography',
     lambda r: r.get('topic') in ('standard-english', 'typography') or 'standard-english' in (r.get('key_items') or []), lambda r: r['severity'] <= 2),
    ('structure', 'Structure: front and back of the contract, layout, amendments, letter agreements, internal rules',
     lambda r: r.get('topic') in ('front', 'back', 'layout', 'structure', 'amendments', 'letter-agreements', 'interpretation'), lambda r: r['severity'] <= 2),
    ('practice', 'Drafting and review practice (method)', lambda r: r.get('topic') == 'method' and r['status'] != 'proposal', lambda r: False),
]


def main():
    setup_output()
    ArgParser(description='Rebuild references/*.md from data/rules.jsonl, data/house-overrides.json and '
              'scripts/ref_headers/*.md. Takes no arguments; run it after changing any of those files.').parse_args()
    recs, house, counterparty = load()
    flag_note = ("For the other side's drafts, the house rule is to flag everything, whatever a rule's \"let-pass\" or \"style-only\" label says.\n"
                 if counterparty == 'flag' else '\n')
    active = [r for r in recs if r['status'] != 'proposal']
    sizes = {}
    for name, title, sel, det in SPECS:
        all_rows = sorted([r for r in active if sel(r)], key=sort_key)
        hdr_path = os.path.join(HEADERS, name + '.md')
        if not os.path.exists(hdr_path):  # the skill reads each file's hand-written header first: a rebuild must never drop it
            raise InputError(f'missing {hdr_path}: every generated reference starts from its hand-written header; restore it before rebuilding')
        with open(hdr_path, encoding='utf-8') as fh:
            head = fh.read().rstrip() + '\n'
        head += ('\n> **Book examples are in MSCD5\'s style, not house style.** They may use lowercase *schedule*, *1 January 2024*, '
                 'spelled-out numbers, 1.1 numbering, *the* before party names, or a passive that MSCD accepts. '
                 'Restate any example in house style (`house-style.md`) before you put it in a contract or a comment. ' + flag_note)
        out = [head,
               f"\n## Rules ({len(all_rows)}, generated from `data/rules.jsonl`)\n",
               ("Format: id, severity (1 = ambiguity or meaning-changing; 2 = vagueness or dispute risk; 3 = style), the rule, and its MSCD paragraphs and PDF page. "
               "`HOUSE` marks a rule that Blake's house style changes: apply the house rule. For a rule's full record (test, fix, exceptions, verified book examples), run "
               "`python3 scripts/rules_query.py --id <id>`.\n")]
        rows = all_rows
        if name == 'words-to-avoid':
            verd = [r for r in all_rows if r['kind'] == 'usage-verdict']
            rows = [r for r in all_rows if r['kind'] != 'usage-verdict']
            out.append(f"\n### Usage verdicts ({len(verd)})\n")
            out.append('| Usage | Rule | Fix | Sev | MSCD | id |')
            out.append('|---|---|---|---|---|---|')
            for r in sorted(verd, key=lambda r: usage_label(r).lower()):
                h = ' HOUSE: ' + house[r['id']] if r['id'] in house else ''
                out.append(f"| {cell(usage_label(r))} | {cell(r['statement'])}{cell(h)} | {cell(r['fix'])} | {r['severity']} | {cell(cite(r))} | {r['id']} |")
            out.append(f"\n### Other usage rules and exceptions ({len(rows)})\n")
        bysec = collections.OrderedDict()
        for r in rows:
            sec = (r.get('section') or '').split(' > ')[0] if (r.get('section') or '') else 'General'
            bysec.setdefault(f"Chapter {r.get('chapter')}: {sec}" if r.get('chapter') else sec, []).append(r)
        for sec, rs in bysec.items():
            out.append(f"\n### {sec}\n")
            out += [entry(r, house, det(r)) for r in rs]
        text = '\n'.join(out) + '\n'
        heads = [line[4:] for line in text.splitlines() if line.startswith('### ')]
        if len(text.splitlines()) > 300 and heads:
            toc = '\n## Contents of the rules list\n\n' + '\n'.join(f'- {h}' for h in heads) + '\n'
            text = text.replace('\n## Rules (', toc + '\n## Rules (', 1)
        dest = os.path.join(REFS, name + '.md')
        write_text(dest, text)  # atomic: a crash mid-write never leaves a truncated reference for the skill to read
        sizes[name] = (len(all_rows), len(text))
    for k, (n, c) in sizes.items():
        print(f'{k:20} rules {n:4}  chars {c:7}')
    return OK


if __name__ == '__main__':
    sys.exit(run_main('build_references.py', main))
