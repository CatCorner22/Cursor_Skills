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

def auto_numbered(p):
    # Word numbering set on the paragraph, or inherited from its style (List Number and the like)
    if p._p.pPr is not None and p._p.pPr.numPr is not None:
        return True
    st = p.style
    while st is not None:
        ppr = st.element.pPr
        if ppr is not None and ppr.numPr is not None:
            return True
        st = st.base_style
    return False


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
            bold_txt = ''.join(r.text for r in p.runs if r.bold)
            try:
                centered = p.alignment is not None and int(p.alignment) == 1
            except (TypeError, ValueError):
                centered = False
            fmt.update({'fonts': sorted(fonts), 'sizes': sorted(sizes), 'underline': underline, 'bold_text': bold_txt,
                        'centered': centered, 'auto_numbered': auto_numbered(p)})
            from docx.oxml.ns import qn
            text = ''.join(el.text or '' if el.tag == qn('w:t') else '\t' if el.tag == qn('w:tab') else '\n'
                           for el in p._p.iter(qn('w:t'), qn('w:tab'), qn('w:br')))  # includes inserted text, skips deleted text
            paras.append({'idx': len(paras), 'text': text, 'where': where,
                          'style': p.style.name if p.style is not None else '', 'fmt': fmt})
        # Walk every paragraph in document order, including paragraphs that python-docx's
        # Document.paragraphs skips: those inside content controls (w:sdt), revision wrappers
        # (w:ins, w:moveTo) and tables. Each paragraph is read once, even in merged table cells.
        from docx.text.paragraph import Paragraph
        from docx.oxml.ns import qn as _qn
        tbl_tag = _qn('w:tbl')
        for p_el in d.element.body.iter(_qn('w:p')):
            anc, in_table = p_el.getparent(), False
            while anc is not None:
                if anc.tag == tbl_tag:
                    in_table = True; break
                anc = anc.getparent()
            add(Paragraph(p_el, d._body), 'table' if in_table else 'body')
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
            fmt = {'bold_text': ' '.join(re.findall(r"\*\*(.+?)\*\*", block))} if ext == '.md' else {}
            paras.append({'idx': len(paras), 'text': block.strip('\n'), 'where': 'body', 'style': '', 'fmt': fmt})
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
PROPER_AFTER = re.compile(r"(?:\s+[A-Z][\w'-]*){0,2}\s+(?:Plaza|Place|Street|St\.|Avenue|Ave\.|Center|Centre|Tower|Towers|Square|Park|Building|Court|Circle|Way|Road|Boulevard|Drive|Lane|Bank|Judicial|Circuit|District|Floor)\b", re.I)
FIRST_COUNT = re.compile(r"\bfirst\s+(?:anniversary|day|business day|month|year|quarter|installment|payment|calendar|week|period)\b", re.I)
ORD_RE = re.compile(r"\b((?:twenty|thirty)-)?(second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|thirtieth|hundredth|(?<=-)first)\b", re.I)
WORDS_DIGITS = re.compile(r"\b[a-z][a-z\- ]{2,40}\s*\(\s*\$?\d[\d,\.]*\s*%?\)", re.I)
ABBREV = re.compile(r"(?:\b(?:Inc|Ltd|Co|Corp|No|Nos|Mr|Ms|Mrs|Dr|St|Jr|Sr|U\.S|e\.g|i\.e|v|vs|etc|L\.L\.C|L\.P|N\.A|Sec|Art|p|pp|a\.m|p\.m)\.)$")
ONE_SPACE = re.compile(r"([.?!][\"”’)]?) (?=[A-Z“\"(])")
TWO_AFTER_COLON = re.compile(r":  +\S")
NEG_SUBJ_SHALL = re.compile(r"(?:^\s*(?:\(?[A-Za-z0-9]{1,4}[.)]\s*|\d+(?:\.\d+)+\.?\s*|[IVXLC]+\.\s*)?|[.;:]\s+|,\s+(?:and|or|but)\s+|\b(?:that|and|or|but)\s+)(Neither|No|None of|Nobody|No one|Nothing)\b(?!\s+(?:later|earlier|more|less|fewer|sooner)\s+than)[^.;:,]{0,100}?\bshall\b(?!\s+not)", re.I)
SHOULD = re.compile(r"\bshould\b", re.I)
ONCE = re.compile(r"\bonce\b", re.I)
WHEN_COND = re.compile(r"(?:^|[.;:]\s+|\(\w{1,4}\)\s+)When\b")
AMP = re.compile(r"&")
XREF = re.compile(r"\b(?:[Ss]ections?|[Aa]rticles?|[Cc]lauses?|[Pp]aragraphs?|[Ss]ubsections?|§)\s*(?:[IVXLC]+|\d+|[A-Z](?=[.\s,;)]))(?:[.-][\dA-Za-z]+)*(?:\s*\([a-z0-9]{1,4}\))*(?![\w.-]*(?:\s*\([a-z0-9]{1,4}\))*\s+of\s+(?:the\s+)?(?:[A-Z]|\d+\s+U\.S\.C|title))")
REL_XREF = re.compile(r"\b(?:above|below|the foregoing|hereof|hereunder|herein|hereinafter|aforesaid)\b", re.I)
ATT_LOWER = re.compile(r"\b(schedule|exhibit|annex|appendix)\s+(?:[A-Z]\b|\d+\b)")
ATT_HERETO = re.compile(r"\b(?:Schedules?|Exhibits?|schedules?|exhibits?)\b[^.;]{0,40}?\b(?:hereto|attached hereto|to this [Aa]greement)\b|\battached hereto\b")
ATT_ON = re.compile(r"\bon (?:Schedule|schedule)\s+[A-Z0-9]")
ATT_PART = re.compile(r"\b(?:form(?:s|ing)?|constitut(?:e|es|ing)|made)\s+(?:a\s+|an\s+)?(?:integral\s+)?part of this [Aa]greement|\bincorporated (?:herein )?by reference\b", re.I)
ATT_QUOTE = re.compile(r"\b(?:Schedule|Exhibit)\s+[\"“][A-Z0-9]+[\"”]")
DMY = re.compile(r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b")
NUMDATE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
THIS_DAY = re.compile(r"\b(?:this|the)\s+\S+\s+day\s+of\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|[_\s]{2,})|\bthis\s+\S+\s+day\s+of\b", re.I)
HEADINGS_CLAUSE = re.compile(r"\bheadings?\b[^.]{0,120}\b(?:convenience|reference)\b", re.I)
TYPED_NUM = re.compile(r"^\s*(?:\d+\.\d+(?:\.\d+)*\.?|\(\d+\)|\([ivx]+\)|\([a-z]\)|[IVX]+\.|[A-Z]\.|\d+\.)\s+")


# House rule 11: no article before a defined party name (MSCD 2.105 and 6.63 differ).
PARTY_DEFAULT = {'Company', 'Buyer', 'Seller', 'Purchaser', 'Supplier', 'Vendor', 'Contractor', 'Subcontractor', 'Consultant',
                 'Customer', 'Client', 'Employee', 'Executive', 'Employer', 'Licensor', 'Licensee', 'Landlord', 'Tenant', 'Lender',
                 'Borrower', 'Guarantor', 'Provider', 'Sponsor', 'University', 'Hotel', 'Distributor', 'Manufacturer'}  # role labels keep the (house rule 11)
WHOSE = None  # 'blake' or 'other-side' when known (--whose)
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
    doc_word = re.compile(r"(?:Agreement|Note|Lease|Plan|Guaranty|Amendment|Policy|Date|Period|Term|Property|Premises|Assets|Business|Shares|Units|Price)$")
    return {t for t in found if t not in NOT_PARTY and not ROLE_DEF.fullmatch('"' + t + '"') and not doc_word.search(t)}


def party_article_re(terms):
    alts = '|'.join(sorted(map(re.escape, terms), key=len, reverse=True))
    return re.compile(r"\b[Tt]he\s+(" + alts + r")\b(?!\s+[A-Z])(?!\s+(?:" + ATTRIBUTIVE + r")\b)")


# Signature phrases: high-precision words and phrases MSCD tells you to change. Reported as direct findings,
# with the fix and the paragraph, so a reviewer doesn't have to dig them out of the rule triggers.
MONTH = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
SIGNATURE = [
    (r"\band/or\b", 'and-or', 2, 'and/or: write "X or Y or both" or "1 or both of X and Y"; in an obligation, state the duty and the choice separately (MSCD 11.90-11.95).', ['R-11.90-no-and-or']),
    (r"\b(?:reasonable\s+)?best\s+(?:efforts|endeavou?rs)\b", 'efforts', 1, 'best efforts: write reasonable efforts; best invites a reader to find extra meaning (MSCD 8.91; 8.134).', ['R-8.91-best-efforts-ambiguous']),
    (r"\bgood[- ]faith\s+efforts\b", 'efforts', 2, 'good-faith efforts: write reasonable efforts; good faith brings in the implied duty of good faith (MSCD 8.38).', ['R-8.38-good-faith-efforts']),
    (r"\bdiligent\s+efforts\b", 'efforts', 2, 'diligent efforts: write reasonable efforts; don\'t mix diligence into an efforts standard (MSCD 8.153; 8.134).', ['R-8.153-no-mixed-standards']),
    (r"\b(?:all|every|very)\s+(?:reasonable|best)\s+efforts?\b", 'efforts', 2, 'all, every or very in an efforts standard: delete it and write reasonable efforts (MSCD 8.15).', ['R-8.15-no-very-all-every']),
    (r"\bcommercially\s+reasonable\s+efforts\b|\breasonable\s+commercial\s+efforts\b", 'efforts', 2, 'commercially reasonable efforts: delete commercially and write reasonable efforts (MSCD 8.14).', ['R-8.14-no-commercially']),
    (r"\buse\s+(?:its|their|his|her)\s+(?:reasonable|best)\s+efforts\b", 'efforts', 3, 'Write use reasonable efforts, without the pronoun (MSCD 8.17).', ['R-8.17-use-verb-use']),
    (r"\brepresents?\s+and\s+warrants?\b|\bwarrants?\s+and\s+represents?\b", 'represents-warrants', 2, "represents and warrants: on Blake's draft use states (3.457); on the other side's draft keep it and suggest the remedies-neutral sentence in a comment (3.459-3.463).", ['R-3.457-use-states']),
    (r"\(this\s+[\"“]\*{0,2}[A-Z][a-z]+\*{0,2}[\"”]\)|^[\s*_#]*(?:THIS|This)\s+(?:[\w-]+\s+){0,6}?(?:" + "|".join(N + r"\s+\(the\s+[\"“]\*{0,2}" + n + r"\*{0,2}[\"”]\)" for n in ("Agreement", "Amendment", "Addendum", "Lease", "Sublease", "Note", "Guaranty", "Release", "License") for N in (n, n.upper())) + ")", 'this-agreement-term', 3, 'Don\'t define this agreement as a term; delete the definition and write this agreement (or this amendment, this lease) in lowercase throughout (MSCD 2.123).', ['R-2.123-no-this-agreement-term']),
    (r"\b[Tt]he\s+same\b(?=\s*(?:[,.;:)]|$)|\s+(?:to|by|in|on|at|for|and|or|within|if|when|from|with|under|until|without)\b)", 'same-pronoun', 3, 'same as a pronoun: write it, them or their, or repeat the noun (MSCD 13.760).', ['R-13.760-same-pronoun']),
    (r"\bWHEREAS\b|\bWITNESSETH\b|\bNOW,?\s+THEREFORE\b|\b[Ww]hereas\b", 'archaic', 3, 'Traditional recitals or lead-in: delete WHEREAS, WITNESSETH and NOW, THEREFORE; put any background in plain sentences (MSCD 2.137; 2.165).', ['R-2.137-no-witnesseth', 'R-1.4-no-archaisms']),
    (r"\bgood\s+and\s+valuable\s+consideration\b|\breceipt\s+and\s+sufficiency\s+of\s+which\b", 'archaic', 3, 'Recital of consideration: delete it (MSCD 2.165; 2.188).', ['R-2.188-good-and-valuable']),
    (r"\bIN\s+WITNESS\s+WHEREOF\b|\b[Ii]n\s+[Ww]itness\s+[Ww]hereof\b", 'archaic', 3, "Traditional concluding clause: use MSCD's concluding clause (5.13-5.17).", ['R-5.17-traditional-concluding-clause']),
    (r"\b[Hh]ere(?:of|in|under|inafter|inabove|inbefore|with|to|after|tofore)\b", 'archaic', 3, 'Archaic here-word: write this agreement, refer by heading, or delete it (MSCD 1.4). Keep hereby only in language of performance.', ['R-1.4-no-archaisms']),
    (r"\b[Ss]aid\s+(?=[A-Z][a-z]|(?:agreement|party|parties|premises|equipment|property|goods|notice|amount|payment|sum)\b)", 'archaic', 3, 'said as a pointing word: use the or this (MSCD 13.758).', ['R-13.758-said']),
    (r"\b(?:hereby\s+)?(?:agrees?|undertakes?|covenants?)\s+(?:and\s+agrees?\s+)?to\b(?!\s+(?:the|this|that|such|any|its|these|those|a|an)\b)", 'agrees-to', 2, 'agrees to / undertakes to / covenants to: state the obligation with shall (MSCD 3.125, 3.129).', ['R-3.125-no-agrees-to-obligation']),
    (r"\b(?:in|at)\s+(?:its|their|his|her|the\s+\w+['’]s)\s+(?:sole|absolute|sole\s+and\s+absolute|own)\s+discretion\b", 'sole-discretion', 2, 'sole discretion: delete it; if it addresses the implied duty of good faith, address that directly (MSCD 3.249-3.269).', ['R-3.249-no-sole-discretion']),
    (r"\b[Tt]ime\s+is\s+of\s+the\s+essence\b", 'time-is-of-the-essence', 2, 'Time is of the essence: delete it; say what happens when a deadline is missed (MSCD 13.884).', ['R-13.884-time-of-the-essence']),
    (r"\bhold\s+(?:\w+\s+)?harmless\b", 'doublet', 2, 'hold harmless adds nothing to indemnify; write indemnify. Defend is a separate obligation: keep it if the parties intend it (MSCD 13.440).', ['R-13.440-hold-harmless']),
    (r"\bterms\s+and\s+conditions\b", 'doublet', 3, 'terms and conditions: write terms (MSCD 13.860).', ['R-13.860-terms-and-conditions']),
    (r"\bincluding,?\s+(?:but\s+not\s+limited\s+to|without\s+limitation)\b", 'doublet', 3, 'including but not limited to / including without limitation: write including (MSCD 13.359-13.393).', ['R-13.361-without-limitation']),
    (r"\b(?:null\s+and\s+void|due\s+and\s+payable|any\s+and\s+all|each\s+and\s+every|cease\s+and\s+desist|full\s+force\s+and\s+effect|sole\s+and\s+exclusive|true\s+and\s+correct|fit\s+and\s+proper|free\s+and\s+clear)\b", 'doublet', 3, 'Redundant string: use 1 word (MSCD 1.36-1.49).', ['R-1.43-prune-synonym-strings']),
    (r"\barising\s+(?:out\s+of|under)\s+or\s+(?:relating|related|in\s+connection\s+with)\b|\barising\s+out\s+of\s+or\s+in\s+connection\s+with\b|\brelating\s+to\s+or\s+arising\s+out\s+of\b", 'arising-out-of', 2, 'arising out of or relating to: write arising out of, or state the connection you mean (MSCD 13.41-13.54).', ['R-13.41-arising-out-of-or-relating-to']),
    (r"\b[Ff]or\s+the\s+avoidance\s+of\s+doubt\b", 'throat-clearing', 3, 'for the avoidance of doubt: delete it, or fix the ambiguity it signals (MSCD 13.312).', ['R-13.312-for-the-avoidance-of-doubt']),
    (r"\b[Ii]t\s+is\s+(?:expressly\s+|further\s+|hereby\s+|mutually\s+)?(?:understood|agreed|acknowledged)(?:\s+and\s+(?:agreed|understood|acknowledged))?\s+(?:by\s+the\s+parties\s+)?that\b|\b[Tt]he\s+parties\s+(?:hereby\s+)?(?:acknowledge|agree|understand)\s+and\s+(?:agree|acknowledge|understand)\s+that\b", 'throat-clearing', 2, 'Throat-clearing: delete the lead-in and state the rule (MSCD 3.27).', ['R-3.27-throat-clearing']),
    (r"\bsuccessors\s+and\s+(?:permitted\s+)?assigns\b", 'successors-assigns', 3, 'successors and assigns: usually delete; the law already binds successors (MSCD 2.95; 15.24).', ['R-15.24-rule-successors-assigns']),
    (r"\b(?:shall|will)\s+survive\b|\bsurvives?\s+(?:the\s+)?(?:termination|expiration)\b", 'survival', 2, 'Survival provision: delete it; give each obligation that outlasts the agreement its own duration (MSCD 13.822-13.831).', ['R-13.822-survival']),
    (r"\b[Ww]ithin\s+(?:\d+|[a-z]+(?:\s+\(\d+\))?)\s+(?:calendar\s+|business\s+|Business\s+)?(?:days?|Days?|months?|years?|weeks?|hours?)\b(?!\s+(?:after|following)\b)", 'time-ambiguity', 1, 'within: unclear whether the period runs before the event, after it or both; write no later than [N] days after [event], or during the [N] days before (MSCD 10.69-10.71).', ['R-10.69-within-ambiguity']),
    (r"\b[Ww]ithin\s+(?:\d+|[a-z]+(?:\s+\(\d+\))?)\s+(?:calendar\s+|business\s+|Business\s+)?(?:days?|Days?|months?|years?|weeks?|hours?)\b\s+(?:after|following)\b", 'within-after', 3, 'within [N] days after: MSCD says not to use within; write no later than [N] days after (10.69-10.71). After already sets the direction, so this is a wording fix, not an ambiguity.', ['R-10.69-within-ambiguity']),
    (r"\bby\s+(?:" + MONTH + r"\s+\d{1,2}(?:,\s*\d{4})?|\d{1,2}/\d{1,2}/\d{2,4})\b", 'time-ambiguity', 2, 'by [date]: write no later than [date], so the deadline day is clearly included (MSCD 13.608).', ['R-13.608-no-later-than']),
    (r"\b[Ff]rom\s+(?:and\s+including\s+)?" + MONTH + r"\s+\d{1,2},?\s*(?:\d{4}\s+)?(?:to|until|till|through)\s+(?!and\s+including)", 'time-ambiguity', 2, 'from [date] to/until [date]: say whether each end date is included ("from and including ... to and including ...") (MSCD 15.16).', ['R-15.16-rule-from-to-until']),
    (r"\b[Bb]etween\s+" + MONTH + r"\s+\d{1,2}(?:,\s*\d{4})?\s+and\s+", 'time-ambiguity', 2, 'between [date] and [date]: say whether the end dates are included (MSCD 15.16).', ['R-15.16-rule-from-to-until']),
    (r"\bpromptly\b", 'vagueness', 3, 'promptly is vague, and a court may read it as immediately; state a number of days if timing matters (MSCD 10.114; 7.46-7.47).', ['R-10.114-promptly-equals-immediately']),
    (r"\bthird[- ]part(?:y|ies)\b(?![- ]beneficiar)", 'usage', 3, 'third party: write Person, any Person other than a party, or a defined Nonparty (MSCD 13.875).', ['R-13.875-third-party']),
    (r"\b(?:duly\s+)?execut(?:e|es|ed|ing|ion)\b(?!\s+(?:the\s+|its\s+|their\s+|all\s+|any\s+)?(?:work|services?|tasks?|project|duties|obligations|deliverables|plan|protocol|testing)\b)", 'archaic', 3, 'execute for signing: write sign (MSCD 5.7).', ['R-5.7-signing-not-executing']),
    (r"\bshall\s+be\s+entitled\s+to\b|\bshall\s+have\s+the\s+right\s+to\b", 'category-shall', 2, 'shall be entitled to / shall have the right to: write may for discretion, or is entitled to (MSCD 3.206; 3.147).', ['R-3.206-use-may']),
    (r"\bshall\s+be\s+(?:governed|construed|interpreted)\s+(?:by|in\s+accordance)\b|\bshall\s+(?:be\s+)?deemed\b|\bshall\s+(?:commence|begin|continue|terminate|expire|end|accrue)\b(?=\s*(?:[,.;:)]|$)|\s+(?:on|at|upon|when|whenever|if|unless|in|until|for|automatically|immediately|with|after|before|no\s+later|as\s+of|and|or|without|by|effective|under|while|once|daily|monthly)\b)|\bshall\s+be\s+(?:effective|valid|binding|void|enforceable|final)\b|\bshall\s+(?:remain|be)\s+in\s+(?:full\s+)?(?:force|effect)\b", 'category-shall', 2, 'shall with no duty on the subject: use language of policy in the present tense (Tennessee law governs this agreement; the Term begins on ...) (MSCD 3.89-3.98; 3.332).', ['R-3.92-has-a-duty-test']),
]
def _rule_sev():
    try:
        return {json.loads(l)['id']: json.loads(l)['severity'] for l in open(os.path.join(ROOT, 'data', 'rules.jsonl'), encoding='utf-8')}
    except Exception:
        return {}
_SEV = _rule_sev()
# the rule record decides severity, so the lint and rules_query.py agree
SIGNATURE = [(re.compile(p), c, _SEV.get(r[0], s) if r and c != 'within-after' else s, m, r) for p, c, s, m, r in SIGNATURE]


TOA = 'Term of art used in its everyday sense; the contract may also use it in its legal sense, and one word should carry one meaning (MSCD 1.57). '

EXTRA = [
    (re.compile(r"\bsuch\b(?!\s+as\b)(?=\s+[A-Za-z])", re.I), 'such-pointing', 3, 'Such as a pointing word: use the, this, that, these or those (13.816-13.818); keep such only for "of this kind".', []),
    (re.compile(r"(?<![,(])(?<!\b(?:in|on|of|to|by|at))(?<!\bfor)(?<!\b(?:from|with|upon|into))(?<!\b(?:under|after))(?<!\bthrough)\s+which\b(?!\s+(?:is|are)\s+(?:not\s+)?(?:a|an|the)\b)"), 'restrictive-which', 2, 'Which without a comma introduces a restrictive clause: use that (12.44; 12.53-12.56).', []),
    (re.compile(r"\b(?:if|unless|until|in the event)\b[^,.;:]{0,90}?\bshall\b", re.I), 'shall-in-condition', 1, 'Shall in a conditional clause: use the present tense (3.358-3.360).', ['R-3.358-conditional-present-tense']),
    (re.compile(r"\b(?:is|are|shall be|will be)\s+entitled to\b", re.I), 'is-entitled-to', 2, 'Is entitled to: if it hides another party\'s duty, state the duty with shall (3.168-3.171; 3.288-3.291); for discretion use may (3.206).', ['R-3.169-no-is-entitled-to-obligation']),
    (re.compile(r"\b(?:Attachment|Appendix|Annex|Addendum|ATTACHMENT|APPENDIX|ANNEX|ADDENDUM)\s+(?:[A-Z]|\d+)\b"), 'generic-attachment-label', 2, 'Generic attachment label. House rule: Schedule A (lettered; information the body refers to, such as lists and disclosures) or Exhibit 1 (numbered; a stand-alone document, such as a form of agreement). Decide which it is and update every reference (MSCD 5.72-5.74; attachments.md).', ['R-5.74-generic-attachment-term']),
    (re.compile(r"\b(?:Exhibit|EXHIBIT)\s+[A-Z]\b(?!\.)"), 'attachment-scheme', 2, 'Lettered exhibit. House rule 6: exhibits take numbers (Exhibit 1), schedules take letters (Schedule A); relabel and update every reference (MSCD 5.80-5.83 differs).', []),
    (re.compile(r"\b(?:Schedules?|SCHEDULES?)\s+\d+(?:\.\d+)*\b"), 'attachment-scheme', 2, 'Numbered schedule. House rule 6: schedules take letters (Schedule A), exhibits take numbers (Exhibit 1); relabel and update every reference (MSCD 5.80-5.83 differs).', []),
    (re.compile(r"\b(?:[Tt]he|[Aa]ny|[Ee]ach|[Aa]ll|[Ee]very|[Aa]n?)\s+(?:[A-Z][\w-]*|[a-z]+)\s+(?:[a-z]+ed(?=\s+by\b)|given|paid|made|sent|delivered|received|issued|provided|described|specified|listed|referred|contemplated|required|owned|held|granted|incurred|used|stated|set forth|identified|included|attached|signed|imposed|issued|filed|obtained|collected|charged|purchased|sold|performed)\s+(?:by|under|in|to|on|at|for|from|pursuant|with|as|before|after)\b(?<!made for)"), 'reduced-passive', 3, 'Possible reduced passive (a past participle after a noun, short for "that is given ..."). House rule 1: recast in the active if a clean form exists ("the notice that Acme gives under ..."); otherwise leave it.', ['R-3.15-active-voice']),
    (re.compile(r"\b(?:for|of|reimburse|pay|repay|bear|all|any|on|to)\s+(?!(?:the|a|an|any|each|all|every|its|their|his|her)\s)[a-z]+\s+[a-z]{3,}s\s+(?:incurred|paid|made|given|sent|received|issued|provided|delivered|imposed|charged|suffered|sustained|caused|owed|held|owned|granted|performed)\s+by\b"), 'reduced-passive', 3, 'Possible reduced passive (a past participle after a noun, short for "that are incurred by ..."). House rule 1: recast in the active if a clean form exists ("the travel expenses that the Consultant incurs"); otherwise leave it.', ['R-3.15-active-voice']),
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
                    'start': m.start() if m else -1, 'end': m.end() if m else -1,
                    'message': msg, 'confidence': conf, 'rule_ids': list(rules), 'source': 'house'})
    seen_verbs = set()
    for m in list(PASSIVE_RE.finditer(t)) + list(MODAL_BE.finditer(t)):
        word = m.group(1).lower()
        if word in NOT_PASSIVE or word.rstrip('?') in NOT_PASSIVE or m.start(1) in seen_verbs:
            continue
        if re.match(r"un[a-z]{3,}ed$", word):
            continue  # unresolved, unpaid, unused: adjectives, not passives
        seen_verbs.add(m.start(1))  # one flag per participle, even when both patterns match it
        if word == 'required' and re.search(r'\bnot\s+required\s+to\b', m.group(0) + t[m.end():m.end() + 4], re.I):
            continue  # is not required to: Blake's fixed exception (MSCD 3.292)
        add('passive-voice', 2, 'Possible passive voice; house rule is active voice only. Name the actor (house-style.md section 1).', m,
            'medium', ['R-3.15-active-voice'])
    for rx, chk, sev, msg, rules in SIGNATURE:
        for m in rx.finditer(t):
            if chk == 'represents-warrants' and WHOSE == 'other-side':
                add(chk, 3, "Keep represents and warrants on the other side's draft; suggest the remedies-neutral sentence in a comment (3.459-3.463; house rule 10).", m, 'high', rules)
            elif chk == 'represents-warrants' and WHOSE == 'blake':
                add(chk, 2, 'represents and warrants on your draft: use states (MSCD 3.457; house rule 10).', m, 'high', rules)
                out[-1]['keep_sev'] = True  # house rule 10 on Blake's draft
            elif chk == 'and-or' and re.search(r"\w+,\s+(?:[\w-]+\s+){0,4}?[\w-]+,?\s*$", t[max(0, m.start() - 80):m.start()]):
                add(chk, 1, 'and/or after a list of 3 or more items: unclear whether it means any 1, any combination or all; list the combinations allowed (MSCD 11.94).', m, 'high', rules)
                out[-1]['keep_sev'] = True
            else:
                add(chk, sev, msg, m, 'high', rules)
    if PARTY_TERMS:
        names = '|'.join(sorted(map(re.escape, PARTY_TERMS | {'each party', 'Each party', 'either party', 'Either party'}), key=len, reverse=True))
        for m in re.finditer(r"\b(?:" + names + r")\s+will\s+(?!be\b|have\b|not\s+be\b)", t):
            add('category-will', 2, 'will for a party\'s duty: use shall (MSCD 3.111). Keep will only for future events no party controls.', m, 'medium', ['R-3.111-no-will-for-obligation'])
        for m in re.finditer(r"\b(?:" + names + r")\s+must\b(?!\s+not\b)", t):
            if re.search(r"(?:^|[.;:]\s+)(?:To|In\s+order\s+to)\s+[^.;]{3,120},\s*(?:\w+\s+){0,3}$", t[:m.start()]):
                continue  # must in a condition (To exercise the Option, Acme must ...) is right (MSCD 3.386)
            add('category-must', 2, 'must for a duty on the subject: use shall (MSCD 3.107). Keep must for a condition (To exercise ..., Acme must ...) or when the subject is a nonparty (an escrow agent that only acknowledges, 3.154).', m, 'medium', ['R-3.107-no-must-for-subject'])
        for m in re.finditer(r"\b(?:" + names + r")\s+may\s+not\b", t):
            add('may-not', 1, 'may not for a prohibition with an affirmative subject: write shall not (MSCD 3.307). (With a negative subject, Neither party may is right: house rule 8.)', m, 'high', ['R-3.307-no-may-not'])
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
        if m.group(0)[0].isupper() and m.start() > 0 and PROPER_AFTER.match(t, m.end()):
            continue  # part of a proper name (Two Lattice Plaza, Fourth Judicial Circuit)
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
        if re.match(r"[- ]part(?:y|ies)\b", t[m.end():], re.I):
            continue  # third party: a usage point (13.875), reported by the signature check, not a count
        add('ordinal-word', 3, 'Ordinal word; if it counts something, write it in digits (2nd, 3rd).', m, 'low')
    for m in WORDS_DIGITS.finditer(t):
        if NUM_RE.search(m.group(0)):
            add('words-and-digits', 2, 'Words and digits together; use digits only (MSCD 14.5-14.11; house rule).', m, 'high', ['R-14.5-words-and-digits'])
    for m in ONE_SPACE.finditer(t):
        before = t[:m.start() + 1]
        if ABBREV.search(before) or re.search(r"\b[A-Z]\.$", before):
            continue
        if re.fullmatch(r"[\s#>*_]*(?:(?:Article|ARTICLE|Section|SECTION)\s+)?(?:[IVXLC]+|[A-Za-z]|\d+(?:\.\d+)*|\([a-z0-9]+\))\.", before):
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
        if re.search(r"\b(?:[Ii]f|[Uu]nless|[Uu]ntil|[Ii]n the event(?: that)?|[Ee]ven if|[Ww]hether)\b[^,.;:]{0,90}$", t[:m.start()]):
            add('should', 3, 'Should in a conditional clause: write the present tense (If Acme exercises the Option) (MSCD 3.358-3.360).', m, 'high', ['R-3.358-conditional-present-tense'])
        else:
            add('should', 1, 'Should outside a condition: unclear whether it states a duty or advice; for a duty use shall; for advice use recommends (MSCD 3.360; blog).', m, 'high')
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
            if chk == 'reduced-passive':
                noun = m.group(0).split()[1]
                if noun in (PARTY_TERMS or PARTY_DEFAULT) or re.search(r"\b(?:that|which|who|whom)\s+$", t[:m.start()]):
                    continue  # "that the Company provided to": an active relative clause, not a reduced passive
            add(chk, sev, msg, m, 'medium', rules)
    for m in AMP.finditer(t):
        if re.match(r"[^.;:]{0,40}?\b(?:LLC|L\.L\.C\.|LLP|L\.L\.P\.|PLLC|Inc\.?|P\.A\.|P\.C\.|Co\.|Company|Corporation|Corp\.|Ltd\.?|LP|L\.P\.|Partners)\b", t[m.end():], re.I):
            continue  # inside a business or law-firm name (rider: keep it there)
        add('ampersand', 3, 'Ampersand: keep only inside a business or law-firm name; otherwise and (rider).', m, 'medium', ['R-rider-ampersand'])
    for m in XREF.finditer(t):
        lead = re.match(r"\D*(\d+)", m.group(0))
        if lead and int(lead.group(1)) >= 100 or re.search(r"(?:C\.F\.R\.|U\.S\.C\.|Code|Regulations?|Act|Rule)\s*$", t[:m.start()]):
            continue  # Section 164.308; 17 U.S.C. Section 101: references to statutes and regulations
        if not t[:m.start()].strip(' #*_>'):
            continue  # a heading's own label (Section 3.01 Use.), not a cross-reference; the outline check covers numbering
        add('numbered-cross-reference', 2, 'Numbered cross-reference; house rule: avoid cross-references, and refer by heading where one is needed (house-style.md section 4).', m,
            'high', ['R-4.100-crossref-name-and-number'])
    for m in REL_XREF.finditer(t):
        add('contract-reference', 2, 'Here-word or above/below reference: ambiguous contract reference (7.23-7.27); name the provision by heading.', m, 'high')
    for m in ATT_LOWER.finditer(t):
        add('attachment-capitals', 3, 'Attachment reference in lowercase; house rule is Schedule A, Exhibit 2.', m, 'high')
    for rx, chk, msg, rid in ((ATT_HERETO, 'attachment-hereto', 'Drop hereto / attached hereto / to this agreement from attachment references (5.77).', 'R-5.77-no-hereto-attachments'),
                              (ATT_ON, 'attachment-on', 'Say in Schedule X, not on Schedule X (5.95).', 'R-5.95-in-not-on-schedule'),
                              (ATT_PART, 'attachment-part-of', 'Don\'t say an attachment forms part of the agreement or is incorporated by reference (5.96-5.99; 13.408-13.414).', 'R-5.96-dont-say-part-of'),
                              (ATT_QUOTE, 'attachment-quotes', 'No quotation marks around an attachment designation (5.78).', 'R-5.78-no-emphasis-attachment-refs')):
        for m in rx.finditer(t):
            add(chk, 3, msg, m, 'high', [rid])
    if re.search(r"\b(?:Schedule|Exhibit|SCHEDULE|EXHIBIT)s?\s+[A-Z0-9]", t):
        add('attachment-check', 3, 'Attachment mentioned: confirm schedule-versus-exhibit classification, order and references (attachments.md).', None, 'low')
    for m in DMY.finditer(t):
        add('day-month-year', 2, 'Day-month-year date; house rule 7 is the U.S. form (January 1, 2027) (MSCD 10.7 differs).', m, 'high', ['R-10.7-day-month-year'])
    for m in NUMDATE.finditer(t):
        add('numeric-date', 1, 'Numerical date: 2/3/2027 can be read as February 3 or March 2; write January 1, 2027 (MSCD 10.13; house rule 7).', m, 'high', ['R-10.13-no-numerical-dates'])
    for m in THIS_DAY.finditer(t):
        add('this-day', 3, 'Archaic date form (this __ day of); write January 1, 2027 (MSCD 10.11).', m, 'high', ['R-10.11-no-this-day-of'])
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


