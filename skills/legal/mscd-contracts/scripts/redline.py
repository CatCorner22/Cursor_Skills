#!/usr/bin/env python3
"""Make Word tracked changes and comments from a list of edits, and the matching clean copy.

Works on an unpacked .docx whose runs have been merged (the docx skill's merge_runs.py), so each
run holds 1 w:t. Paragraph numbers are the lint's: every w:p in the body, in document order,
counted from 0 (mscd_lint.py --json gives them).

  python3 redline.py apply <unpacked_dir> edits.json            tracked changes and comments
  python3 redline.py apply <unpacked_dir> edits.json --clean    the same edits with no markup, no comments
  python3 redline.py --self-test

edits.json is a list. Each item is 1 of:
  {"para": 12, "old": "shall be governed by", "new": "governs", "comment": ["Why: ...", "MSCD 3.98."]}
  {"para": 12, "old": "", "new": " no later than 10 days after", "before": "pay", "comment": [...]}   (an insertion)
  {"para": 12, "old": "promptly ", "new": ""}                                                        (a deletion)
  {"para": 3, "anchor": "the Contractor", "comment": ["House rule 11: ..."]}                         (a comment, no change)
"before" and "after" are optional context that make "old" unique in the paragraph; "occurrence"
(1, 2, ...) picks 1 match when the text repeats. The comment's lines become line breaks in 1 comment.
The author is "Blake's AI Agent" unless --author says otherwise.
"""
import argparse
import copy
import glob
import json
import os
import sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"


def q(tag):
    return "{%s}%s" % (W, tag)


def docx_scripts():
    """The docx skill's scripts folder (for comment.py); DOCX_SKILL_SCRIPTS overrides the search."""
    cands = [os.environ.get('DOCX_SKILL_SCRIPTS', ''), '/mnt/skills/public/docx/scripts']
    cands += sorted(glob.glob(os.path.expanduser('~/.claude/skills/**/docx/scripts'), recursive=True))
    for c in cands:
        if c and os.path.exists(os.path.join(c, 'comment.py')):
            return c
    return None


class RedlineError(Exception):
    pass


