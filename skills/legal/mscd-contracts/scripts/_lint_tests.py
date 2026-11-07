#!/usr/bin/env python3
"""The self-test for mscd_lint.py: every case the linter must keep passing.

`python3 mscd_lint.py --self-test` imports self_test() from here and prints 1 line ("self-test: N/N passed"),
exiting 1 on any failure. The groups below follow the hardening rounds that found the cases. Nothing here runs
at import time, so the linter itself pays nothing for the test suite.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # the linter sits beside this file
import mscd_lint as L  # noqa: E402


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
    deeper = [f for f in L.outline_checks(word, L.document_shape(word)) if 'Only child' in f['message']]
    word[10]['auto_level'] = 2  # Word numbers (i) at the same level as (h): the letter i, so (ii) is a lone subclause
    same = [f for f in L.outline_checks(word, L.document_shape(word)) if 'Only child' in f['message']]
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
    out.append(('IMPORTS reads "Each capitalized term"', bool(L.IMPORTS.search('Each capitalized term used in this amendment has the meaning given in the Agreement.'))))
    # C10: the phrase-variants file with the wrong shape is a data error
    out.append(('a phrase-variants file that is a list, or has no checks list, is an InputError', all(_raises(L.InputError, lambda d=d: L._variant_entries(d)) for d in ([], {'about': 'x'}, {'checks': 'x'})) and L._variant_entries({'checks': []}) == []))
    # C12: 2 patterns reading 1 definition are not a term defined twice; a term really defined twice in 1 paragraph is
    res = run_text(intro + '.\n\nSeller shall lease the Premises for 3 years (the "Term" is 3 years), and Buyer shall pay Rent during the Term.\n\nA. Definitions.  "Unit" means a widget.  "Unit" means a gadget.  Seller shall deliver each Unit.\n')
    out.append(('defined-twice: deduped on (kind, paragraph, position); a real repeat in 1 paragraph still counts', [f['match'] for f in res[2] if f['check'] == 'defined-twice'] == ['Unit']))
    # C13: shall after a closing quotation mark in the next paragraph is not shall in a definition
    res = run_text(intro + '.\n\nSeller shall deliver the goods listed under the heading "Goods"\n\nshall be void if Buyer fails to pay.\n\n"Unit" shall mean a widget.  Seller shall deliver each Unit.\n')
    out.append(('shall-in-definition never spans 2 paragraphs', [f['match'] for f in res[2] if f['check'] == 'shall-in-definition'] == ['"Unit" shall mean']))
    # C14, R3: a Markdown table's Total cell is located, not the 1st $80 in the table; a pipe table without outer pipes is read
    t = '| Item | Amount |\n|---|---|\n| Fee | $80 |\n| Credit | $20 |\n| Total | $80 |'
    f_ = L.table_total_checks([{'idx': 0, 'text': t}], None)
    out.append(('Markdown table: the finding points at the Total cell', len(f_) == 1 and f_[0]['start'] == t.rfind('$80') and t[f_[0]['start']:f_[0]['end']] == '$80'))
    t2 = 'Item | Amount | Note\n--- | --- | ---\nSetup | $100.00 | x\nSupport | $200.00 | y\nTotal | $400.00 |'  # a rate row (Monthly) would be no sum (PER_PERIOD)
    f_ = L.table_total_checks([{'idx': 0, 'text': t2}], None)
    out.append(('Markdown table without outer pipes is read; a sentence with a pipe is not a table', len(f_) == 1 and t2[f_[0]['start']:f_[0]['end']] == '$400.00'
                and not L.table_total_checks([{'idx': 0, 'text': 'Acme | Beta shall pay $5 | Total $5'}], None)))
    # C15: obligation-in-definition's match is the text at its offsets
    res = run_text(intro + '.\n\n"Approved Budget" means the budget in Schedule A, which Buyer shall approve in writing.  Seller shall follow the Approved Budget.\n')
    oid = [f for f in res[2] if f['check'] == 'obligation-in-definition']
    out.append(('obligation-in-definition: match == text[start:end], context in the message', len(oid) == 1 and res[0][oid[0]['para']]['text'][oid[0]['start']:oid[0]['end']] == oid[0]['match'] == 'shall' and 'which Buyer shall approve' in oid[0]['message']))
    # C19 is in cases; C5, C8, C9, C11 are in the variants' examples and look-alikes
    # R10: the bounded regex hints run in linear time on a 20,000-digit run; a paragraph over RULE_PARA_MAX skips the triggers with a note
    import time
    t0 = time.monotonic()
    for r, rx in L.load_rules()[0]:
        rx.search('9' * 20000)
        rx.search('$1 ' * 5000)
    out.append(('every rule trigger runs in under 2 seconds each on 20,000 digits (no quadratic hint)', time.monotonic() - t0 < 2 * len(L.load_rules()[0])))
    res = run_text(intro + '.\n\n' + 'Seller shall deliver the Units and/or the Parts. ' * 300 + '\n\nBuyer shall pay.\n', False)
    out.append(('a paragraph over 10,000 characters skips the rule triggers, with a note', res[1].get('long_paras') == [1] and any('over 10,000 characters' in n for n in L.report_notes(res[1], res[0]))
                and any(f['check'] == 'and-or' and f['para'] == 1 for f in res[2])))
    # R11: a fenced code block in Markdown is not contract text
    res = run_text('# AGREEMENT\n\n' + intro + '.\n\n```\nSeller shall pay the Rent within thirty (30) days.\n```\n\nSeller shall deliver.\n', False, '.md')
    out.append(('a fenced code block is dropped, with a note', res[1].get('code_blocks') == 1 and not any(f['check'] == 'words-and-digits' for f in res[2]) and [p['text'] for p in res[0]][-1] == 'Seller shall deliver.'))
    # S1: every rule id the code and the variants cite exists in the rule database
    src = ''
    for f_src in (L.__file__, os.path.abspath(__file__)):  # the rule ids cited by the linter and by this test file
        with open(f_src, encoding='utf-8') as fh:
            src += fh.read()
    cited = set(re.findall(r"'(R-[\w.]+-[\w.-]+)'", src)) | {r for c in L.phrase_variants() for r in c['rule_ids']}
    out.append(('every rule id cited by the code tables and the variants exists in the rule database', all(r in L._SEV for r in cited) and len(cited) > 50))
    # S2: collapse keeps a 2nd distinct bold-definition message and the document-default font beside a paragraph's font
    two = [{'check': 'bold-definition', 'severity': 3, 'para': 1, 'match': 'Acme', 'message': 'unbolded', 'confidence': 'medium', 'rule_ids': [], 'source': 'house'},
           {'check': 'bold-definition', 'severity': 3, 'para': 2, 'match': 'Beta', 'message': 'bold quotation marks', 'confidence': 'medium', 'rule_ids': [], 'source': 'house'},
           {'check': 'font', 'severity': 3, 'para': 1, 'match': '', 'message': 'Font Arial', 'confidence': 'high', 'rule_ids': [], 'source': 'house'},
           {'check': 'font', 'severity': 3, 'para': 2, 'match': '', 'message': 'Font Arial', 'confidence': 'high', 'rule_ids': [], 'source': 'house'},
           {'check': 'font', 'severity': 3, 'para': -1, 'match': '', 'message': 'Document default font is Arial', 'confidence': 'high', 'rule_ids': [], 'source': 'house'}]
    out.append(('collapse keeps distinct per-document messages', [(g['check'], g['message'], len(g['occurrences'])) for g in L.collapse(two)]
                == [('bold-definition', 'unbolded', 1), ('bold-definition', 'bold quotation marks', 1), ('font', 'Font Arial (2 places in 2 paragraphs: paras 1, 2)', 2), ('font', 'Document default font is Arial', 1)]))
    # S5: front findings on a contract with a 9-line table of contents before the introductory clause
    toc = ''.join(f'Article {n} Heading {n}\n\n' for n in range(1, 10))
    res = run_text(toc + 'This agreement is dated January 1, 2027, and is between Acme Widgets, Inc. ("Acme") and Widgetco LLC ("Widgetco").\n\nAcme shall sell the Units to Widgetco.\n', False)
    fr = [f['message'] for f in res[2] if f['check'] == 'front']
    out.append(('front findings (capitals, lead-in) appear behind a 9-line table of contents', any('capitals (' in m for m in fr) and any('No lead-in' in m for m in fr)))
    # load test: a pasted 1-line clause is a sentence, not a title; a real short title still draws the capitals finding
    one = [f for f in run_text('Neither party may assign this agreement.\n', False)[2] if f['check'] == 'front' and 'capitals (' in f['message']]
    ttl = [f for f in run_text('Services Agreement\n\nThis agreement is dated January 1, 2027, and is between Acme Widgets, Inc. ("Acme") and Widgetco LLC ("Widgetco").\n', False)[2] if f['check'] == 'front' and 'capitals (' in f['message']]
    out.append(('a pasted 1-line clause draws no title finding; a short real title in mixed case still does', not one and bool(ttl)))
    # S6: the sentence forms of a definition reach the term-of-art and circular checks
    res = run_text(intro + '.\n\nEach task that Seller gives Buyer is an "Assignment."  Buyer may not assign this agreement.\n\nThe "Carrier List" is the list of Approved Carriers.  The "Approved Carrier" is a carrier on the Carrier List.\n')
    out.append(('a term defined with is an "X" reaches the term-of-art check; the "X" is forms reach the circular check',
                any(f['check'] == 'term-of-art-defined' and f['match'] == 'Assignment' for f in res[2]) and any(f['check'] == 'circular-definition' for f in res[2])))
    # S7: single-quoted definitions count
    res = run_text(intro + ".\n\n'Deliverable' means each item in Schedule A.  Seller shall deliver each Deliverable at the closing (the 'Closing').  The Closing is on March 1, 2027.\n")
    out.append(("single-quoted definitions ('Deliverable' means; (the 'Closing')) enter the inventory", {'Deliverable', 'Closing'} <= {r['term'] for r in res[4]}
                and not any(f['check'] == 'possibly-undefined-term' and f['match'] in ('Deliverable', 'Closing') for f in res[2])))
    # S9: run() restores WHOSE; load_rules() is cached
    before = L.WHOSE
    rw = intro + '.\n\nSeller represents and warrants that it owns the Shares.\n'
    other = [f for f in lint_text(rw, whose='other-side')[2] if f['check'] == 'represents-warrants']
    mine = [f for f in lint_text(rw, whose='blake')[2] if f['check'] == 'represents-warrants']
    out.append(('--whose: other-side keeps represents and warrants (sev 3); blake gets the states finding (sev 2); run() restores WHOSE',
                other and other[0]['severity'] == 3 and 'Keep' in other[0]['message'] and mine and mine[0]['severity'] == 2 and 'use states' in mine[0]['message'] and L.WHOSE == before))
    out.append(('load_rules() is cached', L.load_rules() is L.load_rules()))
    # S13: severity ownership: an explicit severity is kept; a house rule or the rule record decides otherwise
    out.append(('severity_for: explicit, house, rule record, default', L.severity_for('x', [], 1) == 1 and L.severity_for('party-article', []) == 2
                and L.severity_for('x', ['R-3.89-shall-duty']) == L._SEV['R-3.89-shall-duty'] and L.severity_for('x', ['R-none']) == 3 and L.sev_is_free('x', ['R-none']) and not L.sev_is_free('party-article', [])))
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
    k = L.collapse([L.finding('font', 'Font Arial', 15, sev=3, match='x', start=0, end=1), L.finding('font', 'Font Arial', 15, sev=3, match='y', start=5, end=6)])
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
    out.append(('comment text is kept whole; the report shortens it with ...', L._shorten('x' * 400, L.COMMENT_SHOWN).endswith('...') and L._shorten('short', L.COMMENT_SHOWN) == 'short'))
    many = [('A', f'comment {n}', None) for n in range(12)] + [('B', 'reply', 11)]
    notes = L.report_notes({'comments': many}, [])
    out.append(('the comments list says how many more it holds (ROB-010)', any(n.startswith('  - ... and 2 more comments') for n in notes)
                and not any('more comments' in n for n in L.report_notes({'comments': many[:10]}, []))))
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
    cs = [f for f in L.house_checks({'idx': 0, 'text': 'Final Completion shall occur no later than July 31, 2027.', 'fmt': {}}) if f['check'] == 'category-shall']
    out.append(('category-shall on a thing or event offers must (MSCD 3.154) and keeps R-3.98 first (ACC-003)',
                cs and 'write must' in cs[0]['message'] and cs[0]['rule_ids'] == ['R-3.98-shall-future-time', 'R-3.154-must-for-others'] and cs[0]['severity'] == 3))
    # ROB-001: invisible characters are stripped and counted
    res = lint_text(intro + 'Seller shall protect the information (the "Confi\u00addential Information").  Buyer shall keep the Confidential Information secret.  Seller shall return the Confidential Information.  Buyer may use the Confidential\u200b Information.\n', inventory=True)
    out.append(('a soft hyphen and a zero-width space are removed and noted: no 2nd form, no unused term (ROB-001)',
                res[1].get('invisible_chars') == 2 and any('invisible characters' in n for n in L.report_notes(res[1], res[0]))
                and not any(f['check'] in ('possibly-undefined-term', 'defined-unused') for f in res[2])))
    # ROB-002: quoted, section-numbered and 1-line form labels are attachment headings; a reference in running text is not
    quoted = intro + 'Seller shall deliver the release in Exhibit 1.\n\nEXHIBIT "1"\n\nFORM OF RELEASE\n\n"Agreement" means the asset purchase agreement.  Executive gives this release under the Agreement.\n'
    out.append(('EXHIBIT "1" (a quoted label) is an exhibit heading: its definitions are not defined twice (ROB-002)', not checks_of(quoted, True, want={'defined-twice'})
                and L.EXHIBIT_HEAD.match('SCHEDULE 1.1') and L.EXHIBIT_HEAD.match('Schedule 3.2(a)') and L.EXHIBIT_HEAD.match('EXHIBIT A FORM OF PROMISSORY NOTE')
                and not L.EXHIBIT_HEAD.match('Exhibit A lists the Assets.') and not L.EXHIBIT_HEAD.match('Schedule 1, as updated from time to time, lists the Products.')))
    # ROB-007: a malformed addition or lint block in the overrides, and a hint that matches whitespace, are data errors
    import json as _json
    from _rules_data import load_overrides as _lo
    def bad_ov(ov):
        f_ = _tmp(_json.dumps(ov).encode('utf-8'), '.json')
        try:
            return _raises(L.InputError, lambda: _lo(f_))
        finally:
            os.unlink(f_)
    out.append(('house-overrides: a malformed addition, a string broad_only and a list suppress are rejected; a good file is read (ROB-007)',
                bad_ov({'overrides': [], 'additions': [{'statement': 5}]}) and bad_ov({'overrides': [], 'lint': {'broad_only': 'R-1'}}) and bad_ov({'overrides': [], 'lint': {'suppress': []}})
                and not bad_ov({'overrides': [], 'additions': [{'statement': 's', 'applies_with': ['R-1']}], 'lint': {'suppress': {'R-1': 'x'}, 'broad_only': []}})))
    out.append(('a regex_hint that matches whitespace alone, or does not compile, is reported (ROB-007)', L.compile_hint(r'\s*')[1] and L.compile_hint('(')[1] and L.compile_hint(r'\bshall\b')[1] is None))
    # ROB-008: the reference generator refuses to run without a hand-written header, and writes atomically
    import build_references as _br
    from _cli import write_text as _wt
    import tempfile as _tf
    saved = (_br.HEADERS, _br.REFS, sys.argv)
    with _tf.TemporaryDirectory() as td:
        _br.HEADERS, _br.REFS, sys.argv = os.path.join(td, 'no-such-ref-headers'), td, ['build_references.py']  # never the skill's own references
        try:
            out.append(('build_references: a missing header is an InputError, not a silent bare title (ROB-008)', _raises(L.InputError, _br.main) and not os.listdir(td)))
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
        _sp.run(f'"{sys.executable}" "{os.path.abspath(L.__file__)}" "{fc}" --json "{fj}" | head -1', shell=True, capture_output=True, check=False)
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
    ent = lambda t: [f['source'] for f in L.house_checks({'idx': 0, 'text': t, 'fmt': {}}) if f['check'] == 'is-entitled-to']
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
    # probe, then Blake's answer Q2 (November 7, 2026): a conspicuous clause in capitals is a direct finding (severity 2) whose fix is the house form
    # (bold, 14-point, sentence case, an initial line); body text in capitals stays a severity-3 finding
    disc = [f for f in lint_text(intro + 'SELLER DISCLAIMS ALL IMPLIED WARRANTIES, INCLUDING THE IMPLIED WARRANTY OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.\n')[2] if f['check'] == 'capitals-body']
    jury = [f for f in lint_text(intro + 'EACH PARTY WAIVES ITS RIGHT TO A TRIAL BY JURY IN ANY PROCEEDING ARISING OUT OF THIS AGREEMENT.\n')[2] if f['check'] == 'capitals-body']
    body_caps = [f for f in lint_text(intro + 'BUYER SHALL PAY THE FEE NO LATER THAN 30 DAYS AFTER RECEIVING AN INVOICE FROM SELLER.\n')[2] if f['check'] == 'capitals-body']
    out.append(('a conspicuous clause in capitals (a disclaimer, a jury waiver) is a severity-2 direct finding with the house form (Q2); body text in capitals is severity 3',
                len(disc) == 1 and disc[0]['source'] == 'house' and disc[0]['severity'] == 2 and '14-point' in disc[0]['message'] and 'Initials:' in disc[0]['message']
                and len(jury) == 1 and jury[0]['severity'] == 2
                and len(body_caps) == 1 and body_caps[0]['source'] == 'house' and body_caps[0]['severity'] == 3 and '14-point' not in body_caps[0]['message']))
    # probe: "Business Day" shall mean is caught at the sentence level, and once with --inventory
    bd = lambda inv: [f for f in lint_text(intro + '"Business Day" shall mean a day other than a Saturday or Sunday.  Seller shall deliver on a Business Day.\n', inventory=inv)[2] if f['check'] == 'shall-in-definition']
    out.append(('"Business Day" shall mean is a sentence-level finding without --inventory, and 1 finding (not 2) with it', len(bd(False)) == 1 and len(bd(True)) == 1))
    # probe: a file of whitespace and punctuation gets the no-text note
    out.append(('a file that holds only whitespace and punctuation gets the "No text found" note', any('No text found' in n for n in L.report_notes({}, [{'idx': 0, 'text': ' \u201c\u201d \u2018\u2019 , . '}]))
                and not any('No text found' in n for n in L.report_notes({}, [{'idx': 0, 'text': 'Acme shall pay.'}]))))
    return out


def _round11_cases():
    """Blake's answers to the 35 open questions (November 7, 2026): the document-level cases, each a (name, passed) pair. The sentence-level
    cases sit beside each check's own cases in self_test(), and the phrase-variant entries carry their own examples and look-alikes."""
    out = []
    intro = 'This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company ("Seller"), and BETA INC., a Texas corporation ("Buyer").\n\n'
    of = lambda text, check, whose=None: [f for f in lint_text(text, whose=whose)[2] if f['check'] == check]
    # Q22: a nonparty subject gets the restructure onto the party, never may; a party subject keeps the may form
    np_ = of('No employee of Customer shall share credentials.\n', 'negative-subject-shall')
    pt_ = of('Neither party shall assign this agreement.\n', 'negative-subject-shall')
    out.append(('Q22: No employee of Customer shall gives the 2-part MSCD 3.180 form (reasonable efforts plus liability), shall cause only for an instrumentality; Neither party shall keeps Neither party may',
                len(np_) == 1 and 'Customer shall use reasonable efforts to prevent any employee of Customer' in np_[0]['message'] and 'Customer is liable' in np_[0]['message']
                and 'instrumentality' in np_[0]['message']
                and np_[0]['severity'] == 1 and len(pt_) == 1 and 'Neither party may' in pt_[0]['message'] and 'shall cause' not in pt_[0]['message']))
    # Q4: a fraction with digits after it keeps the word; a number with digits after it keeps the digits
    fr = of('Each party shall pay one-half (50%) of the fees.\n', 'words-and-digits')
    nm = of('Buyer shall pay within thirty (30) days.\n', 'words-and-digits')
    out.append(('Q4: one-half (50%) keeps one-half and drops the digits; thirty (30) keeps the digits',
                len(fr) == 1 and 'keep one-half' in fr[0]['message'] and len(nm) == 1 and 'use digits only' in nm[0]['message']))
    # Q23: numbered definitions keep their form; numbered sections in the same contract are still a finding
    defs = ('A. Definitions.  In this agreement:\n\n(1) "Affiliate" means any Person that controls Seller.\n\n(2) "Business Day" means a day other than a Saturday.\n\n'
            'B. Sale.  Seller shall sell the Assets to Buyer.\n')
    secs = intro + '1. Sale.  Seller shall sell the Assets.\n\n2. Price.  Buyer shall pay the Price.\n'
    out.append(('Q23: (1) "Affiliate" means ... draws no enumeration finding; top-level sections 1. and 2. still do',
                not of(intro + defs, 'enumeration') and len(of(secs, 'enumeration')) == 1))
    # Q13: a schedule that holds a signature block is an exhibit; a schedule of information is not
    signed = (intro + 'Seller shall sell the Assets to Buyer.\n\nACME LLC\n\nBy: ____\n\nBETA INC.\n\nBy: ____\n\nSCHEDULE A\n\nOrder Form\n\n'
              'Buyer orders 10 Units at $500 each.\n\nBETA INC.\n\nBy: ____\n\nName:\n\nTitle:\n')
    info = signed.split('BETA INC.\n\nBy: ____\n\nName:')[0]
    sa, sb = of(signed, 'attachment-classification'), of(info, 'attachment-classification')
    out.append(('Q13: SCHEDULE A with its own By: line is an exhibit (severity 2); a schedule of information is not',
                len(sa) == 1 and sa[0]['severity'] == 2 and 'Exhibit 1' in sa[0]['message'] and sa[0]['match'] == 'SCHEDULE A' and not sb
                and not of(signed, 'schedule-provision')))
    # Q10: typed numbering is noted once at severity 3; the message follows whose draft it is
    typed = [{'idx': n, 'text': t, 'where': 'body', 'fmt': {'fonts': ['Aptos']}} for n, t in enumerate(
        ['A. Sale.  Seller shall sell the Assets.', 'B. Price.  Buyer shall pay the Price.', 'C. Closing.  The parties shall close on March 1, 2027.'])]
    tn = {}
    saved = L.WHOSE
    try:
        for w in ('blake', 'other-side', None):
            L.WHOSE = w
            tn[w] = [f for f in L.outline_checks(typed, L.document_shape(typed)) if f['check'] == 'typed-numbering']
    finally:
        L.WHOSE = saved
    out.append(('Q10: typed numbering is 1 severity-3 note; Blake\'s draft converts, the other side\'s keeps it, unknown says both',
                all(len(v) == 1 and v[0]['severity'] == 3 for v in tn.values()) and 'use Word\'s native' in tn['blake'][0]['message']
                and 'keep its typed numbering' in tn['other-side'][0]['message'] and 'only in a document Blake drafts' in tn[None][0]['message']))
    # Q2 (.docx formatting): a conspicuous clause not in bold 14 point is severity 2; bold 14 point with an initial line is clear;
    # bold 14 point without an initial line is severity 3; 14 point there is no font-size finding, and an ordinary clause is untouched
    jury = 'Each party waives its right to a trial by jury in any proceeding arising out of this agreement.'
    plain = lambda sz, bold: {'fonts': ['Aptos'], 'sizes': [sz], 'bold_text': jury if bold else ''}
    cp = lambda fmt, nxt='Seller shall deliver the Units.': L.conspicuous_checks([{'idx': 0, 'text': jury, 'where': 'body', 'fmt': fmt},
                                                                               {'idx': 1, 'text': nxt, 'where': 'body', 'fmt': {'fonts': ['Aptos'], 'sizes': [12.0]}}])
    bad, good, no_init = cp(plain(12.0, False)), cp(plain(14.0, True), 'Initials: ________ Seller ________ Buyer'), cp(plain(14.0, True))
    ordinary = L.conspicuous_checks([{'idx': 0, 'text': 'Seller shall deliver the Units to Buyer at the Closing in good condition.', 'where': 'body', 'fmt': plain(12.0, False)}])
    fs14 = [f for f in L.house_checks({'idx': 0, 'text': jury, 'fmt': plain(14.0, True)}) if f['check'] == 'font-size']
    fs14b = [f for f in L.house_checks({'idx': 0, 'text': 'Seller shall deliver the Units to Buyer at the Closing in good condition.', 'fmt': plain(14.0, True)}) if f['check'] == 'font-size']
    out.append(('Q2: a jury waiver in 12-point plain type is severity 2; bold 14-point with initials is clear; without initials severity 3; 14 point is no font-size finding there only',
                len(bad) == 1 and bad[0]['severity'] == 2 and 'not bold' in bad[0]['message'] and 'no initial line' in bad[0]['message']
                and not good and len(no_init) == 1 and no_init[0]['severity'] == 3 and not ordinary and not fs14 and len(fs14b) == 1))
    # Q6: a stray represents and warrants in a contract that otherwise says states: Blake's draft conforms it; the other side's keeps it
    stray = intro + 'Seller states that it owns the Assets.  Seller states that no Proceeding is pending.  Seller represents and warrants that the Assets are free of Liens.\n'
    b6, o6 = of(stray, 'represents-warrants', 'blake'), of(stray, 'represents-warrants', 'other-side')
    out.append(('Q6: on Blake\'s draft a stray represents and warrants is a severity-2 finding to use states; on the other side\'s it is kept',
                len(b6) == 1 and b6[0]['severity'] == 2 and 'use states' in b6[0]['message'] and len(o6) == 1 and o6[0]['message'].startswith('Keep')))
    # Q7: the deadline finding takes the rule record's severity (1)
    q7 = of('Tenant may exercise the Renewal Option by notifying Landlord no later than June 30, 2027.\n', 'time-of-day')
    out.append(('Q7: a deadline that decides a right with no time of day is severity 1 and gives the 5:00 p.m. form', len(q7) == 1 and q7[0]['severity'] == 1 and '5:00 p.m. Eastern time' in q7[0]['message']))
    # Q26: "Obligations" means all Obligations is severity 1; the lowercase form is clear
    q26 = of('"Obligations" means all Obligations of Borrower to Lender under the Loan Documents.\n', 'definition')
    out.append(('Q26: the term heading its own definition is severity 1; the lowercase form is clear',
                len(q26) == 1 and q26[0]['severity'] == 1 and not of('"Obligations" means all obligations of Borrower to Lender under the Loan Documents.\n', 'definition')))
    return out