SMALL_WORDS = r"(?:of|and|or|the|to|for|in|on|by|with|a|an|from|under|upon|as)"
# a run-in section heading (Return of Materials.  Consultant shall ...) or a heading line
RUNIN_HEAD = re.compile(r"^[*_]*[A-Z][\w'’-]*(?:\s+(?:" + SMALL_WORDS + r"|[A-Z][\w'’-]*|[;,]))*?[*_]*\.(?:\s|$)")


def has_heading(rest):
    rest = rest.strip()
    if RUNIN_HEAD.match(rest) and len(RUNIN_HEAD.match(rest).group(0).split()) <= 8:
        return True
    words = re.sub(r"[*_]+", '', rest).rstrip('.: ').split()
    return 1 <= len(words) <= 8 and all(w[0].isupper() or not w[0].isalpha() or re.fullmatch(SMALL_WORDS, w) for w in words)


ENUM_RE = re.compile(r"^[\s#>*_]*(?:(?:Article|ARTICLE|Section|SECTION)\s+)?(\d+(?:\.\d+)+\.?|[IVXLC]+\.|[A-Z]\.|\d+\.|\(\d+\)|\([a-z]{1,4}\)|\d+\))(?=\s)")


def outline_checks(paras):
    """House rule 3: I. (articles), A. (sections), 1. (subsections), (a) (clauses), (i) (subclauses); no only child."""
    items = []
    texts = [p['text'] for p in paras]
    has_roman2 = any(re.match(r"^[\s#>*_]*(?:(?:Article|ARTICLE)\s+)?II\.", x) for x in texts)
    has_small_roman2 = any(re.search(r"\(ii\)", x) for x in texts)
    last = {'upper': 0, 'lower': 0}  # value of the last roman numeral seen at each case
    last_letter = {'upper': '', 'lower': ''}  # the last letter label seen at each case

    def is_roman(core, case):
        v = roman_value(core)
        if not v:
            return False
        if len(core) > 1:
            return True  # II, IV, ix: a letter label is never 2 characters
        if last_letter[case] and ord(core) == ord(last_letter[case]) + 1:
            return False  # I. after H., V. after U.: house rule 3 uses every letter, so this is the next section
        if core.lower() == 'i':
            return has_roman2 if case == 'upper' else has_small_roman2
        return last[case] + 1 == v  # V after IV, X after IX; otherwise C, D, L, V, X are letters

    for p in paras:
        m = ENUM_RE.match(p['text'])
        if not m or p.get('where') == 'table':
            continue
        tok = m.group(1)
        core = re.sub(r"[().]", '', tok)
        if re.fullmatch(r"\d+(?:\.\d+)+\.?", tok):
            lvl, kind = 9, 'decimal'
        elif re.fullmatch(r"[IVXLC]+\.", tok) and is_roman(core, 'upper'):
            lvl, kind = 0, 'roman'; last['upper'] = roman_value(core); last_letter['upper'] = ''
        elif re.fullmatch(r"[A-Z]\.", tok):
            lvl, kind = 1, 'letter'; last_letter['upper'] = core
        elif re.fullmatch(r"\d+\.", tok):
            lvl, kind = 2, 'digit'
        elif re.fullmatch(r"\([ivxlc]+\)", tok) and is_roman(core, 'lower'):
            lvl, kind = 4, 'small-roman'; last['lower'] = roman_value(core)
        elif re.fullmatch(r"\([a-z]{1,2}\)", tok):
            lvl, kind = 3, 'small-letter'; last_letter['lower'] = core
        else:
            lvl, kind = 8, 'other'  # (1) or 1)
        items.append((p['idx'], lvl, kind, tok, m))
    out = []
    def add(idx, sev, msg, m):
        out.append({'check': 'enumeration', 'severity': sev, 'para': idx, 'match': m.group(1), 'start': m.start(1), 'end': m.end(1),
                    'message': msg, 'confidence': 'medium', 'rule_ids': ['R-4.11-article-numerals'], 'source': 'house'})
    if not items:
        return out
    first_dec = next((it for it in items if it[2] == 'decimal'), None)
    if first_dec:
        add(first_dec[0], 3, 'Decimal numbering (1.1, 1.1(a)); house rule 3 uses I. (articles), A. (sections), 1. (subsections), (a), (i).', first_dec[4])
    other = next((it for it in items if it[2] == 'other'), None)
    if other:
        add(other[0], 3, f'Enumerator {other[3]}; house rule 3 uses (a) for clauses and (i) for subclauses.', other[4])
    kinds = {it[2] for it in items}
    if 'digit' in kinds and not kinds & {'letter', 'roman'} and not first_dec:
        it = next(it for it in items if it[2] == 'digit')
        add(it[0], 3, 'Top-level sections numbered 1., 2.; house rule 3 numbers sections A., B. (under articles I., II.), and keeps 1. for subsections.', it[4])
    # only child: a level that has a 1st item but no 2nd before its parent level moves on
    ordinal = lambda tok: (re.sub(r'[().]', '', tok))
    starts = {}
    seq = [it for it in items if it[1] < 8]
    for n, it in enumerate(seq):
        idx, lvl, kind, tok, m = it
        for deeper in [k for k in list(starts) if k > lvl]:
            first, count = starts.pop(deeper)
            if count == 1:
                add(first[0], 2, f'Only child: {first[3]} has no sibling at its level (house rule 3).', first[4])
        if lvl in starts and starts[lvl][0][2] == kind:
            starts[lvl] = (starts[lvl][0], starts[lvl][1] + 1)
        else:
            starts[lvl] = (it, 1)
    for lvl, (first, count) in starts.items():
        if count == 1 and lvl > min(it[1] for it in seq):
            add(first[0], 2, f'Only child: {first[3]} has no sibling at its level (house rule 3).', first[4])
    # each section needs a heading (MSCD 4.21); house rule 4 refers to provisions by heading
    secs = [it for it in items if it[2] == 'decimal' and it[3].rstrip('.').count('.') == 1]
    if not secs and seq:
        lv = 1 if any(it[2] == 'roman' for it in items) else min(it[1] for it in seq)
        secs = [it for it in seq if it[1] == lv]
    text_of = {p['idx']: p['text'] for p in paras}
    att = next((p['idx'] for p in paras if EXHIBIT_HEAD.match(p['text'])), len(paras))
    secs = [it for it in secs if it[0] < att and not re.match(r"\s*\*{0,2}[\"“]", text_of[it[0]][it[4].end():])]  # skip attachments and autonomous definitions
    bare = [it for it in secs if not has_heading(text_of[it[0]][it[4].end():])]
    if len(secs) >= 2 and bare:
        it = bare[0]
        out.append({'check': 'section-headings', 'severity': 2, 'para': it[0], 'match': it[4].group(1), 'start': it[4].start(1), 'end': it[4].end(1),
                    'message': f'{len(bare)} of {len(secs)} sections have no heading. Give each section a heading (MSCD 4.21); house rule 4 refers to provisions by heading, so a section without one can\'t be referred to.',
                    'confidence': 'medium', 'rule_ids': ['R-4.21-section-heading-format'], 'source': 'house'})
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

