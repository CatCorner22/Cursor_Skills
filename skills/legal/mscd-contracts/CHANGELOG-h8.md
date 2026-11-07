# CHANGELOG-h8: round-8 hardening (skill-r4-h8)

Each line: item | what changed | test added (mscd_lint.py --self-test unless noted).

## Group A: behavior defects

- C1 | party_collective reads every quoted term in the (each ... collectively ...) parenthetical (COLLECTIVE_PAREN, COLLECTIVE_TERM), strips a comma inside the quotes, expands with _forms(); PARTY_PHRASES adds Each Party, Either Party, The/the Parties, Both Parties | round-8: collective party terms drive will/must/may-not (4 findings)
- C2 | installment list `more` regex accepts " and $Y" / " or $Y" with no comma | arithmetic: a list of installments with no serial comma (2 clear, 1 look-alike still flagged)
- C3 | outline: numbering_labeler returns (label, level); paragraphs carry auto_level; is_roman uses the next enumerator and Word's level: typed (i) after (h) followed by (ii) is a subclause; Word-numbered (i) deeper than (h) is roman, at the same level the letter | outline: typed (i)...(ii); Word's list level tells the 2 apart
- C4 | defined-unused masks longer defined terms (Closing Date) out of the use text before counting the shorter (Closing) | defined-unused: Closing is unused when only Closing Date is used
- C5 | variant agrees-not-to: no match after a/the/this/each/any/its/their (the noun covenant not to) | variant example "Beta covenants not to compete"; look-alike "The covenant not to compete"
- C6 | such-pointing skips the correlative such X as Y (up to 4 words, none a verb) | cases: "such additional amounts as Schedule A states" clear; "such consent before the Closing" and "such insurance must name Customer as" flagged
- C7 | IMPORTS: `[Cc]apitalized terms?\b` | IMPORTS reads "Each capitalized term"
- C8 | variant money-currency-word: `/` in the lookbehind | look-alike "no/100 Dollars ($5,000.00)" (words-and-digits still reports it)
- C9 | variant until-end-day: dropped the "the end/expiration/expiry of" alternative (a moment, not a day) | 3 look-alikes; "until December 31, 2028" still flagged
- C10 | _variant_entries(): a phrase-variants file that is not an object with a "checks" list is an InputError (exit 2) | a phrase-variants file that is a list, or has no checks list, is an InputError
- C11 | variant foreclosure: the noun, or a verb form after a time anchor (on/upon/after/at/before/once/until/following) | example "after Lender forecloses"; look-alike "Lender may foreclose on the Collateral"
- C12 | definitions dedupe on (kind, paragraph, position); a term really defined twice in 1 paragraph now counts | defined-twice: deduped; a real repeat in 1 paragraph still counts
- C13 | shall-in-definition: `[ \t]+` after the closing quote, never across paragraphs | shall-in-definition never spans 2 paragraphs
- C14 | _md_tables(): Markdown cells carry their offset; the finding points at the Total cell | Markdown table: the finding points at the Total cell
- C15 | obligation-in-definition: match == text[start:end] ("shall"); the context moved to the message | obligation-in-definition: match == text[start:end]
- C16 | arithmetic pattern 3: parenthetical total "3 payments of $25,000 ($70,000)"; "($25,000 each)" is not a total | arithmetic: a parenthetical total
- C17 | NOT_PARTICIPLE (red, indeed, need, deed, seed, speed, hundred, sacred, naked): never a passive, with or without by; also in NOT_PASSIVE for the rules channel | cases: "are red by design" clear; "are painted by Acme" flagged
- C18 | coverage.py requires both "paragraphs" and "findings" lists (exit 2 otherwise) | coverage.py --self-test: rejects {} and {"findings": []}
- C19 | within-after and within time-ambiguity accept "within a period of N days" | cases
- R1 | own_text reads m:t (Word equations) in line; meta['equations'] counts m:oMath; report note | docx: a Word equation reads as text, with a count
- R2 | EDGE_L/EDGE_R `(?<![\w-])...(?![\w-])` in _variants() and the lowercase count, so a term ending in ")" is counted | a term that ends in a parenthesis is counted
- R3 | _md_tables() reads a pipe table without outer pipes when the block's 2nd line is the ---|--- separator | Markdown table without outer pipes is read; a sentence with a pipe is not a table
- R4, R6 | _run_format() (the formatting block) wrapped in try/except Exception in add(): paragraph kept with fmt {}, meta['formatting_unread'] counted, report note; DOCX_XML_ERRORS (python-docx InvalidXmlError, guarded import of both modules) in _run's catch → exit 2 "damaged .docx" | docx: a <w:sz w:val="abc"/> run keeps its paragraph
- R5 | theme_fonts() and doc_default_font() catch Exception (best effort) | theme_fonts and doc_default_font survive any error
- R7 | own_text(p_el, stats) counts skipped hidden runs into meta['hidden_runs']; report note | docx: a hidden-text run is skipped and counted
- R8 | arithmetic pattern 2: Decimal/quantize InvalidOperation → continue | arithmetic: thousands of digits and an overflowing percentage are skipped
- R9 | _money() and _count() return None on ValueError/InvalidOperation; callers check n is None | same case
- R10 | rules.jsonl: bounded the repetitions in R-14.75-range-gaps-overlaps, R-14.65-no-percent-in-equation, R-14.41-formula-ambiguity, R-13.546-money-decimals; variants us-respectively and money-mixed-notation bounded; RULE_PARA_MAX = 10,000: rule_checks skips a longer paragraph and returns its indexes; meta['long_paras'] note | every rule trigger runs in under 2 s on 20,000 digits; a paragraph over 10,000 characters skips the rule triggers, with a note
- R11 | .md: fenced code blocks dropped before the split; meta['code_blocks'] note | a fenced code block is dropped, with a note
- R12 | _comments_with_replies(): commentsExtended.xml (w15:paraIdParent) threads replies; comments are (author, text, reply_to); the note lists replies under their parent; JSON comments carry reply_to | docx: a comment reply is read from commentsExtended.xml and listed under its parent
- R13 | meta['para_mark_deletions'] counts w:pPr/w:rPr/w:del; the tracked-changes note says those paragraphs weren't merged | docx: a tracked deletion of a paragraph mark is counted and noted
- S1 | self-test: every rule id cited by the code (regex over the source) and by every variant exists in _SEV | every rule id cited ... exists
- S2 | collapse keys bold-definition and the document-level font by (check, message) | collapse keeps distinct per-document messages
- S3 | NUM_RUN (number words via words_value) replaces NUMW; _count reads digits or number words | arithmetic: a count in number words (fifteen, twenty-four)
- S4 | PARTY_DEFAULT gains Lessor, Lessee, Reseller, Subscriber, User, Owner, Agency, Developer, Publisher, Author, Artist, Holder, Investor, Member; PARTY_CAPS built from it; the 3 caps variants use a {party_caps} placeholder the loader fills | variant examples THE LESSOR / THE LESSEE MAY NOT / RESELLER MUST
- S5 | document_shape(paras) → intro, lead_in, lead, tail, tail_text, computed once in _run; nonparty_named, front_checks (intro and the signature-block tail), inventory (lead_in) and RECITAL_IDX use it | front findings appear behind a 9-line table of contents
- S6 | definitions(paras) replaces _definitions_with_text: INTEG, SECOND_TERM, AUTON, AUTON_INNER/LEAD, and the sentence forms IS_A_TERM, THE_TERM_IS, IS_TERM_IF (kind 'sentence', listed as integrated); inventory, term_of_art_checks, nonparty_named, front_checks consume it; the circular check sees the sentence forms | a term defined with is an "X" reaches the term-of-art check; the "X" is forms reach the circular check
- S7 | QO, QC, QT quote constants used by DEF_PAREN, ROLE_PAREN, DEF_WITH_ARTICLE, COLLECTIVE_TERM and the definition forms | single-quoted definitions enter the inventory
- S8 | variant self-test asserts c['rx'].search(ex) and that at least 1 example needs the entry; deleted is-deemed and reduced-by-role-label (fully shadowed by the code; their examples became lint cases) and neg-inverted (shadowed by neg-inverted-split; a caps-only neg-inverted-caps replaces it); survive-nature and us-in-the-event got an example only they catch | the variant loop
- S9 | run(path, want_inventory, whose=None) sets (when given) and restores WHOSE; load_rules() cached as (compiled + phrase rules, bad, ctrl); rule_checks takes ctrl; LINT_CTRL and BAD_RULES deleted | --whose cases; load_rules() is cached
- S10 | coverage.py lists source=="rules" rows whose check is in OPTIONAL (attachment-check) as optional; docstring updated | coverage.py --self-test
- S11 | rules_query.py: --severity outside 1-3 and --limit < 1 are usage errors (exit 5); `is not None` tests | (manual: exit 5)
- S12 | deleted 'table-total' from statutory_text_filter's tuple, the redundant `ul is not False`, MISSING_DEP (exit 4) from _cli.py; INTERRUPTED = 130 documented | —
- S13 | add(check, msg, m, conf, rules, sev=None): severity_for() resolves HOUSE_SEV then the rule record; an explicit sev sets keep_sev; apply_severity and the SIGNATURE rebind deleted; outline and front_checks use severity_for; the other-agreement numbered cross-reference keeps 3 | sev_cases: other-agreement reference 3; severity_for cases
- S14 | record_problem validates the full record shape; rules_query.fmt and build_references.entry/cite/sort_key use .get with defaults | record_problem checks every field the readers use
- S15 (part, pulled forward) | collapse() defaults start/end to -1, so group C's 0-diff gate holds | —