class Doc:
    def __init__(self, unpacked, author="Blake's AI Agent", clean=False):
        from lxml import etree
        self.etree = etree
        self.dir = unpacked
        self.path = os.path.join(unpacked, 'word', 'document.xml')
        self.tree = etree.parse(self.path)
        self.body = self.tree.getroot().find(q('body'))
        self.paras = list(self.body.iter(q('p')))
        self.author, self.clean = author, clean
        self.date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        ids = [int(x) for x in self.tree.getroot().xpath('//w:ins/@w:id | //w:del/@w:id', namespaces={'w': W}) if str(x).isdigit()]
        self.next_id = max(ids + [900])
        self._add_comment = None

    def _id(self):
        self.next_id += 1
        return str(self.next_id)

    def _track(self, el):
        el.set(q('id'), self._id()); el.set(q('author'), self.author); el.set(q('date'), self.date)
        return el

    def runs(self, p):
        """The paragraph's own text runs (direct children), each with exactly 1 w:t."""
        out = []
        for r in p:
            if r.tag != q('r') or r.find(q('t')) is None:
                continue
            if len(r.findall(q('t'))) != 1 or any(c.tag not in (q('rPr'), q('t')) for c in r):
                raise RedlineError('a run mixes text with tabs or breaks; run the docx skill\'s merge_runs.py first, or make this edit by hand')
            out.append(r)
        return out

    def text(self, p):
        return ''.join(r.find(q('t')).text or '' for r in self.runs(p))

    def _split(self, p, pos):
        off = 0
        for r in self.runs(p):
            t = r.find(q('t')); s = t.text or ''
            if off < pos < off + len(s):
                r2 = copy.deepcopy(r)
                t.text, r2.find(q('t')).text = s[:pos - off], s[pos - off:]
                for tt in (t, r2.find(q('t'))):
                    tt.set('{%s}space' % XML_NS, 'preserve')
                r.addnext(r2)
                return
            off += len(s)

    def _span(self, p, start, end):
        self._split(p, start); self._split(p, end)
        off, sel = 0, []
        for r in self.runs(p):
            n = len(r.find(q('t')).text or '')
            if start <= off and off + n <= end and n:
                sel.append(r)
            off += n
        return sel

    def _find(self, pi, old, before='', after='', occurrence=None):
        if not 0 <= pi < len(self.paras):
            raise RedlineError(f'paragraph {pi} does not exist (the document has {len(self.paras)})')
        txt = self.text(self.paras[pi]); needle = before + old + after
        hits = [i for i in range(len(txt)) if txt.startswith(needle, i)] if needle else []
        if not hits:
            raise RedlineError(f'para {pi}: {needle!r} not found in {txt[:100]!r}')
        if occurrence is None and len(hits) > 1:
            raise RedlineError(f'para {pi}: {needle!r} occurs {len(hits)} times; add before/after context or an occurrence number')
        s = hits[(occurrence or 1) - 1] + len(before)
        return s, s + len(old)

    def _run(self, text, rpr):
        r = self.etree.Element(q('r'))
        if rpr is not None:
            r.append(copy.deepcopy(rpr))
        t = self.etree.SubElement(r, q('t')); t.text = text; t.set('{%s}space' % XML_NS, 'preserve')
        return r

    def comment(self, pi, first, last, lines):
        if self.clean or not lines:
            return None
        if self._add_comment is None:
            sp = docx_scripts()
            if not sp:
                raise RedlineError("can't find the docx skill's comment.py; set DOCX_SKILL_SCRIPTS to its scripts folder")
            sys.path.insert(0, sp)
            from comment import add_comment  # the docx skill's helper writes comments.xml and its companion parts
            self._add_comment = add_comment
        body = '</w:t><w:br/><w:t xml:space="preserve">'.join(escape(x) for x in lines)  # line breaks inside 1 comment paragraph
        cid = self._add_comment(self.dir, body, author=self.author, initials='BAA', raw=True)[0]
        first.addprevious(self.etree.Element(q('commentRangeStart'), {q('id'): str(cid)}))
        end = self.etree.Element(q('commentRangeEnd'), {q('id'): str(cid)}); last.addnext(end)
        ref = self.etree.Element(q('r')); rpr = self.etree.SubElement(ref, q('rPr'))
        self.etree.SubElement(rpr, q('rStyle'), {q('val'): 'CommentReference'})
        self.etree.SubElement(ref, q('commentReference'), {q('id'): str(cid)}); end.addnext(ref)
        return cid

    def anchor(self, pi, text, lines, before='', after='', occurrence=None):
        p = self.paras[pi]
        s, e = self._find(pi, text, before, after, occurrence)
        runs = self._span(p, s, e)
        return self.comment(pi, runs[0], runs[-1], lines)

    def edit(self, pi, old, new, before='', after='', occurrence=None, lines=None):
        p = self.paras[pi]
        s, e = self._find(pi, old, before, after, occurrence)
        if old:
            olds = self._span(p, s, e)
            rpr = olds[0].find(q('rPr'))
            if self.clean:
                anchor_el = olds[0]
                if new:
                    anchor_el.addprevious(self._run(new, rpr))
                for r in olds:
                    p.remove(r)
                return None
            d = self._track(self.etree.Element(q('del'))); olds[0].addprevious(d)
            for r in olds:
                d.append(r); t = r.find(q('t')); t.tag = q('delText'); t.set('{%s}space' % XML_NS, 'preserve')
            first = last = d
            if new:
                ins = self._track(self.etree.Element(q('ins'))); ins.append(self._run(new, rpr)); d.addnext(ins); last = ins
        else:
            if not new:
                raise RedlineError(f'para {pi}: an edit needs old or new text')
            self._split(p, s)
            off, nxt, prev = 0, None, None
            for r in self.runs(p):
                n = len(r.find(q('t')).text or '')
                if off == s and nxt is None:
                    nxt = r
                if off + n <= s:
                    prev = r
                off += n
            base = prev if prev is not None else nxt
            rpr = base.find(q('rPr')) if base is not None else None
            el = self._run(new, rpr) if self.clean else self._track(self.etree.Element(q('ins')))
            if not self.clean:
                el.append(self._run(new, rpr))
            if nxt is not None:
                nxt.addprevious(el)
            elif prev is not None:
                prev.addnext(el)
            else:
                p.append(el)
            if self.clean:
                return None
            first = last = el
        return self.comment(pi, first, last, lines)

    def save(self):
        self.tree.write(self.path, xml_declaration=True, encoding='UTF-8', standalone=True)


def apply(unpacked, edits, author="Blake's AI Agent", clean=False):
    """Apply edits; return the number applied. Edits are checked against the original text first, so
    one bad item stops the run before anything changes."""
    doc = Doc(unpacked, author, clean)
    for i, e in enumerate(edits):  # validate every item before changing anything
        if 'para' not in e:
            raise RedlineError(f'item {i}: no para')
        if 'anchor' in e:
            doc._find(e['para'], e['anchor'], e.get('before', ''), e.get('after', ''), e.get('occurrence'))
        else:
            doc._find(e['para'], e.get('old', ''), e.get('before', ''), e.get('after', ''), e.get('occurrence'))
    # apply from the end of each paragraph backward, so earlier offsets stay valid
    order = sorted(range(len(edits)), key=lambda i: (edits[i]['para'], -doc._find(edits[i]['para'], edits[i].get('anchor', edits[i].get('old', '')),
                                                                                     edits[i].get('before', ''), edits[i].get('after', ''), edits[i].get('occurrence'))[0]))
    for i in order:
        e = edits[i]
        if 'anchor' in e:
            doc.anchor(e['para'], e['anchor'], e.get('comment'), e.get('before', ''), e.get('after', ''), e.get('occurrence'))
        else:
            doc.edit(e['para'], e.get('old', ''), e.get('new', ''), e.get('before', ''), e.get('after', ''), e.get('occurrence'), e.get('comment'))
    doc.save()
    return len(edits)