INTEG = re.compile(r"\((?:each,?\s+)?(?:the|a|an)?\s*\*{0,2}[\"“‘']\*{0,2}([^\"”’']{1,60}?)\*{0,2}[\"”’']\*{0,2}")
AUTON = re.compile(r"^\s*\*{0,2}[\"“‘']\*{0,2}([^\"”’']{1,60}?)\*{0,2}[\"”’']\*{0,2}\s+(?:means|includes|has the meaning|shall mean|shall have)")
CONTRACT_NOUN = re.compile(r"\b(?:Information|Agreement|Date|Period|Price|Assets?|Software|Services?|Products?|Effect|Event|Change|Claims?|Losses|Fees?|Rent|Term|Territory|Data|Materials|Property|Rights|Work|Deliverables?|Documentation|Units?|Shares|Amount|Account|Plan|Certificate|Statement|Orders?|Budget|Report|Specifications|Equipment|Goods|Premises|Interest|Payment|Expenses|Release|Cause|Reason|Disability|Control|Default|Closing|Obligations|Liabilities|Approval|Notice)\b")
EXHIBIT_HEAD = re.compile(r"^[\s#*_]*(?:EXHIBIT|Exhibit|SCHEDULE|Schedule|ANNEX|Annex|APPENDIX|Appendix)\s+[A-Z0-9]+[\s*_]*(?:$|[-\u2014\u2013:]|\s{2,})")


