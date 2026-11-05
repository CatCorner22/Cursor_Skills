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
Exit codes: 0 ok, 2 unreadable input, 5 bad usage.
"""
import argparse, collections, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- reading the document

def read_paragraphs(path):
    """Return a list of dicts: idx, text, where (body/table), style, and docx formatting facts."""
    ext = os.path.splitext(path)[1].lower()
    paras = []
    if ext == '.docx':
        import docx  # python-docx
        d = docx.Document(path)
        def add(p, where):
            fmt = {}
            try:
                if p.alignment is not None and int(p.alignment) == 3:
                    fmt['justified'] = True
            except (TypeError, ValueError):
                pass
            fonts, sizes, underline = set(), set(), False
            for r in p.runs:
                if r.font.underline:
                    underline = True
                if r.font.name: fonts.add(r.font.name)
                if r.font.size: sizes.add(r.font.size.pt)
            fmt.update({'fonts': sorted(fonts), 'sizes': sorted(sizes), 'underline': underline,
                        'auto_numbered': p._p.pPr is not None and p._p.pPr.numPr is not None})
            from docx.oxml.ns import qn
            text = ''.join(el.text or '' if el.tag == qn('w:t') else '\t' if el.tag == qn('w:tab') else '\n'
                           for el in p._p.iter(qn('w:t'), qn('w:tab'), qn('w:br')))  # includes inserted text, skips deleted text
            paras.append({'idx': len(paras), 'text': text, 'where': where,
                          'style': p.style.name if p.style is not None else '', 'fmt': fmt})
        for p in d.paragraphs:
            add(p, 'body')
        for t in d.tables:
            for row in t.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        add(p, 'table')
        try:
            st = d.styles['Normal'].font
            paras_meta = {'normal_font': st.name, 'normal_size': st.size.pt if st.size else None}
        except KeyError:
            paras_meta = {}
        from docx.oxml.ns import qn
        body = d.element.body
        if body.find('.//' + qn('w:ins')) is not None or body.find('.//' + qn('w:del')) is not None:
            paras_meta['tracked_changes'] = True  # text is read as if every change were accepted
        return paras, paras_meta
    if ext not in ('.txt', '.md', ''):
        raise ValueError(f'unsupported file type {ext}: convert it to .docx or .txt first (for a PDF, extract its text)')
    text = open(path, encoding='utf-8', errors='replace').read()
    for block in re.split(r'\n\s*\n|\n(?=\s*(?:[IVX]+\.|[A-Z]\.|\d+\.|\([a-z]{1,3}\))\s)', text):
        if block.strip():
            paras.append({'idx': len(paras), 'text': block.strip('\n'), 'where': 'body', 'style': '', 'fmt': {}})
    return paras, {}

# ---------------------------------------------------------------- house-style checks

BE = r"(?:am|is|are|was|were|be|been|being)"
IRREG = ("made|paid|given|taken|held|sold|bought|sent|kept|done|known|shown|told|brought|found|left|met|put|set|"
         "laid|led|lent|lost|meant|read|run|seen|spent|won|written|borne|begun|chosen|drawn|driven|forgotten|"
         "frozen|hidden|ridden|shaken|spoken|stolen|sworn|thrown|undertaken|withdrawn|withheld|forgiven|"
         "granted|bound|built|caught|cut|dealt|fed|felt|fought|got|gotten|heard|hit|hung|hurt|let|"
         "overcome|paid|proven|quit|shut|sought|split|spread|struck|taught|thought|understood|upheld|wound")
NOT_PASSIVE = set("""void voidable effective liable entitled responsible able unable subject due payable eligible
 bound obligated aware available necessary sufficient deemed? concerned interested located based
 married divorced incorporated organized licensed qualified authorized registered dated""".split())
PASSIVE_RE = re.compile(rf"\b{BE}\s+(?:not\s+|also\s+|hereby\s+|then\s+|thereby\s+|so\s+|each\s+|jointly\s+|severally\s+|fully\s+|promptly\s+){{0,3}}((?:\w+ed)|(?:{IRREG}))\b", re.I)
MODAL_BE = re.compile(rf"\b(?:shall|will|may|must|would|should|could|might|can)\s+(?:not\s+)?(?:be|have been)\s+(?:\w+ly\s+)?((?:\w+ed)|(?:{IRREG}))\b", re.I)

NUM_WORDS = ("one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen "
             "eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand").split()
NUM_RE = re.compile(r"\b(" + "|".join(NUM_WORDS) + r")(?:-(" + "|".join(NUM_WORDS) + r"))?\b", re.I)
ONE_WORD = re.compile(r"\b(?:no one|one another|any one time|each one|the one(?=\s+(?:that|who|which|whom)\b)|one-(?!(?:half|third|quarter|fourth|fifth|tenth|hundredth)\b)[a-z]+)", re.I)  # pronoun or part of a word: keep
ONE_COUNT = re.compile(r"\b(?:one or more|one or both|any one|one of|one side|one party)\b", re.I)  # counts something: digit
FIRST_COUNT = re.compile(r"\bfirst\s+(?:anniversary|day|business day|month|year|quarter|installment|payment|calendar|week|period)\b", re.I)
ORD_RE = re.compile(r"\b(second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|twentieth|thirtieth)\b", re.I)
WORDS_DIGITS = re.compile(r"\b[a-z][a-z\- ]{2,40}\s*\(\s*\$?\d[\d,\.]*\s*%?\)", re.I)
ABBREV = re.compile(r"(?:\b(?:Inc|Ltd|Co|Corp|No|Nos|Mr|Ms|Mrs|Dr|St|Jr|Sr|U\.S|e\.g|i\.e|v|vs|etc|L\.L\.C|L\.P|N\.A|Sec|Art|p|pp|a\.m|p\.m)\.)$")
ONE_SPACE = re.compile(r"([.?!][\"”’)]?) (?=[A-Z“\"(])")
TWO_AFTER_COLON = re.compile(r":  +\S")
NEG_SUBJ_SHALL = re.compile(r"(?:^|[.;:]\s+|,\s+(?:and|or|but)\s+|\b(?:that|and|or|but)\s+)(Neither|No|None of|Nobody|No one|Nothing)\b(?!\s+(?:later|earlier|more|less|fewer|sooner)\s+than)[^.;:,]{0,60}?\bshall\b(?!\s+not)", re.I)
SHOULD = re.compile(r"\bshould\b", re.I)
ONCE = re.compile(r"\bonce\b", re.I)
WHEN_COND = re.compile(r"(?:^|[.;:]\s+|\(\w{1,4}\)\s+)When\b")
AMP = re.compile(r"&")
XREF = re.compile(r"\b(?:[Ss]ections?|[Aa]rticles?|[Cc]lauses?|[Pp]aragraphs?|[Ss]ubsections?|§)\s*(?:[IVXLC]+|\d+)(?:[.-][\dA-Za-z]+)*(?:\s*\([a-z0-9]{1,4}\))*(?![\w.-]*(?:\s*\([a-z0-9]{1,4}\))*\s+of\s+(?:the\s+)?(?:[A-Z]|\d+\s+U\.S\.C|title))")
REL_XREF = re.compile(r"\b(?:above|below|the foregoing|hereof|hereunder|herein|hereinafter|aforesaid)\b", re.I)
ATT_LOWER = re.compile(r"\b(schedule|exhibit|annex|appendix)\s+(?:[A-Z]\b|\d+\b)")
ATT_HERETO = re.compile(r"\b(?:Schedules?|Exhibits?|schedules?|exhibits?)\b[^.;]{0,40}?\b(?:hereto|attached hereto|to this [Aa]greement)\b|\battached hereto\b")
ATT_ON = re.compile(r"\bon (?:Schedule|schedule)\s+[A-Z0-9]")
ATT_PART = re.compile(r"\b(?:form(?:s|ing)?|constitut(?:e|es|ing)|made)\s+(?:a\s+|an\s+)?(?:integral\s+)?part of this [Aa]greement|\bincorporated (?:herein )?by reference\b", re.I)
ATT_QUOTE = re.compile(r"\b(?:Schedule|Exhibit)\s+[\"“][A-Z0-9]+[\"”]")
DMY = re.compile(r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b")
NUMDATE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
THIS_DAY = re.compile(r"\bthis\s+\S+\s+day\s+of\b", re.I)
HEADINGS_CLAUSE = re.compile(r"\bheadings?\b[^.]{0,120}\b(?:convenience|reference)\b", re.I)
TYPED_NUM = re.compile(r"^\s*(?:\d+\.\d+(?:\.\d+)*\.?|\(\d+\)|\([ivx]+\)|\([a-z]\)|[IVX]+\.|[A-Z]\.|\d+\.)\s+")


# House rule 11: no article before a defined party name (MSCD 2.105 and 6.63 differ).
PARTY_DEFAULT = {'Company', 'Buyer', 'Seller', 'Purchaser', 'Supplier', 'Vendor', 'Contractor', 'Subcontractor', 'Consultant',
                 'Customer', 'Client', 'Employee', 'Executive', 'Employer', 'Licensor', 'Licensee', 'Landlord', 'Tenant', 'Lender',
                 'Borrower', 'Guarantor', 'Provider', 'Sponsor', 'University', 'Hotel', 'Distributor', 'Manufacturer'}  # role labels keep the (house rule 11)
PARTY_TERMS = set()  # run() fills this from the document's own party definitions
NOT_PARTY = {'Agreement', 'Effective Date', 'Parties', 'Party'}
DEF_PAREN = re.compile(r"\(\s*(?:the\s+|a\s+|an\s+)?[\"\u201c]\**([A-Z][\w-]*(?:\s+[A-Z][\w-]*){0,2})\**[\"\u201d]\s*\)")
ROLE_DEF = re.compile(r"[\"\u201c]((?:Disclosing|Receiving|Indemnifying|Indemnified|Defaulting|Nondefaulting|Terminating|Notifying) Party)[\"\u201d]")
ATTRIBUTIVE = ('employee|employees|board|stock|shares|securities|plan|plans|group|products|product|property|personnel|policy|policies|'
               'entity|entities|subsidiary|subsidiaries|affiliate|affiliates|premises|facility|facilities|data|information|account|'
               'accounts|system|systems|site|sites|benefit|benefits|parties|party|representative|representatives|indemnitees')
DEF_WITH_ARTICLE = re.compile(r"\(\s*the\s+[\"\u201c]\**([A-Z][\w-]*(?:\s+[A-Z][\w-]*){0,2})\**[\"\u201d]\s*\)")


def party_terms(paras):
    found = set()
    for p in paras[:15]:
        if re.search(r"\bbetween\b", p['text'], re.I):
            found |= {m.group(1) for m in DEF_PAREN.finditer(p['text'])}
    return {t for t in found if t not in NOT_PARTY and not ROLE_DEF.fullmatch('"' + t + '"')}


def party_article_re(terms):
    alts = '|'.join(sorted(map(re.escape, terms), key=len, reverse=True))
    return re.compile(r"\b[Tt]he\s+(" + alts + r")\b(?!\s+[A-Z])(?!\s+(?:" + ATTRIBUTIVE + r")\b)")


TOA = 'Term of art used in its everyday sense; the contract may also use it in its legal sense, and one word should carry one meaning (MSCD 1.57). '

EXTRA = [
    (re.compile(r"\bsuch\b(?!\s+as\b)(?=\s+[A-Za-z])", re.I), 'such-pointing', 3, 'Such as a pointing word: use the, this, that, these or those (13.816-13.818); keep such only for "of this kind".', []),
    (re.compile(r"(?<![,(])(?<!\b(?:in|on|of|to|by|at))(?<!\bfor)(?<!\b(?:from|with|upon|into))(?<!\b(?:under|after))(?<!\bthrough)\s+which\b(?!\s+(?:is|are)\s+(?:not\s+)?(?:a|an|the)\b)"), 'restrictive-which', 2, 'Which without a comma introduces a restrictive clause: use that (12.44; 12.53-12.56).', []),
    (re.compile(r"\b(?:if|unless|until|in the event)\b[^,.;:]{0,90}?\bshall\b", re.I), 'shall-in-condition', 1, 'Shall in a conditional clause: use the present tense (3.358-3.360).', ['R-3.358-conditional-present-tense']),
    (re.compile(r"\b(?:is|are|shall be|will be)\s+entitled to\b", re.I), 'is-entitled-to', 2, 'Is entitled to: if it hides another party\'s duty, state the duty with shall (3.168-3.171; 3.288-3.291); for discretion use may (3.206).', ['R-3.169-no-is-entitled-to-obligation']),
    (re.compile(r"\b(?:Attachment|Appendix|Annex|Addendum)\s+(?:[A-Z]|\d+)\b"), 'generic-attachment-label', 2, 'Generic attachment label. House rule: Schedule A (lettered; information the body refers to, such as lists and disclosures) or Exhibit 1 (numbered; a stand-alone document, such as a form of agreement). Decide which it is and update every reference (MSCD 5.72-5.74; attachments.md).', ['R-5.74-generic-attachment-term']),
    (re.compile(r"\bExhibit\s+[A-Z]\b(?!\.)"), 'attachment-scheme', 2, 'Lettered exhibit. House rule 6: exhibits take numbers (Exhibit 1), schedules take letters (Schedule A); relabel and update every reference (MSCD 5.80-5.83 differs).', []),
    (re.compile(r"\bSchedules?\s+\d+(?:\.\d+)*\b"), 'attachment-scheme', 2, 'Numbered schedule. House rule 6: schedules take letters (Schedule A), exhibits take numbers (Exhibit 1); relabel and update every reference (MSCD 5.80-5.83 differs).', []),
    (re.compile(r"\b(?:[Tt]he|[Aa]ny|[Ee]ach|[Aa]ll|[Ee]very|[Aa]n?)\s+(?:[A-Z][\w-]*|[a-z]+)\s+(?:given|paid|made|sent|delivered|received|issued|provided|described|specified|listed|referred|contemplated|required|owned|held|granted|incurred|used|stated|set forth|identified|included|attached|signed)\s+(?:by|under|in|to|on|at|for|pursuant|with|as|before|after)\b(?<!made for)"), 'reduced-passive', 3, 'Possible reduced passive (a past participle after a noun, short for "that is given ..."). House rule 1: recast in the active if a clean form exists ("the notice that Acme gives under ..."); otherwise leave it.', ['R-3.15-active-voice']),
    # Terms of art used in their everyday sense: an elaboration of MSCD 1.57 (one word, one meaning). Idea suggested by a file Blake supplied; patterns written fresh.
    (re.compile(r"\bexecut(?:e|es|ed|ing)\s+(?:the\s+|its\s+|their\s+|all\s+|any\s+)?(?:work|services?|tasks?|project|duties|obligations|deliverables|plan|protocol|testing)\b", re.I), 'term-of-art', 2, TOA + 'Execute here means perform; write perform. For signing, MSCD uses sign, not execute (5.7).', ['R-1.57-one-word-one-meaning', 'R-5.7-signing-not-executing']),
    (re.compile(r"\b(?:[Ii]f|[Ww]hen|[Oo]nce|[Aa]fter|[Uu]nless|[Uu]ntil)\s+(?:the\s+)?(?:[A-Z][\w-]+|either party|a party|any party|it|they)\s+notices\b"), 'term-of-art', 3, TOA + 'Notices here means observes, but notice is the formal communication under the notices provision. Write discovers or becomes aware of.', ['R-1.57-one-word-one-meaning']),
    (re.compile(r"\b(?:circumstances|conditions|results|events|volumes?)\s+warrant\b|\bwarrants?\s+(?:additional|further|immediate|special|extra)\b", re.I), 'term-of-art', 3, TOA + 'Warrant here means justify; write justify or require.', ['R-1.57-one-word-one-meaning']),
    (re.compile(r"\brepresent(?:s|ed)?\s+(?:approximately\s+|about\s+)?\d+(?:\.\d+)?\s*(?:%|percent)", re.I), 'term-of-art', 3, TOA + 'Represents here means constitutes; write is, equals or constitutes.', ['R-1.57-one-word-one-meaning']),
    (re.compile(r"\b(?:work|project|job|task|new|each)\s+assignments?\b|\bassign(?:s|ed|ing)?\s+(?:\d+\s+)?(?:qualified\s+|licensed\s+|certified\s+)?(?:personnel|staff|employees|technicians|workers|consultants|individuals|a team)\b", re.I), 'term-of-art', 2, TOA + 'Assign here means allocate work or staff, but assignment is the transfer of rights that an assignment provision restricts. Write designate, task, or work order.', ['R-1.57-one-word-one-meaning']),
    (re.compile(r"\bfor\s+(?:the\s+)?(?:[A-Z][\w-]*['\u2019]s|its|their|further|careful|prompt)\s+consideration\b|\bunder consideration\b|\btake\s+into\s+consideration\b", re.I), 'term-of-art', 3, TOA + 'Consideration here means review, but consideration is also the bargained-for exchange. Write review or evaluation.', ['R-1.57-one-word-one-meaning']),
    (re.compile(r"\brelease\s+(?:the\s+)?(?:payment|funds)\b", re.I), 'term-of-art', 3, TOA + 'Release here means pay, but release is also the giving up of claims. Write pay or disburse (escrow agreements conventionally say release; keep it there).', ['R-1.57-one-word-one-meaning']),
    (re.compile(r"\b(?:strategic|business|vendor|preferred|trusted|channel|campus)\s+partners?\b", re.I), 'term-of-art', 2, TOA + 'Partner can suggest a legal partnership. Name the actual relationship (contractor, supplier, collaborator).', ['R-1.57-one-word-one-meaning']),
]

WORDY = {  # MSCD 17.19 table (Wordy -> Better); "once" dropped from "at the time that" per the once/if rider
    'at that point in time': 'then', 'at the place where': 'where', 'at the time at which': 'when', 'at the time that': 'when',
    'at the time when': 'when', 'by means of': 'by', 'by reason of': 'because of', 'by virtue of the fact that': 'because',
    'commensurate with': 'equal to, appropriate for', 'despite the fact that': 'although', 'due to the fact that': 'because',
    'during such time as': 'while, during', 'during the course of': 'while', 'following the conclusion of': 'after',
    'for the purpose of': 'to [verb]', 'in combination with': 'with', 'in furtherance of': 'furthering, to advance',
    'in lieu of': 'instead of', 'in order for': 'so', 'in order that': 'so', 'in order to': 'to', 'in the course of': 'while, during',
    'in the event of': 'if', 'in the event that': 'if', 'is binding upon': 'binds', 'is unable to': 'cannot', 'per annum': 'a year, per year, annually',
    'period of time': 'period, time', 'previous to': 'before', 'prior to': 'before', 'pursuant to': 'under, in accordance with, authorized by',
    'set forth in': 'stated in, in', 'subsequent to': 'after', 'under the provisions of': 'under', 'until such time as': 'until',
    'with the exception of': 'except for'}
WORDY_RE = re.compile(r"\b(" + '|'.join(re.escape(k) for k in sorted(WORDY, key=len, reverse=True)) + r")\b", re.I)
PROVISO = re.compile(r"\bprovided,?\s+(?:however|further|also)?,?\s*that\b|\bprovided\s+that\b", re.I)

STOP = set('shall will may must if and or the a an any each all every which such before after date day days within '
           'notice party parties agreement section article clause in on of to for by with as that this these those '
           'is are be been being not no including include includes means term terms closing'.split())


def phrase_rules(compiled_ids):
    """Second trigger channel: literal trigger words from the database (for rules whose regex misses them)."""
    recs = [json.loads(l) for l in open(os.path.join(ROOT, 'data', 'rules.jsonl'), encoding='utf-8') if l.strip()]
    ov = json.load(open(os.path.join(ROOT, 'data', 'house-overrides.json'), encoding='utf-8'))
    superseded = {rid for o in ov['overrides'] if not o.get('partial') for rid in o['rule_ids']}
    out = []
    for r in recs:
        if r['status'] == 'proposal' or r['id'] in superseded:
            continue
        words = [w.strip().lower() for w in (r.get('trigger') or {}).get('words') or [] if w and '...' not in w and '[' not in w]
        words = [w for w in words if (' ' in w and not all(x in STOP for x in w.split())) or (len(w) > 5 and w not in STOP)]
        if words:
            out.append((r, re.compile(r"\b(?:" + '|'.join(re.escape(w) for w in sorted(set(words), key=len, reverse=True)) + r")\b", re.I)))
    return out


def sentences(text):
    return [s for s in re.split(r"(?<=[.?!])\s+(?=[A-Z“\"(])", text) if s.strip()]


def house_checks(p):
    t = p['text']; out = []
    def add(check, sev, msg, m=None, conf='high', rules=()):
        out.append({'check': check, 'severity': sev, 'para': p['idx'], 'match': (m.group(0) if m else '')[:120],
                    'message': msg, 'confidence': conf, 'rule_ids': list(rules), 'source': 'house'})
    seen_verbs = set()
    for m in list(PASSIVE_RE.finditer(t)) + list(MODAL_BE.finditer(t)):
        word = m.group(1).lower()
        if word in NOT_PASSIVE or word.rstrip('?') in NOT_PASSIVE or m.start(1) in seen_verbs:
            continue
        seen_verbs.add(m.start(1))  # one flag per participle, even when both patterns match it
        if word == 'required' and re.search(r'\bnot\s+required\s+to\b', m.group(0) + t[m.end():m.end() + 4], re.I):
            continue  # is not required to: Blake's fixed exception (MSCD 3.292)
        add('passive-voice', 2, 'Possible passive voice; house rule is active voice only. Name the actor (house-style.md section 1).', m,
            'medium', ['R-3.15-active-voice'])
    terms = PARTY_TERMS or PARTY_DEFAULT
    for m in party_article_re(terms).finditer(t):
        if t[max(0, m.start() - 1):m.start()] == '"' or t[max(0, m.start() - 1):m.start()] == '\u201c':
            continue
        add('party-article', 3, f'House rule 11: no article before a defined party name. Write {m.group(1)}, not the {m.group(1)} (MSCD 2.105 differs).', m,
            'medium', ['R-2.105-definite-article'])
    for m in DEF_WITH_ARTICLE.finditer(t):
        if m.group(1) in terms:
            add('party-article', 3, f'House rule 11: a party-name definition takes no article: ("{m.group(1)}") (MSCD 6.63 differs).', m, 'high', ['R-6.63-article-in-parenthetical'])
    keep_spans = [(k.start(), k.end()) for k in ONE_WORD.finditer(t)]
    count_spans = [(k.start(), k.end()) for k in ONE_COUNT.finditer(t)]
    for m in NUM_RE.finditer(t):
        pre = t[max(0, m.start() - 12):m.start()]
        if any(a <= m.start() < b for a, b in keep_spans):
            continue  # one as a pronoun or part of a word (no one, one another, one-time): house rule 2 keeps the word
        if any(a <= m.start() < b for a, b in count_spans):
            add('number-word', 2, 'One counts something here (one or more, one of, one party): write 1 (house rule 2; keep one only as a pronoun or part of a word, such as no one, one another, one-time).', m, 'high', ['R-14.15-words-then-digits'])
        elif not re.search(r"\d\s*$", pre):
            add('number-word', 2, 'Spelled-out number; house rule is digits for every number (house-style.md section 2).', m, 'high', ['R-14.15-words-then-digits'])
    for m in FIRST_COUNT.finditer(t):
        add('ordinal-word', 2, 'First counts something here: write 1st (house rule 2). Keep fixed terms such as right of first refusal.', m, 'medium')
    for m in ORD_RE.finditer(t):
        if m.group(0)[0].isupper() and re.match(r"\s+[A-Z]", t[m.end():m.end() + 2]):
            continue  # part of a proper name (500 Third Avenue, Fifth Third Bank)
        add('ordinal-word', 3, 'Ordinal word; if it counts something, write it in digits (2nd, 3rd).', m, 'low')
    for m in WORDS_DIGITS.finditer(t):
        if NUM_RE.search(m.group(0)):
            add('words-and-digits', 2, 'Words and digits together; use digits only (MSCD 14.5-14.11; house rule).', m, 'high', ['R-14.5-words-and-digits'])
    for m in ONE_SPACE.finditer(t):
        before = t[:m.start() + 1]
        if ABBREV.search(before) or re.search(r"\b[A-Z]\.$", before):
            continue
        if re.fullmatch(r"\s*(?:[IVXLC]+|[A-Za-z]|\d+(?:\.\d+)*|\([a-z0-9]+\))\.", before):
            continue  # a typed enumerator at the start of the paragraph, not a sentence end
        add('spacing', 3, 'One space after a sentence; house rule is two spaces between sentences.', m, 'high', ['R-16.44-one-space'])
    for m in TWO_AFTER_COLON.finditer(t):
        add('spacing', 3, 'Two spaces after a colon; house rule is one space after a colon.', m, 'high')
    for m in NEG_SUBJ_SHALL.finditer(t):
        add('negative-subject-shall', 1, 'Shall with a negative subject reads as absence of duty, not prohibition (MSCD 3.324; house rule). Use "Neither party may" or "No X may".', m,
            'high', ['R-3.323-collective-noun-prohibition'])
    for m in SHOULD.finditer(t):
        if re.match(r"should\s+(?:reasonably\s+)?(?:have\s+known|know)\b", t[m.start():], re.I):
            add('should', 2, 'Should have known: a legal knowledge standard, not the modal of obligation, so changing the words can change the standard. Don\'t rewrite it; flag it and offer a defined Knowledge term (MSCD 13.506: whose knowledge, and actual knowledge or knowledge after inquiry) for Blake\'s decision.', m, 'high', ['R-13.506-define-knowledge'])
            continue
        add('should', 1, 'Should: never in a contract. In a condition write the present tense; for a duty use shall; for advice use recommends (3.360; blog).', m, 'high')
    for m in ONCE.finditer(t):
        add('once', 2, 'Once: use if to introduce a condition, or delete once before an adjective phrase (rider, 2025).', m, 'medium', ['R-rider-once-if'])
    for m in WHEN_COND.finditer(t):
        add('when-condition', 3, 'When at the start of a clause: if it introduces a condition, use if (rider).', m, 'low', ['R-rider-once-if'])
    for m in WORDY_RE.finditer(t):
        add('wordy-phrase', 3, f'Wordy: use {WORDY[m.group(1).lower()]} (17.19).', m, 'high', ['R-17.19-wordy-phrases'])
    for m in PROVISO.finditer(t):
        add('provided-that', 1, 'Provided that: state the relationship directly with except that, and in any event, on condition that, or a separate sentence (13.698-13.701).', m, 'high')
    for rx, chk, sev, msg, rules in EXTRA:
        for m in rx.finditer(t):
            add(chk, sev, msg, m, 'medium', rules)
    for m in AMP.finditer(t):
        add('ampersand', 3, 'Ampersand: keep only inside a business or law-firm name; otherwise and (rider).', m, 'medium', ['R-rider-ampersand'])
    for m in XREF.finditer(t):
        add('numbered-cross-reference', 2, 'Numbered cross-reference; house rule: avoid cross-references, and refer by heading where one is needed (house-style.md section 4).', m,
            'high', ['R-4.100-crossref-name-and-number'])
    for m in REL_XREF.finditer(t):
        add('contract-reference', 2, 'Here-word or above/below reference: ambiguous contract reference (7.23-7.27); name the provision by heading.', m, 'high')
    for m in ATT_LOWER.finditer(t):
        add('attachment-capitals', 3, 'Attachment reference in lowercase; house rule is Schedule A, Exhibit 2.', m, 'high')
    for rx, msg in ((ATT_HERETO, 'Drop hereto / attached hereto / to this agreement from attachment references (5.77).'),
                    (ATT_ON, 'Say in Schedule X, not on Schedule X (5.95).'),
                    (ATT_PART, 'Don\'t say an attachment forms part of the agreement or is incorporated by reference (5.96-5.99; 13.408-13.414).'),
                    (ATT_QUOTE, 'No quotation marks around an attachment designation (5.78).')):
        for m in rx.finditer(t):
            add('attachments', 2, msg, m, 'high')
    if re.search(r"\b(Schedule|Exhibit|schedule|exhibit)s?\b", t):
        add('attachment-check', 3, 'Attachment mentioned: confirm schedule-versus-exhibit classification, order and references (attachments.md).', None, 'low')
    for m in DMY.finditer(t):
        add('date-format', 3, 'Day-month-year date; house rule is the U.S. form (January 1, 2027).', m, 'high', ['R-10.7-day-month-year'])
    for m in NUMDATE.finditer(t):
        add('date-format', 2, 'Numerical date; write January 1, 2027 (10.13; house rule).', m, 'high')
    for m in THIS_DAY.finditer(t):
        add('date-format', 3, 'Archaic date form (this __ day of); write January 1, 2027 (10.11).', m, 'high')
    for m in HEADINGS_CLAUSE.finditer(t):
        add('headings-clause', 2, 'Headings-for-convenience clause: if the contract refers to provisions by heading, delete or limit it (15.18; house rule).', m, 'medium', ['R-15.18-rule-headings'])
    f = p.get('fmt') or {}
    if f.get('justified'):
        add('justified', 3, 'Justified paragraph; use ragged right (16.16-16.17; clean visual lines).', None, 'high')
    if f.get('underline'):
        add('underline', 3, 'Underlined text; don\'t underline (16.21).', None, 'high')
    bad_fonts = [x for x in f.get('fonts', []) if x and x.lower() != 'aptos']
    if bad_fonts:
        add('font', 3, f'Font {", ".join(bad_fonts)}; house rule is 12-point Aptos.', None, 'high')
    bad_sizes = [s for s in f.get('sizes', []) if s and abs(s - 12) > 0.01]
    if bad_sizes:
        add('font-size', 3, f'Font size {", ".join(map(str, bad_sizes))} pt; house rule is 12 point.', None, 'medium')
    mt = TYPED_NUM.match(t)
    if mt and not f.get('auto_numbered') and p.get('where') == 'body' and f:
        add('typed-numbering', 3, 'Typed enumeration; use native Word multilevel numbering in the I., A., 1., (a), (i) scheme.', mt, 'medium')
    return out

# ---------------------------------------------------------------- rule-database triggers

LINT_CTRL = {}


def load_rules():
    recs = [json.loads(l) for l in open(os.path.join(ROOT, 'data', 'rules.jsonl'), encoding='utf-8') if l.strip()]
    ov = json.load(open(os.path.join(ROOT, 'data', 'house-overrides.json'), encoding='utf-8'))
    superseded = {rid for o in ov['overrides'] if not o.get('partial') for rid in o['rule_ids']}
    partial = {rid: o['replacement'] for o in ov['overrides'] if o.get('partial') for rid in o['rule_ids']}
    LINT_CTRL.update(ov.get('lint') or {})
    compiled = []
    for r in recs:
        if r['status'] == 'proposal' or r['id'] in superseded:
            continue
        if r['id'] in partial:
            r = dict(r, _house=partial[r['id']])
        h = (r.get('trigger') or {}).get('regex_hint') or ''
        if not h:
            continue
        try:
            rx = re.compile(h, re.I if '(?i)' not in h else 0)
        except re.error:
            continue
        compiled.append((r, rx))
    return compiled


def rule_checks(paras, compiled, broad_share=0.15):
    hits = collections.defaultdict(list)
    for p in paras:
        if not p['text'].strip():
            continue
        seen = set()
        for r, rx in compiled:
            if r['id'] in seen:
                continue
            m = rx.search(p['text'])
            if m and 'active-voice' in (r.get('key_items') or []) and m.group(0).split()[-1].lower().strip('.,;') in NOT_PASSIVE:
                m = None  # a linking verb plus an adjective (is dated, is liable), not a passive
            sup = (LINT_CTRL.get('suppress') or {}).get(r['id'])
            if m and sup and re.match(sup, p['text'][m.start():m.start() + 40]):
                m = None  # the matched text already meets the house rule
            if m:
                seen.add(r['id'])
                hits[r['id']].append((p['idx'], m.group(0)[:120], r))
    out, broad = [], []
    n = max(1, sum(1 for p in paras if p['text'].strip()))
    for rid, hs in hits.items():
        r = hs[0][2]
        if (len(hs) > 5 and len(hs) / n > broad_share) or rid in (LINT_CTRL.get('broad_only') or []):
            broad.append({'rule_id': rid, 'hits': len(hs), 'statement': r['statement'][:160]})
            continue
        for idx, mtxt, r in hs:
            out.append({'check': 'rule:' + r['kind'], 'severity': r['severity'], 'para': idx, 'match': mtxt,
                        'message': r['statement'][:220] + (f" [HOUSE: {r['_house'][:220]}]" if r.get('_house') else ''),
                        'confidence': 'medium', 'rule_ids': [rid], 'source': 'rules'})
    return out, broad

# ---------------------------------------------------------------- defined-term inventory

INTEG = re.compile(r"\((?:each,?\s+)?(?:the|a|an)?\s*[\"“]\*{0,2}([^\"”]{1,60}?)\*{0,2}[\"”]")
AUTON = re.compile(r"^\s*[\"“]\*{0,2}([^\"”]{1,60}?)\*{0,2}[\"”]\s+(?:means|includes|has the meaning|shall mean|shall have)")


def inventory(paras):
    defs = {}
    for p in paras:
        for m in INTEG.finditer(p['text']):
            defs.setdefault(m.group(1).strip(), []).append(('integrated', p['idx']))
        m = AUTON.match(p['text'])
        if m:
            defs.setdefault(m.group(1).strip(), []).append(('autonomous', p['idx']))
    full = '\n'.join(p['text'] for p in paras)
    rows, findings = [], []
    for term, where in sorted(defs.items()):
        cap = len(re.findall(r"\b" + re.escape(term) + r"\b", full)) - len(where)
        low = len(re.findall(r"\b" + re.escape(term.lower()) + r"\b", full)) if term.lower() != term else 0
        rows.append({'term': term, 'defined': [w[0] for w in where], 'defined_in_para': [w[1] for w in where],
                     'uses': max(cap, 0), 'lowercase_uses': low})
        if len(where) > 1:
            findings.append({'check': 'defined-twice', 'severity': 1, 'para': where[1][1], 'match': term,
                             'message': f'"{term}" is defined more than once; define each term once (1.57: one word, one meaning).', 'confidence': 'high', 'rule_ids': [], 'source': 'inventory'})
        if cap <= 0:
            findings.append({'check': 'defined-unused', 'severity': 2, 'para': where[0][1], 'match': term,
                             'message': f'"{term}" is defined but never used (6.122).', 'confidence': 'high', 'rule_ids': [], 'source': 'inventory'})
        if 'shall mean' in full and any(w[0] == 'autonomous' for w in where):
            pass
    for m in re.finditer(r"[\"“][^\"”]{1,60}[\"”]\s+shall\s+(?:mean|be|have)", full):
        findings.append({'check': 'shall-in-definition', 'severity': 2, 'para': -1, 'match': m.group(0)[:80],
                         'message': 'Use means, not shall mean or shall be, in a definition (6.33-6.42; blog).', 'confidence': 'high', 'rule_ids': [], 'source': 'inventory'})
    caps = collections.Counter(m.group(0) for m in re.finditer(r"(?<![.?!]\s)(?<!^)\b(?:[A-Z][a-z]+)(?:\s+[A-Z][a-z]+){0,3}\b", full))
    known = set(defs)
    for phrase, c in caps.items():
        if c >= 3 and phrase not in known and not any(phrase in k or k in phrase for k in known) and len(phrase) > 3 and ' ' in phrase:
            findings.append({'check': 'possibly-undefined-term', 'severity': 2, 'para': -1, 'match': phrase,
                             'message': f'"{phrase}" is capitalized {c} times but not defined; define it or lowercase it (6.122).', 'confidence': 'low', 'rule_ids': [], 'source': 'inventory'})
    return rows, findings

# ---------------------------------------------------------------- report

def report(path, paras, meta, findings, broad, inv):
    sev_name = {1: 'Severity 1: must fix (ambiguity, meaning-changing)', 2: 'Severity 2: should fix (vagueness, dispute risk, house rules)', 3: 'Severity 3: style'}
    nd = sum(1 for f in findings if f['source'] != 'rules')
    lines = [f'# Lint report: {os.path.basename(path)}', '',
             f'{len(paras)} paragraphs read; {nd} direct findings (house rules, word checks, inventory) and {len(findings) - nd} rule triggers. All are candidates: confirm each in context before acting.', '']
    if meta:
        nf, ns = meta.get('normal_font'), meta.get('normal_size')
        if (nf and nf.lower() != 'aptos') or (ns and abs(ns - 12) > 0.01):
            lines.append(f'- Document default font: {nf} {ns} pt (house rule: 12-point Aptos).')
        if meta.get('tracked_changes'):
            lines.append('- The document has tracked changes; the text was read as if every change were accepted. Ask Blake whether to accept them first or redline on top.')
    cnt = collections.Counter(f['check'] for f in findings)
    lines += ['## Counts by check', ''] + [f'- {k}: {v}' for k, v in cnt.most_common()] + ['']
    direct = [f for f in findings if f['source'] != 'rules']
    triggers = [f for f in findings if f['source'] == 'rules']
    groups = [(sev_name[s], [f for f in direct if int(f['severity']) == s]) for s in (1, 2, 3)]
    groups.append((f'Rule triggers to check in the analysis passes (severity shown is the rule\'s, if the problem is confirmed; most triggers in a clean draft are not problems)', triggers))
    for title, fs in groups:
        if not fs: continue
        lines += [f'## {title} ({len(fs)})', '']
        for f in sorted(fs, key=lambda f: (f['para'], f['check'])):
            txt = paras[f['para']]['text'][:90].replace('\n', ' ') if 0 <= f['para'] < len(paras) else ''
            lines.append(f"- para {f['para']} · sev {f['severity']} · {f['check']} · \"{f['match']}\" · {f['message']}" + (f" · rules: {', '.join(f['rule_ids'])}" if f['rule_ids'] else '') + (f" · [{f['confidence']}]" if f['confidence'] != 'high' else ''))
            if txt: lines.append(f'  - context: {txt}')
        lines.append('')
    if broad:
        lines += ['## Broad triggers (matched too many paragraphs to list; check these in pass 3)', '']
        lines += [f"- {b['rule_id']} ({b['hits']} paragraphs): {b['statement']}" for b in broad] + ['']
    if inv is not None:
        lines += ['## Defined-term inventory', '', '| Term | Defined | Uses | Lowercase uses |', '|---|---|---|---|']
        lines += [f"| {r['term']} | {', '.join(r['defined'])} (para {', '.join(map(str, r['defined_in_para']))}) | {r['uses']} | {r['lowercase_uses']} |" for r in inv]
    return '\n'.join(lines) + '\n'


def run(path, want_inventory):
    paras, meta = read_paragraphs(path)
    findings = []
    global PARTY_TERMS
    PARTY_TERMS = party_terms(paras)
    for p in paras:
        if p['text'].strip():
            findings += house_checks(p)
    # the attachment reminder is a per-document check: keep the first one only
    first_att = next((i for i, f in enumerate(findings) if f['check'] == 'attachment-check'), None)
    findings = [f for i, f in enumerate(findings) if f['check'] != 'attachment-check' or i == first_att]
    if first_att is not None:
        n_att = sum(1 for p in paras if re.search(r"\b(Schedule|Exhibit|schedule|exhibit)s?\b", p['text']))
        findings[first_att] = dict(findings[first_att], message=f'Attachments mentioned in {n_att} paragraphs: confirm each schedule-versus-exhibit classification, the order (schedules before exhibits) and every reference (attachments.md).')
    comp = load_rules()
    comp_ids = {r['id'] for r, _ in comp}
    rf, broad = rule_checks(paras, comp + [(r, rx) for r, rx in phrase_rules(comp_ids)])
    house_keys = {(f['para'], f['match'].lower()) for f in findings}
    findings += [f for f in rf if (f['para'], f['match'].lower()) not in house_keys]
    inv = None
    if want_inventory:
        inv, invf = inventory(paras)
        findings += invf
    return paras, meta, findings, broad, inv


def self_test():
    cases = [
        ('Neither party shall assign this agreement.', 'negative-subject-shall', True),
        ('Acme shall not assign this agreement.', 'negative-subject-shall', False),
        ('If Acme should exercise the Option, Widgetco shall pay.', 'should', True),
        ('1. The Company shall pay.  Acme shall deliver.', 'spacing', False),
        ('II. Termination of Employment', 'spacing', False),
        ('The Shares will be issued at Closing.', 'passive-voice', True),
        ('Any purported transfer will be void.', 'passive-voice', False),
        ('Acme is liable for the Losses.', 'passive-voice', False),
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
        ('The Shares will be issued at Closing.', 'passive-voice', True),
        ('This consulting agreement is dated January 1, 2027.', 'passive-voice', False),
        ('the day on which this agreement ends', 'restrictive-which', False),
        ('any claim which arises under this agreement', 'restrictive-which', True),
        ('Acme shall pay within five (5) days.', 'words-and-digits', True),
        ('Acme shall pay within three days.', 'number-word', True),
        ('Acme shall pay within 3 days.', 'number-word', False),
        ('See Section 4.2(a) for details.', 'numbered-cross-reference', True),
        ('The Assets listed on Schedule A are excluded.', 'attachments', True),
        ('The form attached hereto as Exhibit 2 governs.', 'attachments', True),
        ('The list in schedule A governs.', 'attachment-capitals', True),
        ('This agreement is dated 1 January 2027.', 'date-format', True),
        ('Acme shall pay. Widgetco shall deliver.', 'spacing', True),
        ('Acme shall pay.  Widgetco shall deliver.', 'spacing', False),
        ('Acme Inc. shall pay.', 'spacing', False),
        ('Once Acme pays, the lien terminates.', 'once', True),
        ('Smith & Jones LLP shall act as escrow agent.', 'ampersand', True),
        ('The headings in this agreement are for convenience only.', 'headings-clause', True),
        ('Acme shall pay the Price no later than 30 days after the Closing Date, and Widgetco shall deliver the Units.', 'negative-subject-shall', False),
        ('If no Default exists, Acme shall pay the Price.', 'negative-subject-shall', False),
        ('Acme shall pay, and no Shareholder shall transfer any Shares.', 'negative-subject-shall', True),
        ('The parties agree that no party shall assign this agreement.', 'negative-subject-shall', True),
        ('Payments under Section 409A of the Internal Revenue Code are exempt.', 'numbered-cross-reference', False),
        ('as stated in Section 4.2', 'numbered-cross-reference', True),
        ('Notice is effective at 5:00 p.m. Central time.', 'spacing', False),
        ('the form attached as Exhibit A', 'attachment-scheme', True),
        ('the prices in Schedule 1', 'attachment-scheme', True),
        ('the prices in Schedule A and the form in Exhibit 1', 'attachment-scheme', False),
    ]
    fails = 0
    for text, check, expect in cases:
        got = any(f['check'] == check for f in house_checks({'idx': 0, 'text': text, 'fmt': {}}))
        if got != expect:
            fails += 1; print(f'FAIL: {check} expected {expect} for: {text}')
    # Whole-pipeline cases: run() on a temporary file, so the rule channel and the house overrides are exercised too.
    import tempfile
    doc_cases = [
        ('This consulting agreement is dated January 1, 2027, and is between ACME, INC. ("Acme") and DANA PARK ("Park").', 'R-3.15-passive-hides-actor', False),
        ('Acme shall deliver the Units listed in Schedule A to Park.', 'R-5.78-no-emphasis-attachment-refs', False),
        ('Acme shall deliver the Units listed in Schedule A to Park.', 'R-17.29-initial-capitals', False),
        ('The Units will be delivered to Park.', 'R-3.15-passive-hides-actor', True),
    ]
    for text, rid, expect in doc_cases:
        with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8') as fh:
            fh.write(text + '\n'); tmp = fh.name
        try:
            fs = run(tmp, False)[2]
        finally:
            os.unlink(tmp)
        got = any(rid in f.get('rule_ids', []) for f in fs)
        if got != expect:
            fails += 1; print(f'FAIL (run): {rid} expected {expect} for: {text}')
    try:
        read_paragraphs('contract.pdf'); fails += 1; print('FAIL: a .pdf was accepted')
    except ValueError:
        pass
    total = len(cases) + len(doc_cases) + 1
    print(f'self-test: {total - fails}/{total} passed')
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('path', nargs='?')
    ap.add_argument('--json', help='also write findings as JSON to this path')
    ap.add_argument('--inventory', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.path:
        ap.print_usage(); return 5
    try:
        paras, meta, findings, broad, inv = run(a.path, a.inventory)
    except Exception as e:  # unreadable or unsupported file
        print(f'error: could not read {a.path}: {e}', file=sys.stderr); return 2
    sys.stdout.write(report(a.path, paras, meta, findings, broad, inv))
    if a.json:
        json.dump({'file': a.path, 'paragraphs': [{'idx': p['idx'], 'text': p['text']} for p in paras],
                   'findings': findings, 'broad_triggers': broad, 'inventory': inv}, open(a.json, 'w'), indent=1, ensure_ascii=False)
    return 0


if __name__ == '__main__':
    sys.exit(main())
