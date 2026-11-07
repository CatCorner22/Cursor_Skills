# CHANGELOG-h10-prose: fix pass on the prose and knowledge base (November 7, 2026)

Scope: the h10 copy only, per `r4/review-final/BRIEF-fix-prose-kb.md`. Sources: `r4/review-final/prose-report.md` (A-E) and `r4/review-final/kb-report.md` (sections 2-7). Files touched: `SKILL.md`; `references/house-style.md`, `fix-check.md`, `look-alikes.md`, `fix-patterns.md`, `rule-database.md`, `riders.md`; new `references/docx-mechanics.md`; `scripts/ref_headers/ambiguity-catalog.md`, `attachments.md`, `defined-terms.md`, `vagueness.md`, `verbs.md`; `data/house-overrides.json`, `data/terms-of-art.json`, `data/rules.jsonl`; `deploy/RELEASE.md`; and the 12 generated references, rebuilt by `scripts/build_references.py`. No script, `data/phrase-variants.json`, or `evals/` file changed.

## Summary

- Applied: 62 items (prose report: 32 of 32; KB report: 30 of 31).
- Skipped: 1 (KB section 2, the words-to-avoid.md Usage column, per the brief: `build_references.py` generates it, and the scripts agent owns that).
- Gates: `build_references.py` rebuilt 12 files; `mscd_lint.py --self-test` 2278/2278; `coverage.py --self-test` 13/13; description 991 characters; `should` grep clean of new breaches; all 3 JSON files load; every `_other` pattern in `terms-of-art.json` compiles.

## Prose report, applied

