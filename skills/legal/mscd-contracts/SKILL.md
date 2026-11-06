---
name: mscd-contracts
disable-model-invocation: true
description: "Review, redline (real Word tracked changes), comment on, revise, proofread and draft business contracts to Kenneth A. Adams's A Manual of Style for Contract Drafting (MSCD, 5th edition) as updated by his blog, applying Blake Reagan's house style (active voice only, digits for every number, I./A./1./(a)/(i) enumeration, two spaces between sentences, Schedule A and Exhibit 1, cross-references by heading, no article before party names). Use it whenever Blake asks to review, mark up, redline, edit, tighten, fix, comment on or draft any contract, agreement, amendment, NDA, clause, definition or term sheet; whenever he asks about shall, will, may, must, should, active voice, ambiguity, vagueness, defined terms or schedules versus exhibits in contract language; and whenever he pastes contract language and asks what's wrong with it, even without naming MSCD. Not for deal or legal-risk advice on its own, or for writing that isn't contract language."
---
# MSCD contracts

This skill makes contract language say one thing, clearly, the way Ken Adams's *A Manual of Style for Contract Drafting* (MSCD5, 2023) prescribes, as updated by his blog through October 2026 and adjusted by Blake's house style. It works in four modes: **Review** (a findings report), **Redline** (tracked changes in the .docx), **Comment** (Word comments), and **Draft** (a new contract). Every mode runs the same analysis and cites the MSCD paragraph or blog post behind every change.

Two principles drive everything:

- **Ambiguity is never acceptable; vagueness stays only on purpose.** Ambiguity is text that can express 2 or more inconsistent meanings (MSCD 7.5). It causes disputes, so the skill removes every instance it finds. MSCD concedes that some ambiguity of the part versus the whole can't realistically be eliminated (7.5); where you can't remove one, flag it. Vagueness (a standard that depends on circumstances, such as *reasonable*) is sometimes the right tool, so the skill flags it and keeps it only for a stated reason.
- **Annotate first; never change meaning silently.** Adams doubts that technology can turn a traditional contract into an MSCD-compliant draft unaided, and suggests "explanatory annotations," leaving fixes to the user ("Could You Use Artificial Intelligence to Check Whether a Contract Complies with MSCD?"). So every change comes with its reason. A redline changes only wording whose meaning is certain; anything that needs a choice of meaning or a business term becomes a comment for Blake's decision.

Blake wants to understand the mechanics of every fix, so every internal finding explains the grammar or reasoning behind it, not just the replacement wording.

## Precedence: which source wins

When sources conflict, follow the first one that addresses the point, and say in the finding which one you followed.

1. **Blake's instruction for the matter.**
2. **Blake's house style** (`references/house-style.md`). Blake's rule: his way always prevails over MSCD.
3. **Law that requires specific wording**, when Blake identifies it (for example, a statute requiring capitals). Flag it; don't research or decide law. Wording a statute or rule requires isn't a drafting choice, so keep it even where a house rule would change it, and say so in the finding.
4. **Adopted riders** (`references/riders.md`): blog posts in which Adams changes MSCD5.
5. **MSCD5** (`data/rules.jsonl` and the reference files).
6. **Blog elaborations** that extend MSCD5 without changing it.
7. **Proposals** Adams only floats (language of inaction, language of state of mind, *human* for *individual*, *afterwards*, descriptive headings instead of *Miscellaneous*): note them, don't apply them.
8. **Standard English** per *The Chicago Manual of Style*, where everything above is silent.

## What's in the skill

| File | Read it when |
|---|---|
| `references/house-style.md` | Always, first. Blake's rules and how to apply them in hard cases |
| `references/verbs.md` | Pass 3, and any question about shall, will, may, must, hereby, states, conditions |
| `references/ambiguity-catalog.md` | Pass 4: every cause of ambiguity, with its signal, test and fix |
| `references/vagueness.md` | Pass 5 |
| `references/words-to-avoid.md` | Pass 6; the usage table (one verdict per MSCD Chapter 13 entry) |
| `references/attachments.md` | Every contract: the schedule-versus-exhibit procedure |
| `references/defined-terms.md` | Pass 2 |
| `references/time-and-numbers.md`, `standard-english.md`, `structure.md`, `active-voice.md`, `efforts-material.md` | The passes that need them; `structure.md` for drafting |
| `references/riders.md` | Whenever a rule might have changed since 2023 |
| `references/comment-templates.md` | Before writing any comment or report |
| `references/practice.md`, `references/rule-database.md` | Review practice; the database fields and the refresh step |
| `scripts/mscd_lint.py` | Pass 0, on every document. `--inventory` adds the defined-term inventory |
| `scripts/rules_query.py` | To pull a rule's full record (test, fix, exceptions, verified book examples) by id, word or paragraph |

