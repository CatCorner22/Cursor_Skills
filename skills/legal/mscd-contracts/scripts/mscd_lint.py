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
from typing import NamedTuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # the shared helpers sit beside this script
from _cli import ArgParser, InputError, read_json, run_main, setup_output, write_json  # noqa: E402
from _rules_data import TERMS_OF_ART_PATH, VARIANTS_PATH, load_overrides, load_records, superseded_ids  # noqa: E402

# ---------------------------------------------------------------- shared constants

# invisible format characters a paste from a PDF or a web page carries: a soft hyphen, zero-width spaces and joiners, a word
# joiner, a stray byte-order mark. Word shows none of them, and each one splits a word in 2 for every regex here
INVISIBLE = re.compile('[\u00ad\u200b\u200c\u200d\u2060\ufeff]')


_A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'


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


COMMENT_SHOWN = 300  # characters of each comment the Markdown report shows; the JSON carries the whole text

# ---------------------------------------------------------------- text utilities

SENT_BREAK = re.compile(r"[.;!?][\"”’)]*\s+(?=[A-Z“\"(])")  # where 1 sentence (or a semicolon clause) ends and the next starts
ABBREV_REACH = 12  # characters a $-anchored ABBREV search needs: its longest alternative (L.L.C.) plus a word-boundary character


def tail(t, pos, n):
    """The n characters of t before pos. A $-anchored search over this window decides exactly as it would over t[:pos],
    as long as n exceeds the pattern's longest possible match, so the pattern still sees a real character (not the window
    edge) where it tests a word boundary. Without the window, a search over the whole prefix costs O(pos), which makes a
    check that runs once per match in a 200 KB single-paragraph document quadratic."""
    return t[max(0, pos - n):pos]


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
    __slots__ = ('_end', '_start', '_text')

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


def roman_value(s):
    vals = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100}
    s = s.lower()
    if not s or any(ch not in vals for ch in s):
        return 0
    total = 0
    for a, b in zip(s, s[1:] + ' '):
        total += -vals[a] if b != ' ' and vals[a] < vals[b] else vals[a]
    return total if 0 < total < 40 else 0


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

# ---------------------------------------------------------------- reading the document

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


def _points(size):
    """A python-docx font size in points, or None when the style sets none."""
    return size.pt if size else None


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
    sz = sz or _points(chain(cst, lambda s_: s_.font.size)) or _points(chain(pst, lambda s_: s_.font.size)) or dflt[1]
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
    paras_meta = {}  # the reader fills it below; add_para() may set 'numbering_unread' before the font entries are known
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
    def add_para(p, where):
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
        add_para(Paragraph(p_el, d._body), _where(p_el, 'body'))
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
                    add_para(hp, where)
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

# ---------------------------------------------------------------- the document model

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
    for term, words, pidx, st, en, kind, lead in defs:
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
            # the paragraph's leading definition, with means (not includes); definitions() matched it once
            if not lead or lead.group(1).strip().rstrip(',.;:') != term or not lead.group(0).rstrip().endswith('means'):
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
    for term, words, pidx, st, en, kind, _lead in defs:
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


class Definition(NamedTuple):
    """1 definition the contract makes. kind is 'integrated' (a parenthetical), 'sentence' (a sentence that makes a term:
    is the "X", the "X" is, is "X" if; the inventory lists it as integrated), 'autonomous' ("X" means ...), or 'pointer'
    ("X" has the meaning in ...). lead is the leading autonomous definition of the paragraph this definition sits in, as
    AUTON matched it, or None: every definition in a paragraph carries the same lead, which definitions() matches once."""

    term: str
    words: str
    para: int
    start: int
    end: int
    kind: str
    lead: 'object'


def definitions(paras):
    """Each definition in the contract, as a Definition record, in paragraph and position order. A comma or period typed
    inside the closing quotation mark isn't part of the term. The same definition read by 2 patterns counts once (the
    dedupe on kind, paragraph and position)."""
    out = []
    for p in paras:
        t = p['text']
        dt = def_text(t)
        off = len(t) - len(dt)  # def_text strips a prefix only
        dm = AUTON.match(dt)   # the paragraph's leading autonomous definition: 1 match here, carried on every record below
        for m in INTEG.finditer(t):
            cut = max(t.rfind('.', 0, m.start()), t.rfind(';', 0, m.start()))
            # the defining words: the text before the parenthetical, plus its scope noun (that position, the "Title")
            words = t[cut + 1:m.start()] + ' ' + m.group(0)[:m.start(1) - m.start()]
            out.append(Definition(m.group(1).strip().rstrip(',.;:'), words, p['idx'], m.start(1), m.end(1), 'integrated', dm))
            close = t.find(')', m.end())
            for m2 in SECOND_TERM.finditer(t, m.end(), close if close > 0 else m.end() + 120):
                out.append(Definition(m2.group(1).strip().rstrip(',.;:'), words, p['idx'], m2.start(1), m2.end(1), 'integrated', dm))
        if dm:
            out.append(Definition(dm.group(1).strip().rstrip(',.;:'), sentence_from(t, off + dm.end()), p['idx'], off + dm.start(1), off + dm.end(1),
                                  'pointer' if re.search(r"\b(?:has|shall have)\b", dm.group(0)) else 'autonomous', dm))
        for m in list(AUTON_INNER.finditer(t)) + list(AUTON_LEAD.finditer(t)):
            out.append(Definition(m.group(1).strip().rstrip(',.;:'), sentence_from(t, m.end()), p['idx'], m.start(1), m.end(1),
                                  'pointer' if re.search(r"\bhas\b", m.group(0)) else 'autonomous', dm))
        for rx in (IS_A_TERM, THE_TERM_IS, IS_TERM_IF):
            for m in rx.finditer(t):
                out.append(Definition(m.group(1).strip().rstrip(',.;:'), _sentence_words(t, m), p['idx'], m.start(1), m.end(1), 'sentence', dm))
    seen, uniq = set(), []
    for d in sorted(out, key=lambda d: (d.para, d.start)):  # a stable sort: at 1 position, the parenthetical reading comes before the sentence reading
        key = ('integrated' if d.kind == 'sentence' else d.kind, d.para, d.start)
        if key not in seen:
            seen.add(key)
            uniq.append(d)
    return uniq


INTEG = re.compile(r"\((?:[A-Za-z][^()\"“”]{0,80}?,\s+)?(?:each,?\s+)?(?:the|a|an|its|their|his|her|(?:that|each|such)\s+[A-Z][\w-]*['’]s|[A-Z][\w-]*['’]s)?\s*\*{0,2}[\"“‘']\*{0,2}((?:[^\"”’']|['’](?=[A-Za-z])){1,60}?)\*{0,2}[\"”’'](?![A-Za-z])\*{0,2}")
AUTON = re.compile(r"^\s*\*{0,2}[\"“‘']\*{0,2}((?:[^\"”’']|['’](?=[A-Za-z])){1,60}?)\*{0,2}[\"”’'](?![A-Za-z])\*{0,2}\s+(?:(?:of|for|with\s+respect\s+to)\s+(?:a|an|any|each)\s+[A-Za-z][\w-]*\s+)?(?:means|includes|has the meaning|has the same meaning|shall mean|shall have)")
AUTON_INNER = re.compile(r"(?:(?<=[.;:]\s)|(?<=[.;:]\s\s)|(?<=\)\s)|(?<=\s\s)|(?<=,\sand\s)|(?<=\band\s))\**[\"“‘]\**([A-Z](?:[^\"”’]|’(?=[A-Za-z])){0,59}?)\**[\"”’](?![A-Za-z])\**\s+(?:(?:of|for)\s+(?:a|an|any|each)\s+[A-Za-z][\w-]*\s+)?(?:means|has the meaning|includes)\b")
# a definition after a lead phrase anywhere in a paragraph: In this agreement, (the) "Reports" means ...
# the lead phrases a definition may follow: As used herein, In this agreement, For purposes of this Amendment
DEF_LEAD_WORDS = r"(?:As\s+used\s+(?:herein|in\s+this\s+\w+)|When\s+used\s+in\s+this\s+\w+|For\s+(?:the\s+)?purposes?\s+of\s+this\s+\w+|In\s+this\s+\w+)(?:\s+[A-Z0-9]{1,3}\b)?"  # In this Schedule A, "Error" means
AUTON_LEAD = re.compile(r"(?i:\b" + DEF_LEAD_WORDS + r")\s*,\s*(?:the\s+)?\**[\"“‘]\**([A-Z](?:[^\"”’]|’(?=[A-Za-z])){0,59}?)\**[\"”’](?![A-Za-z])\**\s+(?:means|has the meaning|includes|refers to)\b")
# an attachment heading: the label (A; "A"; 1.1; 3.2(a)) then the end of the line, a dash, a colon, 2 spaces, or FORM OF on the same line;
# "Exhibit A lists ..." in running text is not a heading
ATT_LABEL = r"\s+[\"“]?[A-Z0-9]+(?:\.[0-9]+)*(?:\([a-z0-9]{1,3}\))?[\"”]?"
ATT_TAIL = r"[ \t*_]*(?:$|[-\u2014\u2013:]|\s{2,}|\n|\s+(?:FORM|Form)\s+(?:OF|of)\b)"
EXHIBIT_HEAD = re.compile(r"^[\s#*_]*(?:EXHIBIT|Exhibit|SCHEDULE|Schedule|ANNEX|Annex|APPENDIX|Appendix)" + ATT_LABEL + ATT_TAIL)


DEF_LEAD = re.compile(r"^" + DEF_LEAD_WORDS + r"\s*,?\s*(?=\**[\"“‘'])", re.I)