def _variants(term):
    """The term as defined plus its singular, plural and possessive forms (15.23: singular includes plural)."""
    forms = {term, term + 's', term + 'es'}
    if term.endswith('ies'):
        forms.add(term[:-3] + 'y')
    elif term.endswith('s'):
        forms.add(term[:-1])
    if term.endswith('y'):
        forms.add(term[:-1] + 'ies')
    return r"\b(?:" + '|'.join(sorted(map(re.escape, forms), key=len, reverse=True)) + r")(?:['’]s)?\b"


def inventory(paras):
    defs, in_exhibit = {}, False
    for p in paras:
        if EXHIBIT_HEAD.match(p['text']):
            in_exhibit = True  # a stand-alone form defines its own terms; don't count those as duplicates
        if in_exhibit:
            continue
        for m in INTEG.finditer(p['text']):
            defs.setdefault(m.group(1).strip(), []).append(('integrated', p['idx']))
        m = AUTON.match(TYPED_NUM.sub('', p['text'], count=1))  # allow a typed enumerator before the definition (A. "X" means)
        if m:
            defs.setdefault(m.group(1).strip(), []).append(('autonomous', p['idx']))
    full = '\n'.join(p['text'] for p in paras)
    # text for the undefined-term check: skip headings, run-in headings and signature lines
    prose = '\n'.join(re.sub(r"^[\s#*_>]*(?:(?:Section|SECTION|Article|ARTICLE)\s+)?(?:\(?[A-Za-z0-9]{1,4}[.)]\s+|\d+(?:\.\d+)+\.?\s+)?[*_]*[A-Z][\w'’-]*(?:\s+(?:" + SMALL_WORDS + r"|[A-Z][\w'’-]*)){0,6}[*_]*\.\s+", '', p['text'])
                      for p in paras if len(p['text'].split()) > 8 or p['text'].rstrip().endswith('.'))
    prose = re.sub(r"\b(?:titled|headed|entitled)\s+[\"“][^\"”]{1,80}[\"”]", 'titled', prose)  # a heading named in a reference (the section titled "Termination for Cause")
    rows, findings = [], []

    def locate(text, cased=True):
        # the 1st place a phrase occurs, so a document-level finding can point at real text
        rx = re.compile(r"(?<![\w-])" + re.escape(text) + r"(?![\w-])", 0 if cased else re.I)
        for p in paras:
            m = rx.search(p['text'])
            if m:
                return {'para': p['idx'], 'start': m.start(), 'end': m.end()}
        return {'para': -1}
    for term, where in sorted(defs.items()):
        cap = len(re.findall(_variants(term), full)) - len(where)
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
        findings.append({'check': 'shall-in-definition', 'severity': 2, **locate(m.group(0)), 'match': m.group(0)[:80],
                         'message': 'Use means, not shall mean or shall be, in a definition (6.33-6.42; blog).', 'confidence': 'high', 'rule_ids': [], 'source': 'inventory'})
    caps = collections.Counter(m.group(0) for m in re.finditer(r"(?<![.?!:]\s)(?<![.?!:]\s\s)(?<!^)(?<!\n)\b(?:[A-Z][a-z]+)(?:\s+[A-Z][a-z]+){0,3}\b", prose))
    known = set(defs) | {v for t in defs for v in (t + 's', t[:-1] if t.endswith('s') else t)} | PARTY_TERMS
    for phrase, c in caps.items():
        if phrase in known or not CONTRACT_NOUN.search(phrase):
            continue
        if re.search(re.escape(phrase) + r"(?:,?\s+(?:" + ENTITY + r"|Company|Corporation|Bank)|\.?\s*\()", full) or re.search(r"\s(?:Corp|Inc|Co|Ltd)$", phrase):
            continue  # a business name (Front Range Equipment Finance, LLC), or a name defined in the next parenthetical
        if re.search(r"(?:^|\s)(?:Agreement|Addendum|Amendment)$", phrase) or phrase.split()[0] in ('This', 'The', 'These', 'Those'):
            continue  # the contract's own title, or a sentence-initial article
        part_of = [k for k in known if k in phrase and k != phrase]
        if part_of and re.search(r"\b[A-Z][a-z]+\s+" + re.escape(part_of[0]) + r"\b|\b" + re.escape(part_of[0]) + r"\s+[A-Z][a-z]+", phrase):
            findings.append({'check': 'possibly-undefined-term', 'severity': 1, **locate(phrase), 'match': phrase,
                             'message': f'"{phrase}" looks like a 2nd form of the defined term "{part_of[0]}"; use 1 form throughout (MSCD 1.57; 6.122).',
                             'confidence': 'medium', 'rule_ids': ['R-1.57-one-word-one-meaning'], 'source': 'inventory'})
            continue
        if any(phrase in k for k in known):
            continue
        if phrase.split()[0] in ('This', 'The', 'Each', 'Any', 'All', 'No', 'If', 'In', 'On', 'Section', 'Schedule', 'Exhibit', 'Article'):
            continue
        if re.search(r"(?:^|\s)(?:Agreement|Addendum|Amendment)$", phrase):
            continue  # the contract's own title, or another agreement's name; MSCD's lowercase-agreement rule covers it
        if c >= 1:
            findings.append({'check': 'possibly-undefined-term', 'severity': 1, **locate(phrase), 'match': phrase,
                             'message': f'"{phrase}" is capitalized {c} times but not defined; define it, or lowercase it; ignore it if it is a name (6.122).', 'confidence': 'low', 'rule_ids': [], 'source': 'inventory'})
    return rows, findings