The reference files list every rule as one line with its id; pull the full record with `rules_query.py --id` when you need the test, exceptions or the book's own example. Reading the rule record is how you avoid citing a rule wrongly. The reference files are large (`words-to-avoid.md` and `verbs.md` are over 100 KB): read each file's header, then search it (grep, or `rules_query.py --word`) for the words in front of you rather than reading it whole. Book examples in them are in MSCD style; restate them in house style before use.

## Stage 1: Intake

Ask only what you can't infer; if Blake isn't there to answer, use the default and state it at the top of the output.

| Question | Default |
|---|---|
| Whose draft is it: Blake's, or the other side's? | Either way, full MSCD conformance (Blake's rule: "We need to start educating people"), with 1 exception: on the other side's draft, keep their *represents and warrants* and suggest the remedies-neutral sentence in a comment (3.459-3.463); on Blake's draft, use *states*. On the other side's draft, separate changes that affect meaning from style changes, so the other side sees what matters first. If nobody knows whose draft it is, treat it as the other side's (it is the more cautious choice: it doesn't rewrite a verb the drafter may have chosen on purpose) and say so |
| Which mode, and what output? | Review → report in a Claude doc (or .docx if asked); Redline/Comment → the .docx; Draft → .docx. A pasted clause or a short question → answer in the reply, using the same finding fields, with no file |
| Governing law, and kind of deal | Ask; if unknown, U.S. law, general commercial, and say so. English or Commonwealth law changes the advice on *represents and warrants* and efforts (3.416-3.450; 8.50-8.63) |
| Who reads the comments? | Blake (internal form). Use the external form when Blake says the comments go to the other side |
| Tracked-change author | `Blake's AI Agent` |

Then read the whole document before changing anything: the meaning of one provision often depends on another.

## Stage 2: Analysis

Run these passes in order; later passes use what earlier ones learn.

0. **Lint.** Run `python3 scripts/mscd_lint.py <file> --inventory --json lint.json`, adding `--whose blake` or `--whose other-side` when you know whose draft it is. It reads .docx, .txt and .md: save pasted text to a .txt file first, and extract a PDF's text to .txt (a .docx with tracked changes is read as if they were accepted, and the report says so). It reports *candidates* in 2 groups: direct findings (house rules, MSCD's signature phrases such as *and/or*, *best efforts*, *within 30 days of*, the outline and the defined-term inventory), which are usually right and carry their fix, and rule triggers, which point you at sentences to check in passes 3 to 9 and are often not problems in a clean draft. Broad triggers (every *shall*, every *may*) appear once as counts. Confirm or reject each candidate in context; the script can't read meaning. On a traditional template expect hundreds of candidates, most of them real.
1. **Structure.** Front of the contract, body, back, attachments; enumeration in the house scheme; headings; cross-references (house rule: avoid them, refer by heading). `structure.md`, `attachments.md`.
2. **Defined terms.** From the inventory: terms defined twice, unused, undefined, used in two forms, stuffed with obligations, defined with *shall mean*; *this Agreement* defined as a term (2.123); party names take no article (house rule 11). `defined-terms.md`.
3. **Categories, sentence by sentence.** Assign every sentence in the body a category of contract language and check its verb (`verbs.md`): the *has a duty* test on every *shall*; *must* only for a duty on someone other than the subject; *may* only for discretion; never *shall* with a negative subject; active voice in every clause.
4. **Ambiguity.** Check every sentence against every cause in `ambiguity-catalog.md`, including the riders (right-node-raising pivot ambiguity; *each* or *in the aggregate*; the specific versus the general). For each ambiguity, write down each meaning before you propose a fix.
5. **Vagueness.** Flag each vague standard and classify it: keep on purpose, replace, or ask (`vagueness.md`).
6. **Words to avoid.** Every hit in `words-to-avoid.md`, judged in context.
7. **Time, numbers, money.** `time-and-numbers.md`; house rules: digits for every number, January 1, 2027.
8. **Consistency.** One word for one meaning across the whole document, attachments included (1.57-1.60).
9. **Standard English and typography.** `standard-english.md`; house rules: two spaces between sentences, one after a colon, 12-point Aptos, ragged right, clean visual lines. The front: title centered in capitals (2.2), party names in capitals in the introductory clause (2.51), the lead-in *The parties agree as follows:* (2.159), defined terms in bold where defined (2.92). A .txt file carries no font, alignment or bold, and a .md file carries only bold (`**...**`): say once in the report which typography wasn't checked, and don't guess. Leave *date* and *day* alone unless one causes confusion (10.16). MSCD lets you omit the concluding clause (5.5), so a contract without one has no problem to report.