def def_text(text):
    """A paragraph's text as a definition: without a typed enumerator (A. or 6.1) or a lead phrase (As used herein,)."""
    t = TYPED_NUM.sub('', text, count=1)
    t = re.sub(r"^[*_]*[A-Z][\w'’-]*(?:\s+(?:and|of|or|the|[A-Z][\w'’-]*)){0,5}[*_]*\.[*_]*\s{1,2}(?=\**[\"“‘']|(?:As\s+used|When\s+used|For\s+(?:the\s+)?purposes?|In\s+this)\b)", '', t, count=1)  # a run-in heading (Definitions.  "X" means; Business Days.  In this agreement, "X" means)
    return DEF_LEAD.sub('', t, count=1)


SCHED_HEAD = re.compile(r"^[\s#*_]*(?:SCHEDULE|Schedule|ANNEX|Annex|APPENDIX|Appendix)" + ATT_LABEL)
EXH_HEAD_ONLY = re.compile(r"^[\s#*_]*(?:EXHIBIT|Exhibit)" + ATT_LABEL)

# ---------------------------------------------------------------- severity policy and findings

LOAD_ERRORS = []  # a data file that couldn't be read: main() stops with exit 2, and the self-test fails


def _rule_sev():
    """Each rule's severity, from data/rules.jsonl. A bad or missing file is recorded in LOAD_ERRORS (main stops), not hidden."""
    try:
        return {r['id']: r['severity'] for r in load_records() if 'severity' in r}
    except InputError as e:
        LOAD_ERRORS.append(str(e))
        return {}
_SEV = _rule_sev()


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


def cleared(out, p, m, rules):
    """The house check judged this word correct here: a marker that stops the rules channel from reporting it in this paragraph
    (run() drops the marker before returning)."""
    out.append(finding('_cleared', '', p['idx'], m, 'high', rules, sev=3))


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
# a fraction in words stays a word (Blake's answer Q4, November 7, 2026; house rule 2): one-half, two-thirds, a third of, one quarter of.
# A mixed number (one and one-half) is a number, so the code drops a fraction that follows "N and" and the count stays a finding.
_FRAC = r"(?:half|halves|thirds?|quarters?|fourths?|fifths?|sixths?|sevenths?|eighths?|ninths?|tenths?|hundredths?)"
FRACTION_WORD = re.compile(r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten)-" + _FRAC + r"\b|\b(?:a|one)\s+(?:half|third|quarter|fourth|fifth|sixth|seventh|eighth|ninth|tenth|hundredth)(?=\s+of\b)"
                           r"|\b(?:two|three|four|five|six|seven|eight|nine)\s+(?:thirds|quarters|fourths|fifths|sixths|sevenths|eighths|ninths|tenths|hundredths)\b", re.I)
MIXED_NUMBER_LEAD = re.compile(r"\b(?:\d+|" + '|'.join(NUM_WORDS) + r")\s+and\s+$", re.I)  # one and one-half: the fraction is part of a number
# a document's name keeps its ordinal word (Blake's answer Q29, November 7, 2026; house rule 2): the Second Amendment, this second amendment
# (a renewal TERM, period, option or year is a count of periods, not a document's name: the third renewal term stays a finding)
DOC_ORDINAL_NEXT = re.compile(r"[\s-]+(?:amendments?|amended|restatements?|restated|supplements?|supplemental|modifications?|addend(?:um|a)|renewals?(?!\s+(?:terms?|periods?|options?|years?|dates?)\b))\b", re.I)
# to be hired (employed, engaged, retained): a passive to recast every time (Blake's answer Q3, November 7, 2026; house rule 1)
TO_BE_HIRED = re.compile(r"\bto\s+be\s+(hired|employed|engaged|retained)\b", re.I)
HIRE_CONTEXT = re.compile(r"\b(?:solicit\w*|induc\w*|encourag\w*|recruit\w*|entic\w*|hire|employ|employees?|persons?|individuals?|consultants?|contractors?|personnel|staff|"
                          r"officers?|directors?|workers?|managers?|executives?)\b", re.I)  # someone who can be hired, before to be hired
# a warranty of goods in a sale of goods: warrants is the right verb there (MSCD 3.415; 3.453), and it may speak of future performance
GOODS_WARRANTY = re.compile(r"\bwarrants?\s+(?:to\s+[A-Z][\w-]*(?:\s+[A-Z][\w-]*)?\s+)?that\s+(?:the|each|all|any|every)\s+(?:Goods|Products?|Equipment|Units?|Parts?|Components?|Materials?|Merchandise|Inventory|Machines?|Vehicles?|Hardware)\b")
RELATIVE_AGREES = re.compile(r"\b(?!(?:states?|acknowledges?|confirms?|represents?|warrants?|certif(?:y|ies)|understands?|agrees?|provides?|provided|means|requires?|so|such|except)\b)[a-z]+\s+(?:that|which)\s+(?:(?:the|its|each|any)\s+)?[A-Za-z][\w-]*(?:\s+[A-Za-z][\w-]*){0,2}\s+$"
                            r"|\b(?:under|by|in|with|through)\s+which\s+(?:(?:the|its|each|any)\s+)?[A-Za-z][\w-]*(?:\s+[A-Za-z][\w-]*){0,2}\s+$")