- A1 | SKILL.md Hard cases (nonparty row) | *Company shall cause the Board to approve* is correct (MSCD 3.160-3.161; question 20 for Blake); *acting through* offered as a style option.
- A1 | fix-check.md test 1 | same rule for the checker: `keep` on a finding that calls it a nonparty error, `pass` on one that offers *acting through* as style.
- A2 | fix-patterns.md:3 | the 6 tests now point to `fix-check.md`, 'The 6 tests' (SKILL.md Stage 2b points to them).
- A3 | deploy/RELEASE.md step 1 | 2 self-tests only; "the reviewer suites" deleted.
- A3 | deploy/RELEASE.md step 3 | names `deploy/build_zip.sh` (copied from `r4/release/`), its gates, and its full exclusion list.
- A4 | deploy/RELEASE.md:3 | marks the saved Project instructions out of date since the November 7 edits to items 1, 3(l), and 3(m), and sends the reader to step 5.
- A5 | data/house-overrides.json (singular-they) | "Use singular they for an individual of unspecified gender (house-style.md section 10); the rest of 17.11-17.18 applies."
- A6 (CHANGED per the brief) | SKILL.md Stage 2b | schema unchanged; added the 2 sentences on the `fix` field (wording first, then explanation and question; the checker rules on all of it).
- B1 | SKILL.md | the fix-patterns paragraph moved from Stage 2b to just before "Record each finding in this form"; reference-table row reads "before you write the Fix field of any finding".
- B1 | fix-patterns.md:3 | "Read this file in Stage 2, before you write the Fix field of any finding."
- B2 | SKILL.md pass 0 | split into 4 sub-bullets (*Run it*, *What the report lists*, *Judge each candidate*, *Read the text from lint.json*), text kept; added the serial comma in "headers, footers, and notes".
- B3 | references/docx-mechanics.md (new) | holds the tracked-change markup, the validate and accept commands with the fallback, and the comment command, markers, and line breaks.
- B3 | SKILL.md Redline steps 3, 6, 7 and the Comment paragraph | 1-line pointers to `docx-mechanics.md`; a row for the file in the reference table; `rule-database.md` step 4 lists it among the hand-written files.
- B4 | SKILL.md Stage 2b | the subagent also gets this skill's folder path, so it can open `look-alikes.md`, `terms-of-art.json`, and the lint. Also, for consistency, fix-check.md:3 now says the same ("plus this skill's folder path"); the report named only SKILL.md.
- B5 | house-style.md Contents | "0. Severity of a house-rule finding" is the 1st entry; the afterthought line deleted.
- B6 | look-alikes.md header | a 1-line list of the 43 sections by lint check, then "Recurring cases from blind tests".
- B7 | SKILL.md severity policy | the duplicate bullet deleted; its tip kept as a sentence: `rules_query.py --id` gives a rule record's severity and also accepts a paragraph number.
- C1 | rule-database.md:3, :9, :10; ref_headers/ambiguity-catalog.md:16; riders.md:18; fix-patterns.md:26 | 1st, 2nd for first, second.
- C2 | ref_headers/ambiguity-catalog.md:8 | "never let a comma alone decide meaning".
- C3 | SKILL.md pass 0 (2 sentences), Hard cases (reduced passives), Limits (unverified case); ref_headers/vagueness.md:3 and :12; ref_headers/attachments.md:8; ref_headers/verbs.md:20; riders.md:14 and :15; look-alikes.md (shall in the matrix clause; after-acquired Shares) | each passive recast as the report gives it.
- C4 | fix-patterns.md | 2 spaces collapsed to 1 on 29 prose lines (34, 40, 46, 52, 66, 72, 78, 84, 115, 135, 141, 147, 153, 165, 171, 177, 183, 189, 195, 201, 204, 207, 227, 233, 239, 245, 250, 251, 263); 2 spaces kept inside the 3 quoted wordings at lines 64, 76, and 230.
- C5 | fix-check.md:9 (twice), 15, 41, 47, 54, 57, 71 (twice), 80 | "the lawyer" is now "Blake" in each form the report lists.
- C6 | data/house-overrides.json:2 | serial comma: "MSCD5, riders, and the blog."
- C7 (CHANGED per the brief) | ref_headers/ambiguity-catalog.md:8; ref_headers/defined-terms.md:5 | the 2 undated blog-post titles deleted; the MSCD paragraphs kept.
- C8 | SKILL.md Hard cases | "section 6.1 ... section 6.2 ...".
- C9 | SKILL.md Stage 2b | "each lint direct finding whose text you checked and found correct".
- C10 | SKILL.md pass 0 and Stage 2b | `python3 <skill folder>/scripts/mscd_lint.py ...` and `python3 <skill folder>/scripts/coverage.py ...`.
- D1 | look-alikes.md:3 | "Built from `data/phrase-variants.json` (267 checks, each with examples the lint must catch and look-alikes it must not); the lint runs that file." (267 verified by loading the file; the now-redundant clause about the problem forms trimmed to "the lint runs that file").
- D2 | look-alikes.md doublet section | the *void* entry leads with "*void* alone, not the doublet *null and void* (MSCD 1.36)" and keeps the voice and tense notes.
- D3 | ref_headers/ambiguity-catalog.md:15 | "13.359-13.407".
- E1 | SKILL.md Stage 2b | the 3 sentences on `rejected.json` and rejected triggers added after the schema sentence; the line-116 parenthetical now covers `"check": "pass-N"` for a finding the lint never fired on (checked: `coverage.py` matches rejected entries only against lint findings, so an unmatched entry never surfaces).
- E2 | ref_headers/attachments.md step 6; SKILL.md pass 1 | where a moved provision goes, how to track it, and the 5.94 exception; pass 1 points to step 6.
- E3 | SKILL.md Stage 2 opening; fix-check.md test 6 | the combined-wording rule (higher severity wins; the earlier pass if equal; the other finding's Fix reads *wording: see finding N*).
- E4 | SKILL.md Hard cases | new row for a *joinder* (MSCD 13.480-13.484; rule R-13.480-joinder, severity 3, confirmed in rules.jsonl).
- E5 | SKILL.md severity policy; house-style.md Severity paragraph | the severity-lowering test replaced; house-style.md points to the SKILL.md policy.
- E6 | SKILL.md Stage 2b | after the independent check, lint each changed fix's new wording before the other 5 tests, then rerun `coverage.py`.

## KB report, applied

- 3 | look-alikes.md:429 (usage) | *such as* replaced by *including*; the note cites 13.816 and 13.806.
- 3 | look-alikes.md:113 (category-will) | the *willful misconduct* sentence replaced by the *goodwill* sentence.
- 3 | look-alikes.md:439 (Recurring cases) | *Acme and Widgetco shall designate ..., respectively.*; *each* dropped.
- 3 | look-alikes.md:174 (doublet) | *the date of this agreement* (2.23); *is dated*, not *made and entered into* (2.21).
- 3 | look-alikes.md:109 | MSCD 13.167.
- 3 | look-alikes.md:29 and :374 | MSCD 13.827.
- 3 | look-alikes.md:180 | MSCD 8.21.
- 3 | look-alikes.md:414 | MSCD 10.63.
- 3 | look-alikes.md:405 and :408 | MSCD 10.25.
- 3 | look-alikes.md:84 | MSCD 3.386 alone.
- 3 | look-alikes.md:157 | "(judgment call; MSCD 6.122 covers only undefined and unused terms)".
- 4 | fix-check.md:46 | "no *until* for an end day (MSCD 10.23; 10.25)".
- 4 | data/rules.jsonl R-3.547-reliance-on-information | `notes` now reads "Verified against the PDF page image (page 266) on November 7, 2026; the OCR text drops this table." (the field was empty, so the sentence starts it with no leading space); no other field changed; fix-patterns.md:165 kept.
- 5 | data/house-overrides.json (negative-subject-shall addition) | the non-person-subject contingency and the pointer to house-style.md section 8 appended to `statement`.
- 5 | house-style.md rule 3 | "Supersedes ... 4.58-4.59, and 4.62 (MSCD's numbering scheme and its Word styles)".
- 5 | house-style.md rule 4 | "Supersedes 4.100-4.106 and 4.108-4.109 (references by number, the rule against headings in references, and automatic cross-references)".
- 5 | house-style.md rule 8 | the *No amendment ...* wording cited to Appendix B, section 9 (with 3.334 and 3.369).
- 6 | data/terms-of-art.json | widened exactly as the report gives them: assignment (`uses_other` 2 substitutions plus 3 added alternatives; `name_other`), release, default, tender (both fields), collateral (both), guarantee (both; *delivery* added to the prefix list so *delivery guarantee* matches), agent (both), title (`name_other`), condition (`name_other`); security widened, not narrowed, with safeguards, vulnerabilities, assessments, audits, and badges in both fields. All 43 of the report's probe strings now match; *tender offer* still excluded; every `_other` pattern compiles; self-test 2278/2278 with the widened patterns (no case failed).
- 7 | data/rules.jsonl R-13.320-fraud-intentional-misrepresentation | `fix`: *knew [or, after reasonable inquiry, would have known]*; also *1 or more Indemnified Parties* (twice, house rule 2); `notes` ends "House rule 12: no should."
- 7 | data/rules.jsonl, the 11 number-word `fix` fields the report names | R-10.69, R-10.80, R-10.111, R-12.22 (also *Sellers*, no article), R-13.22, R-13.178, R-13.615, R-13.628, R-13.826 (also *Recipient*), R-13.945 (also *Vendor*), R-14.15: digits.
- 7 | data/rules.jsonl, 29 more `fix` fields the brief's number grep found, where the word counts something (house rule 2's test) | R-4.89, R-11.3, R-11.9, R-11.18, R-11.28 (*1 or both*; *one or the other* kept as a pronoun), R-11.32, R-11.101, R-11.105, R-11.107, R-11.110, R-13.71, R-13.73, R-13.107, R-13.128, R-13.378, R-13.485, R-13.492, R-13.548, R-13.549, R-13.653, R-13.665, R-13.927, R-15.23: *one or more* to *1 or more* and the like. Left as words: fractions (R-13.671 *one-third*, *two-sevenths*; R-14.56 *one-tenth*), the idiom *on the one hand* (R-11.96), pronouns (*an inclusive one*, R-11.61; *must all go to one*, R-11.80), the book's sentence-start exception *Twenty-five ...* (R-14.16), and the book quotation "three words well spent" (R-12.79).
- 7 | data/rules.jsonl, article before a party name in `fix` | 18 records: the 15 the brief's regex finds (R-12.19, R-12.22, R-13.30, R-13.48, R-13.87, R-13.238, R-13.308, R-13.337, R-13.500, R-13.512, R-13.658, R-13.746, R-13.826, R-13.945, R-17.21) plus 3 sentence-initial ones (R-13.170 *Buyer states*, R-13.479 *Borrower acknowledges*, R-13.649 *Tenant may move*). R-13.746: *the Bank* also dropped its article, because MSCD 13.748's example lists XYZ, the Company, and the Bank as the same kind of term; Bank isn't in the brief's name list, so revert that 1 word if Blake disagrees. R-13.30 and R-17.21 keep their passives (book examples; only the article changed). `examples[].after`, `statement`, and quoted book text untouched.
- 2 (note only) | the report says *shall not be relieved* and *in connection with* are not MSCD5 entries; no edit.