Record each finding in this form (it feeds every mode):

| Field | Content |
|---|---|
| Location | The section's heading (and number if the document has one) and the quoted words |
| Kind and severity | 1 must fix (ambiguity, or a category or usage error that can change meaning); 2 should fix (vagueness, dispute risk); 3 style. A finding under a house rule takes the house severity: 1 for *shall* with a negative subject and for an undefined or 2-form defined term; 3 for typography (spacing, font, size, alignment, underlining, bold definitions) and reduced passives; 2 for every other house rule (house-style.md). Any other finding takes the severity in its rule record (`rules_query.py --id`, which also accepts a paragraph number, such as `--id 3.358`). The lint applies the same policy, so its severities match |
| Meanings | For an ambiguity, each possible meaning in plain words |
| Fix | The replacement wording, in house style |
| Why | The mechanism (grammar, category, or risk) in one or two sentences |
| Source | Rule id and MSCD paragraph, rider post, or house rule (noting where MSCD differs) |
| Decision needed | Yes, with options, when the fix needs a business term or a choice of meaning |

## Stage 3: Output by mode

### Review
Write the report in the form in `comment-templates.md`: a short summary, then findings sorted by severity and location, with wording cleanup, ambiguity fixes and substantive changes kept apart. Group a repeated issue into one row with all its locations.

### Redline
1. Work on a copy; never modify Blake's original.
2. Load the **docx** skill and follow its editing workflow (find its folder from the skill listing; on claude.ai it is usually `/mnt/skills/public/docx`) (unpack, `merge_runs.py`, edit `word/document.xml`, repack). Wrap every change in tracked-change markup (`<w:ins>`, `<w:del>` with `w:author="Blake's AI Agent"` and a date). Change only the words that need to change, so the reader sees exactly what moved; don't retype whole paragraphs.
3. Make only changes whose meaning is certain. Where a fix needs a choice of meaning or a business term, leave the text, insert a bracketed blank if needed, and add a comment with the options.
4. Carry each change through: a renamed defined term changes at every use; a moved provision updates every heading reference to it. Keep an old-to-new numbering map when converting to the I., A., 1., (a), (i) scheme, and deliver it with the redline.
5. Validate: `python <docx-skill>/scripts/office/validate.py out.docx --original in.docx --author "Blake's AI Agent"` must report no untracked changes. Render the result to images and look at it.
6. Deliver the redline, a clean copy (`<docx-skill>/scripts/accept_changes.py`), and the findings report. If the file arrived with the other side's tracked changes, the clean copy accepts theirs and yours alike; say so, and list their changes in the report with a recommendation on each. Don't edit inside the other side's insertion when a comment will do; if you must, say in the comment that rejecting their insertion also removes your change. Open the clean copy and check it: if the script leaves an empty paragraph or a file that fails validation, build the clean copy by applying the same edits without markup, and confirm its text matches the script's output.

### Comment
Anchor one comment to the exact words of each issue with the docx skill's `scripts/comment.py`, passing `--author "Blake's AI Agent"` (its default author is "Claude"). The script writes 1 paragraph per comment; for line breaks inside a comment, pass `--raw` with `<w:br/>` between lines. Use the internal form for Blake and the external form for the other side (`comment-templates.md`). Comments can accompany a redline: put the reason for each tracked change in its comment.

