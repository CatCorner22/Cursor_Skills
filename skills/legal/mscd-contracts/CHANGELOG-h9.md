# CHANGELOG-h9: round-8 review notes, hardening pass (skill-r4-h9)

Each line: item | what changed | test added (mscd_lint.py --self-test, `_round9_cases`, unless noted). MSCD points checked against pdf/mscd_dec.txt.

## A. Lint false alarms and misses

- A1 header | HARNESS_HEAD + skip_harness_header(): the "Draft of ...; Blake's client: ..." note (also "*Lender's draft of ...*") in the first 3 non-blank paragraphs is blanked (paragraph number kept), meta harness_header, report note | 3 cases (plain, Markdown emphasis, a title "DRAFT OF ..." stays)
- A2 covenant | variant covenant-noun: `(?<!restrictive\s)`; usage variants skip a quoted heading reference (HEADING_REF, in_heading_reference: titled/entitled/captioned/headed "..."); message cites 3.186-3.188 (grouped obligations, a loan's covenants, are still covenant -> obligation, so the heading "Financial Covenants" stays flagged) | 2 cases + variant example/look-alikes
- A3 nonparty | party_terms stops after an introductory clause that defined 2 parties (PARTIES_ENOUGH), so a recital's "loan agreement between Borrower and Lender" no longer makes Borrower a party; signing_roles()/signs_individually(): a role term whose definition names a person who signs on an individual line ("Manager" means Dale Marchetti; ______ Dale Marchetti) joins PARTY_COLLECTIVE (subject checks only; house rule 11 unchanged); By:/Name: lines don't count; agent_noun reads the noun after a hyphen (sub-distributors); RELATIVE_WHO_HEAD: "a project sponsor, who shall" takes the antecedent as subject | 4 cases
- A4 category-will | CONTINGENT_LEAD: a month-and-day date right after the lead word (Upon July 1, 2028,) is a stated time | 1 case (date clear, "Upon Closing" flagged)
- A5 undefined terms | CONTRACT_NOUN: Percentages?, Completion (Substantial Completion, Membership Percentages); a phrase that only ever starts a sentence and whose rest is a defined term (Overdue Rent) is skipped; Markdown table rows keep only cells a .docx cell would keep (over 8 words or a sentence: drawing titles drop); a typed text table's heading row (3+ columns 3+ spaces apart, with 2+ such rows) is dropped | 3 cases
- A6 inventory | DEF_LEAD_WORDS reads "In this Schedule A,"; a SCHEDULE/ANNEX/APPENDIX's definitions count with the body's (house rule 6: schedules are part of the contract) unless its heading or next 2 paragraphs say "form of" (FORM_OF); EXHIBIT_HEAD accepts a 2-line heading ("EXHIBIT 1\nFORM OF ..."); exhibit_rows(): a term defined only in an exhibit gets an inventory row with defined ["exhibit"] | 2 cases
- A7 typed-numbering | only on .docx paragraphs (fmt has fonts) | 1 case (.md and .txt)
- A8 R-6.9, R-13.129 | rules.jsonl regex_hint: R-6.9 skips caps runs, entity suffixes, Roman numerals, a lone heading and a run-in caps heading; R-13.129 skips "the Closing" (13.129's own form) and Closing Date/Statement/...; dropped the bare "closing" trigger word | 2 cases
- A9 R-13.862 | regex_hint needs "or" before any "and" (earlier/earliest/later/latest/greater/lesser); its trigger words (which fired on every "the earliest of") emptied | 1 case
- A10 category-shall | EXCEPT_THAT: "..., except that Buyer shall pay" / "except that the Manager shall not elect": the exception's own subject, not the main clause | 1 case
- A11 serial-comma | MODAL_ASIDE: a comma aside after the modal (may, without notice ... and without affecting ..., extend or renew) is no list | 1 case
- A12 immediately | variant immediately: `not` for immediately due/payable/effective/vested/exercisable (MSCD 10.127: the instantaneous sense works for events, not conduct) | 1 case + look-alike
- A13 R-3.222 | regex_hint skips only before if/when/during/from/between/after/before/on/in/at/until/for/upon/by/to the extent (13.651's own fix; 3.363) | 1 case (4 sentences)
- A14 both days | variant time-from-date-range: `not` for "both days/dates included" or inclusive. NOT applied to time-of-day (expires-no-time): that is Q7 (see below) | 1 case
- A15 R-4.6 | regex_hint: [^1] or a bare [1]-[99] not after $ and not before a word or %; $[5] and [10] days stay clear | 1 case
- A16 comments | comment_text(): the whole comment (paragraphs joined); the report shortens to COMMENT_SHOWN = 300 with ...; JSON keeps all | 1 case
- A17 front | signature-name check skips table cells and everything after the 1st attachment heading | 1 case
- A18 time-of-day | variant expires-no-time adds "runs/extends/continues from [date], to/through/until [date]" | 1 case + variant example
- (B) collapse wording | "(2 places in 1 paragraph: para 15)"; the report's trigger-line regex follows | 1 case; 1 existing case's expected string updated

## B. coverage.py
- Rule triggers were already skipped (not required) in the master; the summary line now says so and separates places from findings: "N of M required places ...; each place a direct finding fires counts once (K direct findings); the T rule triggers are optional pointers ... not counted." | coverage.py --self-test unchanged (13/13); output-only change

## C. rules_query.py
- --id partial match and --para cite-only match print "(No exact match ...)" on stdout before the results (stderr in --json mode); --para lists rules that state the paragraph before rules that only cite it | manual (no self-test harness in rules_query.py)
- Header prints only the house rule for the other side's drafts ("review of other side's draft: flag (house rule)") | manual

## D. SKILL.md, references
- SKILL.md hard cases: shall use ... only to now matches look-alikes (a use restriction is correct; 3.222-3.226 concern may; don't write it as the fix for may only use; may ... only before a time phrase or only if is MSCD's form, 13.651, 3.363)
- SKILL.md pass 0: read the lint's paragraphs (accepted view), not a python-docx dump; paragraph numbers count tables, text boxes, then headers, footers, notes; harness note skipped; coverage counts places
- SKILL.md test 1: explanation passives list (is defined, is bracketed, is stated, is needed, is required) and a 2nd lint run on explanations; no 2nd definition in a fix; Term/period fixes give a start and end time of day (10.33, 10.38) and the zone when the parties sit in 2 zones (10.51)
- SKILL.md test 5: terminate by giving N days' notice: offer giving/receipt AND both counts (13.627; 10.65-10.66)
- SKILL.md hard cases (must row): a nonparty's "no X shall": the may form plus a bracketed efforts or liability alternative, never a silent weakening; shall cause the Board -> Company, acting through the Board, shall (MSCD 2.80's acting-through form, applied to a board; 3.161)
- SKILL.md findings.json: "all": true allowed for a repeated finding; pass 6 covenant note
- look-alikes.md: a participle used as an adjective before its noun (accepted order) is not a reduced passive; may operate ... only from April 1 (13.651)
- fix-check.md: traps (shall use ... only to, may ... only + time, participle adjective); explanation passives and linting only the wording; rules for a 2nd definition, Term time of day and zone, nonparty no X shall, shall cause the Board, terminate by giving notice

## E. Coordinator's 9 missed problems
- E1 | leading-modifier-list accepts a modifier pair (defective or nonconforming) and a mass noun last (equipment); new leading-jurisdiction-list (United States patent, copyright, or trade secret; R-12.3) | variant examples + look-alikes
- E2 | new trailing-modifier-of-who (employees and consultants of the Company who; R-12.7, low) and trailing-purpose-pair (the Software and the Documentation for backup purposes; R-12.7, low) | variant examples + look-alikes
- E3 | new any-in-failure (If X does not pay any ...; fails to pay any; R-11.110, verified: 11.110 is the failure/inability ambiguity of any) | variant examples + look-alikes
- E4 | new termination-does-not-relieve (category-will; 13.823's own form "will not relieve", verified) | variant example + look-alike
- E5 | restated_amount_checks(): "the X Fee of $N" that a schedule line naming the same fee restates (R-1.56, sev 3, check restated-amount) | 1 case. Security Badge: terms-of-art security gains Badge/Card/Pass/Fob/Guard/Camera names and badge/access card words, but the entry is only_with_legal_use, and c167 never uses security in its legal sense, so it is still not flagged (changing only_with_legal_use is Blake's call)

## Left for Blake (kept current behavior)
- Q7: time-of-day on "ends on [date]" (also with "both days included"); the corpus6 c125 key has both an optional issue and a trap on that sentence
- R2(2): "are authorized to close" without "by law" (adjective or passive)
- Security as a term of art when the contract never uses it in its legal sense (only_with_legal_use)

## Merge note
- The master's SKILL.md and references/fix-patterns.md changed at 06:54 (after this copy was made at 06:27). This copy now carries those changes too (the fix-patterns.md row and paragraph, "MSCD 12.26; 12.37; 12.74", and the file itself), so the copy is the master plus this pass.

## Coordinator additions (07:45 ET)
- party_terms/document_shape: an introductory clause that lists each party in its own paragraph ("is among the following parties:" then "Alpha ... ("Alpha");") names every party; PARTIES_ENOUGH no longer stops after 2 parties while the list continues (a 3- or 4-party agreement would have had its later parties flagged as nonparties). Self-test added.
- CONTINGENT_REL (category-will): a policy whose contingency sits in a restrictive relative clause or a qualifier on the subject ("Any Transfer that this agreement does not permit is void"; "An assignment made without Lender's consent is of no effect") takes will (MSCD 3.334; table 8 [8-1]). 5 self-test cases. The share2 doublet entries and the phrase-variants look-alike that called "Any purported assignment that breaches this section is void." correct now use "This agreement is void." (voice correct; tense was the point).
- numbered-cross-reference: statute citations with hyphenated section numbers (Section 47-2-314 of the Tennessee Code Annotated) and chained citations (Section 47-2-314 and Section 47-2-315 of the ... Code) are no longer flagged (c174 trap).
