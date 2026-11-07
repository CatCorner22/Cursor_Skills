#!/usr/bin/env python3
"""Mechanical first pass for the mscd-contracts skill.

Reads a contract (.docx, .txt or .md), runs Blake's house-style checks, the trigger patterns of
every rule in data/rules.jsonl, and (with --inventory) a defined-term inventory. It reports
CANDIDATES for judgment, never conclusions: Claude confirms or rejects each one in context.

Usage:
  python3 scripts/mscd_lint.py contract.docx                 # markdown report to stdout
  python3 scripts/mscd_lint.py contract.docx --json out.json # machine-readable findings too
  python3 scripts/mscd_lint.py contract.docx --inventory     # add the defined-term inventory
  python3 scripts/mscd_lint.py --self-test                   # run the built-in checks
Exit codes (scripts/_cli.py): 0 ok (findings are a report, not an error); 1 a self-test failure; 2 unreadable input,
an output that can't be written, or a damaged data file; 3 an internal error (a bug: the traceback shows where);
5 bad usage.
"""
import argparse, codecs, collections, datetime, os, re, sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # the shared helpers sit beside this script
from _cli import ArgParser, InputError, read_json, run_main, setup_output, write_json  # noqa: E402
from _rules_data import TERMS_OF_ART_PATH, VARIANTS_PATH, load_overrides, load_records, superseded_ids  # noqa: E402


def _docx_xml_errors():
    """python-docx's InvalidXmlError classes (the module moved between versions), or () without python-docx."""
    classes = []
    for mod in ('docx.exceptions', 'docx.oxml.exceptions'):
        try:
            classes.append(__import__(mod, fromlist=['InvalidXmlError']).InvalidXmlError)
        except (ImportError, AttributeError):
            pass
    return tuple(classes)


DOCX_XML_ERRORS = _docx_xml_errors()


def _xml_parser():
    """python-docx's own parser setting for the parts this script parses itself (theme, comments, headers, footnotes):
    a part from an untrusted file can't pull in an entity or a network resource. None without lxml."""
    try:
        from lxml import etree
        return etree.XMLParser(resolve_entities=False, no_network=True)
    except ImportError:
        return None


_XML = _xml_parser()
# invisible format characters a paste from a PDF or a web page carries: a soft hyphen, zero-width spaces and joiners, a word
# joiner, a stray byte-order mark. Word shows none of them, and each one splits a word in 2 for every regex here
INVISIBLE = re.compile('[\u00ad\u200b\u200c\u200d\u2060\ufeff]')

# ---------------------------------------------------------------- reading the document

def _fmt_num(n, fmt):
    if fmt in ('upperLetter', 'lowerLetter'):
        s = ''
        while n > 0:
            n, r = divmod(n - 1, 26)
            s = chr(65 + r) + s
        return s if fmt == 'upperLetter' else s.lower()
    if fmt in ('upperRoman', 'lowerRoman') and 0 < n < 4000:  # beyond MMMCMXCIX Word falls back to digits; so do we
        vals = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
        s = ''
        for v, sym in vals:
            while n >= v:
                s += sym
                n -= v
        return s if fmt == 'upperRoman' else s.lower()
    return str(n)


def _int(v, default=0):
    """An integer from an XML attribute; the default when the value is missing or malformed (a damaged file mustn't stop the lint)."""
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _style_chain(st, limit=20):
    """A style and its base styles, nearest first. Stops at a style seen before (a style based on itself, or a loop) or
    after limit styles, so a damaged styles.xml can't hang the lint."""
    seen = set()
    while st is not None and len(seen) < limit:
        key = getattr(st, 'style_id', None) or id(st)
        if key in seen:
            return
        seen.add(key)
        yield st
        try:
            st = st.base_style
        except (AttributeError, KeyError, ValueError):
            return


def numbering_labeler(doc):
    """Return a function that gives the label Word displays for a numbered paragraph (A., 1., (a)), or None.
    Counters run per abstract numbering definition, as Word continues a list across paragraphs that share it."""
    from docx.oxml.ns import qn
    try:
        root = doc.part.numbering_part.element
    except (KeyError, NotImplementedError, AttributeError):
        return lambda p: (None, None)
    absmap = {a.get(qn('w:abstractNumId')): a for a in root.findall(qn('w:abstractNum'))}
    by_style = {}
    for a in absmap.values():
        sl = a.find(qn('w:styleLink'))
        if sl is not None:
            by_style[sl.get(qn('w:val'))] = a
    for k, a in list(absmap.items()):  # a list tied to a list style keeps its levels in the style's own definition
        nl = a.find(qn('w:numStyleLink'))
        if nl is not None and not a.findall(qn('w:lvl')) and nl.get(qn('w:val')) in by_style:
            absmap[k] = by_style[nl.get(qn('w:val'))]
    nums = {}
    for n in root.findall(qn('w:num')):
        aid = n.find(qn('w:abstractNumId'))
        ov = {}
        for o in n.findall(qn('w:lvlOverride')):
            so = o.find(qn('w:startOverride'))
            if so is not None:
                ov[o.get(qn('w:ilvl'))] = _int(so.get(qn('w:val')), 1)
        nums[n.get(qn('w:numId'))] = (absmap.get(aid.get(qn('w:val')) if aid is not None else None), ov)
    counters = {}
    restarted = set()  # (numId, level) pairs whose startOverride has taken effect: Word restarts the list at a num's 1st use

    def num_pr(p):
        ppr = p._p.pPr
        if ppr is not None and ppr.numPr is not None and ppr.numPr.numId is not None:
            il = ppr.numPr.ilvl
            return str(ppr.numPr.numId.val), _int(il.val) if il is not None else 0
        for st in _style_chain(p.style):
            sp = st.element.pPr
            if sp is not None and sp.numPr is not None and sp.numPr.numId is not None:
                il = sp.numPr.ilvl
                ilvl = _int(il.val) if il is not None else 0
                if ppr is not None and ppr.numPr is not None and ppr.numPr.ilvl is not None:
                    ilvl = _int(ppr.numPr.ilvl.val)
                return str(sp.numPr.numId.val), ilvl
        return None

    def label(p):
        """(the label Word shows, its list level) for a numbered paragraph, or (None, None)."""
        np_ = num_pr(p)
        if not np_ or np_[0] == '0':
            return None, None
        a, ov = nums.get(np_[0], (None, {}))
        if a is None:
            return None, None
        lvls = {_int(l.get(qn('w:ilvl')), -1): l for l in a.findall(qn('w:lvl'))}
        def attr(i, tag, default):
            el = lvls[i].find(qn(tag)) if i in lvls else None
            return el.get(qn('w:val')) if el is not None else default
        lv = np_[1]
        if lv not in lvls or attr(lv, 'w:numFmt', 'decimal') in ('bullet', 'none'):
            return None, None
        c = counters.setdefault(id(a), {})
        def start(i):
            return ov.get(str(i), _int(attr(i, 'w:start', '1'), 1))
        if str(lv) in ov and (np_[0], lv) not in restarted:
            restarted.add((np_[0], lv))
            c[lv] = ov[str(lv)]  # a new list that shares the definition restarts here (startOverride), not where the old list stopped
        else:
            c[lv] = c[lv] + 1 if lv in c else start(lv)
        for d in [k for k in c if k > lv]:
            del c[d]
        txt = attr(lv, 'w:lvlText', '%' + str(lv + 1) + '.')
        return re.sub(r"%(\d)", lambda m: _fmt_num(c.get(int(m.group(1)) - 1, start(int(m.group(1)) - 1)), attr(int(m.group(1)) - 1, 'w:numFmt', 'decimal')), txt), lv
    return label


_A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'


def theme_fonts(d):
    """The theme's body (minor) and heading (major) Latin fonts, from word/theme/theme1.xml: {'minor': 'Aptos', 'major': ...}."""
    out = {}
    try:
        from lxml import etree
        part = next(r.target_part for r in d.part.rels.values() if r.reltype.endswith('/theme'))
        root = etree.fromstring(part.blob, _XML)
        for which in ('minor', 'major'):
            el = root.find('.//' + _A + which + 'Font/' + _A + 'latin')
            if el is not None and el.get('typeface'):
                out[which] = el.get('typeface')
    except Exception:  # best effort: a damaged theme part (any parse or lookup error) leaves the fonts unresolved, not the lint stopped
        pass
    return out


def rfonts_name(rfonts, themes):
    """The Latin font an rFonts element names: its ascii font, or its asciiTheme resolved through the theme (minorHAnsi -> the body font)."""
    if rfonts is None:
        return None
    name = rfonts.get(_W + 'ascii') or rfonts.get(_W + 'hAnsi')
    if name:
        return name
    th = rfonts.get(_W + 'asciiTheme') or rfonts.get(_W + 'hAnsiTheme') or ''
    return themes.get('major' if th.startswith('major') else 'minor') if th else None


def doc_default_font(d):
    """The document's default font and size (styles.xml docDefaults); a theme font is resolved to its name."""
    try:
        rpr = d.styles.element.find(_W + 'docDefaults/' + _W + 'rPrDefault/' + _W + 'rPr')
        if rpr is None:
            return None, None
        z = rpr.find(_W + 'sz')
        name = rfonts_name(rpr.find(_W + 'rFonts'), theme_fonts(d))
        size = int(z.get(_W + 'val')) / 2 if z is not None and (z.get(_W + 'val') or '').isdigit() else None
        return name, size
    except Exception:  # best effort: damaged docDefaults give no default font
        return None, None


def run_effective(r, p, dflt=(None, None)):
    """A run's font name, size (points), underline and bold as Word shows them: the run's own setting, else its
    character style chain, else its paragraph style chain, else the document default."""
    def chain(st, get):
        for s_ in _style_chain(st):
            try:
                v = get(s_)
            except (AttributeError, KeyError, ValueError, TypeError):
                v = None
            if v is not None:
                return v
        return None
    try:
        cst = r.style if r.style is not None and r.style.name != 'Default Paragraph Font' else None
    except Exception:
        cst = None
    pst = p.style
    name = r.font.name or chain(cst, lambda s_: s_.font.name) or chain(pst, lambda s_: s_.font.name) or dflt[0]
    sz = r.font.size.pt if r.font.size else None
    sz = sz or (lambda v: v.pt if v else None)(chain(cst, lambda s_: s_.font.size)) or (lambda v: v.pt if v else None)(chain(pst, lambda s_: s_.font.size)) or dflt[1]
    ul = r.font.underline
    if ul is None:
        ul = chain(cst, lambda s_: s_.font.underline)
    if ul is None:
        ul = chain(pst, lambda s_: s_.font.underline)
    bd = r.bold
    if bd is None:
        bd = chain(cst, lambda s_: s_.font.bold)
    return name, sz, bool(ul), bool(bd)


def visible_runs(p):
    """The runs a reader sees in a paragraph: direct runs and runs inside tracked insertions, hyperlinks, smart tags and
    content controls, but not deleted runs or runs inside a text box (read as its own paragraph). python-docx's p.runs
    returns only direct runs, so formatting inside a tracked insertion went unchecked."""
    from docx.text.run import Run
    skip = {_W + 'del', _W + 'moveFrom', _W + 'txbxContent'}
    out = []
    for r in p._p.iter(_W + 'r'):
        anc, hidden = r.getparent(), False
        while anc is not None and anc is not p._p:
            if anc.tag in skip:
                hidden = True
                break
            anc = anc.getparent()
        if not hidden:
            out.append(Run(r, p))
    return out


def eff_alignment(p):
    # the alignment Word shows: the paragraph's own, else its style's, else the base styles'
    try:
        a = p.alignment
        for st in _style_chain(p.style):
            if a is not None:
                break
            a = st.paragraph_format.alignment
        return int(a) if a is not None else None
    except (TypeError, ValueError, AttributeError):
        return None


def auto_numbered(p):
    # Word numbering set on the paragraph, or inherited from its style (List Number and the like)
    if p._p.pPr is not None and p._p.pPr.numPr is not None:
        return True
    for st in _style_chain(p.style):
        ppr = st.element.pPr
        if ppr is not None and ppr.numPr is not None:
            return True
    return False


_W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
HOUSE_FONT = 'aptos'  # house rule 9: 12-point Aptos
HOUSE_SIZE_PT = 12
ALIGN_CENTER, ALIGN_JUSTIFY = 1, 3  # python-docx WD_ALIGN_PARAGRAPH.CENTER and .JUSTIFY
MONTH = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
# a business entity's suffix, as an introductory clause writes it (Acme Holdings, Inc.; Beta LLC)
ENTITY = r"(?:Inc\.|LLC|L\.L\.C\.|LLP|L\.L\.P\.|LP|L\.P\.|Ltd\.|Corp\.|Co\.|P\.A\.|P\.C\.|PLLC|N\.A\.)"
LEAD_IN = re.compile(r"\bagrees?\s+as\s+follows\b", re.I)  # the lead-in (MSCD 2.159): the recitals end here
BETWEEN_AMONG = re.compile(r"\b(?:between|among|amongst)\b", re.I)  # the introductory clause's word (MSCD 2.47)
INTRO_WINDOW = 60  # substantive paragraphs: a short introductory clause sits among the first 60 (a cover page and a table of contents come before it)
INTRO_MIN_WORDS = 6  # an introductory clause can be short: This agreement is between ACME LLC ("Acme") and BETA INC. ("Beta").
CHANGES_SHOWN = 60  # tracked changes listed in the report; --json lists every one
COMMENTS_SHOWN = 10  # top-level Word comments listed in the report, with their replies; --json lists every one
BROAD_MIN_HITS, BROAD_SHARE = 5, 0.15  # a rule that hits more than 5 paragraphs and 15% of them is a broad trigger, not a finding


def off_house_font(name):
    return bool(name) and name.lower() != HOUSE_FONT


def off_house_size(points):
    return bool(points) and abs(points - HOUSE_SIZE_PT) > 0.01
_FALLBACK = '{http://schemas.openxmlformats.org/markup-compatibility/2006}Fallback'
_M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'  # Word's equation editor (m:oMath): its text sits in m:t, not w:t


def own_text(p_el, stats=None):
    """The text of a w:p, without the text of paragraphs nested inside it (a text box anchored in the paragraph).
    stats, when given, counts the hidden-text runs skipped ('hidden_runs'), so the report can say so."""
    out = []

    def walk(el):
        for ch in el:
            tag = ch.tag if isinstance(ch.tag, str) else ''
            if tag in (_W + 'p', _W + 'txbxContent', _W + 'moveFrom', _W + 'del', _FALLBACK, _W + 'pPr', _W + 'rPr'):
                continue  # nested paragraphs, text moved away or deleted (a deleted tab too), the hidden copy of a text box,
                # and properties (a tab stop in w:pPr/w:tabs is a w:tab too, but not text)
            if tag == _W + 'r':
                rp = ch.find(_W + 'rPr')
                v = rp.find(_W + 'vanish') if rp is not None else None
                if v is not None and v.get(_W + 'val') not in ('0', 'false', 'off'):
                    if stats is not None:
                        stats['hidden_runs'] = stats.get('hidden_runs', 0) + 1
                    continue  # hidden text: Word doesn't show or print it
            if tag == _W + 'noBreakHyphen':
                out.append('-')
                continue
            if tag == _W + 'sym':
                out.append('\ufffc')  # a symbol-font character (a checkbox): kept as 1 marker so the text keeps its place
                continue
            if tag in (_W + 't', _M + 't'):
                txt = ch.text or ''  # an equation's text (m:t) reads in line: Price × 1.05 stays checkable
                if INVISIBLE.search(txt):
                    if stats is not None:
                        stats['invisible_chars'] = stats.get('invisible_chars', 0) + len(INVISIBLE.findall(txt))
                    txt = INVISIBLE.sub('', txt)
                out.append(txt)
            elif tag == _W + 'tab':
                out.append('\t')
            elif tag in (_W + 'br', _W + 'cr'):
                out.append('\n')
            else:
                walk(ch)
    walk(p_el)
    return ''.join(out)


def _where(p_el, default):
    anc = p_el.getparent()
    while anc is not None:
        if anc.tag == _W + 'txbxContent':
            return 'textbox'
        if anc.tag == _W + 'tbl':
            return 'table'
        anc = anc.getparent()
    return default


def _read_docx_stdlib(path):
    """A plain reader for machines without python-docx: text, tables, headers, footers, footnotes and basic formatting
    facts from the XML. It can't show Word's automatic numbers, and the report says so."""
    import zipfile
    import xml.etree.ElementTree as ET
    try:
        return _read_docx_stdlib_inner(path, zipfile, ET)
    except (KeyError, ET.ParseError, zipfile.BadZipFile, AttributeError) as e:
        raise ValueError(f"this .docx is damaged ({e.__class__.__name__}: {e}); save it again from Word, or ask for a fresh copy")


def _read_docx_stdlib_inner(path, zipfile, ET):
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        def parts(prefix):
            return sorted(n for n in names if n.startswith('word/' + prefix) and n.endswith('.xml') and '/_rels/' not in n)
        def load(n):
            return ET.fromstring(z.read(n))
        doc = load('word/document.xml')
        paras, meta = [], {'stdlib_reader': True}
        body = doc.find(_W + 'body')

        def walk_paras(root, where, parent_map):
            for p_el in root.iter(_W + 'p'):
                w = where
                anc = parent_map.get(p_el)
                hidden = False
                while anc is not None:
                    if anc.tag == _FALLBACK:
                        hidden = True
                        break
                    anc = parent_map.get(anc)
                if hidden:
                    continue
                anc = parent_map.get(p_el)
                while anc is not None:
                    if anc.tag == _W + 'txbxContent':
                        w = 'textbox'
                        break
                    if anc.tag == _W + 'tbl' and where == 'body':
                        w = 'table'
                        break
                    anc = parent_map.get(anc)
                text = own_text(p_el)
                if where != 'body' and not text.strip():
                    continue
                ppr = p_el.find(_W + 'pPr')
                jc = ppr.find(_W + 'jc') if ppr is not None else None
                runs = [r for r in p_el.iter(_W + 'r')]
                def rprop(r, tag):
                    rp = r.find(_W + 'rPr')
                    return rp.find(_W + tag) if rp is not None else None
                bold = ''.join(''.join(t.text or '' for t in r.findall(_W + 't')) for r in runs
                               if rprop(r, 'b') is not None and rprop(r, 'b').get(_W + 'val') not in ('0', 'false'))
                underline = any(rprop(r, 'u') is not None and rprop(r, 'u').get(_W + 'val') not in ('none', None) for r in runs)
                fonts = sorted({rprop(r, 'rFonts').get(_W + 'ascii') for r in runs if rprop(r, 'rFonts') is not None and rprop(r, 'rFonts').get(_W + 'ascii')})
                sizes = sorted({int(rprop(r, 'sz').get(_W + 'val')) / 2 for r in runs if rprop(r, 'sz') is not None and (rprop(r, 'sz').get(_W + 'val') or '').isdigit()})
                fmt = {'fonts': fonts, 'sizes': sizes, 'underline': underline, 'bold_text': bold,
                       'centered': jc is not None and jc.get(_W + 'val') == 'center',
                       'auto_numbered': ppr is not None and ppr.find(_W + 'numPr') is not None}
                if jc is not None and jc.get(_W + 'val') == 'both':
                    fmt['justified'] = True
                paras.append({'idx': len(paras), 'text': text, 'where': w, 'style': '', 'fmt': fmt})
        walk_paras(body, 'body', {c: p for p in body.iter() for c in p})
        for prefix, where in (('header', 'header'), ('footer', 'footer'), ('footnotes', 'footnote'), ('endnotes', 'endnote')):
            for n in parts(prefix):
                root = load(n)
                for sep in [e for e in root if e.get(_W + 'type') in ('separator', 'continuationSeparator', 'continuationNotice')]:
                    root.remove(sep)
                walk_paras(root, where, {c: p for p in root.iter() for c in p})
        if any(body.find('.//' + _W + t) is not None for t in ('ins', 'del', 'moveFrom', 'moveTo')):
            meta['tracked_changes'] = True
        if 'word/comments.xml' in names:
            cr = load('word/comments.xml')
            meta['comments'] = [(c.get(_W + 'author') or '', comment_text(c, _W)) for c in cr.iter(_W + 'comment')]
    return paras, meta


def _docx_tables(body, el_idx):
    """Every table in the body (nested tables too), as rows of (cell text, paragraph number), read with the lint's own
    paragraph text, so tracked insertions count and deletions don't. A cell spanning 2 grid columns fills both, so the
    columns line up; a vertically merged continuation cell is empty, as Word shows it."""
    tables = []
    for tbl in body.iter(_W + 'tbl'):
        if any(a.tag == _FALLBACK for a in tbl.iterancestors()):
            continue
        rows = []
        for tr in tbl.iter(_W + 'tr'):
            if next((a for a in tr.iterancestors(_W + 'tbl')), None) is not tbl:
                continue  # a row of a nested table: read with that table
            cells = []
            for tc in tr.iter(_W + 'tc'):
                if next((a for a in tc.iterancestors(_W + 'tr')), None) is not tr:
                    continue
                own = [p for p in tc.iter(_W + 'p') if next((a for a in p.iterancestors(_W + 'tc')), None) is tc and p in el_idx]
                vm = tc.find(f'{_W}tcPr/{_W}vMerge')
                merged = vm is not None and vm.get(_W + 'val') not in ('restart',)
                text = '' if merged else '\n'.join(own_text(p) for p in own).strip()
                idx = next((el_idx[p] for p in own if own_text(p).strip()), el_idx[own[0]] if own else -1)
                gs = tc.find(f'{_W}tcPr/{_W}gridSpan')
                span = int(gs.get(_W + 'val')) if gs is not None and (gs.get(_W + 'val') or '').isdigit() else 1
                cells += [(text, idx)] * min(max(1, span), 63)  # Word allows 63 columns; a damaged file can claim billions
            rows.append(cells)
        tables.append(rows)
    return tables


def _run_format(p, dflt):
    """The formatting facts of a python-docx paragraph: alignment, fonts and sizes (with where an off-house font comes from),
    underline, bold text and Word numbering. Raises whatever python-docx raises on a damaged property; the caller decides."""
    fmt = {}
    align = eff_alignment(p)
    if align == ALIGN_JUSTIFY:
        fmt['justified'] = True
    fonts, sizes, underline = set(), set(), False
    font_styles = set()
    bold_parts = []
    for r in visible_runs(p):
        # what Word shows: the run's own setting, else its character style's, else the paragraph style's, else the document default
        name, size, ul, bd = run_effective(r, p, dflt)
        if ul and r.text.strip():
            underline = True
        if name and r.text.strip():
            fonts.add(name)
            if not r.font.name and off_house_font(name):
                try:  # where Word gets the font: a character style, the paragraph style, or the default
                    rst = r.style
                    if rst is not None and rst.name != 'Default Paragraph Font' and any(st_.font.name for st_ in _style_chain(rst)):
                        font_styles.add(f'character style "{rst.name}"')
                    elif p.style is not None and any(st_.font.name for st_ in _style_chain(p.style)):
                        font_styles.add(f'paragraph style "{p.style.name}"')
                except (AttributeError, KeyError, ValueError):
                    pass
        if size and r.text.strip():
            sizes.add(size)
        if bd:
            bold_parts.append(r.text)
    fmt.update({'fonts': sorted(fonts), 'font_styles': sorted(font_styles), 'sizes': sorted(sizes), 'underline': underline, 'bold_text': ''.join(bold_parts),
                'centered': align == ALIGN_CENTER, 'auto_numbered': auto_numbered(p)})
    return fmt


_W14_PARA_ID = '{http://schemas.microsoft.com/office/word/2010/wordml}paraId'
_W15 = '{http://schemas.microsoft.com/office/word/2012/wordml}'


COMMENT_SHOWN = 300  # characters of each comment the Markdown report shows; the JSON carries the whole text


def comment_text(c, w=None):
    """A Word comment's whole text, its paragraphs joined by a space (the JSON carries it all; the report shortens it)."""
    w = w or _W
    paras = [''.join(t.text or '' for t in p.iter(w + 't')) for p in c.iter(w + 'p')]
    return ' '.join(x.strip() for x in paras if x.strip()) if paras else ''.join(t.text or '' for t in c.iter(w + 't'))


def _comments_with_replies(croot, d):
    """The Word comments as (author, text, reply_to): reply_to is the index of the comment this one answers, or None.
    Word keeps the threading in commentsExtended.xml (w15:paraIdParent names the parent comment's 1st paragraph);
    without that part, or when it can't be read, every comment is a top-level comment."""
    from lxml import etree
    out, para_ids = [], {}
    for n, c in enumerate(croot.iter(_W + 'comment')):
        out.append([c.get(_W + 'author') or '', comment_text(c), None])
        first_p = c.find(_W + 'p')
        if first_p is not None and first_p.get(_W14_PARA_ID):
            para_ids[first_p.get(_W14_PARA_ID).upper()] = n
    try:
        xpart = next(r.target_part for r in d.part.rels.values() if r.reltype.endswith('/commentsExtended'))
        xroot = etree.fromstring(xpart.blob, _XML)
        for ex in xroot.iter(_W15 + 'commentEx'):
            child, parent = (ex.get(_W15 + 'paraId') or '').upper(), (ex.get(_W15 + 'paraIdParent') or '').upper()
            if child in para_ids and parent in para_ids and para_ids[parent] != para_ids[child]:
                out[para_ids[child]][2] = para_ids[parent]
    except StopIteration:
        pass  # no commentsExtended part: no replies
    except Exception:
        pass  # a damaged commentsExtended part: the comments stay, unthreaded
    return [tuple(c) for c in out]


def read_paragraphs(path):
    """Return (paragraphs, meta): each paragraph a dict with idx, text, where (body, table, textbox, header, footer, footnote, endnote),
    style, and formatting facts (fmt); meta holds what the reader noticed (encoding, tracked changes, comments, unread content)."""
    ext = os.path.splitext(path)[1].lower()
    if ext == '.docx':
        return _read_docx(path)
    if ext not in ('.txt', '.md', ''):
        raise ValueError(f'unsupported file type {ext}: convert it to .docx or .txt first (for a PDF, extract its text)')
    return _read_text(path, ext)


def _read_docx(path):
    """A .docx: text, tables, headers, footers, footnotes, formatting, numbering, tracked changes and comments, through python-docx
    (or the plain reader without it). Raises ValueError for a file that is not a readable .docx."""
    paras = []
    paras_meta = {}  # the reader fills it below; add() may set 'numbering_unread' before the font entries are known
    import zipfile
    if not zipfile.is_zipfile(path):
        with open(path, 'rb') as fh:
            head = fh.read(8)
        if head.startswith(b'\xd0\xcf\x11\xe0'):
            raise ValueError('this is an old binary Word file (.doc) with a .docx name, or a password-protected .docx (Word encrypts those inside the same binary package): '
                             'convert a .doc first (soffice --headless --convert-to docx <file>); for a protected file, ask for an unprotected copy')
        raise ValueError("this file isn't a valid .docx (a .docx is a zip package, and this one won't open); ask for a fresh copy, or save it again from Word")
    try:
        import docx  # python-docx
    except ImportError:
        return _read_docx_stdlib(path)
    try:
        d = docx.Document(path)
    except Exception as e:
        raise ValueError(f"Word couldn't open this .docx ({e.__class__.__name__}: {e}); save it again from Word, or convert it with soffice --headless --convert-to docx") from e
    labeler = numbering_labeler(d)
    dflt = doc_default_font(d)
    def add(p, where):
        try:
            fmt = _run_format(p, dflt)
        except Exception:  # a run property python-docx rejects (<w:sz w:val="abc"/>): the text still counts; the formatting of this paragraph doesn't
            fmt = {}
            paras_meta['formatting_unread'] = paras_meta.get('formatting_unread', 0) + 1
        text = own_text(p._p, paras_meta)  # includes inserted text, skips deleted text and text boxes (read as their own paragraphs)
        try:
            style = p.style.name if p.style is not None else ''
        except Exception:  # a pStyle with no w:val, or a style the file lacks
            style = ''
        entry = {'idx': len(paras), 'text': text, 'where': where, 'style': style, 'fmt': fmt}
        if fmt.get('auto_numbered') and where in ('body', 'table'):
            try:
                lab, lvl = labeler(p)
            except Exception:  # a numId or ilvl with no w:val, or a damaged numbering part: the lint goes on without the label
                lab, lvl = None, None
                paras_meta['numbering_unread'] = True
            if lab:
                entry['auto_label'] = lab  # the number Word shows (A., 1., (a)); it isn't in the text
                entry['auto_level'] = lvl  # its list level (0 is the outermost): tells (i) after (h) from the letter i
        paras.append(entry)
    # Walk every paragraph in document order, including paragraphs that python-docx's
    # Document.paragraphs skips: those inside content controls (w:sdt), revision wrappers
    # (w:ins, w:moveTo) and tables. Each paragraph is read once, even in merged table cells.
    from docx.text.paragraph import Paragraph
    from docx.oxml.ns import qn as _qn
    el_idx = {}  # each body w:p element -> its paragraph number, for the table reader
    for p_el in d.element.body.iter(_qn('w:p')):
        if any(a.tag == _FALLBACK for a in p_el.iterancestors()):
            continue  # the hidden copy of a text box: Word shows the mc:Choice copy, read above or below
        before = len(paras)
        add(Paragraph(p_el, d._body), _where(p_el, 'body'))
        if len(paras) > before:
            el_idx[p_el] = paras[-1]['idx']
    tables = _docx_tables(d.element.body, el_idx)
    # Headers and footers come after the body, so body paragraph numbers don't move (a draft date in a footer is contract text too)
    seen_parts = set()
    for sec in d.sections:
        for part, where in ((sec.header, 'header'), (sec.first_page_header, 'header'), (sec.even_page_header, 'header'),
                            (sec.footer, 'footer'), (sec.first_page_footer, 'footer'), (sec.even_page_footer, 'footer')):
            try:
                if part.is_linked_to_previous:
                    continue
                el = part._element
            except Exception:
                continue
            if id(el) in seen_parts:
                continue
            seen_parts.add(id(el))
            for p_el in el.iter(_qn('w:p')):
                if any(a.tag == _FALLBACK for a in p_el.iterancestors()):
                    continue
                hp = Paragraph(p_el, part)
                if ''.join(x.text or '' for x in p_el.iter(_qn('w:t'))).strip():
                    add(hp, where)
    for rel in list(d.part.rels.values()):
        kind = 'footnote' if rel.reltype.endswith('/footnotes') else 'endnote' if rel.reltype.endswith('/endnotes') else None
        if not kind:
            continue
        try:
            from lxml import etree
            root = etree.fromstring(rel.target_part.blob, _XML)
        except Exception:
            continue
        for note in root:
            if note.get(_qn('w:type')) in ('separator', 'continuationSeparator', 'continuationNotice'):
                continue
            for p_el in note.iter(_qn('w:p')):
                t = own_text(p_el)
                if t.strip():
                    paras.append({'idx': len(paras), 'text': t, 'where': kind, 'style': '', 'fmt': {}})
    try:
        nst = d.styles['Normal']
        st = nst.font
        npr = nst.element.find(_W + 'rPr')
        # the Normal style's font: named, or a theme font resolved to its name, or else the document default
        nfont = st.name or rfonts_name(npr.find(_W + 'rFonts') if npr is not None else None, theme_fonts(d)) or dflt[0]
        paras_meta.update({'normal_font': nfont, 'normal_size': st.size.pt if st.size else dflt[1]})
    except KeyError:
        paras_meta.update({'normal_font': dflt[0], 'normal_size': dflt[1]})
    paras_meta['tables'] = tables
    from docx.oxml.ns import qn
    from lxml import etree
    body = d.element.body
    # tracked changes in the body, and in the headers, footers, footnotes and endnotes (each change says where it is)
    part_roots = [('body', body)]
    for rel in d.part.rels.values():
        kind_ = rel.reltype.rsplit('/', 1)[-1]
        if kind_ in ('header', 'footer', 'footnotes', 'endnotes') and not rel.is_external:
            try:
                part_roots.append((kind_, etree.fromstring(rel.target_part.blob, _XML)))
            except (etree.XMLSyntaxError, ValueError, AttributeError):
                paras_meta.setdefault('unread_parts', []).append(kind_)
    changes = []  # each change with its author, so a response to the other side's markup can take them 1 by 1
    for where_, root_ in part_roots:
        for el in root_.iter(qn('w:ins'), qn('w:del'), qn('w:moveFrom'), qn('w:moveTo')):
            kind = el.tag.split('}')[1]
            txt = ''.join(t.text or '' for t in el.iter(qn('w:t'), qn('w:delText')))
            if txt.strip() or kind in ('ins', 'del'):
                changes.append({'kind': {'ins': 'inserted', 'del': 'deleted', 'moveFrom': 'moved from', 'moveTo': 'moved to'}[kind],
                                'author': el.get(qn('w:author')) or '', 'date': (el.get(qn('w:date')) or '')[:10], 'text': txt[:200],
                                'truncated': len(txt) > 200, **({'where': where_} if where_ != 'body' else {})})
    if changes:
        paras_meta['tracked_changes'] = True  # text is read as if every change were accepted
        paras_meta['changes'] = changes
    n_marks = sum(1 for ppr in body.iter(qn('w:pPr')) if ppr.find(f'{_W}rPr/{_W}del') is not None)  # a deleted paragraph mark
    if n_marks:
        paras_meta['para_mark_deletions'] = n_marks  # accepting them joins each such paragraph to the next; the lint kept them apart
    # content the lint can't read: say so, so the reviewer checks it by hand
    unread = collections.Counter()
    for tag, label_ in (('altChunk', 'embedded documents (altChunk)'), ('object', 'embedded objects (OLE)'), ('subDoc', 'subdocuments')):
        unread[label_] += sum(1 for _ in body.iter(qn('w:' + tag)))
    for gd in body.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}graphicData'):
        uri = gd.get('uri') or ''
        if uri.endswith('/chart'):
            unread['charts'] += 1
        elif uri.endswith('/diagram'):
            unread['SmartArt diagrams'] += 1
    paras_meta['unread'] = {k: v for k, v in unread.items() if v}
    n_eq = sum(1 for _ in body.iter(_M + 'oMath'))
    if n_eq:
        paras_meta['equations'] = n_eq  # read as plain text in the paragraphs; the layout (fractions, exponents) is lost
    try:
        cpart = next(r.target_part for r in d.part.rels.values() if r.reltype.endswith('/comments'))
        croot = etree.fromstring(cpart.blob, _XML)
        paras_meta['comments'] = _comments_with_replies(croot, d)
    except StopIteration:
        pass  # no comments part
    except (etree.XMLSyntaxError, ValueError, AttributeError) as e:
        paras_meta['comments_unreadable'] = f'{e.__class__.__name__}: {e}'
    return paras, paras_meta


def _read_text(path, ext):
    """A .txt or .md file: decode it (UTF-8, UTF-16, UTF-32 or Windows-1252), refuse a binary file with a text name, drop page breaks
    and fenced code blocks, and split the text into paragraphs."""
    with open(path, 'rb') as fh:
        raw = fh.read()
    meta = {}
    if raw.startswith(b'%PDF'):
        raise ValueError('this is a PDF with a text-file name: extract its text first (pdftotext -layout <file> out.txt)')
    if raw.startswith(b'PK\x03\x04'):
        raise ValueError('this is a zip package (probably a .docx) with a text-file name: rename it to .docx and run the lint again')
    if raw.startswith(b'\xd0\xcf\x11\xe0'):
        raise ValueError('this is an old binary Office file (a .doc, or a password-protected .docx) with a text-file name: convert it first (soffice --headless --convert-to docx <file>), or ask for an unprotected copy')
    if raw.startswith((b'\xff\xfe\x00\x00', b'\x00\x00\xfe\xff')):
        text, meta['encoding'] = raw.decode('utf-32', errors='replace'), 'UTF-32'
    elif raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        text, meta['encoding'] = raw.decode('utf-16', errors='replace'), 'UTF-16'
    elif len(raw) > 3 and raw[:2000].count(b'\x00') > len(raw[:2000]) // 4:  # UTF-16 without a byte-order mark
        head = raw[:2000]
        le = head[1::2].count(b'\x00') >= head[0::2].count(b'\x00')  # little-endian puts the zero byte 2nd (A = 41 00)
        text, meta['encoding'] = raw.decode('utf-16-le' if le else 'utf-16-be', errors='replace'), 'UTF-16'
    else:
        try:
            text = raw.decode('utf-8-sig')
        except UnicodeDecodeError:
            # UTF-8 with stray Windows-1252 bytes (a curly quote pasted from Word), or Windows-1252 throughout: decode each
            # byte that isn't valid UTF-8 as Windows-1252, so the valid UTF-8 around it stays intact (curly quotes and dashes survive)
            n_bad = [0]
            def _fallback(err):
                n_bad[0] += err.end - err.start
                return err.object[err.start:err.end].decode('cp1252', errors='replace'), err.end
            codecs.register_error('mscd-cp1252', _fallback)
            text = raw.decode('utf-8-sig', errors='mscd-cp1252')
            utf8_multibyte = sum(1 for b in raw if b >= 0xC2 and b <= 0xF4)
            meta['encoding'] = ('UTF-8 with ' + str(n_bad[0]) + ' Windows-1252 bytes') if utf8_multibyte > n_bad[0] else 'Windows-1252'
    if '\ufffd' in text:
        meta['bad_chars'] = text.count('\ufffd')
    if '\x00' in text:
        meta['nul_chars'] = text.count('\x00')
        text = text.replace('\x00', '')
    n_inv = len(INVISIBLE.findall(text))
    if n_inv:
        meta['invisible_chars'] = n_inv
        text = INVISIBLE.sub('', text)
    junk = sum(1 for ch in text if ch == '\ufffd' or (ord(ch) < 32 and ch not in '\t\n\r\f'))
    if len(text) >= 40 and junk > len(text) // 20:
        raise ValueError("this file isn't text (most of it is control characters or undecodable bytes): it may be an image, a PDF or a binary file with a .txt name; extract or convert its text first")
    if '\f' in text:
        meta['page_breaks'] = text.count('\f')
        text = text.replace('\f', '\n\n')  # a page break from pdftotext ends a paragraph
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    if ext == '.md' and '```' in text:
        # a fenced code block (``` ... ```) is not contract text: a sample, a drafting note, a command; drop it and say so
        text, n_code = re.subn(r"^[ \t]*```[^\n]*\n(?:(?!^[ \t]*```).*\n)*?[ \t]*```[^\n]*(?:\n|$)", '\n', text, flags=re.M)
        if n_code:
            meta['code_blocks'] = n_code
    return _split_text(text, ext, meta), meta


def _split_text(text, ext, meta):
    """The paragraphs of a text file: blocks between blank lines, or between typed enumerators; a file with no blank lines is read
    1 line per paragraph, with wrapped lines joined (meta notes it)."""
    paras = []
    if not re.search(r'\n[ \t]*\n', text.strip()) and text.strip().count('\n') >= 2:
        # no blank lines: paragraphs are separated by single newlines (pasted from an email). A line that
        # continues a sentence (it starts in lowercase and the line before doesn't end a sentence) is a wrapped line.
        out = []
        for line in text.split('\n'):
            if out and line.strip() and (line[:1].islower() and not re.search(r'[.:;!?\u201d")]\s*$', out[-1])
                                         or re.search(r"\b(?:by|of|to|the|a|an|and|or|nor|for|with|in|on|at|from|under|that|which|who|its|their|his|her|"
                                                      r"shall|will|may|must|than|as|between|among|is|are|if|unless|no|not|each|any|all|this|these)\s*$", out[-1], re.I)):
                # a wrapped line: it starts in lowercase after an unfinished sentence, or the line before ends on a word that can't end a sentence
                out[-1] += ' ' + line.strip()
            else:
                out.append(line)
        text = '\n\n'.join(out)
        meta['single_newlines'] = True
    for block in re.split(r'\n\s*\n|\n(?=\s*(?:[IVX]+\.|[A-Z]\.|\d+\.|\([a-z]{1,3}\))\s)', text):
        if block.strip():
            fmt = {'bold_text': ' '.join(re.findall(r"\*\*(.+?)\*\*", block))} if ext == '.md' else {}
            paras.append({'idx': len(paras), 'text': block.strip('\n'), 'where': 'body', 'style': '', 'fmt': fmt})
    return paras

# ---------------------------------------------------------------- house-style checks

BE = r"(?:am|is|are|was|were|be|been|being)"
# words that open a conditional clause, shared by the checks for shall in a condition (MSCD 3.358-3.360)
COND_LEAD = r"(?:if|unless|until|in\s+the\s+event|to\s+the\s+extent|so\s+long\s+as|as\s+long\s+as)"
IRREG = ("made|paid|given|taken|held|sold|bought|sent|kept|done|known|shown|told|brought|found|left|met|put|set|"
         "laid|led|lent|lost|meant|read|run|seen|spent|won|written|borne|begun|chosen|drawn|driven|forgotten|"
         "frozen|hidden|ridden|shaken|spoken|stolen|sworn|thrown|undertaken|withdrawn|withheld|forgiven|"
         "granted|bound|built|caught|cut|dealt|fed|felt|fought|got|gotten|heard|hit|hung|hurt|let|"
         "overcome|paid|proven|quit|shut|sought|split|spread|struck|taught|thought|understood|upheld|wound")
# words that end in -ed but are never a past participle (the Units are red; the price is indeed fixed; a parcel is deeded): never a passive
NOT_PARTICIPLE = set('red indeed need deed seed speed hundred sacred naked'.split())
NOT_PASSIVE = set("""void voidable effective liable entitled responsible able unable subject due payable eligible open limited
 bound obligated aware available necessary sufficient concerned interested located based
 married divorced incorporated organized licensed qualified authorized registered dated closed""".split()) | NOT_PARTICIPLE  # a bank is closed: a state (open is listed too)
# a parenthetical or either/both may sit between be and the participle (shall be (at Acme's election) repaired or replaced); "is (a) paid" is read too
PASSIVE_RE = re.compile(rf"\b{BE}\s+(?:not\s+|also\s+|hereby\s+|then\s+|thereby\s+|so\s+|each\s+|jointly\s+|severally\s+|fully\s+|promptly\s+){{0,3}}(?:\([^()]{{1,60}}\)\s+)?(?:(?:either|both)\s+)?((?:\w+ed)|(?:{IRREG}))\b", re.I)
MODAL_BE = re.compile(rf"\b(?:shall|will|may|must|would|should|could|might|can|(?:is|are)\s+to)\s+(?:not\s+)?(?:be|have\s+been)\s+(?:\([^()]{{1,60}}\)\s+)?(?:(?:either|both)\s+)?(?:\w+ly\s+(?:and\s+\w+ly\s+)?)?(?:\([^()]{{1,60}}\)\s+)?((?:\w+ed)|(?:{IRREG}))\b", re.I)
BY_MEANS = re.compile(r"(?:" + MONTH + r"|\d|(?:the\s+)?(?:[A-Z]\w+\s+)?(?:date|day|end|deadline|time|Date|Day)|"
                      r"(?:wire|electronic|bank|ACH)\s+transfer|check|cheque|mail|courier|hand|email|e-mail|fax|arbitration|mediation|litigation|"
                      r"means\s+of|reference|operation\s+of\s+law|law|written\s+notice|notice)\b", re.I)

NUM_WORDS = ("one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen "
             "eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand").split()
NUM_RE = re.compile(r"\b(" + "|".join(NUM_WORDS) + r")(?:-(" + "|".join(NUM_WORDS) + r"))?\b", re.I)
ONE_WORD = re.compile(r"\b(?:no one|one another|any one time|each one|(?:for|needs?|wants?|requests?|obtains?|provides?|issues?|keeps?|receives?)\s+one(?=\s*[.,;:)]|\s+(?:that|which|who|if|unless|when|before|after|from|to|at|on|in)\b)|(?:the|a|an|this|that|another|new|similar|comparable|equivalent|replacement|with)\s+one(?=\s+(?:that|who|which|whom|of\s+equal|of\s+like|of\s+the\s+same)\b)|(?:a|another|new|similar|comparable|equivalent|replacement)\s+one\b(?!\s+(?:of|or|and)\b)|(?:a|an|the)\s+[a-z]+(?:ed|en|ic|al|ful|ive|ous|ary|ar|er|ing)\s+one\b(?=\s*[.,;:)]|\s+(?:that|who|which)\b)|one-(?!(?:half|third|quarter|fourth|fifth|tenth|hundredth)\b)[a-z]+)", re.I)  # pronoun or part of a word: keep
UNIT_WORDS = r"(?:Dollars?|Cents?|Percent|Days?|Business|Calendar|Working|Trading|Banking|Consecutive|Fiscal|Full|Additional|Months?|Years?|Weeks?|Hours?|Minutes?|Units?|Shares?|Times|Thousand|Hundred|Million|Billion|And)"
NONPARTY_SHALL = re.compile(r"(?:\b[A-Z][\w-]*(?:['’]s)\s+|\b(?:[Ss]ite|[Ii]ts|[Tt]heir)\s+)?\b(?:employees|subcontractors|sub-?agents|Sub-?agents|agents|personnel|staff|contractors|officers|directors|representatives|Affiliates|affiliates|lenders|suppliers|vendors|customers|end users)\s+shall\b(?!\s+not\s+be\b)")
REDUCED_BY = re.compile(r"\b(?:[a-z]+ed|paid|made|given|sent|held|sold|owed|borne|taken|done|shown|known|brought|kept|won|built|bought|chosen|drawn|written|spent|lent|granted)\s+by\s+(?:(?:the|a|an|each|any)\s+)?(?:[A-Z][\w-]*|[a-z]+\s+(?:appraiser|arbitrator|auditor|accountant|court|lender|agent|engineer|architect|physician|inspector))\b")
REDUCED_SKIP = {'is', 'are', 'was', 'were', 'be', 'been', 'being', 'has', 'have', 'had', 'shall', 'will', 'may', 'must', 'not', 'as', 'unless', 'if', 'when', 'except',
                'and', 'or', 'to', 'than', 'then', 'also', 'jointly', 'duly', 'once', 'until', 'followed', 'accompanied', 'it', 'they', 'he', 'she', 'we', 'who', 'that', 'which',
                'expressly', 'previously', 'otherwise', 'hereby', 'thereby', 'already', 'later', 'first', 'last', 'directly'}
ONE_COUNT = re.compile(r"\b(?:one or more|one or both|any one|one of|one side|one party)\b", re.I)  # counts something: digit
# a warranty of goods in a sale of goods: warrants is the right verb there (MSCD 3.415; 3.453), and it may speak of future performance
GOODS_WARRANTY = re.compile(r"\bwarrants?\s+(?:to\s+[A-Z][\w-]*(?:\s+[A-Z][\w-]*)?\s+)?that\s+(?:the|each|all|any|every)\s+(?:Goods|Products?|Equipment|Units?|Parts?|Components?|Materials?|Merchandise|Inventory|Machines?|Vehicles?|Hardware)\b")
RELATIVE_AGREES = re.compile(r"\b(?!(?:states?|acknowledges?|confirms?|represents?|warrants?|certif(?:y|ies)|understands?|agrees?|provides?|provided|means|requires?|so|such|except)\b)[a-z]+\s+(?:that|which)\s+(?:(?:the|its|each|any)\s+)?[A-Za-z][\w-]*(?:\s+[A-Za-z][\w-]*){0,2}\s+$"
                            r"|\b(?:under|by|in|with|through)\s+which\s+(?:(?:the|its|each|any)\s+)?[A-Za-z][\w-]*(?:\s+[A-Za-z][\w-]*){0,2}\s+$")
PROPER_AFTER = re.compile(r"(?:\s+[A-Z][\w'-]*){0,2}\s+(?:Plaza|Place|Street|St\.|Avenue|Ave\.|Center|Centre|Tower|Towers|Square|Park|Building|Court|Circle|Way|Road|Boulevard|Drive|Lane|Bank|Judicial|Circuit|District|Floor)\b")  # case matters: Two Lattice Plaza is a name; Two bank accounts is a count
FIRST_COUNT = re.compile(r"\bfirst\s+(?:anniversary|day|business day|month|year|quarter|installment|payment|calendar|week|period)\b", re.I)
ORD_RE = re.compile(r"\b((?:twenty|thirty)-)?(second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|thirtieth|hundredth|(?<=-)first)\b", re.I)
CENTS_00 = re.compile(r"\$\d{1,3}(?:,\d{3})+\.00\b|\$\d{4,}\.00\b")  # $1,000.00 and up; the money-small-cents variant covers $2.00 to $999.00 with its nearby-cents exception


SENT_BREAK = re.compile(r"[.;!?][\"”’)]*\s+(?=[A-Z“\"(])")  # where 1 sentence (or a semicolon clause) ends and the next starts


def sentence_bounds(t, a, b):
    """The start and end of the sentence holding t[a:b]. A period after an abbreviation (Inc., No., U.S.) doesn't end a sentence."""
    lo, hi = 0, len(t)
    for e in SENT_BREAK.finditer(t):
        if ABBREV.search(t[max(0, e.start() - 8):e.start() + 1]):
            continue
        if e.end() <= a:
            lo = e.end()
        elif e.start() >= b:
            hi = e.start() + 1
            break
    return lo, hi


def sentence_at(t, pos):
    """The sentence of t that holds position pos."""
    lo, hi = sentence_bounds(t, pos, pos + 1)
    return t[lo:hi]


def sentence_from(t, pos):
    """The rest of the sentence of t from position pos on (a definition's words after means)."""
    return t[pos:sentence_bounds(t, pos, pos + 1)[1]]


class _Span:
    """A match-like object for a span that no single regex matched: group(), start() and end() of t[start:end]."""
    __slots__ = ('_text', '_start', '_end')

    def __init__(self, text, start, end):
        self._text, self._start, self._end = text, start, end

    def group(self, i=0):
        return self._text[self._start:self._end]

    def start(self):
        return self._start

    def end(self):
        return self._end


_SMALL = {w: i for i, w in enumerate('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen '
                                     'sixteen seventeen eighteen nineteen'.split())}
_TENS = {w: 10 * i for i, w in enumerate('_ _ twenty thirty forty fifty sixty seventy eighty ninety'.split()) if w != '_'}
_SCALES = {'thousand': 10 ** 3, 'million': 10 ** 6, 'billion': 10 ** 9}
_NUMBER_WORDS = set(_SMALL) | set(_TENS) | set(_SCALES) | {'hundred'}
_FRACTION_WORDS = {'half', 'halves', 'quarter', 'quarters', 'thirds', 'fourths', 'fifths', 'tenths', 'hundredths', 'point'}
# words that may sit between a number in words and its digits: Five Thousand Dollars ($5,000); thirty (30) days
_UNIT_WORDS = {'dollars', 'dollar', 'us', 'u', 's', 'percent', 'per', 'cent'}


def words_value(text):
    """The value of a number written in words (Four Hundred Twenty-Eight Thousand Five Hundred) as an int, or None.
    Every word must be a number word or *and*; a fraction or decimal in words (one and one-half) gives None."""
    words = re.findall(r"[a-z]+", text.lower().replace('-', ' '))
    if not words or any(w in _FRACTION_WORDS for w in words) or not any(w in _SMALL or w in _TENS for w in words):
        return None
    total, cur = 0, 0
    for w in words:
        if w in _SMALL:
            cur += _SMALL[w]
        elif w in _TENS:
            cur += _TENS[w]
        elif w == 'hundred':
            cur = (cur or 1) * 100
        elif w in _SCALES:
            total += (cur or 1) * _SCALES[w]
            cur = 0
        elif w != 'and':
            return None
    return total + cur


_WD_PAREN = re.compile(r"\(\s*(?:US|U\.S\.)?\$?\s*(\d[\d,]*(?:\.\d+)?)\s*(%?)\s*\)")
_WD_CENTS = re.compile(r"\s+and\s+(?:(\d{1,2}|no)\s*/\s*100|([a-z][a-z\- ]{1,40}?)\s+cents?)\s*(?:(?:U\.?S\.?\s+)?dollars?)?\s*$", re.I)
_WD_TOKEN = re.compile(r"[A-Za-z]+(?:[-\u2010\u2011][A-Za-z]+)*")
# digits then the words in parentheses: 30 (thirty) days; $5,000 (five thousand dollars). Section 3 (Payment) has no number words, so it stays clear
DIGITS_THEN_WORDS = re.compile(r"(?<![\d.,])\$?(\d[\d,]*(?:\.\d+)?)\s*%?\s*\(\s*((?:[A-Za-z]+(?:[-\u2010\u2011\s]+[A-Za-z]+)*))\s*\)")


def words_before(t, pos):
    """A number written in words that ends just before position pos (the parenthesis of its digits).
    Returns (start, value): start is where the words begin, or None if no number words come right before;
    value is an int (a Decimal when cents are stated), or None when the words can't be read with certainty."""
    head = t[max(0, pos - 400):pos]
    base = pos - len(head)
    cents = 0
    mc = _WD_CENTS.search(head)
    if mc:
        cents = (0 if mc.group(1).lower() == 'no' else int(mc.group(1))) if mc.group(1) else words_value(mc.group(2))
        head = head[:mc.start()]
    toks = list(_WD_TOKEN.finditer(head))
    end = len(toks)
    while end and toks[end - 1].group(0).lower() in _UNIT_WORDS:
        end -= 1  # Dollars, Percent, U.S. Dollars
    if not end or re.search(r"[^\s.\-A-Za-z]", head[toks[end - 1].end():]):
        return None, None  # only spaces, hyphens, unit words and the periods of U.S. may come between the words and the digits

    def is_number(tok):
        return all(w in _NUMBER_WORDS or w in _FRACTION_WORDS or w == 'and' for w in re.split(r"[-\u2010\u2011]", tok.group(0).lower()))

    k = end
    while k and is_number(toks[k - 1]) and (k == end or not head[toks[k - 1].end():toks[k].start()].strip()):
        k -= 1  # walk back over number words; a comma or other mark between 2 of them ends the number
    while k < end and toks[k].group(0).lower() == 'and':
        k += 1  # a number never starts with and
    if k == end:
        return None, None
    value = words_value(head[toks[k].start():toks[end - 1].end()])
    if k >= 2 and toks[k - 1].group(0).lower() == 'of' and is_number(toks[k - 2]):
        value = None  # one-half of one percent (0.5%): a fraction of a number; report words and digits, never a conflict
    if value is not None and cents is None:
        value = None  # cents in words that can't be read
    elif value is not None and cents:
        value = Decimal(value) + Decimal(cents) / 100
    return base + toks[k].start(), value


ABBREV = re.compile(r"(?:\b(?:Inc|INC|Ltd|LTD|Co|CO|Corp|CORP|No|Nos|Mr|Ms|Mrs|Dr|St|Jr|Sr|Ave|Blvd|Rd|Ste|Dept|Esq|Bros|Assn|Mfg|Intl|Natl|U\.S|e\.g|i\.e|v|vs|etc|L\.L\.C|L\.P|N\.A|P\.A|P\.C|Sec|Art|p|pp|a\.m|p\.m|"
                    r"Ann|Stat|Gen|Rev|Civ|Proc|Reg|Regs|Supp|App|Cir|Ct|Dist|Div|Ch|Pt|Vol|Fed|Cal|Calif|Tenn|Ga|Ky|Ala|Miss|Ark|Fla|Mass|Mich|Minn|Va|"
                    r"Wash|Wis|Pa|Tex|Okla|Or|Ore|Colo|Conn|Del|Ill|Ind|Kan|La|Md|Mo|Mont|Neb|Nev|Vt|Wyo|N\.C|S\.C|N\.J|N\.M|N\.Y|N\.D|S\.D|W\.Va|R\.I|N\.H|D\.C)\.)$")
ONE_SPACE = re.compile(r"([.?!][\"”’)]?)[ \u00a0](?=[A-Z“\"(])")
TWO_AFTER_COLON = re.compile(r":  +\S")
POLICY_VERB = r"(?P<verb>terminates|renews|expires|becomes(?:\s+(?:effective|due|void|payable|final|binding))?|extends|ends|lapses|passes|accrues|survives|ceases|reverts|applies|increases|decreases|takes\s+effect|is\s+(?:effective|void|subordinate|terminated|extended|suspended|released|due|payable|final|binding))"
# the subject of a contingent policy: a determiner or a possessive (Beta's right to use the Software) and up to 5 more words
POLICY_SUBJ = r"(?:(?:this|the|that|a|an|each|any|no|neither|such)|[A-Z][\w'’-]*['’]s|title\s+to(?:\s+the)?|risk\s+of\s+loss)\s+(?:[\w'’-]+\s+){0,5}?"
# a policy about a contingent future event in the present tense: MSCD 3.334 and 3.361 take will
# leads: If ... , the Term ends; also In case, Should, Where and Were Beta to (the lead itself is another check's business). A
# fixed date after the lead word (Upon July 1, 2028, the Annual Fee increases) is a stated time, so the present tense is right (3.334)
CONTINGENT_LEAD = re.compile(r"(?:^|[.;:]\s+)[\s#*_>]*(?:\(?[A-Za-z0-9]{1,4}[.)]\s+)?(?:If|When|Whenever|Unless|Upon|Once|In\s+case|Should|Where|Were\s+[A-Z][\w'’-]*\s+to|In\s+the\s+event\s+that|To\s+the\s+extent\s+that)\b(?!\s+" + MONTH + r"\s+\d)[^.;:]{3,200}?,\s+(?:then\s+)?" + POLICY_SUBJ + r"\b" + POLICY_VERB + r"\b")
# a trailing condition: the named subjects (this agreement, the Term, title) fire on their own; the generic subject (group subj:
# a determiner or possessive plus up to 5 words, "the Software lapses if", "A Statement of Work becomes binding when") is
# checked in house_checks, which drops a party or person subject (the Supplier applies the discount when ...), a relative clause
# (the amount that becomes due after ...) and a condition that belongs to a later clause (..., and if Beta fails ...)
CONTINGENT_TAIL = re.compile(r"\b(?:this\s+(?:agreement|lease|license|release|option|right|offer|waiver|consent|amendment|Term|term)|the\s+(?:Term|Option|license|right|termination|cancellation|rescission|Effective\s+Time|Closing|Renewal\s+Term|Initial\s+Term|risk\s+of\s+loss|title)|risk\s+of\s+loss|title\s+to\s+[\w\s]{1,30}?|no\s+(?:installment|payment|amount)\b[\w\s]{0,40}?|(?P<subj>(?:the|this|that|a|an|each|any|no|\w[\w'’-]*['’]s)(?:\s+(?!(?:before|after|until|when|whenever|if|unless|once|while|than|later|earlier)\b)[\w'’-]+){0,8}?))\s+" + POLICY_VERB + r"\b(?=[^.;]{0,140}\b(?:if|when|whenever|unless|upon|once|after|before|until)\s+(?!(?:" + MONTH + r"|the\s+(?:date|day)\s+of\s+this|\d)))", re.I)
# a contingent event stated as a restrictive relative clause or a qualifier on the subject (MSCD 3.334; table 8 example [8-1]: Any attempted transfer of Shares in violation of this agreement will be void):
# "Any Transfer that this agreement does not permit is void"; "An assignment made without Lender's consent is of no effect"
CONTINGENT_REL = re.compile(r"\b(?:Any|An|A|Each)\s+(?:attempted\s+|purported\s+)?(?:[A-Z]?[\w'’-]+\s+){0,3}?(?:that|which|made|given|effected|entered\s+into|purportedly\s+made)\s+(?:[\w'’-]+\s+){0,12}?(?:(?:does\s+not|do\s+not|doesn't|fails?\s+to)\s+(?:[\w'’-]+\s+){1,4}?|(?:breaches|violates|contravenes)\s+(?:[\w'’-]+\s+){1,5}?|in\s+(?:violation|breach)\s+of\s+(?:[\w'’-]+\s+){1,4}?|without\s+(?:[\w'’-]+\s+){1,5}?(?:consent|approval)\s+)"
                            r"(?P<verb>is\s+(?:void|voidable|ineffective|invalid|of\s+no\s+(?:force\s+(?:or|and)\s+)?effect|null\s+and\s+void))\b")
# a negative subject with shall; the subject may hold 1 comma-set clause (No change order, unless Acme signs it, shall bind Acme),
# but a 2nd independent clause (No Default exists, and Acme shall pay) is not that subject
NEG_SUBJ_SHALL = re.compile(r"(?:^\s*(?:\(?[A-Za-z0-9]{1,4}[.)]\s*|\d+(?:\.\d+)+\.?\s*|[IVXLC]+\.\s*)?|[.;:][*_]*\s+|,\s+(?:and|or|but)\s+|\b(?:that|and|or|but)\s+)(Neither|No|None of|Nobody|No one|Nothing)\b(?!\s+(?:later|earlier|more|less|fewer|sooner)\s+than)[^.;:,]{0,100}?"
                            r"(?:,\s+(?!(?:and|or|but|nor)\b)[^.;:,]{1,60},\s+[^.;:,]{0,40}?)?\bshall\b(?!\s+not)", re.I)  # any comma-set phrase inside the subject (Neither party, during the Term, shall); a 2nd clause that starts with a conjunction is not the subject
SHOULD = re.compile(r"\bshould\b(?!-)", re.I)  # not inside a hyphenated defined term (Should-Cost Model)
SERIAL_1 = re.compile(r"\b((?:[\w'’-]+,\s+)+)([\w'’-]+)\s+(?:and|or|and/or)\s+(?=[\w'’])")
DET = r"(?:the|its|their|his|her|any|all|each|such|our|your)"
LIST_LEADS = {'shall', 'may', 'must', 'will', 'can', 'not', 'to', 'the', 'its', 'their', 'his', 'her', 'our', 'your', 'and', 'or', 'for', 'of', 'including', 'by', 'all', 'each',
              'in', 'on', 'with', 'from', 'as', 'than', 'when', 'if', 'once', 'any', 'every', 'between', 'among'}
# items of up to 3 words when the extra words are capitalized (the Base Rent, the Additional Rent and all other sums); "in its sole discretion, the Lender and the Borrower" stays clear
SERIAL_2 = re.compile(r"\b((?:" + DET + r"\s+(?:[A-Z][\w'’-]*\s+){0,2}[\w'’-]+,\s+)+)(" + DET + r"\s+(?:[A-Z][\w'’-]*\s+){0,2}[\w'’-]+)\s+(?:and|or|and/or)\s+(?=" + DET + r"\b)")
US_STATES = ("Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|"
             "Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|Ohio|Oklahoma|"
             "Oregon|Pennsylvania|Tennessee|Texas|Utah|Vermont|Virginia|Washington|Wisconsin|Wyoming")


SERIAL_Q = re.compile(r"((?:[\"“][A-Z][^\"”]{0,40}?,?[\"”],?\s+){2,})(?:and|or)\s+[\"“]")


SERIAL_V = re.compile(r"\b(?:shall|must|will|may|to)\s+(?:not\s+)?[a-z]+\s+(?:" + DET + r"|a|an)\s+[^,;:.()]{1,40}?,\s+[a-z]+\s+(?:" + DET + r"|a|an)\s+[^,;:.()]{1,40}?\s+(?:and|or)\s+(?=[a-z]+\s+(?:" + DET + r"|a|an)\b)")


# an aside opened by a comma after the modal (Lender may, without notice to Guarantor and without affecting ...,): its closing
# comma is not a list comma. "Acme shall copy, modify and distribute" has no preposition after the comma and stays a list
MODAL_ASIDE = re.compile(r"\b(?:shall|may|must|will)(?:\s+not)?\s*,\s+(?:with|without|in|at|on|for|by|upon|after|before|subject|notwithstanding|except|to)\b[^,;:]*$")


# an opening adverbial phrase, with or without a leading adverb or an enumerator (Immediately after the Closing, Seller and Buyer ...),
# ends at the sentence's 1st comma: the 2 names after it are a compound subject, not a list
OPENERS = (r"(?:after|before|if|when|once|upon|on|until|unless|during|following|except|notwithstanding|in|at|by|for|from|under|within|without|"
           r"subject\s+to|as\s+of|prior\s+to|subsequent\s+to|pursuant\s+to|throughout|pending|effective|concurrently\s+with|simultaneously\s+with|"
           r"with\s+respect\s+to|regarding|concerning|beginning|commencing|starting|absent|despite|to)")
OPENING_PHRASE = re.compile(r"(?:^|[.;:]\s+)(?:\(?[A-Za-z0-9]{1,4}[.)]\s+)?(?:[A-Za-z]+ly\s+)?" + OPENERS + r"\b[^,;:]*$", re.I)


def serial_lists(t):
    # lists of 3 or more items with no serial comma; items alike in case (a clause boundary mixes them:
    # If Acme defaults, Beta and Gamma may ...), with no digits (dates, amounts) and no place names
    out = []
    for rx in (SERIAL_1, SERIAL_2):
        for m in rx.finditer(t):
            items = [x.strip() for x in m.group(1).split(',') if x.strip()] + [m.group(2)]
            heads = [x.split()[-1] for x in items]
            if any(re.search(r"\d", x) for x in items) or re.fullmatch(US_STATES, heads[-1]):
                continue
            if len({h[0].isupper() for h in heads}) > 1:
                continue
            before = t[:m.start()]
            if heads[0][0].isupper() and (not before.strip() or re.search(r"[.;:]\s*$|^\s*(?:\(?[A-Za-z0-9]{1,4}[.)]\s*)$", before)) \
                    and (items[0] in SENT_STARTERS or items[0].lower().endswith('ly') or len(items) < 3 and items[0] in ('Accordingly', 'However', 'Therefore', 'Thereafter')):
                continue  # However, Acme and Beta ...: an opening word, not a list
            if any(w in ('shall', 'may', 'will', 'must', 'is', 'are') for x in items for w in x.split()):
                continue
            if any(x.split()[0].lower() in ('with', 'without', 'in', 'at', 'on', 'for', 'by', 'from', 'to', 'under', 'of', 'into', 'upon', 'as', 'than') for x in items[1:]):
                continue  # the position, with or without accommodation: a phrase after the comma, not a list item
            if heads[0][0].isupper() and re.search(r"\b(?:Department|Office|Bureau|Division|Ministry|Board|Commission|Committee|Council|Agency|Institute|School|College|University|Society|Association|Federation|Union)\s+(?:of|for|on)\s+$", before):
                continue  # Department of Agriculture, Trade and Consumer Protection: a proper name, punctuated as its owner does
            if rx is SERIAL_1 and len(items) == 2:
                # 1 comma: a list only when the 1st item follows a verb, a negative, an article or a possessive
                # (shall not copy, modify or ...; the employees, agents and ...); otherwise the comma usually
                # ends a phrase (in its sole discretion, accept or reject; at any time, with or without cause)
                prev = re.search(r"([\w'’]+)\s+$", before)
                pw = prev.group(1).lower() if prev else ''
                at_start = not before.strip() or re.search(r"[.;:]\s*$", before)
                if not (pw in LIST_LEADS or pw.endswith(("'s", "’s")) or at_start and items[0][0].isupper() and items[0] not in SENT_STARTERS):
                    continue
                if OPENING_PHRASE.search(before.rstrip()):
                    continue  # After the Closing, Seller and Owner ...; Prior to the Closing, Seller and Buyer ...: the 1st comma ends an opening phrase, not a list item
                if MODAL_ASIDE.search(before):
                    continue  # Lender may, without notice ... and without affecting its rights, extend or renew: the 1st comma closes an aside after the modal
                if re.search(r",\s+(?!(?:and|or|but|nor)\s+$)\w+\s+$", before):
                    continue  # Beta shall, on request, inspect and test ...: a phrase set off by commas, not a list
                if re.search(r"\b(?:at|in|for|on|under|with|upon|by)\s+(?:its|their|his|her|our|your|the|such|any)\s+(?:\w+\s+)?$", before + ' '):
                    continue  # at its expense, defend and ...; in its discretion, accept or ...: a phrase, not a list
            nxt = re.match(r"([\w'’-]+(?:\s+[\w'’-]+)?)\s*,", t[m.end():])
            if len(items) == 2 and nxt:
                pair = f"{m.group(2)} {m.group(0).split()[-1]} {nxt.group(1)}"
                if re.fullmatch(r"\w+ly\s+(?:or|and)\s+\w+ly|alone\s+or\s+(?:jointly\s+)?with\s+others|jointly\s+(?:or|and)\s+severally|"
                                r"with\s+or\s+without\s+\w+|(\w+)\s+(?:or|and)\s+(?:non-?|un|in)\1", pair, re.I):
                    continue  # a pair set off by commas (engage, directly or indirectly, in; repairs, structural and nonstructural, to): an aside, not a list
            out.append(m)
    for m in SERIAL_V.finditer(t):
        if not any(o.start() <= m.start() < o.end() for o in out):
            out.append(m)
    for m in SERIAL_Q.finditer(t):
        last = re.findall(r"[\"“][^\"”]*[\"”],?", m.group(1))[-1]
        if not last.endswith(',') and not last.endswith(',”') and not last.endswith(',"') and not re.search(r",[\"”]$", last):
            out.append(m)
    return out
ONCE = re.compile(r"(?<!\bat )(?<!\bAt )(?<!\bleast )(?<!\bthan )(?<!\bonly )(?<!\bexactly )(?<!\bjust )(?<!\bmost )\bonce\b(?!\s+(?:before|again|more)\b)(?!\s+(?:a|per|every|each)\s+(?:day|week|month|quarter|year|calendar))(?!\s+(?:in|during|for)\s+(?:each|any|every|a)\b)(?!\s+or\s+(?:more|twice))", re.I)
WHEN_COND = re.compile(r"(?:^|[.;:]\s+|\(\w{1,4}\)\s+)When\b")
AMP = re.compile(r"&")
XREF = re.compile(r"(?:\b(?:[Ss]ections?|[Aa]rticles?|[Cc]lauses?|[Pp]aragraphs?|[Ss]ubsections?)|§)\s*(?:[IVXLC]+|\d+|[A-Z](?=[.\s,;)]))(?:[.-][\dA-Za-z]+)*(?:\s*\([a-z0-9]{1,4}\))*(?![\w.-]*(?:\s*\([a-z0-9]{1,4}\))*(?:\s+[(\[][^)\]]{1,60}[)\]])?\s+of\s+(?:the\s+)?(?:[A-Z]|\d+\s+U\.S\.C|title))")
REL_XREF = re.compile(r"(?<!\bsign )(?<!\bcountersign )(?<!\bsigning )\b(?:above|below|the foregoing|hereof|hereunder|herein|hereinafter|aforesaid)\b(?!-)", re.I)  # "sign below" in a letter agreement points at the signature line, not a provision
ATT_LOWER = re.compile(r"\b(schedule|exhibit|annex|appendix)\s+(?:[A-Z]\b|\d+\b)")
ATT_HERETO = re.compile(r"\b(?:Schedules?|Exhibits?|schedules?|exhibits?)\b[^.;]{0,40}?\b(?:hereto|attached hereto|to this (?:[Aa]greement|[Ll]ease|[Ss]ublease|[Cc]ontract|[Aa]mendment|[Ll]icen[cs]e|[Nn]ote|[Gg]uarant(?:y|ee)|[Dd]eed|[Ss]ubcontract|[Ii]ndenture|[Pp]lan))\b|\battached hereto\b")  # the document's own noun (Schedule A to this lease), not only agreement
ATT_ON = re.compile(r"\b(?:on|at) (?:Schedule|schedule)\s+[A-Z0-9]")  # on Schedule A, set out at Schedule B: in Schedule A; "the fee stated in Schedule A" stays clear
ATT_PART = re.compile(r"\b(?:form(?:s|ing)?|constitut(?:e|es|ing)|made)\s+(?:a\s+|an\s+)?(?:integral\s+)?part of this (?:agreement|lease|sublease|contract|amendment|licen[cs]e|note|guarant(?:y|ee)|deed|subcontract|indenture|plan)\b|\bincorporated (?:herein )?by reference\b", re.I)  # the document's own noun; "forms part of the Premises" stays clear
ATT_QUOTE = re.compile(r"\b(?:Schedule|Exhibit)\s+[\"“][A-Z0-9]+[\"”]")
DMY = re.compile(r"\b\d{1,2}\s+" + MONTH + r"\s+\d{4}\b")
DATE_WORDS = re.compile(r"\b(?:(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+)?(" + '|'.join(MONTHS) + r")\s+(\d{1,2}),\s+(\d{4})\b")
TERM_NOTICE = re.compile(r"\b(?:terminate|determine)\s+(?:this\s+[A-Za-z]+|the\s+[A-Z][\w ]{0,30}?|it)\s+(?:at\s+any\s+time\s+)?(?:upon|by\s+giving(?:\s+to)?(?:\s+(?:the\s+other(?:\s+party)?|[A-Z]\w+))?|with)\s+(?:at\s+least\s+|not\s+less\s+than\s+)?(?:\d+|[a-z]+(?:[- ][a-z]+)?)(?:\s+\(\d+\))?\s+(?:days|months|Business\s+Days|business\s+days)['’]?\s+(?:prior\s+|advance\s+|written\s+|prior\s+written\s+)?notice")
# 2/3/2027 and the year-first 2027/01/05; a month or day never exceeds 31 and a year has 2 or 4 digits, so 24/7/365 (a service level)
# and a version number 2.0/3 are not dates
NUMDATE = re.compile(r"\b(?:0?[1-9]|[12]\d|3[01])/(?:0?[1-9]|[12]\d|3[01])/(?:\d{4}|\d{2})(?![\d/])|(?<![\w./-])(?:19|20)\d{2}/(?:0?[1-9]|1[0-2])/(?:0?[1-9]|[12]\d|3[01])(?![\w/])")
THIS_DAY = re.compile(r"\b(?:this|the)\s+\S+\s+day\s+of\s+(?:" + MONTH + r"|[_\s]{2,})|\bthis\s+\S+\s+day\s+of\b", re.I)
HEADINGS_CLAUSE = re.compile(r"\bheadings?\b[^.]{0,120}\b(?:convenience|reference|guidance|identification|navigation)\b", re.I)  # the clause headings are for guidance only
TYPED_NUM = re.compile(r"^\s*(?:\d+\.\d+(?:\.\d+)*\.?|\(\d+\)|\([ivx]+\)|\([a-z]\)|[IVX]+\.|[A-Z]\.|\d+\.)\s+")


# House rule 11: no article before a defined party name (MSCD 2.105 and 6.63 differ).
PARTY_DEFAULT = {'Company', 'Buyer', 'Seller', 'Purchaser', 'Supplier', 'Vendor', 'Contractor', 'Subcontractor', 'Consultant',
                 'Customer', 'Client', 'Employee', 'Executive', 'Employer', 'Licensor', 'Licensee', 'Landlord', 'Tenant', 'Lender',
                 'Borrower', 'Guarantor', 'Provider', 'Sponsor', 'University', 'Distributor', 'Manufacturer', 'Lessor', 'Lessee',
                 'Reseller', 'Subscriber', 'User', 'Owner', 'Agency', 'Developer', 'Publisher', 'Author', 'Artist', 'Holder',
                 'Investor', 'Member'}  # role labels keep the (house rule 11)
# the same nouns in capitals, for the conspicuous-text variants in data/phrase-variants.json (their {party_caps} placeholder):
# 1 list, so the 2 can't drift apart
PARTY_CAPS = '|'.join(sorted((t.upper() for t in PARTY_DEFAULT), key=len, reverse=True)) + r"|EACH\s+PARTY|EITHER\s+PARTY|THE\s+PARTIES|BOTH\s+PARTIES"
# generic party subjects for the will / must / may not checks (the contract's own party names and collective terms join them)
PARTY_PHRASES = {'each party', 'Each party', 'Each Party', 'either party', 'Either party', 'Either Party', 'the parties', 'The parties',
                 'the Parties', 'The Parties', 'both parties', 'Both parties', 'Both Parties', 'each of the parties', 'Each of the parties'}
WHOSE = None  # 'blake' or 'other-side' when known (--whose)
PARTY_TERMS = set()  # run() fills this from the document's own party definitions
PARTY_COLLECTIVE = set()  # collective names for the parties ("each, a Co-Owner"): parties for subject analysis, not for house rule 11
RECITAL_IDX = set()  # paragraphs between the introductory clause and "agree as follows": recitals state background, so will there is a future event, not a duty
EXHIBIT_PARTIES = set()  # the parties of a form attached as an exhibit (an escrow agreement the escrow agent signs), while run() lints that exhibit
NONPARTY_NAMED = set()  # people and entities the contract names and defines outside the introductory clause (a subsidiary, an owner): not parties
AGENT_ROLES = {'Inspector', 'Appraiser', 'Accountant', 'Auditor', 'Architect', 'Engineer', 'Surveyor', 'Liquidator', 'Receiver',
               'Arbitrator', 'Mediator', 'Expert', 'Escrow Agent', 'Paying Agent', 'Property Manager', 'Independent Accountant', 'Title Company'}
# roles that are sometimes a party (a Manager who signs an operating agreement): left to the reviewer, who checks the signature blocks
NOT_PARTY = {'Agreement', 'Effective Date', 'Parties', 'Party'}
# the quotation marks a definition may use: straight or curly, double or single (the term's characters exclude QC below)
QO = r"[\"“‘']"
QC = r"[\"”’']"
QT = r"(?:[^\"”’']|['’](?=[A-Za-z]))"  # 1 character inside a quoted term: an apostrophe inside a word (Tenant’s Share) is not the closing mark
DEF_PAREN = re.compile(r"\(\s*(?:the\s+|a\s+|an\s+)?\**" + QO + r"\**([A-Z][\w-]*(?:\s+[A-Z][\w-]*){0,2})\**" + QC + r"\**\s*\)")
ROLE_DEF = re.compile(r"[\"\u201c]((?:Disclosing|Receiving|Indemnifying|Indemnified|Defaulting|Nondefaulting|Terminating|Notifying) Party)[\"\u201d]")
ATTRIBUTIVE = ('employee|employees|board|stock|shares|securities|plan|plans|group|products|product|property|personnel|policy|policies|'
               'entity|entities|subsidiary|subsidiaries|affiliate|affiliates|premises|facility|facilities|data|information|account|'
               'accounts|system|systems|site|sites|benefit|benefits|parties|party|representative|representatives|indemnitees')
ROLE_PAREN = re.compile(r"\(\s*in\s+(?:that|its|such|this)\s+(?:role|capacity),\s+(?:the\s+)?\**" + QO + r"\**([A-Z][\w-]*(?:\s+[A-Z][\w-]*){0,2})\**" + QC + r"\**\s*\)")
DEF_WITH_ARTICLE = re.compile(r"\(\s*the\s+" + QO + r"\**([A-Z][\w-]*(?:\s+[A-Z][\w-]*){0,2})\**" + QC + r"\s*\)")


def front(paras, n=15, min_words=12):
    """The first n substantive paragraphs: where the introductory clause lives. A cover page, a table of
    contents or spacer paragraphs would otherwise push it past a fixed window of 15 paragraphs."""
    return [p for p in paras if len(p['text'].split()) >= min_words][:n]


def intro_like(paras):
    """The indexes of short paragraphs near the front that read like an introductory clause whatever their length:
    between or among plus a defined party (This agreement is between ACME LLC ("Acme") and BETA INC. ("Beta"), 10 words)."""
    return {p['idx'] for p in front(paras, INTRO_WINDOW, INTRO_MIN_WORDS) if BETWEEN_AMONG.search(p['text']) and DEF_PAREN.search(p['text'])}


def intro_candidates(paras, n=15):
    """The paragraphs the introductory clause may sit in, in document order: front(paras, n) plus intro_like(paras)."""
    ids = {p['idx'] for p in front(paras, n)} | intro_like(paras)
    return [p for p in paras if p['idx'] in ids]


PARTIES_ENOUGH = 2  # an introductory clause that defines 2 parties is complete: a later "between" names another agreement's parties


def party_terms(paras):
    found = set()
    cont_i = None  # index of the next paragraph when the introductory clause lists each party in its own paragraph (the list item ends with ":", ";", or "; and")
    front_ids = {p['idx'] for p in intro_candidates(paras)}
    for p in paras:
        continues = cont_i is not None and p['idx'] == cont_i
        if p['idx'] not in front_ids and not continues:
            continue  # a short list item ("Beta Partners LP, a Texas limited partnership ("Beta"); and") is below front()'s word floor but continues the introductory clause
        if len(found) >= PARTIES_ENOUGH and not continues:
            break  # a recital's "a loan agreement ... between Borrower and Lender" defines a nonparty (Borrower), not a party
        before = len(found)
        if BETWEEN_AMONG.search(p['text']) or continues:
            for m in DEF_PAREN.finditer(p['text']):
                prev = p['text'][max(0, m.start() - 80):m.start()].rstrip(' ,')
                if re.search(r"(?:corporation|company|partnership|association|cooperative|trust|bank|credit\s+union|union|foundation|society|fund|university|college|hospital|district|individual|organization|LLC|L\.L\.C\.|Inc\.|Co\.|Corp\.|LP|L\.P\.|LLP|PLLC|N\.A\.)$", prev, re.I) \
                        or re.search(r"(?:^|\b(?:between|and|;)\s+)[A-Z][\w.&'’ -]{1,60}$", prev) or re.search(r"\b[A-Z][\w'’-]+$", prev) and not re.search(r"\b(?:the|a|an|its|their)\s+(?:[A-Z][\w'’-]+\s+){0,4}[A-Z][\w'’-]+$", prev) \
                        or re.search(r"\b(?:as|in\s+(?:its|their|that)\s+(?:capacity|role)\s+as)\s+(?:an?\s+)?[a-z][\w-]*(?:\s+[a-z][\w-]*){0,3}$", prev):
                    found.add(m.group(1))  # a party: a name or an entity description just before the parenthetical, not "the Desert Basin Water Authority (the "Authority")"; or a role after the name (Fifth Third Bank, in its capacity as escrow agent (the "Escrow Agent"))
            for m in ROLE_PAREN.finditer(p['text']):
                found.add(m.group(1))  # Volunteer State Trust Company, as escrow agent (in that role, the "Escrow Agent")
            if re.search(r"(?::|;|;\s*and|,\s*and)\s*$", p['text'].rstrip()) and (len(found) > before or BETWEEN_AMONG.search(p['text'])):
                cont_i = p['idx'] + 1
    for p in ([] if found else intro_candidates(paras, 4)):  # no "between" clause (purchase terms): "Saltmarsh Provisions Co., a Virginia corporation ("Buyer"), issues to a supplier ("Seller")"
        for m in DEF_PAREN.finditer(p['text']):
            if re.search(r"(?:corporation|company|partnership|association|cooperative|individual|LLC|Inc\.|Co\.|supplier|vendor|customer|seller|buyer|contractor|licensee|licensor)\W{0,4}$", p['text'][max(0, m.start() - 60):m.start()], re.I):
                found.add(m.group(1))
    doc_word = re.compile(r"(?:Agreement|Note|Lease|Plan|Guaranty|Amendment|Policy|Lawsuit|Action|Litigation|Proceeding|Arbitration|Claims?|Dispute|Settlement|Case|Matter|Complaint|Transaction|Acquisition|Merger|Financing|Offering|Deal|Investment|Date|Period|Term|Property|Premises|Assets|Business|Shares|Units|Price|Loan|Loans|Parts|Products|Goods|Services|Software|Equipment|Work|Materials|Deliverables|Data|Information|Collateral|Facility|Project|Study|Trademarks?|Marks|Territory|Fee|Fees|Building|Land|Site|Suite|Hotel|Store|Center|Plant|Warehouse)$")  # a thing named in the introductory clause (the building at 100 Main Street (the "Building")) is not a party
    return {t for t in found if t not in NOT_PARTY and not ROLE_DEF.fullmatch('"' + t + '"') and not doc_word.search(t)}


TAIL_SHARE = 0.5  # the signature blocks sit in the back half of the document's non-blank paragraphs


def document_shape(paras):
    """Where the contract's parts are, computed once per document: intro (the paragraph of the introductory clause, with
    between/among and a defined party), lead_in (the paragraph with "agree as follows", or None), lead (the lead-in, or
    the 1st article after the intro: house style has no lead-in, so the recitals end there), attachments (the index of the
    1st attachment heading, or len(paras)), tail (the paragraph index where the signature-block search starts), and
    tail_text (the text from there on)."""
    by_idx = {p['idx']: p for p in paras}
    intro_i = next((p['idx'] for p in intro_candidates(paras) if BETWEEN_AMONG.search(p['text'])
                    and (DEF_PAREN.search(p['text']) or p['text'].rstrip().endswith(':') and p['idx'] + 1 in by_idx and DEF_PAREN.search(by_idx[p['idx'] + 1]['text']))), None)  # "is among the following parties:" with each party in its own paragraph
    attachments = next((p['idx'] for p in paras if EXHIBIT_HEAD.match(p['text'])), len(paras))
    lead_in = next((p['idx'] for p in paras if LEAD_IN.search(p['text'])), None)
    # the lead-in or the 1st article after the intro, anywhere before the attachments (a cover page and a table of contents can push
    # it past any fixed window; an attached form's own lead-in isn't this contract's)
    lead_i = next((p['idx'] for p in paras if p['idx'] < attachments and (LEAD_IN.search(p['text'])
                   or (intro_i is not None and p['idx'] > intro_i
                       and re.match(r"\s*(?:#+\s*)?(?:(?:ARTICLE|Article)\s+)?(?:[IVX]+|\d+)[.:]?\s+[A-Z]", ((p.get('auto_label') or '') + ' ' + p['text']).strip())))), None)
    body = [p for p in paras if p['text'].strip()]
    tail_i = body[int(len(body) * TAIL_SHARE)]['idx'] if body else 0
    return {'intro': intro_i, 'lead_in': lead_in, 'lead': lead_i, 'attachments': attachments, 'tail': tail_i,
            'tail_text': ' '.join(p['text'] for p in paras if p['idx'] >= tail_i)}


def nonparty_named(paras, parties, shape, defs):
    """Names the contract defines for a person or an entity outside the introductory clause (in the recitals or the body):
    Brazos Valve Holdings, Inc., a Texas corporation ("Brazos"); John Hollis ("Owner"). They don't sign, so they aren't
    parties, unless a signature block names them. defs: definitions(paras)."""
    tail = shape['tail_text']
    by_idx = {p['idx']: p for p in paras}
    found, lead_done = set(), set()

    def signs(term):
        return re.search(r"(?:^|\s)" + re.escape(term.upper()) + r"\s*:", tail) or re.search(r"\bBy:[^\n]{0,60}\b" + re.escape(term) + r"\b", tail)
    for term, words, pidx, st, en, kind in defs:
        p = by_idx[pidx]
        if pidx == shape['intro'] or EXHIBIT_HEAD.match(p['text']) or term in parties or term in NOT_PARTY:
            continue
        if kind == 'integrated' and re.fullmatch(r"[A-Z][\w-]*(?:\s+[A-Z][\w-]*){0,2}", term):
            paren = p['text'].rfind('(', 0, st)
            if paren < 0 or not re.fullmatch(r"\(\s*(?:the\s+|a\s+|an\s+)?\**" + QO + r"\**", p['text'][paren:st]):
                continue  # not a plain parenthetical definition ((that position, the "Title") names a thing)
            prev = p['text'][max(0, paren - 90):paren].rstrip(' ,')
            entity = re.search(r"(?:corporation|company|partnership|association|trust|LLC|L\.L\.C\.|Inc\.|Corp\.|LP|L\.P\.|LLP|PLLC|an individual|subsidiary|affiliate)\W{0,3}$", prev, re.I)
            person = re.search(r"(?:^|[\s,(])(?:Mr\.|Ms\.|Dr\.)?\s*[A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+(?:-[A-Z][a-z]+)?$", prev)
            if (entity or person) and not signs(term):
                found.add(term)
        elif kind == 'autonomous' and re.fullmatch(r"[A-Z][^\"”]{0,40}", term) and p['idx'] not in lead_done:
            dm = AUTON.match(def_text(p['text']))  # the paragraph's leading definition, with means (not includes)
            if not dm or dm.group(1).strip().rstrip(',.;:') != term or not dm.group(0).rstrip().endswith('means'):
                continue
            lead_done.add(p['idx'])
            body = words[:160]
            if (re.search(r"\b(?:" + ENTITY_WORDS + r")\b", body) or re.match(r"\s*[A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+\s*(?:,|$)", body)) and not signs(term):
                found.add(term)  # "Brazos" means Brazos Valve & Fitting Co., a Texas corporation that Halvorsen wholly owns
    return found


# the person a role term names at the start of its definition: "Manager" means Dale Marchetti, or any successor ...;
# Dale Marchetti (the "Manager"). A thing ("Manager Fee" means the fee ...) starts with a lowercase word and isn't read
NAME_AT_START = re.compile(r"\s*((?:Mr\.|Ms\.|Dr\.)?\s*[A-Z][\w.&'’-]*(?:\s+(?:[A-Z]\.|[A-Z][\w.&'’-]*)){1,5})(?=\s*(?:,|\(|;|\.|$|\bor\b|\band\b))")
NAME_BEFORE = re.compile(r"((?:[A-Z][\w.&'’-]*\s+){1,5}[A-Z][\w.&'’-]*)\s*,?\s*$")


def signs_individually(name, tail):
    """True when a signature line in the tail names this person signing for themselves: the name right after the line
    (______\nDale Marchetti), not after By: (By: ______ Name: Dale Marchetti signs for an entity, in a representative role)."""
    for m in re.finditer(r"(By:\s*)?_{3,}\s*(?:Name:\s*)?" + re.escape(name) + r"\b", tail):
        if not m.group(1):
            return True
    return False


def signing_roles(paras, parties, shape, defs):
    """Role terms whose holder signs the contract in their own name ("Manager" means Dale Marchetti, who signs as a Member):
    a party for the subject checks (the Manager shall is a duty that binds a signer), though not a party name for house rule 11
    (the Manager keeps its article). A role whose holder signs only for an entity (By: ... Name: Dale Marchetti) stays a nonparty."""
    tail, by_idx, found = shape['tail_text'], {p['idx']: p for p in paras}, set()
    for term, words, pidx, st, en, kind in defs:
        if term in parties or not re.fullmatch(r"[A-Z][\w-]*(?:\s+[A-Z][\w-]*){0,2}", term):
            continue
        if kind == 'autonomous':
            t = by_idx[pidx]['text']
            mm = re.match(r"\W*means\b", t[en:])
            name = NAME_AT_START.match(t[en + mm.end():]) if mm else None
        elif kind == 'integrated':
            t = by_idx[pidx]['text']
            name = NAME_BEFORE.search(t[max(0, t.rfind('(', 0, st) - 80):max(0, t.rfind('(', 0, st))])
        else:
            continue
        if name and signs_individually(name.group(1).strip(), tail):
            found |= _forms(term)
    return found


ENTITY_WORDS = r"corporation|limited\s+liability\s+company|limited\s+partnership|general\s+partnership|partnership|LLC|L\.L\.C|Inc|Corp|Co|LLP|PLLC|N\.A"


# the parenthetical that names the parties together: (each, a "Party," and collectively, the "Parties"); every quoted term in
# it counts, and a comma typed inside the closing quotation mark isn't part of the term. "(the "Effective Date")" has no lead word
COLLECTIVE_PAREN = re.compile(r"\((?:each|collectively|together|individually)\b[^()]{0,120}\)")
COLLECTIVE_TERM = re.compile(QO + r"\**([A-Z][\w-]*(?:\s+[A-Z][\w-]*){0,2}),?\**" + QC)


def party_collective(paras):
    found = set()
    for p in intro_candidates(paras):
        if BETWEEN_AMONG.search(p['text']):
            for paren in COLLECTIVE_PAREN.finditer(p['text']):
                for m in COLLECTIVE_TERM.finditer(paren.group(0)):
                    found |= _forms(m.group(1))
    return found


# a signatory named by its role with no defined term: HARBOR TITLE LLC, a Tennessee limited liability company, as escrow agent.
# The role must follow an entity description or suffix (not "the Loan Agreement, as amended") and end the clause
SIGNATORY_ROLE = re.compile(r",\s+(?:as|in\s+(?:its|their|that)\s+(?:capacity|role)\s+as)\s+(?:an?\s+)?([a-z][\w-]*(?:\s+[a-z][\w-]*){0,3}?)\s*(?=[.;,)]|\(|$|\s+(?:and|or)\b)")
ENTITY_BEFORE = re.compile(r"(?:corporation|company|partnership|association|cooperative|trust|bank|credit\s+union|union|foundation|society|fund|university|college|hospital|district|individual|organization|LLC|L\.L\.C\.|Inc\.|Co\.|Corp\.|LP|L\.P\.|LLP|PLLC|N\.A\.)$", re.I)


def signatory_roles(paras):
    """The roles the introductory clause gives a signatory without a defined term (as escrow agent), as written and in title case:
    that signatory is a party, so "the escrow agent shall" states a duty (MSCD 3.89). They join PARTY_COLLECTIVE, not PARTY_TERMS:
    a role label keeps its article (house rule 11), and the missing defined term is the inventory's finding (MSCD 2.91)."""
    found = set()
    for p in intro_candidates(paras):
        if not BETWEEN_AMONG.search(p['text']):
            continue
        for m in SIGNATORY_ROLE.finditer(p['text']):
            if ENTITY_BEFORE.search(p['text'][max(0, m.start() - 60):m.start()].rstrip(' ,')):
                role = m.group(1)
                found |= {role, ' '.join(w.capitalize() for w in role.split())}
    return found


def party_article_re(terms):
    alts = '|'.join(sorted(map(re.escape, terms), key=len, reverse=True))
    return re.compile(r"\b[Tt]he\s+(" + alts + r")\b(?!\s+[A-Z0-9])(?!\s+(?:" + ATTRIBUTIVE + r")\b)")  # not the Company 401(k) Plan


# Signature phrases: high-precision words and phrases MSCD tells you to change. Reported as direct findings,
# with the fix and the paragraph, so a reviewer doesn't have to dig them out of the rule triggers.
AGENCY_NAME = re.compile(r"(?:Internal Revenue Service|Securities and Exchange Commission|Food and Drug Administration|Environmental Protection Agency|"
                         r"(?:United States )?Postal Service|(?:United States )?Patent and Trademark Office|(?:United States )?Copyright Office|Federal Trade Commission|"
                         r"Social Security Administration|Small Business Administration|Equal Employment Opportunity Commission|National Labor Relations Board|"
                         r"Federal Communications Commission|Occupational Safety and Health Administration|Federal Aviation Administration|Federal Reserve(?: Board)?|"
                         r"Department of (?:[A-Z][a-z]+(?: and [A-Z][a-z]+)?)|Secretary of State|Attorney General|Internal Revenue Code|Uniform Commercial Code|United States)")  # names of agencies and codes, not undefined terms
ANCHOR_STOP = {'Section', 'Sections', 'Article', 'Articles', 'Party', 'Parties', 'Person', 'Persons', 'Business', 'Day', 'Days', 'Agreement'}  # capitalized words in a definition that name no external reality (see inventory(): circular definitions)
SIGNATURE_SRC = [  # (pattern, check, severity, message, rule ids); SIGNATURE below compiles it
    (r"\band/or\b", 'and-or', 2, 'and/or: write "X or Y or both" or "1 or both of X and Y"; in an obligation, state the duty and the choice separately (MSCD 11.90-11.95).', ['R-11.90-no-and-or']),
    (r"\b(?:reasonable\s+)?best\s+(?:efforts|endeavou?rs)\b", 'efforts', 1, 'best efforts: write reasonable efforts; best invites a reader to find extra meaning (MSCD 8.91; 8.134).', ['R-8.91-best-efforts-ambiguous']),
    (r"\bgood[- ]faith\s+efforts\b", 'efforts', 2, 'good-faith efforts: write reasonable efforts; good faith brings in the implied duty of good faith (MSCD 8.38).', ['R-8.38-good-faith-efforts']),
    (r"\bdiligent\s+efforts\b", 'efforts', 2, 'diligent efforts: write reasonable efforts; don\'t mix diligence into an efforts standard (MSCD 8.153; 8.134).', ['R-8.153-no-mixed-standards']),
    (r"\b(?:all|every|very)\s+(?:reasonable|best)\s+efforts?\b", 'efforts', 2, 'all, every or very in an efforts standard: delete it and write reasonable efforts (MSCD 8.15).', ['R-8.15-no-very-all-every']),
    (r"\bcommercially\s+reasonable\s+(?:efforts|endeavou?rs)\b|\breasonable\s+commercial\s+(?:efforts|endeavou?rs)\b", 'efforts', 2, 'commercially reasonable efforts: delete commercially and write reasonable efforts (MSCD 8.14).', ['R-8.14-no-commercially']),
    (r"\buse\s+(?:its|their|his|her)\s+(?:reasonable|best)\s+efforts\b", 'efforts', 3, 'Write use reasonable efforts, without the pronoun (MSCD 8.17).', ['R-8.17-use-verb-use']),
    # the doublet, whole or split by its addressee (represents to Acme and warrants); "represents Acme in the arbitration and warrants" has no "to"
    (r"\brepresents?\s+(?:to\s+(?:[A-Z][\w-]*(?:\s+[A-Z][\w-]*)?|the\s+other\s+part(?:y|ies)|each\s+other)\s+)?and\s+warrants?\b|\bwarrants?\s+(?:to\s+(?:[A-Z][\w-]*(?:\s+[A-Z][\w-]*)?|the\s+other\s+part(?:y|ies)|each\s+other)\s+)?and\s+represents?\b"
     r"|\bREPRESENTS?\s+(?:TO\s+(?:[A-Z][\w-]*(?:\s+[A-Z][\w-]*)?|THE\s+OTHER\s+PART(?:Y|IES)|EACH\s+OTHER)\s+)?AND\s+WARRANTS?\b|\bWARRANTS?\s+(?:TO\s+(?:[A-Z][\w-]*(?:\s+[A-Z][\w-]*)?|THE\s+OTHER\s+PART(?:Y|IES)|EACH\s+OTHER)\s+)?AND\s+REPRESENTS?\b", 'represents-warrants', 2, "represents and warrants: on Blake's draft use states (3.457); on the other side's draft keep it and suggest the remedies-neutral sentence in a comment (3.459-3.463).", ['R-3.457-use-states']),
    (r"\(this\s+[\"“]\*{0,2}[A-Z][a-z]+\*{0,2}[\"”]\)|^[\s*_#]*(?:THIS|This)\s+(?:[\w-]+\s+){0,6}?(?:" + "|".join(N + r"\s+\(the\s+[\"“]\*{0,2}" + n + r"\*{0,2}[\"”]\)" for n in ("Agreement", "Amendment", "Addendum", "Lease", "Sublease", "Note", "Guaranty", "Guarantee", "Release", "License", "Licence", "Deed", "Subcontract", "Contract") for N in (n, n.upper())) + ")", 'this-agreement-term', 3, 'Don\'t define this agreement as a term; delete the definition and write this agreement (or this amendment, this lease) in lowercase throughout (MSCD 2.123).', ['R-2.123-no-this-agreement-term']),
    (r"(?<!\bstays\s)(?<!\bstay\s)(?<!\bremains\s)(?<!\bremain\s)(?<!\bis\s)(?<!\bare\s)(?<!\bbe\s)(?<!\bwas\s)(?<!\bwere\s)\b[Tt]he\s+same\b(?=\s*(?:[,.;:)]|$)|\s+(?:to|by|in|on|at|for|and|or|within|if|when|from|with|under|until|without)\b)", 'same-pronoun', 3, 'same as a pronoun: write it, them or their, or repeat the noun (MSCD 13.760).', ['R-13.760-same-pronoun']),
    (r"\b(?:he or she|she or he|his or her|her or his|him or her|her or him|he/she|she/he|s/he|his/her|him/her|himself or herself|herself or himself|him-?\s?or\s?herself|himself/herself|he, she,? or (?:it|they)|his, her,? or (?:its|their)|him, her,? or (?:it|them))\b", 'singular-they', 2, 'House rule 10: singular they (they, their, them), not he or she.', []),
    (r"\b[Ff]orm\s+(?:of|in)\s+Schedule\s+[A-Z0-9]+\b|\bSCHEDULE\s+[A-Z0-9]+\s*[-–—:]\s*FORM\s+OF\b|\bSchedule\s+[A-Z0-9]+\s*[-–—:]\s*Form\s+of\b", 'attachment-classification', 2, 'A form of document is a stand-alone document, so it belongs in an exhibit (Exhibit 1), not a schedule (house rule 6; MSCD 5.72-5.73).', []),
    (r"\bWHEREAS\b|\bWITNESSETH\b|\bNOW,?\s+THEREFORE\b|\b[Ww]hereas\b", 'archaic', 3, 'Traditional recitals or lead-in: delete WHEREAS, WITNESSETH and NOW, THEREFORE; put any background in plain sentences (MSCD 2.137; 2.165).', ['R-2.137-no-witnesseth', 'R-1.4-no-archaisms']),
    (r"\bgood\s+and\s+valuable\s+consideration\b|\breceipt\s+and\s+sufficiency\s+of\s+which\b", 'archaic', 3, 'Recital of consideration: delete it (MSCD 2.165; 2.188).', ['R-2.188-good-and-valuable']),
    (r"\bIN\s+WITNESS\s+WHEREOF\b|\b[Ii]n\s+[Ww]itness\s+[Ww]hereof\b", 'archaic', 3, "Traditional concluding clause: use MSCD's concluding clause (5.13-5.17).", ['R-5.17-traditional-concluding-clause']),
    (r"\b[Hh]ere(?:of|in|under|inafter|inabove|inbefore|with|to|after|tofore)\b|\b[Ww]here(?:in|of|under)\b(?!-)", 'archaic', 3, 'Archaic here-word: write this agreement, refer by heading, or delete it (MSCD 1.4). Keep hereby only in language of performance.', ['R-1.4-no-archaisms']),
    (r"\b[Ss]aid\s+(?=[A-Z][a-z]|(?:agreement|party|parties|premises|equipment|property|goods|notice|amount|payment|sum)\b)", 'archaic', 3, 'said as a pointing word: use the or this (MSCD 13.758).', ['R-13.758-said']),
    (r"\b(?:hereby\s+)?(?:agrees?|undertakes?|covenants?)\s+(?:and\s+agrees?\s+)?to\b(?!\s+(?:the|this|that|such|any|its|these|those|a|an|in\s+writing|otherwise)\b)(?<!\bas the parties agree to)(?<!\bthe parties agree to)", 'agrees-to', 2, 'agrees to / undertakes to / covenants to: state the obligation with shall (MSCD 3.125, 3.129).', ['R-3.125-no-agrees-to-obligation']),
    (r"\b(?:in|at)\s+(?:its|their|his|her|the\s+\w+['’]s)\s+(?:sole|absolute|sole\s+and\s+absolute|own)\s+discretion\b", 'sole-discretion', 2, 'sole discretion: delete it; if it addresses the implied duty of good faith, address that directly (MSCD 3.249-3.269).', ['R-3.249-no-sole-discretion']),
    (r"\b[Tt]ime\s+is\s+of\s+the\s+essence\b", 'time-is-of-the-essence', 2, 'Time is of the essence: delete it; say what happens when a deadline is missed (MSCD 13.884).', ['R-13.884-time-of-the-essence']),
    (r"\bhold\s+(?:[\w'’-]+\s+){0,6}?harmless\b", 'doublet', 2, 'hold harmless adds nothing to indemnify; write indemnify. Defend is a separate obligation: keep it if the parties intend it (MSCD 13.440).', ['R-13.440-hold-harmless']),
    (r"\bterms\s+and\s+conditions\b", 'doublet', 3, 'terms and conditions: write terms (MSCD 13.860).', ['R-13.860-terms-and-conditions']),
    (r"\bincluding,?\s+(?:but\s+not\s+limited\s+to|without\s+limitation)\b", 'doublet', 3, 'including but not limited to / including without limitation: write including (MSCD 13.359-13.393).', ['R-13.361-without-limitation']),
    (r"\b(?:null\s+and\s+void|due\s+and\s+payable|any\s+and\s+all|each\s+and\s+every|cease\s+and\s+desist|full\s+force\s+and\s+effect|sole\s+and\s+exclusive|true\s+and\s+correct|true,?\s+correct,?\s+and\s+complete|true\s+and\s+complete|fit\s+and\s+proper|free\s+and\s+clear)\b", 'doublet', 3, 'Redundant string: use 1 word (MSCD 1.36-1.49).', ['R-1.43-prune-synonym-strings']),
    (r"\barising\s+(?:out\s+of|under)\s+or\s+(?:relating|related|in\s+connection\s+with)\b|\barising\s+out\s+of\s+or\s+in\s+connection\s+with\b|\brelating\s+to\s+or\s+arising\s+out\s+of\b", 'arising-out-of', 2, 'arising out of or relating to: write arising out of, or state the connection you mean (MSCD 13.41-13.54).', ['R-13.41-arising-out-of-or-relating-to']),
    (r"\b[Ff]or\s+the\s+avoidance\s+of\s+doubt\b", 'throat-clearing', 3, 'for the avoidance of doubt: delete it, or fix the ambiguity it signals (MSCD 13.312).', ['R-13.312-for-the-avoidance-of-doubt']),
    (r"\b[Ii]t\s+is\s+(?:expressly\s+|further\s+|hereby\s+|mutually\s+)?(?:understood|agreed|acknowledged)(?:\s+and\s+(?:agreed|understood|acknowledged))?\s+(?:by\s+the\s+parties\s+)?that\b|\b[Tt]he\s+parties\s+(?:hereby\s+)?(?:acknowledge|agree|understand)\s+and\s+(?:agree|acknowledge|understand)\s+that\b", 'throat-clearing', 2, 'Throat-clearing: delete the lead-in and state the rule (MSCD 3.27).', ['R-3.27-throat-clearing']),
    (r"\bsuccessors\s+and\s+(?:permitted\s+)?assignees\b", 'usage', 3, 'successors and assignees: the usage is successors and assigns (MSCD 15.24), and usually delete the provision; the law already binds successors (2.95).', ['R-15.24-rule-successors-assigns']),
    (r"\bsuccessors\s+and\s+(?:permitted\s+)?assigns\b", 'successors-assigns', 3, 'successors and assigns: usually delete; the law already binds successors (MSCD 2.95; 15.24).', ['R-15.24-rule-successors-assigns']),
    (r"\b(?:shall|will)\s+survive\b(?!\s+(?:[\w'’]+\s+){0,3}(?:death|incompetence|incapacity|disability|dissolution|bankruptcy))|\bsurvives?\s+(?:the\s+)?(?:termination|expiration)\b", 'survival', 2, 'Survival provision: delete it; give each obligation that outlasts the agreement its own duration (MSCD 13.822-13.831).', ['R-13.822-survival']),
    # within N days, within a period of N days; a within ... after is the next entry's wording fix
    (r"\b[Ww]ithin\s+(?:a\s+period\s+of\s+)?(?:\d+|[a-z]+(?:\s+\(\d+\))?)\s+(?:calendar\s+|business\s+|Business\s+)?(?:days?|Days?|months?|years?|weeks?|hours?)\b(?!\s+(?:after|following)\b)", 'time-ambiguity', 1, 'within: unclear whether the period runs before the event, after it or both; write no later than [N] days after [event], or during the [N] days before (MSCD 10.69-10.71).', ['R-10.69-within-ambiguity']),
    (r"\b[Ww]ithin\s+(?:a\s+period\s+of\s+)?(?:\d+|[a-z]+(?:\s+\(\d+\))?)\s+(?:calendar\s+|business\s+|Business\s+)?(?:days?|Days?|months?|years?|weeks?|hours?)\b\s+(?:after|following)\b", 'within-after', 3, 'within [N] days after: MSCD says not to use within; write no later than [N] days after (10.69-10.71). After already sets the direction, so this is a wording fix, not an ambiguity.', ['R-10.69-within-ambiguity']),
    (r"\bby\s+(?:" + MONTH + r"\s+\d{1,2}(?:,\s*\d{4})?|\d{1,2}/\d{1,2}/\d{2,4}|the\s+\d{1,2}(?:st|nd|rd|th)\s+(?:Business\s+|business\s+)?day\s+of|(?:that|the|this|its|such|each)\s+(?:(?:[\w-]+\s+)?(?:deadline|date|day|anniversary|Date)|(?:[A-Z][\w-]*\s+){2,3}Date)\b(?!\s+(?:of|on|that|which)\s+(?:this|the)\s+(?:agreement|lease|notice)\b)(?!\s+(?:of|on)\b))", 'time-ambiguity', 2, 'by [date or deadline]: courts split on whether the stated day is included (MSCD 10.25). Offer both, no later than [that day] (day included) and before [that day] (day excluded), and ask which the parties intend (MSCD 10.23-10.25; 13.608).', ['R-10.23-inclusive-exclusive-ambiguity']),
    (r"\b[Ff]rom\s+(?:and\s+including\s+)?" + MONTH + r"\s+\d{1,2},?\s*(?:\d{4}\s+)?(?:to|until|till|through)\s+(?!and\s+including)", 'time-ambiguity', 2, 'from [date] to/until [date]: unclear whether each end date is included; say so ("from and including ... to and including ...") (MSCD 10.23).', ['R-10.23-inclusive-exclusive-ambiguity']),
    (r"\b[Bb]etween\s+" + MONTH + r"\s+\d{1,2}(?:,\s*\d{4})?\s+and\s+", 'time-ambiguity', 2, 'between [date] and [date]: unclear whether the end dates are included; say so (MSCD 10.23).', ['R-10.23-inclusive-exclusive-ambiguity']),
    # the adverb and the adjective (prompt written notice); "prompts" (a verb, or a software prompt) and the defined term Prompt stay clear
    (r"\bprompt(?:ly)?\b(?!\s+(?:engineering|template|text|window|box)\b)", 'vagueness', 3, 'prompt (or promptly) is vague, and a court may read it as immediately; state a number of days if timing matters (MSCD 10.114; 7.46-7.47).', ['R-10.114-promptly-equals-immediately']),
    (r"\b(?:[Tt]hird|3rd)[- ][Pp]art(?:y|ies)\b(?![- ][Bb]eneficiar)(?![- ][Ll]ogistics)(?![- ][Aa]dministrator)", 'usage', 3, 'third party: write Person, any Person other than a party, or a defined Nonparty (MSCD 13.875).', ['R-13.875-third-party']),
    # signature_checks exempts this entry inside quoted text (a statute's words), keyed on its rule id
    (r"\b(?:duly\s+)?execut(?:e|es|ed|ing|ion)\b(?!\s+(?i:(?:of\s+)?(?:the\s+|its\s+|their\s+|all\s+|any\s+)?(?:work|services?|tasks?|project|duties|obligations|deliverables|plan|protocol|testing))\b)(?!\s+(?:a|an)\s+(?!copy|counterpart|document|written|separate|new\s+agreement|joinder|release|certificate|deed|note|amendment|instrument)[a-z])", 'archaic', 3, 'execute for signing: write sign (MSCD 5.7).', ['R-5.7-signing-not-executing']),
    (r"\bshall\s+be\s+entitled\s+to\b|\bshall\s+have\s+the\s+right\s+to\b", 'category-shall', 2, 'shall be entitled to / shall have the right to: for discretion write may (MSCD 3.206); if another party owes the thing, state that party\'s duty with shall (3.169; 3.288); is entitled to plus a noun stays only when no party owes it (3.147).', ['R-3.206-use-may']),
    (r"\bshall\s+be\s+(?:governed|construed|interpreted)\s+(?:by|in\s+accordance)\b|\bshall\s+(?:be\s+)?deemed\b|\bshall\s+(?:commence|begin|continue|terminate|expire|end|accrue)\b(?=\s*(?:[,.;:)]|$)|\s+(?:on|at|upon|when|whenever|if|unless|in|until|for|automatically|immediately|with|after|before|no\s+later|as\s+of|and|or|without|by|effective|under|while|once|daily|monthly)\b)|\bshall\s+be\s+(?:effective|valid|binding|void|enforceable|final)\b|\bshall\s+be\s+for\s+(?:a|the)\s+(?:term|period)\b|\bshall\s+be\s+(?:equal\s+to\s+)?(?:\$\s?\d|\d+(?:\.\d+)?\s*(?:%|percent\b))|\bshall\s+(?:remain|be)\s+in\s+(?:full\s+)?(?:force|effect)\b", 'category-shall', 2, 'shall with no duty on the subject: language of policy. Pick the tense by MSCD 3.334: the present tense for a policy in force on signing or at a fixed date (Tennessee law governs this agreement; the Term ends on May 31, 2030); will for a policy tied to an event that may not happen or whose timing is uncertain (this agreement will terminate when ...; will be void) (MSCD 3.98; 3.334; 3.335).', ['R-3.98-shall-future-time']),
]
LOAD_ERRORS = []  # a data file that couldn't be read: main() stops with exit 2, and the self-test fails


def _rule_sev():
    """Each rule's severity, from data/rules.jsonl. A bad or missing file is recorded in LOAD_ERRORS (main stops), not hidden."""
    try:
        return {r['id']: r['severity'] for r in load_records() if 'severity' in r}
    except InputError as e:
        LOAD_ERRORS.append(str(e))
        return {}
_SEV = _rule_sev()
SIGNATURE = [(re.compile(p), c, s, m, r) for p, c, s, m, r in SIGNATURE_SRC]


TOA = 'Term of art used in its everyday sense; the contract may also use it in its legal sense, and 1 word carries 1 meaning (MSCD 1.57). '

EXTRA = [
    # not the correlative such X as Y (such additional amounts as Schedule A states): up to 4 words before as, none of them a verb;
    # such consent before the Closing, and such insurance must name Customer as an additional insured (a verb before as), stay
    (re.compile(r"(?<![Aa]ny )(?<![Nn]o )(?<!ANY )(?<!NO )(?<![Ee]ach )(?<!\dst )(?<!\dnd )(?<!\drd )(?<!\dth )(?<!other )\bsuch\b(?!\s+as\b)"
                r"(?!\s+(?:(?!(?:shall|must|may|will|is|are|was|were|has|have|had|does|do|did|can|cannot|should|would)\b)[\w'’-]+\s+){1,4}as\b)(?=\s+[A-Za-z])", re.I), 'such-pointing', 3, 'Such as a pointing word: use the, this, that, these or those (13.816-13.818); keep such only for "of this kind".', []),
    (re.compile(r"(?<![,(])(?<!\b(?:in|on|of|to|by|at))(?<!\bfor)(?<!\b(?:from|with|upon|into))(?<!\b(?:under|after))(?<!\bthrough)\s+which\b"), 'restrictive-which', 2, 'Which without a comma introduces a restrictive clause: use that (12.44; 12.53-12.56).', []),
    (re.compile(r"\b" + COND_LEAD + r"\b[^,.;:]{0,90}?\bshall\b", re.I), 'shall-in-condition', 1, 'Shall in a conditional clause: use the present tense (3.358-3.360).', ['R-3.358-conditional-present-tense']),
    # present-tense discretion disguises that R-3.206 lists (is at liberty to, has the right to); "Seller states that it has the right to sell" is a statement of fact (the exclusion below)
    (re.compile(r"\b(?:is|are)\s+(?:at\s+liberty|free)\s+to\b|\b(?:has|have|retains?)\s+the\s+(?:right|option)(?:,\s+but\s+not\s+the\s+(?:obligation|duty),)?\s+to\b", re.I), 'category-may', 2,
     'Is at liberty to / is free to / has the right to / retains the right to: write may for discretion (MSCD 3.206); if it hides the other party\'s duty, state that duty with shall (3.168-3.171).', ['R-3.206-use-may']),
    (re.compile(r"\b(?:is|are|shall be|will be)\s+entitled(?:,\s+[^,.;]{1,40},)?\s+to\b", re.I), 'is-entitled-to', 2, 'Is entitled to: if it hides another party\'s duty, state the duty with shall (3.168-3.171; 3.288-3.291); for discretion use may (3.206).', ['R-3.169-no-is-entitled-to-obligation']),
    (re.compile(r"\b(?:Attachment|Appendix|Annex|Addendum|ATTACHMENT|APPENDIX|ANNEX|ADDENDUM)\s+(?:[A-Z]|\d+)\b(?!\s+(?:to|of)\s+(?:the\s+)?(?!this\b)[A-Z0-9])"), 'generic-attachment-label', 2, 'Generic attachment label. House rule: Schedule A (lettered; information the body refers to, such as lists and disclosures) or Exhibit 1 (numbered; a stand-alone document, such as a form of agreement). Decide which it is and update every reference (MSCD 5.72-5.74; attachments.md).', ['R-5.74-generic-attachment-term']),
    (re.compile(r"\b(?:Exhibit|EXHIBIT)\s+[A-Z]\b(?!\.[A-Za-z0-9])"), 'attachment-scheme', 2, 'Lettered exhibit. House rule 6: first decide what it holds: a stand-alone document (a form of agreement, certificate or notice) is an exhibit, numbered (Exhibit 1); information the body refers to (a list, a price table, a disclosure) is a schedule, lettered (Schedule A). Relabel it, and update every reference (MSCD 5.72-5.83).', []),
    (re.compile(r"\b(?:Schedules?|SCHEDULES?)\s+\d+(?:\.\d+)*\b"), 'attachment-scheme', 2, 'Numbered schedule. House rule 6: schedules take letters (Schedule A), exhibits take numbers (Exhibit 1); relabel and update every reference (MSCD 5.80-5.83 differs).', []),
    (re.compile(r"\b(?:[Tt]he|[Aa]ny|[Ee]ach|[Aa]ll|[Ee]very|[Aa]n?)\s+(?:[A-Z][\w-]*|[a-z]+)\s+(?:[a-z]+ed(?=\s+by\b)|given|paid|made|sent|delivered|received|issued|provided|described|specified|listed|referred|contemplated|required|owned|held|granted|incurred|used|stated|set forth|identified|included|attached|signed|imposed|issued|filed|obtained|collected|charged|purchased|sold|performed)\s+(?:by|under|in|to|on|at|for|from|pursuant|with|as|before|after)\b(?<!made for)"), 'reduced-passive', 3, 'Possible reduced passive (a past participle after a noun, short for "that is given ..."). House rule 1: recast in the active if a clean form exists ("the notice that Acme gives under ..."); otherwise leave it.', ['R-3.15-active-voice']),
    (re.compile(r"\b(?:for|of|reimburse|pay|repay|bear|all|any|on|to)\s+(?!(?:the|a|an|any|each|all|every|its|their|his|her)\s)[a-z]+\s+[a-z]{3,}s\s+(?:incurred|paid|made|given|sent|received|issued|provided|delivered|imposed|charged|suffered|sustained|caused|owed|held|owned|granted|performed)\s+by\b"), 'reduced-passive', 3, 'Possible reduced passive (a past participle after a noun, short for "that are incurred by ..."). House rule 1: recast in the active if a clean form exists ("the travel expenses that the Consultant incurs"); otherwise leave it.', ['R-3.15-active-voice']),
    # Terms of art used in their everyday sense: an elaboration of MSCD 1.57 (one word, one meaning). Idea suggested by a file Blake supplied; patterns written fresh.
    (re.compile(r"\bexecut(?:e|es|ed|ing)\s+(?:the\s+|its\s+|their\s+|all\s+|any\s+)?(?:work|services?|tasks?|project|duties|obligations|deliverables|plan|protocol|testing)\b|\bexecution\s+of\s+(?:the\s+|its\s+|their\s+|all\s+|any\s+)?(?:work|services?|tasks?|project|duties|obligations|deliverables|plan|protocol|testing)\b", re.I), 'term-of-art', 2, TOA + 'Execute here means perform; write perform. For signing, MSCD uses sign, not execute (5.7).', ['R-1.57-one-word-one-meaning', 'R-5.7-signing-not-executing']),
    (re.compile(r"\bexecut(?:e|es)\s+(?:a|an)\s+(?!copy|counterpart|document|written|separate|new\s+agreement|joinder|release|certificate|deed|note|amendment|instrument)[a-z]+"), 'term-of-art', 2, TOA + 'Execute here means perform; write perform. For signing, MSCD uses sign, not execute (5.7).', ['R-1.57-one-word-one-meaning']),
    (re.compile(r"\b(?:[Ii]f|[Ww]hen|[Oo]nce|[Aa]fter|[Uu]nless|[Uu]ntil)\s+(?:the\s+)?(?:[A-Z][\w-]+|either party|a party|any party|it|they)\s+notices\b"), 'term-of-art', 2, TOA + 'Notices here means observes, but notice is the formal communication under the notices provision. Write discovers or becomes aware of.', ['R-1.57-one-word-one-meaning']),
    (re.compile(r"\b(?:circumstances|conditions|results|events|volumes?)\s+warrant\b|\bwarrants?\s+(?:additional|further|immediate|special|extra)\b", re.I), 'term-of-art', 2, TOA + 'Warrant here means justify; write justify or require.', ['R-1.57-one-word-one-meaning']),
    (re.compile(r"\brepresent(?:s|ed)?\s+(?:approximately\s+|about\s+)?\d+(?:\.\d+)?\s*(?:%|percent)", re.I), 'term-of-art', 2, TOA + 'Represents here means constitutes; write is, equals or constitutes.', ['R-1.57-one-word-one-meaning']),
    (re.compile(r"\b(?:work|project|job|task|new|each)\s+assignments?\b|\bassign(?:s|ed|ing)?\s+(?:\d+\s+)?(?:qualified\s+|licensed\s+|certified\s+)?(?:personnel|staff|employees|technicians|workers|consultants|individuals|a team)\b", re.I), 'term-of-art', 2, TOA + 'Assign here means allocate work or staff, but assignment is the transfer of rights that an assignment provision restricts. Write designate, task, or work order.', ['R-1.57-one-word-one-meaning']),
    (re.compile(r"\bfor\s+(?:the\s+)?(?:[A-Z][\w-]*['\u2019]s|its|their|further|careful|prompt)\s+consideration\b|\bunder consideration\b|\btake\s+into\s+consideration\b", re.I), 'term-of-art', 2, TOA + 'Consideration here means review, but consideration is also the bargained-for exchange. Write review or evaluation.', ['R-1.57-one-word-one-meaning']),
    (re.compile(r"\brelease\s+(?:the\s+)?(?:payment|funds)\b", re.I), 'term-of-art', 2, TOA + 'Release here means pay, but release is also the giving up of claims. Write pay or disburse (escrow agreements conventionally say release; keep it there).', ['R-1.57-one-word-one-meaning']),
    (re.compile(r"\b(?:strategic|business|vendor|preferred|trusted|channel|campus)\s+partners?\b", re.I), 'term-of-art', 2, TOA + 'Partner can suggest a legal partnership. Name the actual relationship (contractor, supplier, collaborator).', ['R-1.57-one-word-one-meaning']),
]

WORDY = {  # MSCD 17.19 table (Wordy -> Better); "once" dropped from "at the time that" per the once/if rider
    'at that point in time': 'then', 'at the place where': 'where', 'at the time at which': 'when', 'at the time that': 'when',
    'at the time when': 'when', 'by means of': 'by', 'by reason of': 'because of', 'by virtue of the fact that': 'because',
    'commensurate with': 'equal to, appropriate for', 'despite the fact that': 'although', 'due to the fact that': 'because',
    'during such time as': 'while, during', 'during the course of': 'while', 'following the conclusion of': 'after',
    'for the purpose of': 'to [verb]', 'in combination with': 'with', 'in furtherance of': 'furthering, to advance',
    'in lieu of': 'instead of', 'in order for': 'so', 'in order that': 'so', 'in order to': 'to', 'in the course of': 'while, during',
    'in the event of': 'if', 'in the event that': 'if', 'is binding upon': 'binds', 'is unable to': 'cannot (for inability; for a prohibition use shall not, MSCD 3.321)', 'per annum': 'a year, per year, annually',
    'period of time': 'period, time', 'previous to': 'before', 'prior to': 'before', 'pursuant to': 'under, in accordance with, authorized by',
    'set forth in': 'stated in, in', 'subsequent to': 'after', 'under the provisions of': 'under', 'until such time as': 'until',
    'with the exception of': 'except for'}
WORDY_RE = re.compile(r"\b(" + '|'.join(re.escape(k) for k in sorted(WORDY, key=len, reverse=True)) + r")\b", re.I)
# not the verb after an auxiliary (Seller has provided that information): only the proviso
PROVISO = re.compile(r"(?<!\bhas\s)(?<!\bhave\s)(?<!\bhad\s)(?<!\bnot\s)(?<!\bbeen\s)(?<!\bhaving\s)\bprovided,?\s+(?:however|further|also)?,?\s*that\b", re.I)

STOP = set('shall will may must if and or the a an any each all every which such before after date day days within '
           'notice party parties agreement section article clause in on of to for by with as that this these those '
           'is are be been being not no including include includes means term terms closing'.split())


def phrase_rules():
    """Second trigger channel: literal trigger words from the database (for rules whose regex misses them)."""
    recs, ov = load_records(), load_overrides()
    superseded = superseded_ids(ov)
    out = []
    for r in recs:
        if r['status'] == 'proposal' or r['id'] in superseded:
            continue
        words = [w.strip().lower() for w in (r.get('trigger') or {}).get('words') or [] if w and '...' not in w and '[' not in w]
        words = [w for w in words if (' ' in w and not all(x in STOP for x in w.split())) or (len(w) > 5 and w not in STOP)]
        if words:
            out.append((r, re.compile(r"\b(?:" + '|'.join(re.escape(w) for w in sorted(set(words), key=len, reverse=True)) + r")\b", re.I)))
    return out


# Subject analysis for shall and will: a duty needs a party as the subject (MSCD 3.89). With a thing as the subject,
# shall is language of policy written in the wrong form (3.98; 3.335); with a nonparty person, a duty binds no one (3.89; 3.154).
SUBJ_CUT = re.compile(r"\s+[a-z]+ing\b|\s+(?:of|in|under|to|for|on|from|with|by|at|between|among|during|after|before|within|without|regarding|concerning|"
                      r"relating|arising|pursuant|as|that|which|who|whom|whose|titled|entitled|named|called|described|listed|set|"
                      r"issued|made|given|delivered|received|referred|required|provided|specified|contemplated|identified)\b|\s*\(|\s*,")
SUBJ_DET = re.compile(r"^(?:the|this|that|these|those|each|every|any|all|such|its|their|his|her|our|a|an|both)$", re.I)
SUBJ_COND = re.compile(r"^(?:if|unless|when|whenever|where|wherever|until|once|while|whether|because|although|provided|so\s+long\s+as|"
                       r"to\s+the\s+extent|in\s+the\s+event|except|notwithstanding|subject|upon|on|after|before|during|for|in|at|with|by|as|from|under)\b", re.I)
THING_HEADS = set("""agreement amendment term period fee fees price payment payments amount amounts rent interest rate rates notice notices
    title risk closing license licenses provision provisions section sections article articles limitation limitations remedy remedies
    determination decision award deliverable deliverables unit units product products goods shares share warrant option options software
    services work equipment premises property date deposit plan policy loan note collateral obligation obligations right rights restriction
    restrictions covenant covenants representation representations warranty warranties indemnity indemnities schedule exhibit statement
    report budget milestone royalty royalties cap basket escrow account facility territory specifications documentation information data
    materials marks trademarks patents release laws law consent approval waiver failure delay breach termination expiration assignment
    transfer meeting vote quorum election lease order orders invoice invoices tax taxes insurance coverage purchase sale sales proceeds
    commission commissions bonus salary compensation benefits capital contribution distribution distributions liability liabilities cost
    costs expense expenses damages loss losses claim claims dispute disputes arbitration hearing venue jurisdiction validity effect
    effectiveness noncompetition nonsolicitation confidentiality exclusivity commitment commitments guaranty guarantee security lien liens
    certificate deed contract contracts subcontract
    completion delivery possession occupancy commencement performance acceptance settlement repayment prepayment installation
    construction vesting funding disbursement maturity renewal extension suspension cancellation""".split())  # event nouns too: Final Completion shall occur
PERSONISH = set("""party parties person persons individual entity entities company corporation member members manager managers shareholder
    shareholders stockholder stockholders partner partners holder holders investor investors officer officers director directors board
    committee administrator representative representatives owner owners optionee participant participants grantee executive indemnitee
    indemnitees licensee licensor buyer seller tenant landlord contractor consultant employer lender borrower guarantor purchaser
    supplier customer client provider distributor agent agents affiliate affiliates subsidiary subsidiaries it they he she who one other
    others either neither none nobody anyone everyone someone we you i
    counsel attorney attorneys surety sureties bank banks depositary registrar government authority authorities agency agencies""".split())  # nonparty actors with no agent suffix
THING_ER = set("""order orders matter matters letter letters offer offers transfer transfers waiver waivers disclaimer disclaimers register registers
    rider riders cover covers character characters center centers quarter quarters number numbers paper papers power powers water computer computers
    server servers printer printers meter meters container containers trailer trailers charter charters answer answers chapter chapters remainder
    reminder reminders tender tenders schedule warrant warrants grant grants covenant covenants restaurant restaurants plant plants list lists""".split())


def agent_noun(head):
    """True for a lowercase noun that names someone who can act (person, manufacturer, transferee, consultant), by the PERSONISH list or an
    agent ending; False for a thing whose name shares the ending (order, waiver, transfer, warrant)."""
    h = head.lower().split('-')[-1]  # sub-distributors, co-lessees: the noun after the prefix decides (a hyphenated thing, a follow-up order, stays a thing)
    return h in PERSONISH or (h not in THING_ER and bool(re.fullmatch(r"[a-z]+(?:er|or|ee|ant|ist|ian|eer)s?", h)))


NONPARTY_HEADS = re.compile(r"^(?:(?:Escrow|Paying|Collateral|Exchange|Transfer|Disbursing|Settlement|Closing|Rights)\s+Agent|"
                            r"(?:[Ii]ndependent\s+)?(?:[Aa]rbitrators?|[Aa]rbitral\s+[Tt]ribunal|[Mm]ediators?|[Aa]ccountants?|[Aa]uditors?|[Aa]ppraisers?|[Ee]xperts?)|"
                            r"Title\s+Company|[Tt]itle\s+(?:company|insurer)|Escrow\s+Holder|[Ss]ub-?licensees?|[Ss]ub-?contractors?|[Ss]pouse|"
                            r"[Ii]nvitees?|[Gg]uests?|[Vv]isitors?|[Ee]mployees|[Pp]ersonnel|[Ss]taff|[Ee]nd\s+[Uu]sers?|[Cc]ourt|[Jj]udge|[Rr]eferee|"
                            r"[Ss]urveyor|[Ii]nspector|[Tt]rustee|[Ss]ub-?agents?|[Vv]olunteers?|(?:[a-z]+\s+)?[Aa]dministrators?|(?:[A-Z][\w-]*\s+)?[Uu]sers?|[Ss]uppliers?|"
                            r"[Mm]embers?\s+(?:[A-Z][\w-]*\s+)*(?:Personnel|Staff|Team))$")
PARTY_STATE = [  # shall with a party subject that still imposes no clean duty (will forms are in data/phrase-variants.json, with their exceptions)
    # shall be liable, shall remain liable, shall be solely (or jointly and severally) liable: all policy; "is liable" stays clear
    (re.compile(r"\bshall\s+(?:not\s+|in\s+no\s+event\s+|at\s+no\s+time\s+)?(?:be|remain)\s+(?:held\s+|solely\s+|fully\s+|jointly\s+and\s+severally\s+|personally\s+)?liable\b", re.I),
     'shall be liable / shall not be liable: language of policy. In a matrix clause after if, when, or unless, or for a liability that arises only if an event happens, write will be liable (MSCD 3.361; 3.334); for a standing allocation in force on signing (No Member is liable for the Company\'s debts), is liable (MSCD 3.98; 3.335).', ['R-3.98-shall-future-time'], 2),
    (re.compile(r"\bshall\s+be\s+(?:solely\s+)?responsible\s+for\b", re.I),
     'shall be responsible for: state the duty with shall and a verb (Customer shall pay all freight charges); keep is responsible for only for a duty owed to a nonparty, such as taxes (MSCD 3.144-3.146).', ['R-3.144-no-is-responsible-for'], 2),
    (re.compile(r"\bshall\s+be\s+(?:obligated|obliged)\s+to\b", re.I),
     'shall be obligated to: write shall (MSCD 3.130).', ['R-3.130-no-shall-be-obligated'], 3),
    (re.compile(r"\bshall\s+be\s+required\s+to\b", re.I),
     'shall be required to: write shall for the duty (MSCD 3.130; 3.89).', ['R-3.89-shall-duty'], 2),
    (re.compile(r"\bshall\s+not\s+be\s+required\s+to\b", re.I),
     'shall not be required to: write is not required to; in a matrix clause after if or unless, will not be required to (MSCD 3.292; 3.296; 3.361; house rule 1 keeps it).', ['R-3.292-is-not-required-to'], 2),
    (re.compile(r"\bshall\s+be\s+(?:permitted|allowed|authorized|authorised)\s+to\b", re.I),
     'shall be permitted to: write may for discretion (MSCD 3.206).', ['R-3.206-use-may'], 2),
    (re.compile(r"\bshall\s+not\s+be\s+(?:permitted|allowed|authorized|authorised)\s+to\b", re.I),
     'shall not be permitted to: write shall not for a prohibition (MSCD 3.307).', ['R-3.307-no-may-not'], 2),
    (re.compile(r"\bshall\s+(?:have\s+no|not\s+have\s+any|be\s+under\s+no)\s+(?:obligation|duty)\s+to\b", re.I),
     'shall have no obligation to: write is not required to; in a matrix clause after if or unless, will not be required to (MSCD 3.292; 3.296; 3.361).', ['R-3.292-is-not-required-to'], 2),
    (re.compile(r"\bshall\s+(?:have\s+no|not\s+have\s+any)\s+(?:liability|responsibility)\b", re.I),
     'shall have no liability: language of policy; write is not liable for a standing allocation, or will not be liable where the liability would arise only if an event happens (MSCD 3.98; 3.334; 3.361).', ['R-3.98-shall-future-time'], 2),
    (re.compile(r"\bshall\s+be\s+(?:subject\s+to|bound\s+by)\b", re.I),
     'shall be subject to / shall be bound by: language of policy; write is subject to or is bound by (MSCD 3.98; 3.335).', ['R-3.98-shall-future-time'], 2),
    (re.compile(r"\bshall\s+be\s+(?:at\s+liberty|free)\s+to\b", re.I),
     'shall be at liberty to / shall be free to: write may for discretion (MSCD 3.206).', ['R-3.206-use-may'], 2),
    (re.compile(r"\bshall\s+have\s+the\s+(?:right|option|power|authority|ability)(?:\s*,\s*but\s+not\s+the\s+(?:obligation|duty)\s*,)?\s+to\b", re.I),
     'shall have the right (or option) to: write may for discretion (MSCD 3.206).', ['R-3.206-use-may'], 2),
]
REF_SUBJ = re.compile(r"^(?:there|it)$", re.I)
DIGIT_START = re.compile(r"(?:^|(?<=[.!?]\s)|(?<=[.!?]\s\s)|(?<=[.!?][\"”)]\s)|(?<=[.!?][\"”)]\s\s))\$?\d[\d,]*(?:\.\d+)?%?(?=\s+[A-Za-z(])(?!\s+(?:U\.S\.C|C\.F\.R|Fed|F\.\d|Stat)\b)")
# shall cause (or its disguises: see to it that, make sure that) for people the party doesn't control; shall cause its
# Subsidiaries (an instrumentality) is not in the noun list and stays clear
SHALL_CAUSE_UNCONTROLLED = re.compile(r"\b(?:shall|will|must)\s+(?:cause(?:\s+that)?|require(?:\s+that)?|ensure(?:\s+that)?|procure(?:\s+that)?|guarantee\s+that|see\s+to\s+it\s+that|make\s+sure\s+that|make\s+certain\s+that)\s+(?:each\s+of\s+|all\s+of\s+|any\s+of\s+|\d+\s+of\s+|one\s+of\s+|at\s+least\s+\d+\s+of\s+)?(?:its|their|his|her|each|all|any|every|the)\s+"
                                      r"(?:[\w'’-]+\s+){0,2}?(?:employees?|personnel|staff|agents?|contractors?|subcontractors?|sub-?agents?|representatives?|officers?|directors?|"
                                      r"invitees?|guests?|customers?|end\s+users?|sublicensees?|suppliers?|vendors?|consultants?|workers?|technicians?|lenders?|"
                                      r"carriers?|drivers?|haulers?|brokers?|dealers?|resellers?|franchisees?|licensees?|members?|participants?|volunteers?|visitors?|passengers?|"
                                      r"tenants?|occupants?|students?|patients?|physicians?|providers?|nurses?|crews?|pilots?|installers?|auditors?|insurers?|"
                                      # the other nonparty roles (NONPARTY_HEADS) and the counterparties a party doesn't control: the landlord of the Premises, a lender, a bank
                                      r"landlords?|lessors?|lessees?|licensors?|borrowers?|counterpart(?:y|ies)|banks?|clients?|governmental\s+authorit(?:y|ies)|"
                                      r"(?:escrow|paying|collateral|exchange|transfer|disbursing|settlement|closing)\s+agents?|arbitrators?|arbitral\s+tribunals?|mediators?|accountants?|"
                                      r"appraisers?|experts?|title\s+compan(?:y|ies)|title\s+insurers?|escrow\s+holders?|spouses?|courts?|judges?|referees?|surveyors?|inspectors?|"
                                      r"trustees?|administrators?|users?)\b", re.I)


def clause_start(t, pos):
    """Where the clause holding position pos begins: after the last period, semicolon, colon or line break, skipping the
    period of an abbreviation (Acme Holdings, Inc. shall), of an initial (U.S.) and a decimal point (Section 5.2 shall)."""
    i = pos
    while True:
        j = max(t.rfind(c, 0, i) for c in '.;:\n')
        if j < 0:
            return 0
        if t[j] == '.' and (ABBREV.search(t[:j + 1]) or re.search(r"(?:^|\s)[A-Z]\.$", t[:j + 1]) or re.match(r"\d", t[j + 1:j + 2])):
            i = j
            continue
        return j + 1


# an exception clause with its own subject: except that the Manager shall not; provided, however, that Buyer shall. A bare
# "except as ..." or "except for ..." has no subject of its own and is still read as a condition
# the noun a nonrestrictive who points back to: Supplier shall appoint a project sponsor, who shall; "Acme, who shall" names a party,
# which the subject test then reads as a party
RELATIVE_WHO_HEAD = re.compile(r"(?:\b(?:the|a|an|each|any|every|its|their)\s+|[A-Z][\w-]*['’]s\s+)((?:[A-Za-z][\w-]*\s+){0,2}[A-Za-z][\w-]*)\s*$|^\s*([A-Z][\w-]*(?:\s+[A-Z][\w-]*){0,2})\s*$")
EXCEPT_THAT = re.compile(r"(?:except|provided|save)(?:\s*,?\s*however\s*,?)?\s+that\s+(\S.*)$", re.I | re.S)


# a typed enumerator or section label before the subject: 1., (a), (a)(i), 3.1(a), Section 3.1(a), Section 3, Article II
SUBJ_LABEL = re.compile(r"^(?:(?:Section|SECTION|Article|ARTICLE|Clause|Paragraph)\s+[IVXLC\d]+(?:\.\d+)*(?:\([a-z0-9]{1,4}\))*\.?|"
                        r"\d+(?:\.\d+)*(?:\([a-z0-9]{1,4}\))*\.?|\(?[A-Za-z0-9]{1,4}[.)](?:\([a-z0-9]{1,4}\))*)\s+")


def subject_of(t, pos):
    """The subject before a modal at pos: (kind, words), kind = party | thing | nonparty | unknown | skip."""
    start = clause_start(t, pos)
    seg = re.sub(r",\s+(?:Inc|LLC|L\.L\.C|L\.P|LP|LLP|PLLC|N\.A|Ltd|Co|Corp|P\.C|P\.A)\.?(?=\s|$)", '', t[start:pos])  # Acme Holdings, Inc. shall: the suffix is part of the name, not a 2nd comma phrase
    first = re.search(r"\b(?:shall|will|may|must)\b", seg)
    if first and re.search(r"\b(?:and|or|but)\s*$", seg):
        seg = seg[:first.start()]  # Acme shall give notice and shall deliver it: the 2nd shall shares the 1st one's subject
    parts = seg.split(',')
    cand = parts[-1].strip()
    rel = RELATIVE_WHO_HEAD.search(parts[-2]) if len(parts) > 1 and cand.lower() == 'who' else None
    if rel:
        cand = parts[-1] = rel.group(1) or rel.group(2)  # a project sponsor, who shall review: the relative pronoun's antecedent is the subject
    exc = EXCEPT_THAT.match(cand)
    if exc:
        cand = parts[-1] = exc.group(1)  # ..., except that Buyer shall pay: Buyer is the subject, not the main clause before the comma
    if len(parts) > 1 and (not cand or SUBJ_COND.match(cand) or re.match(r"(?:\w+ly|[a-z]+ing)\b", cand)):
        cand = parts[0].strip()  # Seller, at its own cost, shall: the subject is before the 1st comma
    cand = SUBJ_LABEL.sub('', cand, count=1)  # a typed enumerator or section label
    cand = re.sub(r"^[A-Z][\w'’ -]{0,40}\.\s{1,2}", '', cand)  # a run-in heading
    cand = re.sub(r"^(?:and|or|but|then|also|so|thus|that|and\s+that)\s+", '', cand, flags=re.I).strip()
    cand = re.sub(r"\s+(?:also|then|thereafter|promptly|immediately|automatically|each|jointly|severally|not|further|only|solely|in\s+no\s+event|at\s+no\s+time)$", '', cand, flags=re.I).strip()
    if not cand or SUBJ_COND.match(cand) or re.match(r"(?:neither|no|none|nothing|nobody)\b", cand, re.I):
        return 'skip', cand
    if REF_SUBJ.match(cand):
        return 'expletive', cand
    head_chunk = SUBJ_CUT.split(cand, maxsplit=1)[0].strip()
    words = [w for w in re.findall(r"[A-Za-z][\w'’-]*", head_chunk)]
    words = [w for w in words if not SUBJ_DET.match(w) and not re.search(r"['’]s?$", w)]
    if not words or len(words) > 6:
        return 'unknown', cand
    joined, head = ' '.join(words), words[-1]
    parties = (PARTY_TERMS or PARTY_DEFAULT) | PARTY_COLLECTIVE | EXHIBIT_PARTIES
    roles_low = {r.lower() for r in AGENT_ROLES}
    if joined in NONPARTY_NAMED and joined not in parties:
        return 'nonparty', joined  # Brazos, a Texas corporation and Seller's subsidiary ("Brazos"), named in the recitals: not a party
    if (joined.lower() in roles_low or head.lower() in roles_low) and joined not in parties and head not in parties \
            and (PARTY_TERMS or head[0].islower()):
        return 'nonparty', joined  # the parties are known, and this role (the Manager, the Servicer) isn't one of them
    if NONPARTY_HEADS.match(joined) and joined not in parties and not (not PARTY_TERMS and joined in PARTY_DEFAULT):
        return 'nonparty', joined  # the Title Company: a nonparty, though its head word (Company) can name a party
    if joined in parties or head in parties or head.lower() in ('party', 'parties') or any(re.search(r"\b" + re.escape(pt) + r"\b(?!['’])", head_chunk) for pt in parties) \
            or re.search(r"\b(?:and|or|nor)\b", head_chunk) and any(w in parties for w in words):
        return 'party', joined
    if NONPARTY_HEADS.match(joined) or NONPARTY_HEADS.match(head):
        return ('party' if joined in parties or (not PARTY_TERMS and head in PARTY_DEFAULT) else 'nonparty'), joined
    if head.lower() in ('member', 'members') and re.search(r"\bof\s+(?:the\s+|its\s+|[A-Z][\w-]*['’]s\s+)?(?:[A-Z][\w-]*\s+)*(?:Personnel|Staff|Team)\b", cand):
        return 'nonparty', re.sub(r"^(?:[Ee]ach|[Aa]ny|[Ee]very)\s+", '', cand).strip()  # Each member of the Key Personnel: individuals, not parties
    if head.lower() in PERSONISH or joined.lower() in PERSONISH:
        return 'unknown', joined
    if head.lower() in THING_HEADS:
        return 'thing', joined
    return 'unknown', joined


def subject_modal_checks(t, out, add):
    for m in re.finditer(r"\b(?:shall|will)\b", t):
        if in_quotation(t, m.start()):
            continue  # quoted text keeps its own verbs (house rule 1): a clause another contract must contain, a statute's words
        word = m.group(0)
        kind, subj = subject_of(t, m.start())
        after = t[m.end():m.end() + 60]
        if kind == 'thing' and word == 'shall':
            if any(o['check'] in ('passive-voice', 'passive-hides-actor', 'category-shall', 'shall-in-definition', 'negative-subject-shall')
                   and o['start'] < m.end() + 12 and o['end'] > m.start() for o in out):
                continue  # a passive (The Fee shall be paid) or another check already reports this shall
            mm = re.match(r"\s+(?:not\s+)?\w+", after)
            span = _Span(t, m.start(), m.end() + (mm.end() if mm else 0))
            add('category-shall', f'Shall with a subject that can\'t have a duty ({subj}). Apply the has-a-duty test (MSCD 3.92) and pick the category: '
                'for a policy, the present tense (The Term is 3 years; Tennessee law governs this agreement; this agreement controls) or will for a contingent '
                'future event (MSCD 3.98; 3.334-3.335); for a requirement the sentence imposes on this thing or event (The Closing shall take place; Each Deliverable '
                'shall conform), write must (MSCD 3.154: The Closing must take place at Acme\'s offices), or better, restructure so a party is the subject of shall (3.158). '
                'Don\'t turn a requirement into a statement of fact (The Closing takes place).', span, 'medium', ['R-3.98-shall-future-time', 'R-3.154-must-for-others'])
        elif kind == 'expletive' and word == 'shall' and re.match(r"\s+be\b", after):
            span = re.compile(r"\b(?:There|there|It|it)\s+shall\s+be\b").match(t, t.rfind(subj, 0, m.start()))
            if span:
                add('category-shall', 'There shall be / It shall be: language of policy with no duty; find the real subject and use the present tense '
                    '(The Purchase Price does not change for ...; It is a condition to ...) (MSCD 3.98; 17.24).', span, 'medium', ['R-17.24-there-is-there-are'])
        elif kind == 'nonparty' and not re.match(r"\s+(?:not\s+)?be\s+(?:entitled|deemed|liable)\b", after):
            if any(o['check'] == 'nonparty-obligation' and o['start'] <= m.start() < o['end'] + 2 for o in out):
                continue
            mm = re.match(r"\s+(?:not\s+)?\w+", after)
            st = t.rfind(subj, 0, m.start())
            if st < 0:  # the subject's words aren't contiguous (Sandia Crest's volunteers): start at the clause
                st = clause_start(t, m.start())
                st += len(t[st:m.start()]) - len(t[st:m.start()].lstrip())
            span = _Span(t, st, m.end() + (mm.end() if mm else 0))
            # with no introductory clause read (a pasted clause), a capitalized role (the Trustee, the Sublicensee) may be the signing party: a candidate, not a required finding
            conf = 'low' if not PARTY_TERMS and subj[:1].isupper() else 'medium'
            note = '' if PARTY_TERMS else ' No introductory clause was read, so the parties are unknown: if this role signs the document, it is a party and shall is right.'
            add('nonparty-obligation', f'{word.capitalize()} with a nonparty subject ({subj}): a contract binds only its parties, so this duty binds no one. '
                'Restructure so a party has the duty (Acme shall deliver the notice to the escrow agent), or use must for the nonparty and say what happens if it doesn\'t act (MSCD 3.89; 3.166). '
                'Use shall cause only for a party\'s instrumentality, such as a wholly owned subsidiary, never for a nonparty the party doesn\'t control (MSCD 3.160-3.163). '
                'If this nonparty signs the contract, it is a party and shall is right.' + note, span, conf, ['R-3.89-shall-duty'])
        elif kind == 'unknown' and word == 'shall' and PARTY_TERMS and subj.islower() and not re.match(r"\s+(?:not\s+)?be\b", after) \
                and re.search(r"\b(?:the|each|any|every|an?|all|such|its|their|[A-Z][\w-]*['’]s)\s+$", t[:max(t.rfind(subj, 0, m.start()), 0)], re.I) \
                and subj.split()[-1] not in ('party', 'parties', 'other', 'others', 'one', 'who') and ' '.join(w.capitalize() for w in subj.split()) not in PARTY_TERMS \
                and agent_noun(subj.split()[-1]):
            # the parties are known, and this subject is a lowercase noun for someone who can act (the freight forwarder shall; each transferee shall)
            # that isn't one of them: a nonparty unless the drafter dropped a capital. "the other party shall" and "the Supplier shall" stay clear,
            # and so does a thing as subject (the headings shall not affect; the unpaid balance shall become due), which category-shall reports
            mm = re.match(r"\s+(?:not\s+)?\w+", after)
            st = t.rfind(subj, 0, m.start())
            add('nonparty-obligation', f'Shall with a lowercase common-noun subject ({subj}) that the introductory clause doesn\'t name as a party. If it is a nonparty, '
                'this duty binds no one: restructure so a party has the duty, or use must for the nonparty and say what happens if it doesn\'t act (MSCD 3.89; 3.166). '
                'If it is a party written in lowercase, capitalize the defined term (MSCD 6.7).', _Span(t, st, m.end() + (mm.end() if mm else 0)), 'low', ['R-3.89-shall-duty'], sev=2)
    for m in SHALL_CAUSE_UNCONTROLLED.finditer(t):
        if in_quotation(t, m.start()):
            continue
        add('nonparty-obligation', 'Shall cause (or shall require, shall ensure) for nonparties the party doesn\'t control, such as employees or contractors: '
            'the party can\'t guarantee what they do. Restructure so the party has the duty (Acme shall enter into a confidentiality agreement with each of its employees), '
            'or use must for the nonparty (MSCD 3.162-3.166). Shall cause is right only for an instrumentality, such as a wholly owned subsidiary (3.160).', m, 'medium', ['R-3.163-no-shall-cause-uncontrolled'])
    for rx, msg, rules, sev in PARTY_STATE:
        for m in rx.finditer(t):
            if any(o['check'] in ('category-shall', 'category-will', 'is-entitled-to') and o['start'] < m.end() and o['end'] > m.start() for o in out):
                continue
            if re.search(r"\b(?:" + COND_LEAD + r"|when|whether)\b[^,.;:]{0,90}$", t[:m.start()], re.I):
                continue  # in a condition, the shall-in-condition check reports it
            check = 'category-shall' if m.group(0).lower().startswith('shall') else 'category-will'
            add(check, msg, m, 'medium', rules, sev=sev if sev_is_free(check, rules) else None)


QUOTE_OPEN = re.compile(r'[“]|(?<![\w])"(?=\w)')
QUOTE_CLOSE = re.compile(r'[”]|(?<=[\w.,;:!?])"')


def in_quotation(t, pos):
    """True when pos sits inside a quotation of 3 or more words that closes in the same paragraph: quoted text keeps its own
    words (a clause another contract must contain, a statute's wording). A defined term in quotation marks closes before the
    verb that follows it, so it never counts."""
    opens = [m.start() for m in QUOTE_OPEN.finditer(t[:pos])]
    closes = [m.start() for m in QUOTE_CLOSE.finditer(t[:pos])]
    if len(opens) <= len(closes):
        return False
    close = QUOTE_CLOSE.search(t, pos)
    if not close:
        return False
    return len(t[opens[-1]:close.start()].split()) >= 3


MATCH_CUT = 120  # characters of matched text a finding carries


def finding(check, msg, para, m=None, conf='medium', rules=(), source='house', sev=None, match=None, start=None, end=None, cut=MATCH_CUT):
    """The 1 shape every finding has. m is the match (or _Span) the finding points at; match, start and end override what it
    gives (a defined term's name, a cell's offset); a finding about the whole document has para -1 and start and end -1.
    sev=None takes the severity policy's value (severity_for); an explicit sev is the site's own judgment."""
    f = {'check': check, 'severity': severity_for(check, rules, sev), 'para': para,
         'match': (match if match is not None else (m.group(0) if m else ''))[:cut],
         'start': start if start is not None else (m.start() if m else -1), 'end': end if end is not None else (m.end() if m else -1),
         'message': msg, 'confidence': conf, 'rule_ids': list(rules), 'source': source}
    return f


def passive_checks(t, p, add, out):
    """the passive voice (house rule 1): a passive with no actor, the deemed fiction, and the words that look passive but are not."""
    for m in GOODS_WARRANTY.finditer(t):
        cleared(out, p, m, ['R-3.457-use-states', 'R-13.937-warrants-statement-of-fact', 'R-3.474-no-future-facts', 'R-3.27-throat-clearing', 'R-3.436-verb-not-remedy'])
    for m in re.finditer(r"\bCAN(?=-[A-Z])", t):
        cleared(out, p, m, ['R-3.207-no-can'])  # the CAN-SPAM Act: a statute's name
    seen_verbs = set()
    for m in list(PASSIVE_RE.finditer(t)) + list(MODAL_BE.finditer(t)):
        word = m.group(1).lower()
        if m.start(1) in seen_verbs or word in NOT_PARTICIPLE:
            continue  # the Units are red, the price is indeed fixed: not a verb, with or without a by-phrase
        if word in NOT_PASSIVE or word.rstrip('?') in NOT_PASSIVE:
            agent_by = re.match(r"(?:\s+(?:or|and)\s+\w+ed)?[^.;:,]{0,25}?\bby\s+(\S+(?:\s+\S+){0,2})", t[m.end():])
            by_law = agent_by and re.match(r"(?:(?:applicable|any|the)\s+)?(?:law|operation\s+of\s+law|statute)\b", agent_by.group(1), re.I)
            if not agent_by or (BY_MEANS.match(agent_by.group(1)) and not by_law) or re.match(r"(?:reason|virtue|means|way)\b", agent_by.group(1), re.I):
                continue  # an adjective (Acme is duly authorized; Tenant is bound), not a passive; with an actor (banks are authorized by law; bound by this agreement) it is one
        if re.match(r"un[a-z]{3,}ed$", word):
            continue  # unresolved, unpaid, unused: adjectives, not passives
        if word == 'deemed':
            seen_verbs.add(m.start(1))
            if not any(o['check'] == 'category-shall' and o['start'] < m.end() and o['end'] > m.start() for o in out):
                add('passive-voice', 'Deemed is a passive stating a legal fiction. House rule 1: make the agreement the subject (This agreement treats Client as having accepted it), '
                    'or use a linking verb with will, because a notice is a contingent future event (Any notice will be effective on delivery) (house-style.md section 1; MSCD 3.334; 13.209).', m, 'high', ['R-3.15-active-voice'])
            continue
        if word in ('closed', 'opened') and re.match(r"\s+(?:to\s+the\s+public|for\s+(?:business|banking)|on\s+(?:that|the|a)\s+day)|\s*(?:[.,;:)]|$|\s+(?:or|and)\s+(?:open|required|authorized|permitted)\b)", t[m.end():], re.I):
            continue  # the bank is closed to the public: a state (adjective), not a passive
        seen_verbs.add(m.start(1))  # one flag per participle, even when both patterns match it
        if word == 'required' and (re.search(r'\bnot\s+(?:be\s+)?required\s+to\b', t[max(0, m.start() - 8):m.end() + 4], re.I)
                                   or re.search(r"\b(?:No|Neither|None\s+of)\b[^.;:,]{0,60}$", t[:m.start()], re.I) and re.match(r"\s*to\b", t[m.end():])):
            continue  # is not required to: Blake's fixed exception (MSCD 3.292); shall not be required to: the category check reports it
        modal = re.match(r"(?:shall|will|must|may|is\s+to|are\s+to)\b", m.group(0), re.I) or re.search(r"\b(?:shall|will|must|may|is\s+to|are\s+to)\s+(?:not\s+)?(?:\w+ly\s+)?$", t[:m.start()], re.I)
        clause = re.split(r"[.;:]", t[m.end():], maxsplit=1)[0][:120]
        agent = next((b for b in re.finditer(r"\bby\s+(?:the\s+|each\s+|either\s+)?(\S+(?:\s+\S+)?)", clause) if not BY_MEANS.match(b.group(1))), None)
        if modal and agent is None:
            add('passive-hides-actor', 'Passive with a modal and no actor: the reader can\'t tell who must (or may) act. Name the actor in the active voice (MSCD 3.15; house rule 1). Severity 1 if more than 1 party could be the actor; if only 1 party could act, it is severity 2 (house rule 1).', m, 'medium', ['R-3.15-passive-hides-actor'])
            continue
        add('passive-voice', 'Possible passive voice; house rule is active voice only. Name the actor (house-style.md section 1).', m, 'medium', ['R-3.15-active-voice'])


def signature_checks(t, p, add, out):
    """the signature phrases MSCD tells you to change (SIGNATURE), with their contextual exceptions."""
    for rx, chk, sev, msg, rules in SIGNATURE:
        for m in rx.finditer(t):
            if rules == ['R-5.7-signing-not-executing'] and in_quotation(t, m.start()):
                continue  # quoted text the contract must reproduce word for word (Cal. Civ. Code Section 1542); keyed on the rule id, which outlives the message
            if chk == 'represents-warrants' and WHOSE == 'other-side':
                add(chk, "Keep represents and warrants on the other side's draft; suggest the remedies-neutral sentence in a comment (3.459-3.463; house rule 10).", m, 'high', rules, sev=3)
            elif chk == 'represents-warrants' and WHOSE == 'blake':
                add(chk, 'represents and warrants on your draft: use states (MSCD 3.457; house rule 10).', m, 'high', rules, sev=2)
            elif chk == 'agrees-to' and RELATIVE_AGREES.search(t[:m.start()]):
                cleared(out, p, m, ['R-3.125-no-agrees-to-obligation', 'R-3.59-no-agrees-to-performance'])
                continue  # the amount that Provider agrees to pay in settlement: a relative clause describing an agreement, not language of obligation
            elif chk == 'and-or' and re.search(r"\w+,\s+(?:[\w-]+\s+){0,4}?[\w-]+,?\s*$", t[max(0, m.start() - 80):m.start()]):
                add(chk, 'and/or after a list of 3 or more items: unclear whether it means any 1, any combination or all; list the combinations allowed (MSCD 11.94).', m, 'high', rules, sev=1)
            else:
                add(chk, msg, m, 'high', rules, sev=sev if chk in OWN_SEV or sev_is_free(chk, rules) else None)


def party_verb_checks(t, p, add, out):
    """the verb used with a party subject: will, must and may not for a duty or a prohibition (MSCD 3.111, 3.107, 3.307), the subject analysis, and the article before a party name (house rule 11)."""
    # party subjects: the contract's own party names, or common party nouns in a fragment with no introductory clause
    subj = (PARTY_TERMS or PARTY_DEFAULT) | PARTY_COLLECTIVE | PARTY_PHRASES
    names = '|'.join(sorted(map(re.escape, subj), key=len, reverse=True))
    # a comma phrase may sit between the party and the modal (Brightwater, at its own expense, will maintain); after a clause
    # that names a party, a pronoun subject (If Kestrel receives a subpoena, it will notify) is that party; "it will terminate"
    # and the other policy verbs after a pronoun are a contingent event, not a duty (the pronoun form excludes them)
    party_x = r"\b(?:" + names + r")(?:,\s+[^,;:.]{1,60},)?\s+"
    pronoun_x = r"\b(?:" + names + r")\b[^.;:]{0,100}?,\s+(?:and\s+|but\s+|then\s+)?(?:it|they)\s+"
    will_x = r"(?:will\b(?!\s+(?:be|have|not\s+be|need|require|exceed|receive|incur|owe|become|reach|fall|own|hold|know|lose|suffer|benefit%s)\b)|won['’]t\b)"
    policy_verbs = '|terminate|expire|apply|continue|remain|survive|take|vest|lapse|cease|end|renew|automatically|no\\s+longer'
    for m in list(re.finditer(party_x + will_x % policy_verbs, t)) + list(re.finditer(pronoun_x + will_x % policy_verbs, t)):
        if re.search(r"\bwhether\s+$", t[:m.start()], re.I) or re.search(r"\b(?:evaluate|decide|determine|consider|assess|know|ask)s?\s+if\s+$", t[:m.start()], re.I):
            continue  # evaluate whether Mesa Verde will build: an indirect question about a future event, not a duty (MSCD 3.111 keeps will there)
        lead_in = LEAD_IN.search(t)
        if p['idx'] in RECITAL_IDX or (lead_in and m.start() < lead_in.start()):
            continue  # a recital (Manager will do so through the Operator): background, not a duty; the recital may share a paragraph with the lead-in
        if in_quotation(t, m.start()):
            continue  # quoted text keeps its own verbs
        add('category-will', 'will for a party\'s duty: use shall (MSCD 3.111). Keep will only for future events no party controls.', m, 'medium', ['R-3.111-no-will-for-obligation'])
    must_x = r"(?:must\b(?!\s+(?:be|have)\b)|mustn['’]t\b)"
    for m in list(re.finditer(party_x + must_x, t)) + list(re.finditer(pronoun_x + must_x, t)):
        if re.search(r"(?:^|[.;:][\"”’)]*\s+)(?:To|In\s+order\s+to|For\s+[^,.;]{1,80}?\s+to)\s+[^.;]{3,120},\s*(?:\w+\s+){0,3}$", t[:m.start()]):
            continue  # must in a condition (To exercise the Option, Acme must ...) is right (MSCD 3.386)
        add('category-must', 'must for a duty on the subject: use shall (MSCD 3.107). Keep must for a condition (To exercise ..., Acme must ...) or when the subject is a nonparty (an escrow agent that only acknowledges, 3.154).', m, 'medium', ['R-3.107-no-must-for-subject'])
    for m in list(re.finditer(party_x + r"may\s+not\b", t)) + list(re.finditer(pronoun_x + r"may\s+not\b(?!\s+be\b)", t)):
        add('may-not', 'may not for a prohibition with an affirmative subject: write shall not (MSCD 3.307). (With a negative subject, Neither party may is right: house rule 8.)', m, 'high', ['R-3.307-no-may-not'])
    subject_modal_checks(t, out, add)
    terms = PARTY_TERMS or PARTY_DEFAULT
    for m in party_article_re(terms).finditer(t):
        if t[max(0, m.start() - 1):m.start()] == '"' or t[max(0, m.start() - 1):m.start()] == '\u201c':
            continue
        add('party-article', f'House rule 11: no article before a defined party name. Write {m.group(1)}, not the {m.group(1)} (MSCD 2.105 differs).', m, 'medium', ['R-2.105-definite-article'])
    for m in DEF_WITH_ARTICLE.finditer(t):
        if m.group(1) in terms:
            add('party-article', f'House rule 11: a party-name definition takes no article: ("{m.group(1)}") (MSCD 6.63 differs).', m, 'high', ['R-6.63-article-in-parenthetical'])


# pay [Party] N% of ...: a bare percentage as the amount (MSCD 14.24 inserts an amount equal to); a fee equal to N% of and an amount equal to N% of stay clear
PERCENT_PAY = re.compile(r"\b(?:pay|pays|paid|reimburse|reimburses|refund|refunds|credit|credits)\s+(?:(?:to\s+)?(?:[A-Z][\w-]*(?:\s+[A-Z][\w-]*)?|(?:the|each|either|both)\s+(?:other\s+)?part(?:y|ies)|it|them)\s+)?(\d+(?:\.\d+)?\s*(?:%|percent))\s+of\b")


def number_checks(t, p, add, out):
    """numbers (house rule 2): words for numbers, a sentence that starts with a digit, ordinals, words and digits together, and needless cents."""
    keep_spans = [(k.start(), k.end()) for k in ONE_WORD.finditer(t)]
    count_spans = [(k.start(), k.end()) for k in ONE_COUNT.finditer(t)]
    for m in NUM_RE.finditer(t):
        pre = t[max(0, m.start() - 12):m.start()]
        if m.group(0)[0].isupper() and m.start() > 0 and PROPER_AFTER.match(t, m.end()):
            continue  # part of a proper name (Two Lattice Plaza, Fourth Judicial Circuit)
        nxt = re.match(r"\s+([A-Z][\w'’-]*)", t[m.end():])
        if m.group(0)[0].isupper() and nxt and not re.fullmatch(UNIT_WORDS, nxt.group(1), re.I) and not NUM_RE.fullmatch(nxt.group(1)) \
                and not re.search(r"(?:^|[.;:!?]\s+|\n\s*)$", t[:m.start()]):
            continue  # a proper name mid-sentence (Twelve Oaks Mall, One Liberty Plaza)
        if m.group(0)[0].isupper() and nxt and not re.fullmatch(UNIT_WORDS, nxt.group(1), re.I) and (
                re.search(r"\b(?:Address|Attention|Attn\.?|Location|Premises|Property|Street|Office|Located\s+at)\s*:?\s*$", t[:m.start()], re.I)
                or re.match(r"\s+[A-Z][\w'’-]*(?:\s+[A-Z][\w'’-]*)?,\s+(?:Suite|Ste\.|Floor|Unit|Room|Building)\b", t[m.end():])):
            continue  # a building's name in an address (Address: One Riverway, Suite 1700)
        if any(a <= m.start() < b for a, b in keep_spans):
            continue  # one as a pronoun or part of a word (no one, one another, one-time): house rule 2 keeps the word
        if any(a <= m.start() < b for a, b in count_spans):
            add('number-word', 'One counts something here (one or more, one of, one party): write 1 (house rule 2; keep one only as a pronoun or part of a word, such as no one, one another, one-time).', m, 'high', ['R-14.15-words-then-digits'])
        elif not re.search(r"\d\s*$", pre):
            add('number-word', 'Spelled-out number; house rule is digits for every number (house-style.md section 2).', m, 'high', ['R-14.15-words-then-digits'])
    for m in DIGIT_START.finditer(t):
        before = t[:m.start()].rstrip()
        if before and (ABBREV.search(before) or re.search(r"(?:^|\s)(?:\(?[A-Za-z0-9]{1,3}[.)]|[IVXLC]+\.)$", before)):
            continue  # Unit No. 1; a typed enumerator before the amount (1. $200,000 at signing): not a sentence that starts with a digit
        if m.start() == 0 and re.match(r"\d+(?:\.\d+)+\.?\s|\d+\s+[A-Z][\w'’-]*(?:\s+[A-Z][\w'’-]*){0,5}\.\s", t):
            continue  # a typed enumerator (1.1 Consultant shall ...) or a numbered run-in heading (12 Notices.  ...), not a sentence that starts with a number
        sent = sentence_from(t, m.start())
        if len(sent.split()) < 5 or not sent.rstrip().endswith(('.', ';', ':')):
            continue  # a table cell, a heading or a label (30 days; 2027 Budget), not a sentence
        add('number-word', 'A sentence starts with a digit. House rule 2: restructure the sentence rather than spell the number out '
            '(5 directors constitute a quorum becomes A quorum of the Board is 5 directors; 30 days after ... becomes Acme shall ..., no later than 30 days after ...).', m, 'medium', [])
    for m in FIRST_COUNT.finditer(t):
        add('ordinal-word', 'First counts something here: write 1st (house rule 2). Keep fixed terms such as right of first refusal.', m, 'medium')
    for m in ORD_RE.finditer(t):
        if m.group(0)[0].isupper() and re.match(r"\s+[A-Z]", t[m.end():m.end() + 2]):
            continue  # part of a proper name (500 Third Avenue, Fifth Third Bank)
        if re.match(r"[- ]part(?:y|ies)\b", t[m.end():], re.I):
            continue  # third party: a usage point (13.875), reported by the signature check, not a count
        add('ordinal-word', 'Ordinal word; if it counts something, write it in digits (2nd, 3rd).', m, 'low')
    for m in _WD_PAREN.finditer(t):
        start, w = words_before(t, m.start())
        if start is None:
            continue
        span = _Span(t, start, m.end())
        add('words-and-digits', 'Words and digits together; use digits only (MSCD 14.5-14.11; house rule).', span, 'high', ['R-14.5-words-and-digits'])
        try:
            dv = Decimal(m.group(1).replace(',', ''))
        except InvalidOperation:
            continue
        if w is not None and Decimal(w) != dv:
            unit = '%' if m.group(2) else ''
            add('words-digits-conflict', f'The words say {Decimal(w):,}{unit} and the digits say {dv:,}{unit}. A court may prefer the words (UCC 3-114 does for '
                'negotiable instruments); confirm the intended amount, then state it once in digits (MSCD 14.5-14.11).', span, 'high', ['R-14.5-words-and-digits'], sev=1)
    for m in DIGITS_THEN_WORDS.finditer(t):  # 30 (thirty) days; $5,000 (five thousand dollars)
        toks = re.findall(r"[a-z]+", m.group(2).lower().replace('-', ' '))
        while toks and toks[-1] in _UNIT_WORDS:
            toks.pop()
        w = words_value(' '.join(toks)) if toks else None
        if w is None:
            continue  # Section 3 (Payment): no number words
        add('words-and-digits', 'Words and digits together; use digits only (MSCD 14.5-14.11; house rule).', m, 'high', ['R-14.5-words-and-digits'])
        try:
            dv = Decimal(m.group(1).replace(',', ''))
        except InvalidOperation:
            continue
        if Decimal(w) != dv:
            add('words-digits-conflict', f'The digits say {dv:,} and the words say {Decimal(w):,}. A court may prefer the words (UCC 3-114 does for '
                'negotiable instruments); confirm the intended amount, then state it once in digits (MSCD 14.5-14.11).', m, 'high', ['R-14.5-words-and-digits'], sev=1)
    for m in PERCENT_PAY.finditer(t):
        add('percentage-amount-equal-to', f'A bare percentage as the amount paid (pay {m.group(1)} of ...): when calculating money, write an amount equal to {m.group(1)} of ... (MSCD 14.24).',
            m, 'high', ['R-14.22-simple-formula'])
    for m in CENTS_00.finditer(t):
        add('money-cents', 'Needless cents: write $850,000, not $850,000.00, unless an amount nearby has cents (MSCD 13.546).', m, 'high', ['R-13.546-money-decimals'])


def spacing_list_checks(t, p, add, out):
    """spacing between sentences (house rule 5) and the serial comma (MSCD 12.58)."""
    for m in ONE_SPACE.finditer(t):
        before = t[:m.start() + 1]
        if ABBREV.search(before) or re.search(r"\b[A-Z]\.$", before):
            continue
        if re.fullmatch(r"[\s#>*_]*(?:(?:Article|ARTICLE|Section|SECTION)\s+)?(?:[IVXLC]+|[A-Za-z]|\d+(?:\.\d+)*|\([a-z0-9]+\))\.", before):
            continue  # a typed enumerator at the start of the paragraph, not a sentence end
        add('spacing', 'One space after a sentence; house rule is two spaces between sentences.', m, 'high', ['R-16.44-one-space'])
    for m in TWO_AFTER_COLON.finditer(t):
        add('spacing', 'Two spaces after a colon; house rule is one space after a colon.', m, 'high')
    for m in serial_lists(t):
        add('serial-comma', 'A list of 3 or more items with no comma before the and/or: add the serial comma, which also stops the last 2 items reading as 1 (MSCD 12.58-12.61).', m, 'medium', ['R-12.58-use-serial-comma'])


def policy_checks(t, p, add, out):
    """a nonparty with shall, a contingent policy in the present tense, a negative subject with shall, should, once, when, wordy phrases and provisos."""
    for m in NONPARTY_SHALL.finditer(t):
        if re.search(r"\b(?:nor|and|or)\s+$", t[:m.start()]) or in_quotation(t, m.start()):
            continue  # a compound subject that includes a party (neither Buyer nor its agents shall): other checks cover it; quoted text keeps its verbs
        add('nonparty-obligation', 'Shall with a nonparty subject: a contract binds only its parties, so this duty binds no one. Restructure so the party has the duty (Consultant shall enter into a confidentiality agreement with each of its employees), or use must for the nonparty (MSCD 3.89; 3.166). Don\'t write shall cause, shall require or shall ensure for employees or other nonparties the party doesn\'t control (MSCD 3.162-3.163); keep shall cause for a party\'s instrumentality, such as a wholly owned subsidiary (3.160).', m, 'high', ['R-3.89-shall-duty'])
    seen_policy = set()
    party_words = {w.lower() for w in (PARTY_TERMS or PARTY_DEFAULT) | PARTY_COLLECTIVE}
    for rx in (CONTINGENT_LEAD, CONTINGENT_TAIL, CONTINGENT_REL):
        for m in rx.finditer(t):
            span = (m.start('verb'), m.end('verb'))  # the present-tense policy verb
            if span in seen_policy or re.search(r"\b(?:shall|will|may|must|to|that|which|who)\s+$", t[:span[0]]) or in_quotation(t, span[0]):
                continue  # a modal before the verb, or a relative clause (the amount that becomes due after ...), or quoted text
            if rx is CONTINGENT_TAIL and re.search(r"\b(?:before|after|until|when|whenever|if|unless|once|while|as\s+long\s+as|so\s+long\s+as|the\s+day|the\s+date)\s+(?:[\w'’-]+\s+){0,5}$", t[:m.start()]):
                continue  # "no later than 180 days before the Term ends": the verb sits in a time clause, not a matrix clause
            if m.groupdict().get('subj'):
                # the generic subject: a person or a party acts (the Supplier applies the discount when ...), so this is no policy;
                # a noun after a preposition (notice of any fee increases before ...) is not a subject; a condition in a later
                # clause (..., and if Beta fails to pay) is not this clause's condition. A notices rule is no exception: MSCD's own
                # form reads "A notice ... will be effective if", and 13.209 puts deem with will because it applies to future events
                # the subject's head is the noun phrase before its 1st preposition (each statement of Seller or Buyer: statement),
                # except a partitive (each of the parties); a party named after "of" doesn't make the subject a party
                subj_txt = m.group('subj')
                core = subj_txt if re.match(r"(?:each|any|all|none|either|neither|one|both|some)\s+of\b", subj_txt, re.I) \
                    else re.split(r"\s+(?:of|in|by|to|for|under|with|from|on|at)\s+", subj_txt, maxsplit=1)[0]
                heads = {w.lower() for w in re.findall(r"[A-Za-z][\w'’-]*", core)}
                tail = t[m.end('verb'):m.end('verb') + 140]
                if heads & (party_words | PERSONISH | {'employee', 'employees', 'executive', 'user', 'users', 'staff', 'personnel'}) \
                        or re.search(r"\b(?:of|for|to|in|on|at|by|with|without|under|about|regarding|concerning|from|into|than|and|or|nor)\s+$", t[:m.start('subj')]) \
                        or re.match(r"(?:(?!,\s+(?:and|but|or)\b)[^.;]){0,140}?\b(?:if|when|whenever|unless|upon|once|after|before|until)\s+"
                                    r"(?!(?:" + MONTH + r"|the\s+(?:date|day)\s+of\s+this|\d))", tail) is None:
                    continue
            seen_policy.add(span)
            add('category-will', 'Present tense for a policy about a contingent future event: MSCD 3.334 and 3.361 take will (this agreement will terminate; the termination will take effect). Keep the present tense for a policy that applies now or at a fixed date.', _Span(t, span[0], span[1]), 'medium', ['R-3.334-policy-will-contingent'])
    for m in NEG_SUBJ_SHALL.finditer(t):
        if re.match(r"\s*that\s+no\b", m.group(0), re.I) and re.search(r"\b(?:is|are|was|were|has|have|exists?|remains?|occurs?)\b", m.group(0), re.I):
            continue  # shall ensure that no Hazardous Materials are stored ... and shall indemnify: the 2nd shall keeps its own subject
        add('negative-subject-shall', 'Shall with a negative subject reads as absence of duty, not prohibition (MSCD 3.324; house rule 8). For a prohibition on a party, use "Neither party may" or "No [person] may". When the subject is not a person (No amendment shall be effective, No failure shall operate as a waiver), it is language of policy about an event that may never happen, so it takes will (No amendment of this agreement will be effective unless ...; A failure to exercise a right will not waive it) (MSCD 3.334; 3.369); the present tense fits only a policy in force on signing or at a fixed date.', m, 'high', ['R-3.323-collective-noun-prohibition'])
    for m in SHOULD.finditer(t):
        # house rule 12: should never appears in Blake's contracts, whatever its sense; each finding gives the replacement
        if re.match(r"should\s+(?:reasonably\s+)?(?:have\s+known|know)\b", t[m.start():], re.I):
            add('should', 'Should have known: house rule 12 (no should) applies, but the words set a legal knowledge standard, so don\'t pick a '
                'replacement: offer a defined Knowledge term with wording for actual knowledge and for knowledge after reasonable inquiry '
                '(MSCD 13.506: whose knowledge counts), and ask Blake which.', m, 'high', ['R-13.506-define-knowledge'], sev=2)
            continue
        if re.search(r"\b(?:[Ii]f|[Uu]nless|[Uu]ntil|[Ii]n the event(?: that)?|[Ee]ven if|[Ww]hether)\b[^,.;:]{0,90}$", t[:m.start()]):
            add('should', 'Should in a conditional clause (house rule 12: no should): write the present tense (If Acme exercises the Option) (MSCD 3.358-3.360).', m, 'high', ['R-3.358-conditional-present-tense'], sev=2)
        else:
            add('should', 'Should (house rule 12: no should): the reader can\'t tell whether it states a duty, advice, or an expectation. '
                'For a duty use shall (MSCD 3.89); for discretion, may; for advice, recommends or delete it (MSCD 3.502); '
                'for an expectation (The Units should arrive by March 1), a duty or a statement of fact, and ask Blake which.', m, 'high', sev=1)
    for m in ONCE.finditer(t):
        add('once', 'Once: use if to introduce a condition, or delete once before an adjective phrase (rider, 2025).', m, 'medium', ['R-rider-once-if'])
    for m in WHEN_COND.finditer(t):
        add('when-condition', 'When at the start of a clause: if it introduces a condition, use if (rider).', m, 'low', ['R-rider-once-if'])
    for m in WORDY_RE.finditer(t):
        add('wordy-phrase', f'Wordy: use {WORDY[m.group(1).lower()]} (17.19).', m, 'high', ['R-17.19-wordy-phrases'])
    for m in PROVISO.finditer(t):
        add('provided-that', 'Provided that: state the relationship directly with except that, and in any event, on condition that, or a separate sentence (13.698-13.701).', m, 'high', sev=1)


# a verb of saying or choosing right before which: an embedded question, where which is a question word, not a relative pronoun
EMBEDDED_QUESTION = re.compile(r"\b(?:specif(?:y|ies|ying)|determin(?:e|es|ing)|stat(?:e|es|ing)|indicat(?:e|es|ing)|identif(?:y|ies|ying)|designat(?:e|es|ing)|"
                               r"decid(?:e|es|ing)|select(?:s|ing)?|choos(?:e|es|ing)|elect(?:s|ing)?|say(?:s|ing)?|confirm(?:s|ing)?|know(?:s|ing)?|ask(?:s|ing)?|"
                               r"(?:notify|notifies|tell|tells|inform|informs)\s+[\w'’-]+)\s*$", re.I)
# the participles a reference by heading uses: stated in the section titled "Payment"
HEADING_PARTICIPLE = re.compile(r"\b(?:stated|described|set\s+out|set\s+forth|listed|specified)\s+in\b", re.I)
# is entitled to that names something no party to this agreement owes (MSCD 3.169 bars is entitled to only where it stands in for another
# party's duty): an award or proceeds a nonparty pays, or a right that a plan, a charter, or the law creates. Every other object stays a finding.
ENTITLED_NOT_OWED = re.compile(r"\s+(?:the\s+|any\s+|all\s+|its\s+)?(?:entire\s+|full\s+)?(?:[\w-]+\s+){0,3}?(?:condemnation|eminent\s+domain|insurance)\s+(?:award|proceeds|payments?)\b|"
                               r"[^.;:]{0,80}?\b(?:under|by)\s+(?:the\s+)?(?:(?:[A-Z0-9][\w()-]*\s+){0,4}(?:Plan|Charter|Bylaws|Certificate|Policy)|applicable\s+law|law|statute)\b", re.I)


def usage_checks(t, p, add, out):
    """the EXTRA patterns (such, which, conditions, attachments, reduced passives, terms of art), reduced passives with a by-agent, and the ampersand."""
    for rx, chk, sev, msg, rules in EXTRA:
        for m in rx.finditer(t):
            if chk == 'restrictive-which' and re.search(r"\b(?:during|before|among|between|within|without|against|about|over|beyond|across|behind|"
                                                         r"below|above|beside|besides|toward|towards|throughout|including|regarding|concerning|via|per|around|"
                                                         r"near|past|since|onto|unto|despite|except|like|upon|until|of\s+all|each\s+of|any\s+of|all\s+of|some\s+of|none\s+of)\s*$", t[:m.start()], re.I):
                continue  # a preposition before which (the period during which): which is right there
            if chk == 'restrictive-which' and re.search(r"[,(]\s*$", t[:m.start()]):
                continue  # a comma or a parenthesis before which, with 2 spaces or a line break between: nonrestrictive
            if chk == 'restrictive-which' and EMBEDDED_QUESTION.search(t[:m.start()]):
                continue  # an embedded question (Buyer shall specify which Units it wants): which is a question word, and that would be wrong
            if chk == 'shall-in-condition' and re.match(r"until\b[^,.;:]{0,60}?\s+and\s+shall\b", m.group(0), re.I):
                continue  # "shall insure the Equipment until the Closing and shall name Seller": until ends the 1st duty; the 2nd shall is a new duty
            if chk == 'attachment-scheme' and re.match(r"[\w.]*\s+(?:of|to|in|under)\s+(?:the\s+)?(?:[A-Z][\w-]+\s+){1,3}(?:Agreement|Lease|Note|Plan|Indenture|Guaranty|Declaration|Credit\s+Agreement)\b", t[m.end():]):
                continue  # Schedule 2 of the Services Agreement: another agreement's own label, kept as it is (house rule 4's other-agreement default)
            if chk == 'such-pointing' and re.match(r"[^.;\"\u201c]{0,60}?,\s+(?:a|an|the|each|any)\s+\**[\"\u201c]", t[m.end():]):
                continue  # an integrated definition (each such consent, a "Required Consent"): correct (MSCD 6.74)
            if chk in ('is-entitled-to', 'category-may') and re.search(r"\b(?:states?|represents?|warrants?|acknowledges?|confirms?)(?:\s+and\s+\w+)?\s+(?:to\s+\w+\s+)?that\b[^.;]{0,120}$", t[:m.start()], re.I):
                continue  # a statement of fact that a party has a right (Seller states that it is entitled to sell the Assets)
            if chk == 'is-entitled-to' and ENTITLED_NOT_OWED.match(t, m.end()):
                # no party owes it (the entire condemnation award; benefits under the Company 401(k) Plan): a trigger for the analysis passes, not a finding
                out.append(finding(chk, msg, p['idx'], m, 'low', rules, source='rules'))
                continue
            if chk == 'reduced-passive' and re.search(r"\b(?:divided|multiplied|reduced|increased|offset|rounded|adjusted)\s+by\b", m.group(0), re.I):
                continue  # arithmetic (the Valuation Cap divided by the Fully Diluted Capitalization), not a passive that hides an actor
            if chk == 'reduced-passive':
                noun = m.group(0).split()[1]
                if noun in (PARTY_TERMS or PARTY_DEFAULT) or noun.lower() in ('parties', 'party') or re.search(r"\b(?:that|which|who|whom)\s+$", t[:m.start()]):
                    continue  # "that the Company provided to": an active relative clause, not a reduced passive
                if (noun.lower() == 'manner' or re.search(r"\bas\s*$", t[:m.start()])) and HEADING_PARTICIPLE.search(m.group(0)) \
                        and re.match(r"\s+the\s+(?:section|article|clause|paragraph)s?\s+(?:titled|entitled|captioned|headed)\b", t[m.end():]):
                    continue  # as stated in / in the manner stated in the section titled "Payment": house rule 4's form of a reference by heading.
                    # A participle that modifies a thing (the sale described in the section titled "Consent") still has a clean active form: the sale that the section titled "Consent" describes.
            add(chk, msg, m, 'medium', rules, sev=sev if sev_is_free(chk, rules) else None)
    for m in REDUCED_BY.finditer(t):
        before = t[:m.start()].rstrip()
        prev = before.split()[-1].lower().strip('",;:(') if before.split() else ''
        if not prev or prev in REDUCED_SKIP or re.search(r"\b(?:that|which|who|whom)\s+(?:\w+\s+){0,3}$", before + ' ') or not re.match(r"[a-z]", prev):
            continue
        if any(f['check'] == 'reduced-passive' and f['start'] <= m.start() < f['end'] + 1 for f in out):
            continue
        if re.match(r"(?:divided|multiplied|reduced|increased|offset|rounded|adjusted)\s+by\b", m.group(0), re.I):
            continue  # arithmetic (X divided by Y), not a passive that hides an actor
        if (before.split()[-1] in (PARTY_TERMS or PARTY_DEFAULT) or prev in ('parties', 'party')) and not re.search(r"\bby\s+(?:the\s+|a\s+|an\s+|each\s+|any\s+)?[A-Z]", m.group(0)):
            continue  # "the parties agreed by email": an active verb after its subject; "Information disclosed by the Disclosing Party" names an actor, so it is a reduced passive
        add('reduced-passive', 'Possible reduced passive (a past participle after a noun, short for "that are sold by ..."). House rule 1: recast in the active if a clean form exists ("Licensed Products that Licensee sells"); otherwise leave it.', m, 'medium', ['R-3.15-active-voice'])
    for m in AMP.finditer(t):
        if re.match(r"[^.;:]{0,40}?\b(?:LLC|L\.L\.C\.|LLP|L\.L\.P\.|PLLC|Inc\.?|P\.A\.|P\.C\.|Co\.|Company|Corporation|Corp\.|Ltd\.?|LP|L\.P\.|Partners)\b", t[m.end():], re.I):
            continue  # inside a business or law-firm name (rider: keep it there)
        add('ampersand', 'Ampersand: keep only inside a business or law-firm name; otherwise and (rider).', m, 'medium', ['R-rider-ampersand'])


def reference_checks(t, p, add, out):
    """numbered and relative cross-references (house rule 4)."""
    for m in XREF.finditer(t):
        lead = re.match(r"\D*(\d+)", m.group(0))
        if lead and int(lead.group(1)) >= 100 or re.search(r"(?:C\.F\.R\.|U\.S\.C\.|Code|Regulations?|Act|Rule|Ann\.|Stat\.|Statutes|Regs?\.)\s*$", t[:m.start()]) \
                or re.match(r"(?:§|Section|Sections|Sec\.)\s*\d+[-–]\d+[-–.]\d", m.group(0)) \
                or re.match(r"(?:§|Section|Sections|Sec\.)\s*\d+(?:[-–.]\d+)*(?:\s*\([a-z0-9]{1,4}\))*(?:\s*(?:,|and|or|through)\s*(?:§|Section|Sections)?\s*\d+(?:[-–.]\d+)*(?:\s*\([a-z0-9]{1,4}\))*)*\s+of\s+(?:the\s+)?(?:[A-Z][\w.]*\s+){0,5}(?:Code|Act|Statutes|Regulations|Annotated)\b", t[m.start():]):
            continue  # Section 164.308; 17 U.S.C. Section 101; Tenn. Code Ann. § 47-18-104; § 1542 of the Civil Code: references to statutes and regulations
        if not t[:m.start()].strip(' #*_>'):
            continue  # a heading's own label (Section 3.01 Use.), not a cross-reference; the outline check covers numbering
        if re.match(r"[^.;]{0,40}?\b(?:of|in|under|to)\s+the\s+(?:[A-Z][\w-]+\s+){1,3}(?:Agreement|Lease|Note|Plan|Indenture|Guaranty|Declaration|Charter|Bylaws)\b", t[m.end():]):
            add('numbered-cross-reference', "Reference to another agreement's section: keep its number, and add its heading when it has one (Section 4 (Payment) of the Original Agreement); the house rule on cross-references governs references inside this contract (SKILL.md hard cases).", m, 'medium', ['R-4.100-crossref-name-and-number'], sev=3)
            continue
        add('numbered-cross-reference', 'Numbered cross-reference; house rule: avoid cross-references, and refer by heading where one is needed (house-style.md section 4).', m, 'high', ['R-4.100-crossref-name-and-number'])
    for m in REL_XREF.finditer(t):
        if m.group(0).lower() in ('above', 'below') and (re.search(r"\b(?:at|or|is|are|falls?|drops?|rises?|goes|prices?|amounts?|rates?|levels?|costs?|values?|sales|revenues?|temperatures?|grades?|percentages?|figures?)\s+(?:or\s+)?$", t[:m.start()], re.I)
                                                         or re.match(r"\s+(?:or\s+(?:above|below)\b|\$|\d|[A-Z][\w-]*(?:\s+[A-Z][\w-]*)*['\u2019]s\s|(?:its|their|his|her|that\s+party['’]s|each\s+party['’]s|the\s+(?:[\w-]+\s+)?[\w-]+['’]s)\s+(?:name\s+and\s+)?signatures?|the\s+(?:[\w-]+\s+){0,2}(?:threshold|level|limit|cap|amount|rate|minimum|maximum|price|budget|estimate|signatures?))", t[m.end():])):
            cleared(out, p, m, ['R-7.23-contract-reference-ambiguity', 'R-7.26-specific-section-refs'])
            continue  # a comparison (at or below 5%), not a pointer to another provision
        add('contract-reference', 'Here-word or above/below reference: ambiguous contract reference (7.23-7.27); name the provision by heading.', m, 'high', sev=2)


def attachment_checks(t, p, add, out):
    """attachment references (house rule 6; MSCD 5.77-5.99)."""
    for m in ATT_LOWER.finditer(t):
        add('attachment-capitals', 'Attachment reference in lowercase; house rule is Schedule A, Exhibit 2.', m, 'high', sev=2)
    for rx, chk, msg, rid in ((ATT_HERETO, 'attachment-hereto', 'Drop hereto / attached hereto / to this agreement from attachment references (5.77).', 'R-5.77-no-hereto-attachments'),
                              (ATT_ON, 'attachment-on', 'Say in Schedule X, not on (or at) Schedule X (5.95).', 'R-5.95-in-not-on-schedule'),
                              (ATT_PART, 'attachment-part-of', 'For an attachment, delete forms part of this agreement or incorporated by reference: an attachment is part of the agreement without it (5.96-5.99). To bring in another agreement\'s provisions, keep the concept and say it in plain words (Sections 4 to 7 of the Prime Lease apply to Subtenant as if Subtenant were the tenant under it) (13.408-13.414).', 'R-5.96-dont-say-part-of'),
                              (ATT_QUOTE, 'attachment-quotes', 'No quotation marks around an attachment designation (5.78).', 'R-5.78-no-emphasis-attachment-refs')):
        for m in rx.finditer(t):
            add(chk, msg, m, 'high', [rid], sev=3 if sev_is_free(chk, [rid]) else None)
    if re.search(r"\b(?:Schedule|Exhibit|SCHEDULE|EXHIBIT)s?\s+[A-Z0-9]", t):
        add('attachment-check', 'Attachment mentioned: confirm schedule-versus-exhibit classification, order and references (attachments.md).', None, 'low', sev=3)


def date_checks(t, p, add, out):
    """dates (house rule 7), a weekday that does not match its date, a termination-notice period, and the headings clause."""
    for m in DMY.finditer(t):
        add('day-month-year', 'Day-month-year date; house rule 7 is the U.S. form (January 1, 2027) (MSCD 10.7 differs).', m, 'high', ['R-10.7-day-month-year'])
    for m in NUMDATE.finditer(t):
        add('numeric-date', 'Numerical date: 2/3/2027 can be read as February 3 or March 2; write January 1, 2027 (MSCD 10.13; house rule 7).', m, 'high', ['R-10.13-no-numerical-dates'])
    for m in THIS_DAY.finditer(t):
        add('this-day', 'Archaic date form (this __ day of); write January 1, 2027 (MSCD 10.11).', m, 'high', ['R-10.11-no-this-day-of'])
    for m in DATE_WORDS.finditer(t):
        wd, mon, day, yr = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
        try:
            real = datetime.date(yr, MONTHS.index(mon) + 1, day)
        except ValueError:
            add('date-conflict', f'{mon} {day}, {yr} is not a real date; state the date intended.', m, 'high', [], sev=1)
            continue
        if wd and real.strftime('%A') != wd:
            add('date-conflict', f'{mon} {day}, {yr} is a {real.strftime("%A")}, not a {wd}; drop the weekday or correct the date.', m, 'high', [], sev=1)
    for m in TERM_NOTICE.finditer(t):
        add('termination-notice', 'Terminate by giving (or upon, or with) N days\' notice: unclear whether termination happens when notice is given or when the period ends. Write: "... may terminate this agreement by notifying the other party; the termination will be effective N days after the other party receives the notice", or N days after [party] gives the notice; offer both and ask which the parties intend (MSCD 13.627; 10.62; will, because the termination is a contingent future event, 3.334).', m, 'high', ['R-13.623-termination-prior-notice'])
    for m in HEADINGS_CLAUSE.finditer(t):
        sent = sentence_at(t, m.start())
        if re.search(r"\bby\s+(?:its|their)\s+headings?\b|\bheadings?\s+identif|\breference\s+to\s+(?:a|an|the)\s+(?:section|article|provision|schedule|exhibit)s?\s+by\b", sent, re.I) \
                and not re.search(r"\bconvenience\b|\bdo(?:es)?\s+not\s+(?:affect|limit|define|govern)\b|\bno\s+(?:legal\s+)?effect\b", sent, re.I):
            continue  # a clause that makes references by heading work: house rule 4 wants it
        add('headings-clause', 'Headings-for-convenience clause: always delete it, or limit it so it doesn\'t undercut references by heading (house rule 4; MSCD 15.18).', m, 'high', ['R-15.18-rule-headings'])


CAPS_BODY_WORDS = 8  # a title or an article heading is shorter; body text in capitals runs on
CAPS_HEADING = re.compile(r"^[\s#>*_]*(?:ARTICLE|EXHIBIT|SCHEDULE|ANNEX|APPENDIX|ATTACHMENT)\s+[IVXLC\d]+|^[\s#>*_]*[IVXLC]+\.\s")  # an article or attachment heading: capitals are right there (MSCD 4.10; 16.18)
CONSPICUOUS = re.compile(r"\b(?:DISCLAIM\w*|WARRANT\w*|MERCHANTABILITY|FITNESS|AS\s+IS|LIABILITY|CONSEQUENTIAL|NEGLIGENCE)\b")


def format_checks(t, p, add, out):
    """the paragraph's formatting (house rule 9): justified, underlined, off-house font or size."""
    f = p.get('fmt') or {}
    if f.get('justified'):
        add('justified', 'Justified paragraph; use ragged right (16.16-16.17; clean visual lines).', None, 'high')
    if f.get('underline'):
        add('underline', 'Underlined text; don\'t underline (16.21).', None, 'high')
    bad_fonts = [x for x in f.get('fonts', []) if off_house_font(x)]
    if bad_fonts:
        via = f.get('font_styles') or []
        add('font', f'Font {", ".join(bad_fonts)}; house rule is 12-point Aptos.' + (
            f' The font comes from the {" and the ".join(via)}: change the style itself, and say so in 1 comment, because a style change doesn\'t show as a tracked change.' if via else ''), None, 'high')
    bad_sizes = [s for s in f.get('sizes', []) if off_house_size(s)]
    if bad_sizes:
        add('font-size', f'Font size {", ".join(map(str, bad_sizes))} pt; house rule is 12 point.', None, 'medium')
    if len(t.split()) >= CAPS_BODY_WORDS and t == t.upper() and re.search(r"[A-Z]", t) and not CAPS_HEADING.match(t):
        if CONSPICUOUS.search(t):
            # a conspicuous disclaimer: MSCD 16.19 prefers bold for conspicuousness, but a statute-driven form (UCC 2-316, 1-201(b)(10)) stays; a trigger for the analysis passes
            out.append(finding('capitals-body', 'A paragraph in all capitals that reads as a conspicuous disclaimer or limitation: MSCD 16.19 prefers bold for conspicuousness, '
                               'but a form a statute drives (UCC 2-316: a conspicuous warranty disclaimer) stays as it is; confirm which this is (house rule 9).', p['idx'], None, 'low',
                               ['R-16.18-caps-headings-names'], source='rules', match=t[:60]))
        else:
            add('capitals-body', 'A paragraph in all capitals: house rule 9 and MSCD 16.18-16.19 use sentence case for body text; capitals are for article headings and party names in the introductory clause and signature blocks.',
                _Span(t, 0, min(len(t), MATCH_CUT)), 'medium', ['R-16.18-caps-headings-names'])


# a heading quoted in a reference (the section titled "Financial Covenants"; the article captioned "Restrictive Covenants"); a quoted
# defined term (the "Covenants") has no titled/captioned/headed before it and stays
HEADING_REF = re.compile(r"\b(?:titled|entitled|captioned|headed)\s+[\"“]([^\"”\n]{1,80})[\"”]")


def in_heading_reference(t, a, b):
    """True when t[a:b] sits inside the quoted title of a heading reference."""
    return any(m.start(1) <= a and b <= m.end(1) for m in HEADING_REF.finditer(t))


def variant_checks(t, p, add, out):
    """the data-driven phrase variants (data/phrase-variants.json)."""
    # phrase variants from data/phrase-variants.json: other ways drafters write the same problems
    for c in phrase_variants():
        for m in c['rx'].finditer(t):
            if c['not_rx'] is not None:
                lo, hi = sentence_bounds(t, m.start(), m.end())
                if c['not_rx'].search(t, max(lo, m.start() - c['ctx']), min(hi, m.end() + c['ctx'])):
                    continue  # a look-alike in the same sentence; a word in the next sentence doesn't excuse this one
            if any(o['check'] == c['check'] and o['start'] < m.end() and o['end'] > m.start() for o in out):
                continue  # another check already reports this problem here
            if c['check'] == 'usage' and in_heading_reference(t, m.start(), m.end()):
                continue  # the section titled "Financial Covenants": the reference quotes the heading word for word; the heading's own finding carries the fix
            if c.get('not_party') and any(re.search(r"(?<![\w-])" + re.escape(p) + r"(?:['’]s)?(?![\w-])", m.group(0)) for p in PARTY_TERMS | PARTY_COLLECTIVE):
                continue  # the match names a party (Licensee shall obtain Licensor's approval): the other party's consent is a deal term, not a nonparty's
            # own_severity: the entry's severity governs, not its rule record's (a narrower case than the rule)
            add(c['check'], c['message'], m, c.get('confidence', 'high'), c['rule_ids'], sev=c['severity'] if c.get('own_severity') or sev_is_free(c['check'], c['rule_ids']) else None)


HOUSE_SECTIONS = (passive_checks, signature_checks, party_verb_checks, number_checks, spacing_list_checks, policy_checks, usage_checks,
                  reference_checks, attachment_checks, date_checks, format_checks, variant_checks)  # in this order: later sections read earlier findings


def cleared(out, p, m, rules):
    """The house check judged this word correct here: a marker that stops the rules channel from reporting it in this paragraph
    (run() drops the marker before returning)."""
    out.append(finding('_cleared', '', p['idx'], m, 'high', rules, sev=3))


def house_checks(p):
    """Every house check on 1 paragraph, in HOUSE_SECTIONS order; each section has the shape (t, p, add, out)."""
    t = p['text']
    out = []

    def add(check, msg, m=None, conf='high', rules=(), sev=None):
        """Record a finding in this paragraph and return it. sev=None takes the severity policy's value; an explicit sev is kept."""
        f = finding(check, msg, p['idx'], m, conf, rules, sev=sev)
        out.append(f)
        return f
    for section in HOUSE_SECTIONS:
        section(t, p, add, out)
    return out


_VARIANTS = None
BAD_VARIANTS = []  # phrase-variant entries that are malformed (a missing field, a pattern that doesn't compile)


def variant_problem(c):
    """What is wrong with a phrase-variant entry, or None. The lint skips a bad entry, and the self-test fails on it."""
    if not isinstance(c, dict):
        return 'not an object'
    for k, typ in (('id', str), ('check', str), ('pattern', str), ('message', str), ('severity', int), ('rule_ids', list)):
        if not isinstance(c.get(k), typ):
            return f'field {k} is missing or not a {typ.__name__}'
    if type(c['severity']) is not int or c['severity'] not in (1, 2, 3):
        return f"severity {c['severity']} is not 1, 2 or 3"
    for k in ('id', 'check', 'pattern', 'message'):
        if not c[k].strip():
            return f'field {k} is empty'
    if not all(isinstance(r, str) for r in c['rule_ids']):
        return 'rule_ids must be strings'
    for k in ('examples', 'lookalikes'):
        if not isinstance(c.get(k, []), list) or not all(isinstance(x, str) for x in c.get(k, [])):
            return f'{k} must be a list of strings'
    if not isinstance(c.get('own_severity', False), bool) or not isinstance(c.get('not_party', False), bool):
        return 'own_severity and not_party must be true or false'
    if type(c.get('ctx', 40)) is not int or c.get('ctx', 40) < 0 or not isinstance(c.get('flags', ''), str):
        return 'ctx must be a whole number of 0 or more and flags a string'
    fl = re.I if 'i' in c.get('flags', '') else 0
    for k in ('pattern', 'not'):
        if c.get(k):
            try:
                rx = re.compile(c[k], fl)
            except re.error as e:
                return f'{k} does not compile ({e})'
            if k == 'pattern' and rx.fullmatch('') is not None:
                return 'pattern matches the empty string'
    return None


def _variant_entries(data):
    """The entries of the phrase-variants file, or InputError when the file has the wrong shape (a list, or no "checks" list):
    a wrong shape would otherwise disable every variant check without a word."""
    if not isinstance(data, dict) or not isinstance(data.get('checks'), list):
        raise InputError(f'{VARIANTS_PATH}: expected an object with a "checks" list')
    return data['checks']


def phrase_variants():
    """The data-driven checks in data/phrase-variants.json, compiled once. Each has a pattern, an optional
    exclusion (a look-alike that is correct, searched within ctx characters of the match), a severity,
    rule ids, a message, and examples and look-alikes that the self-test runs."""
    global _VARIANTS
    if _VARIANTS is None:
        _VARIANTS = []
        try:
            entries = _variant_entries(read_json(VARIANTS_PATH, 'the phrase-variant checks'))
        except InputError as e:
            LOAD_ERRORS.append(str(e))  # main() stops with exit 2, like a damaged terms-of-art file; the self-test fails
            return _VARIANTS
        for c in entries:
            if isinstance(c, dict):  # the uppercase party list is the code's (PARTY_DEFAULT), filled in here
                c = dict(c, **{k: c[k].replace('{party_caps}', PARTY_CAPS) for k in ('pattern', 'not') if isinstance(c.get(k), str)})
            problem = variant_problem(c)
            if problem:
                BAD_VARIANTS.append(f"{c.get('id', '?') if isinstance(c, dict) else '?'}: {problem}")
                continue  # 1 bad entry must not stop the whole lint; the self-test reports it
            fl = re.I if 'i' in c.get('flags', '') else 0
            _VARIANTS.append(dict(c, rx=re.compile(c['pattern'], fl), not_rx=re.compile(c['not'], fl) if c.get('not') else None, ctx=c.get('ctx', 40)))
    return _VARIANTS


_TERMS_OF_ART = None
TOA_FIELDS = ('id', 'term_word', 'legal_meaning', 'legal_def', 'legal_use', 'name_other', 'def_other', 'uses_other', 'replace')


def terms_of_art():
    """The terms of art in data/terms-of-art.json, compiled once (house rule 13). A missing or bad file is an error:
    without it the check would silently do nothing."""
    global _TERMS_OF_ART
    if _TERMS_OF_ART is None:
        _TERMS_OF_ART = []
        try:
            data = read_json(TERMS_OF_ART_PATH, 'the terms of art')
            _TERMS_OF_ART = [dict(e, rx=_toa_regexes(e)) for e in _toa_entries(data)]
        except InputError as e:
            LOAD_ERRORS.append(str(e))  # main() stops with exit 2; the self-test fails
    return _TERMS_OF_ART


def _toa_entries(data):
    if not isinstance(data, dict) or not isinstance(data.get('terms'), list):
        raise InputError(f'{TERMS_OF_ART_PATH}: expected an object with a "terms" list')
    for e in data['terms']:
        if not isinstance(e, dict):
            raise InputError(f'{TERMS_OF_ART_PATH}: a term is not an object')
        missing = [k for k in TOA_FIELDS if k not in e]
        if missing:
            raise InputError(f"{TERMS_OF_ART_PATH}: term {e.get('id', '?')} lacks {', '.join(missing)}")
        if not isinstance(e['term_word'], str) or not e['term_word']:
            raise InputError(f"{TERMS_OF_ART_PATH}: term {e.get('id', '?')} needs a term_word pattern")
        for k in ('examples', 'lookalikes'):
            if not isinstance(e.get(k, []), list) or not all(isinstance(x, str) for x in e.get(k, [])):
                raise InputError(f"{TERMS_OF_ART_PATH}: term {e.get('id', '?')}: {k} must be a list of strings")
    return data['terms']


def _toa_regexes(e):
    out = {}
    for k in ('term_word', 'legal_def', 'legal_use', 'name_other', 'def_other', 'uses_other'):
        if e[k] and not isinstance(e[k], str):
            raise InputError(f"{TERMS_OF_ART_PATH}: term {e['id']}: {k} must be a string")
        try:
            out[k] = re.compile(e[k], re.I) if e[k] else None
        except re.error as err:
            raise InputError(f"{TERMS_OF_ART_PATH}: term {e['id']}: {k} does not compile ({err})")
    return out


# a 2nd term defined in the same parenthetical: (the "Buyer" or "Purchaser"); the forms a sentence defines a term with:
# the last day is the "Separation Date."; The "Term" starts on ...; a Member is "Disabled" if ...
SECOND_TERM = re.compile(r"\b(?:or|and)\s+(?:the\s+|a\s+|an\s+)?\**" + QO + r"\**([A-Z]" + QT + r"{0,60}?)\**" + QC)
IS_A_TERM = re.compile(r"\b(?:is|are|becomes)\s+(?:the|a|an|each)\s+\**" + QO + r"\**([A-Z]" + QT + r"{0,40}?)[.,]?\**" + QC)
THE_TERM_IS = re.compile(r"\b[Tt]he\s+\**" + QO + r"\**([A-Z]" + QT + r"{0,40}?)\**" + QC + r"\**\s+(?:is|are|starts|begins|ends|runs|consists)\b")
IS_TERM_IF = re.compile(r"\b(?:is|are)\s+\**" + QO + r"\**([A-Z]" + QT + r"{0,40}?)\**" + QC + r"\**\s+(?:if|when|while|during)\b")


def _sentence_words(t, m):
    """The words of the sentence that defines m's term (group 1), without the quoted term and a leading determiner, so the
    circular-definition check sees what the definition rests on (Each task that Seller gives Buyer is an "Assignment.")."""
    lo, hi = sentence_bounds(t, m.start(1), m.end(1))
    words = t[lo:m.start(1)].rstrip('*"“‘\' ') + ' ' + t[m.end(1):hi].lstrip('*"”’\'.,')
    return re.sub(r"^\s*(?:The|A|An|Each|Any|Every|This|That|These|Those|No|All|Such)\s+", '', words)


def definitions(paras):
    """Each definition in the contract: (term, the words that define it, paragraph, start, end of the term, kind), in order.
    kind is 'integrated' (a parenthetical), 'sentence' (a sentence that makes a term: is the "X", the "X" is, is "X" if; the
    inventory lists it as integrated), 'autonomous' ("X" means ...), or 'pointer' ("X" has the meaning in ...). A comma or period typed inside the closing quotation mark
    isn't part of the term. The same definition read by 2 patterns counts once (the dedupe on kind, paragraph and position)."""
    out = []
    for p in paras:
        t = p['text']
        for m in INTEG.finditer(t):
            cut = max(t.rfind('.', 0, m.start()), t.rfind(';', 0, m.start()))
            # the defining words: the text before the parenthetical, plus its scope noun (that position, the "Title")
            words = t[cut + 1:m.start()] + ' ' + m.group(0)[:m.start(1) - m.start()]
            out.append((m.group(1).strip().rstrip(',.;:'), words, p['idx'], m.start(1), m.end(1), 'integrated'))
            close = t.find(')', m.end())
            for m2 in SECOND_TERM.finditer(t, m.end(), close if close > 0 else m.end() + 120):
                out.append((m2.group(1).strip().rstrip(',.;:'), words, p['idx'], m2.start(1), m2.end(1), 'integrated'))
        dt = def_text(t)
        off = len(t) - len(dt)  # def_text strips a prefix only
        dm = AUTON.match(dt)
        if dm:
            out.append((dm.group(1).strip().rstrip(',.;:'), sentence_from(t, off + dm.end()), p['idx'], off + dm.start(1), off + dm.end(1),
                        'pointer' if re.search(r"\b(?:has|shall have)\b", dm.group(0)) else 'autonomous'))
        for m in list(AUTON_INNER.finditer(t)) + list(AUTON_LEAD.finditer(t)):
            out.append((m.group(1).strip().rstrip(',.;:'), sentence_from(t, m.end()), p['idx'], m.start(1), m.end(1),
                        'pointer' if re.search(r"\bhas\b", m.group(0)) else 'autonomous'))
        for rx in (IS_A_TERM, THE_TERM_IS, IS_TERM_IF):
            for m in rx.finditer(t):
                out.append((m.group(1).strip().rstrip(',.;:'), _sentence_words(t, m), p['idx'], m.start(1), m.end(1), 'sentence'))
    seen, uniq = set(), []
    for d in sorted(out, key=lambda d: (d[2], d[3])):  # a stable sort: at 1 position, the parenthetical reading comes before the sentence reading
        key = ('integrated' if d[5] == 'sentence' else d[5], d[2], d[3])
        if key not in seen:
            seen.add(key)
            uniq.append(d)
    return uniq


def term_of_art_checks(paras):
    """House rule 13: a term of art of contract law keeps its legal meaning. Reports a defined term built on a term of art
    that names something else (an Assignment that is a work order), and an ordinary word used in another sense
    (marketing collateral), at severity 1 when the contract also uses the word in its legal sense."""
    out = []
    full = '\n'.join(p['text'] for p in paras)
    defs = definitions(paras)
    defined_lower = {d[0].lower() for d in defs}
    for e in terms_of_art():
        rx = e['rx']
        legal_here = bool(rx['legal_use'] and rx['legal_use'].search(full))
        sev = 1 if legal_here else 2
        both = f' The contract also uses {e["id"]} in its legal sense, so 1 word carries 2 meanings.' if legal_here else ''
        for term, deftext, pidx, st, en, _kind in defs:
            if not rx['term_word'].search(term) or (e.get('only_with_legal_use') and not legal_here):
                continue  # only_with_legal_use: the other sense is common and harmless unless the contract also uses the legal one
            named_other = bool(rx['name_other'] and rx['name_other'].search(term))
            def_other = bool(rx['def_other'] and rx['def_other'].search(deftext)) and not (rx['legal_def'] and rx['legal_def'].search(deftext))
            if named_other or def_other:
                out.append(finding('term-of-art-defined', f'"{term}" uses {e["id"]}, a term of art that means {e["legal_meaning"]}; here it names something else.{both} '
                                   f'Rename it ({e["replace"]}) and change every use (house rule 13; MSCD 1.57).', pidx, None,
                                   'high' if legal_here else 'medium', ['R-1.57-one-word-one-meaning'], sev=sev, match=term, start=st, end=en))
        if not rx['uses_other'] or (e.get('only_with_legal_use') and not legal_here):
            continue
        for p in paras:
            for m in rx['uses_other'].finditer(p['text']):
                if m.group(0)[0].isupper() or m.group(0).lower() in defined_lower:
                    continue  # part of a defined term: the definition check reports it
                out.append(finding('term-of-art', f'"{m.group(0)}" uses {e["id"]} in another sense; as a term of art it means {e["legal_meaning"]}.{both} '
                                   f'Use another word ({e["replace"]}) (house rule 13; MSCD 1.57).', p['idx'], m,
                                   'high' if legal_here else 'medium', ['R-1.57-one-word-one-meaning'], sev=sev))
    return out


def roman_value(s):
    vals = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100}
    s = s.lower()
    if not s or any(ch not in vals for ch in s):
        return 0
    total = 0
    for a, b in zip(s, s[1:] + ' '):
        total += -vals[a] if b != ' ' and vals[a] < vals[b] else vals[a]
    return total if 0 < total < 40 else 0


SMALL_WORDS = r"(?:of|and|or|the|to|for|in|on|by|with|a|an|from|under|upon|as|at|after|before|between|during|into|over|without|within|per|through|against|among|about|following|not|nor|vs\.?|versus)"
# a run-in section heading (Return of Materials.  Consultant shall ...) or a heading line
RUNIN_HEAD = re.compile(r"^[*_]*[A-Z][\w'’-]*[;,]?(?:\s+(?:" + SMALL_WORDS + r"|[A-Z0-9][\w'’-]*[;,]?))*?[*_]*\.[*_]*(?:\s|$)")  # Section 409A. is a heading


def heading_of(rest):
    """The heading at the start of a section's text (Return of Materials; SERVICES), or None: a run-in heading that ends in a
    period, or a heading line of up to 8 capitalized words."""
    rest = rest.strip()
    m = RUNIN_HEAD.match(rest)
    if m and len(m.group(0).split()) <= 8:
        return re.sub(r"[*_]+", '', m.group(0)).strip().rstrip('.').strip()
    words = re.sub(r"[*_]+", '', rest).rstrip('.: ').split()
    if 1 <= len(words) <= 8 and all(w[0].isupper() or not w[0].isalpha() or re.fullmatch(SMALL_WORDS, w) for w in words):
        return ' '.join(words)
    return None


# outline levels, outermost first (house rule 3: I., A., 1., (a), (i)); a decimal number (1.1) and another enumerator ((1), 1)) sit outside the scheme
LVL_ARTICLE, LVL_SECTION, LVL_SUBSECTION, LVL_CLAUSE, LVL_SUBCLAUSE, LVL_OTHER, LVL_DECIMAL = 0, 1, 2, 3, 4, 8, 9
ENUM_RE = re.compile(r"^[\s#>*_]*(?:(?:Article|ARTICLE|Section|SECTION)\s+)?(\d+(?:\.\d+)+\.?|[IVXLC]+\.|[A-Z]\.|\d+\.|\(\d+\)|\([a-z]{1,4}\)|\d+\))(?=\s)")


def outline_checks(paras, shape):
    """House rule 3: I. (articles), A. (sections), 1. (subsections), (a) (clauses), (i) (subclauses); no only child."""
    items = []

    def labeled(p):
        # the typed or Word-numbered label plus the text; "Article I" (no period, lvlText "Article %1") counts as the roman label I.
        t_enum = (p['auto_label'] + ' ' + p['text']) if p.get('auto_label') else p['text']
        return re.sub(r"^([\s#>*_]*(?:Article|ARTICLE)\s+[IVXLC]+)(?=\s|$)", r"\1.", t_enum)

    texts = [labeled(p) for p in paras]
    has_roman2 = any(re.match(r"^[\s#>*_]*(?:(?:Article|ARTICLE)\s+)?II\.", x) for x in texts)
    has_small_roman2 = any(re.search(r"\(ii\)", x) for x in texts)
    last = {'upper': 0, 'lower': 0}  # value of the last roman numeral seen at each case
    last_letter = {'upper': '', 'lower': ''}  # the last letter label seen at each case
    letter_level = {'upper': None, 'lower': None}  # the Word list level of that letter label, when Word numbers it

    def is_roman(core, case, nxt, word_level):
        """Is this 1-character label (I, V, X, i, v, x, ...) a roman numeral? nxt is the next enumerator's core, and
        word_level the paragraph's Word list level (None when the number is typed)."""
        v = roman_value(core)
        if not v:
            return False
        if len(core) > 1:
            return True  # II, IV, ix: a letter label is never 2 characters
        if last_letter[case] and ord(core) == ord(last_letter[case]) + 1:
            # I. after H., (i) after (h): house rule 3 uses every letter, so this is usually the next section or clause.
            # Word's own list level settles it; for a typed (i), the (ii) right after it makes it a subclause. The
            # section I. after H. with the article II. after it stays a section (the article is not its sibling).
            if word_level is not None and letter_level[case] is not None:
                return word_level > letter_level[case]
            return case == 'lower' and core == 'i' and nxt == 'ii'
        if core.lower() == 'i':
            return has_roman2 if case == 'upper' else has_small_roman2
        return last[case] + 1 == v  # V after IV, X after IX; otherwise C, D, L, V, X are letters

    enumerated = [(p, m) for p in paras for m in [ENUM_RE.match(labeled(p))] if m and p.get('where') == 'body']
    for n, (p, m) in enumerate(enumerated):
        tok = m.group(1)
        core = re.sub(r"[().]", '', tok)
        nxt = re.sub(r"[().]", '', enumerated[n + 1][1].group(1)) if n + 1 < len(enumerated) else ''
        word_level = p.get('auto_level')
        if re.fullmatch(r"\d+(?:\.\d+)+\.?", tok):
            lvl, kind = LVL_DECIMAL, 'decimal'
        elif re.fullmatch(r"[IVXLC]+\.", tok) and is_roman(core, 'upper', nxt, word_level):
            lvl, kind = LVL_ARTICLE, 'roman'
            last['upper'] = roman_value(core)
            last_letter['upper'] = ''
        elif re.fullmatch(r"[A-Z]\.", tok):
            lvl, kind = LVL_SECTION, 'letter'
            last_letter['upper'], letter_level['upper'] = core, word_level
        elif re.fullmatch(r"\d+\.", tok):
            lvl, kind = LVL_SUBSECTION, 'digit'
        elif re.fullmatch(r"\([ivxlc]+\)", tok) and is_roman(core, 'lower', nxt, word_level):
            lvl, kind = LVL_SUBCLAUSE, 'small-roman'
            last['lower'] = roman_value(core)
        elif re.fullmatch(r"\([a-z]{1,2}\)", tok):
            lvl, kind = LVL_CLAUSE, 'small-letter'
            last_letter['lower'], letter_level['lower'] = core, word_level
        else:
            lvl, kind = LVL_OTHER, 'other'  # (1) or 1)
        items.append((p['idx'], lvl, kind, tok, m))
    out = []
    auto = {p['idx'] for p in paras if p.get('auto_label')}
    text_of_all = {p['idx']: p['text'] for p in paras}
    # a Word document only: a .docx paragraph carries its fonts in fmt; a .md file has bold but no fonts, and Markdown or plain
    # text can't carry Word's native numbering, so typed numbers there are no finding
    typed = [p for p in paras if p.get('where') == 'body' and not p.get('auto_label') and 'fonts' in (p.get('fmt') or {})
             and ENUM_RE.match(p['text'])]
    if len(typed) >= 3 and not auto:
        out.append(finding('typed-numbering', f'{len(typed)} paragraphs have numbers typed into the text; house rule 3 uses Word\'s native multilevel numbering, so numbers update when provisions move.',
                           typed[0]['idx'], match=ENUM_RE.match(typed[0]['text']).group(1)))
    def add(idx, msg, m):
        if idx in auto:
            msg += ' (Word automatic numbering: the number is in the list definition, not the text.)'
        out.append(finding('enumeration', msg, idx, rules=['R-4.11-article-numerals'], match=m.group(1),
                           start=-1 if idx in auto else m.start(1), end=-1 if idx in auto else m.end(1)))
    if not items:
        return out
    first_dec = next((it for it in items if it[2] == 'decimal'), None)
    if first_dec:
        add(first_dec[0], 'Decimal numbering (1.1, 1.1(a)); house rule 3 uses I. (articles), A. (sections), 1. (subsections), (a), (i).', first_dec[4])
    other = next((it for it in items if it[2] == 'other'), None)
    if other:
        add(other[0], f'Enumerator {other[3]}; house rule 3 uses (a) for clauses and (i) for subclauses.', other[4])
    kinds = {it[2] for it in items}
    if 'digit' in kinds and not kinds & {'letter', 'roman'} and not first_dec:
        it = next(it for it in items if it[2] == 'digit')
        add(it[0], 'Top-level sections numbered 1., 2.; house rule 3 numbers sections A., B. (under articles I., II.), and keeps 1. for subsections.', it[4])
    # only child: a level that has a 1st item but no 2nd before its parent level moves on
    starts = {}
    seq = [it for it in items if it[1] < LVL_OTHER]
    for n, it in enumerate(seq):
        idx, lvl, kind, tok, m = it
        for deeper in [k for k in list(starts) if k > lvl]:
            first, count = starts.pop(deeper)
            if count == 1:
                add(first[0], f'Only child: {first[3]} has no sibling at its level (house rule 3).', first[4])
        if lvl in starts and starts[lvl][0][2] == kind:
            starts[lvl] = (starts[lvl][0], starts[lvl][1] + 1)
        else:
            starts[lvl] = (it, 1)
    for lvl, (first, count) in starts.items():
        if count == 1 and lvl > min(it[1] for it in seq):
            add(first[0], f'Only child: {first[3]} has no sibling at its level (house rule 3).', first[4])
    # article headings are in capitals (MSCD 4.10; house rule 3)
    low_art = [it for it in items if it[2] == 'roman' and re.search(r"[a-z]", re.sub(r"[*_#]", '', (text_of_all.get(it[0], '')[it[4].end():] if not it[0] in auto else text_of_all.get(it[0], ''))))]
    if low_art:
        it = low_art[0]
        out.append(finding('article-heading', f'{len(low_art)} article headings are not in all capitals; house rule 3 and MSCD 4.10 put article headings in capitals.',
                           it[0], rules=['R-4.10-article-heading-caps'], match=it[4].group(1)))
    # each section needs a heading (MSCD 4.21); house rule 4 refers to provisions by heading
    secs = [it for it in items if it[2] == 'decimal' and it[3].rstrip('.').count('.') == 1]
    if not secs and seq:
        lv = LVL_SECTION if any(it[2] == 'roman' for it in items) else min(it[1] for it in seq)
        secs = [it for it in seq if it[1] == lv]
    text_of = {p['idx']: ((p['auto_label'] + ' ' + p['text']) if p.get('auto_label') else p['text']) for p in paras}
    att = shape['attachments']
    secs = [it for it in secs if it[0] < att and not re.match(r"\s*\*{0,2}[\"“]", text_of[it[0]][it[4].end():])]  # skip attachments and autonomous definitions
    heads = [(it, heading_of(text_of[it[0]][it[4].end():])) for it in secs]
    bare = [it for it, h in heads if h is None]
    if len(secs) >= 2 and bare:
        it = bare[0]
        out.append(finding('section-headings', f'{len(bare)} of {len(secs)} sections have no heading. Give each section a heading (MSCD 4.21); house rule 4 refers to provisions by heading, so a section without one can\'t be referred to.',
                           it[0], rules=['R-4.21-section-heading-format'], match=it[4].group(1), start=it[4].start(1), end=it[4].end(1)))
    # a section heading in all capitals (A. SERVICES.): house rules 3 and 9 and MSCD 4.21 put it in bold headline-style capitals; all capitals are for article headings (4.10)
    caps = [(it, h) for it, h in heads if h and h == h.upper() and (len(h.split()) >= 2 or len(re.findall(r"[A-Z]", h)) >= 4)]
    if caps:
        it, h = caps[0]
        st = text_of[it[0]].find(h, it[4].end())
        out.append(finding('section-heading-caps', f'{len(caps)} section headings are in all capitals ({h}); house rules 3 and 9 and MSCD 4.21 put a section heading in bold, headline-style capitalization (Services), and keep all capitals for article headings (MSCD 4.10).',
                           it[0], rules=['R-4.21-section-heading-format'], match=h, start=st, end=st + len(h) if st >= 0 else -1))
    return out

# ---------------------------------------------------------------- rule-database triggers

_RULES = None  # the compiled rule triggers, loaded once: (compiled, bad, ctrl)


def compile_hint(h):
    """(the compiled regex_hint, None), or (None, the problem): a hint that doesn't compile, or one that matches whitespace alone,
    which would make every paragraph a hit and crash the active-voice token test."""
    try:
        # a hint that spells out capitals ([A-Z], NOT, [Ee]ffective) means them; other hints match any case
        cased = '(?i)' in h or re.search(r"\[A-Z\]|(?<![\\\[])[A-Z]{2,}|\[[A-Z][a-z]\]", h)
        rx = re.compile(h, 0 if cased else re.I)
    except re.error as e:
        return None, str(e)
    if rx.search('  \t'):
        return None, 'regex_hint matches whitespace alone'
    return rx, None


def load_rules():
    """The rule triggers, compiled once: (compiled [(record, regex)] with the literal-word channel after the regex channel,
    bad [the ids of records whose regex_hint doesn't compile: the self-test reports them], ctrl [the house overrides' lint
    settings: suppress and broad_only])."""
    global _RULES
    if _RULES is not None:
        return _RULES
    recs, ov = load_records(), load_overrides()
    superseded = superseded_ids(ov)
    partial = {rid: o['replacement'] for o in ov['overrides'] if o.get('partial') for rid in o['rule_ids']}
    ctrl = dict(ov.get('lint') or {})
    compiled, bad = [], []
    for r in recs:
        if r['status'] == 'proposal' or r['id'] in superseded:
            continue
        if r['id'] in partial:
            r = dict(r, _house=partial[r['id']])
        h = (r.get('trigger') or {}).get('regex_hint') or ''
        if not h:
            continue
        rx, problem = compile_hint(h)
        if problem:
            bad.append(f"{r['id']}: {problem}")
            continue
        compiled.append((r, rx))
    _RULES = (compiled + phrase_rules(), bad, ctrl)
    return _RULES


RULE_PARA_MAX = 10000  # characters: a longer paragraph (a pasted table, a damaged file) is skipped by the rule triggers, with a note


def rule_checks(paras, compiled, ctrl, broad_share=BROAD_SHARE):
    """Returns (findings, broad triggers, the indexes of paragraphs too long to run the triggers on). ctrl: load_rules()'s lint settings."""
    hits = collections.defaultdict(list)
    skipped = []
    for p in paras:
        if not p['text'].strip():
            continue
        if len(p['text']) > RULE_PARA_MAX:
            skipped.append(p['idx'])  # some hints still cost quadratic time on a huge paragraph; the house checks ran on it
            continue
        seen = set()
        for r, rx in compiled:
            if r['id'] in seen:
                continue
            if p.get('where') == 'table' and r.get('chapter') == 2:
                continue  # the front of the contract (introductory clause, dates, recitals) isn't in a table
            m = rx.search(p['text'])
            tokens = m.group(0).split() if m else []
            if m and 'active-voice' in (r.get('key_items') or []) and tokens and tokens[-1].lower().strip('.,;') in NOT_PASSIVE:
                m = None  # a linking verb plus an adjective (is dated, is liable), not a passive
            sup = (ctrl.get('suppress') or {}).get(r['id'])
            if m and sup and re.match(sup, p['text'][m.start():m.start() + 100]):
                m = None  # the matched text already meets the house rule
            if m:
                seen.add(r['id'])
                hits[r['id']].append((p['idx'], m.group(0)[:120], r))
    out, broad = [], []
    n = max(1, sum(1 for p in paras if p['text'].strip()))
    for rid, hs in hits.items():
        r = hs[0][2]
        if (len(hs) > BROAD_MIN_HITS and len(hs) / n > broad_share) or rid in (ctrl.get('broad_only') or []):
            broad.append({'rule_id': rid, 'hits': len(hs), 'statement': r['statement'][:160]})
            continue
        for idx, mtxt, r in hs:
            out.append(finding('rule:' + r['kind'], r['statement'][:220] + (f" [HOUSE: {r['_house'][:220]}]" if r.get('_house') else ''),
                               idx, rules=[rid], source='rules', sev=r['severity'], match=mtxt))
    return out, broad, skipped

# ---------------------------------------------------------------- defined-term inventory

INTEG = re.compile(r"\((?:[A-Za-z][^()\"“”]{0,80}?,\s+)?(?:each,?\s+)?(?:the|a|an|its|their|his|her|(?:that|each|such)\s+[A-Z][\w-]*['’]s|[A-Z][\w-]*['’]s)?\s*\*{0,2}[\"“‘']\*{0,2}((?:[^\"”’']|['’](?=[A-Za-z])){1,60}?)\*{0,2}[\"”’'](?![A-Za-z])\*{0,2}")
AUTON = re.compile(r"^\s*\*{0,2}[\"“‘']\*{0,2}((?:[^\"”’']|['’](?=[A-Za-z])){1,60}?)\*{0,2}[\"”’'](?![A-Za-z])\*{0,2}\s+(?:(?:of|for|with\s+respect\s+to)\s+(?:a|an|any|each)\s+[A-Za-z][\w-]*\s+)?(?:means|includes|has the meaning|has the same meaning|shall mean|shall have)")
AUTON_INNER = re.compile(r"(?:(?<=[.;:]\s)|(?<=[.;:]\s\s)|(?<=\)\s)|(?<=\s\s)|(?<=,\sand\s)|(?<=\band\s))\**[\"“‘]\**([A-Z](?:[^\"”’]|’(?=[A-Za-z])){0,59}?)\**[\"”’](?![A-Za-z])\**\s+(?:(?:of|for)\s+(?:a|an|any|each)\s+[A-Za-z][\w-]*\s+)?(?:means|has the meaning|includes)\b")
# a definition after a lead phrase anywhere in a paragraph: In this agreement, (the) "Reports" means ...
# the lead phrases a definition may follow: As used herein, In this agreement, For purposes of this Amendment
DEF_LEAD_WORDS = r"(?:As\s+used\s+(?:herein|in\s+this\s+\w+)|When\s+used\s+in\s+this\s+\w+|For\s+(?:the\s+)?purposes?\s+of\s+this\s+\w+|In\s+this\s+\w+)(?:\s+[A-Z0-9]{1,3}\b)?"  # In this Schedule A, "Error" means
AUTON_LEAD = re.compile(r"(?i:\b" + DEF_LEAD_WORDS + r")\s*,\s*(?:the\s+)?\**[\"“‘]\**([A-Z](?:[^\"”’]|’(?=[A-Za-z])){0,59}?)\**[\"”’](?![A-Za-z])\**\s+(?:means|has the meaning|includes|refers to)\b")
IMPORTS = re.compile(r"[Cc]apitalized terms?\b[^.]{0,120}\b(?:have|has|given)\b[^.]{0,40}\bmeanings?\b[^.]{0,80}\b(?:in|that)\b", re.I)
CONTRACT_NOUN = re.compile(r"\b(?:(?:Disclosing|Receiving|Indemnifying|Indemnified|Defaulting|Nondefaulting|Non-Defaulting|Breaching|Nonbreaching|Non-Breaching|Terminating|Notifying|Requesting|Affected|Prevailing|Paying) Party|Information|Agreement|Date|Period|Price|Assets?|Software|Services?|Products?|Effect|Event|Change|Claims?|Losses|Fees?|Rent|Term|Territory|Data|Materials|Property|Rights|Work|Deliverables?|Documentation|Units?|Shares|Amount|Account|Plan|Certificate|Statement|Orders?|Budget|Report|Specifications|Equipment|Goods|Premises|Interest|Payment|Expenses|Release|Cause|Reason|Disability|Control|Default|Closing|Obligations|Liabilities|Approval|Notice|Days?|Hours|Year|Month|Quarter|Representatives|Affiliates?|Subsidiar(?:y|ies)|Indemnitees?|Liens?|Taxes|Personnel|Permits|Contracts|Persons?|Members?|Shareholders?|Stockholders?|Partners?|Ratios?|Manuals?|Lists?|Users?|Transferees?|Holders?|Standards?|Levels?|Tests?|Milestones?|Deposits?|Securities|Index|Environment|Credits?|Commitments?|Percentages?|Completion|Guarant(?:y|ee)|Warrant(?:y|ies)|Polic(?:y|ies)|Schedule|"
                           r"Assistance|Targets?|Criteria|Indicators?|Window|Region|Review|Process|Procedures?|Program|Threshold|Objectives?)\b")
# an attachment heading: the label (A; "A"; 1.1; 3.2(a)) then the end of the line, a dash, a colon, 2 spaces, or FORM OF on the same line;
# "Exhibit A lists ..." in running text is not a heading
ATT_LABEL = r"\s+[\"“]?[A-Z0-9]+(?:\.[0-9]+)*(?:\([a-z0-9]{1,3}\))?[\"”]?"
ATT_TAIL = r"[ \t*_]*(?:$|[-\u2014\u2013:]|\s{2,}|\n|\s+(?:FORM|Form)\s+(?:OF|of)\b)"
EXHIBIT_HEAD = re.compile(r"^[\s#*_]*(?:EXHIBIT|Exhibit|SCHEDULE|Schedule|ANNEX|Annex|APPENDIX|Appendix)" + ATT_LABEL + ATT_TAIL)


def _forms(term):
    """The term plus its singular and plural forms (Subsidiary, Subsidiaries; Unit, Units)."""
    forms = {term, term + 's', term + 'es'}
    if term.endswith('ies'):
        forms.add(term[:-3] + 'y')
    elif term.endswith('s'):
        forms.add(term[:-1])
    if term.endswith('y'):
        forms.add(term[:-1] + 'ies')
    return forms


# the edges of a term in running text: not inside a longer word or a hyphenated word (Non-Defaulting Party is not a use of
# Defaulting Party). Unlike \b, this works for a term that starts or ends with a non-word character (Purchase Price (Adjusted))
EDGE_L, EDGE_R = r"(?<![\w-])", r"(?![\w-])"


def _variants(term):
    """The term as defined plus its singular, plural and possessive forms (15.23: singular includes plural)."""
    forms = _forms(term)
    return EDGE_L + r"(?:" + '|'.join(sorted(map(re.escape, forms), key=len, reverse=True)) + r")(?:['’]s)?" + EDGE_R


def _canonical(term):
    """A term stripped of what a 2nd form changes: case, hyphens, spaces and each word's plural ending
    (Statements of Work and Statement of Work agree; Service Levels and Service do not)."""
    words = re.findall(r"[A-Za-z]+", term.lower())
    return ''.join(w[:-3] + 'y' if w.endswith('ies') and len(w) > 4 else w[:-2] if w.endswith(('ses', 'xes', 'ches', 'shes')) else w[:-1] if w.endswith('s') and len(w) > 3 else w
                   for w in words)


SENT_STARTERS = set("""A An The This That These Those Each Every Any All No If In On Upon At After Before During For From Under Unless Until
When Where While With Without Within Notwithstanding Subject Except As By To Neither Either Both Such Its Their His Her Our
Promptly Nothing Not And Or But Then Thereafter Following Prior Following Once Only Except Although Because Despite""".split())


DEF_LEAD = re.compile(r"^" + DEF_LEAD_WORDS + r"\s*,?\s*(?=\**[\"“‘'])", re.I)


def def_text(text):
    """A paragraph's text as a definition: without a typed enumerator (A. or 6.1) or a lead phrase (As used herein,)."""
    t = TYPED_NUM.sub('', text, count=1)
    t = re.sub(r"^[*_]*[A-Z][\w'’-]*(?:\s+(?:and|of|or|the|[A-Z][\w'’-]*)){0,5}[*_]*\.[*_]*\s{1,2}(?=\**[\"“‘']|(?:As\s+used|When\s+used|For\s+(?:the\s+)?purposes?|In\s+this)\b)", '', t, count=1)  # a run-in heading (Definitions.  "X" means; Business Days.  In this agreement, "X" means)
    return DEF_LEAD.sub('', t, count=1)


def _splits_into(words, known):
    """True if the words are 2 or more known terms in a row (Lessor + Basic Rent), each term whole."""
    n = len(words)
    ok = [False] * (n + 1)
    ok[0] = True
    for i in range(n):
        if ok[i]:
            for j in range(i + 1, n + 1):
                if ' '.join(words[i:j]) in known:
                    ok[j] = True
    return n > 1 and ok[n]


FORM_OF = re.compile(r"\bform\s+of\b|^\W*form\b", re.I)  # a form of a document signed later; "the form of payment" in a schedule's text is past the 2-paragraph window


def collect_definitions(paras, all_defs, shape):
    """The body's definitions, keyed by term: {term: [(kind, paragraph, position)]}, with the terms defined inside exhibits
    (exhibit_defs), the terms defined only inside an attached form, keyed to that form's label (form_defs), and where the
    attachments start (body_end). all_defs: definitions(paras); shape: document_shape(paras)."""
    defs, in_exhibit, in_att, exhibit_defs, exhibit_where = {}, False, False, set(), {}
    form_defs, in_form, att_label, since_head = {}, False, '', 99
    body_end = shape['attachments']
    by_para = collections.defaultdict(list)
    for d in all_defs:
        by_para[d[2]].append(d)
    for p in paras:
        if EXHIBIT_HEAD.match(p['text']):
            # an exhibit (a stand-alone document) defines its own terms; don't count those as duplicates. A schedule, annex or
            # appendix holds information that is part of the contract (house rule 6), so a term it defines counts with the body's
            # ("In this Schedule A, "Error" means ..." beside the body's "Error" is defined twice)
            # (a schedule that is a form, "SCHEDULE B — FORM OF ESTOPPEL CERTIFICATE", is a stand-alone document all the same)
            in_att, in_exhibit = True, not SCHED_HEAD.match(p['text']) or bool(FORM_OF.search(p['text']))
            att_label, in_form, since_head = re.sub(r"[\s#*_]+", ' ', p['text']).strip()[:30], bool(FORM_OF.search(p['text'])), 0
        elif in_att:
            since_head += 1
            if since_head <= 2 and FORM_OF.search(p['text']):
                in_form = in_exhibit = True  # a form of a document signed later (a release, a certificate): its definitions govern only that document
        if in_exhibit:
            # but a term defined only there isn't undefined (Protected Health Information defined in the business associate exhibit)
            here = {d[0] for d in by_para[p['idx']]}
            exhibit_defs.update(here)
            for term, words, pidx, st, en, kind in by_para[p['idx']]:
                exhibit_where.setdefault(term, []).append(('exhibit', pidx, st))
            if in_form:
                for term_ in here:
                    form_defs.setdefault(term_, att_label)
            continue
        for term, words, pidx, st, en, kind in by_para[p['idx']]:
            # a pointer ("Renewal Term" has the meaning that the section titled "Term" gives it) indexes a definition made elsewhere (MSCD 6.99)
            defs.setdefault(term, []).append(('integrated' if kind == 'sentence' else kind, pidx, st))
    return defs, exhibit_defs, form_defs, body_end, exhibit_where


TYPED_COLUMNS = re.compile(r"\S(?:\s{3,}|\t+)\S.*\S(?:\s{3,}|\t+)\S")  # a typed text table's row: 3 or more columns 3 or more spaces apart
MD_ROW = re.compile(r"\s*\|?[^|\n]*\|")  # a Markdown table row (cells between pipes)


def _inventory_text(paras):
    """The text views the inventory reads: full (every paragraph), prose (the undefined-term text: no headings, run-in headings,
    signature lines or Markdown heading rows), use_text (for counting a term's uses), and the is_heading and head_runin helpers."""
    full = '\n'.join(p['text'] for p in paras)
    # text for the undefined-term check: skip headings, run-in headings and signature lines
    head_runin = re.compile(r"^[\s#*_>]*(?:(?:Section|SECTION|Article|ARTICLE)\s+)?(?:\(?[A-Za-z0-9]{1,4}[.)]\s+|\d+(?:\.\d+)+\.?\s+)?[*_]*[A-Z][\w'’-]*[;,]?(?:\s+(?:" + SMALL_WORDS + r"|[A-Z][\w'’-]*[;,]?)){0,6}[*_]*\.[*_]*\s+")
    head_label = re.compile(head_runin.pattern.replace("[*_]*\\.[*_]*\\s+", "[*_]*[.:][*_]*\\s+"))  # for the undefined-term text only: a run-in label can end in a colon (4. Permitted Liens: the security interest ...), but "Expiration Date: March 31, 2032" still counts as a use of a defined term
    md_header_row = re.compile(r"\s*\|?(?:\s*[A-Z][\w./'’-]*(?:\s+(?:" + SMALL_WORDS + r"|[A-Z][\w./'’-]*)){0,4}\s*\|)+(?:\s*[A-Z][\w./'’-]*(?:\s+(?:" + SMALL_WORDS + r"|[A-Z][\w./'’-]*)){0,4})?\s*")  # a table's heading row, with or without outer pipes (| Product | Unit Price |; Installment | Percentage of Purchase Price | Amount)
    sig_line = re.compile(r"\bBy:\s*_{3,}|_{5,}.*\b(?:Name|Title|Date):|\b(?:Name|Title|Date):.*_{5,}")  # a signature block line (By: ____  Name: ____  Date: ____)
    # words inside a column are 1 space apart, so a tab is always a column boundary (a tab that both loops could take made a failing line exponential)
    typed_header_row = re.compile(r"\s*[A-Z][\w./'’-]*(?: (?:" + SMALL_WORDS + r"|[A-Z][\w./'’-]*))*(?:(?: {2,}|\t+)[A-Z][\w./'’-]*(?: (?:" + SMALL_WORDS + r"|[A-Z][\w./'’-]*))*)+\s*")
    head_only = re.compile(r"[\s#*_>]*(?:(?:Section|SECTION|Article|ARTICLE)\s+)?(?:\(?[A-Za-z0-9]{1,4}[.)]\s+|\d+(?:\.\d+)+\.?\s+)?[*_]*[A-Z][\w'’-]*(?:\s+(?:" + SMALL_WORDS + r"|[A-Z][\w'’-]*)){0,7}[*_]*\.?[*_]*\s*")  # a heading alone (F. Access and Information.)

    def is_heading(p):
        return p['text'].lstrip().startswith('#') or EXHIBIT_HEAD.match(p['text']) or (p.get('where') != 'table' and head_only.fullmatch(p['text'])) \
            or bool(sig_line.search(p['text']))

    def drop_md_header_rows(text):
        # a Markdown table arrives as 1 paragraph; its heading row (| Product | Unit Price |) holds column labels, not defined terms.
        # Its other rows keep only the cells a .docx table cell would keep (over 8 words, or a sentence): a drawing's title
        # (| S-203 | Roof Framing Plan |) is a name, as it is in a Word table. A typed text table's heading row (Model   Description
        # Reseller Price, columns 2 or more spaces apart, with more such rows below) is dropped too; a sentence with 1 double space stays
        lines = text.split('\n')
        typed = sum(1 for ln in lines if TYPED_COLUMNS.search(ln)) >= 2
        out = []
        for ln in lines:
            if md_header_row.fullmatch(ln) or (typed and typed_header_row.fullmatch(ln)):
                continue
            if '|' in ln and MD_ROW.match(ln):
                ln = ' | '.join(c for c in ln.strip().strip('|').split('|') if len(c.split()) > 8 or c.rstrip().endswith('.'))
            out.append(ln)
        return '\n'.join(out)
    # text for the undefined-term check: skip headings, run-in headings and signature lines
    prose = '\n'.join(drop_md_header_rows(head_label.sub('', p['text'])) for p in paras
                      if (len(p['text'].split()) > 8 or p['text'].rstrip().endswith('.')) and not is_heading(p) and p.get('where') not in ('header', 'footer'))
    # text for counting uses: every paragraph but headings, without run-in headings (D. Additional Rent. is a heading, not a use)
    use_text = '\n'.join(head_runin.sub('', p['text']) for p in paras if not is_heading(p))
    prose = re.sub(r"\b(?:titled|headed|entitled)\s+[\"“][^\"”]{1,80}[\"”](?:\s*,?\s*(?:and\s+|or\s+)?[\"“][^\"”]{1,80}[\"”])*", 'titled', prose)  # a heading named in a reference (the section titled "Termination for Cause")
    return {'full': full, 'prose': prose, 'use_text': use_text, 'is_heading': is_heading, 'head_runin': head_runin}


def _locate(paras, text, cased=True):
    """The 1st place a phrase occurs (para, start, end), so a document-level finding can point at real text; {'para': -1} if nowhere."""
    rx = re.compile(r"(?<![\w-])" + re.escape(text) + r"(?![\w-])", 0 if cased else re.I)
    for p in paras:
        m = rx.search(p['text'])
        if m:
            return {'para': p['idx'], 'start': m.start(), 'end': m.end()}
    return {'para': -1}


def term_rows(paras, defs, tx):
    """The inventory rows (term, how and where it is defined, uses, lowercase uses) and the defined-twice and defined-unused findings."""
    full, use_text, is_heading = tx['full'], tx['use_text'], tx['is_heading']
    rows, findings = [], []
    for term, where in sorted(defs.items()):
        # a use of a longer term that contains this one (Closing Date) is not a use of this one (Closing): mask the longer terms first
        longer = [k for k in defs if k != term and re.search(EDGE_L + re.escape(term) + EDGE_R, k)]
        counted = re.sub('|'.join(_variants(k) for k in longer), ' ', use_text) if longer else use_text
        cap = len(re.findall(_variants(term), counted)) - sum(1 for w in where if not is_heading(next(p for p in paras if p['idx'] == w[1])))
        low = len(re.findall(EDGE_L + re.escape(term.lower()) + EDGE_R, full)) if term.lower() != term else 0
        rows.append({'term': term, 'defined': [w[0] for w in where], 'defined_in_para': [w[1] for w in where],
                     'uses': max(cap, 0), 'lowercase_uses': low})
        real = [w for w in where if w[0] != 'pointer']
        if len(real) > 1:
            findings.append(finding('defined-twice', f'"{term}" is defined more than once; define each term once (1.57: one word, one meaning).', real[1][1], conf='high', source='inventory', match=term))
        if cap <= 0:
            findings.append(finding('defined-unused', f'"{term}" is defined but never used (6.122).', where[0][1], conf='high', source='inventory', sev=2, match=term))
    return rows, findings


def exhibit_rows(paras, defs, exhibit_where, tx):
    """Inventory rows for the terms defined only inside an exhibit (a stand-alone form: Released Parties in a form of release),
    marked defined "exhibit", so a reviewer sees them; uses count every paragraph. They raise no defined-twice or unused finding."""
    rows = []
    for term, where in sorted(exhibit_where.items()):
        if term in defs or term in PARTY_TERMS:
            continue
        cap = len(re.findall(_variants(term), tx['use_text'])) - len(where)
        low = len(re.findall(EDGE_L + re.escape(term.lower()) + EDGE_R, tx['full'])) if term.lower() != term else 0
        rows.append({'term': term, 'defined': [w[0] for w in where], 'defined_in_para': [w[1] for w in where], 'uses': max(cap, 0), 'lowercase_uses': low})
    return rows


def definition_findings(paras, defs, all_defs, shape, tx):
    """Findings about the definitions themselves: an obligation inside one, a circular pair, a defined term used in lowercase,
    and shall in a definition."""
    full = tx['full']
    findings = []
    for p in paras:
        dm = AUTON.match(def_text(p['text']))
        if dm:
            off = len(p['text']) - len(def_text(p['text']))  # the definition sentence (after any enumerator or heading); later sentences are separate provisions
            first = sentence_at(def_text(p['text']), 0)
            for sm in re.finditer(r"\b(?:shall|must|agrees? to)\b(?!\s+(?:mean|have\s+the\s+meaning)\b)", first):
                st, en = off + sm.start(), off + sm.end()
                context = p['text'][max(0, st - 30):en + 30].replace('\n', ' ')
                findings.append(finding('obligation-in-definition', f'Obligation inside the definition of "{dm.group(1)}" ("...{context}..."): a definition states what a term means; move the duty to a section of its own (MSCD 6.49-6.50).',
                                        p['idx'], rules=['R-6.49-no-stuffing', 'R-6.50-stuffing-verbs'], source='inventory', match=sm.group(0), start=st, end=en))
    # circular definitions: A's definition uses B and B's uses A, and neither anchors to anything outside the pair (MSCD 6.115-6.117).
    # Autonomous definitions only: an integrated definition and a party's name in the introductory clause sit inside a sentence
    # about something else ("Confidential Information" means information that a party (the "Disclosing Party") discloses).
    # Each definition's words end where the next definition in the paragraph starts ("Closing" means ..., and "Closing Date" means),
    # and a term inside its own definition is allowed (MSCD 6.3).
    next_def = re.compile(r"[\"“][A-Z][^\"”]{0,60}[\"”]\s+(?:means|includes|has\s+the\s+(?:same\s+)?meaning)\b")
    def_words, all_terms = {}, set()
    for term, words, pidx, st, en, kind in all_defs:
        all_terms.add(term)
        if kind not in ('autonomous', 'sentence'):
            continue  # a parenthetical sits inside a sentence about something else; a pointer defines nothing
        cut = next_def.search(words)
        def_words.setdefault(term, (words[:cut.start()] if cut else words, pidx, st, en))
    cap_word = re.compile(r"\b[A-Z][\w-]*")  # no apostrophe: Norvale's is the party Norvale
    term_words = {_canonical(w) for t in all_terms | PARTY_TERMS | PARTY_COLLECTIVE | NONPARTY_NAMED | ANCHOR_STOP for w in cap_word.findall(t)}
    anchor_ref = re.compile(r"\b(?:Schedule|Exhibit|Annex|Appendix|Attachment)\s+[A-Z0-9]|\$|\d|\b" + MONTH + r"\b")

    def anchored(words):
        # 6.115's fix is to anchor 1 definition to an external reality. A definition that names a schedule, an amount, a date,
        # a statute, or a thing by its own name (the Lodgepole platform; Lakeshore Field Service, Inc.) has one, so the pair is not
        # circular. A party's name is not an anchor (6.116: "determined by Acme"; 6.117: "owned by the Licensor"), nor is a defined term.
        return bool(anchor_ref.search(words)) or any(_canonical(w) not in term_words for w in cap_word.findall(words))
    uses = {a: {b for b in def_words if b != a and re.search(_variants(b), def_words[a][0])} for a in def_words}
    for a in sorted(def_words, key=lambda k: (def_words[k][1], def_words[k][2])):
        if anchored(def_words[a][0]):
            continue
        for b in sorted(uses[a]):
            if a in uses[b] and not anchored(def_words[b][0]) and (def_words[a][1], def_words[a][2]) <= (def_words[b][1], def_words[b][2]):
                _, pidx, st, en = def_words[a]
                findings.append(finding('circular-definition', f'"{a}" is defined by "{b}", and "{b}" is defined by "{a}": together they have no fixed meaning. '
                                        f'Anchor 1 of them to something outside the pair (MSCD 6.115-6.117).',
                                        pidx, rules=['R-6.115-no-circular-definitions'], source='inventory', match=a, start=st, end=en))
    lead = shape['lead_in'] if shape['lead_in'] is not None else -1
    in_form_idx, cur_form = set(), False  # paragraphs of an attached form (Form of Escrow Agreement): it uses its own terms
    for i, p in enumerate(paras):
        if EXHIBIT_HEAD.match(p['text']):
            cur_form = any(re.search(r"\bform\s+of\b|^\W*form\b", q['text'], re.I) for q in paras[i:i + 3])
        elif cur_form:
            in_form_idx.add(p['idx'])
    body_paras = [p for p in paras if p['idx'] > lead and p['idx'] not in in_form_idx
                  and not AUTON.match(def_text(p['text'])) and p.get('where') not in ('header', 'footer')
                  and not re.search(r"\bis\s+between\b|\bis\s+made\b.{0,80}\bbetween\b", p['text'][:300])]  # body provisions only: a definition and the introductory clause use the generic words
    for term in [t for t in defs if ' ' in t and t[0].isupper()]:
        rx = re.compile(r"(?<![\w-])" + re.escape(term.lower()) + r"(?![\w-])")
        hit = next(((p, x) for p in body_paras for x in rx.finditer(p['text'])
                    if not re.search(r"\b(?:as|in\s+(?:its|that|the)\s+(?:role|capacity)\s+as)\s+(?:the\s+|an?\s+)?$", p['text'][:x.start()])
                    and not (re.search(r"\bthis\s+$", p['text'][:x.start()]) and re.search(r"(?:Order|Agreement|Amendment|Addendum|Statement\s+of\s+Work|Lease|Note|Release)$", term))
                    and not re.search(r"\((?:each,?\s+)?(?:the\s+|a\s+|an\s+)?\**[\"“‘']\**" + re.escape(term), re.split(r"(?<=[.;])\s", p['text'][x.end():], maxsplit=1)[0])), None)  # skip the definition's own sentence (this split stops at an abbreviation's period too: "11:59 p.m. Mountain time ... (the "Initial Term")" is still reported; sentence_from() would not report it: a behavior change left for a later round)
        if hit:
            p, x = hit
            findings.append(finding('defined-term-lowercase', f'"{term}" is a defined term, but "{term.lower()}" appears in lowercase; a reader may take it to mean something else. Capitalize it, or use a different word (MSCD 6.7; 1.57).',
                                    p['idx'], x, rules=['R-1.57-one-word-one-meaning'], source='inventory', match=term.lower()))
    for m in re.finditer(r"[\"“][^\"”\n]{1,60}[\"”][ \t]+shall\s+(?:mean|be|have)", full):  # within 1 paragraph: neither the quotation nor the space after it spans 2
        findings.append(finding('shall-in-definition', 'Use means, not shall mean or shall be, in a definition (MSCD 6.42).', conf='high', rules=['R-6.42-no-shall-mean'], source='inventory',
                                match=m.group(0)[:80], **_locate(paras, m.group(0))))
    return findings


def undefined_terms(paras, defs, exhibit_defs, form_defs, body_end, tx):
    """Capitalized phrases the contract never defines: a term defined only inside an attached form, a 2nd form of a defined term,
    and an undefined term (6.122); names, statutes, agencies and table labels are left out."""
    full, prose, is_heading, head_runin = tx['full'], tx['prose'], tx['is_heading'], tx['head_runin']
    findings = []
    caps, initial = collections.Counter(), collections.Counter()  # initial: uses that start a sentence
    for m in re.finditer(r"(?<![\w-])(?:[A-Z][a-z]+(?:-[A-Z][a-z]+)*)(?:[ \t ]+[A-Z][a-z]+(?:-[A-Z][a-z]+)*){0,3}\b(?!-)", prose):  # within 1 line: never join 2 table cells  # Non-Defaulting Party and Letter of Credit whole; not inside Out-of-Scope Services
        phrase, st = m.group(0), m.start()
        if re.search(r"(?:\d|\(\w{1,3}\))\s+$", prose[max(0, st - 8):st]) and not re.fullmatch(r"(?:Business|Calendar|Trading|Banking)\s+Days?|Units?|Shares?|Contract\s+Years?|Lease\s+Years?", phrase):
            continue  # part of a name with a number in it (the Company 401(k) Plan); a counted term (15 Business Days) is still a use
        line_before = prose[prose.rfind('\n', 0, st) + 1:st]
        if re.search(r"(?:^|:\s*)[A-Z][\w.'’-]+(?:\s+[A-Z][\w.'’-]+){1,3},\s*$", line_before) or line_before.endswith('['):
            continue  # a title after a person's name (Attention: Lucia Okafor, Managing Member), or a bracketed drafting instruction ([List each Deliverable ...])
        if re.fullmatch(r"\s*(?:\(?[A-Za-z0-9]{1,4}[.)]|\d+(?:\.\d+)+\.?)?\s*", line_before) or re.search(r"[.?!:][\"”’)]?\s{1,2}$", line_before):
            words = phrase.split()  # a sentence starts here: its 1st word is capitalized anyway
            if len(words) == 1:
                continue
            if words[0] in SENT_STARTERS:
                phrase = ' '.join(words[1:])
            else:
                initial[phrase] += 1
        caps[phrase] += 1
    # a term defined only inside a form (a release signed later) is undefined in the body that uses it (Separation Date)
    body_text = '\n'.join(head_runin.sub('', p['text']) for p in paras[:body_end] if not is_heading(p))
    for term_, label_ in sorted(form_defs.items()):
        if term_ in defs or term_ in PARTY_TERMS:
            continue
        n_body = sum(1 for x in re.finditer(r"(?<![\w-])" + re.escape(term_) + r"(?![\w-])(?!\s+[A-Z])", body_text)
                     if not re.search(r"\b[A-Z][\w-]*\s+$", body_text[max(0, x.start() - 30):x.start()]))  # not part of a longer name (Asset Purchase Agreement)
        if n_body:
            exhibit_defs.discard(term_)
            findings.append(finding('possibly-undefined-term', f'"{term_}" is defined only inside the form in {label_.title()}, a document signed later, but the body uses it {n_body} {"time" if n_body == 1 else "times"}: '
                                    f'define it in the body, where the form can then use it (MSCD 6.122).', source='inventory', match=term_, **_locate(paras, term_)))
            caps.pop(term_, None)
    known = set(defs) | exhibit_defs | {v for t in set(defs) | exhibit_defs for v in _forms(t)} | PARTY_TERMS
    for phrase, c in caps.items():
        # a 2nd form differs from a defined term only by inflection or hyphenation (Sub-Licensee for Sublicensee; Non-Defaulting Party
        # for Nondefaulting Party); Service Levels is not a 2nd form of Service: it is a longer, undefined term
        second_form = next((k for k in sorted(set(defs) | exhibit_defs | PARTY_TERMS) if k != phrase and _canonical(k) == _canonical(phrase)), None)
        if phrase in known or not (second_form or CONTRACT_NOUN.search(phrase)):
            continue
        if re.search(re.escape(phrase) + r"(?:,?\s+(?:" + ENTITY + r"|Company|Corporation|Bank)|\.?\s*\()", full) or re.search(r"\s(?:Corp|Inc|Co|Ltd)$", phrase) \
                or re.search(r"(?:^|\s)(?:Union|Administration|Association|Authority|Agency|Department|Bureau|Commission|Board|Institute|Foundation|University|College|Hospital|District)$", phrase) \
                or re.search(re.escape(phrase) + r",\s+an?\s+(?:[A-Z][\w.]*\s+)?(?:[a-z][\w-]*\s+){0,3}(?:" + ENTITY + r"|corporation|company|union|association|partnership|trust|bank|individual)\b", full) \
                or (len(phrase.split()) >= 4 and re.search(re.escape(phrase) + r"\s+[A-Z][a-z]+", full)):
            continue  # a business or institution name (Front Range Equipment Finance, LLC; Pell River Credit Union, a Minnesota credit union; the National Credit Union Administration), a name defined in the next parenthetical, or a 4-word prefix of a longer name
        if re.search(re.escape(phrase) + r"\s+(?:[IVX]+\s+)?(?:of\s+the\s+(?:[A-Z][\w-]*\s+){1,6})?(?:Act|Code|Regulations?|Rules?|Statutes?)\b", full) or re.fullmatch(r"(?:Title|Chapter|Part|Subtitle|Article)\s+[IVX]+", phrase) \
                or re.search(re.escape(phrase) + r"\s+[IVX]+\s+of\s+the\b", full):
            continue  # part of a statute's name (the Consolidated Omnibus Budget Reconciliation Act of 1985; Title VII of the Civil Rights Act)
        if re.search(r"(?:^|\s)(?:Act|Code|Regulations?|Rules?|Statutes?|Ordinance)$", phrase) or re.search(r"\b(?:Title|Chapter|Section|Part)\s+[IVX\d]+\s+of\s+the\s+" + re.escape(phrase), full) \
                or re.search(r"\b(?:Code|Rules|Act|Statutes|Regulations)\s+of\s+" + re.escape(phrase) + r"\b", full):
            continue  # a statute's name (the Civil Rights Act; the California Code of Civil Procedure)
        if re.search(re.escape(phrase) + r"\s+(?:in|under|at|of)\s+\d+\s+(?:C\.F\.R\.|U\.S\.C\.|CFR\b|USC\b)", full) or AGENCY_NAME.fullmatch(phrase):
            continue  # a program or rule named with its citation (the National Organic Program in 7 C.F.R. Part 205), or a government agency
        if phrase in ('Amount', 'Date', 'Description', 'Item', 'Quantity', 'Total', 'Price', 'Rate', 'Name', 'Address', 'Title', 'Signature', 'Hours', 'Fee', 'Installment', 'Milestone', 'Deliverable', 'Due Date') and any(
                (p.get('where') == 'table' and re.fullmatch(r"\s*" + phrase + r"\s*", p['text']))
                or re.search(r"(?:^|\s{2,}|\t)" + phrase + r"(?=\s{2,}|\t|\n|$)", p['text'], re.M) for p in paras):
            continue  # a table column heading (in a .docx cell, or a typed text table with 2 or more spaces between columns), not a defined term
        if phrase.split()[-1] in ('No', 'Nos', 'Number') and re.search(re.escape(phrase) + r"\.?\s*\d", full):
            continue  # a label with a number (Unit No. 1), not a term
        if re.search(r"(?:^|\s)(?:Agreement|Addendum|Amendment)$", phrase) or phrase.split()[0] in ('This', 'The', 'These', 'Those', 'A', 'An', 'Each', 'Any', 'No', 'Every', 'All', 'Such'):
            continue  # the contract's own title, or a sentence-initial article
        rest = ' '.join(phrase.split()[1:])
        if initial[phrase] == c and (rest in known or _splits_into(rest.split(), known)):
            continue  # only ever at a sentence's start, before a defined term: Overdue Rent bears interest (an adjective, capitalized as the 1st word)
        if _splits_into(phrase.split(), known):
            continue  # defined terms side by side (Transfer Shares; pay Lessor Basic Rent), not a 2nd form of 1 term
        if second_form:
            findings.append(finding('possibly-undefined-term', f'"{phrase}" looks like a 2nd form of the defined term "{second_form}"; use 1 form throughout (MSCD 1.57; 6.122).',
                                    rules=['R-1.57-one-word-one-meaning'], source='inventory', match=phrase, **_locate(paras, phrase)))
            continue
        if any(phrase in k for k in known):
            continue
        if phrase.split()[0] in ('This', 'The', 'Each', 'Any', 'All', 'No', 'If', 'In', 'On', 'Section', 'Schedule', 'Exhibit', 'Article'):
            continue
        note = ' This document gives capitalized terms the meanings in another document, so check that one first.' if IMPORTS.search(full) else ''
        findings.append(finding('possibly-undefined-term', f'"{phrase}" is capitalized {c} {"time" if c == 1 else "times"} but not defined; define it, or lowercase it; ignore it if it is a name (6.122).' + note,
                                conf='low', source='inventory', match=phrase, **_locate(paras, phrase)))
    return findings


def inventory(paras, shape, all_defs):
    """The defined-term inventory and its findings: (rows, findings). shape: document_shape(paras); all_defs: definitions(paras)."""
    defs, exhibit_defs, form_defs, body_end, exhibit_where = collect_definitions(paras, all_defs, shape)
    tx = _inventory_text(paras)
    rows, findings = term_rows(paras, defs, tx)
    rows += exhibit_rows(paras, defs, exhibit_where, tx)
    findings += definition_findings(paras, defs, all_defs, shape, tx)
    findings += undefined_terms(paras, defs, exhibit_defs, form_defs, body_end, tx)
    return rows, findings

# ---------------------------------------------------------------- report

REPORT_CAP = 60  # lines per group in the Markdown report; --json keeps everything


def _shorten(text, n):
    """text cut to n characters, with ... when cut."""
    return text if len(text) <= n else text[:n].rstrip() + '...'


def report_notes(meta, paras=()):
    """The notes at the top of the report: what the lint couldn't read or decoded specially. --json carries them too."""
    out = []
    if not any(re.search(r"\w", p['text']) for p in paras):  # whitespace and punctuation alone is no text either
        out.append("- No text found. If this came from a scanned PDF or an image, its text must be recognized first; if it's a Word file, check that it isn't empty.")
    if meta and meta.get('harness_header'):
        out.append(f"- The 1st line is a note about the draft, not contract text (\"{meta['harness_header'][:80]}...\"); the lint skipped it, so its paragraph reads as blank.")
    if meta and meta.get('encoding'):
        out.append(f"- The file is {meta['encoding']} text; it was decoded as such. Check that quotation marks and dashes read correctly.")
    if meta and meta.get('bad_chars'):
        out.append(f"- {meta['bad_chars']} characters couldn't be decoded and show as \ufffd. Ask for the file in UTF-8 or as a .docx, or check those spots by hand: a defined term or a quotation mark may be among them.")
    if meta and meta.get('nul_chars'):
        out.append(f"- The file held {meta['nul_chars']} NUL characters (a sign of a damaged or misnamed file); they were removed. Check the text against the original.")
    if meta and meta.get('invisible_chars'):
        out.append(f"- {meta['invisible_chars']} invisible characters (soft hyphens, zero-width spaces or joiners, a stray byte-order mark: a paste from a PDF or a web page) were removed before the lint; Word doesn't show them, but each one splits a word. Delete them in the file too (Find and Replace ^- for a soft hyphen).")
    if meta and meta.get('page_breaks'):
        out.append(f"- The file has {meta['page_breaks']} page breaks (text extracted from a PDF); each one was read as a paragraph break, so a sentence split across 2 pages shows as 2 paragraphs.")
    if meta and meta.get('code_blocks'):
        out.append(f"- {meta['code_blocks']} fenced code blocks (``` ... ```) were dropped before the lint: a code sample is not contract text. If one of them holds contract wording, move it out of the fence.")
    if meta and meta.get('single_newlines'):
        out.append("- The text has no blank lines, so each line was read as its own paragraph (a wrapped line that continues a sentence was joined to it). Check the paragraph breaks if a finding looks misplaced.")
    if meta and meta.get('formatting_unread'):
        out.append(f"- {meta['formatting_unread']} paragraphs have formatting Word's file format rejects (a damaged size or font property); their text was read, their font, size, underline and numbering weren't. Check those in Word, or save the file again from Word.")
    if meta and meta.get('hidden_runs'):
        out.append(f"- {meta['hidden_runs']} hidden-text runs were skipped (Word doesn't show or print hidden text); show hidden text in Word to review them.")
    if meta and meta.get('numbering_unread'):
        out.append("- Word's numbering definitions are damaged in places, so some automatic numbers couldn't be read; check the outline in Word.")
    if meta and meta.get('stdlib_reader'):
        out.append("- python-docx isn't installed, so a plain reader was used: Word's automatic numbers, fonts set by styles and the Normal style weren't read. Check those in Word.")
    if meta:
        nf, ns = meta.get('normal_font'), meta.get('normal_size')
        if off_house_font(nf) or off_house_size(ns):
            out.append(f'- Document default font: {nf} {ns} pt (house rule: 12-point Aptos).')
        if meta.get('auto_numbered') and meta.get('auto_labels'):
            out.append(f"- {meta['auto_numbered']} paragraphs use Word's automatic numbering; the lint read {meta['auto_labels']} of their numbers from the list definitions and checked the outline. Confirm the numbers in Word, because a list can restart in ways the lint can't see.")
        elif meta.get('auto_numbered'):
            out.append(f"- {meta['auto_numbered']} paragraphs use Word's automatic numbering, and the lint couldn't read their numbers, so it didn't check the outline. Check the numbering scheme, only children and headings in Word.")
        if meta.get('comments'):
            cms = [(c[0], c[1], c[2] if len(c) > 2 else None) for c in meta['comments']]
            who = sorted({a for a, _, _ in cms if a})
            n_rep = sum(1 for c in cms if c[2] is not None)
            out.append(f"- The file already has {len(cms)} Word comments (by {', '.join(who) or 'unnamed authors'}"
                       + (f"; {n_rep} of them replies" if n_rep else '') + "). Read each before you review: leave them in place, and answer any that bear on your findings.")
            shown = 0
            for i, (a, t, parent) in enumerate(cms):  # each reply under its parent, indented
                if parent is not None or shown >= COMMENTS_SHOWN:
                    continue
                out.append(f'  - {a}: "{_shorten(t, COMMENT_SHOWN)}"')
                shown += 1
                out += [f'    - reply by {ra}: "{_shorten(rt, COMMENT_SHOWN)}"' for ra, rt, rp in cms if rp == i]
            hidden = sum(1 for c in cms if c[2] is None) - shown
            if hidden > 0:
                out.append(f'  - ... and {hidden} more comments, with their replies (the JSON from --json lists every one under "comments")')
        if meta.get('tracked_changes'):
            out.append('- The document has tracked changes; the text was read as if every change were accepted. Ask Blake whether to accept them first or redline on top. Text they deleted is not in the paragraphs below: review it from this list.')
            if meta.get('para_mark_deletions'):
                out.append(f"  - {meta['para_mark_deletions']} paragraph marks are tracked deletions: accepting them joins each such paragraph to the one after it. The lint read them as separate paragraphs, so a sentence split across 2 of them may show a finding at the join.")
            shown_c = [c for c in (meta.get('changes') or []) if c['text'].strip()]
            for c in shown_c[:CHANGES_SHOWN]:
                at = f" (in the {c['where']})" if c.get('where') else ''
                more = '...' if len(c['text']) > 120 or c.get('truncated') else ''
                out.append(f"  - {c['author'] or 'unnamed'} {c['kind']}{at}: \"{c['text'][:120]}{more}\"")
            if len(shown_c) > CHANGES_SHOWN:
                out.append(f"  - ... and {len(shown_c) - CHANGES_SHOWN} more changes (the JSON from --json lists every one)")
        notes_n = sum(1 for p in paras if p.get('where') in ('footnote', 'endnote'))
        if notes_n:
            out.append(f'- {notes_n} footnote or endnote paragraphs were read after the body (marked where = footnote). MSCD 4.6: keep operative terms out of footnotes; flag any that hold them.')
    if meta and meta.get('unread'):
        what = '; '.join(f'{v} {k}' for k, v in meta['unread'].items())
        out.append(f"- The file holds content the lint can't read: {what}. Open the document and review that content by hand; it may hold contract terms.")
    if meta and meta.get('equations'):
        out.append(f"- {meta['equations']} Word equations were read as plain text in their paragraphs; a fraction, an exponent or a layout operator may read wrongly, so check each formula in Word.")
    if meta and meta.get('unread_parts'):
        out.append(f"- These parts couldn't be read: {', '.join(meta['unread_parts'])}. Check them in Word for tracked changes and contract text.")
    if meta and meta.get('comments_unreadable'):
        out.append(f"- The file's comments couldn't be read ({meta['comments_unreadable']}). Open them in Word before you review.")
    if meta and meta.get('long_paras'):
        shown = ', '.join(map(str, meta['long_paras'][:10])) + ('...' if len(meta['long_paras']) > 10 else '')
        out.append(f"- {len(meta['long_paras'])} paragraphs are over {RULE_PARA_MAX:,} characters (paras {shown}); the house checks ran on them, but the rule triggers were skipped. Read those paragraphs by hand in the analysis passes.")
    if meta and meta.get('skipped_checks'):
        out.append(f"- {meta['skipped_checks']} checks were skipped because their data entries are malformed (run --self-test to see which); the lint may miss findings until the skill is repaired.")
    return out


def report(path, paras, meta, findings, broad, inv):
    sev_name = {1: 'Severity 1: must fix (ambiguity, meaning-changing)', 2: 'Severity 2: should fix (vagueness, dispute risk, house rules)', 3: 'Severity 3: style'}
    nd = sum(1 for f in findings if f['source'] != 'rules')
    lines = [f'# Lint report: {os.path.basename(path)}', '',
             f'{len(paras)} paragraphs read; {nd} direct findings (house rules, word checks, inventory) and {len(findings) - nd} rule triggers. All are candidates: confirm each in context before acting.',
             'Paragraphs are numbered from 0 (the title is usually para 0); para -1 means the finding is about the whole document.', '']
    lines += report_notes(meta, paras)
    if lines[-1]:
        lines.append('')
    cnt = collections.Counter(f['check'] for f in findings)
    lines += ['## Counts by check', ''] + [f'- {k}: {v}' for k, v in cnt.most_common()] + ['']
    direct = [f for f in findings if f['source'] != 'rules']
    triggers = [f for f in findings if f['source'] == 'rules']
    groups = [(sev_name[s], [f for f in direct if int(f['severity']) == s]) for s in (1, 2, 3)]
    groups.append((f'Rule triggers to check in the analysis passes (1 line per rule, with every paragraph it matched; severity is the rule\'s, if the problem is confirmed; most triggers in a clean draft are not problems)', triggers))
    for title, fs in groups:
        if not fs: continue
        lines += [f'## {title} ({len(fs)})', '']
        shown = sorted(fs, key=lambda f: (f['para'], f['check']))
        if len(shown) > REPORT_CAP and fs is not triggers:  # triggers stay complete: each is 1 short line
            lines.append(f'(showing the first {REPORT_CAP} of {len(shown)}; the JSON from --json lists every one)')
            shown = shown[:REPORT_CAP]
        is_trig = fs is triggers
        for f in shown:
            txt = paras[f['para']]['text'][:90].replace('\n', ' ') if 0 <= f['para'] < len(paras) else ''
            msg = f['message']
            if is_trig:  # keep trigger lines short: the rule id leads to the full record (rules_query.py --id)
                places = re.search(r" \(\d+ places[^)]*\)$", msg)
                msg = (msg[:150].rstrip() + ('...' if len(msg) > 150 else '')) + (places.group(0) if places and places.group(0) not in msg[:150] else '')
            lines.append(f"- para {f['para']} · sev {f['severity']} · {f['check']} · \"{f['match'][:60]}\" · {msg}" + (f" · rules: {', '.join(f['rule_ids'])}" if f['rule_ids'] else '') + (f" · [{f['confidence']}]" if f['confidence'] != 'high' else ''))
            if txt and not is_trig: lines.append(f'  - context: {txt}')
        lines.append('')
    if broad:
        lines += ['## Broad triggers (rules whose trigger words appear almost everywhere; the analysis passes apply them to every sentence anyway; look one up with rules_query.py --id)', '']
        lines += ['; '.join(f"{b['rule_id']} ({b['hits']})" for b in sorted(broad, key=lambda b: -b['hits'])), '']
    if inv is not None:
        lines += ['## Defined-term inventory', '', '| Term | Defined | Uses | Lowercase uses |', '|---|---|---|---|']
        lines += [f"| {r['term']} | {', '.join(r['defined'])} (para {', '.join(map(str, r['defined_in_para']))}) | {r['uses']} | {r['lowercase_uses']} |" for r in inv]
    return '\n'.join(lines) + '\n'


# Severity policy (SKILL.md): a check that applies a house rule takes the house severity; any other check that cites
# an MSCD rule takes that rule record's severity, so the lint and rules_query.py agree.
HOUSE_SEV = {
    'negative-subject-shall': 1, 'possibly-undefined-term': 1, 'defined-twice': 1,                  # always must-fix
    'passive-voice': 2, 'number-word': 2, 'words-and-digits': 2, 'ordinal-word': 2, 'enumeration': 2,  # house rules 1-3
    'section-headings': 2, 'numbered-cross-reference': 2, 'headings-clause': 2,                      # house rule 4
    'attachment-scheme': 2, 'generic-attachment-label': 2, 'day-month-year': 2, 'party-article': 2,  # house rules 6, 7, 11
    'spacing': 3, 'font': 3, 'font-size': 3, 'justified': 3, 'underline': 3, 'bold-definition': 3,   # typography
    'singular-they': 2, 'attachment-classification': 2, 'defined-term-lowercase': 1, 'article-heading': 3, 'typed-numbering': 3,
    'reduced-passive': 3, 'passive-hides-actor': 1, 'serial-comma': 2,
}
OWN_SEV = {'term-of-art', 'term-of-art-defined', 'within-after', 'schedule-provision', 'footnote'}  # elaborations that set their own severity case by case


def sev_is_free(check, rules):
    """True when neither a house severity nor the 1st rule's record fixes this check's severity: the site's own value governs."""
    return check not in HOUSE_SEV and not (rules and rules[0] in _SEV)


def severity_for(check, rules, sev=None):
    """The severity a finding takes: an explicit sev (the site's judgment: a narrower case than the rule, or a check that
    sets its own, such as within-after); else the house severity; else the 1st rule record's; else 3 (style)."""
    if sev is not None:
        return sev
    if check in HOUSE_SEV:
        return HOUSE_SEV[check]
    if rules and rules[0] in _SEV:
        return _SEV[rules[0]]
    return 3


EFFORTS_STD = re.compile(r"\b((?:commercially\s+|all\s+|every\s+|very\s+)?reasonable(?:\s+best|\s+commercial)?|best|good[- ]faith|diligent)\s+(?:efforts|endeavou?rs)\b", re.I)


# a definition that names an entity: Acme Widgets, Inc., a Tennessee corporation; Dana Ruiz, an individual; Acme Holdings LLC
ENTITY_NAMED = re.compile(r"\s*(?:means\s+)?[A-Z][\w.&'’-]*(?:,?\s+[A-Z][\w.&'’-]*){0,6}?,?\s+(?:" + ENTITY + r"\s*,?\s*)?(?:a|an)\s+(?:[A-Z][\w-]*\s+)?"
                          r"(?:corporation|company|partnership|limited\s+liability\s+company|limited\s+partnership|trust|association|bank|credit\s+union|individual)\b"
                          r"|\s*(?:means\s+)?[A-Z][\w.&'’-]*(?:,?\s+[A-Z][\w.&'’-]*){0,6}?,?\s+" + ENTITY + r"(?=[\s.,;]|$)")


def party_term_caps_checks(paras, defs):
    """MSCD 2.96: no all capitals for a party-name defined term ("ACME" means Acme Widgets, Inc., a Tennessee corporation; ACME WIDGETS, INC.,
    a Tennessee corporation ("ACME")). An acronym with another kind of definition ("SOW" means a statement of work) stays. defs: definitions(paras)."""
    out = []
    for term, words, pidx, st, en, kind in defs:
        if kind not in ('autonomous', 'integrated') or not re.fullmatch(r"[A-Z][A-Z&.-]*(?:\s+[A-Z][A-Z&.-]*){0,2}", term) or len(re.findall(r"[A-Z]", term)) < 2:
            continue
        body = words.rstrip() if kind == 'autonomous' else re.sub(r"\(\s*(?:the\s+|a\s+|an\s+)?\**[\"“‘']?\s*$", '', words).rstrip(' ,')
        if kind == 'integrated':
            body = body[-120:]  # the entity description right before the parenthetical
        if (ENTITY_NAMED.match(body) if kind == 'autonomous' else ENTITY_BEFORE.search(body)):
            cap = ''.join(w.capitalize() if w.isupper() else w for w in re.split(r"(\s+)", term))
            out.append(finding('party-term-capitals', f'"{term}" names a party in all capitals: MSCD 2.96 and house rule 9 put a party-name defined term in initial capitals only ("{cap}"); '
                               'all capitals are for the party\'s name in the introductory clause and signature blocks (MSCD 2.51).', pidx, conf='high',
                               rules=['R-2.96-no-emphasis-party-terms'], match=term, start=st, end=en))
    return out


def efforts_mix(paras):
    """MSCD 8.154: use 1 efforts standard in a contract. Flag the 1st place a 2nd standard appears."""
    seen = {}
    for p in paras:
        for m in EFFORTS_STD.finditer(p['text']):
            key = re.sub(r"\s+", ' ', m.group(1).lower()).replace('-', ' ')
            if key not in seen:
                seen[key] = (p, m)
    if len(seen) < 2:
        return []
    odd = [v for k, v in seen.items() if k != 'reasonable']
    (p, m) = odd[0] if odd else list(seen.values())[1]  # the place to fix is the standard that isn't plain reasonable efforts
    return [finding('efforts-mixed', f'{len(seen)} efforts standards in 1 contract ({"; ".join(seen)}): a reader may infer they differ. Use reasonable efforts throughout (MSCD 8.154; 8.1).',
                    p['idx'], m, 'high', ['R-8.154-one-efforts-standard'])]


# A dollar amount: $4,200,000, $1,234.56, $2 million, $1.2 million. 3 groups: whole dollars, decimals, scale word.
MONEY = r"\$\s?(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?(?:\s+(thousand|million|billion)\b)?"
MONEY_RE = re.compile(MONEY, re.I)
# a count in digits or in number words (3; twelve; twenty-four; one hundred twenty): words_value() reads the words
NUM_RUN = r"(?:\d+|(?:" + '|'.join(sorted(_NUMBER_WORDS)) + r")(?:[-\s]+(?:" + '|'.join(sorted(_NUMBER_WORDS)) + r"))*)"
RATE_AFTER = re.compile(r"\s*(?:per|a|each|every)\s+(?:calendar\s+)?(?:day|week|month|quarter|year|hour|unit)\b|\s*monthly\b|\s*annually\b|\s*/\s*(?:mo|month|yr|year)\b", re.I)
PER_PERIOD = re.compile(r"\b(?:monthly|annual(?:ly)?|quarterly|weekly|daily|hourly|recurring|per\s+(?:month|year|quarter|week|day|hour|unit|user|seat|licen[cs]e)|/\s*(?:mo|month|yr|year|hr|hour|user|seat))\b", re.I)
NOT_A_TOTAL = re.compile(r"\b(?:balance|remainder|remaining|rest|deposit|down\s+payment|thereafter|then|plus|interest|amortiz\w*|principal\s+and\s+interest)\b", re.I)


def _money(m, i=1):
    """Integer cents of the MONEY match whose 1st group is i (no floating point), or None for fractional cents or an amount
    too long to read (thousands of digits: Python refuses the conversion)."""
    whole, dec, scale = m.group(i), m.group(i + 1), m.group(i + 2)
    mult = _SCALES.get((scale or '').lower(), 1)
    try:
        cents = int(whole.replace(',', '')) * 100 * mult  # integer arithmetic: exact at any size
        if dec:
            frac = Decimal('0.' + dec) * 100 * mult
            if frac != frac.to_integral_value():
                return None  # fractional cents ($1.005); $1.5 million is exact
            cents += int(frac)
    except (ValueError, InvalidOperation):
        return None
    return cents


def _usd(cents):
    """Format integer cents as $1,234.56 (a credit as -$1,234.56)."""
    sign = '-' if cents < 0 else ''
    return f'{sign}${abs(cents) // 100:,}.{abs(cents) % 100:02d}'


def _count(word):
    """The count that digits or number words state (3, twelve, twenty-four), or None when it can't be read."""
    if word.isdigit():
        try:
            return int(word)
        except ValueError:  # thousands of digits
            return None
    return words_value(word)


def arithmetic_checks(paras, path=None, tables=None):
    """Numbers that should agree and don't: installments against their total, a percentage against the amount it states,
    2 definitions of 1 amount, and a table column against its Total row. Integer cents throughout (Decimal for percentages).
    Each finding asks which figure is intended."""
    out = []

    def add(p, start, end, match, msg):
        out.append(finding('arithmetic', msg + ' Confirm the intended figure with Blake; don\'t pick 1 (MSCD 7.37: conflict).', p['idx'],
                           rules=['R-7.37-conflict'], match=match, start=start, end=end))
    amounts = {}  # a defined amount: $4,200,000 (the "Purchase Price"), or the "Purchase Price" is $4,200,000
    for p in paras:
        t = p['text']
        defs = [(m, m.group(4), _money(m)) for m in re.finditer(MONEY + r"\s*\((?:the\s+)?[\"“]\**([A-Z][\w ]{1,40}?)\**[\"”]\)", t)]
        # the unconditional form only: the amount ends the statement. The Base Rent is $5,000 for the first Lease Year is a schedule, not a conflict
        defs += [(m, m.group(1), _money(m, 2)) for m in re.finditer(r"[Tt]he\s+(?:[\"“])?([A-Z][\w ]{1,40}?)(?:[\"”])?\s+(?:is|equals|means)\s+" + MONEY
                                                                     + r"(?!\d|,\d|\.\d)(?=\s*[.,;:)]|\s*$|\s+(?:and|or|which|payable|plus|less|minus|net)\b)", t)]
        for m, name, cents in defs:
            if cents is None:
                continue
            if name in amounts and amounts[name][0] != cents:
                add(p, m.start(), m.end(), m.group(0), f'The {name} is stated as {_usd(amounts[name][0])} and as {_usd(cents)}.')
            amounts.setdefault(name, (cents, p['idx']))
    for p in paras:
        t = p['text']
        spans = []
        # 1. a total paid in N installments of $Y, including a restatement in parentheses: $12,000 (12 installments of $1,000)
        for m in re.finditer(MONEY + r"([^.;$]{0,80}?)(?:\b(?:in|by|as|through)\s+|\(\s*)(" + NUM_RUN + r")(?:\s+\(\d+\))?\s+(?:equal\s+|consecutive\s+|successive\s+)*(?:monthly\s+|quarterly\s+|annual\s+|semiannual\s+|weekly\s+)?(?:installments|payments)\s+of\s+" + MONEY, t, re.I):
            total, n, each = _money(m), _count(m.group(5)), _money(m, 6)
            sentence = sentence_at(t, m.start())
            if None in (total, each, n) or RATE_AFTER.match(t, m.end(3) if m.group(3) else m.end(2) if m.group(2) else m.end(1)) \
                    or NOT_A_TOTAL.search(m.group(4)) or NOT_A_TOTAL.search(sentence):
                continue  # $12,000 per month; a deposit and the balance; installments that include interest: not a total to check
            # the rest of a list of installments: ", $Y", ", and $Y", or " and $Y" with no serial comma; "$Y per month" stops at the rate
            more = re.match(r"(?:(?:\s*,\s*(?:and\s+|or\s+)?|\s+(?:and|or)\s+)" + MONEY + r")+", t[m.end():], re.I)
            if more:
                # installments of different amounts: $19,200, $19,200, and $9,600
                parts = [each] + [_money(x) for x in MONEY_RE.finditer(more.group(0))]
                if None in parts:
                    continue
                if sum(parts) != total or len(parts) != n:
                    count_note = '' if len(parts) == n else f' and number {len(parts)}, not {n}'
                    add(p, m.start(), m.end() + more.end(), m.group(0) + more.group(0),
                        f'The {len(parts)} installments listed add to {_usd(sum(parts))}{count_note}; the total is {_usd(total)}.')
                spans.append((m.start(), m.end() + more.end()))
                continue
            if n * each != total:
                add(p, m.start(), m.end(), m.group(0), f'{n} installments of {_usd(each)} make {_usd(n * each)}, not {_usd(total)}.')
            spans.append((m.start(), m.end()))
        # 2. a percentage that states its amount: 30% of the Purchase Price ($42,000)
        for m in re.finditer(r"(\d+(?:\.\d+)?)%\s+of\s+(?:the\s+)?(?:(" + MONEY + r")|([A-Z][\w ]{1,40}?))\s*\(\s*" + MONEY + r"\s*\)", t, re.I):
            base = _money(m, 3) if m.group(2) else (amounts.get((m.group(6) or '').strip()) or (None,))[0]
            stated = _money(m, 7)
            if base is None or stated is None:
                continue
            try:
                pct = Decimal(m.group(1))
                computed = (Decimal(base) * pct / 100).quantize(Decimal(1), rounding=ROUND_HALF_UP)  # to the cent
            except InvalidOperation:
                continue  # an absurd amount or percentage (thousands of digits) overflows Decimal's precision: nothing to compare
            if computed != stated:
                add(p, m.start(), m.end(), m.group(0), f'{pct}% of {_usd(base)} is {_usd(int(computed))}, not {_usd(stated)}.')
        # 3. N payments of $Y stated with their total: 3 payments of $25,000, totaling $60,000; 3 payments of $25,000 ($60,000).
        # "3 payments of $25,000 ($25,000 each)" restates the installment, not the total, so the parenthetical form ends at the amount
        for m in re.finditer(r"\b(" + NUM_RUN + r")(?:\s+\(\d+\))?\s+(?:equal\s+)?(?:installments|payments|tranches)\s+of\s+" + MONEY
                             + r"(?:\s+each)?(?:[^.;$]{0,60}?\b(?:totaling|totalling|for\s+a\s+total\s+of|aggregating|in\s+the\s+aggregate\s+of)\s+" + MONEY
                             + r"|\s*\(\s*(?:a\s+total\s+of\s+|totaling\s+|in\s+total\s+)?" + MONEY + r"\s*(?:in\s+total\s*)?\))", t, re.I):
            if any(a < m.end() and m.start() < b for a, b in spans):
                continue  # pattern 1 already checked these installments
            n, each = _count(m.group(1)), _money(m, 2)
            total = _money(m, 5) if m.group(5) else _money(m, 8)
            if None not in (n, each, total) and n * each != total:
                add(p, m.start(), m.end(), m.group(0), f'{n} payments of {_usd(each)} make {_usd(n * each)}, not {_usd(total)}.')
        # 4. an annual total restated as a per-period amount: the annual Fees are $84,000, payable as $7,000 each month (12 months);
        # a rate alone ($7,000 per month) or 2 unrelated amounts in 1 sentence ($84,000 ... a $500 deposit each month) are left alone
        for m in re.finditer(r"\b(?:annual|yearly|per\s+year|a\s+year|each\s+year)\b[^.;$]{0,60}?" + MONEY + r"[^.;$]{0,80}?\b(?:as|in|(?:installments|payments)\s+of)\s+" + MONEY
                             + r"\s+(?:on\s+the\s+(?:\d+(?:st|nd|rd|th)|first|last)\s+(?:business\s+)?day\s+of\s+)?(?:per|each|a|every)\s+(?:calendar\s+)?(month|quarter|week)\b", t, re.I):
            total, each = _money(m), _money(m, 4)
            periods = {'month': 12, 'quarter': 4, 'week': 52}[m.group(7).lower()]
            if None not in (each, total) and periods * each != total and not NOT_A_TOTAL.search(m.group(0)):
                add(p, m.start(), m.end(), m.group(0), f'{periods} {m.group(7).lower()}ly payments of {_usd(each)} make {_usd(periods * each)}, not the annual {_usd(total)}.')
    out += table_total_checks(paras, path, tables)
    return out


# a credit is the whole cell in parentheses or with a leading minus; "30% ($30,000)" restates an amount, it doesn't negate it
_NEG_MONEY = re.compile(r"^\s*(?:\(\s*\$[^()]*\)|[-−–]\s*\$[^()]*|\$\s*\([^()]*\))\s*$")


def _cell_cents(cell):
    """The amount in a table cell, in integer cents (a credit in parentheses or with a minus sign is negative), or None."""
    m = MONEY_RE.search(cell or '')
    if not m:
        return None
    cents = _money(m)
    if cents is not None and _NEG_MONEY.search(cell):
        cents = -cents
    return cents


_MD_SEP = re.compile(r"\s*:?-{2,}:?\s*")


def _md_tables(p):
    """The Markdown tables in a paragraph, each a list of rows of (cell text, paragraph idx, offset of the cell in the paragraph).
    A row has outer pipes (| A | B |), or interior pipes only (A | B) when the block's 2nd line is the ---|--- separator;
    a lone sentence with a pipe in it (Acme | Beta) is no table. The separator row is dropped."""
    text = p['text']
    blocks, cur, pos = [], [], 0
    for line in text.split('\n'):
        st = line.strip()
        if st.startswith('|') and st.endswith('|') or ' | ' in st or st.count('|') >= 2:
            cur.append((pos, line))
        elif cur:
            blocks.append(cur)
            cur = []
        pos += len(line) + 1
    if cur:
        blocks.append(cur)
    tables = []
    for block in blocks:
        def cells_of(line):
            return [c.strip() for c in line.strip().strip('|').split('|')]
        outer = all(ln.strip().startswith('|') and ln.strip().endswith('|') for _, ln in block)
        sep2 = len(block) > 1 and all(_MD_SEP.fullmatch(c) for c in cells_of(block[1][1]) if c) and any(c for c in cells_of(block[1][1]))
        if not (outer or sep2):
            continue
        rows = []
        for start, line in block:
            if all(_MD_SEP.fullmatch(c) for c in cells_of(line) if c):
                continue  # the ---|--- separator
            lead = len(line) - len(line.lstrip())
            body = line.strip()
            if body.startswith('|'):
                lead += 1
                body = body[1:]
            if body.endswith('|'):
                body = body[:-1]
            row, at = [], start + lead
            for raw in body.split('|'):
                cell = raw.strip()
                row.append((cell, p['idx'], at + (len(raw) - len(raw.lstrip()))))
                at += len(raw) + 1
            rows.append(row)
        if rows:
            tables.append(rows)
    return tables


# a named amount in the body (the Support Fee of $24,000) that a schedule also states on a line naming the same fee
# (Annual Support Fee: $24,000): stated twice (MSCD 1.56). An amount the body states once, or a schedule line with another
# amount or another fee, stays clear; exhibits (stand-alone forms) aren't read
NAMED_AMOUNT = re.compile(r"\bthe\s+((?:[A-Z][\w-]*\s+){0,3}(?:Fee|Rent|Price|Deposit|Payment|Charge|Amount|Salary|Retainer))\s+of\s+(\$\s?[\d,]+(?:\.\d{2})?)")


def restated_amount_checks(paras, shape):
    """Findings for a named body amount that a schedule restates (MSCD 1.56). shape: document_shape(paras)."""
    start = shape['attachments']
    sched_lines, in_sched = [], False
    for p in paras[start:]:
        if EXHIBIT_HEAD.match(p['text']):
            in_sched = bool(SCHED_HEAD.match(p['text']))
        if in_sched:
            sched_lines += p['text'].split('\n')
    out = []
    for p in paras[:start]:
        for m in NAMED_AMOUNT.finditer(p['text']):
            head, amount = m.group(1).split()[-1], re.sub(r"\s", '', m.group(2))
            if any(head in ln and re.search(re.escape(amount) + r"(?![\d,])", ln.replace(' ', '')) for ln in sched_lines):
                out.append(finding('restated-amount', f'{m.group(1)} of {amount}: a schedule states this amount too. Stated twice, the 2 copies invite a dispute if 1 ever changes; '
                                   'state it once, in the body or in the schedule, and refer to the other (MSCD 1.56).', p['idx'], m, conf='medium', rules=['R-1.56-no-repetition'], sev=3))
    return out


def table_total_checks(paras, path, tables=None):
    """A table column whose Total row doesn't equal the sum of the rows above it (.docx tables and Markdown tables).
    tables: for a .docx, the reader's tables, each a list of rows of (cell text, paragraph idx); None for text files.
    A Subtotal row is a checkpoint: it must equal the rows since the last subtotal, and the Total adds the subtotals
    and any rows after the last one. Header rows (no amount) are skipped."""
    out = []
    if tables is None:
        tables = [t for p in paras for t in _md_tables(p)]
    for rows in tables:
        labels = [r[0][0] if r else '' for r in rows]
        tot_i = next((i for i, lab in enumerate(labels) if re.search(r"\btotal\b", lab, re.I) and not re.search(r"\bsub-?\s?total\b", lab, re.I)), None)
        if tot_i is None or tot_i < 2:
            continue
        for col in range(1, max(len(r) for r in rows)):
            vals = [_cell_cents(r[col][0]) if col < len(r) else None for r in rows[:tot_i]]
            k = 0
            while k < len(vals) and vals[k] is None and not re.search(r"\btotal\b", labels[k], re.I):
                k += 1  # header rows: the rows before the 1st amount
            body = list(zip(labels[k:tot_i], vals[k:]))
            stated = _cell_cents(rows[tot_i][col][0]) if col < len(rows[tot_i]) else None
            if stated is None or not body or any(v is None for _, v in body):
                continue
            cells = [r[col][0] if col < len(r) else '' for r in rows[k:tot_i]]
            if any(NOT_A_TOTAL.search(lab) for lab, _ in body):
                continue  # Purchase Price, Deposit, Balance, Total: a closing statement, not a column that sums to its Total row
            per = [bool(PER_PERIOD.search(lab) or PER_PERIOD.search(c)) for (lab, _), c in zip(body, cells)]
            if any(per) and (not all(per) or not PER_PERIOD.search(labels[tot_i])):
                continue  # a rate row ($1,000 per month) beside a one-time fee, or monthly rows under a Total Year 1: a contract value over a term, not the
                # column's sum. Rows that are all the same kind (3 monthly fees and a Total Monthly Fee; a Monthly Fee column) still must add up.
            problems, running, subtotals = [], 0, 0
            for lab, v in body:
                if re.search(r"\bsub-?\s?total\b", lab, re.I):
                    if v != running:
                        problems.append(f'the rows above the {lab.strip()} row add to {_usd(running)}, but it says {_usd(v)}')
                    subtotals += v
                    running = 0
                else:
                    running += v
            computed = subtotals + running
            if computed != stated:
                problems.append(f"the rows add to {_usd(computed)}, but its Total row says {_usd(stated)}")
            if problems:
                cell = rows[tot_i][col]
                cell_text, pidx = cell[0], cell[1]
                tp = next((p for p in paras if p['idx'] == pidx), None)
                # a Markdown cell carries its offset (the Total row's $80, not the 1st $80 in the table); a .docx cell is its own paragraph
                st = cell[2] if len(cell) > 2 else tp['text'].find(cell_text) if tp else -1
                out.append(finding('arithmetic', f"In the table, {'; and '.join(problems)}. Confirm the intended figures with Blake; don't pick 1 (MSCD 7.37: conflict).",
                                   pidx, rules=['R-7.37-conflict'], match=cell_text, start=st, end=st + len(cell_text) if st >= 0 else -1))
    return out


# the test harness's note above a contract ("Draft of November 2, 2026; Blake's client: Employee (other side's draft ...)";
# "*Lender's draft of November 3, 2026; Blake's client: Guarantor*"): not contract text. A title ("DRAFT OF SUPPLY AGREEMENT")
# or a sentence that only mentions a draft has no "; Blake's client:" and stays
HARNESS_HEAD = re.compile(r"^[\s#>*_]*(?:[A-Z][\w'’-]*\s+)?[Dd]raft\s+of\s+[^;\n]{1,80};\s+Blake['’]s\s+client:")
HARNESS_WINDOW = 3  # non-blank paragraphs at the top of the file where the note can sit


def skip_harness_header(paras, meta):
    """Blank the harness note at the top of the file, so no check reads it as contract text; the paragraph keeps its number."""
    seen = 0
    for i, p in enumerate(paras):
        if not p['text'].strip():
            continue
        if HARNESS_HEAD.match(p['text']):
            paras = paras[:i] + [dict(p, text='')] + paras[i + 1:]
            return paras, dict(meta, harness_header=p['text'][:200])
        seen += 1
        if seen >= HARNESS_WINDOW:
            break
    return paras, meta


def run(path, want_inventory, whose=None):
    """Lint 1 file; whose is 'blake' or 'other-side' (--whose), or None to keep the module's WHOSE. The checks read the
    document's parties and boundaries from module state, so this wrapper restores that state afterward: a 2nd file, or a
    direct call to house_checks(), never inherits the last document's parties."""
    global PARTY_TERMS, PARTY_COLLECTIVE, NONPARTY_NAMED, EXHIBIT_PARTIES, RECITAL_IDX, WHOSE
    saved = (PARTY_TERMS, PARTY_COLLECTIVE, NONPARTY_NAMED, EXHIBIT_PARTIES, RECITAL_IDX, WHOSE)
    if whose is not None:
        WHOSE = whose
    try:
        return _run(path, want_inventory)
    finally:
        PARTY_TERMS, PARTY_COLLECTIVE, NONPARTY_NAMED, EXHIBIT_PARTIES, RECITAL_IDX, WHOSE = saved


def _run(path, want_inventory):
    try:
        paras, meta = read_paragraphs(path)
    except DOCX_XML_ERRORS as e:  # python-docx found XML it can't read: a damaged package, not a bug in the lint
        raise InputError(f'could not read {path}: damaged .docx ({e.__class__.__name__}: {e}); save it again from Word, or ask for a fresh copy') from e
    except (ValueError, OSError, UnicodeError) as e:  # an unreadable or unsupported file (read_paragraphs says what to do): exit 2
        raise InputError(f'could not read {path}: {e}') from e
    findings = []  # from here on, an exception is a bug in the lint (exit 3), not a bad file
    paras, meta = skip_harness_header(paras, meta)
    shape, defs = document_shape(paras), definitions(paras)  # computed once; the document-level checks share them
    global PARTY_TERMS
    PARTY_TERMS = party_terms(paras)
    global PARTY_COLLECTIVE, NONPARTY_NAMED
    PARTY_COLLECTIVE = party_collective(paras) - PARTY_TERMS
    PARTY_COLLECTIVE |= signing_roles(paras, PARTY_TERMS | PARTY_COLLECTIVE, shape, defs) if PARTY_TERMS else set()
    PARTY_COLLECTIVE |= signatory_roles(paras)  # a signatory named by its role alone (as escrow agent) is a party for the subject checks
    named = nonparty_named(paras, PARTY_TERMS | PARTY_COLLECTIVE, shape, defs) if PARTY_TERMS else set()
    global EXHIBIT_PARTIES, RECITAL_IDX
    intro_i, lead_i = shape['intro'], shape['lead']
    RECITAL_IDX = {p['idx'] for p in paras if intro_i is not None and lead_i is not None and intro_i < p['idx'] < lead_i} if lead_i is not None else set()
    ex_starts = [i for i, p in enumerate(paras) if EXHIBIT_HEAD.match(p['text'])]
    ex_parties = {a: party_terms(paras[a:(ex_starts[k + 1] if k + 1 < len(ex_starts) else len(paras))]) | signatory_roles(paras[a:(ex_starts[k + 1] if k + 1 < len(ex_starts) else len(paras))])
                  for k, a in enumerate(ex_starts)}
    for i, p in enumerate(paras):
        # in an exhibit (a form the nonparty signs, such as an escrow agreement), a named nonparty may be a party,
        # and the form's own introductory clause names its parties
        NONPARTY_NAMED = named if not ex_starts or i < ex_starts[0] else set()
        EXHIBIT_PARTIES = ex_parties[max(a for a in ex_starts if a <= i)] if ex_starts and i >= ex_starts[0] else set()
        if p['text'].strip():
            findings += house_checks(p)
    NONPARTY_NAMED, EXHIBIT_PARTIES, RECITAL_IDX = named, set(), set()
    findings += outline_checks(paras, shape)
    findings += party_term_caps_checks(paras, defs)
    findings += front_checks(paras, meta, shape, defs)
    findings += efforts_mix(paras)
    findings += term_of_art_checks(paras)
    findings += schedule_section_checks(paras)
    first_note = next((p for p in paras if p.get('where') in ('footnote', 'endnote') and p['text'].strip()), None)
    if first_note is not None:
        n_notes = sum(1 for p in paras if p.get('where') in ('footnote', 'endnote') and p['text'].strip())
        findings.append(finding('footnote', f'{n_notes} footnote or endnote paragraphs: don\'t use footnotes in a contract (MSCD 4.6). Move any operative term into the body '
                                '(a footnote that states a figure or a condition is a term the body may contradict); delete explanatory notes.',
                                first_note['idx'], conf='high', rules=['R-4.6-no-footnotes'], sev=3, match=first_note['text'][:80], start=0, end=min(80, len(first_note['text']))))
    findings += arithmetic_checks(paras, path, meta.get('tables') if path.lower().endswith('.docx') else None)
    findings += restated_amount_checks(paras, shape)
    nf, ns = meta.get('normal_font'), meta.get('normal_size')
    if off_house_font(nf) or off_house_size(ns):
        findings.append(finding('font', f'Document default font is {nf} {ns} pt; house rule 9 is 12-point Aptos (set it in the Normal style).', -1, conf='high'))
    if re.search(r"\$[\d,]+\.(?:\d[1-9]|[1-9]\d)\b", '\n'.join(p['text'] for p in paras)):
        findings = [f for f in findings if f['check'] != 'money-cents']  # amounts with cents appear, so .00 keeps the amounts parallel (MSCD 13.546)
    n_auto = sum(1 for p in paras if (p.get('fmt') or {}).get('auto_numbered') and p['text'].strip())
    if n_auto:
        meta = dict(meta, auto_numbered=n_auto, auto_labels=sum(1 for p in paras if p.get('auto_label')))
    # the attachment reminder is a per-document check: keep the first one only, and report it with the rule triggers (a note for the
    # analysis passes, not a direct finding: it names no problem, so it never counts as one)
    first_att = next((i for i, f in enumerate(findings) if f['check'] == 'attachment-check'), None)
    findings = [f for i, f in enumerate(findings) if f['check'] != 'attachment-check' or i == first_att]
    if first_att is not None:
        n_att = sum(1 for p in paras if re.search(r"\b(Schedule|Exhibit|schedule|exhibit)s?\b", p['text']))
        findings[first_att] = dict(findings[first_att], source='rules', message=f'Attachments in {n_att} paragraphs: confirm each schedule-versus-exhibit classification, the order (schedules first) and every reference (attachments.md).')
    comp, _bad, ctrl = load_rules()
    rf, broad, long_paras = rule_checks(paras, comp, ctrl)
    if long_paras:
        meta = dict(meta, long_paras=long_paras)
    house_keys = {(f['para'], f['match'].lower()) for f in findings}
    direct_rules = {(f['para'], rid) for f in findings for rid in f.get('rule_ids') or []}
    findings += [f for f in rf if (f['para'], f['match'].lower()) not in house_keys and (f['para'], f['rule_ids'][0]) not in direct_rules]
    findings = statutory_text_filter(paras, [f for f in findings if f['check'] != '_cleared'])
    inv = None
    if want_inventory:
        inv, invf = inventory(paras, shape, defs)
        # shall in a definition: the sentence-level variant reports the sentence-initial form; the inventory's catch-all keeps the rest
        house_shall = [f for f in findings if f['check'] == 'shall-in-definition']
        findings += [f for f in invf if f['check'] != 'shall-in-definition'
                     or not any(h['para'] == f['para'] and h['start'] < f['end'] and f['start'] < h['end'] for h in house_shall)]
    return paras, meta, collapse(findings), broad, inv


STATUTE_TEXT = re.compile(r"\b(?:disclosure|notice|statement|legend|warning|language|text|wording)\s+(?:that|which)\s+[^.:]{0,160}?\b(?:requires?|mandates?|prescribes?)\s*:"
                          r"|\b(?:disclosure|notice|statement|legend|warning|language|text|wording)\s+(?:required|mandated|prescribed)\s+by\s+[^.:]{0,160}?:", re.I)


SCHED_HEAD = re.compile(r"^[\s#*_]*(?:SCHEDULE|Schedule|ANNEX|Annex|APPENDIX|Appendix)" + ATT_LABEL)
EXH_HEAD_ONLY = re.compile(r"^[\s#*_]*(?:EXHIBIT|Exhibit)" + ATT_LABEL)


def schedule_section_checks(paras):
    """MSCD 5.93: a schedule holds information, not contract sections. A duty (shall) or a prohibition in a schedule
    is a provision that belongs in the body; an exhibit (a stand-alone form) has its own provisions and is skipped."""
    out, in_sched, done = [], False, False
    for p in paras:
        t = p['text']
        if EXHIBIT_HEAD.match(t):
            in_sched, done = bool(SCHED_HEAD.match(t)) and not EXH_HEAD_ONLY.match(t), False
            continue
        if done:
            continue
        if not in_sched or p.get('where') == 'table':
            continue
        if re.search(r"\bform\s+of\b", t, re.I) and len(t.split()) <= 8:
            in_sched = False  # a form inside a schedule heading: treat the rest as an exhibit
            continue
        for m in re.finditer(r"\b(?:[A-Z][\w-]*|[a-z]+)\s+(?:shall|must|may)\s+(?:not\s+)?[a-z]+", t):
            if re.search(r"\b(?:shall|must)\s+(?:mean|have\s+the\s+meaning)\b", m.group(0)):
                continue
            n_prov = 0
            for q in paras[p['idx']:]:
                if EXHIBIT_HEAD.match(q['text']):
                    break
                n_prov += bool(re.search(r"\b(?:shall|must|may)\s+(?:not\s+)?[a-z]+", q['text']))
            out.append(finding('schedule-provision', f'This schedule holds provisions (a duty, a prohibition or a grant of discretion; {n_prov} paragraphs with shall, must or may). '
                               'A schedule holds information that the body refers to; contract sections belong in the body (MSCD 5.93), unless the schedule carries '
                               'standardized provisions on purpose (a statement of work, a service-level schedule; MSCD 5.94), in which case the body says that it does. '
                               'Check which this is; 1 finding per schedule.', p['idx'], m, 'low', ['R-5.93-no-sections-in-schedules'], sev=3))
            done = True  # 1 finding per schedule
            break
    return out


def statutory_text_filter(paras, findings):
    """Text that a statute requires word for word (This section contains the disclosure that Section 8-70-115(2) of the Colorado
    Revised Statutes requires: ...) keeps the statute's words, even where they break a house rule. Drop the style findings on that
    text and add 1 note per paragraph so the reviewer knows why."""
    spans = {p['idx']: m.end() for p in paras for m in [STATUTE_TEXT.search(p['text'])] if m}
    if not spans:
        return findings
    by_idx = {p['idx']: p for p in paras}
    keep = []
    for f in findings:
        pos = spans.get(f.get('para'))
        if pos is not None and f['check'] not in ('arithmetic', 'defined-twice'):
            st = f.get('start')
            if st is None or st < 0:
                st = by_idx[f['para']]['text'].find(f.get('match') or '\0')
            if st >= pos:
                continue
        keep.append(f)
    for idx, pos in spans.items():
        t = by_idx[idx]['text']
        keep.append(finding('statutory-text', "This text reproduces wording a statute requires: keep the statute's words, even where they break a house rule "
                            "(passive, words for numbers). Confirm them against the statute, including any formatting it requires. Comment, don't edit.",
                            idx, match=t[pos:pos + 60].strip(), start=pos, end=len(t)))
    return keep


PER_DOC = {'font', 'font-size', 'justified', 'underline', 'bold-definition'}


def collapse(findings):
    """Report a repeated finding once, with every location, so the report stays short (a template can repeat
    the same problem 40 times). Each collapsed finding keeps all its locations in 'occurrences'."""
    out, seen = [], {}
    for f in findings:
        if f['source'] == 'rules':
            key = ('rule', f['rule_ids'][0] if f['rule_ids'] else f['check'])
        elif f['check'] in PER_DOC:
            # 1 finding per document for a formatting check; bold-definition has 2 distinct messages (unbolded terms, bold quotation
            # marks) and the document-default font differs from a paragraph's, so those keep each distinct message
            key = ('doc', f['check'], f['message']) if f['check'] == 'bold-definition' or (f['check'] == 'font' and f['para'] == -1) else ('doc', f['check'])
        else:
            key = (f['check'], f['match'].lower(), f['message'])
        loc = (f['para'], f.get('start', -1), f.get('end', -1), f['match'])
        if key in seen:
            g = seen[key]
            g['occurrences'].append(loc)
            continue
        g = dict(f, occurrences=[loc])
        seen[key] = g
        out.append(g)
    for g in out:
        n = len(g['occurrences'])
        if n > 1:
            paras_ = sorted({o[0] for o in g['occurrences'] if o[0] >= 0})
            k = len(paras_)  # 2 places in 1 paragraph reads as 1 place when only the paragraph list is shown: say both counts
            g['message'] = g['message'] + (f' ({n} places in {k} paragraph{"" if k == 1 else "s"}: para{"" if k == 1 else "s"} '
                                           f'{", ".join(map(str, paras_[:15]))}{"..." if k > 15 else ""})' if k else f' ({n} places)')
    return out


# a party name in the introductory clause: before ", a Delaware corporation" or before its defined-term parenthetical
INTRO_NAME = re.compile(r"(?:between|and|;)\s+([A-Z][\w.&'’ -]{1,60}?(?:,?\s+" + ENTITY + r")?)(?=,\s+(?:a|an)\s+|\s*\()")


def front_checks(paras, meta, shape, defs):
    """The front and the definitions: title (2.2), party names in capitals (2.51), lead-in (2.159), bold defined terms (2.92).
    shape: document_shape(paras); defs: definitions(paras)."""
    out = []
    def add(check, msg, p, m=None, rules=()):
        out.append(finding(check, msg, p['idx'] if p else -1, m, rules=rules, cut=80))
    body = [p for p in paras if p['text'].strip()]
    if not body:
        return out
    legend = re.compile(r"^[#\s*_\[(]*(?:[\w&.,'’ -]{0,60}\s)?(?:draft|DRAFT|Draft)\b[^\n]{0,60}$|^[#\s*_\[(]*(?:confidential|privileged|for discussion|execution (?:copy|version))\b", re.I)
    while len(body) > 1 and legend.search(re.sub(r"[*_\])]+$", '', body[0]['text'].strip())) and len(body[0]['text'].split()) <= 12:
        body = body[1:]  # a draft legend or a confidentiality legend above the title (Halvorsen draft of February 10, 2027) isn't the title
    title = body[0]
    tt = re.sub(r"^[#\s*_]+|[*_]+$", '', title['text']).strip()
    if 2 <= len(tt.split()) <= 10 and not re.search(r"\b(?:between|dated|is|are)\b", tt):
        if tt != tt.upper():
            add('front', 'Title: put it in all capitals (MSCD 2.2).', title, None, ['R-2.2-title-format'])
        if 'centered' in (title.get('fmt') or {}) and not title['fmt']['centered']:
            add('front', 'Title: center it at the top of the 1st page (MSCD 2.2).', title, None, ['R-2.2-title-format'])
    letter = any(re.match(r"\s*(?:Dear|To)\s+[A-Z]", p['text']) for p in body[:12]) or any(re.search(r"\bthis letter agreement\b", p['text'], re.I) for p in body[:6])
    # a letter agreement has no introductory clause (MSCD 19.3-19.9); otherwise the shape's intro, or an early between-clause with a parenthetical
    by_idx = {p['idx']: p for p in paras}
    intro = None if letter else by_idx.get(shape['intro']) if shape['intro'] is not None else next((p for p in body[:6] if BETWEEN_AMONG.search(p['text']) and re.search(r"\(", p['text'])), None)
    if intro:
        for m in INTRO_NAME.finditer(intro['text']):
            name = m.group(1)
            if name != name.upper() and not re.fullmatch(r"(?:the\s+)?\w+", name) and not re.search(r"[a-z][A-Z]", name):
                add('front', f'Introductory clause: state the party name in all capitals ({name.upper()}) (MSCD 2.51).', intro, m, ['R-2.51-names-in-capitals'])
        # each entity name in a signature block must match the name in the introductory clause, or who signed is in doubt
        def _nm(x):
            return re.sub(r"\s+", ' ', re.sub(r"[^\w& ]", ' ', x.upper())).strip()
        intro_names = {_nm(m.group(1)) for m in INTRO_NAME.finditer(intro['text']) if re.search(ENTITY + r"\s*$", m.group(1))}
        intro_names |= {_nm(m.group(0)) for m in re.finditer(r"[A-Z][\w.&'’ -]{1,60}?,?\s+" + ENTITY, intro['text'])}
        seen = set()
        for p in (q for q in body if q['idx'] >= shape['tail']):
            if p.get('where') == 'table' or p['idx'] >= shape['attachments']:
                continue  # a schedule's table of contracts names counterparties, and an exhibit is a form with its own signers: not this contract's signature blocks
            s = re.sub(r"^[#>\s*_]+|[*_:\s]+$", '', p['text']).strip()
            m = re.fullmatch(r"([A-Z0-9][A-Za-z0-9.&'’ -]{1,70}?,?\s+" + ENTITY + r")(?:,\s+as\s+[\w ]{2,40})?", s)
            if not m or not intro_names:
                continue
            n = _nm(m.group(1))
            if n in seen or any(n == i or n in i or i.endswith(' ' + n) or n.endswith(' ' + i) for i in intro_names):
                continue
            seen.add(n)
            near = max(intro_names, key=lambda i: len(set(i.split()) & set(n.split())))
            if set(near.split()) & set(n.split()) - {'LLC', 'INC', 'CORP', 'CO', 'LP', 'LLP', 'LTD', 'THE', 'AND', 'PLLC', 'L', 'C', 'P', 'A', 'N'}:
                add('front', f'Signature block: "{m.group(1)}" differs from the name in the introductory clause; use the exact legal name in both, and confirm which is correct (MSCD 2.50; 5.29).', p, m, ['R-2.50-full-names', 'R-5.29-entity-name-caps'])
        if not any(LEAD_IN.search(p['text']) for p in body):
            add('front', 'No lead-in: add "The parties agree as follows:" after the introductory clause (MSCD 2.159).', intro, None, ['R-2.159-lead-in'])
    unbolded, bold_quotes = [], []
    for term, _words, pidx, st, en, _kind in defs:
        p = by_idx[pidx]
        f = p.get('fmt') or {}
        if 'bold_text' not in f or pidx >= shape['attachments'] or not p['text'].strip():  # a form attached as an exhibit keeps its own format
            continue
        m = _Span(p['text'], st, en)
        if term and term not in f['bold_text']:
            unbolded.append((p, m))
        elif term and any(q + term + r in f['bold_text'] for q, r in (('"', '"'), ('“', '”'))):
            bold_quotes.append((p, m))
    if unbolded:
        p, m = unbolded[0]
        add('bold-definition', f'Defined term not in bold where it is defined ({len(unbolded)} definitions, integrated and autonomous); bold the term, not the quotation marks (MSCD 2.92; 6.31).', p, m, ['R-2.92-party-term-format', 'R-6.31-quote-and-bold'])
    if bold_quotes:
        p, m = bold_quotes[0]
        add('bold-definition', f'Quotation marks in bold around {len(bold_quotes)} defined terms; bold the term only (MSCD 2.92; 6.31).', p, m, ['R-6.31-quote-and-bold'])
    return out


def _round8_cases(_tmp, ar, tb):
    """The round-8 hardening cases: each a (name, passed) pair. _tmp writes a temporary file; ar and tb run the arithmetic checks."""
    out = []

    def run_text(text, inventory=True, suffix='.txt'):
        return lint_text(text, suffix, inventory)
    intro = 'This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Seller”), and BETA INC., a Texas corporation (“Buyer”)'
    # C1: every term in the collective parenthetical, with a comma inside the quotation marks
    res = run_text(intro + ' (each, a "Party," and collectively, the "Parties").\n\nThe Parties will cooperate.  Each Party will pay.  The Parties must sign.  The Parties may not assign.\n', False)
    out.append(('collective party terms (each, a "Party," and collectively, the "Parties") drive the will, must and may-not checks',
                sorted(f['check'] for f in res[2] if f['check'] in ('category-will', 'category-must', 'may-not')) == ['category-must', 'category-will', 'category-will', 'may-not']))
    # C2, C16, S3, R8, R9: installment lists without a serial comma; a parenthetical total; number words; absurd amounts
    out.append(('arithmetic: a list of installments with no serial comma', not ar('Buyer shall pay $10,000 in 3 installments of $3,333.33, $3,333.33 and $3,333.34.')
                and not ar('Buyer shall pay $10,000 in 3 installments of $5,000, $3,000 and $2,000.') and len(ar('Buyer shall pay $10,000 in 3 installments of $3,000, $3,000 and $3,000.')) == 1))
    out.append(('arithmetic: a parenthetical total', len(ar('Buyer shall make 3 payments of $25,000 ($70,000).')) == 1 and not ar('Buyer shall make 3 payments of $25,000 ($75,000).')
                and not ar('Buyer shall make 3 payments of $25,000 ($25,000 each).')))
    out.append(('arithmetic: a count in number words (fifteen, twenty-four)', len(ar('Buyer shall pay $60,000 in fifteen equal installments of $3,000.')) == 1
                and not ar('Buyer shall pay $60,000 in fifteen equal installments of $4,000.') and len(ar('Lessee shall pay $24,000 in twenty-four installments of $500.')) == 1))
    out.append(('arithmetic: thousands of digits and an overflowing percentage are skipped, not a crash',
                not ar('Buyer shall pay $100 in ' + '9' * 5000 + ' installments of $1.') and not ar('Buyer shall pay $' + '9' * 5000 + ' in 2 installments of $5.')
                and not ar('Buyer shall pay ' + '9' * 5000 + '% of the Purchase Price ($100).') and not ar('Buyer shall pay 30% of $1' + '0' * 60 + ' ($300) at Closing.')))
    # C3: (i) after (h) followed by (ii) is a subclause (typed); Word's list level decides for Word numbering
    body = 'I. ARTICLE ONE\n\nA. Heading.  Acme shall pay:\n\n' + ''.join(f'({c}) item {c};\n\n' for c in 'abcdefgh') + '(i) item i;\n\n(ii) item ii.\n\nB. Next.  Beta shall pay.\n'
    out.append(('outline: typed (i) after (h) followed by (ii) is a subclause, not an only child', not any(f['check'] == 'enumeration' for f in run_text(body, False)[2])))
    word = [{'idx': 0, 'auto_label': 'I.', 'auto_level': 0, 'text': 'ARTICLE ONE', 'where': 'body', 'fmt': {}},
            {'idx': 1, 'auto_label': 'A.', 'auto_level': 1, 'text': 'Heading.  Acme shall pay:', 'where': 'body', 'fmt': {}}]
    word += [{'idx': 2 + n, 'auto_label': f'({c})', 'auto_level': 2, 'text': f'item {c};', 'where': 'body', 'fmt': {}} for n, c in enumerate('abcdefgh')]
    word += [{'idx': 10, 'auto_label': '(i)', 'auto_level': 3, 'text': 'item i;', 'where': 'body', 'fmt': {}}, {'idx': 11, 'auto_label': '(ii)', 'auto_level': 3, 'text': 'item ii.', 'where': 'body', 'fmt': {}},
             {'idx': 12, 'auto_label': 'B.', 'auto_level': 1, 'text': 'Next.  Beta shall pay.', 'where': 'body', 'fmt': {}}]
    deeper = [f for f in outline_checks(word, document_shape(word)) if 'Only child' in f['message']]
    word[10]['auto_level'] = 2  # Word numbers (i) at the same level as (h): the letter i, so (ii) is a lone subclause
    same = [f for f in outline_checks(word, document_shape(word)) if 'Only child' in f['message']]
    out.append(("outline: Word's list level tells (i) the subclause from (i) the letter", not deeper and len(same) == 1 and same[0]['match'] == '(ii)'))
    # C4, R2: a longer term's uses don't count for the shorter term; a term with a non-word edge is counted
    res = run_text(intro + '.\n\n"Closing" means the closing of the sale.  "Closing Date" means the day on which the sale closes.\n\nSeller shall deliver the Shares on the Closing Date.\n')
    out.append(('defined-unused: Closing is unused when only Closing Date is used', any(f['check'] == 'defined-unused' and f['match'] == 'Closing' for f in res[2])))
    res = run_text(intro + '.\n\nBuyer shall pay the price (the "Purchase Price (Adjusted)") and the fee (the "Fee (Net)").\n\nBuyer shall pay the Purchase Price (Adjusted) and the Fee (Net) at the Closing.\n')
    out.append(('a term that ends in a parenthesis is counted (no false defined-unused or 2nd form)', not any(f['check'] in ('defined-unused', 'possibly-undefined-term') and f['match'] in ('Purchase Price (Adjusted)', 'Fee (Net)', 'Purchase Price', 'Fee') for f in res[2])
                and {r['term']: r['uses'] for r in res[4]}.get('Fee (Net)') == 1))
    # red team F2: a possessive before a lowercase nonparty subject; a PERSONISH noun with no agent suffix (counsel, surety)
    res = run_text(intro + ".\n\nSeller's counsel shall deliver to Buyer a legal opinion at the Closing.  The surety shall remain bound notwithstanding any change in the Work.  Seller's invoice shall state the amount due.\n", False)
    out.append(('a possessive nonparty subject (Seller\'s counsel shall) and a surety are flagged; an invoice is a thing',
                sorted(f['match'].split(' shall')[0] for f in res[2] if f['check'] == 'nonparty-obligation') == ['counsel', 'surety']))
    # C7: a singular import clause
    out.append(('IMPORTS reads "Each capitalized term"', bool(IMPORTS.search('Each capitalized term used in this amendment has the meaning given in the Agreement.'))))
    # C10: the phrase-variants file with the wrong shape is a data error
    out.append(('a phrase-variants file that is a list, or has no checks list, is an InputError', all(_raises(InputError, lambda d=d: _variant_entries(d)) for d in ([], {'about': 'x'}, {'checks': 'x'})) and _variant_entries({'checks': []}) == []))
    # C12: 2 patterns reading 1 definition are not a term defined twice; a term really defined twice in 1 paragraph is
    res = run_text(intro + '.\n\nSeller shall lease the Premises for 3 years (the "Term" is 3 years), and Buyer shall pay Rent during the Term.\n\nA. Definitions.  "Unit" means a widget.  "Unit" means a gadget.  Seller shall deliver each Unit.\n')
    out.append(('defined-twice: deduped on (kind, paragraph, position); a real repeat in 1 paragraph still counts', [f['match'] for f in res[2] if f['check'] == 'defined-twice'] == ['Unit']))
    # C13: shall after a closing quotation mark in the next paragraph is not shall in a definition
    res = run_text(intro + '.\n\nSeller shall deliver the goods listed under the heading "Goods"\n\nshall be void if Buyer fails to pay.\n\n"Unit" shall mean a widget.  Seller shall deliver each Unit.\n')
    out.append(('shall-in-definition never spans 2 paragraphs', [f['match'] for f in res[2] if f['check'] == 'shall-in-definition'] == ['"Unit" shall mean']))
    # C14, R3: a Markdown table's Total cell is located, not the 1st $80 in the table; a pipe table without outer pipes is read
    t = '| Item | Amount |\n|---|---|\n| Fee | $80 |\n| Credit | $20 |\n| Total | $80 |'
    f_ = table_total_checks([{'idx': 0, 'text': t}], None)
    out.append(('Markdown table: the finding points at the Total cell', len(f_) == 1 and f_[0]['start'] == t.rfind('$80') and t[f_[0]['start']:f_[0]['end']] == '$80'))
    t2 = 'Item | Amount | Note\n--- | --- | ---\nSetup | $100.00 | x\nSupport | $200.00 | y\nTotal | $400.00 |'  # a rate row (Monthly) would be no sum (PER_PERIOD)
    f_ = table_total_checks([{'idx': 0, 'text': t2}], None)
    out.append(('Markdown table without outer pipes is read; a sentence with a pipe is not a table', len(f_) == 1 and t2[f_[0]['start']:f_[0]['end']] == '$400.00'
                and not table_total_checks([{'idx': 0, 'text': 'Acme | Beta shall pay $5 | Total $5'}], None)))
    # C15: obligation-in-definition's match is the text at its offsets
    res = run_text(intro + '.\n\n"Approved Budget" means the budget in Schedule A, which Buyer shall approve in writing.  Seller shall follow the Approved Budget.\n')
    oid = [f for f in res[2] if f['check'] == 'obligation-in-definition']
    out.append(('obligation-in-definition: match == text[start:end], context in the message', len(oid) == 1 and res[0][oid[0]['para']]['text'][oid[0]['start']:oid[0]['end']] == oid[0]['match'] == 'shall' and 'which Buyer shall approve' in oid[0]['message']))
    # C19 is in cases; C5, C8, C9, C11 are in the variants' examples and look-alikes
    # R10: the bounded regex hints run in linear time on a 20,000-digit run; a paragraph over RULE_PARA_MAX skips the triggers with a note
    import time
    t0 = time.monotonic()
    for r, rx in load_rules()[0]:
        rx.search('9' * 20000)
        rx.search('$1 ' * 5000)
    out.append(('every rule trigger runs in under 2 seconds each on 20,000 digits (no quadratic hint)', time.monotonic() - t0 < 2 * len(load_rules()[0])))
    res = run_text(intro + '.\n\n' + 'Seller shall deliver the Units and/or the Parts. ' * 300 + '\n\nBuyer shall pay.\n', False)
    out.append(('a paragraph over 10,000 characters skips the rule triggers, with a note', res[1].get('long_paras') == [1] and any('over 10,000 characters' in n for n in report_notes(res[1], res[0]))
                and any(f['check'] == 'and-or' and f['para'] == 1 for f in res[2])))
    # R11: a fenced code block in Markdown is not contract text
    res = run_text('# AGREEMENT\n\n' + intro + '.\n\n```\nSeller shall pay the Rent within thirty (30) days.\n```\n\nSeller shall deliver.\n', False, '.md')
    out.append(('a fenced code block is dropped, with a note', res[1].get('code_blocks') == 1 and not any(f['check'] == 'words-and-digits' for f in res[2]) and [p['text'] for p in res[0]][-1] == 'Seller shall deliver.'))
    # S1: every rule id the code and the variants cite exists in the rule database
    src = open(os.path.abspath(__file__), encoding='utf-8').read()
    cited = set(re.findall(r"'(R-[\w.]+-[\w.-]+)'", src)) | {r for c in phrase_variants() for r in c['rule_ids']}
    out.append(('every rule id cited by the code tables and the variants exists in the rule database', all(r in _SEV for r in cited) and len(cited) > 50))
    # S2: collapse keeps a 2nd distinct bold-definition message and the document-default font beside a paragraph's font
    two = [{'check': 'bold-definition', 'severity': 3, 'para': 1, 'match': 'Acme', 'message': 'unbolded', 'confidence': 'medium', 'rule_ids': [], 'source': 'house'},
           {'check': 'bold-definition', 'severity': 3, 'para': 2, 'match': 'Beta', 'message': 'bold quotation marks', 'confidence': 'medium', 'rule_ids': [], 'source': 'house'},
           {'check': 'font', 'severity': 3, 'para': 1, 'match': '', 'message': 'Font Arial', 'confidence': 'high', 'rule_ids': [], 'source': 'house'},
           {'check': 'font', 'severity': 3, 'para': 2, 'match': '', 'message': 'Font Arial', 'confidence': 'high', 'rule_ids': [], 'source': 'house'},
           {'check': 'font', 'severity': 3, 'para': -1, 'match': '', 'message': 'Document default font is Arial', 'confidence': 'high', 'rule_ids': [], 'source': 'house'}]
    out.append(('collapse keeps distinct per-document messages', [(g['check'], g['message'], len(g['occurrences'])) for g in collapse(two)]
                == [('bold-definition', 'unbolded', 1), ('bold-definition', 'bold quotation marks', 1), ('font', 'Font Arial (2 places in 2 paragraphs: paras 1, 2)', 2), ('font', 'Document default font is Arial', 1)]))
    # S5: front findings on a contract with a 9-line table of contents before the introductory clause
    toc = ''.join(f'Article {n} Heading {n}\n\n' for n in range(1, 10))
    res = run_text(toc + 'This agreement is dated January 1, 2027, and is between Acme Widgets, Inc. ("Acme") and Widgetco LLC ("Widgetco").\n\nAcme shall sell the Units to Widgetco.\n', False)
    fr = [f['message'] for f in res[2] if f['check'] == 'front']
    out.append(('front findings (capitals, lead-in) appear behind a 9-line table of contents', any('capitals (' in m for m in fr) and any('No lead-in' in m for m in fr)))
    # S6: the sentence forms of a definition reach the term-of-art and circular checks
    res = run_text(intro + '.\n\nEach task that Seller gives Buyer is an "Assignment."  Buyer may not assign this agreement.\n\nThe "Carrier List" is the list of Approved Carriers.  The "Approved Carrier" is a carrier on the Carrier List.\n')
    out.append(('a term defined with is an "X" reaches the term-of-art check; the "X" is forms reach the circular check',
                any(f['check'] == 'term-of-art-defined' and f['match'] == 'Assignment' for f in res[2]) and any(f['check'] == 'circular-definition' for f in res[2])))
    # S7: single-quoted definitions count
    res = run_text(intro + ".\n\n'Deliverable' means each item in Schedule A.  Seller shall deliver each Deliverable at the closing (the 'Closing').  The Closing is on March 1, 2027.\n")
    out.append(("single-quoted definitions ('Deliverable' means; (the 'Closing')) enter the inventory", {'Deliverable', 'Closing'} <= {r['term'] for r in res[4]}
                and not any(f['check'] == 'possibly-undefined-term' and f['match'] in ('Deliverable', 'Closing') for f in res[2])))
    # S9: run() restores WHOSE; load_rules() is cached
    before = WHOSE
    rw = intro + '.\n\nSeller represents and warrants that it owns the Shares.\n'
    other = [f for f in lint_text(rw, whose='other-side')[2] if f['check'] == 'represents-warrants']
    mine = [f for f in lint_text(rw, whose='blake')[2] if f['check'] == 'represents-warrants']
    out.append(('--whose: other-side keeps represents and warrants (sev 3); blake gets the states finding (sev 2); run() restores WHOSE',
                other and other[0]['severity'] == 3 and 'Keep' in other[0]['message'] and mine and mine[0]['severity'] == 2 and 'use states' in mine[0]['message'] and WHOSE == before))
    out.append(('load_rules() is cached', load_rules() is load_rules()))
    # S13: severity ownership: an explicit severity is kept; a house rule or the rule record decides otherwise
    out.append(('severity_for: explicit, house, rule record, default', severity_for('x', [], 1) == 1 and severity_for('party-article', []) == 2
                and severity_for('x', ['R-3.89-shall-duty']) == _SEV['R-3.89-shall-duty'] and severity_for('x', ['R-none']) == 3 and sev_is_free('x', ['R-none']) and not sev_is_free('party-article', [])))
    # S14: a rule record with a field of the wrong type is rejected; a missing optional field is allowed
    from _rules_data import record_problem
    base = {'id': 'x', 'status': 'book', 'kind': 'rule', 'statement': 's', 'severity': 2}
    out.append(('record_problem checks every field the readers use', record_problem(base) is None and all(record_problem(dict(base, **kv)) for kv in (
        {'paras': '3.1'}, {'pdf_pages': ['3']}, {'trigger': {'words': 'x'}}, {'chapter': '3'}, {'examples': [1]}, {'section': 3}, {'counterparty_review': []}, {'trigger': []}))))
    out += _round8_docx_cases(_tmp)
    return out


def _round9_cases():
    """The round-9 hardening cases (each a failing input from the round-8 reviews, with a look-alike that stays clear): (name, passed) pairs."""
    out = []
    intro = 'This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company ("Seller"), and BETA INC., a Texas corporation ("Buyer").\n\n'

    def checks_of(text, inventory=False, suffix='.txt', want=None):
        res = lint_text(text, suffix, inventory)
        return [(f['check'], f['match']) for f in res[2] if want is None or f['check'] in want]

    def rule_hit(text, rid):
        return any(rid in (f.get('rule_ids') or []) for f in lint_text(text)[2])
    # A1: the harness note above a contract is skipped; a title that mentions a draft is read
    res = lint_text("Draft of November 2, 2026; Blake's client: Employee (other side's draft, prepared by counsel for Brightwater, LLC)\n\nSEPARATION AGREEMENT\n\nAcme shall pay.\n")
    out.append(('the harness note ("Draft of ...; Blake\'s client: ...") is skipped, its paragraph kept blank', not any(f['para'] == 0 for f in res[2]) and res[0][0]['text'] == '' and res[1].get('harness_header')))
    res = lint_text("*Lender's draft of November 3, 2026; Blake's client: Guarantor*\n\nAcme shall pay.\n")
    out.append(('the harness note in Markdown emphasis is skipped', res[0][0]['text'] == ''))
    out.append(('a title that names a draft is not the harness note', lint_text('DRAFT OF SUPPLY AGREEMENT\n\nAcme shall pay.\n')[0][0]['text'] == 'DRAFT OF SUPPLY AGREEMENT'))
    # A2: covenant: restrictive covenants and a quoted heading reference stay; a heading's own covenant is flagged (MSCD 3.188)
    usage = lambda t: [m for c, m in checks_of(t, want={'usage'}) if 'ovenant' in m]
    out.append(('covenant: restrictive covenants and the section titled "Financial Covenants" stay clear',
                not usage('ARTICLE VII. RESTRICTIVE COVENANTS\n\nThe restrictive covenants survive.  Borrower fails to perform any obligation in the section titled "Financial Covenants".')))
    out.append(('covenant: a heading "Financial Covenants" and "each covenant" are flagged', len(usage('A. Financial Covenants.  Borrower shall maintain the ratio.  Each covenant survives.')) == 2))
    # A3: nonparty subjects: a recital's other agreement doesn't make Borrower a party; a role holder who signs is a party
    g = ('This guaranty is dated January 1, 2027, and is between JOHN OAKES, an individual ("Guarantor"), and ACME LLC, a Delaware limited liability company ("Lender").\n\n'
         'Lender is lending to Oakes Fabrication, LLC, a Tennessee limited liability company ("Borrower"), under a loan agreement between Borrower and Lender.\n\n'
         'Borrower shall deliver to Guarantor each notice of default.  Guarantor shall pay on demand.\n')
    out.append(('a nonparty defined in a recital (Borrower in a guaranty) is not a party: Borrower shall is flagged, Guarantor shall is not',
                [m.split(' shall')[0] for c, m in checks_of(g, want={'nonparty-obligation'})] == ['Borrower']))
    mp = ('This agreement is dated January 5, 2027, and is among the following parties:\n\nAlpha Holdings LLC, a Delaware limited liability company ("Alpha");\n\n'
          'Beta Partners LP, a Texas limited partnership ("Beta"); and\n\nGamma Trust Company, a Tennessee corporation ("Gamma").\n\n'
          'Gamma is lending to Delta Mills LLC, a Georgia limited liability company ("Borrower"), under a loan agreement between Borrower and Gamma.\n\n'
          'Gamma shall hold the Escrow Funds.  Beta shall deliver the Shares.  Borrower shall repay the loan.\n')
    out.append(('an introductory clause that lists each party in its own paragraph names every party (Gamma is a party; Borrower, defined in the recital, is not)',
                [m.split(' shall')[0] for c, m in checks_of(mp, want={'nonparty-obligation'})] == ['Borrower']))
    llc = ('This operating agreement is dated January 1, 2027, and is between ACME LLC, a Tennessee limited liability company (the "Company"), and BETA INC., a Texas corporation ("Beta").\n\n'
           '"Manager" means Dale Marchetti, or any successor manager that the Members elect.\n\nThe Manager shall deliver the reports.  The Manager may make any tax election, except that the Manager shall not elect to treat the Company as a corporation.\n\n'
           'ACME LLC\nBy: ______________\nDale Marchetti, Manager\n\n______________\nDale Marchetti\n\nBETA INC.\nBy: ______________\nName: Ann Lee\n')
    out.append(('a role term whose holder signs in their own name (the Manager) is a party: no nonparty-obligation or category-shall',
                not checks_of(llc, want={'nonparty-obligation', 'category-shall'})))
    out.append(('a role holder who signs only for an entity (By: ... Name:) stays a nonparty', len(checks_of(llc.replace('______________\nDale Marchetti\n\n', ''), want={'nonparty-obligation'})) == 2))
    out.append(('except that Supplier shall pay: Supplier is the subject (no category-shall); a thing after except that still is one',
                not checks_of(intro + 'Each party shall pay its own expenses, except that Seller shall pay the escrow fees.', want={'category-shall'})
                and checks_of(intro + 'The fee is $5, except that the fee shall be $7 in 2028.', want={'category-shall'})))
    out.append(('a hyphenated nonparty (sub-distributors) and a who-clause subject (a project sponsor, who shall) are flagged; a party antecedent is not',
                len(checks_of(intro + "Seller's sub-distributors shall honor the warranty.  Seller shall appoint a project sponsor, who shall review each report.  Seller shall notify Buyer, who shall then pay.", want={'nonparty-obligation'})) == 2))
    # A4: a fixed date after the lead word is a stated time: the present tense is right
    will = lambda t: checks_of(t, want={'category-will'})
    out.append(('category-will: Upon July 1, 2028, the Annual Fee increases is clear; Upon Closing, the Annual Fee increases is flagged',
                not will('Upon July 1, 2028, the Annual Fee increases by 3%.') and will('Upon Closing, the Annual Fee increases by 3%.')))
    # A5, A6: the inventory
    inv = lambda t, sfx='.txt': [(c, m) for c, m in checks_of(t, True, sfx, {'possibly-undefined-term', 'defined-twice'})]
    out.append(('possibly-undefined-term: Substantial Completion and Membership Percentages are reported',
                {m for c, m in inv(intro + 'Seller shall achieve Substantial Completion by June 30, 2027, and distribute cash by Membership Percentages.')} >= {'Substantial Completion', 'Membership Percentages'}))
    out.append(('possibly-undefined-term: a sentence-initial adjective before a defined term (Overdue Rent) is clear; an undefined Overdue Fees is reported',
                not inv(intro + '"Rent" means $100 a month.  Buyer shall pay Rent monthly.  Overdue Rent bears interest at 10% per year.')
                and inv(intro + 'Buyer shall pay the fees monthly.  Overdue Fees bear interest at 10% per year.  Buyer shall pay the Overdue Fees.')))
    md = intro + 'Seller shall build to the drawings.\n\nSCHEDULE A\n\n| Sheet | Title | Date |\n|---|---|---|\n| S-101 | Foundation and Anchor Bolt Plan | September 12, 2026 |\n| S-203 | Roof Framing Plan | September 12, 2026 |\n'
    txt = intro + 'Buyer shall buy the printers.\n\nSCHEDULE A\n\nModel            Description                          Reseller Price\nTG-410           Desktop label printer                $212\nTG-420           Industrial label printer             $489\n'
    out.append(('possibly-undefined-term: drawing titles in a Markdown table and a typed table heading row are clear', not inv(md, '.md') and not inv(txt)))
    sch = intro + '"Error" means a failure of the Software.  Seller shall correct each Error.\n\nSCHEDULE A\n\nIn this Schedule A, "Error" means a reproducible failure.  Seller shall fix each Error.\n'
    out.append(('defined-twice: a 2nd definition inside a schedule (In this Schedule A, "Error" means) counts; an exhibit form\'s own definitions do not',
                ('defined-twice', 'Error') in inv(sch) and ('defined-twice', 'Error') not in inv(sch.replace('SCHEDULE A', 'EXHIBIT 1\nFORM OF CERTIFICATE'))))
    rows = lint_text(intro + 'Seller shall deliver the release in Exhibit 1.\n\nEXHIBIT 1 — FORM OF RELEASE\n\nSeller releases Buyer and its affiliates (the "Released Parties") from all claims.\n', '.md', True)[4]
    out.append(('inventory: a term defined only inside an exhibit gets a row marked exhibit', any(r['term'] == 'Released Parties' and r['defined'] == ['exhibit'] for r in rows)))
    # A7: typed numbers in .md or .txt are no typed-numbering finding (they can't carry Word's numbering)
    body = intro + ''.join(f'{n}. Heading {n}.  Seller shall pay.\n\n' for n in range(1, 5))
    out.append(('typed-numbering: not reported on a .md or .txt file', not checks_of(body, suffix='.md', want={'typed-numbering'}) and not checks_of(body, want={'typed-numbering'})))
    # A8, A9, A13, A15: rule triggers narrowed to their rule's pattern
    out.append(('R-6.9: an all-caps heading or name is no abbreviation; SEC in a sentence is', not rule_hit('2. TERM.  HOLLIS RIDGE CAPITAL, LLC shall pay the fee.', 'R-6.9-define-all-abbreviations')
                and rule_hit('Acme shall file the report with the SEC.', 'R-6.9-define-all-abbreviations')))
    out.append(('R-13.129: Closing Date and the Closing are clear; at Closing is flagged', not rule_hit('On the Closing Date, Buyer shall pay.  At the Closing, Seller shall deliver.', 'R-13.129-the-closing')
                and rule_hit('At Closing, Seller shall deliver the Shares.', 'R-13.129-the-closing')))
    out.append(('R-13.862: the earliest of (a), (b), and (c) is clear; the earlier of X or Y is flagged', not rule_hit('Payment is due on the earliest of (a) the Closing, (b) the termination, and (c) December 31, 2027.', 'R-13.862-earlier-of-x-and-y')
                and rule_hit('Payment is due on the later of the Closing or December 31, 2027.', 'R-13.862-earlier-of-x-and-y')))
    out.append(('R-3.222: may ... only before a time phrase (MSCD 13.651) and may ... only if (3.363) are clear; may only move is flagged',
                not rule_hit('Buyer may operate the Equipment only from April 1 to October 31.', 'R-3.222-may-only-ambiguous')
                and not rule_hit('Tenant may move furniture into the Premises only during nonbusiness hours.', 'R-3.222-may-only-ambiguous')
                and not rule_hit('Acme may sell the Shares only if Widgetco consents.', 'R-3.222-may-only-ambiguous') and rule_hit('Tenant may only move furniture.', 'R-3.222-may-only-ambiguous')))
    out.append(('R-4.6: a bracketed placeholder ($[5], [5] days) is no footnote; [^1] is', not rule_hit('The price is $[5] per Unit, payable within [10] days.', 'R-4.6-no-footnotes') and rule_hit('The price is fixed.[^1]', 'R-4.6-no-footnotes')))
    # A10-A12, A14, A18: serial comma, immediately due, both days included, runs from ... to
    out.append(('serial-comma: a modal aside (may, without notice ... and without affecting ..., extend or renew) is no list; copy, modify and distribute is',
                not checks_of('Lender may, without notice to Guarantor and without affecting its rights, extend or renew the Obligations.', want={'serial-comma'})
                and checks_of('Acme shall copy, modify and distribute the Software.', want={'serial-comma'})))
    out.append(('immediately due and payable is clear (MSCD 10.127); shall immediately notify is flagged', not checks_of('Lender may declare the Loan immediately due and payable.', want={'usage'})
                and checks_of('Seller shall immediately notify Buyer.', want={'usage'})))
    tod = lambda t: checks_of(t, want={'time-of-day', 'time-ambiguity'})
    # time-of-day on "ends on [date]" stays until Blake decides (question Q7), even with both days included
    out.append(('a window with both days included is clear of time-ambiguity; time-of-day on its end date stays (Q7)',
                tod('The Term starts on January 1, 2027, and ends on December 31, 2029, both days included.') == [('time-of-day', 'ends on December 31, 2029')]
                and not tod('Buyer may return Units from January 1, 2027, through March 31, 2027, both days included.')))
    k = collapse([finding('font', 'Font Arial', 15, sev=3, match='x', start=0, end=1), finding('font', 'Font Arial', 15, sev=3, match='y', start=5, end=6)])
    out.append(('collapse: 2 places in 1 paragraph say so', len(k) == 1 and k[0]['message'].endswith('(2 places in 1 paragraph: para 15)')))
    out.append(('time-of-day: runs from [date], to [date] is flagged', ('time-of-day', 'runs from January 1, 2027, to December 31, 2029') in tod('The Term runs from January 1, 2027, to December 31, 2029.')))
    # A16, A17: comment text kept whole; a schedule's counterparty is not a signature block
    sched = ('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company ("Seller"), and BETA INC., a Texas corporation ("Buyer").\n\n'
             'Seller shall sell.\n\nACME LLC\nBy: ____\n\nBETA INC.\nBy: ____\n\nSCHEDULE A\n\nContracts\n\nMeridian Acme Supply Co.\n')
    out.append(('front: a counterparty listed in a schedule is not a signature-block name', not any('Signature block' in f['message'] for f in lint_text(sched)[2])))
    # E5: a named body amount that a schedule restates (MSCD 1.56)
    rs = intro + 'Buyer shall pay the Support Fee of $24,000 each year.\n\nSCHEDULE A\n\nAnnual Support Fee: $24,000\n'
    out.append(('restated-amount: the Support Fee of $24,000 restated in Schedule A is flagged; a schedule with another amount is not',
                [m for c, m in checks_of(rs, want={'restated-amount'})] == ['the Support Fee of $24,000'] and not checks_of(rs.replace('Fee: $24,000', 'Fee: $30,000'), want={'restated-amount'})))
    out.append(('comment text is kept whole; the report shortens it with ...', _shorten('x' * 400, COMMENT_SHOWN).endswith('...') and _shorten('short', COMMENT_SHOWN) == 'short'))
    many = [('A', f'comment {n}', None) for n in range(12)] + [('B', 'reply', 11)]
    notes = report_notes({'comments': many}, [])
    out.append(('the comments list says how many more it holds (ROB-010)', any(n.startswith('  - ... and 2 more comments') for n in notes)
                and not any('more comments' in n for n in report_notes({'comments': many[:10]}, []))))
    return out


def _round10_cases(_tmp):
    """The round-10 cases (the board review and the adversarial probe), each a (name, passed) pair."""
    out = []
    intro = 'This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company ("Seller"), and BETA INC., a Texas corporation ("Buyer").\n\n'

    def checks_of(text, inventory=False, suffix='.txt', want=None, whose=None):
        res = lint_text(text, suffix, inventory, whose)
        return [(f['check'], f['match']) for f in res[2] if want is None or f['check'] in want]
    # ACC-004: a short introductory clause (10 words) still names the parties
    short = 'This agreement is between ACME LLC ("Acme") and BETA INC. ("Beta").\n\nAcme will deliver the Units.  Beta must pay the Price.  The Company that owns the Site is not a party.\n'
    got = {c for c, m in checks_of(short)}
    out.append(('a 10-word introductory clause names the parties: Acme will is category-will, and the Company (a nonparty) keeps its article (ACC-004)',
                {'category-will', 'category-must'} <= got and 'party-article' not in got))
    # ACC-008: a capitalized nonparty role in a fragment is a low-confidence candidate; with the parties known it is medium
    frag = [f for f in lint_text('The Trustee shall distribute the income to the beneficiaries each quarter.\n')[2] if f['check'] == 'nonparty-obligation']
    known = [f for f in lint_text(intro + 'The Trustee shall distribute the income to the beneficiaries each quarter.\n')[2] if f['check'] == 'nonparty-obligation']
    out.append(('nonparty-obligation on a fragment is low confidence and says the parties are unknown; with an introductory clause it is medium (ACC-008)',
                frag and frag[0]['confidence'] == 'low' and 'parties are unknown' in frag[0]['message'] and known and known[0]['confidence'] == 'medium'))
    # ACC-010: a 70-line table of contents before the introductory clause and the lead-in: the recital's will is not a duty
    toc = ''.join(f'Article {n} Heading {n}\n\n' for n in range(1, 71))
    res = lint_text(toc + intro + 'Seller owns the Assets, and Buyer will operate the Business after the Closing.\n\nThe parties therefore agree as follows:\n\nSeller will deliver the Assets.\n')
    wills = [f for f in res[2] if f['check'] == 'category-will']
    out.append(('a 70-line table of contents does not hide the lead-in: will in the recital is not a duty, will in the body is (ACC-010)',
                len(wills) == 1 and 'deliver' in res[0][wills[0]['para']]['text']))
    # ACC-003: the thing-subject message offers must and cites R-3.154
    cs = [f for f in house_checks({'idx': 0, 'text': 'Final Completion shall occur no later than July 31, 2027.', 'fmt': {}}) if f['check'] == 'category-shall']
    out.append(('category-shall on a thing or event offers must (MSCD 3.154) and keeps R-3.98 first (ACC-003)',
                cs and 'write must' in cs[0]['message'] and cs[0]['rule_ids'] == ['R-3.98-shall-future-time', 'R-3.154-must-for-others'] and cs[0]['severity'] == 3))
    # ROB-001: invisible characters are stripped and counted
    res = lint_text(intro + 'Seller shall protect the information (the "Confi\u00addential Information").  Buyer shall keep the Confidential Information secret.  Seller shall return the Confidential Information.  Buyer may use the Confidential\u200b Information.\n', inventory=True)
    out.append(('a soft hyphen and a zero-width space are removed and noted: no 2nd form, no unused term (ROB-001)',
                res[1].get('invisible_chars') == 2 and any('invisible characters' in n for n in report_notes(res[1], res[0]))
                and not any(f['check'] in ('possibly-undefined-term', 'defined-unused') for f in res[2])))
    # ROB-002: quoted, section-numbered and 1-line form labels are attachment headings; a reference in running text is not
    quoted = intro + 'Seller shall deliver the release in Exhibit 1.\n\nEXHIBIT "1"\n\nFORM OF RELEASE\n\n"Agreement" means the asset purchase agreement.  Executive gives this release under the Agreement.\n'
    out.append(('EXHIBIT "1" (a quoted label) is an exhibit heading: its definitions are not defined twice (ROB-002)', not checks_of(quoted, True, want={'defined-twice'})
                and EXHIBIT_HEAD.match('SCHEDULE 1.1') and EXHIBIT_HEAD.match('Schedule 3.2(a)') and EXHIBIT_HEAD.match('EXHIBIT A FORM OF PROMISSORY NOTE')
                and not EXHIBIT_HEAD.match('Exhibit A lists the Assets.') and not EXHIBIT_HEAD.match('Schedule 1, as updated from time to time, lists the Products.')))
    # ROB-007: a malformed addition or lint block in the overrides, and a hint that matches whitespace, are data errors
    import json as _json
    from _rules_data import load_overrides as _lo
    def bad_ov(ov):
        f_ = _tmp(_json.dumps(ov).encode('utf-8'), '.json')
        try:
            return _raises(InputError, lambda: _lo(f_))
        finally:
            os.unlink(f_)
    out.append(('house-overrides: a malformed addition, a string broad_only and a list suppress are rejected; a good file is read (ROB-007)',
                bad_ov({'overrides': [], 'additions': [{'statement': 5}]}) and bad_ov({'overrides': [], 'lint': {'broad_only': 'R-1'}}) and bad_ov({'overrides': [], 'lint': {'suppress': []}})
                and not bad_ov({'overrides': [], 'additions': [{'statement': 's', 'applies_with': ['R-1']}], 'lint': {'suppress': {'R-1': 'x'}, 'broad_only': []}})))
    out.append(('a regex_hint that matches whitespace alone, or does not compile, is reported (ROB-007)', compile_hint(r'\s*')[1] and compile_hint('(')[1] and compile_hint(r'\bshall\b')[1] is None))
    # ROB-008: the reference generator refuses to run without a hand-written header, and writes atomically
    import build_references as _br
    from _cli import write_text as _wt
    import tempfile as _tf
    saved = (_br.HEADERS, _br.REFS, sys.argv)
    with _tf.TemporaryDirectory() as td:
        _br.HEADERS, _br.REFS, sys.argv = os.path.join(td, 'no-such-ref-headers'), td, ['build_references.py']  # never the skill's own references
        try:
            out.append(('build_references: a missing header is an InputError, not a silent bare title (ROB-008)', _raises(InputError, _br.main) and not os.listdir(td)))
        finally:
            _br.HEADERS, _br.REFS, sys.argv = saved
    f_ = _tmp(b'old', '.md')
    try:
        _wt(f_, 'new')
        with open(f_, encoding='utf-8') as fh:
            written = fh.read()
        out.append(('write_text replaces the file whole (ROB-008)', written == 'new' and not [x for x in os.listdir(os.path.dirname(f_)) if x.startswith('.tmp-') and x.endswith('.md')]))
    finally:
        os.unlink(f_)
    # ROB-004: --json is written even when the reader closes the pipe after the 1st line
    import subprocess as _sp
    fc = _tmp((intro + 'Seller shall deliver the Units and/or the Parts. ' * 400 + '\n').encode('utf-8'))
    fj = fc + '.json'
    try:
        _sp.run(f'"{sys.executable}" "{os.path.abspath(__file__)}" "{fc}" --json "{fj}" | head -1', shell=True, capture_output=True, check=False)
        written = {}
        if os.path.exists(fj):
            with open(fj, encoding='utf-8') as fh:
                written = _json.load(fh)
        out.append(('--json is written before the report, so | head leaves no stale lint.json (ROB-004)', written.get('file') == fc))
    finally:
        os.unlink(fc)
        if os.path.exists(fj):
            os.unlink(fj)
    # probe: a signatory named by its role alone (as escrow agent) is a party for the subject checks, with or without a defined term
    escrow = ('This agreement is dated January 15, 2027, and is between CUMBERLAND HOLDINGS, INC., a Tennessee corporation ("Buyer"), ORION FABRICATION LLC, '
              'a Delaware limited liability company ("Seller"), and HARBOR TITLE LLC, a Tennessee limited liability company, as escrow agent{}.\n\n'
              'The parties agree as follows:\n\n{} shall hold the Deposit in a segregated account at Pinnacle Bank until the Closing.\n')
    out.append(('a signatory named as escrow agent is a party: the escrow agent shall (unquoted) and Escrow Agent shall (defined) both clear nonparty-obligation',
                not checks_of(escrow.format('', 'The escrow agent'), want={'nonparty-obligation', 'party-article'})
                and not checks_of(escrow.format(' ("Escrow Agent")', 'Escrow Agent'), want={'nonparty-obligation'})
                and checks_of(intro + 'The escrow agent shall hold the Deposit until the Closing.\n', want={'nonparty-obligation'})))
    # probe: quoted text keeps its verbs; the unquoted clause with a nonparty subject still fires; a 4-word statutory quotation clears execute
    req = intro + 'Each Subcontract must contain the following sentence (the "Required Clause"): {}Subcontractor shall not disclose any Buyer Confidential Information to any Person other than Subcontractor\'s employees who need to know it.{}\n'
    out.append(('a quoted clause another contract must contain keeps its shall; the unquoted form with no Subcontractor party fires',
                not checks_of(req.format('"', '"'), want={'nonparty-obligation', 'category-shall'}) and checks_of(req.format('', ''), want={'nonparty-obligation'})))
    out.append(('a 4-word statutory quotation ("at the time of executing the release.") clears execute; a 2-word quotation does not',
                not checks_of(intro + 'Employee hereby waives the protection of Section 1542 of the California Civil Code, which covers claims that a releasing party does not know of "at the time of executing the release."\n', want={'archaic'})
                and checks_of(intro + 'Employee shall sign the form marked "duly executed" at the Closing.\n', want={'archaic'})))
    out.append(('a quoted will or shall cause keeps its verb', not checks_of(intro + 'The Guaranty must read: "Guarantor will pay each amount when due and shall cause its lenders to release the lien."\n', want={'category-will', 'nonparty-obligation'})))
    # probe: is entitled to fires as a finding only where it stands in for another party's duty; otherwise it is a trigger
    ent = lambda t: [f['source'] for f in house_checks({'idx': 0, 'text': t, 'fmt': {}}) if f['check'] == 'is-entitled-to']
    out.append(('is-entitled-to: a direct finding wherever another party could owe the thing; a trigger only for a condemnation award or a right a plan or the law creates',
                ent('Consultant is entitled to receive the Fee at the Closing.') == ['house'] and ent('Consultant is entitled to reimbursement from Company.') == ['house']
                and ent('Contractor is entitled to an extension of the Completion Date.') == ['house'] and ent('Sponsor is entitled to 20 complimentary tickets.') == ['house']
                and ent('Tenant is entitled to quiet enjoyment of the Premises.') == ['house'] and ent('Employee is entitled to participate in each benefit plan.') == ['house']
                and ent('Buyer is entitled to the entire condemnation award for the Property.') == ['rules']
                and ent('Employee is entitled to the benefits under the Company 401(k) Plan.') == ['rules']))
    # probe: a section heading in capitals; an article heading and an exhibit label are not
    caps = intro + 'I. FIRST ARTICLE\n\nA. SERVICES.  Seller shall perform the Services.\n\nB. FEES AND PAYMENT.  Buyer shall pay the Fee.\n\nII. SECOND ARTICLE\n\nA. Term.  The Term is 2 years.\n\nB. Use.  Buyer may use the Units.\n\nEXHIBIT 1\n\nFORM OF NOTE\n'
    sh = [f for f in lint_text(caps)[2] if f['check'] == 'section-heading-caps']
    out.append(('section headings in all capitals (A. SERVICES.) are flagged once at severity 3; Services, Use, ARTICLE and EXHIBIT lines are not',
                len(sh) == 1 and sh[0]['match'] == 'SERVICES' and '2 section headings' in sh[0]['message'] and sh[0]['severity'] == 3
                and not [f for f in lint_text(caps.replace('SERVICES', 'Services').replace('FEES AND PAYMENT', 'Fees and Payment'))[2] if f['check'] == 'section-heading-caps']))
    # probe: an all-capitals party-name defined term; an acronym with another kind of definition stays
    pt = lambda t: [f['match'] for f in lint_text(t)[2] if f['check'] == 'party-term-capitals']
    out.append(('"ACME" means Acme Widgets, Inc., a Tennessee corporation is flagged (MSCD 2.96); "SOW" means a statement of work is not',
                pt(intro + '"ACME" means Acme Widgets, Inc., a Tennessee corporation.  "SOW" means a statement of work that the parties sign.  "LLC" means a limited liability company.\n') == ['ACME']
                and pt('This agreement is between ACME WIDGETS, INC., a Tennessee corporation ("ACME"), and DANA RUIZ, an individual ("Consultant").\n') == ['ACME']
                and not pt(intro + '"GAAP" means generally accepted accounting principles in the United States.\n')))
    # probe: a conspicuous disclaimer in capitals is a trigger, not a finding; body text in capitals is a finding
    disc = [f for f in lint_text(intro + 'SELLER DISCLAIMS ALL IMPLIED WARRANTIES, INCLUDING THE IMPLIED WARRANTY OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.\n')[2] if f['check'] == 'capitals-body']
    body_caps = [f for f in lint_text(intro + 'BUYER SHALL PAY THE FEE NO LATER THAN 30 DAYS AFTER RECEIVING AN INVOICE FROM SELLER.\n')[2] if f['check'] == 'capitals-body']
    out.append(('a conspicuous disclaimer in capitals is a rule trigger (MSCD 16.19 prefers bold; a statute-driven form stays); body text in capitals is a direct finding',
                len(disc) == 1 and disc[0]['source'] == 'rules' and 'prefers bold' in disc[0]['message'] and len(body_caps) == 1 and body_caps[0]['source'] == 'house'))
    # probe: "Business Day" shall mean is caught at the sentence level, and once with --inventory
    bd = lambda inv: [f for f in lint_text(intro + '"Business Day" shall mean a day other than a Saturday or Sunday.  Seller shall deliver on a Business Day.\n', inventory=inv)[2] if f['check'] == 'shall-in-definition']
    out.append(('"Business Day" shall mean is a sentence-level finding without --inventory, and 1 finding (not 2) with it', len(bd(False)) == 1 and len(bd(True)) == 1))
    # probe: a file of whitespace and punctuation gets the no-text note
    out.append(('a file that holds only whitespace and punctuation gets the "No text found" note', any('No text found' in n for n in report_notes({}, [{'idx': 0, 'text': ' \u201c\u201d \u2018\u2019 , . '}]))
                and not any('No text found' in n for n in report_notes({}, [{'idx': 0, 'text': 'Acme shall pay.'}]))))
    return out


def _round8_docx_cases(_tmp):
    """The round-8 .docx reader cases; [] without python-docx."""
    try:
        import docx as _dx
        from docx.oxml import parse_xml as _px
        from docx.oxml.ns import nsdecls as _nsd
    except ImportError:
        return []
    import zipfile
    out = []
    W = _nsd('w')

    def build(fill):
        d = _dx.Document()
        d.add_paragraph('AGREEMENT')
        fill(d)
        f_ = _tmp(b'', '.docx')
        d.save(f_)
        return f_

    def read(f_):
        try:
            return read_paragraphs(f_)
        finally:
            os.unlink(f_)
    # R4, R6: a run property Word's format rejects keeps the paragraph's text; the formatting is noted as unread
    def sz_abc(d):
        r = d.add_paragraph().add_run('Lessee shall pay the Rent.')
        r._r.get_or_add_rPr().append(_px(f'<w:sz {W} w:val="abc"/>'))
    paras, meta = read(build(sz_abc))
    out.append(('a <w:sz w:val="abc"/> run keeps its paragraph, with formatting_unread noted', paras[1]['text'] == 'Lessee shall pay the Rent.' and meta.get('formatting_unread') == 1
                and any('formatting' in n for n in report_notes(meta, paras))))
    # R7: hidden text is skipped and counted
    def vanish(d):
        para = d.add_paragraph()
        para.add_run('Lessee shall pay ')
        para.add_run('nothing').\
            _r.get_or_add_rPr().append(_px(f'<w:vanish {W}/>'))
        para.add_run('the Rent.')
    paras, meta = read(build(vanish))
    out.append(('a hidden-text run is skipped and counted', paras[1]['text'] == 'Lessee shall pay the Rent.' and meta.get('hidden_runs') == 1))
    # R1: an equation's text (m:t) reads in line, and the equations are counted
    def equation(d):
        para = d.add_paragraph('The Fee is ')
        para._p.append(_px('<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><m:r><m:t>Price × 1.05</m:t></m:r></m:oMath>'))
    paras, meta = read(build(equation))
    out.append(('a Word equation reads as text, with a count', paras[1]['text'] == 'The Fee is Price × 1.05' and meta.get('equations') == 1))
    # R13: a deleted paragraph mark is counted and noted
    def mark(d):
        para = d.add_paragraph('Lessee shall pay a late fee.')
        para._p.get_or_add_pPr().append(_px(f'<w:rPr {W}><w:del w:id="7" w:author="X" w:date="2027-01-01T00:00:00Z"/></w:rPr>'))
        d.add_paragraph('Lessee shall also pay interest.')
    paras, meta = read(build(mark))
    out.append(('a tracked deletion of a paragraph mark is counted and noted', meta.get('para_mark_deletions') == 1 and len(paras) == 3))
    # R12: a reply (commentsExtended.xml, paraIdParent) is listed under its parent comment
    def commented(d):
        para = d.add_paragraph()
        para._p.append(_px(f'<w:commentRangeStart {W} w:id="0"/>'))
        para.add_run('Lessee shall insure the Equipment.')
        para._p.append(_px(f'<w:commentRangeEnd {W} w:id="0"/>'))
        para._p.append(_px(f'<w:r {W}><w:commentReference w:id="0"/></w:r>'))
        para._p.append(_px(f'<w:r {W}><w:commentReference w:id="1"/></w:r>'))
    f_ = build(commented)
    comments = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:comments {W} xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml">'
                '<w:comment w:id="0" w:author="Opposing Counsel"><w:p w14:paraId="AAAA0001"><w:r><w:t>Add a minimum.</w:t></w:r></w:p></w:comment>'
                '<w:comment w:id="1" w:author="Blake Reagan"><w:p w14:paraId="AAAA0002"><w:r><w:t>Agreed.</w:t></w:r></w:p></w:comment></w:comments>')
    ext = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w15:commentsEx xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml">'
           '<w15:commentEx w15:paraId="AAAA0001" w15:done="0"/><w15:commentEx w15:paraId="AAAA0002" w15:paraIdParent="AAAA0001" w15:done="0"/></w15:commentsEx>')
    parts = (('comments.xml', comments, 'application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments', 'rId901'),
             ('commentsExtended.xml', ext, 'application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml', 'http://schemas.microsoft.com/office/2011/relationships/commentsExtended', 'rId902'))
    tmp2 = f_ + '.2'
    with zipfile.ZipFile(f_) as zin, zipfile.ZipFile(tmp2, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == '[Content_Types].xml':
                data = data.replace(b'</Types>', ''.join(f'<Override PartName="/word/{n}" ContentType="{ct}"/>' for n, _, ct, _, _ in parts).encode() + b'</Types>')
            if item.filename == 'word/_rels/document.xml.rels':
                data = data.replace(b'</Relationships>', ''.join(f'<Relationship Id="{rid}" Type="{rt}" Target="{n}"/>' for n, _, _, rt, rid in parts).encode() + b'</Relationships>')
            zout.writestr(item, data)
        for n, content, _, _, _ in parts:
            zout.writestr('word/' + n, content)
    os.replace(tmp2, f_)
    paras, meta = read(f_)
    notes = report_notes(meta, paras)
    out.append(('a comment reply is read from commentsExtended.xml and listed under its parent', meta.get('comments') == [('Opposing Counsel', 'Add a minimum.', None), ('Blake Reagan', 'Agreed.', 0)]
                and any(n.startswith('    - reply by Blake Reagan') for n in notes)))
    # ROB-006: an entity declared inside a comments part is not expanded (python-docx's own parser setting)
    f_ = build(commented)
    ent = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><!DOCTYPE w:comments [<!ENTITY leak "SECRET">]><w:comments {W}>'
           '<w:comment w:id="0" w:author="X"><w:p><w:r><w:t>Add &leak; here.</w:t></w:r></w:p></w:comment></w:comments>')
    tmp2 = f_ + '.2'
    with zipfile.ZipFile(f_) as zin, zipfile.ZipFile(tmp2, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == '[Content_Types].xml':
                data = data.replace(b'</Types>', f'<Override PartName="/word/comments.xml" ContentType="{parts[0][2]}"/></Types>'.encode())
            if item.filename == 'word/_rels/document.xml.rels':
                data = data.replace(b'</Relationships>', f'<Relationship Id="rId901" Type="{parts[0][3]}" Target="comments.xml"/></Relationships>'.encode())
            zout.writestr(item, data)
        zout.writestr('word/comments.xml', ent)
    os.replace(tmp2, f_)
    paras, meta = read(f_)
    out.append(('an entity declared in a comments part is never expanded into the comment text: the part is refused and noted as unreadable (ROB-006)',
                not any('SECRET' in c[1] for c in meta.get('comments') or []) and bool(meta.get('comments') or meta.get('comments_unreadable'))))
    # ROB-001: a soft hyphen typed into a run is removed and counted
    def soft(d):
        d.add_paragraph('Lessee shall keep the Confi\u00addential Information secret.')
    paras, meta = read(build(soft))
    out.append(('a soft hyphen inside a run is removed and counted (ROB-001)', paras[1]['text'] == 'Lessee shall keep the Confidential Information secret.' and meta.get('invisible_chars') == 1))
    # R5: a damaged theme or docDefaults part is best effort
    class _Broken:
        part = property(lambda self: (_ for _ in ()).throw(RuntimeError('damaged')))
        styles = part
    out.append(('theme_fonts and doc_default_font survive any error', theme_fonts(_Broken()) == {} and doc_default_font(_Broken()) == (None, None)))
    return out


def _tmp(data, suffix='.txt'):
    """Write bytes to a temporary file and return its path (the caller deletes it)."""
    import tempfile
    with tempfile.NamedTemporaryFile('wb', suffix=suffix, delete=False) as fh:
        fh.write(data)
    return fh.name


def lint_text(text, suffix='.txt', inventory=False, whose=None):
    """run() on text (str, or bytes for an encoding test) written to a temporary file: (paras, meta, findings, broad, inventory)."""
    f_ = _tmp(text.encode('utf-8') if isinstance(text, str) else text, suffix)
    try:
        return run(f_, inventory, whose)
    finally:
        os.unlink(f_)


def _read_tmp(data, suffix='.txt'):
    """read_paragraphs() on bytes written to a temporary file."""
    f_ = _tmp(data, suffix)
    try:
        return read_paragraphs(f_)
    finally:
        os.unlink(f_)


def _refused(data, suffix='.txt'):
    """True when read_paragraphs() refuses these bytes with a ValueError."""
    try:
        _read_tmp(data, suffix)
        return False
    except ValueError:
        return True


def _raises(exc, fn):
    """True when fn() raises exc."""
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


def self_test():
    skipped = 0  # blocks of .docx tests skipped because python-docx isn't installed
    cases = [
        ('Neither party shall assign this agreement.', 'negative-subject-shall', True),
        ('Tenant shall ensure that no Hazardous Materials are stored at the Premises and shall indemnify Landlord.', 'negative-subject-shall', False),
        ('Payment shall be made no later than 10 days after Closing.', 'passive-hides-actor', True),
        ('The Fee shall be paid by the end of the month.', 'passive-hides-actor', True),
        ('The Units shall be delivered by the Closing Date.', 'passive-hides-actor', True),
        ('Acme shall maintain the Premises,  which Beta owns, in good repair.', 'restrictive-which', False),
        ('Acme shall pay, deliver and install the Units.', 'serial-comma', True),
        ('Acme shall pay, deliver, and install the Units.', 'serial-comma', False),
        ('Acme may, in its sole discretion, accept or reject the Units.', 'serial-comma', False),
        ('Acme may terminate at any time, with or without cause.', 'serial-comma', False),
        ('The Seller\'s employees, agents and contractors shall comply.', 'serial-comma', True),
        ('If Acme defaults, Beta and Gamma may terminate.', 'serial-comma', False),
        ('Prior to the Closing, Seller and Buyer shall sign the Deed.', 'serial-comma', False),  # an opening phrase with a 2-word opener (ACC-005)
        ('Immediately after the Closing, Buyer and Seller shall file the Deed.', 'serial-comma', False),  # an adverb before the opener
        ('Acme shall deliver the Units, Parts and Tools.', 'serial-comma', True),  # the positive control
        ('However, Acme and Beta shall meet.', 'serial-comma', False),
        ('Acme may use the Software, the Documentation and the Updates.', 'serial-comma', True),
        ('The office is in Nashville, Tennessee and Acme shall staff it.', 'serial-comma', False),
        ('This agreement is dated January 5, 2027 and is between Acme and Beta.', 'serial-comma', False),
        ('Acme shall pay the Price. Beta shall deliver the Units.', 'spacing', True),
        ('Acme shall not assign this agreement.', 'negative-subject-shall', False),
        ('If Acme should exercise the Option, Widgetco shall pay.', 'should', True),
        ('1. The Company shall pay.  Acme shall deliver.', 'spacing', False),
        ('Notices go to 1234 Main Ave. Suite 100, Nashville.', 'spacing', False),
        ('II. Termination of Employment', 'spacing', False),
        ('The Shares will be issued at Closing.', 'passive-hides-actor', True),
        ('Any purported transfer will be void.', 'passive-voice', False),
        ('Any Transfer that this agreement does not permit is void.', 'category-will', True),  # MSCD 3.334, table 8 [8-1]: a contingent event stated as a relative clause takes will
        ('Any purported assignment that breaches this section is void.', 'category-will', True),
        ("An assignment made without Lender's consent is of no effect.", 'category-will', True),
        ('Any attempted transfer of Shares in violation of this agreement will be void.', 'category-will', False),
        ('This agreement is void.', 'category-will', False),  # a standing policy keeps the present tense
        ('Acme is liable for the Losses.', 'passive-voice', False),
        ('"Business Day" means a day other than a day on which banks in Houston are authorized or required by law to close.', 'passive-voice', True),
        ('Acme is duly authorized to sign this agreement.', 'passive-voice', False),
        ('Tenant is bound by this agreement.', 'passive-voice', True),
        ('Acme shall pay the Fee each year.  The Contract Year is defined in Schedule A.', 'unit-of-time', True),
        ('Acme shall pay the Fee each Contract Year.', 'unit-of-time', False),
        ('The parties hereby amend Section 2.1 (Term) of the Services Agreement by replacing the date.', 'numbered-cross-reference', False),
        ('The parties amended the Services Agreement once before, on April 14, 2026.', 'once', False),
        ('Tenant may assign this lease only once.', 'once', False),
        ('Once Tenant pays the Deposit, Landlord shall deliver the keys.', 'once', True),
        ('The fees in Schedule A replace the fees in Schedule 2 of the Services Agreement.', 'attachment-scheme', False),
        ('The fees are listed in Schedule 2.', 'attachment-scheme', True),
        ('Buyer shall indemnify Seller to the extent Supplier shall be liable for the Losses.', 'shall-in-condition', True),
        ('So long as Tenant shall not be in default, Tenant may renew this lease.', 'shall-in-condition', True),
        ('If Client does not reject the Deliverable within 10 days, Client is deemed to have accepted it.', 'passive-voice', True),
        ('If Client does not reject the Deliverable within 10 days, Client is deemed to have accepted it.', 'passive-hides-actor', False),
        ('Provider shall indemnify Customer against the damages that a court awards or that Provider agrees to pay in settlement of it.', 'agrees-to', False),
        ('Seller agrees to name Buyer as an additional insured.', 'agrees-to', True),
        ('Seller shall obtain an endorsement under which the insurer agrees to name Buyer as an additional insured.', 'agrees-to', False),
        ("Sandia Crest's volunteers shall wear badges at the Event.", 'nonparty-obligation', True),
        ('Each member of the Key Personnel shall devote 40 hours each week to the Services.', 'nonparty-obligation', True),
        ('Each Authorized User shall comply with the Acceptable Use Policy.', 'nonparty-obligation', True),
        ('The Exercise Price stays the same.', 'same-pronoun', False),
        ('The Conversion Price is the Valuation Cap divided by the Fully Diluted Capitalization.', 'reduced-passive', False),
        ('For 3 years, Seller shall not engage, directly or indirectly, in any Competing Business.', 'serial-comma', False),
        ('Tenant shall make all repairs, structural and nonstructural, to the Premises.', 'serial-comma', False),
        ('Employee hereby assigns each Invention that Employee conceives or creates, alone or with others, during the Term.', 'serial-comma', False),
        ("Each party shall send notices to the address below that party's signature.", 'contract-reference', False),
        ("Company's benefits administrator shall send Executive the COBRA notice.", 'nonparty-obligation', True),
        ("Each party shall send notices to the address below the recipient's signature.", 'contract-reference', False),
        ('Licensee shall comply with the requirements below.', 'contract-reference', True),
        ('Electronic signatures are as effective as a handwritten one.', 'number-word', False),
        ('Each party shall appoint one representative.', 'number-word', True),
        ('Acme shall deliver the report no later than Thirty Calendar Days after the Closing.', 'number-word', True),
        ('Acme shall open Two bank accounts.', 'number-word', True),
        ('Acme states that Widgetco agrees to pay the Fee.', 'agrees-to', True),
        ('The parties wish to evaluate whether Acme will build the modules into its robots.', 'category-will', False),
        ('Seller will deliver the modules.', 'category-will', True),
        ('Company will continue until the Members dissolve it.', 'category-will', False),  # a party plus a policy verb: a contingent event, not a duty
        ("Company's liability is limited, in the aggregate, to the Fees that Customer paid.", 'passive-voice', False),  # a cap with a linking verb
        ('The amount is limited by the terms that Lender imposes.', 'passive-voice', True),
        ('Company shall give Customer a copy of the report after Customer asks for one.', 'number-word', False),  # one as a pronoun
        ('Customer may order one or more Units.', 'number-word', True),
        ('This lease is subordinate to any mortgage that Landlord grants if the mortgagee agrees not to disturb Tenant.', 'category-will', True),
        ('This agreement renews automatically for successive 1-year terms unless either party notifies the other no later than 90 days before the renewal term begins.', 'category-will', True),
        ('If Executive does not revoke this release, this release becomes effective on the 8th day after Executive signs it.', 'category-will', True),
        ('The termination takes effect 90 days after Provider receives the notice.', 'category-will', True),
        ('Risk of loss passes to Buyer when Supplier tenders the Products to the carrier.', 'category-will', True),
        ('No installment of the Severance Amount becomes due before the Release becomes effective.', 'category-will', True),
        ('This agreement terminates on December 31, 2027.', 'category-will', False),
        ('If Customer terminates this agreement, Vendor shall refund the prepaid fees.', 'category-will', False),
        ('This agreement will terminate when Borrower pays the Obligations in full.', 'category-will', False),
        ('Tenant may extend the Term by notifying Landlord no later than 180 days before the Term ends.', 'category-will', False),
        ('Acme shall return the Deposit no later than 10 days after this agreement terminates.', 'category-will', False),
        ('A Business Day is a day on which Fifth Third Bank is closed.', 'passive-voice', False),
        ('Acme operates a third-party logistics business.', 'usage', False),
        ('Each party shall sign below and return 1 signed copy.', 'contract-reference', False),
        ('The parties wish to evaluate whether Seller will build the modules.', 'category-will', False),
        ('Address: One Riverway, Suite 1700, Houston, Texas 77056', 'number-word', False),
        ('One party may terminate this agreement.', 'number-word', True),
        ('Client is not required to pay fees for the Services above the not-to-exceed amount in Schedule A.', 'contract-reference', False),
        ('Acme is bound by operation of law.', 'passive-voice', True),
        ('The notice is effective by email.', 'passive-voice', False),
        ('Acme is liable by reason of its breach.', 'passive-voice', False),
        ('Acme has offices at 500 Third Avenue.', 'ordinal-word', False),
        ('Acme shall pay the third installment.', 'ordinal-word', True),
        ('Acme may sell one or more Units.', 'number-word', True),
        ('No one may enter the Premises.', 'number-word', False),
        ('The parties shall cooperate with one another.', 'number-word', False),
        ('Acme shall pay a one-time fee.', 'number-word', False),
        ('Acme shall deliver one-half of the Shares.', 'number-word', True),
        ('Acme shall pay on the first anniversary of the Closing Date.', 'ordinal-word', True),
        ('Acme has a right of first refusal.', 'ordinal-word', False),
        ('Acme is not required to repair the Equipment.', 'passive-voice', False),
        ('Acme shall pay if Park knows or should have known of the defect.', 'should', True),
        ('Acme shall reimburse any expenses incurred by Park.', 'reduced-passive', True),
        ('Acme shall pay the amounts that Park invoices.', 'reduced-passive', False),
        ('Buyer shall pay the Purchase Price in the manner stated in the section titled "Payment."', 'reduced-passive', False),  # the house form of a reference by heading (probe)
        ('Buyer shall pay the Purchase Price in the manner stated in the Payment Schedule.', 'reduced-passive', True),
        ('This waiver applies only to the sale described in the section titled "Consent".', 'reduced-passive', True),  # a thing the participle modifies: recast (corpus6 c147)
        ('The Receiving Party shall not disclose the information.', 'party-article', False),
        ('The Company shall pay Employee.', 'party-article', True),
        ("ACME WIDGETS, INC., a Tennessee corporation (the \u201cCompany\u201d)", 'party-article', True),
        ('Company shall reimburse the Company Plan administrator.', 'party-article', False),
        ('Company shall give the employee handbook to the other party.', 'party-article', False),
        ('Each party shall bear the Company employee costs.', 'party-article', False),
        ('the prices listed in Attachment 1', 'generic-attachment-label', True),
        ('the prices listed in Schedule A', 'generic-attachment-label', False),
        ('Supplier shall execute the services.', 'term-of-art', True),
        ('Acme shall sign and deliver the Notes.', 'term-of-art', False),
        ('If Supplier notices an error, it shall notify Acme.', 'term-of-art', True),
        ('All notices that Acme gives under this agreement must be in writing.', 'term-of-art', False),
        ('Supplier shall assign qualified personnel to each work assignment.', 'term-of-art', True),
        ('Acme may not assign this agreement.', 'term-of-art', False),
        ('The Shares will be issued at Closing.', 'passive-hides-actor', True),
        ('This consulting agreement is dated January 1, 2027.', 'passive-voice', False),
        ('the day on which this agreement ends', 'restrictive-which', False),
        ('any claim which arises under this agreement', 'restrictive-which', True),
        ('The notice must specify which option Tenant elects.', 'restrictive-which', False),  # an embedded question (ACC-006)
        ('Buyer shall notify Seller which Units it rejects.', 'restrictive-which', False),
        ('Acme shall pay within five (5) days.', 'words-and-digits', True),
        ('Acme shall pay within three days.', 'number-word', True),
        ('Acme shall pay within 3 days.', 'number-word', False),
        ('See Section 4.2(a) for details.', 'numbered-cross-reference', True),
        ('Acme shall pay the fee under § 5.2.', 'numbered-cross-reference', True),
        ('Seller shall comply with Tenn. Code Ann. § 47-18-104 in marketing the Products.', 'numbered-cross-reference', False),
        ('Harlow waives the protection of § 1542 of the California Civil Code.', 'numbered-cross-reference', False),
        ('The Assets listed on Schedule A are excluded.', 'attachment-on', True),
        ('The form attached hereto as Exhibit 2 governs.', 'attachment-hereto', True),
        ('The list in schedule A governs.', 'attachment-capitals', True),
        ('This agreement is dated 1 January 2027.', 'day-month-year', True),
        ('Acme shall pay. Widgetco shall deliver.', 'spacing', True),
        ('Acme shall pay.  Widgetco shall deliver.', 'spacing', False),
        ('Acme Inc. shall pay.', 'spacing', False),
        ('ACME WIDGETS, INC. (the "Seller") shall pay.', 'spacing', False),
        ('This Agreement shall be for a term of 2 years.', 'category-shall', True),
        ('Once Acme pays, the lien terminates.', 'once', True),
        ('Smith & Jones LLP shall act as escrow agent.', 'ampersand', False),
        ('Amendment & Waiver', 'ampersand', True),
        ('Section 3.01 Use.  Lessee shall use the Equipment only at the Site.', 'numbered-cross-reference', False),
        ('Acme shall not disclose it to a third party.', 'ordinal-word', False),
        ('Acme shall not disclose it to a third party.', 'usage', True),
        ('Acme signed this note on the 15th day of January, 2027.', 'this-day', True),
        ('Each party shall pay the costs imposed on it by law.', 'reduced-passive', True),
        ('The parties agreed to the price.', 'reduced-passive', False),
        ('Acme shall deliver the Units ordered by Widgetco.', 'reduced-passive', True),
        ('(a) Neither party shall assign this agreement.', 'negative-subject-shall', True),
        ('3.2 No party shall make any statement that disparages another party.', 'negative-subject-shall', True),
        ('Acme shall pay, and no delay by Widgetco in exercising any right under this guaranty shall operate as a waiver.', 'negative-subject-shall', True),
        ('The Receiving Party may disclose it to its lenders and/or advisers.', 'and-or', True),
        ('Acme shall use best efforts to obtain the Consent.', 'efforts', True),
        ('Acme shall pay the Fee within 30 days of the Closing.', 'time-ambiguity', True),
        ('If Tenant does not cure the default by that deadline, Landlord may terminate this lease.', 'time-ambiguity', True),
        ('Tenant shall deliver the documents by the Outside Date.', 'time-ambiguity', True),
        ('Buyer shall pay the Price by wire transfer.', 'time-ambiguity', False),
        ('This lease is dated by the date of this agreement.', 'time-ambiguity', False),
        ('Acme shall pay the Fee no later than 30 days after the Closing.', 'time-ambiguity', False),
        ('The Term runs from January 1, 2027 to March 31, 2027.', 'time-ambiguity', True),
        ('This agreement shall be governed by Tennessee law.', 'category-shall', True),
        ('It is understood and agreed that Acme is an independent contractor.', 'throat-clearing', True),
        ('Acme hereby grants Widgetco a license.', 'archaic', False),
        ('The parties hereto agree as follows.', 'archaic', True),
        ('The headings in this agreement are for convenience only.', 'headings-clause', True),
        ('Buyer may assign this agreement, provided that Seller consents.', 'provided-that', True),
        ('Seller has provided that information to Buyer.', 'provided-that', False),  # the verb after an auxiliary (ACC-009)
        ('Acme shall pay the Price no later than 30 days after the Closing Date, and Widgetco shall deliver the Units.', 'negative-subject-shall', False),
        ('If no Default exists, Acme shall pay the Price.', 'negative-subject-shall', False),
        ('Acme shall pay, and no Shareholder shall transfer any Shares.', 'negative-subject-shall', True),
        ('The parties agree that no party shall assign this agreement.', 'negative-subject-shall', True),
        ('Payments under Section 409A of the Internal Revenue Code are exempt.', 'numbered-cross-reference', False),
        ('as stated in Section 4.2', 'numbered-cross-reference', True),
        ('Acme shall obtain each such consent, a "Required Consent," before the Closing.', 'such-pointing', False),
        ('Acme shall obtain such consent before the Closing.', 'such-pointing', True),
        ('Provider shall maintain umbrella insurance, and such insurance must name Customer as an additional insured.', 'such-pointing', True),
        ('Buyer shall insure the Equipment until the Closing and shall name Seller as loss payee.', 'shall-in-condition', False),
        ('Until the Closing shall occur, Seller shall operate the Business.', 'shall-in-condition', True),
        ('Seller is not liable for any day on which the bank is closed to the public.', 'passive-voice', False),
        ('Licensee may audit the records once in each Contract Year.', 'once', False),
        ('Once Licensee pays the Fee, the license is perpetual.', 'once', True),
        ('Distributor may not sell the Products at a price below Company\'s published price list.', 'contract-reference', False),
        ('Licensee shall pay 5% of Net Sales above $2,000,000.', 'contract-reference', False),
        ('Company shall pay Consultant 2% of the Net Revenue for each Contract Year.', 'percentage-amount-equal-to', True),  # a bare percentage as the amount (MSCD 14.24)
        ('Company shall pay Consultant a fee equal to 2% of the Net Revenue.', 'percentage-amount-equal-to', False),
        ('Company shall pay an amount equal to 2% of the Net Revenue.', 'percentage-amount-equal-to', False),
        ('Licensee shall comply with the requirements stated below.', 'contract-reference', True),
        ('Notice is effective at 5:00 p.m. Central time.', 'spacing', False),
        ('the form attached as Exhibit A', 'attachment-scheme', True),
        ('the prices in Schedule 1', 'attachment-scheme', True),
        ('the prices in Schedule A and the form in Exhibit 1', 'attachment-scheme', False),
        ('Acme shall pay within 30 days of the Closing.', 'time-ambiguity', True),
        ('Acme shall pay within 30 days after the Closing.', 'time-ambiguity', False),
        ('Acme shall pay within ten (10) days after the Closing.', 'within-after', True),
        ('This Distribution Agreement (this "Agreement") is dated', 'this-agreement-term', True),
        ('Landlord and Tenant are parties to a lease (the "Lease") for Suite 210.', 'this-agreement-term', False),
        ('THIS CONSULTING AGREEMENT (the "Agreement") is made', 'this-agreement-term', True),
        ('Acme shall use good-faith efforts to obtain the consent.', 'efforts', True),
        ('Acme shall use reasonable efforts to obtain the consent.', 'efforts', False),
        ('The payment is due on 2/3/2027.', 'numeric-date', True),
        ('Supplier shall staff the help desk 24/7/365.', 'numeric-date', False),  # a service level, not a date (ACC-001)
        ('The Term begins on 1/15/2027.', 'numeric-date', True),
        ('Acme shall continue providing the Services during the dispute.', 'category-shall', False),
        ('Acme shall terminate the subcontract if Widgetco fails to pay.', 'category-shall', False),
        ('Acme shall commence the Work on May 1, 2027.', 'category-shall', False),
        ('This agreement shall terminate on December 31, 2027.', 'category-shall', True),
        ('The term shall continue for 2 years.', 'category-shall', True),
        ('Interest shall accrue on the unpaid principal balance.', 'category-shall', True),
        # subject analysis: a thing can't have a duty; a nonparty isn't bound; party subjects with shall be liable and the like
        ('The laws of the State of Tennessee shall govern all disputes arising out of this agreement.', 'category-shall', True),
        ('If a Purchase Order conflicts with this agreement, this agreement shall control.', 'category-shall', True),
        ('Title to each Unit shall pass to Buyer on delivery.', 'category-shall', True),
        ('There shall be no adjustment to the Purchase Price after the Closing.', 'category-shall', True),
        ('Supplier shall not be liable for any delay that a Force Majeure Event causes.', 'category-shall', True),
        ('Customer shall have the right, but not the obligation, to inspect the Facility.', 'category-shall', True),
        ('Seller, at its own cost, shall repair the Unit.', 'category-shall', False),
        ('Section 3.1(a) Company shall pay the Fee at the Closing.', 'category-shall', False),  # a typed section label is not the subject (probe)
        ('Section 3 Company shall pay the Fee.', 'category-shall', False),
        ('3.1(a) Company shall pay the Fee.', 'category-shall', False),
        ('(a)(i) Company shall pay the Fee.', 'category-shall', False),
        ('A party giving notice under this agreement shall send it by certified mail.', 'category-shall', False),
        ('Each party shall give each notice in writing and shall deliver it by hand.', 'category-shall', False),
        ('The Fee shall be paid by Customer.', 'category-shall', False),
        ('The Title Company shall record the Deed at the Closing.', 'nonparty-obligation', True),
        ("Tenant's invitees shall not smoke anywhere in the Building.", 'nonparty-obligation', True),
        ('The Escrow Agent must release the Escrow Amount.', 'nonparty-obligation', False),
        ('Buyer and its Affiliates shall keep the Terms confidential.', 'nonparty-obligation', False),
        ('Consultant shall cause each of its employees to sign a confidentiality agreement.', 'nonparty-obligation', True),
        ('5 directors constitute a quorum of the Board.', 'number-word', True),
        ('A quorum of the Board is 5 directors.', 'number-word', False),
        ('Parent shall cause Sub to sell the Widget Assets.', 'nonparty-obligation', False),
        ('The Installer shall not assert the same in any later proceeding.', 'same-pronoun', True),
        ('Acme shall pay the same fee as Widgetco.', 'same-pronoun', False),
        ('The Kiosk is at Twelve Oaks Mall in Novi.', 'number-word', False),
        ('Thirty days after the Closing, Acme shall pay.', 'number-word', True),
        ('The Price is Four Hundred Eighty-Two Thousand Five Hundred Dollars ($428,500).', 'words-digits-conflict', True),
        ('The Price is Ten Thousand Dollars ($10,000).', 'words-digits-conflict', False),
        ('Interest accrues at one-half of one percent (0.5%) per month.', 'words-digits-conflict', False),
        ('The fee is one-quarter of one percent (0.25%) of the Loan.', 'words-digits-conflict', False),
        ('Buyer shall pay Three Hundred Seventy-Five Thousand Dollars ($375,000).', 'words-digits-conflict', False),
        ('Buyer shall pay Four Hundred Twenty-Eight Thousand Five Hundred Dollars ($428,500).', 'words-digits-conflict', False),
        ('Buyer shall pay one installment of Five Thousand Dollars ($5,000).', 'words-digits-conflict', False),
        ('Buyer shall pay One Hundred Dollars and Fifty Cents ($100.50).', 'words-digits-conflict', False),
        ('Buyer shall pay Five Thousand and No/100 Dollars ($5,000.00).', 'words-digits-conflict', False),
        ('Buyer shall pay One Million Five Hundred Thousand Dollars ($1,500,000).', 'words-digits-conflict', False),
        ('Buyer shall pay Two Million Dollars ($1,500,000).', 'words-digits-conflict', True),
        ('Interest accrues at ten percent (12%) per year.', 'words-digits-conflict', True),
        ('Interest accrues at one and one-half percent (1.5%) per month.', 'words-and-digits', True),
        ('Section 3 (Payment) applies.', 'words-and-digits', False),
        ('Interest accrues at one and one-half percent (1.5%) per month.', 'words-digits-conflict', False),
        ('Lender shall lend Borrower $850,000.00 at the Closing.', 'money-cents', True),
        ("Consultant's employees shall comply with the site rules.", 'nonparty-obligation', True),
        ('Neither Buyer nor its agents shall disassemble the Equipment.', 'nonparty-obligation', False),
        ('The prices are in the price list attached hereto as Exhibit A.', 'attachment-scheme', True),
        ('The Indemnifying Party shall defend each Third-Party Claim.', 'usage', True),
        ('unless he or she is responding to an advertisement', 'singular-they', True),
        ('Licensee shall deliver a royalty report in the form of Schedule B.', 'attachment-classification', True),
        ('The interest rate on the Loan shall be 6.25% per year.', 'category-shall', True),
        ('Agency shall invoice Client by the 5th day of each month.', 'time-ambiguity', True),
        ('Consultant shall execute a hydrology study of the Site.', 'term-of-art', True),
        ('Consultant shall execute a copy of this agreement.', 'term-of-art', False),
        ('Licensee shall pay 6% of Net Sales of Licensed Products sold by Licensee.', 'reduced-passive', True),
        ('The parties agreed by email to extend the date.', 'reduced-passive', False),
        ('The Client shall reimburse travel expenses incurred by the Consultant.', 'reduced-passive', True),
        # red-team round: a contingent policy with a generic or possessive subject, and new leads
        ("Beta's right to use the Software lapses if Beta misses a payment of the Fees.", 'category-will', True),
        ('A Statement of Work becomes binding on both parties when Beta countersigns it.', 'category-will', True),
        ("Acme's warranty in this section is void if Beta modifies the Software without Acme's written approval.", 'category-will', True),
        ('In case Beta becomes insolvent, title to the Equipment reverts to Acme.', 'category-will', True),
        ('Should Beta become insolvent, the license terminates.', 'category-will', True),
        ('The Fees increase by 3% on January 1, 2028.', 'category-will', False),
        ('The Supplier applies the discount when Customer pays early.', 'category-will', False),
        ('Acme shall pay the amount that becomes due after the Closing.', 'category-will', False),
        ('Acme shall notify Beta of any fee increases before they take effect.', 'category-will', False),
        ('The Deposit is due on signing, and if Beta fails to pay it, Acme may terminate this agreement.', 'category-will', False),
        ('Acme may increase the Fees once in each period of 12 consecutive months, but no increase may exceed 4%.', 'category-will', False),
        ('A notice is effective when the recipient receives it.', 'category-will', True),  # MSCD's form: "will be effective if ... received" (3.334; 13.209)
        ('No notice of default is effective against a Leasehold Mortgagee until the Leasehold Mortgagee receives that copy.', 'category-will', True),
        ('A notice will be effective when the recipient receives it.', 'category-will', False),
        ('Tennessee law governs this agreement.', 'category-will', False),
        # shall cause in disguise, and nouns the party doesn't control
        ('Beta shall ensure that its carriers maintain cargo insurance of at least $1,000,000 for each shipment.', 'nonparty-obligation', True),
        ('Beta shall see to it that each driver completes the safety course before operating the Equipment.', 'nonparty-obligation', True),
        ('Operator shall make sure that all passengers wear seat belts.', 'nonparty-obligation', True),
        ('Parent shall cause each of its Subsidiaries to sign a joinder.', 'nonparty-obligation', False),
        ('Consultant shall cause the landlord of the Premises to sign an estoppel certificate.', 'nonparty-obligation', True),  # a counterparty the party doesn't control (probe)
        ('Borrower shall cause the bank to release the lien.', 'nonparty-obligation', True),
        ('Parent shall cause its Affiliates to comply.', 'nonparty-obligation', False),  # an instrumentality stays as it is
        ('Beta shall see to it that the Equipment stays insured.', 'nonparty-obligation', False),
        # a negative subject with 1 comma-set clause inside it
        ('No change order, unless Acme signs it, shall bind Acme.', 'negative-subject-shall', True),
        ('No Shareholder, if it is an Affiliate of Buyer, shall transfer any Shares.', 'negative-subject-shall', True),
        ('No Default exists, and Acme shall pay the Price.', 'negative-subject-shall', False),
        ('No later than 10 days after Closing, Acme shall pay the Price.', 'negative-subject-shall', False),
        # the doublet split by its addressee
        ('Beta represents to Acme and warrants that the Equipment is free of liens.', 'represents-warrants', True),
        ('Seller warrants to Buyer and represents that the Shares are fully paid.', 'represents-warrants', True),
        ('Beta states to Acme that the Equipment is free of liens.', 'represents-warrants', False),
        ('Counsel represents Acme in the arbitration and warrants nothing.', 'represents-warrants', False),
        # prompt as an adjective
        ('Beta shall give Acme prompt written notice of any defect in the Equipment.', 'vagueness', True),
        ('Acme shall respond promptly to each support request.', 'vagueness', True),
        ('Acme shall respond to each support request no later than 2 Business Days after receiving it.', 'vagueness', False),
        ('The Software prompts the user for a password.', 'vagueness', False),
        # round 8 (hardening): correlative such ... as; within a period of; -ed words that are never participles; deemed and
        # role-label reduced passives (the code's own checks, formerly duplicated as variants)
        ('Acme shall pay such additional amounts as Schedule A states.', 'such-pointing', False),
        ('Acme shall obtain such consent before the Closing.', 'such-pointing', True),
        ('Provider shall maintain umbrella insurance, and such insurance must name Customer as an additional insured.', 'such-pointing', True),
        ('Acme shall pay within a period of 30 days after the Closing.', 'within-after', True),
        ('Acme shall pay within a period of 30 days.', 'time-ambiguity', True),
        ('The Units are red by design, and the price is indeed fixed.', 'passive-voice', False),
        ('The Units are painted by Acme.', 'passive-voice', True),
        ('Any notice is deemed received 3 Business Days after the sender mails it.', 'passive-voice', True),
        ('This agreement treats a notice as received 3 Business Days after the sender mails it.', 'passive-voice', False),
        ('The Receiving Party shall return all Confidential Information disclosed by the Disclosing Party.', 'reduced-passive', True),
        ('The Receiving Party shall return all Confidential Information that the Disclosing Party has disclosed to it.', 'reduced-passive', False),
        # red team, round 8 (probe2.txt, with the party names of PARTY_DEFAULT): each planted line, and its clean look-alike
        ('Supplier, at its own expense, will maintain the structural elements of the Building.', 'category-will', True),
        ('If Supplier receives a subpoena for Confidential Information, it will notify Customer before responding.', 'category-will', True),
        ('If Supplier receives a subpoena, it will be required to notify Customer.', 'category-will', False),
        ('If Supplier defaults, it will terminate.', 'category-will', False),
        ('Supplier shall appoint a Data Protection Officer, and it may not change that appointment without notifying Customer.', 'may-not', True),
        ('Supplier shall appoint a Data Protection Officer, and it may not be an employee of Customer.', 'may-not', False),
        ('Supplier, at its own cost, must insure the Units.', 'category-must', True),
        ('Supplier shall procure that its employees and agents comply with the Site Rules at all times.', 'nonparty-obligation', True),
        ('Supplier shall procure the materials that its employees need.', 'nonparty-obligation', False),
        ('Neither party, during the Term or for 12 months after it ends, shall solicit any employee of the other party.', 'negative-subject-shall', True),
        ('Neither party is in default, and Supplier shall pay the Fee.', 'negative-subject-shall', False),
        ("Each defective component shall be (at Customer's election) repaired or replaced at no cost to Supplier.", 'passive-hides-actor', True),
        ('The Units shall be either delivered by Supplier or collected by Customer.', 'passive-voice', True),
        ('Supplier shall be either the operator or the owner of the Site.', 'passive-voice', False),
        ('Supplier shall pay each invoice no later than 30 (thirty-five) days after receiving it.', 'words-digits-conflict', True),
        ('Supplier shall pay each invoice no later than 30 (thirty) days after receiving it.', 'words-digits-conflict', False),
        ('Supplier shall pay each invoice no later than 30 (thirty) days after receiving it.', 'words-and-digits', True),
        ('Supplier shall pay the Security Deposit by the Rent Commencement Date.', 'time-ambiguity', True),
        ('Supplier shall pay the Security Deposit by the Rent Commencement Date of this lease.', 'time-ambiguity', False),
        ('The Initial Term begins on 2027/01/05.', 'numeric-date', True),
        ('The ratio under this section is 2027/15.', 'numeric-date', False),
        ('Supplier shall begin execution of the Work no later than 10 days after receiving the Notice to Proceed.', 'term-of-art', True),
        ('Supplier shall begin execution of the Work no later than 10 days after receiving the Notice to Proceed.', 'archaic', False),
        ('The execution of the Deed takes place at the Closing.', 'term-of-art', False),
        ('The right of first refusal in this section ends if Supplier assigns this agreement.', 'category-will', True),
        ('Supplier shall renew the policy no later than 180 days before the Term ends.', 'category-will', False),
        ('Final Completion shall occur no later than July 31, 2027.', 'category-shall', True),
        ('Supplier shall complete the Work no later than July 31, 2027.', 'category-shall', False),
        ('Supplier shall be at liberty to appoint a replacement Project Manager at any time.', 'category-shall', True),
        ('Supplier is free to appoint a replacement Project Manager at any time.', 'category-may', True),
        ('Supplier has the right, but not the obligation, to audit the records.', 'category-may', True),
        ('Seller states that it has the right to sell the Assets.', 'category-may', False),
        ('Supplier is entitled, on request, to a copy of the records.', 'is-entitled-to', True),
        ('Consultant is entitled to receive the Fee at the Closing.', 'is-entitled-to', True),
        ('Consultant is entitled to reimbursement from Company for all expenses.', 'is-entitled-to', True),
        ('Supplier shall pay the Base Rent, the Additional Rent and all other sums due under this lease.', 'serial-comma', True),
        ('In its sole discretion, the Lender and the Borrower may extend the date.', 'serial-comma', False),
        ('Supplier shall indemnify and hold each of the Customer Indemnitees harmless from all Losses.', 'doublet', True),
        ('Supplier shall hold the Deposit in a segregated account.', 'doublet', False),
        ('EACH PARTY REPRESENTS AND WARRANTS THAT IT HAS FULL POWER TO ENTER INTO THIS AGREEMENT.', 'represents-warrants', True),
        ('EACH PARTY STATES THAT IT HAS FULL POWER TO ENTER INTO THIS AGREEMENT.', 'represents-warrants', False),
        ('COMPANY SHALL PAY THE FEE NO LATER THAN 30 DAYS AFTER RECEIVING AN INVOICE.', 'capitals-body', True),  # body text in capitals (house rule 9; MSCD 16.18)
        ('Company shall pay the Fee no later than 30 days after receiving an invoice.', 'capitals-body', False),
        ('ARTICLE I DEFINITIONS AND RULES OF INTERPRETATION OF THIS AGREEMENT', 'capitals-body', False),  # an article heading
        ('MASTER SERVICES AGREEMENT', 'capitals-body', False),  # a title: under 8 words
        ('Supplier shall pay the Rent stated in Schedule A to this lease.', 'attachment-hereto', True),
        ('Supplier shall pay the Rent stated in Schedule A.', 'attachment-hereto', False),
        ('Each Key Person shall conduct himself or herself in accordance with the Code of Conduct.', 'singular-they', True),
        ('Each Key Person shall devote their full working time to the Project.', 'singular-they', False),
        ('Supplier shall use reasonable commercial endeavours to obtain the Planning Permission.', 'efforts', True),
        ('Customer may reject any Units which are the subject of a recall notice.', 'restrictive-which', True),
        # the dodges the red team listed but did not plant
        ('Supplier shall remain liable for the Fees after the assignment.', 'category-shall', True),
        ('Supplier shall be solely liable for all taxes on the Fees.', 'category-shall', True),
        ('Supplier is liable for the Fees.', 'category-shall', False),
        ('The fees are set out at Schedule B.', 'attachment-on', True),
        ('The fees are stated in Schedule B.', 'attachment-on', False),
        ('Schedule A forms part of this lease.', 'attachment-part-of', True),
        ('The loading dock forms part of the Premises.', 'attachment-part-of', False),
        ('The clause headings are for guidance only and do not affect interpretation.', 'headings-clause', True),
        ('Supplier shall follow the guidance in the headings of the Manual.', 'headings-clause', False),
        ('The records that Supplier keeps are true, correct, and complete.', 'doublet', True),
        ('The records that Supplier keeps are complete.', 'doublet', False),
        ('This agreement binds the successors and assignees of each party.', 'usage', True),
        ('This agreement binds the successors and assigns of each party.', 'usage', False),
        ('Supplier shall keep the premises wherein the Equipment sits in good repair.', 'archaic', True),
        ('Supplier shall deliver the Units to the Site, where Customer will inspect them.', 'archaic', False),
        ('Supplier shall not disclose the Data to a 3rd-party vendor.', 'usage', True),
        ('Supplier shall deliver the 3rd Unit no later than March 1, 2027.', 'usage', False),
    ]
    sev_cases = [  # severity policy: house severity for house rules, else the rule record's
        ('Acme shall pay the Price. If Acme shall fail to pay, Widgetco may terminate.', 'shall-in-condition', 3),
        ('Acme shall deliver the Widgets, the Gadgets, and/or the Gizmos.', 'and-or', 1),
        ('Acme shall purchase Widget A and/or Widget B.', 'and-or', 2),
        ('Acme shall use its best efforts to sell the Units.', 'efforts', 1),
        ('The Units will be delivered to Widgetco.', 'passive-hides-actor', 1),
        ('The Units were delivered by Acme.', 'passive-voice', 2),
        ('Acme shall pay within ten (10) days after the Closing.', 'within-after', 3),
        ('The form attached hereto as Exhibit 2 governs.', 'attachment-hereto', 3),
        ('The payment is due on 2/3/2027.', 'numeric-date', 1),
        ('If Acme should exercise the Option, Widgetco shall pay.', 'should', 2),
        ('Acme should deliver the Units by noon.', 'should', 1),
        ('The Company shall pay Widgetco.', 'party-article', 2),
        ('The parties amend Section 4 under the Master Agreement.', 'numbered-cross-reference', 3),  # another agreement's number: the site's own severity (S13)
        ('This agreement shall be governed by Tennessee law.', 'category-shall', 3),  # a policy fork: the rule record's severity
        ('Company shall pay Consultant 2% of the Net Revenue.', 'percentage-amount-equal-to', 3),
        ('COMPANY SHALL PAY THE FEE NO LATER THAN 30 DAYS AFTER RECEIVING AN INVOICE.', 'capitals-body', 3),
    ]
    checks = []  # every self-test case: (name, passed); the printed count is len(checks), so it can't drift
    for text, check, expect in cases:
        got = any(f['check'] == check for f in house_checks({'idx': 0, 'text': text, 'fmt': {}}))
        checks.append((f'{check} {"flagged" if expect else "clear"}: {text[:90]}', got == expect))
    sev_cases.append(('The Option expires on September 1, 2027.', 'time-of-day', 2))  # the entry's own severity (own_severity) governs
    for text, check, want in sev_cases:
        fs = [f for f in house_checks({'idx': 0, 'text': text, 'fmt': {}}) if f['check'] == check]
        checks.append((f'severity: {check} {want} (got {[f["severity"] for f in fs]}) for: {text[:80]}', bool(fs) and int(fs[0]['severity']) == want))
    # Whole-pipeline cases: run() on a temporary file, so the rule channel and the house overrides are exercised too.
    doc_cases = [
        ('This consulting agreement is dated January 1, 2027, and is between ACME, INC. ("Acme") and DANA PARK ("Park").', 'R-3.15-passive-hides-actor', False),
        ('Acme shall deliver the Units listed in Schedule A to Park.', 'R-5.78-no-emphasis-attachment-refs', False),
        ('Acme shall deliver the Units listed in Schedule A to Park.', 'R-17.29-initial-capitals', False),
        ('The Units will be delivered to Park.', 'R-3.15-passive-hides-actor', True),
    ]
    for text, rid, expect in doc_cases:
        got = any(rid in f.get('rule_ids', []) for f in lint_text(text + '\n')[2])
        checks.append((f'run: {rid} {"fires" if expect else "clear"} for: {text[:80]}', got == expect))
    # Document-level checks: section headings, mixed efforts standards, party names, bold definitions in Markdown.
    whole = [
        ('.txt', 'This agreement is dated January 1, 2027, and is between Acme Widgets, Inc. ("Acme") and Widgetco LLC ("Widgetco").\n\n'
                 '1.1 Acme shall sell the Units to Widgetco.\n\n1.2 Widgetco shall pay the Price.\n\n1.3 Payment.  Widgetco shall pay by wire.\n\n'
                 'Acme shall use reasonable efforts.  Widgetco shall use commercially reasonable efforts.\n',
         {'section-headings': True, 'efforts-mixed': True, 'front': True}),
        ('.txt', 'I. DEFINITIONS\n\nA. "Units" means the widgets.\n\nB. "Price" means $5.\n\nII. SALE\n\nA. Sale.  Acme shall sell the Units.\n\nB. Payment.  Widgetco shall pay the Price.\n',
         {'section-headings': False, 'efforts-mixed': False}),
        ('.md', 'This agreement is between ACME, INC. ("**Acme**") and WIDGETCO LLC ("Widgetco").\n', {'bold-definition': True}),
        ('.md', 'This agreement is between ACME, INC. ("**Acme**") and WIDGETCO LLC ("**Widgetco**").\n', {'bold-definition': False}),
        ('.txt', 'These terms govern each order that Acme Widgets, Inc., a Texas corporation ("Buyer"), issues to a supplier ("Seller").\n\nA. Assignment.  Seller may not assign an order.\n', {'may-not': True}),
        ('.txt', 'This agreement is between ACME, INC. ("Acme") and WIDGETCO LLC ("Widgetco").\n\nA. Definitions.\n\n1. "Approved Budget" means the budget in Schedule A, which Widgetco shall approve in writing.\n\n2. "Units" means the widgets.\n\nB. Budget.  Acme shall not exceed the approved budget.\n',
         {'obligation-in-definition': True, 'defined-term-lowercase': True}),
    ]
    for ext, body, wants in whole:
        fs = lint_text(body, ext, inventory=True)[2]
        for check, want in wants.items():
            got = any(f['check'] == check and (check != 'front' or 'capitals (' in f['message']) for f in fs)
            checks.append((f'document: {check} {"found" if want else "clear"} for: {body[:60]}', got == want))
    # House rule 3 uses every letter: section I. after H. is a section, not an article.
    # Section I. has no heading on purpose: the heading check sees it only if the outline reads it as a section.
    secs9 = ''.join(f'{c}. {h}.  Acme shall do task {n}.\n\n' for n, (c, h) in enumerate(zip('ABCDEFGH', ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel']), 1)) + 'I. Acme shall do task 9.\n\n'
    fs9 = lint_text('I. FIRST ARTICLE\n\n' + secs9 + 'II. SECOND ARTICLE\n\nA. Kilo.  Acme shall pay.\n\nB. Lima.  Acme shall sign.\n')[2]
    heads9 = [f for f in fs9 if f['check'] == 'section-headings']
    checks.append(('outline: section I. after H. is a section (11 sections, 1 without a heading)',
                   not any(f['check'] == 'enumeration' for f in fs9) and bool(heads9) and heads9[0]['message'].startswith('1 of 11 sections')))
    # Word automatic numbering and footers are read (.docx).
    try:
        import docx as _docx2
        dn = _docx2.Document()
        dn.add_paragraph('SUPPLY AGREEMENT')
        for t_ in ('Supplier shall deliver the Goods.', 'Buyer shall pay the Price.'):
            dn.add_paragraph(t_, style='List Number')
        dn.sections[0].footer.paragraphs[0].text = 'Draft of 11/9/2026'
        tmp = _tmp(b'', '.docx')
        dn.save(tmp)
        try:
            pn = read_paragraphs(tmp)[0]
            fsn = run(tmp, False)[2]
        finally:
            os.unlink(tmp)
        checks.append(('docx: Word numbering labels are read', [x.get('auto_label') for x in pn if x.get('auto_label')] == ['1.', '2.']))
        checks.append(('docx: the numeric date in the footer is read', any(f['check'] == 'numeric-date' for f in fsn)))
    except ImportError:
        skipped += 1
    # Readers: Windows-1252 text, an invalid .docx, and the plain .docx reader matching python-docx
    checks.append(('reader: Windows-1252 quotation marks survive', '“' in _read_tmp('Acme shall pay “the Price”.'.encode('cp1252'))[0][0]['text']))
    checks.append(('reader: an invalid .docx is refused', _refused(b'not a zip', '.docx')))
    try:
        import docx as _docx3
        from docx.oxml import OxmlElement as _OE
        dt = _docx3.Document()
        dt.add_paragraph('AGREEMENT')
        host = dt.add_paragraph('Box: ')
        from lxml import etree as _et
        pict = _OE('w:pict')
        pict.append(_et.fromstring('<v:shape xmlns:v="urn:schemas-microsoft-com:vml"><v:textbox><w:txbxContent xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:r><w:t>Acme shall pay.</w:t></w:r></w:p></w:txbxContent></v:textbox></v:shape>'))
        rr = _OE('w:r')
        rr.append(pict)
        host._p.append(rr)
        dt.add_table(rows=1, cols=1).cell(0, 0).paragraphs[0].text = 'Price: $5.'
        tmp = _tmp(b'', '.docx')
        dt.save(tmp)
        try:
            a = [(x['where'], x['text']) for x in read_paragraphs(tmp)[0]]
            b = [(x['where'], x['text']) for x in _read_docx_stdlib(tmp)[0]]
        finally:
            os.unlink(tmp)
        checks.append(('reader: a text box is read once, as its own paragraph', [t for w, t in a].count('Acme shall pay.') == 1 and ('textbox', 'Acme shall pay.') in a))
        checks.append(('reader: the plain reader agrees with python-docx', a == b))
    except ImportError:
        skipped += 1
    # A definition after a typed enumerator still enters the inventory.
    rows = lint_text('A. "Confidential Information" means any technical information.\n\nB. Acme shall protect the Confidential Information.\n', inventory=True)[4]
    checks.append(('run: a definition after "A." enters the inventory', any(r['term'] == 'Confidential Information' for r in rows)))
    # Paragraphs inside a content control or a revision wrapper are read.
    try:
        import docx as _docx
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn as _qn
        dd = _docx.Document()
        dd.add_paragraph('Acme shall pay the Price.')
        p2 = dd.add_paragraph('Widgetco shall deliver the Units.')
        sdt, content = OxmlElement('w:sdt'), OxmlElement('w:sdtContent')
        sdt.append(content)
        p2._p.addprevious(sdt)
        content.append(p2._p)
        p3 = dd.add_paragraph('Lee shall sign the Note.')
        ins = OxmlElement('w:ins')
        ins.set(_qn('w:id'), '9')
        ins.set(_qn('w:author'), 'X')
        ins.set(_qn('w:date'), '2026-01-01T00:00:00Z')
        p3._p.addprevious(ins)
        ins.append(p3._p)
        tmp = _tmp(b'', '.docx')
        dd.save(tmp)
        texts = [p['text'] for p in read_paragraphs(tmp)[0]]
        os.unlink(tmp)
        checks.append(('docx: paragraphs inside a content control or a revision wrapper are read in order', texts == ['Acme shall pay the Price.', 'Widgetco shall deliver the Units.', 'Lee shall sign the Note.']))
    except ImportError:
        skipped += 1
    # Round-4 readers and inventory: UTF-16, single newlines, role labels, a typed number before a term, a lead phrase
    checks.append(('UTF-16 text read', [p['text'] for p in _read_tmp('Acme shall pay “the Price”.\n\nBeta shall deliver.'.encode('utf-16'))[0]] == ['Acme shall pay “the Price”.', 'Beta shall deliver.']))
    mix_p, mix_m = _read_tmp('Acme shall pay “the Price” — now.\n\n'.encode('utf-8') + b'Beta\x92s duty.\n')
    checks.append(('UTF-8 with a stray Windows-1252 byte keeps the UTF-8 around it', [p['text'] for p in mix_p] == ['Acme shall pay “the Price” — now.', 'Beta’s duty.']
               and mix_m.get('encoding', '').startswith('UTF-8 with 1 ')))
    checks.append(('Windows-1252 throughout', [p['text'] for p in _read_tmp(b'Acme\x92s \x93Price\x94.\n')[0]] == ['Acme’s “Price”.']))
    checks.append(('UTF-32 with a byte-order mark', [p['text'] for p in _read_tmp('Acme shall pay.\n\nBeta shall deliver.'.encode('utf-32'))[0]] == ['Acme shall pay.', 'Beta shall deliver.']))
    nul_p, nul_m = _read_tmp(b'Acme shall\x00 pay.\n')
    checks.append(('NUL characters removed and noted', [p['text'] for p in nul_p] == ['Acme shall pay.'] and nul_m.get('nul_chars') == 1))
    ff_p, ff_m = _read_tmp(b'Acme shall pay.\fBeta shall deliver.\n')
    checks.append(('a page break ends a paragraph', [p['text'] for p in ff_p] == ['Acme shall pay.', 'Beta shall deliver.'] and ff_m.get('page_breaks') == 1))
    checks.append(('a PDF, a zip and a binary Office file with a .txt name are refused', _refused(b'%PDF-1.7 ...') and _refused(b'PK\x03\x04 ...') and _refused(b'\xd0\xcf\x11\xe0 ...')))
    checks.append(('the data files loaded cleanly', not LOAD_ERRORS and not load_rules()[1]))
    bad_entry = variant_problem({'id': 'x', 'check': 'x', 'pattern': '(', 'message': 'm', 'severity': 2, 'rule_ids': []})
    checks.append(('a malformed phrase-variant entry is caught', bool(bad_entry) and variant_problem({'id': 'x', 'check': 'x', 'severity': 4, 'pattern': 'a', 'message': 'm', 'rule_ids': []}) is not None))
    base = {'id': 'x', 'check': 'x', 'pattern': 'a', 'message': 'm', 'severity': 2, 'rule_ids': []}
    checks.append(('an empty pattern, a bool severity, int rule ids, a negative ctx and string examples are malformed',
               all(variant_problem(dict(base, **kv)) is not None for kv in ({'pattern': ''}, {'pattern': 'a*'}, {'severity': True}, {'rule_ids': [1]}, {'ctx': -5}, {'examples': 'text'}))
               and variant_problem(base) is None))
    toa_ok = {k: '' for k in TOA_FIELDS} | {'id': 't', 'term_word': 'tender', 'legal_meaning': 'x', 'replace': 'offer'}
    checks.append(('a term of art without a term_word, with a bad regex, or with string examples is a data error',
               all(_raises(InputError, lambda d=d: list(_toa_entries({'terms': [d]})) and _toa_regexes(d)) for d in (dict(toa_ok, term_word=''), dict(toa_ok, legal_use='('), dict(toa_ok, examples='x')))
               and _toa_regexes(toa_ok)['term_word'] is not None))
    try:
        import docx as _docx
        from docx.oxml import parse_xml as _px
        from docx.oxml.ns import nsdecls as _nsd
    except ImportError:
        _docx = None
    if _docx is not None:
        dn = _docx.Document()
        np_root = dn.part.numbering_part.element
        np_root.insert(0, _px(f'<w:abstractNum {_nsd("w")} w:abstractNumId="90"><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/>'
                              '<w:lvlText w:val="%1."/></w:lvl></w:abstractNum>'))
        np_root.append(_px(f'<w:num {_nsd("w")} w:numId="91"><w:abstractNumId w:val="90"/></w:num>'))
        np_root.append(_px(f'<w:num {_nsd("w")} w:numId="92"><w:abstractNumId w:val="90"/><w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride></w:num>'))
        for nid, txt in (('91', 'Acme shall pay.'), ('91', 'Acme shall deliver.'), ('92', 'Beta shall pay.'), ('92', 'Beta shall deliver.')):
            para = dn.add_paragraph(txt)
            para._p.get_or_add_pPr().append(_px(f'<w:numPr {_nsd("w")}><w:ilvl w:val="0"/><w:numId w:val="{nid}"/></w:numPr>'))
        tnum = _tmp(b'', '.docx')
        dn.save(tnum)
        try:
            labels = [p_.get('auto_label') for p_ in read_paragraphs(tnum)[0] if p_['text'].strip()]
        finally:
            os.unlink(tnum)
        checks.append(('a list restarts where a new num has a startOverride', labels == ['1.', '2.', '1.', '2.']))
        dt = _docx.Document()  # python-docx's template sets its fonts through the theme (minorHAnsi = Cambria, 11 point)
        dt.add_paragraph('Acme shall pay the Price.')
        tth = _tmp(b'', '.docx')
        dt.save(tth)
        try:
            tf = run(tth, False)[2]
        finally:
            os.unlink(tth)
        checks.append(('a theme font is resolved and checked (Cambria, 11 point)', any(f['check'] == 'font' and 'Cambria' in f['message'] for f in tf)))
    else:
        skipped += 1
    import subprocess as _sp
    def _rc(*args):
        return _sp.run([sys.executable, os.path.abspath(__file__), *args], capture_output=True, text=True).returncode
    checks.append(('exit codes: no such file 2, no file 5, a bad option 5', (_rc('no-such-contract.txt'), _rc(), _rc('--bogus')) == (2, 5, 5)))
    tbin = _tmp(bytes(range(256)) * 4, '.txt')
    try:
        checks.append(('a binary file with a .txt name is refused (exit 2)', _rc(tbin) == 2))
    finally:
        os.unlink(tbin)
    pn = _read_tmp(b'SUPPLY AGREEMENT\nAcme shall deliver the Units.\nNeither party shall assign this agreement or\ndelegate its duties.\nBeta shall pay.')[0]
    checks.append(('single newlines split into paragraphs', [p['text'] for p in pn] == ['SUPPLY AGREEMENT', 'Acme shall deliver the Units.', 'Neither party shall assign this agreement or delegate its duties.', 'Beta shall pay.']))
    invf = lint_text('A. Confidentiality.  The Receiving Party shall protect the Confidential Information of the Disclosing Party.\n\n2. Confidential Information shall be returned when the Disclosing Party asks.\n', inventory=True)[2]
    flagged = {f['match'] for f in invf if f['check'] == 'possibly-undefined-term'}
    checks.append(('undefined role labels flagged', {'Receiving Party', 'Disclosing Party'} <= flagged))
    checks.append(('a term after a typed number read whole', 'Information' not in flagged and 'Confidential Information' in flagged))
    rows = lint_text('Acme shall design the website (that work, the “Services”).  Acme shall perform the Services well.\n', inventory=True)[4]
    checks.append(('integrated definition after a lead phrase', any(r['term'] == 'Services' for r in rows)))
    _, _, fpo, _, ipo = lint_text(('This lease is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Landlord”), and BETA INC., '
                'a Texas corporation (“Tenant”).\n\nLandlord shall complete the work (the “Landlord’s Work”).\n\n“Tenant’s Share” means 12.5%.\n\n'
                'Each Member shall pay the amount in Schedule A (that Member’s “Capital Contribution”).\n\nRecipient may tell its employees (its “Representatives”).\n\n'
                'Landlord’s Work precedes Tenant’s Share, each Capital Contribution and the Representatives.\n'), inventory=True)
    terms = {r['term'] for r in ipo}
    res = lint_text(('D. Business Days.  In this agreement, “Business Day” means a day other than a Saturday or a Sunday.\n\n'
                'Acme shall send the Monthly Report (the “Monthly Report”) and the Final Report (the “Final Report”).  In this agreement, the “Reports” means the Monthly Report and the Final Report.\n\n'
                '“Closing” means the closing of the sale, and “Closing Date” means the day on which the Closing occurs.\n\n'
                '“Member” means a member of Acme.\n\nD. Disability.  A Member is “Disabled” if that Member cannot work for 90 days.\n\n'
                'Acme shall deliver the Reports on the Closing Date, no later than 2 Business Days after a Member becomes Disabled.\n'), inventory=True)
    fdf, idf = res[2], {r['term'] for r in res[4]}
    checks.append(('definitions after a heading, a lead phrase, and, or is "X" if', {'Business Day', 'Reports', 'Closing Date', 'Disabled', 'Member'} <= idf
               and not any(f['check'] == 'possibly-undefined-term' for f in fdf)))
    res = lint_text(('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Seller”), and BETA INC., a Texas corporation (“Buyer”).\n\n'
                'John Hollis (“Owner”) owns Seller.\n\n“Brazos” means Brazos Valve Co., a Texas corporation that Seller wholly owns.\n\n'
                'Owner shall not compete with Buyer.  Brazos shall deliver its records to Buyer.  Seller shall deliver the Shares.\n'), inventory=False)
    np_hits = {f['match'].split()[0] for f in res[2] if f['check'] == 'nonparty-obligation'}
    checks.append(('named nonparties (recital and means forms)', np_hits == {'Owner', 'Brazos'}))
    res = lint_text(('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Seller”), and BETA INC., a Texas corporation (“Buyer”).\n\n'
                '“Escrow Agent” means First Trust Company, a Tennessee trust company.\n\nThe Escrow Agent must hold the Holdback Amount.\n\n'
                'EXHIBIT 2\n\nThis escrow agreement is among Buyer, Seller, and First Trust Company, as escrow agent (in that role, the “Escrow Agent”).\n\n'
                'The Escrow Agent shall hold the Escrow Funds in a segregated account.\n'), inventory=False)
    checks.append(("an exhibit form's own parties (the escrow agent signs the escrow agreement)", not any(f['check'] == 'nonparty-obligation' for f in res[2])))
    res = lint_text(('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Owner”), and BETA INC., a Texas corporation (“Manager”).\n\n'
                'Owner owns the hotel.  Manager will do so through the Operator.\n\nThe parties therefore agree as follows:\n\nManager will manage the hotel.\n\n'
                'EXHIBIT 1\n\nThis escrow agreement is dated ______, 2027, and is among ACME LLC (“Owner”), BETA INC. (“Manager”), and Fifth Third Bank, National Association, in its capacity as escrow agent (the “Escrow Agent”).\n\n'
                'The Escrow Agent shall release the Escrow Amount to Owner.\n'), inventory=False)
    wills = [f for f in res[2] if f['check'] == 'category-will']
    checks.append(('will in a recital is not a duty; will in the body is', len(wills) == 1 and 'manage' in res[0][wills[0]['para']]['text']))
    one_para = house_checks({'idx': 3, 'text': 'Owner owns the hotel.  Manager will do so through the Operator.  The parties therefore agree as follows:', 'fmt': {}})
    checks.append(('will in a recital that shares its paragraph with the lead-in is not a duty', not any(f['check'] == 'category-will' for f in one_para)))
    checks.append(('a role phrase before the parenthetical makes the escrow agent a party of the exhibit', not any(f['check'] == 'nonparty-obligation' for f in res[2])))
    res = lint_text(('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Company”), and DANA PARK (“Executive”).\n\n'
                'Company shall pay Executive the Severance no later than 30 days after the Separation Date.\n\n'
                'Buyer and Seller appoint Escrow Agent as escrow agent.  “Escrow Agent” means First Trust Company, a Tennessee trust company.\n\n'
                'EXHIBIT 1\n\nFORM OF RELEASE\n\nExecutive gives this release.  Executive’s employment ended on [date] (the “Separation Date”).\n'), inventory=True)
    checks.append(('a term defined only inside a form is undefined in the body', any(f['check'] == 'possibly-undefined-term' and f['match'] == 'Separation Date' for f in res[2])
               and not any(f['check'] == 'defined-term-lowercase' for f in res[2])))
    res = lint_text(('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Seller”), and BETA INC., a Texas corporation (“Buyer”).\n\n'
                '“Unit Price” means the price in Schedule A.\n\nBuyer shall pay the Unit Price for each Unit that Buyer orders under a Purchase Order.\n\n'
                '| Product | Part No. | Unit Price | Minimum Order Quantity | Lead Time |\n|---|---|---|---|---|\n| Valve | V-1 | $40 | 100 | 10 days |\n\n'
                '4. Permitted Liens: the security interest of Fifth Third Bank in the turning centers under an equipment loan.\n\n'
                'ACME LLC    By: ____________________    Name: ____________________    Title: Managing Director    Date: ____________________\n'), inventory=True)
    hd_hits = {f['match'] for f in res[2] if f['check'] == 'possibly-undefined-term'}
    checks.append(('a Markdown heading row, a colon run-in label and a signature line are not defined terms', not hd_hits & {'Unit Price', 'Minimum Order Quantity', 'Lead Time', 'Part No', 'Permitted Liens', 'Managing Director', 'Managing Director  Date', 'Date', 'Name', 'Title'}))
    checks.append(('a capitalized term in prose beside them is still flagged', 'Purchase Order' in hd_hits))
    res = lint_text(('Each party waives the protection of Section 664.6 of the California Code of Civil Procedure.  Acme shall follow the Escalation Procedure in Schedule A.\n'), inventory=True)
    cp_hits = {f['match'] for f in res[2] if f['check'] == 'possibly-undefined-term'}
    checks.append(("a statute's name after Code of is not a term; an undefined Procedure is", 'Civil Procedure' not in cp_hits and 'Escalation Procedure' in cp_hits))
    res = lint_text(('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Seller”), and BETA INC., a Texas corporation (“Buyer”).\n\n'
                'Seller shall not disclose the information to any Person other than Buyer.  Each Contributing Member shall pay in proportion to the Sharing Ratios.\n'), inventory=True)
    pn_hits = {f['match'] for f in res[2] if f['check'] == 'possibly-undefined-term'}
    checks.append(('undefined Person, Member and Ratios are flagged', {'Person', 'Contributing Member', 'Sharing Ratios'} <= pn_hits))
    # red-team round: undefined terms whose last word is a new contract noun; a 2nd form is an inflection or a hyphenation only
    res = lint_text(('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Acme”), and BETA INC., a Texas corporation (“Beta”).\n\n'
                '“Services” means the routing services in Schedule A.  “Sublicensee” means a person to which Beta sublicenses the Software.  “Non-Defaulting Party” means the party that is not in default.\n\n'
                'Acme shall complete the Transition Assistance no later than 90 days after the Term ends.  Beta shall meet the Service Levels and the Uptime Targets in Schedule A.\n\n'
                'Each Sub-Licensee shall sign a joinder.  The Nondefaulting Party may terminate this agreement.\n'), inventory=True)
    sf = {f['match']: f['message'] for f in res[2] if f['check'] == 'possibly-undefined-term'}
    checks.append(('Transition Assistance, Service Levels and Uptime Targets are undefined, not 2nd forms', {'Transition Assistance', 'Service Levels', 'Uptime Targets'} <= set(sf)
               and not any('2nd form' in sf[k] for k in ('Transition Assistance', 'Service Levels', 'Uptime Targets') if k in sf)))
    checks.append(('a hyphenated or unhyphenated spelling is a 2nd form of the defined term itself', 'of the defined term "Sublicensee"' in sf.get('Sub-Licensee', '')
               and 'of the defined term "Non-Defaulting Party"' in sf.get('Nondefaulting Party', '')))
    # circular definitions: A uses B and B uses A; a chain (Closing Date uses Closing) and a term in its own definition are not circular
    res = lint_text(('This agreement is between Acme Corp. ("Acme") and Beta LLC ("Beta").  The parties agree as follows:\n\n'
                '“Approved Carrier” means a carrier on the Carrier List.  “Carrier List” means the list of Approved Carriers that Acme maintains.\n\n'
                '“Closing” means the closing of the sale, and “Closing Date” means the day on which the Closing occurs.\n\n'
                '“Trademark” means a registered trademark or any trademark that is the subject of an application.\n\n'
                '“Product” means each component that Schedule A lists and that Beta makes to the Specifications.  “Specifications” means the specifications for the Products that Acme approves.\n\n'
                '“Service” means the Lodgepole platform, including the Documentation.  “Documentation” means the user guides for the Service.\n\n'
                '“Servicer” means Lakeshore Field Service, Inc., or any replacement that services a Unit.  “Unit” means a machine the Servicer maintains.\n\n'
                '“Confidential Information” means information that a party (the "Disclosing Party") gives the other party.  “Disclosing Party” has the meaning in the definition of Confidential Information.\n\n'
                'Acme shall use an Approved Carrier on the Closing Date, shall protect each Trademark, shall deliver the Products, the Service, and the Documentation, '
                'and shall keep each Unit at the Servicer and the Confidential Information with the Disclosing Party.\n'), inventory=True)
    cd = [f['match'] for f in res[2] if f['check'] == 'circular-definition']
    res = lint_text(('Acme shall file each return with the Internal Revenue Service and shall keep organic certification under the National Organic Program in 7 C.F.R. Part 205.  '
                'Acme shall notify the Department of Agriculture.  Acme shall pay the Purchase Price to Beta.\n'), inventory=True)
    checks.append(('agency names and a program named with its citation are not undefined terms; Purchase Price still is',
               [f['match'] for f in res[2] if f['check'] == 'possibly-undefined-term'] == ['Purchase Price']))
    checks.append(('a circular pair is reported once, on the 1st term (a party name is no anchor); a chain, a self-reference, and a pair anchored to a schedule, '
               'a product name, a company name, or an integrated definition are not', cd == ['Approved Carrier']))
    # shall obtain the OTHER PARTY's approval is a deal term, not a nonparty risk (MSCD 8.5); the landlord's consent is
    res = lint_text(('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Licensor”), and BETA INC., a Texas corporation (“Licensee”).\n\n'
                'Before selling any new Licensed Product, Licensee shall obtain Licensor\'s written approval of that product\'s recipe.  '
                'Licensee shall obtain the landlord\'s written consent to the assignment of the Lease before the Closing.\n'), inventory=False)
    ra = [f['match'] for f in res[2] if f['check'] == 'risk-allocation']
    checks.append(('shall obtain the other party\'s approval is not flagged as a nonparty risk; the landlord\'s consent is',
               len(ra) == 1 and 'landlord' in ra[0]))
    # a numId with no w:val: Word's label can't be read; the lint notes it and goes on (no NameError, no exit 3)
    try:
        import docx as _dx
        from docx.oxml import OxmlElement as _OE2
        from docx.oxml.ns import qn as _qn2
        _d = _dx.Document()
        _p = _d.add_paragraph('Acme shall pay the Fee.')
        _npr = _OE2('w:numPr')
        _il = _OE2('w:ilvl')
        _il.set(_qn2('w:val'), '0')
        _npr.append(_il)
        _npr.append(_OE2('w:numId'))
        _p._p.get_or_add_pPr().append(_npr)
        tbn = _tmp(b'', '.docx')
        _d.save(tbn)
        try:
            _paras, _meta = read_paragraphs(tbn)
            res = run(tbn, False)
        finally:
            os.unlink(tbn)
        checks.append(('a numId with no w:val is read with a numbering_unread note, not a crash', _meta.get('numbering_unread') is True and _paras[0]['text'] == 'Acme shall pay the Fee.'))
    except ImportError:
        pass
    # a lowercase common noun as the subject of shall, when the parties are known
    res = lint_text(('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Acme”), and BETA INC., a Texas corporation (“Beta”).\n\n'
                'The freight forwarder shall deliver the bills of lading to Acme no later than 2 Business Days after each shipment.  The other party shall pay the Fees.\n\n'
                'Each customs broker shall file the entry.  The Fees shall be paid by Beta.  Acme shall deliver the Equipment.\n'
                'The headings in this agreement shall not affect its interpretation.  The entire unpaid balance shall become due.  '
                'Each transferee shall sign a joinder.  Any person whom Acme engages shall sign an assignment.  The waiver shall bind Acme.\n'), inventory=False)
    lc = sorted(f['match'].split(' shall')[0] for f in res[2] if f['check'] == 'nonparty-obligation')
    checks.append(('lowercase nonparty subjects (freight forwarder, customs broker, transferee, person) are flagged at low confidence; the other party, Acme, '
               'and things (headings, balance, waiver) are not',
               lc == ['customs broker', 'freight forwarder', 'person whom Acme engages', 'transferee'] and all(f['confidence'] == 'low' and f['severity'] == 2 for f in res[2] if f['check'] == 'nonparty-obligation')))
    toc = ''.join(f'Article {n} Heading {n}\n\n' for n in range(1, 18))
    res = lint_text((toc + 'This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Acme”), and BETA INC., a Texas corporation (“Beta”).\n\n'
                'Acme will pay Beta the Fee.  The Company owns the Shares.  “Subsidiary” means an entity that Acme controls.  Acme shall cause its Subsidiaries to comply.\n'), inventory=True)
    tc_checks = {f['check'] for f in res[2]}
    checks.append(('a table of contents before the introductory clause does not hide the parties', 'category-will' in tc_checks and 'party-article' not in tc_checks))
    checks.append(('a defined term in -y is known in its -ies plural', not any(f['check'] == 'possibly-undefined-term' and f['match'] == 'Subsidiaries' for f in res[2])))
    checks.append(('run() restores the module state', PARTY_TERMS == set() and NONPARTY_NAMED == set() and RECITAL_IDX == set()))
    art = [{'idx': 0, 'auto_label': 'Article I', 'text': 'DEFINITIONS', 'where': 'body', 'fmt': {}},
           {'idx': 1, 'auto_label': 'A.', 'text': 'Terms.  In this agreement, the following definitions apply:', 'where': 'body', 'fmt': {}},
           {'idx': 2, 'auto_label': 'Article II', 'text': 'PAYMENT', 'where': 'body', 'fmt': {}},
           {'idx': 3, 'auto_label': 'A.', 'text': 'Fee.  Acme shall pay the Fee.', 'where': 'body', 'fmt': {}},
           {'idx': 4, 'auto_label': 'B.', 'text': 'Timing.  Acme shall pay it on the Closing Date.', 'where': 'body', 'fmt': {}}]
    oc = [f for f in outline_checks(art, document_shape(art)) if 'Only child' in f['message']]
    checks.append(('Word labels "Article I" are outline items, so a lone A. under one is an only child', len(oc) == 1 and oc[0]['para'] == 1))
    res = lint_text(('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Seller”), and BETA INC., a Texas corporation (“Buyer”).\n\n'
                '“Escrow Agent” means First Trust Company, a Tennessee trust company.\n\nThe Escrow Agent, N.A. shall release the Holdback Amount to Seller.  Acme Holdings, Inc. shall deliver the Units.\n'), inventory=False)
    checks.append(('an abbreviation period does not cut off the subject (Escrow Agent, N.A. shall)', any(f['check'] == 'nonparty-obligation' and 'Escrow Agent' in f['match'] for f in res[2])))
    checks.append(('a thing named in the introductory clause is not a party', party_terms([{'idx': 0, 'text': 'This lease is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company ("Landlord"), and BETA INC., a Texas corporation ("Tenant"), for Suite 200 in the building at 100 Main Street (the "Building").', 'fmt': {}}]) == {'Landlord', 'Tenant'}))
    res = lint_text(('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Seller”), and BETA INC., a Texas corporation (“Buyer”).\n\n'
                'Buyer shall pay the fees in Schedule A.\n\nSCHEDULE A\n\nFees\n\nThe fee for each Unit is $500.\n\nBuyer shall pay each fee no later than 30 days after the invoice date.\n\n'
                'EXHIBIT 1\n\nFORM OF ESCROW AGREEMENT\n\nThe Escrow Agent shall hold the Escrow Funds.\n'), inventory=False)
    sp = [f for f in res[2] if f['check'] == 'schedule-provision']
    checks.append(('a duty inside a schedule is flagged; an exhibit form is not', len(sp) == 1 and 'Buyer shall pay' in sp[0]['match']))
    st_p = [{'idx': 0, 'fmt': {}, 'text': 'This section contains the disclosure that Section 8-70-115(2) of the Colorado Revised Statutes requires: Juniper Peak is not entitled '
                                         'to unemployment insurance benefits unless unemployment compensation coverage is provided by Juniper Peak or some other entity.'}]
    st_f = statutory_text_filter(st_p, house_checks(st_p[0]))
    checks.append(('statutory text keeps its words (1 note, no style findings)', [f['check'] for f in st_f] == ['statutory-text']))
    checks.append(('possessive defined terms', {'Landlord’s Work', 'Tenant’s Share', 'Capital Contribution', 'Representatives'} <= terms
               and not any(f['check'] == 'defined-twice' for f in fpo)))
    ar = lambda t: [f for f in arithmetic_checks([{'idx': 0, 'text': t}])]
    checks.append(('arithmetic: installments that miss the total', len(ar('Buyer shall pay $60,000 in 3 equal installments of $25,000.')) == 1))
    checks.append(('arithmetic: installments that make the total', not ar('Buyer shall pay $60,000 in 3 equal installments of $20,000.')))
    checks.append(('arithmetic: listed installments', not ar('Client shall pay $48,000 in 3 installments of $19,200, $19,200, and $9,600.')))
    checks.append(('arithmetic: a percentage of a defined amount', len(ar('The price is $150,000 (the "Purchase Price").  Buyer shall pay 30% of the Purchase Price ($42,000) at signing.')) == 1))
    checks.append(('arithmetic: $2 million in 4 installments of $500,000', not ar('Buyer shall pay $2 million in 4 equal installments of $500,000.')))
    checks.append(('arithmetic: $2 million in 4 installments of $400,000', len(ar('Buyer shall pay $2 million in 4 equal installments of $400,000.')) == 1))
    checks.append(('arithmetic: a deposit and the balance', not ar('Buyer shall pay a deposit of $10,000 at signing and the balance in 3 installments of $30,000.')))
    checks.append(('arithmetic: installments with interest', not ar('Borrower shall repay the loan of $100,000, payable in 12 monthly installments of $8,792.59, which include interest.')))
    checks.append(('arithmetic: a rate per month', not ar('Lessee shall pay Basic Rent of $12,000 per month for the Units, in 36 monthly installments of $12,000.')))
    checks.append(('arithmetic: or is not a total', not ar('Customer may make 2 payments of $5,000 or $9,000 upfront.')))
    checks.append(('arithmetic: a percentage to the cent', not ar('Buyer shall pay 2.5% of $1,001 ($25.03).') and len(ar('Buyer shall pay 2.5% of $1,001 ($25.02).')) == 1))
    checks.append(('arithmetic: installments restated in parentheses', not ar('Beta shall pay Acme a setup fee of $12,000 (12 installments of $1,000) under the schedule in Schedule A.')
               and len(ar('Beta shall pay Acme a setup fee of $12,000 (12 installments of $900) under the schedule in Schedule A.')) == 1))
    checks.append(('arithmetic: an annual total paid monthly', not ar('The annual Fees are $84,000, which Beta shall pay as $7,000 on the 1st day of each month.')
               and len(ar('The annual Fees are $84,000, which Beta shall pay as $6,000 on the 1st day of each month.')) == 1
               and len(ar('The yearly rent is $48,000, payable in installments of $4,500 per month.')) == 1
               and not ar('The annual budget is $84,000, and Beta shall pay a deposit of $500 each month.')))
    res = lint_text('Acme shall deliver the Units listed in Schedule A.\n\nBeta shall pay the fees in Schedule B.\n', inventory=False)
    att = [f for f in res[2] if f['check'] == 'attachment-check']
    checks.append(('the attachment reminder is 1 trigger-style note, not a direct finding', len(att) == 1 and att[0]['source'] == 'rules' and 'Attachments in 2 paragraphs' in att[0]['message']))
    checks.append(('arithmetic: 1 amount defined twice', len(arithmetic_checks([{'idx': 0, 'text': 'The Purchase Price is $4,200,000, payable at Closing.'},
                                                                           {'idx': 1, 'text': 'The Purchase Price is $4,100,000.'}])) == 1))
    checks.append(('arithmetic: an amount qualified by a period is a schedule, not a conflict (ACC-007)',
                   not ar('The Base Rent is $5,000 for the first Lease Year.  The Base Rent is $5,150 for the second Lease Year.')
                   and not ar('The Fee is $500 per month.  The Fee is $6,000.50 for the year.') and len(ar('The Fee is $500.  The Fee is $600.')) == 1))
    tb = lambda rows: table_total_checks([], None, [[[(c, 0) for c in r] for r in rows]])
    checks.append(('table: subtotal and tax', not tb([['Item', 'Amount'], ['A', '$100'], ['B', '$200'], ['Subtotal', '$300'], ['Tax', '$24'], ['Total', '$324']])))
    checks.append(('table: no header row', not tb([['Phase 1', '$10,000'], ['Phase 2', '$20,000'], ['Total', '$30,000']])))
    checks.append(('table: a credit in parentheses', not tb([['Item', 'Amount'], ['Fee', '$1,000'], ['Credit', '($200)'], ['Total', '$800']])))
    checks.append(('table: a Monthly Fee column whose rows miss their Total Monthly Fee is a conflict (corpus6 c138)',
                   bool(tb([['Service', 'Monthly Fee'], ['Platform', '$10,000'], ['Pipeline', '$6,000'], ['Support', '$3,000'], ['Total Monthly Fee', '$18,500']]))))
    checks.append(('table: a one-time fee beside a monthly fee under a Total Year 1 is a contract value, not a sum',
                   not tb([['Item', 'Amount'], ['Implementation Fee', '$5,000'], ['Monthly Subscription Fee', '$1,000'], ['Total Year 1', '$17,000']])))
    checks.append(('table: a percentage restated in parentheses is not a credit (ACC-002)',
                   not tb([['Milestone', 'Amount'], ['Signing', '30% ($30,000)'], ['Delivery', '70% ($70,000)'], ['Total', '$100,000']])
                   and not tb([['Milestone', 'Amount'], ['Signing', '$30,000'], ['Delivery', '$70,000'], ['Total', '100% ($100,000)']])
                   and not tb([['Item', 'Amount'], ['Fee', '$1,000'], ['Credit', '-$200'], ['Total', '$800']])))
    checks.append(('table: a rate row beside a one-time fee is a contract value, not a sum (ROB-003)',
                   not tb([['Item', 'Amount'], ['Implementation Fee', '$5,000'], ['Monthly Subscription Fee', '$1,000'], ['Total Year 1', '$17,000']])
                   and not tb([['Item', 'Amount'], ['Setup', '$5,000'], ['Support', '$1,000 per month'], ['Total', '$17,000']])))
    checks.append(('money with 30 digits and a scale word is exact', _money(MONEY_RE.search('$' + '9' * 30)) == int('9' * 30) * 100 and _money(MONEY_RE.search('$1.5 million')) == 150000000 and _money(MONEY_RE.search('$1.005')) is None))
    checks.append(('roman numerals past 3999 and a gridSpan of billions are clamped', _fmt_num(4000, 'upperRoman') == '4000' and _fmt_num(14, 'upperRoman') == 'XIV'))
    checks.append(('table: a closing statement with a Balance row is not a sum', not tb([['Item', 'Amount'], ['Purchase Price', '$100,000'], ['Deposit', '$10,000'], ['Balance', '$90,000'], ['Total', '$100,000']])))
    checks.append(('table: a wrong total', len(tb([['Item', 'Amount'], ['Fee', '$1,000'], ['Credit', '$200'], ['Total', '$1,300']])) == 1))
    checks += _round8_cases(_tmp, ar, tb)
    checks += _round9_cases()
    checks += _round10_cases(_tmp)
    # terms of art (house rule 13): each example fires for its term; each look-alike doesn't
    for e in terms_of_art():
        for texts, want in ((e['examples'], True), (e['lookalikes'], False)):
            for tx in texts:
                hits = [f for f in term_of_art_checks([{'idx': i, 'text': x} for i, x in enumerate(tx.split('\n\n'))]) if f'uses {e["id"]}' in f['message']]
                checks.append((f'terms of art: {e["id"]} {"example" if want else "look-alike"}: {tx[:80]!r}', bool(hits) == want))
    # data-driven phrase variants: each example fires its check and needs the entry; each look-alike doesn't fire it
    checks += [(f'variants: pattern does not compile: {bad}', False) for bad in BAD_VARIANTS]
    global _VARIANTS
    all_variants = phrase_variants()
    for c in all_variants:
        own = False  # at least 1 example must need this entry: an entry the code's own checks fully shadow is dead data
        for ex in c.get('examples', []):
            caught = c['rx'].search(ex) and any(f['check'] == c['check'] for f in house_checks({'idx': 0, 'text': ex, 'where': 'body', 'style': '', 'fmt': {}}))
            checks.append((f"variants {c['id']}: caught by its own pattern and its check: {ex}", bool(caught)))
            if not caught:
                continue
            _VARIANTS = [v for v in all_variants if v is not c]
            try:
                own = own or not any(f['check'] == c['check'] for f in house_checks({'idx': 0, 'text': ex, 'where': 'body', 'style': '', 'fmt': {}}))
            finally:
                _VARIANTS = all_variants
        checks.append((f"variants {c['id']}: at least 1 example needs this entry (not fully shadowed: narrow it or delete it)", own))
        for ex in c.get('lookalikes', []):
            checks.append((f"variants {c['id']}: look-alike clear: {ex}", not any(f['check'] == c['check'] for f in house_checks({'idx': 0, 'text': ex, 'where': 'body', 'style': '', 'fmt': {}}))))
    checks.append(('a .pdf is refused', _raises(ValueError, lambda: read_paragraphs('contract.pdf'))))
    fails = [name for name, ok in checks if not ok]
    for name in fails:
        print('FAIL:', name)
    total = len(checks)
    print(f'self-test: {total - len(fails)}/{total} passed' + (f'; {skipped} groups of .docx tests SKIPPED because python-docx is not installed' if skipped else ''))
    return 1 if fails else 0


def main():
    ap = ArgParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('path', nargs='?')
    ap.add_argument('--json', help='also write findings as JSON to this path')
    ap.add_argument('--inventory', action='store_true')
    ap.add_argument('--whose', choices=['blake', 'other-side'], help="whose draft it is; tailors the represents-and-warrants finding")
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.path:
        ap.error('give a contract file (.docx, .txt or .md), or --self-test')
    phrase_variants()
    terms_of_art()
    if LOAD_ERRORS:
        raise InputError('the skill\'s data is damaged, so the lint would miss findings: ' + '; '.join(LOAD_ERRORS) + ' (reinstall the skill)')
    if not os.path.isfile(a.path):
        raise InputError(f'no such file: {a.path}')
    paras, meta, findings, broad, inv = run(a.path, a.inventory, a.whose)
    if BAD_VARIANTS or load_rules()[1]:
        meta = dict(meta, skipped_checks=len(BAD_VARIANTS) + len(load_rules()[1]))
    text = report(a.path, paras, meta, findings, broad, inv)
    if a.json:  # the durable artifact first: a reader that closes the pipe early (| head) must never leave a stale lint.json behind
        write_json(a.json, {'file': a.path,
                            'paragraphs': [dict({'idx': p['idx'], 'text': p['text'], 'where': p.get('where', 'body')},
                                                **({'label': p['auto_label']} if p.get('auto_label') else {})) for p in paras],
                            'findings': findings, 'broad_triggers': broad, 'inventory': inv,
                            'tracked_changes': meta.get('changes') or [],
                            'comments': [dict({'author': c[0], 'text': c[1]}, **({'reply_to': c[2]} if len(c) > 2 and c[2] is not None else {}))
                                         for c in meta.get('comments') or []],
                            'notes': report_notes(meta, paras)})
    sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    setup_output()
    sys.exit(run_main('mscd_lint', main))