### Draft
1. Take in the term sheet, notes or old form. List every deal point you can't find as a question for Blake; never invent a deal term, number, date or party detail.
2. Outline to `structure.md`: title; introductory clause; recitals only if there's a back story; the lead-in *The parties therefore agree as follows:*; the body in the house enumeration with a bold heading for every section; definitions where chapter 6 places them; concluding clause; signature blocks; Schedules, then Exhibits.
3. Write each provision by choosing its category first, then its verb (`verbs.md`), in the active voice, with digits.
4. Run all 10 passes (0 to 9) on your own draft and fix every severity 1 finding.
5. **Get an independent review.** If you can start a subagent, give it the draft, `references/house-style.md` and this file's Stage 2, and ask it to check every sentence and return findings; it hasn't seen your drafting, so it won't share your blind spots. Without subagents, reread the whole draft cold, pass by pass. Fix what the review finds, then rerun the lint script.
6. Build the .docx with the docx skill (12-point Aptos, native multilevel numbering, ragged right), render it, look at it, and deliver it with the open questions.

## Hard cases

| Situation | What to do |
|---|---|
| Fixing an ambiguity requires choosing a meaning | State each meaning; ask which was intended; in a redline, comment with one wording per meaning |
| A house rule and an MSCD verb structure collide | Apply the house rule if a clean active form keeps the meaning; otherwise flag the sentence and ask Blake. Blake has settled 3 cases: *is not required to* stays (3.292); *is dated* stays (2.21); reduced passives are recast only when a clean active form exists (house-style.md section 1) |
| Recasting a passive would narrow or change who can act | Keep the meaning, flag it, ask |
| The .docx already has tracked changes or comments | Ask whether to accept them first or redline on top. If Blake isn't there, leave them untouched, add your changes on top under your own author name, and say so |
| A scanned or image-only PDF | Warn that text recognition may misread words; offer a report or a rebuilt .docx, not a redline |
| A PDF with a text layer, or pasted text, when Blake wants a redline | Rebuild it as a .docx first, say that the redline compares against the rebuilt copy, and keep the original's numbering in the map |
| A statute or court rule requires specific wording | Keep it; flag it; never remove required capitals or conspicuous text (16.24-16.31). Common cases: a UCC disclaimer naming MERCHANTABILITY in capitals; a negotiable note's *promises to pay to the order of* (UCC 3-104); *work made for hire* (17 U.S.C. § 101) |
| Blake keeps a traditional usage on purpose | Apply MSCD's fallback (for *represents and warrants*, the remedies-neutral sentence, 3.459-3.463) and record the departure |
| The contract has a headings-for-convenience clause | Always delete or limit it (15.18; house rule 4), with a comment explaining why: under the house rule, references identify provisions by heading |
| A consumer contract | Confirm with Blake; MSCD covers business contracts only |
| The docx skill isn't available | Say so; deliver the findings report and the full revised text with each change marked in the report, and offer to make the redline when the docx skill is available |
| Legal questions (enforceability, what a statute requires) | Flag them for Blake; this skill addresses how to say things, not what the law requires |
| The contract is too long to hold at once | Work article by article; keep the defined-term inventory and findings in files so later articles are checked against earlier ones |

## Refreshing the knowledge

The knowledge is current through Adams's blog post of October 22, 2026. When Blake asks to refresh, or a question turns on a recent change: read the newest posts in the blog's Categories of Contract Language and Ambiguity archives, classify each as rider, proposal or elaboration, add riders to `data/rules.jsonl` and `references/riders.md` (steps in `references/rule-database.md`), and run `scripts/build_references.py`. Never apply a proposal as a rule.

## Limits to state honestly

- The lint script finds candidates; it can't read meaning. On MSCD's Appendix A redraft, the script alone flags 77% of the changes Adams made (146 of 190 locatable footnotes); the rest come from the analysis passes.
- The rule database records 560 of its 594 book examples as verified against the book's text; quote only verified examples as the book's wording.
- The skill doesn't verify law or caselaw. A case reported to Blake but not verified is not cited.