PROPER_AFTER = re.compile(r"(?:\s+[A-Z][\w'-]*){0,2}\s+(?:Plaza|Place|Street|St\.|Avenue|Ave\.|Center|Centre|Tower|Towers|Square|Park|Building|Court|Circle|Way|Road|Boulevard|Drive|Lane|Bank|Judicial|Circuit|District|Floor)\b")  # case matters: Two Lattice Plaza is a name; Two bank accounts is a count
FIRST_COUNT = re.compile(r"\bfirst\s+(?:anniversary|day|business day|month|year|quarter|installment|payment|calendar|week|period)\b", re.I)
ORD_RE = re.compile(r"\b((?:twenty|thirty)-)?(second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|thirtieth|hundredth|(?<=-)first)\b", re.I)
CENTS_00 = re.compile(r"\$\d{1,3}(?:,\d{3})+\.00\b|\$\d{4,}\.00\b")  # $1,000.00 and up; the money-small-cents variant covers $2.00 to $999.00 with its nearby-cents exception
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
    ((r"\brepresents?\s+(?:to\s+(?:[A-Z][\w-]*(?:\s+[A-Z][\w-]*)?|the\s+other\s+part(?:y|ies)|each\s+other)\s+)?and\s+warrants?\b|\bwarrants?\s+(?:to\s+(?:[A-Z][\w-]*(?:\s+[A-Z][\w-]*)?|the\s+other\s+part(?:y|ies)|each\s+other)\s+)?and\s+represents?\b"
     r"|\bREPRESENTS?\s+(?:TO\s+(?:[A-Z][\w-]*(?:\s+[A-Z][\w-]*)?|THE\s+OTHER\s+PART(?:Y|IES)|EACH\s+OTHER)\s+)?AND\s+WARRANTS?\b|\bWARRANTS?\s+(?:TO\s+(?:[A-Z][\w-]*(?:\s+[A-Z][\w-]*)?|THE\s+OTHER\s+PART(?:Y|IES)|EACH\s+OTHER)\s+)?AND\s+REPRESENTS?\b"), 'represents-warrants', 2, "represents and warrants: on Blake's draft use states (3.457); on the other side's draft keep it and suggest the remedies-neutral sentence in a comment (3.459-3.463).", ['R-3.457-use-states']),
    (r"\(this\s+[\"“]\*{0,2}[A-Z][a-z]+\*{0,2}[\"”]\)|^[\s*_#]*(?:THIS|This)\s+(?:[\w-]+\s+){0,6}?(?:" + "|".join(N + r"\s+\(the\s+[\"“]\*{0,2}" + n + r"\*{0,2}[\"”]\)" for n in ("Agreement", "Amendment", "Addendum", "Lease", "Sublease", "Note", "Guaranty", "Guarantee", "Release", "License", "Licence", "Deed", "Subcontract", "Contract") for N in (n, n.upper())) + ")", 'this-agreement-term', 3, 'Don\'t define this agreement as a term; delete the definition and write this agreement (or this amendment, this lease) in lowercase throughout (MSCD 2.123).', ['R-2.123-no-this-agreement-term']),
    (r"(?<!\bstays\s)(?<!\bstay\s)(?<!\bremains\s)(?<!\bremain\s)(?<!\bis\s)(?<!\bare\s)(?<!\bbe\s)(?<!\bwas\s)(?<!\bwere\s)\b[Tt]he\s+same\b(?=\s*(?:[,.;:)]|$)|\s+(?:to|by|in|on|at|for|and|or|within|if|when|from|with|under|until|without)\b)", 'same-pronoun', 3, 'same as a pronoun: write it, them or their, or repeat the noun (MSCD 13.760).', ['R-13.760-same-pronoun']),
    (r"\b(?:he or she|she or he|his or her|her or his|him or her|her or him|he/she|she/he|s/he|his/her|him/her|himself or herself|herself or himself|him-?\s?or\s?herself|himself/herself|he, she,? or (?:it|they)|his, her,? or (?:its|their)|him, her,? or (?:it|them))\b", 'singular-they', 2, 'House rule 10: singular they (they, their, them), not he or she.', []),
    (r"\b[Ff]orm\s+(?:of|in)\s+Schedule\s+[A-Z0-9]+\b|\bSCHEDULE\s+[A-Z0-9]+\s*[-–—:]\s*FORM\s+OF\b|\bSchedule\s+[A-Z0-9]+\s*[-–—:]\s*Form\s+of\b", 'attachment-classification', 2, 'A form of document is a stand-alone document, so it belongs in an exhibit (Exhibit 1), not a schedule (house rule 6; MSCD 5.72-5.73).', []),
    (r"\bWHEREAS\b|\bWITNESSETH\b|\bNOW,?\s+THEREFORE\b|\b[Ww]hereas\b", 'archaic', 3, 'Traditional recitals or lead-in: delete WHEREAS, WITNESSETH and NOW, THEREFORE; put any background in plain sentences (MSCD 2.137; 2.165).', ['R-2.137-no-witnesseth', 'R-1.4-no-archaisms']),
    (r"\bgood\s+and\s+valuable\s+consideration\b|\breceipt\s+and\s+sufficiency\s+of\s+which\b", 'archaic', 3, 'Recital of consideration: delete it (MSCD 2.165; 2.188).', ['R-2.188-good-and-valuable']),
    (r"\bIN\s+WITNESS\s+WHEREOF\b|\b[Ii]n\s+[Ww]itness\s+[Ww]hereof\b", 'archaic', 3, "Traditional concluding clause: use MSCD's concluding clause (5.13-5.17).", ['R-5.17-traditional-concluding-clause']),
    # RESOLVED, that at the start of a resolution (Blake's answer Q1, November 7, 2026); "the Board has resolved that dispute" is mid-sentence and stays clear
    (r"(?i)(?:^|(?<=[.;:]\s)|(?<=[.;:]\s\s))[\s#>*_]*(?:(?:be\s+it|further)\s+)?\**resolved\**,?\s+(?:\**further\**,?\s+)?that\b", 'resolved', 3,
     ("RESOLVED, that: in a written consent, drop it and state each action as the board's or the members' own act: The Board approves the Merger Agreement; "
     "The Members authorize the Manager to sign the Lease (Blake's house rule 10, following Adams's later blog over MSCD 3.514)."), ['R-3.514-be-and-hereby-is']),
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
    (r"\b[Ff]rom\s+(?:and\s+including\s+)?" + MONTH + r"\s+\d{1,2},?\s*(?:\d{4}\s+)?(?:to|until|till|through)\s+(?!and\s+including)", 'time-ambiguity', 2, 'from [date] to (through, until) [date]: unclear whether each end date is included. Write starting on November 1, 2027, and ending on March 31, 2028 (MSCD 10.23-10.24; Blake\'s answer Q12).', ['R-10.23-inclusive-exclusive-ambiguity']),
    (r"\b[Bb]etween\s+" + MONTH + r"\s+\d{1,2}(?:,\s*\d{4})?\s+and\s+", 'time-ambiguity', 2, 'between [date] and [date]: unclear whether the end dates are included; say so (MSCD 10.23).', ['R-10.23-inclusive-exclusive-ambiguity']),
    # the adverb and the adjective (prompt written notice); "prompts" (a verb, or a software prompt) and the defined term Prompt stay clear
    (r"\bprompt(?:ly)?\b(?!\s+(?:engineering|template|text|window|box)\b)", 'vagueness', 3, 'prompt (or promptly) is vague, and a court may read it as immediately; state a number of days if timing matters (MSCD 10.114; 7.46-7.47).', ['R-10.114-promptly-equals-immediately']),
    (r"\b(?:[Tt]hird|3rd)[- ][Pp]art(?:y|ies)\b(?![- ][Bb]eneficiar)(?![- ][Ll]ogistics)(?![- ][Aa]dministrator)", 'usage', 3, 'third party: write Person, any Person other than a party, or a defined Nonparty (MSCD 13.875).', ['R-13.875-third-party']),
    # signature_checks exempts this entry inside quoted text (a statute's words), keyed on its rule id
    (r"\b(?:duly\s+)?execut(?:e|es|ed|ing|ion)\b(?!\s+(?i:(?:of\s+)?(?:the\s+|its\s+|their\s+|all\s+|any\s+)?(?:work|services?|tasks?|project|duties|obligations|deliverables|plan|protocol|testing))\b)(?!\s+(?:a|an)\s+(?!copy|counterpart|document|written|separate|new\s+agreement|joinder|release|certificate|deed|note|amendment|instrument)[a-z])", 'archaic', 3, 'execute for signing: write sign (MSCD 5.7).', ['R-5.7-signing-not-executing']),
    (r"\bshall\s+be\s+entitled\s+to\b|\bshall\s+have\s+the\s+right\s+to\b", 'category-shall', 2, 'shall be entitled to / shall have the right to: for discretion write may (MSCD 3.206); if another party owes the thing, state that party\'s duty with shall (3.169; 3.288); is entitled to plus a noun stays only when no party owes it (3.147).', ['R-3.206-use-may']),
    (r"\bshall\s+be\s+(?:governed|construed|interpreted)\s+(?:by|in\s+accordance)\b|\bshall\s+(?:be\s+)?deemed\b|\bshall\s+(?:commence|begin|continue|terminate|expire|end|accrue)\b(?=\s*(?:[,.;:)]|$)|\s+(?:on|at|upon|when|whenever|if|unless|in|until|for|automatically|immediately|with|after|before|no\s+later|as\s+of|and|or|without|by|effective|under|while|once|daily|monthly)\b)|\bshall\s+be\s+(?:effective|valid|binding|void|enforceable|final)\b|\bshall\s+be\s+for\s+(?:a|the)\s+(?:term|period)\b|\bshall\s+be\s+(?:equal\s+to\s+)?(?:\$\s?\d|\d+(?:\.\d+)?\s*(?:%|percent\b))|\bshall\s+(?:remain|be)\s+in\s+(?:full\s+)?(?:force|effect)\b", 'category-shall', 2, 'shall with no duty on the subject: language of policy. Pick the tense by MSCD 3.334: the present tense for a policy in force on signing or at a fixed date (Tennessee law governs this agreement; the Term ends on May 31, 2030); will for a policy tied to an event that may not happen or whose timing is uncertain (this agreement will terminate when ...; will be void) (MSCD 3.98; 3.334; 3.335).', ['R-3.98-shall-future-time']),
]
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
     'shall be liable / shall not be liable: language of policy. In a matrix clause after if, when, or unless, or for a liability that arises only if an event happens, write will be liable (MSCD 3.361; 3.334); for a standing allocation in force on signing (No Member is liable for the Company\'s debts; an exclusion such as Supplier is not liable for any delay that events beyond its control cause), is liable (MSCD 3.98; 3.335).', ['R-3.98-shall-future-time'], 2),
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
        if t[j] == '.' and (ABBREV.search(tail(t, j + 1, ABBREV_REACH)) or re.search(r"(?:^|\s)[A-Z]\.$", tail(t, j + 1, 3))
                            or re.match(r"\d", t[j + 1:j + 2])):
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


# a person who is not a party and acts for one or under one: the subject of No [person] shall that a party must answer for (Blake's answer Q22)
NONPARTY_PERSON = re.compile(r"^(?:(?:[A-Z][\w-]*\s+)?[Uu]sers?|[Ee]nd\s+[Uu]sers?|[Ee]mployees?|[Ss]ub-?contractors?|[Cc]ontractors?|[Ss]ub-?agents?|[Aa]gents?|[Rr]epresentatives?|"
                             r"[Oo]fficers?|[Dd]irectors?|[Pp]ersonnel|[Ss]taff|[Aa]ffiliates?|[Ii]nvitees?|[Gg]uests?|[Vv]isitors?|[Ss]ub-?licensees?|[Cc]onsultants?|[Ww]orkers?|"
                             r"[Tt]echnicians?|[Vv]olunteers?|[Ss]ub-?processors?|[Pp]ermitted\s+[Uu]sers?)$")


def negative_nonparty(words):
    """For the words between a negative word and shall (No Authorized User shall; No employee of Customer shall): (subject, the party
    that answers for it, or [Party]) when the subject is a nonparty person; None for a party (Neither party; No Seller or Affiliate of
    a Seller), a thing (No amendment), or anyone at all (No one)."""
    w = re.sub(r"^\s*(?:of\s+)?(?:the|its|their|his|her|any|such)?\s*", '', words).split(',')[0].strip()  # No Authorized User, during the Term, shall
    if not w or re.match(r"(?:one|body|thing)\b", w, re.I):
        return None
    parties = (PARTY_TERMS or PARTY_DEFAULT) | PARTY_COLLECTIVE | EXHIBIT_PARTIES
    owner = None
    o = re.search(r"\bof\s+(?:the\s+|a\s+|an\s+|any\s+|either\s+|each\s+)?([A-Z][\w-]*(?:\s+[A-Z][\w-]*)?)\b", w) or re.search(r"\b([A-Z][\w-]*)['’]s\b", w)
    if o and o.group(1) in parties:
        owner = o.group(1)
    for part in re.split(r"\s+(?:or|and|nor)\s+", w):
        head = re.split(r"\s+(?:of|for|under|in|at|who|that|with)\s+|['’]s?\s+", part.strip(), maxsplit=1)[0].strip()
        head = re.sub(r"^(?:the|its|their|any|each|a|an)\s+", '', head)
        if head in parties or head.lower() in ('party', 'parties') or not (NONPARTY_PERSON.match(head) or NONPARTY_HEADS.match(head)):
            return None
    return w, owner or '[Party]'


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
                and re.search(r"\b(?:the|each|any|every|an?|all|such|its|their|[A-Z][\w-]*['’]s)\s+$", tail(t, max(t.rfind(subj, 0, m.start()), 0), 80), re.I) \
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
            if re.search(r"\b(?:" + COND_LEAD + r"|when|whether)\b[^,.;:]{0,90}$", tail(t, m.start(), 140), re.I):
                continue  # in a condition, the shall-in-condition check reports it
            check = 'category-shall' if m.group(0).lower().startswith('shall') else 'category-will'
            add(check, msg, m, 'medium', rules, sev=sev if sev_is_free(check, rules) else None)