# ---------------------------------------------------------------- report

def report(path, paras, meta, findings, broad, inv):
    sev_name = {1: 'Severity 1: must fix (ambiguity, meaning-changing)', 2: 'Severity 2: should fix (vagueness, dispute risk, house rules)', 3: 'Severity 3: style'}
    nd = sum(1 for f in findings if f['source'] != 'rules')
    lines = [f'# Lint report: {os.path.basename(path)}', '',
             f'{len(paras)} paragraphs read; {nd} direct findings (house rules, word checks, inventory) and {len(findings) - nd} rule triggers. All are candidates: confirm each in context before acting.',
             'Paragraphs are numbered from 0 (the title is usually para 0); para -1 means the finding is about the whole document.', '']
    if meta:
        nf, ns = meta.get('normal_font'), meta.get('normal_size')
        if (nf and nf.lower() != 'aptos') or (ns and abs(ns - 12) > 0.01):
            lines.append(f'- Document default font: {nf} {ns} pt (house rule: 12-point Aptos).')
        if meta.get('auto_numbered'):
            lines.append(f"- {meta['auto_numbered']} paragraphs use Word's automatic numbering, which the lint can't read: check their numbering (house rule 3), only children and section headings in Word.")
        if meta.get('tracked_changes'):
            lines.append('- The document has tracked changes; the text was read as if every change were accepted. Ask Blake whether to accept them first or redline on top.')
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
        for f in sorted(fs, key=lambda f: (f['para'], f['check'])):
            txt = paras[f['para']]['text'][:90].replace('\n', ' ') if 0 <= f['para'] < len(paras) else ''
            lines.append(f"- para {f['para']} · sev {f['severity']} · {f['check']} · \"{f['match']}\" · {f['message']}" + (f" · rules: {', '.join(f['rule_ids'])}" if f['rule_ids'] else '') + (f" · [{f['confidence']}]" if f['confidence'] != 'high' else ''))
            if txt: lines.append(f'  - context: {txt}')
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
    'reduced-passive': 3,
}
OWN_SEV = {'term-of-art', 'within-after'}  # elaborations that set their own severity case by case