Group A gates: self-test 2097/2097; check_all 316/319 (1/91), 363/364 (1/104), 223/229 (2/103); own corpus 496/554 traps 3; corpus5 320/587 traps 5; corpus6 414/665 traps 20 (c135's "Holdback" conflict lost: it was counted by a false defined-twice that C12 removed; c141's Punch List definition gained).
Snapshot i2 vs h22 (start/end None read as -1): 53 files differ: bold-definition match is the term, not the parenthetical (S6); obligation-in-definition match is "shall" (C15); the document-default font finding appears beside a paragraph's font finding in 10 files (S2).

## Group B: the red team's regex fixes (probe2; 24 of 25 applied)

- F1 | party will / must / may not: a comma phrase between the party and the modal (party_x), and a pronoun subject after a clause that names a party (pronoun_x); the pronoun will form excludes the policy verbs | cases: "Supplier, at its own expense, will maintain"; "If Supplier receives a subpoena ..., it will notify"; "it may not change"; look-alikes "it will be required", "it will terminate", "it may not be"
- F2 | PERSONISH += counsel, attorney(s), surety, sureties, bank(s), depositary, registrar, government, authority, authorities, agency, agencies; a possessive ([A-Z]'s) before the lowercase nonparty subject | round-8 docx-free case: Seller's counsel shall; the surety shall; Seller's invoice is a thing
- F3 | SHALL_CAUSE_UNCONTROLLED: cause/require/ensure/procure (that)?, guarantee that | cases: "shall procure that its employees"; "shall procure the materials" clear
- F4 | NEG_SUBJ_SHALL: any comma-set phrase inside the subject (not a 2nd clause starting with and/or/but/nor) | cases
- F5 | PASSIVE_RE / MODAL_BE: a parenthetical or either/both between be and the participle | cases
- F6 | DIGITS_THEN_WORDS loop: 30 (thirty-five) days → words-and-digits plus words-digits-conflict | cases
- F7-F12, F18-F20, F25 | variants shall-not-permit, cap-each-or-aggregate, leading-modifier-list, time-minimum-before, term-notice-on, each-year-unit, pv-variants, new shall-in-where, commits-binds-pledges, vague-promptly-synonyms, arising-pair, tc-ack-agree, discretion-sole, survive-continues, eff-endeavours, amount-restated-installments, thisagr-capital, thisagr-intro-paren: the red team's patterns, each with its probe line as an example and a clean look-alike | the variant loop
- F10 | TERM_NOTICE: determine (UK), "by giving to the other" | (variant term-notice-on example)
- F11 | by-deadline: a defined date of 2-3 capitalized words (by the Rent Commencement Date); NUMDATE: year-first 2027/01/05 | cases. SKIPPED the until-end-day part ("until expiry of the Term" without the): it conflicts with C9 (the end or expiration of the Term is a moment, not a day), so probe L16 stays a miss (39/40)
- F13 | archaic execute: the lookahead is case-insensitive and allows "of" (execution of the Work is performance); term-of-art += execution of ... | cases
- F14 | CONTINGENT_TAIL: a generic subject of up to 8 words, none a time word; the subject's head is the noun phrase before its 1st preposition (partitives excepted) | cases
- F15 | THING_HEADS += completion, delivery, possession, occupancy, commencement, performance, acceptance, settlement, repayment, prepayment, installation, construction, vesting, funding, disbursement, maturity, renewal, extension, suspension, cancellation | cases
- F16 | PARTY_STATE += shall be at liberty / free to; EXTRA category-may (is at liberty to, is free to, has/retains the right to), with the statement-of-fact exclusion; is-entitled-to allows a comma phrase | cases
- F17 | SERIAL_2: items of up to 3 words when the extra words are capitalized | cases
- F21 | hold ... harmless up to 6 words; REPRESENTS AND WARRANTS in capitals | cases
- F22 | ATT_HERETO and this-agreement-term: the document's own noun (lease, licence, deed, ...) | cases
- F23 | reasonable commercial endeavours; reflexive pronoun pairs (himself or herself) | cases
- F24 | restrictive-which: the is/are + article exclusion dropped | case
- extra | shall remain / be solely liable (PARTY_STATE); set out at Schedule B (ATT_ON); Part N of the Schedule (variant att-unlabeled); forms part of this lease (ATT_PART); headings for guidance/identification/navigation; true, correct, and complete; successors and assignees (usage); wherein/whereof/whereunder (archaic); 3rd-party (usage); means and refers to (variant def-means-and-includes) | cases, 1 example + 1 look-alike each; none raised a corpus trap

Group B gates: self-test 2203/2203; check_all 316/319 (1/91), 363/364 (1/104), 223/229 (2/103); own corpus 497 traps 3; corpus5 323/587 traps 5; corpus6 424/665 traps 20; probe2 39/40 caught, 0/20 false alarms (L16 skipped on purpose).
Snapshot i3 vs i2: 28 files differ, all from the fixes above (+category-may 13, +unit-of-time 5, +shall-not-permit 4, +this-agreement-term 3, +nonparty-obligation 3, +repetition 2, the archaic execute-for-signing finding on "execute the Services" gone in 2 files (F13: the term-of-art finding stays), c96's category-will on "accrues" gone (its old match was the nonsense subject "A to the Agreement"; the real 11-word subject exceeds F14's 8).

## Group C: pure refactors (0-diff gate: snapshot i5 vs i3, "0 of 122 files differ"; self-test count unchanged at 2203)

- S15 | finding() builder (check, msg, para, m, conf, rules, source, sev, match, start, end, cut) used by every finding site (house add, cleared, term-of-art, outline, rule triggers, inventory, efforts, arithmetic, tables, footnote, font, schedule-provision, statutory-text, front_checks); start/end always present (-1 when nowhere); collapse() pops keep_sev, so it never reaches the JSON | —
- S16 | constants: ALIGN_CENTER/ALIGN_JUSTIFY, MONTH and MONTHS (1 copy, used by BY_MEANS, CONTINGENT_TAIL, DMY, THIS_DAY, the policy check, anchor_ref), ENTITY (moved up), LEAD_IN (1 regex), LEAD_IN_WINDOW, CHANGES_SHOWN, BROAD_MIN_HITS, BROAD_SHARE, LVL_* outline levels, MATCH_CUT, DEF_LEAD_WORDS (AUTON_LEAD and DEF_LEAD; the union adds "As used herein" to AUTON_LEAD: no snapshot change), SENT_BREAK + sentence_at()/sentence_from() replacing 6 of the ad-hoc sentence splits (definitions ×2, the obligation sentence (now on def_text with offsets), headings clause, arithmetic, DIGIT_START); sentences() deleted; clause_start() at the nonparty-span site; SIGNATURE_SRC → compiled SIGNATURE. Left as they were: the entity suffix lists in subject_of, the ampersand check and nonparty_named (different alternations: a union would change matches), the participle lists (EXTRA, REDUCED_BY, IRREG: likewise), and the defined-term-lowercase "own sentence" split (the ABBREV-aware split drops a current finding on "11:59 p.m. ... (the "Initial Term")": noted inline as a later-round change) | —
- S17 | read_paragraphs → _read_docx, _read_text, _split_text (+ _run_format from R4); house_checks → HOUSE_SECTIONS: passive_checks, signature_checks, party_verb_checks (the `if True:` scaffold removed), number_checks, spacing_list_checks, policy_checks, usage_checks, reference_checks, attachment_checks, date_checks, format_checks, variant_checks, each (t, p, add, out), add() returns the dict; cleared(out, p, m, rules) module-level; inventory → collect_definitions, _inventory_text, _locate, term_rows, definition_findings, undefined_terms | —
- S18 | self-test: module-level lint_text(text, suffix, inventory, whose), _tmp, _read_tmp, _refused, _raises; every ad-hoc block is a (name, passed) tuple in 1 checks list; total = len(checks); the 2 --whose cases (other-side sev-3 "Keep", blake sev-2 "use states") are in _round8_cases | —
- S12 (tail) | unused json import dropped | —

Final gates (after C): self-test 2203/2203; check_all 316/319 (1/91), 363/364 (1/104), 223/229 (2/103); own corpus 497/554 traps 3; corpus5 323/587 traps 5; corpus6 424/665 traps 20; probe2 39/40, 0/20; coverage.py --self-test 13/13; snapshot i5 == i3.
Diff stats vs the master (lines changed, < and > counted): mscd_lint.py 2577 (3880 → 4463 lines), coverage.py 18, rules_query.py 28, _rules_data.py 28, _cli.py 7, build_references.py 50, phrase-variants.json 286, rules.jsonl 8.