def _round12_cases():
    """ROB-005: 1 case per windowed prefix search, with the trigger at the far edge of its window. Each pair holds the
    verdict with the trigger and the verdict without it, so a window someone shrinks later fails here. Every expected
    value below comes from the lint as it ran before the windows went in, so the cases record behavior, not a wish."""
    out = []
    long_name = 'Vandergriffenbakerhollingsworthmontagueprescottwinterbournehaskins'  # 65 characters, no space
    intro = ('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company ("Seller"), '
             'and BETA INC., a Texas corporation ("Buyer").\n\nThe parties agree as follows:\n\n')
    pad = lambda n, w='alpha': ((w + ' ') * (n // (len(w) + 1) + 2))[:n]  # filler with no comma, period, semicolon or colon
    fires = lambda text, check: any(f['check'] == check for f in L.house_checks({'idx': 0, 'text': text, 'fmt': {}}))
    checks_of = lambda text: sorted(f['check'] for f in L.house_checks({'idx': 0, 'text': text, 'fmt': {}}))
    doc_fires = lambda body, check: any(f['check'] == check for f in lint_text(intro + body, inventory=True)[2])

    def seg(t, word):
        pos = t.index(word)
        return t[L.clause_start(t, pos):pos].strip()
    out.append(('tail(): the n characters before pos, clipped at the start of the string',
                (L.tail('abcdefghij', 7, 3), L.tail('abc', 2, 10), L.tail('abc', 0, 5), L.tail('abcdef', 6, 2)) == ('efg', 'ab', '', 'ef')))
    out.append(('clause_start: an abbreviation at the far edge of the ABBREV and initial windows',
                (seg('Acme Holdings, L.L.C. shall deliver the Units.', 'shall'), seg('Beta Supply Co., Inc. shall deliver the Units.', 'shall'),
                 seg('The parties chose U.S. law and Seller shall deliver.', 'law'), seg('Seller delivered the Units. Buyer shall pay.', 'Buyer'))
                == ('C.', 'Beta Supply Co., Inc.', 'The parties chose U.S.', '')))
    out.append(('spacing: 1 space after L.L.C., after an initial, and after a real sentence end',
                (fires('Buyer shall pay Acme Holdings, L.L.C. on the Closing Date.', 'spacing'),
                 fires('The parties chose U.S. law for this agreement.', 'spacing'),
                 fires('Seller shall deliver. Buyer shall pay.', 'spacing')) == (False, False, True)))
    out.append(('a nonparty subject behind a 65-character possessive determiner, and behind no determiner',
                (doc_fires(long_name + "'s freight forwarder shall deliver the Units.\n", 'nonparty-obligation'),
                 doc_fires('Seller shall deliver and freight forwarder shall collect the Units.\n', 'nonparty-obligation')) == (True, False)))
    out.append(('a party-state finding with the conditional lead 90 characters back, and with no lead',
                (checks_of('To the extent that Buyer accepts each of the first 5 Units delivered under this agreement Final Completion shall occur no later than July 31, 2027.'),
                 checks_of('Final Completion shall occur no later than July 31, 2027.')) == (['shall-in-condition'], ['category-shall'])))
    out.append(('required to with a negative subject 45 and 75 characters back',
                (fires('Neither party ' + pad(45) + ' shall be required to deliver the Units.', 'passive-hides-actor'),
                 fires('Neither party ' + pad(75) + ' shall be required to deliver the Units.', 'passive-hides-actor')) == (False, True)))
    out.append(('a passive with a 38-character adverb after the modal, and with no modal',
                (fires('The Units shall be unconditionallyandirrevocably delivered.', 'passive-hides-actor'),
                 fires('The Units are delivered.', 'passive-hides-actor')) == (True, False)))
    out.append(('agrees to behind a 65-character relative clause, and with no relative clause',
                (fires('Seller shall deliver the notice under which the ' + long_name + ' agrees to pay.', 'agrees-to'),
                 fires('Seller agrees to pay the Price.', 'agrees-to')) == (False, True)))
    out.append(('must after whether, after an evaluating verb, and on its own',
                (doc_fires('Buyer shall decide whether the Units must be new.\n', 'category-must'),
                 doc_fires('Buyer evaluates if the Units must be new.\n', 'category-must'),
                 doc_fires('The Units must be new and Buyer must pay the Price.\n', 'category-must')) == (False, False, True)))
    out.append(('a spelled-out number after an address label, and on its own',
                (fires('Address: One Lattice Plaza, Houston, Texas.', 'number-word'),
                 fires('Seller shall deliver one Unit to Buyer.', 'number-word')) == (False, True)))
    out.append(('a policy verb after and, after a contingent lead 5 words back, and on its own',
                (fires('The term runs for 5 years and the agreement terminates on the Closing Date.', 'category-will'),
                 fires('Before the Seller delivers the first Units the agreement terminates.', 'category-will'),
                 fires('The agreement terminates if Seller does not deliver the Units.', 'category-will')) == (False, False, True)))
    out.append(('no ... shall with the conditional lead 79 characters back, and with no lead',
                (checks_of('If Buyer accepts each of the first 5 Units delivered under this agreement then no notice shall be effective until Buyer receives it.'),
                 checks_of('No notice shall be effective until Buyer receives it.'))
                == (['category-shall', 'shall-in-condition'], ['category-shall', 'negative-subject-shall'])))
    out.append(('which after a preposition, after a comma, after an embedded question, and bare',
                (fires('The period during which Seller shall deliver is 5 Business Days.', 'restrictive-which'),
                 fires('Seller shall deliver the Units, which Buyer shall inspect.', 'restrictive-which'),
                 fires('Buyer shall specify which Units it wants.', 'restrictive-which'),
                 fires('Seller shall deliver the Units which Buyer ordered.', 'restrictive-which')) == (False, False, False, True)))
    out.append(('has the right to inside a statement of fact 100 and 115 characters back',
                (fires('Seller states that ' + pad(100) + ' and Seller has the right to sell.', 'category-may'),
                 fires('Seller states that ' + pad(115) + ' and Seller has the right to sell.', 'category-may'),
                 fires('Seller has the right to sell the Units.', 'category-may')) == (False, True, True)))
    out.append(('a reduced passive after that, and its noun phrase 4 words back',
                (fires('Seller shall deliver the notice that is required under this agreement.', 'reduced-passive'),
                 fires('Buyer shall pay the reasonable travel expenses incurred by Seller.', 'reduced-passive')) == (False, True)))
    out.append(('a statute citation, and a real numbered cross-reference',
                (fires('Seller shall comply with 42 U.S.C. Section 1983.', 'numbered-cross-reference'),
                 fires('Seller shall deliver the Units under Section 4.2.', 'numbered-cross-reference')) == (False, True)))
    out.append(('above after a comparison word, and below as a pointer',
                (fires('Buyer shall pay if the index falls at or below 5 percent.', 'contract-reference'),
                 fires('Seller shall deliver the Units as set forth below.', 'contract-reference')) == (False, True)))
    out.append(('a lowercase defined term, and the same words inside a role phrase',
                (doc_fires('"Acceptance Window" means the 5 Business Days after delivery.\n\nSeller shall deliver within the acceptance window.\n', 'defined-term-lowercase'),
                 doc_fires('"Acceptance Window" means the 5 Business Days after delivery.\n\nSeller shall act in its capacity as the acceptance window agent.\n', 'defined-term-lowercase'))
                == (True, False)))
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
            return L.read_paragraphs(f_)
        finally:
            os.unlink(f_)
    # R4, R6: a run property Word's format rejects keeps the paragraph's text; the formatting is noted as unread
    def sz_abc(d):
        r = d.add_paragraph().add_run('Lessee shall pay the Rent.')
        r._r.get_or_add_rPr().append(_px(f'<w:sz {W} w:val="abc"/>'))
    paras, meta = read(build(sz_abc))
    out.append(('a <w:sz w:val="abc"/> run keeps its paragraph, with formatting_unread noted', paras[1]['text'] == 'Lessee shall pay the Rent.' and meta.get('formatting_unread') == 1
                and any('formatting' in n for n in L.report_notes(meta, paras))))
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
    notes = L.report_notes(meta, paras)
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
    out.append(('theme_fonts and doc_default_font survive any error', L.theme_fonts(_Broken()) == {} and L.doc_default_font(_Broken()) == (None, None)))
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
        return L.run(f_, inventory, whose)
    finally:
        os.unlink(f_)


def _read_tmp(data, suffix='.txt'):
    """read_paragraphs() on bytes written to a temporary file."""
    f_ = _tmp(data, suffix)
    try:
        return L.read_paragraphs(f_)
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
        ('No Authorized User shall share credentials.', 'negative-subject-shall', True),  # a nonparty subject: still a finding, with the restructure (Blake's answer Q22)
        ('Customer shall use reasonable efforts to prevent any Authorized User from sharing credentials.', 'negative-subject-shall', False),  # the Q22 fix
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
        ('Employee shall not solicit any employee of Company to be hired by a competitor.', 'passive-voice', True),  # recast every time (Blake's answer Q3)
        ('Employee shall not solicit any employee of Company to accept employment with a competitor.', 'passive-voice', False),  # Q3's active form
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
        ('This second amendment is effective on signing.', 'ordinal-word', False),  # a document's name keeps its word (Blake's answer Q29)
        ('The parties signed the third amended and restated agreement and the fourth supplement to it.', 'ordinal-word', False),  # Q29
        ('Tenant may exercise the third renewal term.', 'ordinal-word', True),  # a renewal term is a count of periods, not a document (Q29)
        ('Acme shall deliver a third of the Units.', 'ordinal-word', False),  # a fraction keeps its word (Blake's answer Q4)
        ('Acme may sell one or more Units.', 'number-word', True),
        ('No one may enter the Premises.', 'number-word', False),
        ('The parties shall cooperate with one another.', 'number-word', False),
        ('Acme shall pay a one-time fee.', 'number-word', False),
        ('Acme shall deliver one-half of the Shares.', 'number-word', False),  # a fraction keeps its word (Blake's answer Q4; house rule 2)
        ('Acme shall deliver two-thirds of the Shares.', 'number-word', False),  # Q4
        ('Interest accrues at one and one-half percent per month.', 'number-word', True),  # a mixed number is a number (Q4): 1.5%
        ('Acme shall pay on the first anniversary of the Closing Date.', 'ordinal-word', True),
        ('Acme has a right of first refusal.', 'ordinal-word', False),
        ('Acme is not required to repair the Equipment.', 'passive-voice', False),
        ('Acme shall pay if Park knows or should have known of the defect.', 'should', True),
        ('Acme shall reimburse any expenses incurred by Park.', 'reduced-passive', True),
        ('Acme shall pay the amounts that Park invoices.', 'reduced-passive', False),
        ('Buyer shall pay the Purchase Price in the manner stated in the section titled "Payment."', 'reduced-passive', True),  # Blake's answer Q32: every such reduced passive
        ('Buyer shall pay the Purchase Price as stated in the section titled "Payment."', 'reduced-passive', True),  # Q32
        ('Buyer shall pay the Purchase Price under the section titled "Payment."', 'reduced-passive', False),  # house rule 4's form after Q32
        ('Buyer shall complete the sale that the section titled "Consent" describes.', 'reduced-passive', False),  # Q32's active form
        ('The parties are signing this agreement as of the date stated in the introductory clause.', 'reduced-passive', True),  # Blake's answer Q24
        ('The parties are signing this agreement as of the date that the introductory clause states.', 'reduced-passive', False),  # Q24's form
        ('Buyer shall pay the Purchase Price as set forth in the section titled "Payment."', 'wordy-phrase', False),  # the reduced-passive finding gives the fix (Q32)
        ('Buyer shall pay the fee set forth in Schedule A.', 'wordy-phrase', True),
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
        ('Tenant may exercise the Renewal Option by notifying Landlord no later than June 30, 2027.', 'time-of-day', True),  # a deadline that decides a right (Blake's answer Q7)
        ('Tenant may exercise the Renewal Option by notifying Landlord no later than 5:00 p.m. Eastern time on June 30, 2027.', 'time-of-day', False),  # Q7's form
        ('Lender shall fund the Loan no later than March 1, 2027.', 'time-of-day', False),  # a deadline that decides no right (Q7)
        ('The Term runs from the Effective Date through the Expiration Date.', 'time-ambiguity', True),  # a defined date term (Blake's answer Q12)
        ('The Term starts on the Effective Date and ends on the Expiration Date.', 'time-ambiguity', False),  # Q12's form
        ('This agreement shall be governed by Tennessee law.', 'category-shall', True),
        ('It is understood and agreed that Acme is an independent contractor.', 'throat-clearing', True),
        ('Acme hereby grants Widgetco a license.', 'archaic', False),
        ('The parties hereto agree as follows.', 'archaic', True),
        ('RESOLVED, that the Board approves the Merger Agreement.', 'resolved', True),  # Blake's answer Q1
        ('Resolved further, that the officers may sign the Merger Agreement.', 'resolved', True),  # any case (Q1)
        ('The Board approves the Merger Agreement.', 'resolved', False),  # Q1's form
        ('The parties have resolved that dispute.', 'resolved', False),  # the verb mid-sentence, not a resolution
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
        ('Franchisee states that it will not contest the Marks.', 'represents-warrants', False),  # a statement of future fact keeps states (Blake's answer Q16)
        ('Franchisee represents and warrants that it will not contest the Marks.', 'represents-warrants', True),  # Q16 reaches states only
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
        got = any(f['check'] == check for f in L.house_checks({'idx': 0, 'text': text, 'fmt': {}}))
        checks.append((f'{check} {"flagged" if expect else "clear"}: {text[:90]}', got == expect))
    sev_cases.append(('The Option expires on September 1, 2027.', 'time-of-day', 2))  # the entry's own severity (own_severity) governs
    for text, check, want in sev_cases:
        fs = [f for f in L.house_checks({'idx': 0, 'text': text, 'fmt': {}}) if f['check'] == check]
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
        ('.txt', ('This agreement is dated January 1, 2027, and is between Acme Widgets, Inc. ("Acme") and Widgetco LLC ("Widgetco").\n\n'
                 '1.1 Acme shall sell the Units to Widgetco.\n\n1.2 Widgetco shall pay the Price.\n\n1.3 Payment.  Widgetco shall pay by wire.\n\n'
                 'Acme shall use reasonable efforts.  Widgetco shall use commercially reasonable efforts.\n'),
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
            pn = L.read_paragraphs(tmp)[0]
            fsn = L.run(tmp, False)[2]
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
            a = [(x['where'], x['text']) for x in L.read_paragraphs(tmp)[0]]
            b = [(x['where'], x['text']) for x in L._read_docx_stdlib(tmp)[0]]
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
        texts = [p['text'] for p in L.read_paragraphs(tmp)[0]]
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
    checks.append(('the data files loaded cleanly', not L.LOAD_ERRORS and not L.load_rules()[1]))
    bad_entry = L.variant_problem({'id': 'x', 'check': 'x', 'pattern': '(', 'message': 'm', 'severity': 2, 'rule_ids': []})
    checks.append(('a malformed phrase-variant entry is caught', bool(bad_entry) and L.variant_problem({'id': 'x', 'check': 'x', 'severity': 4, 'pattern': 'a', 'message': 'm', 'rule_ids': []}) is not None))
    base = {'id': 'x', 'check': 'x', 'pattern': 'a', 'message': 'm', 'severity': 2, 'rule_ids': []}
    checks.append(('an empty pattern, a bool severity, int rule ids, a negative ctx and string examples are malformed',
               all(L.variant_problem(dict(base, **kv)) is not None for kv in ({'pattern': ''}, {'pattern': 'a*'}, {'severity': True}, {'rule_ids': [1]}, {'ctx': -5}, {'examples': 'text'}))
               and L.variant_problem(base) is None))
    toa_ok = {k: '' for k in L.TOA_FIELDS} | {'id': 't', 'term_word': 'tender', 'legal_meaning': 'x', 'replace': 'offer'}
    checks.append(('a term of art without a term_word, with a bad regex, or with string examples is a data error',
               all(_raises(L.InputError, lambda d=d: list(L._toa_entries({'terms': [d]})) and L._toa_regexes(d)) for d in (dict(toa_ok, term_word=''), dict(toa_ok, legal_use='('), dict(toa_ok, examples='x')))
               and L._toa_regexes(toa_ok)['term_word'] is not None))
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
            labels = [p_.get('auto_label') for p_ in L.read_paragraphs(tnum)[0] if p_['text'].strip()]
        finally:
            os.unlink(tnum)
        checks.append(('a list restarts where a new num has a startOverride', labels == ['1.', '2.', '1.', '2.']))
        dt = _docx.Document()  # python-docx's template sets its fonts through the theme (minorHAnsi = Cambria, 11 point)
        dt.add_paragraph('Acme shall pay the Price.')
        tth = _tmp(b'', '.docx')
        dt.save(tth)
        try:
            tf = L.run(tth, False)[2]
        finally:
            os.unlink(tth)
        checks.append(('a theme font is resolved and checked (Cambria, 11 point)', any(f['check'] == 'font' and 'Cambria' in f['message'] for f in tf)))
    else:
        skipped += 1
    import subprocess as _sp
    def _rc(*args):
        return _sp.run([sys.executable, os.path.abspath(L.__file__), *args], capture_output=True, text=True, check=False).returncode
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
    one_para = L.house_checks({'idx': 3, 'text': 'Owner owns the hotel.  Manager will do so through the Operator.  The parties therefore agree as follows:', 'fmt': {}})
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
    checks.append((('a circular pair is reported once, on the 1st term (a party name is no anchor); a chain, a self-reference, and a pair anchored to a schedule, '
               'a product name, a company name, or an integrated definition are not'), cd == ['Approved Carrier']))
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
            _paras, _meta = L.read_paragraphs(tbn)
            res = L.run(tbn, False)
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
    checks.append((('lowercase nonparty subjects (freight forwarder, customs broker, transferee, person) are flagged at low confidence; the other party, Acme, '
               'and things (headings, balance, waiver) are not'),
               lc == ['customs broker', 'freight forwarder', 'person whom Acme engages', 'transferee'] and all(f['confidence'] == 'low' and f['severity'] == 2 for f in res[2] if f['check'] == 'nonparty-obligation')))
    toc = ''.join(f'Article {n} Heading {n}\n\n' for n in range(1, 18))
    res = lint_text((toc + 'This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Acme”), and BETA INC., a Texas corporation (“Beta”).\n\n'
                'Acme will pay Beta the Fee.  The Company owns the Shares.  “Subsidiary” means an entity that Acme controls.  Acme shall cause its Subsidiaries to comply.\n'), inventory=True)
    tc_checks = {f['check'] for f in res[2]}
    checks.append(('a table of contents before the introductory clause does not hide the parties', 'category-will' in tc_checks and 'party-article' not in tc_checks))
    checks.append(('a defined term in -y is known in its -ies plural', not any(f['check'] == 'possibly-undefined-term' and f['match'] == 'Subsidiaries' for f in res[2])))
    checks.append(('run() restores the module state', L.PARTY_TERMS == set() and L.NONPARTY_NAMED == set() and L.RECITAL_IDX == set()))
    art = [{'idx': 0, 'auto_label': 'Article I', 'text': 'DEFINITIONS', 'where': 'body', 'fmt': {}},
           {'idx': 1, 'auto_label': 'A.', 'text': 'Terms.  In this agreement, the following definitions apply:', 'where': 'body', 'fmt': {}},
           {'idx': 2, 'auto_label': 'Article II', 'text': 'PAYMENT', 'where': 'body', 'fmt': {}},
           {'idx': 3, 'auto_label': 'A.', 'text': 'Fee.  Acme shall pay the Fee.', 'where': 'body', 'fmt': {}},
           {'idx': 4, 'auto_label': 'B.', 'text': 'Timing.  Acme shall pay it on the Closing Date.', 'where': 'body', 'fmt': {}}]
    oc = [f for f in L.outline_checks(art, L.document_shape(art)) if 'Only child' in f['message']]
    # Blake's answer Q15 (November 7, 2026): an article may hold a single section, so a lone A. under Article I is no only child; a lone 1. under a section still is
    art2 = art[:4] + [{'idx': 4, 'auto_label': '1.', 'text': 'Acme shall pay the Fee in cash.', 'where': 'body', 'fmt': {}},
                      {'idx': 5, 'auto_label': 'B.', 'text': 'Timing.  Acme shall pay it on the Closing Date.', 'where': 'body', 'fmt': {}}]
    oc2 = [f for f in L.outline_checks(art2, L.document_shape(art2)) if 'Only child' in f['message']]
    checks.append(('Word labels "Article I" are outline items; a lone A. under one is no only child (Q15), a lone 1. under a section is', not oc and [f['para'] for f in oc2] == [4]))
    res = lint_text(('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Seller”), and BETA INC., a Texas corporation (“Buyer”).\n\n'
                '“Escrow Agent” means First Trust Company, a Tennessee trust company.\n\nThe Escrow Agent, N.A. shall release the Holdback Amount to Seller.  Acme Holdings, Inc. shall deliver the Units.\n'), inventory=False)
    checks.append(('an abbreviation period does not cut off the subject (Escrow Agent, N.A. shall)', any(f['check'] == 'nonparty-obligation' and 'Escrow Agent' in f['match'] for f in res[2])))
    checks.append(('a thing named in the introductory clause is not a party', L.party_terms([{'idx': 0, 'text': 'This lease is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company ("Landlord"), and BETA INC., a Texas corporation ("Tenant"), for Suite 200 in the building at 100 Main Street (the "Building").', 'fmt': {}}]) == {'Landlord', 'Tenant'}))
    res = lint_text(('This agreement is dated January 1, 2027, and is between ACME LLC, a Delaware limited liability company (“Seller”), and BETA INC., a Texas corporation (“Buyer”).\n\n'
                'Buyer shall pay the fees in Schedule A.\n\nSCHEDULE A\n\nFees\n\nThe fee for each Unit is $500.\n\nBuyer shall pay each fee no later than 30 days after the invoice date.\n\n'
                'EXHIBIT 1\n\nFORM OF ESCROW AGREEMENT\n\nThe Escrow Agent shall hold the Escrow Funds.\n'), inventory=False)
    sp = [f for f in res[2] if f['check'] == 'schedule-provision']
    checks.append(('a duty inside a schedule is flagged; an exhibit form is not', len(sp) == 1 and 'Buyer shall pay' in sp[0]['match']))
    st_p = [{'idx': 0, 'fmt': {}, 'text': 'This section contains the disclosure that Section 8-70-115(2) of the Colorado Revised Statutes requires: Juniper Peak is not entitled '
                                         'to unemployment insurance benefits unless unemployment compensation coverage is provided by Juniper Peak or some other entity.'}]
    st_f = L.statutory_text_filter(st_p, L.house_checks(st_p[0]))
    checks.append(('statutory text keeps its words (1 note, no style findings)', [f['check'] for f in st_f] == ['statutory-text']))
    checks.append(('possessive defined terms', {'Landlord’s Work', 'Tenant’s Share', 'Capital Contribution', 'Representatives'} <= terms
               and not any(f['check'] == 'defined-twice' for f in fpo)))
    ar = lambda t: [f for f in L.arithmetic_checks([{'idx': 0, 'text': t}])]
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
    checks.append(('arithmetic: 1 amount defined twice', len(L.arithmetic_checks([{'idx': 0, 'text': 'The Purchase Price is $4,200,000, payable at Closing.'},
                                                                           {'idx': 1, 'text': 'The Purchase Price is $4,100,000.'}])) == 1))
    checks.append(('arithmetic: an amount qualified by a period is a schedule, not a conflict (ACC-007)',
                   not ar('The Base Rent is $5,000 for the first Lease Year.  The Base Rent is $5,150 for the second Lease Year.')
                   and not ar('The Fee is $500 per month.  The Fee is $6,000.50 for the year.') and len(ar('The Fee is $500.  The Fee is $600.')) == 1))
    tb = lambda rows: L.table_total_checks([], None, [[[(c, 0) for c in r] for r in rows]])
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
    checks.append(('money with 30 digits and a scale word is exact', L._money(L.MONEY_RE.search('$' + '9' * 30)) == int('9' * 30) * 100 and L._money(L.MONEY_RE.search('$1.5 million')) == 150000000 and L._money(L.MONEY_RE.search('$1.005')) is None))
    checks.append(('roman numerals past 3999 and a gridSpan of billions are clamped', L._fmt_num(4000, 'upperRoman') == '4000' and L._fmt_num(14, 'upperRoman') == 'XIV'))
    checks.append(('table: a closing statement with a Balance row is not a sum', not tb([['Item', 'Amount'], ['Purchase Price', '$100,000'], ['Deposit', '$10,000'], ['Balance', '$90,000'], ['Total', '$100,000']])))
    checks.append(('table: a wrong total', len(tb([['Item', 'Amount'], ['Fee', '$1,000'], ['Credit', '$200'], ['Total', '$1,300']])) == 1))
    checks += _round8_cases(_tmp, ar, tb)
    checks += _round9_cases()
    checks += _round10_cases(_tmp)
    checks += _round11_cases()
    checks += _round12_cases()
    # terms of art (house rule 13): each example fires for its term; each look-alike doesn't
    for e in L.terms_of_art():
        for texts, want in ((e['examples'], True), (e['lookalikes'], False)):
            for tx in texts:
                ps = [{'idx': i, 'text': x} for i, x in enumerate(tx.split('\n\n'))]
                hits = [f for f in L.term_of_art_checks(ps, L.definitions(ps)) if f'uses {e["id"]}' in f['message']]
                checks.append((f'terms of art: {e["id"]} {"example" if want else "look-alike"}: {tx[:80]!r}', bool(hits) == want))
    # data-driven phrase variants: each example fires its check and needs the entry; each look-alike doesn't fire it
    checks += [(f'variants: pattern does not compile: {bad}', False) for bad in L.BAD_VARIANTS]
    all_variants = L.phrase_variants()
    for c in all_variants:
        own = False  # at least 1 example must need this entry: an entry the code's own checks fully shadow is dead data
        for ex in c.get('examples', []):
            caught = c['rx'].search(ex) and any(f['check'] == c['check'] for f in L.house_checks({'idx': 0, 'text': ex, 'where': 'body', 'style': '', 'fmt': {}}))
            checks.append((f"variants {c['id']}: caught by its own pattern and its check: {ex}", bool(caught)))
            if not caught:
                continue
            L._VARIANTS = [v for v in all_variants if v is not c]
            try:
                own = own or not any(f['check'] == c['check'] for f in L.house_checks({'idx': 0, 'text': ex, 'where': 'body', 'style': '', 'fmt': {}}))
            finally:
                L._VARIANTS = all_variants
        checks.append((f"variants {c['id']}: at least 1 example needs this entry (not fully shadowed: narrow it or delete it)", own))
        for ex in c.get('lookalikes', []):
            checks.append((f"variants {c['id']}: look-alike clear: {ex}", not any(f['check'] == c['check'] for f in L.house_checks({'idx': 0, 'text': ex, 'where': 'body', 'style': '', 'fmt': {}}))))
    checks.append(('a .pdf is refused', _raises(ValueError, lambda: L.read_paragraphs('contract.pdf'))))
    fails = [name for name, ok in checks if not ok]
    for name in fails:
        print('FAIL:', name)
    total = len(checks)
    print(f'self-test: {total - len(fails)}/{total} passed' + (f'; {skipped} groups of .docx tests SKIPPED because python-docx is not installed' if skipped else ''))
    return 1 if fails else 0