def apply_severity(findings):
    for f in findings:
        if f['source'] == 'rules' or f['check'] in OWN_SEV or f.get('keep_sev'):
            continue
        if f['check'] in HOUSE_SEV:
            f['severity'] = HOUSE_SEV[f['check']]
        elif f['rule_ids'] and f['rule_ids'][0] in _SEV:
            f['severity'] = _SEV[f['rule_ids'][0]]
    return findings


EFFORTS_STD = re.compile(r"\b((?:commercially\s+|all\s+|every\s+|very\s+)?reasonable(?:\s+best|\s+commercial)?|best|good[- ]faith|diligent)\s+(?:efforts|endeavou?rs)\b", re.I)


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
    (p, m) = list(seen.values())[1]
    return [{'check': 'efforts-mixed', 'severity': 1, 'para': p['idx'], 'match': m.group(0), 'start': m.start(), 'end': m.end(),
             'message': f'{len(seen)} efforts standards in 1 contract ({"; ".join(seen)}): a reader may infer they differ. Use reasonable efforts throughout (MSCD 8.154; 8.1).',
             'confidence': 'high', 'rule_ids': ['R-8.154-one-efforts-standard'], 'source': 'house'}]


def run(path, want_inventory):
    paras, meta = read_paragraphs(path)
    findings = []
    global PARTY_TERMS
    PARTY_TERMS = party_terms(paras)
    for p in paras:
        if p['text'].strip():
            findings += house_checks(p)
    findings += outline_checks(paras)
    findings += front_checks(paras, meta)
    findings += efforts_mix(paras)
    n_auto = sum(1 for p in paras if (p.get('fmt') or {}).get('auto_numbered') and p['text'].strip())
    if n_auto:
        meta = dict(meta, auto_numbered=n_auto)
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
    return paras, meta, collapse(apply_severity(findings)), broad, inv