def passive_checks(t, p, add, out):
    """the passive voice (house rule 1): a passive with no actor, the deemed fiction, and the words that look passive but are not."""
    for m in GOODS_WARRANTY.finditer(t):
        cleared(out, p, m, ['R-3.457-use-states', 'R-13.937-warrants-statement-of-fact', 'R-3.474-no-future-facts', 'R-3.27-throat-clearing', 'R-3.436-verb-not-remedy'])
    for m in re.finditer(r"\bCAN(?=-[A-Z])", t):
        cleared(out, p, m, ['R-3.207-no-can'])  # the CAN-SPAM Act: a statute's name
    seen_verbs = set()
    for m in TO_BE_HIRED.finditer(t):  # Blake's answer Q3 (November 7, 2026): recast every time, with the active form in the message
        lo, _hi = sentence_bounds(t, m.start(), m.end())
        if re.match(r"\s+in\b", t[m.end():]) or not HIRE_CONTEXT.search(t, max(lo, m.start() - 160), m.start()):
            continue  # engaged in the business; records to be retained for 7 years: no hiring, so the general passive check reports it
        seen_verbs.add(m.start(1))
        add('passive-voice', f'To be {m.group(1).lower()}: a passive that hides who does the hiring. Recast it in the active every time: solicit any employee of Company '
            'to accept employment with a competitor (or to work for, or to provide services to, a competitor) (house rule 1; MSCD 3.15).', m, 'high', ['R-3.15-active-voice'])
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
                                   or re.search(r"\b(?:No|Neither|None\s+of)\b[^.;:,]{0,60}$", tail(t, m.start(), 100), re.I) and re.match(r"\s*to\b", t[m.end():])):
            continue  # is not required to: Blake's fixed exception (MSCD 3.292); shall not be required to: the category check reports it
        modal = re.match(r"(?:shall|will|must|may|is\s+to|are\s+to)\b", m.group(0), re.I) or re.search(r"\b(?:shall|will|must|may|is\s+to|are\s+to)\s+(?:not\s+)?(?:\w+ly\s+)?$", tail(t, m.start(), 100), re.I)
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
            elif chk == 'agrees-to' and RELATIVE_AGREES.search(tail(t, m.start(), 120)):
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
        if re.search(r"\bwhether\s+$", tail(t, m.start(), 60), re.I) or re.search(r"\b(?:evaluate|decide|determine|consider|assess|know|ask)s?\s+if\s+$", tail(t, m.start(), 60), re.I):
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
    # a fraction word stays a word (Blake's answer Q4): one-half, two-thirds, a third of; not inside a mixed number (one and one-half)
    frac_spans = [(k.start(), k.end()) for k in FRACTION_WORD.finditer(t) if not MIXED_NUMBER_LEAD.search(t, 0, k.start())]
    keep_spans += frac_spans
    for m in NUM_RE.finditer(t):
        pre = t[max(0, m.start() - 12):m.start()]
        if m.group(0)[0].isupper() and m.start() > 0 and PROPER_AFTER.match(t, m.end()):
            continue  # part of a proper name (Two Lattice Plaza, Fourth Judicial Circuit)
        nxt = re.match(r"\s+([A-Z][\w'’-]*)", t[m.end():])
        if m.group(0)[0].isupper() and nxt and not re.fullmatch(UNIT_WORDS, nxt.group(1), re.I) and not NUM_RE.fullmatch(nxt.group(1)) \
                and not re.search(r"(?:^|[.;:!?]\s+|\n\s*)$", t[:m.start()]):
            continue  # a proper name mid-sentence (Twelve Oaks Mall, One Liberty Plaza)
        if m.group(0)[0].isupper() and nxt and not re.fullmatch(UNIT_WORDS, nxt.group(1), re.I) and (
                re.search(r"\b(?:Address|Attention|Attn\.?|Location|Premises|Property|Street|Office|Located\s+at)\s*:?\s*$", tail(t, m.start(), 60), re.I)
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
        if DOC_ORDINAL_NEXT.match(t, m.end()):
            continue  # a document's name keeps its word (this second amendment; the third restated agreement): Blake's answer Q29 (house rule 2)
        if any(a <= m.start() < b for a, b in frac_spans):
            continue  # a fraction (a third of the Shares, two-thirds): Blake's answer Q4 keeps the word (house rule 2)
        add('ordinal-word', 'Ordinal word; if it counts something, write it in digits (2nd, 3rd).', m, 'low')
    for m in _WD_PAREN.finditer(t):
        start, w = words_before(t, m.start())
        if start is None:
            continue
        span = _Span(t, start, m.end())
        if FRACTION_WORD.fullmatch(t[start:m.start()].strip()):
            add('words-and-digits', f'A fraction in words with digits after it ({span.group(0).strip()}): state it once. House rule 2 keeps a fraction as a word, so delete the digits '
                f'in parentheses and keep {t[start:m.start()].strip()} (Blake\'s answer Q4; MSCD 14.5-14.11).', span, 'high', ['R-14.5-words-and-digits'])
        else:
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
        if ABBREV.search(tail(t, m.start() + 1, ABBREV_REACH)) or re.search(r"(?:^|\W)[A-Z]\.$", tail(t, m.start() + 1, 3)):
            continue
        before = t[:m.start() + 1]  # the whole prefix: the enumerator test below reads all of it
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
        if re.search(r"\b(?:nor|and|or)\s+$", tail(t, m.start(), 40)) or in_quotation(t, m.start()):
            continue  # a compound subject that includes a party (neither Buyer nor its agents shall): other checks cover it; quoted text keeps its verbs
        add('nonparty-obligation', 'Shall with a nonparty subject: a contract binds only its parties, so this duty binds no one. Restructure so the party has the duty (Consultant shall enter into a confidentiality agreement with each of its employees), or use must for the nonparty (MSCD 3.89; 3.166). Don\'t write shall cause, shall require or shall ensure for employees or other nonparties the party doesn\'t control (MSCD 3.162-3.163); keep shall cause for a party\'s instrumentality, such as a wholly owned subsidiary (3.160).', m, 'high', ['R-3.89-shall-duty'])
    seen_policy = set()
    party_words = {w.lower() for w in (PARTY_TERMS or PARTY_DEFAULT) | PARTY_COLLECTIVE}
    for rx in (CONTINGENT_LEAD, CONTINGENT_TAIL, CONTINGENT_REL):
        for m in rx.finditer(t):
            span = (m.start('verb'), m.end('verb'))  # the present-tense policy verb
            if span in seen_policy or re.search(r"\b(?:shall|will|may|must|to|that|which|who)\s+$", tail(t, span[0], 40)) or in_quotation(t, span[0]):
                continue  # a modal before the verb, or a relative clause (the amount that becomes due after ...), or quoted text
            if rx is CONTINGENT_TAIL and re.search(r"\b(?:before|after|until|when|whenever|if|unless|once|while|as\s+long\s+as|so\s+long\s+as|the\s+day|the\s+date)\s+(?:[\w'’-]+\s+){0,5}$", tail(t, m.start(), 160)):
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
                after = t[m.end('verb'):m.end('verb') + 140]
                if heads & (party_words | PERSONISH | {'employee', 'employees', 'executive', 'user', 'users', 'staff', 'personnel'}) \
                        or re.search(r"\b(?:of|for|to|in|on|at|by|with|without|under|about|regarding|concerning|from|into|than|and|or|nor)\s+$", tail(t, m.start('subj'), 40)) \
                        or re.match(r"(?:(?!,\s+(?:and|but|or)\b)[^.;]){0,140}?\b(?:if|when|whenever|unless|upon|once|after|before|until)\s+"
                                    r"(?!(?:" + MONTH + r"|the\s+(?:date|day)\s+of\s+this|\d))", after) is None:
                    continue
            seen_policy.add(span)
            add('category-will', 'Present tense for a policy about a contingent future event: MSCD 3.334 and 3.361 take will (this agreement will terminate; the termination will take effect). Keep the present tense for a policy that applies now or at a fixed date.', _Span(t, span[0], span[1]), 'medium', ['R-3.334-policy-will-contingent'])
    for m in NEG_SUBJ_SHALL.finditer(t):
        if re.match(r"\s*that\s+no\b", m.group(0), re.I) and re.search(r"\b(?:is|are|was|were|has|have|exists?|remains?|occurs?)\b", m.group(0), re.I):
            continue  # shall ensure that no Hazardous Materials are stored ... and shall indemnify: the 2nd shall keeps its own subject
        np_subj = negative_nonparty(t[m.end(1):m.end() - len('shall')])
        if np_subj:
            # Blake's answer Q22 (November 7, 2026): a nonparty subject (No Authorized User shall) gets a party as the subject, never No Authorized User may
            subj, owner = np_subj
            add('negative-subject-shall', f'Shall with a negative subject that is a nonparty ({subj}): it reads as an absence of duty, and "No {subj} may" would bind no one either, '
                f'because the contract binds only its parties (house rule 8; MSCD 3.324; 3.89). Restructure so a party is the subject, in 2 parts (MSCD 3.180; 8.5): '
                f'{owner} shall use reasonable efforts to prevent any {subj} from that conduct, and {owner} is liable for any loss that results if a {subj} nevertheless engages in it. '
                f'Write {owner} shall cause ... only when the {subj} is {owner}\'s instrumentality (its subsidiary or its own board; MSCD 3.160-3.161), because {owner} can\'t '
                f'guarantee what its employees, users, or contractors do (3.163).', m, 'high',
                ['R-3.323-collective-noun-prohibition', 'R-3.165-restructure-nonparty', 'R-3.176-prevent-undesirable-events'])
            continue
        add('negative-subject-shall', 'Shall with a negative subject reads as absence of duty, not prohibition (MSCD 3.324; house rule 8). For a prohibition on a party, use "Neither party may" or "No [person] may". When the subject is not a person (No amendment shall be effective, No failure shall operate as a waiver), it is language of policy about an event that may never happen, so it takes will (No amendment of this agreement will be effective unless ...; A failure to exercise a right will not waive it) (MSCD 3.334; 3.369); the present tense fits only a policy in force on signing or at a fixed date.', m, 'high', ['R-3.323-collective-noun-prohibition'])
    for m in SHOULD.finditer(t):
        # house rule 12: should never appears in Blake's contracts, whatever its sense; each finding gives the replacement
        if re.match(r"should\s+(?:reasonably\s+)?(?:have\s+known|know)\b", t[m.start():], re.I):
            add('should', 'Should have known: house rule 12 (no should) applies, but the words set a legal knowledge standard, so don\'t pick a '
                'replacement: offer a defined Knowledge term with wording for actual knowledge and for knowledge after reasonable inquiry '
                '(MSCD 13.506: whose knowledge counts), and ask Blake which.', m, 'high', ['R-13.506-define-knowledge'], sev=2)
            continue
        if re.search(r"\b(?:[Ii]f|[Uu]nless|[Uu]ntil|[Ii]n the event(?: that)?|[Ee]ven if|[Ww]hether)\b[^,.;:]{0,90}$", tail(t, m.start(), 140)):
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
        if any(r.start() <= m.start() < r.end() for r in REF_PASSIVE.finditer(t)):
            continue  # set forth in the section titled "Payment": stated in would be a reduced passive too (Blake's answer Q32); the reduced-passive finding gives the fix
        add('wordy-phrase', f'Wordy: use {WORDY[m.group(1).lower()]} (17.19).', m, 'high', ['R-17.19-wordy-phrases'])
    for m in PROVISO.finditer(t):
        add('provided-that', 'Provided that: state the relationship directly with except that, and in any event, on condition that, or a separate sentence (13.698-13.701).', m, 'high', sev=1)


# a verb of saying or choosing right before which: an embedded question, where which is a question word, not a relative pronoun
EMBEDDED_QUESTION = re.compile(r"\b(?:specif(?:y|ies|ying)|determin(?:e|es|ing)|stat(?:e|es|ing)|indicat(?:e|es|ing)|identif(?:y|ies|ying)|designat(?:e|es|ing)|"
                               r"decid(?:e|es|ing)|select(?:s|ing)?|choos(?:e|es|ing)|elect(?:s|ing)?|say(?:s|ing)?|confirm(?:s|ing)?|know(?:s|ing)?|ask(?:s|ing)?|"
                               r"(?:notify|notifies|tell|tells|inform|informs)\s+[\w'’-]+)\s*$", re.I)
# a reduced passive that points at a heading or the introductory clause: (as) stated in the section titled "Payment"; the date stated in the
# introductory clause. Blake's answers Q32 and Q24 (November 7, 2026) flag every one (the old exemption for as stated in is gone).
REF_PASSIVE = re.compile(r"\b(?P<lead>as\s+|in\s+the\s+manner\s+)?(?P<part>stated|described|set\s+forth|set\s+out|specified|listed)\s+in\s+the\s+"
                         r"(?:(?P<kind>section|article|clause|paragraph)s?\s+(?P<tw>titled|entitled|captioned|headed)\b(?:\s*[\"“](?P<title>[^\"”\n]{1,80})[\"”])?|(?P<intro>introductory\s+clause)\b)", re.I)
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
                                                         r"near|past|since|onto|unto|despite|except|like|upon|until|of\s+all|each\s+of|any\s+of|all\s+of|some\s+of|none\s+of)\s*$", tail(t, m.start(), 60), re.I):
                continue  # a preposition before which (the period during which): which is right there
            if chk == 'restrictive-which' and re.search(r"[,(]\s*$", tail(t, m.start(), 60)):
                continue  # a comma or a parenthesis before which, with 2 spaces or a line break between: nonrestrictive
            if chk == 'restrictive-which' and EMBEDDED_QUESTION.search(tail(t, m.start(), 80)):
                continue  # an embedded question (Buyer shall specify which Units it wants): which is a question word, and that would be wrong
            if chk == 'shall-in-condition' and re.match(r"until\b[^,.;:]{0,60}?\s+and\s+shall\b", m.group(0), re.I):
                continue  # "shall insure the Equipment until the Closing and shall name Seller": until ends the 1st duty; the 2nd shall is a new duty
            if chk == 'attachment-scheme' and re.match(r"[\w.]*\s+(?:of|to|in|under)\s+(?:the\s+)?(?:[A-Z][\w-]+\s+){1,3}(?:Agreement|Lease|Note|Plan|Indenture|Guaranty|Declaration|Credit\s+Agreement)\b", t[m.end():]):
                continue  # Schedule 2 of the Services Agreement: another agreement's own label, kept as it is (house rule 4's other-agreement default)
            if chk == 'such-pointing' and re.match(r"[^.;\"\u201c]{0,60}?,\s+(?:a|an|the|each|any)\s+\**[\"\u201c]", t[m.end():]):
                continue  # an integrated definition (each such consent, a "Required Consent"): correct (MSCD 6.74)
            if chk in ('is-entitled-to', 'category-may') and re.search(r"\b(?:states?|represents?|warrants?|acknowledges?|confirms?)(?:\s+and\s+\w+)?\s+(?:to\s+\w+\s+)?that\b[^.;]{0,120}$", tail(t, m.start(), 200), re.I):
                continue  # a statement of fact that a party has a right (Seller states that it is entitled to sell the Assets)
            if chk == 'is-entitled-to' and ENTITLED_NOT_OWED.match(t, m.end()):
                # no party owes it (the entire condemnation award; benefits under the Company 401(k) Plan): a trigger for the analysis passes, not a finding
                out.append(finding(chk, msg, p['idx'], m, 'low', rules, source='rules'))
                continue
            if chk == 'reduced-passive' and re.search(r"\b(?:divided|multiplied|reduced|increased|offset|rounded|adjusted)\s+by\b", m.group(0), re.I):
                continue  # arithmetic (the Valuation Cap divided by the Fully Diluted Capitalization), not a passive that hides an actor
            if chk == 'reduced-passive':
                noun = m.group(0).split()[1]
                if noun in (PARTY_TERMS or PARTY_DEFAULT) or noun.lower() in ('parties', 'party') or re.search(r"\b(?:that|which|who|whom)\s+$", tail(t, m.start(), 40)):
                    continue  # "that the Company provided to": an active relative clause, not a reduced passive
                if any(r.start() < m.end() and m.start() < r.end() for r in REF_PASSIVE.finditer(t)):
                    continue  # stated in the section titled "Payment"; the date stated in the introductory clause: the check below reports it with its active form
            add(chk, msg, m, 'medium', rules, sev=sev if sev_is_free(chk, rules) else None)
    # Blake's answers Q32 and Q24 (November 7, 2026): every stated (described, set forth, set out, specified, listed) in the section titled ..., including
    # as stated in, is a reduced passive (house rule 1); house rule 4's form of a reference by heading is under the section titled "Payment"
    for r in REF_PASSIVE.finditer(t):
        part = re.sub(r"\s+", ' ', r.group('part').lower())
        verb = {'stated': 'states', 'described': 'describes', 'specified': 'specifies', 'listed': 'lists'}.get(part, 'states')
        where = 'the introductory clause' if r.group('intro') else f'the {r.group("kind").lower()} {r.group("tw").lower()} "{(r.group("title") or "Payment").rstrip(".,")}"'
        if r.group('lead'):  # as stated in; in the manner stated in
            fix = (f'as {where} states' if r.group('intro') else f'under {where}')
            msg = (f'Reduced passive ({r.group(0).strip()}). Write {fix} (house rule 1; house rule 4\'s form of a reference by heading; Blake\'s answer '
                   f'{"Q24" if r.group("intro") else "Q32"}).')
        else:
            np_m = re.search(r"\b((?:the|each|any|all|every|a|an|its|their|such|this|that)\s+(?:[\w'’-]+\s+){0,3}?[\w'’-]+)\s*$", tail(t, r.start(), 120), re.I)
            np = np_m.group(1) if np_m else '[the thing]'
            msg = (f'Reduced passive ({np} {part} in {where}). Recast it in the active: {np} that {where} {verb} (house rule 1; '
                   f'Blake\'s answer {"Q24" if r.group("intro") else "Q32"}).')
        add('reduced-passive', msg, r, 'high', ['R-3.15-active-voice'])
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
        if lead and int(lead.group(1)) >= 100 or re.search(r"(?:C\.F\.R\.|U\.S\.C\.|Code|Regulations?|Act|Rule|Ann\.|Stat\.|Statutes|Regs?\.)\s*$", tail(t, m.start(), 60)) \
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
        if m.group(0).lower() in ('above', 'below') and (re.search(r"\b(?:at|or|is|are|falls?|drops?|rises?|goes|prices?|amounts?|rates?|levels?|costs?|values?|sales|revenues?|temperatures?|grades?|percentages?|figures?)\s+(?:or\s+)?$", tail(t, m.start(), 60), re.I)
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


# a deadline on a stated date (no later than June 30, 2027; by June 30; on or before June 30, 2027), and the words that make it decide a right
# (Blake's answer Q7, November 7, 2026): such a deadline always states a time of day and a time zone (MSCD 10.33-10.34)
DEADLINE_DATE = re.compile(r"\b(?:[Nn][Oo][Tt]?\s+[Ll][Aa][Tt][Ee][Rr]\s+[Tt][Hh][Aa][Nn]|[Bb][Yy]|[Oo][Nn]\s+[Oo][Rr]\s+[Bb][Ee][Ff][Oo][Rr][Ee])\s+(?:the\s+end\s+of\s+)?"
                           + MONTH + r"\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s*\d{4})?\b")
DECIDES_RIGHT = re.compile(r"\b(?:exercis(?:e|es|ed|ing)|options?|cur(?:e|es|ed|ing)|terminat(?:e|es|ed|ing|ion)|renew(?:s|ed|al|als)?|elect(?:s|ed|ion)?|notice\s+of)\b", re.I)
TIME_STATED = re.compile(r"\b\d{1,2}(?::\d{2})?\s*(?:a\.m\.|p\.m\.|am\b|pm\b)|\b(?:midnight|noon)\b|\b(?:close|end|start|opening)\s+of\s+business\b", re.I)


def date_checks(t, p, add, out):
    """dates (house rule 7), a weekday that does not match its date, a deadline that decides a right, a termination-notice period, and the headings clause."""
    for m in DEADLINE_DATE.finditer(t):
        lo, hi = sentence_bounds(t, m.start(), m.end())
        if TIME_STATED.search(t, lo, hi) or not DECIDES_RIGHT.search(t, lo, hi):
            continue  # a time of day is stated; or the deadline decides no right (Lender shall fund the Loan no later than March 1, 2027)
        add('time-of-day', f'A deadline that decides a right ({m.group(0)}) with no time of day: the right could end at the start of that day or at its end. '
            'State the time and the time zone: no later than 5:00 p.m. Eastern time on June 30, 2027 (MSCD 10.33-10.34; Blake\'s answer Q7; house rule 7).', m, 'medium', ['R-10.33-state-time-of-day'])
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
CONSPICUOUS = re.compile(r"\b(?:DISCLAIM\w*|WARRANT\w*|MERCHANTABILITY|FITNESS|AS\s+IS|LIABILITY|CONSEQUENTIAL|NEGLIGENCE|JURY|ARBITRAT\w*)\b")
# Blake's answer Q2 (November 7, 2026; house rule 9): a clause that law, regulation, case law, or leading practice requires to be conspicuous is
# bold, 14-point type (the 1 exception to 12-point Aptos), never capitals or underlining, with an initial line for each party directly under it
CONSPICUOUS_CLAUSE = re.compile(r"\b(?P<jury>jury|JURY|Jury)\b|(?P<asis>\bAS[\s-]+IS\b|[\"“]as[\s-]+is[\"”]|\bas-is\b)|\b(?i:(?P<merch>merchantability|fitness\s+for\s+a\s+particular)|"
                                r"(?P<conseq>consequential)|(?P<arb>arbitrat\w*)|(?P<renew>automatic(?:ally)?\s+renew\w*)|(?P<release>unknown\s+claims|section\s+1542))\b")
CONSPICUOUS_KIND = {'jury': 'a jury waiver', 'asis': 'a warranty disclaimer', 'merch': 'a warranty disclaimer', 'conseq': 'a limitation of liability or remedies',
                    'arb': 'an arbitration clause', 'renew': 'an automatic-renewal term', 'release': 'a release of unknown claims'}
CONSPICUOUS_SIZE = 14  # points
INITIAL_LINE = re.compile(r"\bInitials?\b", re.I)
CONSPICUOUS_FORM = ('house rule 9 formats a clause that law, regulation, case law, or leading practice requires to be conspicuous in bold, 14-point type '
                    '(the 1 exception to 12-point Aptos), never in capitals or underlined, with an initial line for each party directly under it: '
                    'Initials: ________ [Party] ________ [Party] (Blake\'s answer Q2)')


def conspicuous_kind(t):
    """The kind of conspicuous clause a paragraph holds (a jury waiver, a warranty disclaimer, ...), or None."""
    m = CONSPICUOUS_CLAUSE.search(t)
    return CONSPICUOUS_KIND[m.lastgroup] if m else None


def conspicuous_checks(paras):
    """.docx only (the formatting is known): a conspicuous-type clause whose text isn't bold or isn't 14 point, and a missing initial line
    (house rule 9; Blake's answer Q2). A clause in all capitals is the capitals-body finding's; a heading line (under 8 words) is skipped.
    Consecutive paragraphs of 1 kind are 1 clause: 1 finding on its 1st paragraph."""
    out, prev = [], (None, None)
    body = [p for p in paras if p['text'].strip()]
    for n, p in enumerate(body):
        t, f = p['text'], p.get('fmt') or {}
        kind = conspicuous_kind(t) if 'fonts' in f and p.get('where') in ('body', 'table') else None
        if not kind or len(t.split()) < CAPS_BODY_WORDS or t == t.upper():
            prev = (None, None)
            continue
        if prev == (kind, n - 1):
            prev = (kind, n)
            continue  # the same clause's next paragraph
        prev = (kind, n)
        chars = len(re.sub(r"\s", '', t))
        bold = len(re.sub(r"\s", '', f.get('bold_text', ''))) >= 0.9 * chars
        sizes = f.get('sizes') or []
        big = bool(sizes) and all(abs(s - CONSPICUOUS_SIZE) < 0.01 for s in sizes)
        problems = ([] if bold else ['its text is not bold']) + ([] if big else [f'its type is {", ".join(f"{s:g}" for s in sizes)} point, not 14' if sizes else 'its type size is not 14 point'])
        after = ' '.join(q['text'] for q in body[n + 1:n + 3])
        initials = bool(INITIAL_LINE.search(t[-200:]) or INITIAL_LINE.search(after))
        if not problems and initials:
            continue
        if problems:
            msg = (f'Conspicuous clause ({kind}): {CONSPICUOUS_FORM}. Here {" and ".join(problems)}.' +
                   ('' if initials else ' There is no initial line under it (severity 3 on its own): add one.') +
                   ' Confirm that the clause needs to be conspicuous; if a statute prescribes a different form, Blake decides.')
        else:
            msg = f'Conspicuous clause ({kind}) in bold, 14-point type with no initial line under it: add Initials: ________ [Party] ________ [Party] directly under it (house rule 9; Blake\'s answer Q2).'
        out.append(finding('conspicuous-format', msg, p['idx'], _Span(t, 0, min(len(t), MATCH_CUT)), 'medium', ['R-16.18-caps-headings-names'], sev=2 if problems else 3))
    return out


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
    # 14 point is right for a conspicuous clause (house rule 9's 1 exception; Blake's answer Q2)
    bad_sizes = [s for s in f.get('sizes', []) if off_house_size(s) and not (abs(s - CONSPICUOUS_SIZE) < 0.01 and conspicuous_kind(t))]
    if bad_sizes:
        add('font-size', f'Font size {", ".join(map(str, bad_sizes))} pt; house rule is 12 point.', None, 'medium')
    if len(t.split()) >= CAPS_BODY_WORDS and t == t.upper() and re.search(r"[A-Z]", t) and not CAPS_HEADING.match(t):
        if CONSPICUOUS.search(t):
            # a conspicuous clause in capitals (a disclaimer, a limitation, a jury waiver): Blake's answer Q2 makes it a direct finding with the house form
            add('capitals-body', f'A conspicuous clause in all capitals (a warranty disclaimer, a limitation of liability, a jury waiver): {CONSPICUOUS_FORM}. '
                'Put the text in sentence case (MSCD 16.18-16.19). If a statute prescribes a different form, Blake decides.',
                _Span(t, 0, min(len(t), MATCH_CUT)), 'medium', ['R-16.18-caps-headings-names'], sev=2)
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

# ---------------------------------------------------------------- document-level checks

def term_of_art_checks(paras, defs):
    """House rule 13: a term of art of contract law keeps its legal meaning. Reports a defined term built on a term of art
    that names something else (an Assignment that is a work order), and an ordinary word used in another sense
    (marketing collateral), at severity 1 when the contract also uses the word in its legal sense. defs: definitions(paras)."""
    out = []
    full = '\n'.join(p['text'] for p in paras)
    defined_lower = {d.term.lower() for d in defs}
    for e in terms_of_art():
        rx = e['rx']
        legal_here = bool(rx['legal_use'] and rx['legal_use'].search(full))
        sev = 1 if legal_here else 2
        both = f' The contract also uses {e["id"]} in its legal sense, so 1 word carries 2 meanings.' if legal_here else ''
        for term, deftext, pidx, st, en, _kind, _lead in defs:
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

    # numbered definitions (1. "Affiliate" means ...) keep their form: house rule 3's scheme governs the outline only (Blake's answer Q23, November 7, 2026)
    enumerated = [(p, m) for p in paras for m in [ENUM_RE.match(labeled(p))] if m and p.get('where') == 'body' and not AUTON.match(labeled(p)[m.end(1):])]
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
             and ENUM_RE.match(p['text']) and not AUTON.match(p['text'][ENUM_RE.match(p['text']).end(1):])]
    if len(typed) >= 3 and not auto:
        # Blake's answer Q10 (November 7, 2026): native numbering only in a document Blake drafts; a redline keeps the document's numbering, noted once
        lead = f'{len(typed)} paragraphs have numbers typed into the text.'
        if WHOSE == 'blake':
            tail = ' In a document Blake drafts, use Word\'s native multilevel numbering, so numbers update when provisions move; in a redline of an existing document, keep its numbering (house rule 3; Blake\'s answer Q10).'
        elif WHOSE == 'other-side':
            tail = ' In a redline of an existing document, keep its typed numbering; this note is for Blake\'s information (house rule 3; Blake\'s answer Q10).'
        else:
            tail = ' Convert to Word\'s native multilevel numbering only in a document Blake drafts; in a redline of an existing document, keep its typed numbering (house rule 3; Blake\'s answer Q10).'
        out.append(finding('typed-numbering', lead + tail, typed[0]['idx'], match=ENUM_RE.match(typed[0]['text']).group(1)))
    def add_outline(idx, msg, m):
        if idx in auto:
            msg += ' (Word automatic numbering: the number is in the list definition, not the text.)'
        out.append(finding('enumeration', msg, idx, rules=['R-4.11-article-numerals'], match=m.group(1),
                           start=-1 if idx in auto else m.start(1), end=-1 if idx in auto else m.end(1)))
    if not items:
        return out
    first_dec = next((it for it in items if it[2] == 'decimal'), None)
    if first_dec:
        add_outline(first_dec[0], 'Decimal numbering (1.1, 1.1(a)); house rule 3 uses I. (articles), A. (sections), 1. (subsections), (a), (i).', first_dec[4])
    other = next((it for it in items if it[2] == 'other'), None)
    if other:
        add_outline(other[0], f'Enumerator {other[3]}; house rule 3 uses (a) for clauses and (i) for subclauses.', other[4])
    kinds = {it[2] for it in items}
    if 'digit' in kinds and not kinds & {'letter', 'roman'} and not first_dec:
        it = next(it for it in items if it[2] == 'digit')
        add_outline(it[0], 'Top-level sections numbered 1., 2.; house rule 3 numbers sections A., B. (under articles I., II.), and keeps 1. for subsections.', it[4])
    # only child: a level that has a 1st item but no 2nd before its parent level moves on. An article may hold a single section
    # (a Definitions article with only A.): Blake's answer Q15 (November 7, 2026) keeps no-only-child from reaching it
    starts = {}
    seq = [it for it in items if it[1] < LVL_OTHER]
    lone_section_ok = lambda first: first[1] == LVL_SECTION and first[2] == 'letter' and any(it[2] == 'roman' for it in seq)
    for n, it in enumerate(seq):
        _idx, lvl, kind, tok, m = it
        for deeper in [k for k in list(starts) if k > lvl]:
            first, count = starts.pop(deeper)
            if count == 1 and not lone_section_ok(first):
                add_outline(first[0], f'Only child: {first[3]} has no sibling at its level (house rule 3).', first[4])
        if lvl in starts and starts[lvl][0][2] == kind:
            starts[lvl] = (starts[lvl][0], starts[lvl][1] + 1)
        else:
            starts[lvl] = (it, 1)
    for lvl, (first, count) in starts.items():
        if count == 1 and lvl > min(it[1] for it in seq) and not lone_section_ok(first):
            add_outline(first[0], f'Only child: {first[3]} has no sibling at its level (house rule 3).', first[4])
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