def self_test():
    import shutil
    import tempfile
    import zipfile
    try:
        import docx
    except ImportError:
        print('self-test skipped: python-docx is not installed'); return 0
    fails = 0
    tmp = tempfile.mkdtemp()
    try:
        d = docx.Document()
        d.add_paragraph('MASTER AGREEMENT')
        d.add_paragraph('This agreement shall be governed by Ohio law.  Acme shall pay promptly the Price.')
        src = os.path.join(tmp, 'in.docx'); d.save(src)
        edits = [{'para': 1, 'old': 'shall be governed by Ohio law', 'new': 'is governed by Ohio law', 'comment': ['Why: no duty (MSCD 3.98).', 'Policy takes the present tense.']},
                 {'para': 1, 'old': 'promptly ', 'new': ''},
                 {'para': 1, 'old': '', 'new': ' no later than 10 days after the Closing', 'before': 'the Price'},
                 {'para': 0, 'anchor': 'MASTER', 'comment': ['Title check.']}]
        outs = {}
        for mode in ('redline', 'clean'):
            u = os.path.join(tmp, mode)
            with zipfile.ZipFile(src) as z:
                z.extractall(u)
            if mode == 'redline' and not docx_scripts():
                edits_mode = [e for e in edits if 'comment' not in e and 'anchor' not in e]
            else:
                edits_mode = edits
            apply(u, edits_mode, clean=(mode == 'clean'))
            out = os.path.join(tmp, mode + '.docx')
            with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
                for root_, _, files in os.walk(u):
                    for f in files:
                        full = os.path.join(root_, f); z.write(full, os.path.relpath(full, u))
            outs[mode] = out
        from lxml import etree
        def accepted(path):
            with zipfile.ZipFile(path) as z:
                x = etree.fromstring(z.read('word/document.xml'))
            for dl in x.iter(q('del')):
                dl.getparent().remove(dl)
            return [''.join(t.text or '' for t in p.iter(q('t'))) for p in x.iter(q('p'))]
        want = 'This agreement is governed by Ohio law.  Acme shall pay the Price no later than 10 days after the Closing.'
        if accepted(outs['redline'])[1] != want:
            fails += 1; print('FAIL: redline text after accepting changes:', accepted(outs['redline'])[1])
        if accepted(outs['clean'])[1] != want:
            fails += 1; print('FAIL: clean copy text:', accepted(outs['clean'])[1])
        with zipfile.ZipFile(outs['redline']) as z:
            x = z.read('word/document.xml').decode()
            has_comments = 'word/comments.xml' in z.namelist()
        if x.count('<w:ins ') != 2 or x.count('<w:del ') != 2 or "Blake's AI Agent" not in x:
            fails += 1; print('FAIL: expected 2 insertions and 2 deletions by Blake\'s AI Agent')
        if docx_scripts() and not has_comments:
            fails += 1; print('FAIL: no comments part in the redline')
        try:
            apply(os.path.join(tmp, 'clean'), [{'para': 1, 'old': 'not in the text', 'new': 'x'}])
            fails += 1; print('FAIL: a missing anchor was accepted')
        except RedlineError:
            pass
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'self-test: {"passed" if not fails else f"{fails} failed"}' + ('' if docx_scripts() else ' (comments not tested: docx skill not found)'))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', nargs='?', choices=['apply'])
    ap.add_argument('unpacked', nargs='?'); ap.add_argument('edits', nargs='?')
    ap.add_argument('--clean', action='store_true', help='apply the edits with no markup and no comments (the clean copy)')
    ap.add_argument('--author', default="Blake's AI Agent")
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.cmd != 'apply' or not a.unpacked or not a.edits:
        ap.print_help(); return 5
    try:
        n = apply(a.unpacked, json.load(open(a.edits, encoding='utf-8')), a.author, a.clean)
    except (RedlineError, OSError, ValueError) as e:
        print(f'error: {e}', file=sys.stderr); return 2
    print(f'applied {n} edits' + (' (clean copy)' if a.clean else ' as tracked changes and comments'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