PER_DOC = {'font', 'font-size', 'justified', 'underline', 'bold-definition'}


def collapse(findings):
    """Report a repeated finding once, with every location, so the report stays short (a template can repeat
    the same problem 40 times). Each collapsed finding keeps all its locations in 'occurrences'."""
    out, seen = [], {}
    for f in findings:
        if f['source'] == 'rules':
            key = ('rule', f['rule_ids'][0] if f['rule_ids'] else f['check'])
        elif f['check'] in PER_DOC:
            key = ('doc', f['check'])
        else:
            key = (f['check'], f['match'].lower(), f['message'])
        loc = (f['para'], f.get('start', -1), f.get('end', -1), f['match'])
        if key in seen:
            g = seen[key]; g['occurrences'].append(loc); continue
        g = dict(f, occurrences=[loc]); seen[key] = g; out.append(g)
    for g in out:
        n = len(g['occurrences'])
        if n > 1:
            paras_ = sorted({o[0] for o in g['occurrences'] if o[0] >= 0})
            g['message'] = g['message'] + f' ({n} places: paras {", ".join(map(str, paras_[:15]))}{"..." if len(paras_) > 15 else ""})'
    return out


ENTITY = r"(?:Inc\.|LLC|L\.L\.C\.|LLP|L\.L\.P\.|LP|L\.P\.|Ltd\.|Corp\.|Co\.|P\.A\.|P\.C\.|PLLC|N\.A\.)"
# a party name in the introductory clause: before ", a Delaware corporation" or before its defined-term parenthetical
INTRO_NAME = re.compile(r"(?:between|and)\s+([A-Z][\w.&'’ -]{1,60}?(?:,?\s+" + ENTITY + r")?)(?=,\s+(?:a|an)\s+|\s*\()")