EFFORTS_STD = re.compile(r"\b((?:commercially\s+|all\s+|every\s+|very\s+)?reasonable(?:\s+best|\s+commercial)?|best|good[- ]faith|diligent)\s+(?:efforts|endeavou?rs)\b", re.I)


# a definition that names an entity: Acme Widgets, Inc., a Tennessee corporation; Dana Ruiz, an individual; Acme Holdings LLC
ENTITY_NAMED = re.compile(r"\s*(?:means\s+)?[A-Z][\w.&'’-]*(?:,?\s+[A-Z][\w.&'’-]*){0,6}?,?\s+(?:" + ENTITY + r"\s*,?\s*)?(?:a|an)\s+(?:[A-Z][\w-]*\s+)?"
                          r"(?:corporation|company|partnership|limited\s+liability\s+company|limited\s+partnership|trust|association|bank|credit\s+union|individual)\b"
                          r"|\s*(?:means\s+)?[A-Z][\w.&'’-]*(?:,?\s+[A-Z][\w.&'’-]*){0,6}?,?\s+" + ENTITY + r"(?=[\s.,;]|$)")


def party_term_caps_checks(paras, defs):
    """MSCD 2.96: no all capitals for a party-name defined term ("ACME" means Acme Widgets, Inc., a Tennessee corporation; ACME WIDGETS, INC.,
    a Tennessee corporation ("ACME")). An acronym with another kind of definition ("SOW" means a statement of work) stays. defs: definitions(paras)."""
    out = []
    for term, words, pidx, st, en, kind, _lead in defs:
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

    def add_mismatch(p, start, end, match, msg):
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
                add_mismatch(p, m.start(), m.end(), m.group(0), f'The {name} is stated as {_usd(amounts[name][0])} and as {_usd(cents)}.')
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
                    add_mismatch(p, m.start(), m.end() + more.end(), m.group(0) + more.group(0),
                        f'The {len(parts)} installments listed add to {_usd(sum(parts))}{count_note}; the total is {_usd(total)}.')
                spans.append((m.start(), m.end() + more.end()))
                continue
            if n * each != total:
                add_mismatch(p, m.start(), m.end(), m.group(0), f'{n} installments of {_usd(each)} make {_usd(n * each)}, not {_usd(total)}.')
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
                add_mismatch(p, m.start(), m.end(), m.group(0), f'{pct}% of {_usd(base)} is {_usd(int(computed))}, not {_usd(stated)}.')
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
                add_mismatch(p, m.start(), m.end(), m.group(0), f'{n} payments of {_usd(each)} make {_usd(n * each)}, not {_usd(total)}.')
        # 4. an annual total restated as a per-period amount: the annual Fees are $84,000, payable as $7,000 each month (12 months);
        # a rate alone ($7,000 per month) or 2 unrelated amounts in 1 sentence ($84,000 ... a $500 deposit each month) are left alone
        for m in re.finditer(r"\b(?:annual|yearly|per\s+year|a\s+year|each\s+year)\b[^.;$]{0,60}?" + MONEY + r"[^.;$]{0,80}?\b(?:as|in|(?:installments|payments)\s+of)\s+" + MONEY
                             + r"\s+(?:on\s+the\s+(?:\d+(?:st|nd|rd|th)|first|last)\s+(?:business\s+)?day\s+of\s+)?(?:per|each|a|every)\s+(?:calendar\s+)?(month|quarter|week)\b", t, re.I):
            total, each = _money(m), _money(m, 4)
            periods = {'month': 12, 'quarter': 4, 'week': 52}[m.group(7).lower()]
            if None not in (each, total) and periods * each != total and not NOT_A_TOTAL.search(m.group(0)):
                add_mismatch(p, m.start(), m.end(), m.group(0), f'{periods} {m.group(7).lower()}ly payments of {_usd(each)} make {_usd(periods * each)}, not the annual {_usd(total)}.')
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
            body = body.removesuffix('|')
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