## Skipped

- KB section 2, words-to-avoid.md Usage column | per the brief: `build_references.py` generates it; the scripts agent handles it.

## Notes for the caller

- E1 as written has a mild tension: "`rejected.json` holds lint direct findings only" sits beside "for a finding the lint never fired on, set `"check"` to `"pass-N"`" (a `keep` the reviewer agrees with, moved to `rejected.json`). Both sentences are the report's; `coverage.py` behaves as the 2nd describes.
- attachments.md step 6 now reads "Move it to the body. Move it into the body section that refers to the schedule: ..." because the report's insertion point is right after "Move it to the body."; left as written.
- house-style.md's Contents list now starts at 0; CommonMark honors the start number.
- The generated `standard-english.md`, `structure.md`, `time-and-numbers.md`, and `words-to-avoid.md` differ from the master only in the Fix cells and the singular-they HOUSE line that the rebuild pulls from the data files.
- deploy/RELEASE.md step 3 names `deploy/build_zip.sh`, which exists today only at `r4/release/build_zip.sh`; the step says to copy it.

## Gate results

1. `python3 scripts/build_references.py`: 12 files rebuilt (verbs 223 rules, active-voice 18, words-to-avoid 439, attachments 29, ambiguity-catalog 114, vagueness 169, defined-terms 117, efforts-material 108, time-and-numbers 106, standard-english 70, structure 260, practice 29).
2. `python3 scripts/mscd_lint.py --self-test`: 2278/2278 passed. `python3 scripts/coverage.py --self-test`: 13/13 passed.
3. Description: 991 characters (limit 1,000).
4. `should` grep: the only hits are quoted contract phrases (*If Acme should fail to pay*, *The Units should arrive*, *If Acme should exercise the Option*), the `**should (3.360)**` label and `never "you should."` in comment-templates.md, the trigger-word lists in the description and project-instructions.md, house rule (l), and the rule statements in the generated references (from `rules.jsonl`, not edited); no new breach. "the lawyer": 0 hits.
5. JSON: `house-overrides.json`, `terms-of-art.json`, and all 1,338 lines of `rules.jsonl` load.