def front_checks(paras, meta):
    """The front and the definitions: title (2.2), party names in capitals (2.51), lead-in (2.159), bold defined terms (2.92)."""
    out = []
    def add(check, sev, msg, p, m=None, rules=()):
        out.append({'check': check, 'severity': sev, 'para': p['idx'] if p else -1, 'match': (m.group(0) if m else '')[:80],
                    'start': m.start() if m else -1, 'end': m.end() if m else -1, 'message': msg, 'confidence': 'medium',
                    'rule_ids': list(rules), 'source': 'house'})
    body = [p for p in paras if p['text'].strip()]
    if not body:
        return out
    title = body[0]
    tt = re.sub(r"^[#\s*_]+|[*_]+$", '', title['text']).strip()
    if 2 <= len(tt.split()) <= 10 and not re.search(r"\b(?:between|dated|is|are)\b", tt):
        if tt != tt.upper():
            add('front', 3, 'Title: put it in all capitals (MSCD 2.2).', title, None, ['R-2.2-title-format'])
        if 'centered' in (title.get('fmt') or {}) and not title['fmt']['centered']:
            add('front', 3, 'Title: center it at the top of the 1st page (MSCD 2.2).', title, None, ['R-2.2-title-format'])
    intro = next((p for p in body[:6] if re.search(r"\bbetween\b", p['text']) and re.search(r"\(", p['text'])), None)
    if intro:
        for m in INTRO_NAME.finditer(intro['text']):
            name = m.group(1)
            if name != name.upper() and not re.fullmatch(r"(?:the\s+)?\w+", name) and not re.search(r"[a-z][A-Z]", name):
                add('front', 3, f'Introductory clause: state the party name in all capitals ({name.upper()}) (MSCD 2.51).', intro, m, ['R-2.51-names-in-capitals'])
        if not any(re.search(r"agrees?\s+as\s+follows", p['text'], re.I) for p in body):
            add('front', 3, 'No lead-in: add "The parties agree as follows:" after the introductory clause (MSCD 2.159).', intro, None, ['R-2.159-lead-in'])
    unbolded, in_exhibit = [], False
    for p in body:
        f = p.get('fmt') or {}
        if EXHIBIT_HEAD.match(p['text']):
            in_exhibit = True  # a form attached as an exhibit keeps its own format
        if 'bold_text' not in f or in_exhibit:
            continue
        cands = list(INTEG.finditer(p['text']))
        am = AUTON.match(TYPED_NUM.sub('', p['text'], count=1))
        if am:
            cands += [x for x in [re.search(re.escape(am.group(1)), p['text'])] if x]
        for m in cands:
            term = (m.group(1) if m.re is not None and m.lastindex else m.group(0)).strip()
            if term and term not in f['bold_text']:
                unbolded.append((p, m))
    if unbolded:
        p, m = unbolded[0]
        add('bold-definition', 3, f'Defined term not in bold where it is defined ({len(unbolded)} definitions, integrated and autonomous); bold the term, not the quotation marks (MSCD 2.92; 6.31).', p, m, ['R-2.92-party-term-format', 'R-6.31-quote-and-bold'])
    return out


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
        ('The Assets listed on Schedule A are excluded.', 'attachment-on', True),
        ('The form attached hereto as Exhibit 2 governs.', 'attachment-hereto', True),
        ('The list in schedule A governs.', 'attachment-capitals', True),
        ('This agreement is dated 1 January 2027.', 'day-month-year', True),
        ('Acme shall pay. Widgetco shall deliver.', 'spacing', True),
        ('Acme shall pay.  Widgetco shall deliver.', 'spacing', False),
        ('Acme Inc. shall pay.', 'spacing', False),
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
        ('Acme shall pay the Fee no later than 30 days after the Closing.', 'time-ambiguity', False),
        ('The Term runs from January 1, 2027 to March 31, 2027.', 'time-ambiguity', True),
        ('This agreement shall be governed by Tennessee law.', 'category-shall', True),
        ('It is understood and agreed that Acme is an independent contractor.', 'throat-clearing', True),
        ('Acme hereby grants Widgetco a license.', 'archaic', False),
        ('The parties hereto agree as follows.', 'archaic', True),
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
        ('Acme shall pay within 30 days of the Closing.', 'time-ambiguity', True),
        ('Acme shall pay within 30 days after the Closing.', 'time-ambiguity', False),
        ('Acme shall pay within ten (10) days after the Closing.', 'within-after', True),
        ('This Distribution Agreement (this "Agreement") is dated', 'this-agreement-term', True),
        ('Landlord and Tenant are parties to a lease (the "Lease") for Suite 210.', 'this-agreement-term', False),
        ('THIS CONSULTING AGREEMENT (the "Agreement") is made', 'this-agreement-term', True),
        ('Acme shall use good-faith efforts to obtain the consent.', 'efforts', True),
        ('Acme shall use reasonable efforts to obtain the consent.', 'efforts', False),
        ('The payment is due on 2/3/2027.', 'numeric-date', True),
        ('Acme shall continue providing the Services during the dispute.', 'category-shall', False),
        ('Acme shall terminate the subcontract if Widgetco fails to pay.', 'category-shall', False),
        ('Acme shall commence the Work on May 1, 2027.', 'category-shall', False),
        ('This agreement shall terminate on December 31, 2027.', 'category-shall', True),
        ('The term shall continue for 2 years.', 'category-shall', True),
        ('Interest shall accrue on the unpaid principal balance.', 'category-shall', True),
        ('The Installer shall not assert the same in any later proceeding.', 'same-pronoun', True),
        ('Acme shall pay the same fee as Widgetco.', 'same-pronoun', False),
        ('The Client shall reimburse travel expenses incurred by the Consultant.', 'reduced-passive', True),
    ]
    sev_cases = [  # severity policy: house severity for house rules, else the rule record's
        ('Acme shall pay the Price. If Acme shall fail to pay, Widgetco may terminate.', 'shall-in-condition', 3),
        ('Acme shall deliver the Widgets, the Gadgets, and/or the Gizmos.', 'and-or', 1),
        ('Acme shall purchase Widget A and/or Widget B.', 'and-or', 2),
        ('Acme shall use its best efforts to sell the Units.', 'efforts', 1),
        ('The Units will be delivered to Widgetco.', 'passive-voice', 2),
        ('Acme shall pay within ten (10) days after the Closing.', 'within-after', 3),
        ('The form attached hereto as Exhibit 2 governs.', 'attachment-hereto', 3),
        ('The payment is due on 2/3/2027.', 'numeric-date', 1),
        ('If Acme should exercise the Option, Widgetco shall pay.', 'should', 3),
        ('Acme should deliver the Units by noon.', 'should', 1),
        ('The Company shall pay Widgetco.', 'party-article', 2),
    ]
    fails = 0
    for text, check, expect in cases:
        got = any(f['check'] == check for f in house_checks({'idx': 0, 'text': text, 'fmt': {}}))
        if got != expect:
            fails += 1; print(f'FAIL: {check} expected {expect} for: {text}')
    for text, check, want in sev_cases:
        fs = [f for f in apply_severity(house_checks({'idx': 0, 'text': text, 'fmt': {}})) if f['check'] == check]
        if not fs or int(fs[0]['severity']) != want:
            fails += 1; print(f'FAIL (severity): {check} expected {want}, got {[f["severity"] for f in fs]} for: {text}')
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
    ]
    for ext, body, wants in whole:
        with tempfile.NamedTemporaryFile('w', suffix=ext, delete=False, encoding='utf-8') as fh:
            fh.write(body); tmp = fh.name
        try:
            fs = run(tmp, True)[2]
        finally:
            os.unlink(tmp)
        for check, want in wants.items():
            got = any(f['check'] == check and (check != 'front' or 'capitals (' in f['message']) for f in fs)
            if got != want:
                fails += 1; print(f'FAIL (document): {check} expected {want} for: {body[:60]}')
    # House rule 3 uses every letter: section I. after H. is a section, not an article.
    # Section I. has no heading on purpose: the heading check sees it only if the outline reads it as a section.
    secs9 = ''.join(f'{c}. {h}.  Acme shall do task {n}.\n\n' for n, (c, h) in enumerate(zip('ABCDEFGH', ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel']), 1)) + 'I. Acme shall do task 9.\n\n'
    body9 = 'I. FIRST ARTICLE\n\n' + secs9 + 'II. SECOND ARTICLE\n\nA. Kilo.  Acme shall pay.\n\nB. Lima.  Acme shall sign.\n'
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8') as fh:
        fh.write(body9); tmp = fh.name
    try:
        fs9 = run(tmp, False)[2]
    finally:
        os.unlink(tmp)
    outline_extra = 1
    heads9 = [f for f in fs9 if f['check'] == 'section-headings']
    if any(f['check'] == 'enumeration' for f in fs9) or not heads9 or not heads9[0]['message'].startswith('1 of 11 sections'):
        fails += 1; print('FAIL (outline): section I. after H. was not read as a section: ' + '; '.join(f['message'][:80] for f in fs9 if f['check'] in ('enumeration', 'section-headings')))
    # A definition after a typed enumerator still enters the inventory.
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8') as fh:
        fh.write('A. "Confidential Information" means any technical information.\n\nB. Acme shall protect the Confidential Information.\n'); tmp = fh.name
    try:
        rows = run(tmp, True)[4]
    finally:
        os.unlink(tmp)
    if not any(r['term'] == 'Confidential Information' for r in rows):
        fails += 1; print('FAIL (run): definition after "A." missing from the inventory')
    # Paragraphs inside a content control or a revision wrapper are read.
    try:
        import docx as _docx
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn as _qn
        dd = _docx.Document(); dd.add_paragraph('Acme shall pay the Price.')
        p2 = dd.add_paragraph('Widgetco shall deliver the Units.')
        sdt, content = OxmlElement('w:sdt'), OxmlElement('w:sdtContent'); sdt.append(content); p2._p.addprevious(sdt); content.append(p2._p)
        p3 = dd.add_paragraph('Lee shall sign the Note.')
        ins = OxmlElement('w:ins'); ins.set(_qn('w:id'), '9'); ins.set(_qn('w:author'), 'X'); ins.set(_qn('w:date'), '2026-01-01T00:00:00Z')
        p3._p.addprevious(ins); ins.append(p3._p)
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as fh:
            tmp = fh.name
        dd.save(tmp)
        texts = [p['text'] for p in read_paragraphs(tmp)[0]]
        os.unlink(tmp)
        if texts != ['Acme shall pay the Price.', 'Widgetco shall deliver the Units.', 'Lee shall sign the Note.']:
            fails += 1; print(f'FAIL: wrapped paragraphs not read in order: {texts}')
    except ImportError:
        pass
    total_extra = 2
    try:
        read_paragraphs('contract.pdf'); fails += 1; print('FAIL: a .pdf was accepted')
    except ValueError:
        pass
    total = len(cases) + len(sev_cases) + len(doc_cases) + sum(len(w[2]) for w in whole) + 1 + total_extra + outline_extra
    print(f'self-test: {total - fails}/{total} passed')
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('path', nargs='?')
    ap.add_argument('--json', help='also write findings as JSON to this path')
    ap.add_argument('--inventory', action='store_true')
    ap.add_argument('--whose', choices=['blake', 'other-side'], help="whose draft it is; tailors the represents-and-warrants finding")
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.path:
        ap.print_usage(); return 5
    try:
        global WHOSE
        WHOSE = a.whose
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