STATUTE_TEXT = re.compile(r"\b(?:disclosure|notice|statement|legend|warning|language|text|wording)\s+(?:that|which)\s+[^.:]{0,160}?\b(?:requires?|mandates?|prescribes?)\s*:"
                          r"|\b(?:disclosure|notice|statement|legend|warning|language|text|wording)\s+(?:required|mandated|prescribed)\s+by\s+[^.:]{0,160}?:", re.I)
# a signature block: a By: line, IN WITNESS, a Signature: line, or a signature line (underscores) with Name:, Title: or Date: beside it
SIG_LINE = re.compile(r"^[\s*_]*(?:By|BY)\s*:|(?i:\bin\s+witness\b)|^[\s*_]*(?i:(?:authorized\s+)?signature)\s*:", re.M)
SIG_RULE = re.compile(r"_{5,}")
SIG_LABEL = re.compile(r"^[\s*_]*(?:Name|Title|Date|NAME|TITLE|DATE)\s*:", re.M)


def has_signature_block(ps):
    """True when these paragraphs hold a signature block."""
    for n, q in enumerate(ps):
        if SIG_LINE.search(q['text']):
            return True
        if SIG_RULE.search(q['text']) and any(SIG_LABEL.search(x['text']) for x in ps[n:n + 3]):
            return True
    return False


