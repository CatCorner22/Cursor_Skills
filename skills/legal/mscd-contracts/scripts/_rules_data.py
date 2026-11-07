"""Read the rule database (data/rules.jsonl) and Blake's house overrides (data/house-overrides.json).

Every script that reads the rules goes through these functions, so a bad line or a missing file is reported
the same way everywhere (an InputError naming the file and line) instead of silently changing the results.
"""
import json
import os
import re

from _cli import InputError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_PATH = os.path.join(ROOT, 'data', 'rules.jsonl')
OVERRIDES_PATH = os.path.join(ROOT, 'data', 'house-overrides.json')
VARIANTS_PATH = os.path.join(ROOT, 'data', 'phrase-variants.json')
TERMS_OF_ART_PATH = os.path.join(ROOT, 'data', 'terms-of-art.json')

_cache = {}


def load_records(path=RULES_PATH):
    """The rule records, 1 per non-blank line. Raises InputError naming the line of any record that isn't valid JSON."""
    if path in _cache:
        return _cache[path]
    recs = []
    try:
        with open(path, encoding='utf-8') as fh:
            for n, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except ValueError as e:
                    raise InputError(f'{path}, line {n}, is not valid JSON ({e}); fix that line') from e
                if not isinstance(rec, dict) or 'id' not in rec:
                    raise InputError(f'{path}, line {n}, is not a rule record (an object with an "id")')
                problem = record_problem(rec)
                if problem:
                    raise InputError(f'{path}, line {n} ({rec["id"]}): {problem}')
                recs.append(rec)
    except OSError as e:
        raise InputError(f'cannot read the rule database {path}: {e.strerror or e}') from e
    _cache[path] = recs
    return recs


# the fields the 3 consumers (mscd_lint.py, rules_query.py, build_references.py) read, by type
_STR_FIELDS = ('status', 'kind', 'statement', 'section', 'notes', 'test', 'fix', 'topic', 'counterparty_review')
_LIST_FIELDS = ('paras', 'pdf_pages', 'cross_refs', 'exceptions', 'examples', 'key_items')
_LIST_ITEM_TYPES = {'paras': str, 'cross_refs': str, 'exceptions': str, 'key_items': str, 'pdf_pages': int, 'examples': (dict, str)}


def record_problem(rec):
    """What is wrong with a rule record's shape, or None. A missing optional field is allowed (the readers default it);
    a field of the wrong type is not, because every script reads these fields without checking them again."""
    if not isinstance(rec.get('id'), str) or not rec['id']:
        return 'id must be a non-empty string'
    for k in ('status', 'kind', 'statement'):
        if not isinstance(rec.get(k), str):
            return f'{k} must be a string'
    for k in _STR_FIELDS:
        if rec.get(k) is not None and not isinstance(rec[k], str):
            return f'{k} must be a string'
    if type(rec.get('severity')) is not int or rec['severity'] not in (1, 2, 3):
        return 'severity must be 1, 2 or 3'
    if rec.get('chapter') is not None and type(rec['chapter']) is not int:
        return 'chapter must be a whole number or null'
    for k in _LIST_FIELDS:
        v = rec.get(k)
        if v is None:
            continue
        if not isinstance(v, list):
            return f'{k} must be a list'
        if not all(isinstance(x, _LIST_ITEM_TYPES[k]) and type(x) is not bool for x in v):
            return f'{k} must be a list of {_LIST_ITEM_TYPES[k].__name__ if not isinstance(_LIST_ITEM_TYPES[k], tuple) else "objects or strings"}'
    if rec.get('trigger') is not None and not isinstance(rec['trigger'], dict):
        return 'trigger must be an object'
    trig = rec.get('trigger') or {}
    hint = trig.get('regex_hint')
    if hint is not None and not isinstance(hint, str):
        return 'trigger.regex_hint must be a string'
    words = trig.get('words')
    if words is not None and (not isinstance(words, list) or not all(isinstance(w, str) for w in words)):
        return 'trigger.words must be a list of strings'
    return None


def superseded_ids(ov):
    """Rule ids that a whole-rule house override replaces (a partial override keeps the rule and adds a note)."""
    return {rid for o in ov['overrides'] if not o.get('partial') for rid in o['rule_ids']}


def load_overrides(path=OVERRIDES_PATH):
    """The house overrides file: {"overrides": [...], "additions": [...], ...}."""
    key = ('overrides', path)
    if key in _cache:
        return _cache[key]
    try:
        with open(path, encoding='utf-8') as fh:
            ov = json.load(fh)
    except OSError as e:
        raise InputError(f'cannot read the house overrides {path}: {e.strerror or e}') from e
    except ValueError as e:
        raise InputError(f'{path} is not valid JSON ({e})') from e
    if not isinstance(ov, dict) or not isinstance(ov.get('overrides', []), list):
        raise InputError(f'{path} is not a house-overrides file (an object with an "overrides" list)')
    for i, o in enumerate(ov['overrides']):
        if not isinstance(o, dict) or not isinstance(o.get('rule_ids'), list) or not all(isinstance(r, str) for r in o['rule_ids']) or not isinstance(o.get('replacement'), str):
            raise InputError(f'{path}: override {i} needs a "rule_ids" list of strings and a "replacement" string')
    for rid, sup in ((ov.get('lint') or {}).get('suppress') or {}).items():
        try:
            re.compile(sup)
        except re.error as e:
            raise InputError(f'{path}: lint.suppress[{rid}] does not compile ({e})') from e
    _cache[key] = ov
    return ov


def house_notes(ov, superseded='SUPERSEDED. ', partial='PARTLY SUPERSEDED. ', addition='ADDITION. '):
    """Map each rule id to the house note a reader should apply instead of (or with) the MSCD rule.
    The labels differ by script (a terminal lookup versus a generated reference file), so the caller passes them."""
    house = {}
    for o in ov.get('overrides', []):
        for rid in o.get('rule_ids', []):
            house[rid] = (partial if o.get('partial') else superseded) + o['replacement']
    for a in ov.get('additions', []):
        for rid in a.get('applies_with', []):
            house[rid] = (house[rid] + ' ' if rid in house else '') + addition + a['statement']
    return house