def signed_schedules(paras):
    """{heading paragraph idx: heading text} for each schedule (or annex, or appendix) that holds its own signature block: a stand-alone
    document, so an exhibit under house rule 6 (Blake's answer Q13, November 7, 2026). Only when the body before the 1st attachment has a
    signature block of its own: otherwise the block after a schedule may be the contract's."""
    heads = [n for n, p in enumerate(paras) if EXHIBIT_HEAD.match(p['text'])]
    if not heads or not has_signature_block(paras[:heads[0]]):
        return {}
    out = {}
    for k, a in enumerate(heads):
        head = paras[a]['text']
        if not SCHED_HEAD.match(head) or EXH_HEAD_ONLY.match(head):
            continue
        if has_signature_block(paras[a + 1:(heads[k + 1] if k + 1 < len(heads) else len(paras))]):
            out[paras[a]['idx']] = head
    return out


def attachment_classification_checks(paras, findings):
    """A schedule that holds a signature block is a stand-alone document: label it an exhibit (house rule 6; Blake's answer Q13)."""
    out = []
    for idx, head in signed_schedules(paras).items():
        if any(f['check'] == 'attachment-classification' and f['para'] == idx for f in findings):
            continue  # SCHEDULE A - FORM OF ...: the form-of finding already says it
        m = SCHED_HEAD.match(head)
        label = re.sub(r"[\s#*_]+", ' ', m.group(0)).strip()
        out.append(finding('attachment-classification', f'{label} holds its own signature block, so it is a stand-alone document: label it an exhibit (Exhibit 1, numbered), '
                           'even though the draft calls it a schedule, and update every reference to it (house rule 6; Blake\'s answer Q13; MSCD 5.72-5.73).',
                           idx, m, 'high', [], sev=2))
    return out


def schedule_section_checks(paras):
    """MSCD 5.93: a schedule holds information, not contract sections. A duty (shall) or a prohibition in a schedule
    is a provision that belongs in the body; an exhibit (a stand-alone form) has its own provisions and is skipped, and so is
    a schedule that holds its own signature block (a stand-alone document that attachment-classification relabels: Blake's answer Q13)."""
    out, in_sched, done = [], False, False
    signed = signed_schedules(paras)
    for p in paras:
        t = p['text']
        if EXHIBIT_HEAD.match(t):
            in_sched, done = bool(SCHED_HEAD.match(t)) and not EXH_HEAD_ONLY.match(t) and p['idx'] not in signed, False
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


# a party name in the introductory clause: before ", a Delaware corporation" or before its defined-term parenthetical
INTRO_NAME = re.compile(r"(?:between|and|;)\s+([A-Z][\w.&'’ -]{1,60}?(?:,?\s+" + ENTITY + r")?)(?=,\s+(?:a|an)\s+|\s*\()")


def front_checks(paras, meta, shape, defs):
    """The front and the definitions: title (2.2), party names in capitals (2.51), lead-in (2.159), bold defined terms (2.92).
    shape: document_shape(paras); defs: definitions(paras)."""
    out = []
    def add_front(check, msg, p, m=None, rules=()):
        out.append(finding(check, msg, p['idx'] if p else -1, m, rules=rules, cut=80))
    body = [p for p in paras if p['text'].strip()]
    if not body:
        return out
    legend = re.compile(r"^[#\s*_\[(]*(?:[\w&.,'’ -]{0,60}\s)?(?:draft|DRAFT|Draft)\b[^\n]{0,60}$|^[#\s*_\[(]*(?:confidential|privileged|for discussion|execution (?:copy|version))\b", re.I)
    while len(body) > 1 and legend.search(re.sub(r"[*_\])]+$", '', body[0]['text'].strip())) and len(body[0]['text'].split()) <= 12:
        body = body[1:]  # a draft legend or a confidentiality legend above the title (Halvorsen draft of February 10, 2027) isn't the title
    title = body[0]
    tt = re.sub(r"^[#\s*_]+|[*_]+$", '', title['text']).strip()
    # a sentence is not a title: a pasted clause (Neither party may assign this agreement.) ends in a stop or holds a modal
    if 2 <= len(tt.split()) <= 10 and not re.search(r"\b(?:between|dated|is|are|shall|may|will|must)\b", tt, re.I) and not re.search(r"[.;:]$", tt):
        if tt != tt.upper():
            add_front('front', 'Title: put it in all capitals (MSCD 2.2).', title, None, ['R-2.2-title-format'])
        if 'centered' in (title.get('fmt') or {}) and not title['fmt']['centered']:
            add_front('front', 'Title: center it at the top of the 1st page (MSCD 2.2).', title, None, ['R-2.2-title-format'])
    letter = any(re.match(r"\s*(?:Dear|To)\s+[A-Z]", p['text']) for p in body[:12]) or any(re.search(r"\bthis letter agreement\b", p['text'], re.I) for p in body[:6])
    # a letter agreement has no introductory clause (MSCD 19.3-19.9); otherwise the shape's intro, or an early between-clause with a parenthetical
    by_idx = {p['idx']: p for p in paras}
    intro = None if letter else by_idx.get(shape['intro']) if shape['intro'] is not None else next((p for p in body[:6] if BETWEEN_AMONG.search(p['text']) and re.search(r"\(", p['text'])), None)
    if intro:
        for m in INTRO_NAME.finditer(intro['text']):
            name = m.group(1)
            if name != name.upper() and not re.fullmatch(r"(?:the\s+)?\w+", name) and not re.search(r"[a-z][A-Z]", name):
                add_front('front', f'Introductory clause: state the party name in all capitals ({name.upper()}) (MSCD 2.51).', intro, m, ['R-2.51-names-in-capitals'])
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
                add_front('front', f'Signature block: "{m.group(1)}" differs from the name in the introductory clause; use the exact legal name in both, and confirm which is correct (MSCD 2.50; 5.29).', p, m, ['R-2.50-full-names', 'R-5.29-entity-name-caps'])
        if not any(LEAD_IN.search(p['text']) for p in body):
            add_front('front', 'No lead-in: add "The parties agree as follows:" after the introductory clause (MSCD 2.159).', intro, None, ['R-2.159-lead-in'])
    unbolded, bold_quotes = [], []
    for term, _words, pidx, st, en, _kind, _lead in defs:
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
        add_front('bold-definition', f'Defined term not in bold where it is defined ({len(unbolded)} definitions, integrated and autonomous); bold the term, not the quotation marks (MSCD 2.92; 6.31).', p, m, ['R-2.92-party-term-format', 'R-6.31-quote-and-bold'])
    if bold_quotes:
        p, m = bold_quotes[0]
        add_front('bold-definition', f'Quotation marks in bold around {len(bold_quotes)} defined terms; bold the term only (MSCD 2.92; 6.31).', p, m, ['R-6.31-quote-and-bold'])
    return out

# ---------------------------------------------------------------- rule-database triggers

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

IMPORTS = re.compile(r"[Cc]apitalized terms?\b[^.]{0,120}\b(?:have|has|given)\b[^.]{0,40}\bmeanings?\b[^.]{0,80}\b(?:in|that)\b", re.I)
CONTRACT_NOUN = re.compile(r"\b(?:(?:Disclosing|Receiving|Indemnifying|Indemnified|Defaulting|Nondefaulting|Non-Defaulting|Breaching|Nonbreaching|Non-Breaching|Terminating|Notifying|Requesting|Affected|Prevailing|Paying) Party|Information|Agreement|Date|Period|Price|Assets?|Software|Services?|Products?|Effect|Event|Change|Claims?|Losses|Fees?|Rent|Term|Territory|Data|Materials|Property|Rights|Work|Deliverables?|Documentation|Units?|Shares|Amount|Account|Plan|Certificate|Statement|Orders?|Budget|Report|Specifications|Equipment|Goods|Premises|Interest|Payment|Expenses|Release|Cause|Reason|Disability|Control|Default|Closing|Obligations|Liabilities|Approval|Notice|Days?|Hours|Year|Month|Quarter|Representatives|Affiliates?|Subsidiar(?:y|ies)|Indemnitees?|Liens?|Taxes|Personnel|Permits|Contracts|Persons?|Members?|Shareholders?|Stockholders?|Partners?|Ratios?|Manuals?|Lists?|Users?|Transferees?|Holders?|Standards?|Levels?|Tests?|Milestones?|Deposits?|Securities|Index|Environment|Credits?|Commitments?|Percentages?|Completion|Guarant(?:y|ee)|Warrant(?:y|ies)|Polic(?:y|ies)|Schedule|"
                           r"Assistance|Targets?|Criteria|Indicators?|Window|Region|Review|Process|Procedures?|Program|Threshold|Objectives?)\b")


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
        by_para[d.para].append(d)
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
            here = {d.term for d in by_para[p['idx']]}
            exhibit_defs.update(here)
            for d in by_para[p['idx']]:
                exhibit_where.setdefault(d.term, []).append(('exhibit', d.para, d.start))
            if in_form:
                for term_ in here:
                    form_defs.setdefault(term_, att_label)
            continue
        for d in by_para[p['idx']]:
            # a pointer ("Renewal Term" has the meaning that the section titled "Term" gives it) indexes a definition made elsewhere (MSCD 6.99)
            defs.setdefault(d.term, []).append(('integrated' if d.kind == 'sentence' else d.kind, d.para, d.start))
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
    lead_of = {d.para: d.lead for d in all_defs if d.lead}  # each paragraph's leading autonomous definition, which definitions() matches once
    for p in paras:
        dm = lead_of.get(p['idx'])
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
    for term, words, pidx, st, en, kind, _lead in all_defs:
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
                  and p['idx'] not in lead_of and p.get('where') not in ('header', 'footer')
                  and not re.search(r"\bis\s+between\b|\bis\s+made\b.{0,80}\bbetween\b", p['text'][:300])]  # body provisions only: a definition and the introductory clause use the generic words
    for term in [t for t in defs if ' ' in t and t[0].isupper()]:
        rx = re.compile(r"(?<![\w-])" + re.escape(term.lower()) + r"(?![\w-])")
        hit = next(((p, x) for p in body_paras for x in rx.finditer(p['text'])
                    if not re.search(r"\b(?:as|in\s+(?:its|that|the)\s+(?:role|capacity)\s+as)\s+(?:the\s+|an?\s+)?$", tail(p['text'], x.start(), 80))
                    and not (re.search(r"\bthis\s+$", tail(p['text'], x.start(), 40)) and re.search(r"(?:Order|Agreement|Amendment|Addendum|Statement\s+of\s+Work|Lease|Note|Release)$", term))
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
    groups.append(('Rule triggers to check in the analysis passes (1 line per rule, with every paragraph it matched; severity is the rule\'s, if the problem is confirmed; most triggers in a clean draft are not problems)', triggers))
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



# ---------------------------------------------------------------- running the lint

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
    findings += term_of_art_checks(paras, defs)
    findings += schedule_section_checks(paras)
    findings += attachment_classification_checks(paras, findings)
    findings += conspicuous_checks(paras)
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


def main():
    ap = ArgParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('path', nargs='?')
    ap.add_argument('--json', help='also write findings as JSON to this path')
    ap.add_argument('--inventory', action='store_true')
    ap.add_argument('--whose', choices=['blake', 'other-side'], help="whose draft it is; tailors the represents-and-warrants finding")
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        from _lint_tests import self_test  # the test suite is a module of its own; a lint never imports it
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
