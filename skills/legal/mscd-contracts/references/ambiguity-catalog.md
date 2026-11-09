# Ambiguity catalog

**The skill removes every ambiguity it finds.** For each one, the finding states each possible meaning in plain words before proposing a fix. If the fix requires choosing a meaning, never choose silently: ask which meaning Blake intends, or, in a redline, comment with 1 wording for each meaning.

## Contents

- Definitions
- Causes added by the riders
- Elaboration: terms of art in their everyday sense
- How to use the list below
- Contents of the rules list, then Rules: every ambiguity rule, by MSCD chapter

## Definitions

- Text is **ambiguous** if it can express 2 or more inconsistent meanings (7.5). It is still ambiguous if context resolves it (7.6).
- A dispute alone doesn't make text ambiguous, and never let a comma alone decide meaning (7.28-7.29; 12.75-12.78).
- The 6 sources of uncertain meaning (7.3): ambiguity; not being sufficiently specific; mistake; conflict; not addressing an issue; vagueness (see `vagueness.md`).

## Causes added by the riders

- **Right-node-raising pivot ambiguity**: 2 coordinated clauses share a final element, and it's unclear which words the shared element attaches to (*subject to the jurisdiction of and be construed according to the laws of the State of Florida*). Offsetting commas "aren't optional"; better, repeat the shared element. MSCD's "delimiting commas in coordination" (12.79-12.87) are now "offsetting commas in right node raising."
- **Each or in the aggregate**: a quantity attributed to several items or payments (*monthly severance payments ... in the amount of $680,000*). Say *each* or *in the aggregate*.
- **Ambiguity of the specific versus the general**: *ejusdem generis* and *including* (*insects, birds, rodents, or other animals*). Apply the *including* rules (13.359-13.407).
- **11.106, 2nd printing**: for a single item, the *every/each/all* ambiguity also afflicts *the whole* and *the entire*.

## Elaboration: terms of art in their everyday sense

MSCD 1.57 says not to use 1 word for different meanings. A word that contracts use as a term of art invites the legal reading when it appears in its everyday sense, above all in a contract that also uses the legal sense. Flag these and offer the plain word:

| Everyday use | Legal sense it collides with | Write instead |
|---|---|---|
| *execute the services* | signing (MSCD prefers *sign*, 5.7) | *perform* |
| *if Acme notices an error* | a notice under the notices provision | *discovers*, *becomes aware of* |
| *if circumstances warrant* | warranty | *justify*, *require* |
| *fees represent 15% of* | a representation (a statement of fact) | *are*, *constitute* |
| *assign personnel*; *work assignment* | assignment of rights | *designate*; *task*, *work order* |
| *for Acme's consideration* | consideration for a promise | *review*, *evaluation* |
| *release payment* (outside an escrow) | release of claims | *pay*, *disburse* |
| *strategic partner* | a legal partnership | the actual relationship |

This is house rule 13 (it applies MSCD 1.57 and 1.8-1.13; MSCD doesn't list these words): severity 1 when the contract also uses the word in its legal sense, otherwise 2 (house-style.md section 13). Cite "house rule 13", not "elaboration". The lint flags these as `term-of-art`.

## How to use the list below

Records of kind `ambiguity-cause` give the signal to look for, the test, and the fix. `scripts/mscd_lint.py` flags candidates where a regex can; many causes (modifier scope, part versus whole) need you to read the sentence, so check every sentence against the causes in pass 4.

> **Book examples are in MSCD5's style, not house style.** They may use lowercase *schedule*, *1 January 2024*, spelled-out numbers, 1.1 numbering, *the* before party names, or a passive that MSCD accepts. Restate any example in house style (`house-style.md`) before you put it in a contract or a comment. For the other side's drafts, the house rule is to flag everything, whatever a rule's "let-pass" or "style-only" label says.


## Contents of the rules list

- Chapter 1: Contract Language Shouldn't Be Legalistic
- Chapter 1: Contract Language Shouldn't Be Confusing
- Chapter 7: Sources of Uncertain Meaning
- Chapter 10: References to Time
- Chapter 11: Part Versus the Whole
- Chapter 11: Blog: A New Variant of Ambiguity of the Part Versus the Whole
- Chapter 12: Syntactic Ambiguity
- Chapter 12: Blog: A New Kind of Syntactic Ambiguity
- Chapter 13: Selected Usages
- Chapter 13: Blog: Say Hi to "Ambiguity of the Specific Versus the General"
- Chapter 14: Numbers and Formulas

## Rules (114, generated from `data/rules.jsonl`)

Format: id, severity (1 = ambiguity or meaning-changing; 2 = vagueness or dispute risk; 3 = style), the rule, and its MSCD paragraphs and PDF page. `HOUSE` marks a rule that Blake's house style changes: apply the house rule. For a rule's full record (test, fix, exceptions, verified book examples), run `python3 scripts/rules_query.py --id <id>`.


### Chapter 1: Contract Language Shouldn't Be Legalistic

- **R-1.18-improvised-terms-of-art** [sev 2] Avoid improvised terms of art: ordinary wording onto which lawyers and judges have grafted doctrinal implications, such as hold harmless and best efforts. (1.18, 1.19; PDF p. 64)
- **R-1.20-give-effect-every-word** [sev 2] Expect courts to give effect to every word: that principle, applied zealously, gives significance to stray words and variations and to each element of a redundant string. (1.20, 1.41; PDF p. 65)
  - Look for: redundant words or minor variations in wording

### Chapter 1: Contract Language Shouldn't Be Confusing

- **R-1.33-avoid-confusion** [sev 1] Make avoiding confusion a high priority: uncertain meaning leads to disputes, cost, and mischief, and many judges are ill-equipped to make sense of confusing language. (1.33; PDF p. 67)
- **R-1.34-reader-miscues** [sev 3] Spare the reader miscues: structures that lead the reader to assume one reading, discover another, and have to reassess. (1.34; PDF p. 67)
  - Look for: a sentence whose structure invites a wrong first parse

### Chapter 7: Sources of Uncertain Meaning

- **R-7.1-six-sources** [sev 1] Distinguish six sources of uncertain meaning: ambiguity, not being sufficiently specific, mistake, conflict, not addressing an issue, and vagueness. Don't lump them all under "ambiguity," as courts and Black's Law Dictionary do. (7.1, 7.2, 7.3...; PDF p. 361)
- **R-7.5-ambiguity-def** [sev 1] Text is ambiguous if it can express two or more inconsistent meanings. Aim to eliminate ambiguity from contracts. (7.5, 7.10, 7.11; PDF p. 362)
  - Test: Can a reasonable reader give the text two or more meanings that are inconsistent with each other? If so, it is ambiguous.
  - Exceptions: For ambiguity of the part versus the whole, it is unrealistic to eliminate all possible alternative meanings (7.5; 11.152-.156).
- **R-7.6-ambiguous-even-if-resolved** [sev 1] Describe language as ambiguous even if the broader context resolves the ambiguity, rather than calling it unambiguous. (7.6; PDF p. 362)
  - Fix: Revise the text so it bears only the intended meaning without relying on context (7.5).
- **R-7.7-no-creative-ambiguity** [sev 1] Don't engage in "creative ambiguity" (deliberately ambiguous wording meant to invoke a hidden meaning later). (7.7, 7.8; PDF p. 362)
- **R-7.9-train-to-spot** [sev 1] Train yourself to spot ambiguity; it doesn't come naturally, and most ambiguity is subtle enough to go unnoticed. (7.9; PDF p. 363)
- **R-7.12-lexical-ambiguity** [sev 1] Lexical ambiguity: a word or phrase with more than one meaning, whether homonymy (unrelated meanings: bank of a river versus a financial institution) or polysemy (related senses: bank as an institution or its building). (7.12, 7.13, 7.14...; PDF p. 363)
  - Look for: a word with two or more established meanings used where either could apply
  - Test: List the established meanings of the word; ask whether more than one fits the provision. Homonymy rarely confuses in contracts; polysemy is the usual risk.
  - Fix: State the intended meaning instead of the ambiguous word, or make the word a defined term.
  - Exceptions: Routine instances (represents, material, year) have routine fixes; nonroutine words take imagination to spot (7.15).
- **R-7.16-antecedent-ambiguity** [sev 1] Antecedent ambiguity: a pronoun or other referring word or phrase (said, such, thereof, it, those, the fee) for which two or more antecedents present themselves. (7.16, 7.17, 7.18...; PDF p. 364)
  - Look for: a referring word whose antecedent could be either of two or more earlier nouns or noun phrases
  - Test: For each referring word, list every earlier noun phrase it could point to; if more than one fits grammatically and sensibly, it is ambiguous.
  - Fix: Make clear which antecedent you mean: repeat the noun, use a defined term, or restructure. Replace archaic referring words (said, thereof, such meaning those).
  - Book example: The defendant agrees to pay for one-half the cost of Sarah's college educational expenses ... subject to the limitation that said cost shall not exceed the tuition for a full-time residential student at UCONN-Storrs. → The defendant shall pay half the cost of Sarah's college educational expenses for a four-year degree net of any scholarships and grants, up to an amount equal to half the tuition for a full-time residential student at UCONN-Storrs.
- **R-7.23-contract-reference-ambiguity** [sev 1] Contract-reference ambiguity: here-words (herein, hereunder, hereof, hereto, hereinbelow) and pointing words (above, below, the foregoing, as aforesaid) leave unclear whether they refer to part of the contract or the whole, or which part; hereunder can also be read as "below" rather than "by operation of." (7.23, 7.24, 7.25...; PDF p. 366)
  - HOUSE: partly superseded: House rule 4: where a reference is needed, name the provision by its heading, not its number (the section titled "Payment"); better, restructure so no reference is needed.
  - Look for: a here-word or pointing word instead of a reference to a specific section
  - Test: Ask whether the word could mean the whole contract, the current section, or the text immediately before or after; if more than one reading is possible, it is ambiguous.
  - Fix: Refer to the whole contract as this agreement or to a specific section by number (section 4.2); use hereby only in language of performance.
- **R-7.26-specific-section-refs** [sev 1] When pointing to other parts of a contract, refer to specific sections, not above, below, the foregoing, or as aforesaid. (7.26, 7.27; PDF p. 367)
- **R-7.27-no-here-words** [sev 1] Don't use here-words, except hereby in language of performance. (7.27; PDF p. 367)
  - Fix: Use this agreement, or a specific section reference.
- **R-7.28-beyond-unambiguous** [sev 1] Don't be satisfied with unambiguous drafting; aim to avoid fights. For example, don't rely on a comma to establish meaning. (7.28; PDF p. 367)
  - Look for: meaning that depends on the presence or absence of a comma
  - Fix: Restructure so the meaning doesn't depend on punctuation.
- **R-7.28-ill-informed-dispute** [sev 2] Don't call a provision ambiguous merely because the parties attribute alternative meanings to it; an ill-informed dispute isn't enough (and courts too may see ambiguity where none exists). (7.28, 7.29; PDF p. 367)
- **R-7.30-insufficiently-specific** [sev 1] Not being sufficiently specific: a word or phrase too general for the issue it must decide (full-time basis, subcontractor, cohabitation, offshore, computer gaming business) can lead to fights over which more specific meaning was intended. Courts call it ambiguity; "insufficiently specific" is more accurate. (7.30, 7.31, 7.32...; PDF p. 368)
  - Look for: a general word or phrase that must decide a borderline question (who counts, what counts, how much)
  - Test: Ask what borderline cases the parties could argue about, and whether the text answers them.
  - Fix: Specify the criteria (for example, hours, duration, employee versus consultant).
  - Exceptions: Insufficient specificity can result from changing circumstances rather than a drafting glitch (7.34; Richey v. Metaxpert, 9th Cir. 2010).
- **R-7.35-mistake** [sev 2] Mistake: the parties are mistaken about the facts and the contract reflects that mistake (two ships named Peerless, Raffles v. Wichelhaus). Don't label this "latent ambiguity"; the text doesn't present alternative meanings. (7.35, 7.36; PDF p. 369)
  - Test: Check that each name, identifier, and factual reference picks out the thing both parties intend.
  - Fix: Identify things by unique particulars (date, number, location).
- **R-7.37-conflict** [sev 1] Conflict: two or more components of a contract aren't compatible, often through careless repetition (words and digits that don't match) or entire provisions that conflict (remedies provisions; an establishing-jurisdiction provision versus a consent-to-jurisdiction provision). (7.37, 7.38, 7.39; PDF p. 370)
  - Look for: the same matter addressed in two places, or amounts stated in both words and digits
  - Test: Find every provision addressing the same subject and confirm they can all apply together.
  - Fix: State each point once; reconcile or delete conflicting provisions.
- **R-7.40-not-addressing-issue** [sev 1] Not addressing an issue: by oversight, the drafter doesn't address an issue that should have been addressed (Sabatini v. Roybal: a "private garage" restriction said nothing about size). It is harder to avoid than other sources, because you must figure out what's missing. (7.40, 7.41, 7.42...; PDF p. 370)
  - Test: For each provision, ask what a party could do that complies with the words but defeats the purpose (size, number, timing, who decides).
  - Exceptions: The parties may intentionally leave an issue unaddressed when negotiating it isn't worth the time given the limited likelihood it arises; that might involve risk (7.45).
- **R-7.56-blurred-boundaries** [sev 2] The categories blend: lexical ambiguity and insufficient specificity differ by degree, as do insufficient specificity and failing to address an issue; a usage can be both vague and ambiguous (best efforts, material). (7.56, 7.57, 7.58...; PDF p. 373)

### Chapter 10: References to Time

- **R-10.23-inclusive-exclusive-ambiguity** [sev 1] Inclusive-versus-exclusive ambiguity: a preposition marking the beginning or end of a period (from, after, until, to, by, between) can leave unclear whether the stated day is included. (10.23, 10.24, 10.25...; PDF p. 473)
  - HOUSE: House addition: Every from [date] through [date] (or to or until) gets a finding, because from leaves the 1st day in doubt: write starting on November 1, 2027, and ending on April 30, 2028 (Blake's decision; MSCD 10.24). The finding needs an explicit date or a defined date term after from; from time to time and a place aren't findings. See house-style.md section 7.
  - Look for: a period bounded by a day using from, after, until, to, by, or between
  - Test: Ask whether the boundary day itself falls inside the period. Caselaw: from and after mostly exclusive; until, to, and by split; between mostly exclusive at both ends; starting and commences on likely inclusive; before likely exclusive; through likely inclusive.
  - Fix: State the time of day for each boundary (10.33), or use starting [day] and ending on or through [day], or say expressly inclusive or exclusive.
  - Exceptions: Even where caselaw is consistent, a court could hold otherwise on the circumstances, and the parties may not have had that effect in mind (10.27-.28).
- **R-10.37-midnight-ambiguity** [sev 1] Midnight ambiguity: midnight on [date] could mean the midnight beginning or the midnight ending that day; the convention that it means the end isn't clearly universal or known to the parties. (10.37, 10.38; PDF p. 476)
  - Look for: midnight on a date, or 12:01 a.m. / 11:59 p.m. used to dodge the issue
  - Test: Ask whether midnight on the date could be read as the start of that day.
  - Fix: Say midnight at the beginning [or end] of [date]. Don't use 12:01 a.m. or 11:59 p.m., which is clumsy.
- **R-10.65-minimum-notice-ambiguity** [sev 1] Minimum-notice ambiguity: when a provision requires at least (or no fewer than, or not less than) N days' notice before an event, courts split between counting 1 terminal day (the Nth day before the event is the last valid day, 10.66) and requiring "clear" days that exclude both (the N+1th day before). A plain backward deadline (no later than 10 days before the audit; during the 10 days before the Exclusivity Period expires) follows the convention in 10.65 (count 1 terminal day, not the other): it is not the court split, and making the count explicit there is at most a low-severity improvement. (10.65, 10.66, 10.67; PDF p. 481)
  - HOUSE: partly superseded: Blake's decision: every backward-counted period gets a finding, not only minimum-notice wording. Fix a plain deadline (no later than 30 days before the Closing Date) as no later than the 30th day before the Closing Date (the count stated) or a stated date; a minimum-notice period (at least 20 days' notice) still gets both counts and a question to Blake. See house-style.md section 7.
  - Look for: minimum notice: at least, no fewer than or not less than N days' notice (or N days before an event, where the provision sets how much notice a party must give)
  - Test: For a minimum-notice period, count back both ways (exclude 1 terminal day; exclude both) and see whether the last valid day differs (for a 31 December transfer with at least 10 days' notice: 21 December versus 20 December). For a plain deadline (no later than N days before), apply the 10.65 convention; flag it only if the parties' intent plainly differs.
  - Fix: Name the deadline day and offer both counts (the Nth day before; the N+1th day before) and ask which the parties intend; or denote the period in entire days.
- **R-10.69-within-ambiguity** [sev 1] Within ambiguity: within X days of an event can denote a period running forward, backward, or both (within seven days of the first anniversary), and within X days prior to can mean "during the X days before" or "at least X days before." (10.69, 10.70, 10.71; PDF p. 483)
  - Look for: within X days (or months) of, or within X days prior to, an event or date
  - Test: Ask whether the period could run before the reference point, after it, or both.
  - Fix: Say no later than 7 days after it receives a Sale Notice (or during the X days before, or at least X days before).
  - Book example: within seven days of receiving a Sale Notice → no later than seven days after it receives a Sale Notice
- **R-10.80-bi-semi-ambiguity** [sev 1] Bi- and semi- ambiguity: biannual and semiannual both mean twice a year, but some dictionaries give biannual the meaning of biennial; bimonthly and biweekly invite similar confusion. (10.80; PDF p. 485)
  - Look for: a frequency word with the prefix bi- or semi-
  - Test: Ask whether the word could mean twice per unit or once every two units.
  - Fix: Say twice a year (month, week) or every 2 years (months, weeks).
- **R-10.88-time-of-day-end-ambiguity** [sev 1] Time-of-day-at-end ambiguity: before 2:00 p.m. on the date that is 20 Business Days after the Closing can mean any time up to 2:00 p.m. on day 20, or only on day 20 before 2:00 p.m. (10.88, 10.89, 10.90; PDF p. 487)
  - Look for: before [time] on the [date] that is X days after [event]
  - Test: Ask whether delivery on day 19 (or earlier) counts, or only delivery on day 20 before the stated time.
  - Fix: For the first meaning: between the Closing and 2:00 p.m. 20 Business Days after the Closing. For the second: on the 20th Business Day after the Closing, before 2:00 p.m.
- **R-10.91-point-instead-of-period** [sev 1] Point-for-period ambiguity: tying a figure that pertains to a period to the point marking its end (the Revenues as of the 24-Month Revenue Measurement Point) invites a fight over which part of the period the figure covers. (10.91; PDF p. 487)
  - Look for: a cumulative figure (revenues, sales, income) measured "as of" a point that ends a multi-part period
  - Test: Ask whether the figure covers the whole period or only the last segment before the point.
  - Fix: Refer to the period itself (the Revenues for the 24 months ending ...).
- **R-10.94-will-have-ambiguity** [sev 1] Will-have ambiguity: saying a party will have a period to do something leaves unclear whether you mean an obligation or a condition. (10.94; PDF p. 488)
  - Look for: a party will have (or shall have) a period to do something
  - Test: Ask whether failing to act is a breach (obligation) or just loss of a right (condition).
  - Fix: For an obligation: No later than 60 days after termination, Acme shall return ... For a condition: To validly exercise the Option, Acme must no later than 60 days after termination notify Widgetco that it is doing so.
- **R-10.95-before-period-ambiguity** [sev 1] Before-scope ambiguity: a condition such as If any of the Assets are destroyed or damaged prior to Completion can cover only damage between signing and completion, or any time before completion, including before signing. (10.95, 10.96, 10.97; PDF p. 489)
  - Look for: a condition about something happening before (prior to) Closing or Completion, with no start date
  - Test: Ask whether the period could start before signing.
  - Fix: Address the condition of the assets at signing expressly.
- **R-10.99-year-month-ambiguity** [sev 1] Unit-of-time ambiguity in apportioning: year (per year, annual) can mean a year from the agreement date and each anniversary, or the 12 months from any 1 January (most courts); month can mean to the corresponding day of the next month, or a calendar month; week can mean any seven consecutive days or a traditional week. (10.99, 10.100, 10.101...; PDF p. 489)
  - Look for: a quantity, payment, or limit apportioned per year, month, or week
  - Test: Ask whether the unit runs from the contract date or from the calendar boundary.
  - Fix: State what year or month means, by a more specific alternative (each 12-month period starting on the date of this agreement or an anniversary; each calendar quarter) or a defined term if used several times.
- **R-10.111-consecutive-ambiguity** [sev 1] Block-of-time ambiguity: when the thing apportioned is itself a unit of time (two months of each year), it is unclear whether it must be taken as a single block. (10.111, 10.112, 10.113; PDF p. 492)
  - Look for: a number of days, weeks, or months to be taken within a year or month
  - Test: Ask whether the time may be split into several shorter blocks.
  - Fix: To require a block, use consecutive (2 consecutive months each year; convert 1 month to 30 consecutive days). If not, say so (over the course of 1 or more visits, each no shorter than 5 business days).
  - Book example: (none) → Over the course of one or more visits, each no shorter than five business days, excluding travel days, the Employee shall work in Acme's Budapest office for two months of each year.
- **R-10.152-time-component-ambiguity** [sev 1] Time-component ambiguity: a reference to things that pertain to a party (affiliates, subsidiaries, clients, shares, applicable law) can mean those existing at signing or those existing at some later time. (10.152, 10.153, 10.154...; PDF p. 501)
  - Look for: a class of persons or things belonging to a party (affiliates, subsidiaries, clients, shares) or applicable law, with no time reference
  - Test: Ask whether the class could grow or change after signing, and which members the provision should cover.
  - Fix: Say so in the provision or definition: "Subsidiary" means, for a Person [on the date of this agreement] [at a given time], ... ; say whether shares includes shares acquired later.

### Chapter 11: Part Versus the Whole

- **R-11.1-part-vs-whole-def** [sev 1] Ambiguity of "the part versus the whole": plural nouns and the words and, or, every, each, all, and any can leave unclear whether a provision refers to one member of a group or to the whole group. MSCD examples: numbered sentences are the text at issue; numbered-and-lettered italic sentences state its possible meanings. (11.1, 11.2; PDF p. 503)
- **R-11.3-singular-plural-ambiguity** [sev 1] Singular-for-plural ambiguity: a provision that refers to a thing or unnamed person in the singular (a non-affiliated third party; notice) may or may not apply to more than one. (11.3, 11.4, 11.5...; PDF p. 503)
  - Look for: singular noun naming a counterparty, event, or document that could occur more than once
  - Test: Ask whether the provision should apply regardless of number, only to one, or only to more than one; usually you want regardless of number.
  - Fix: Make the intended scope explicit (1 or more non-affiliated persons); sometimes a further sentence is needed.
- **R-11.7-one-or-more** [sev 3] Use one or more rather than X or Xs (one or more widgets, not the widget or widgets). (11.7; PDF p. 505)
  - Book example: the widget or widgets → one or more widgets
- **R-11.8-no-number-interpretation-rule** [sev 1] Don't rely on an internal rule of interpretation (the singular includes the plural) to make provisions apply regardless of number. (11.8; PDF p. 505)
- **R-11.9-any-not-plural** [sev 1] Don't count on any to extend a provision to more than one; any can mean any one member of the class, like a. Use one or more (if Acme files a complaint with one or more government bodies). (11.9, 11.10, 11.11...; PDF p. 505)
  - Fix: Replace any with 1 or more where more than 1 should be covered.
- **R-11.13-balanced-approach** [sev 3] Use one or more only where the context poses a greater risk of dispute; making every singular provision expressly cover the plural produces ponderous prose. (11.13, 11.14; PDF p. 505)
- **R-11.15-plural-subject-ambiguity** [sev 1] Plural-subject ambiguity: with a plural subject (The Stockholders shall notify Acme), it can be unclear whether members act individually or collectively; in language of discretion (may) there is a third meaning (one or more may act, or only if all do). Adding all of doesn't change the analysis. (11.15, 11.16, 11.17; PDF p. 506)
  - Look for: plural noun (or all of the [noun]s) as the subject of shall, may, must, or will
  - Test: Ask: must each member act, or the members together? With may: can one member act alone, or only if all act?
  - Fix: Say Each Stockholder shall ..., One or more Stockholders may ..., or The Stockholders, acting collectively, ...; or appoint an agent to act for the group.
  - Exceptions: Some plural sentences are unambiguous (The Acme Subsidiaries are Delaware corporations) (11.15).
  - Book example: The Stockholders shall notify Acme. → Each Stockholder shall notify Acme.
- **R-11.18-plural-object-ambiguity** [sev 1] Plural-direct-object ambiguity: with a plural direct object (Acme shall notify the Stockholders; Acme may sell the Shares), it can be unclear whether the subject acts as to each member or the group collectively, and in language of discretion whether it must act as to all or may act as to some. (11.18, 11.19; PDF p. 507)
  - Look for: plural noun as the object of a verb of obligation, discretion, or prohibition
  - Test: Ask whether the action must cover all members, may cover some, or treats them as a group.
  - Fix: Say each of the Stockholders, the Stockholders considered collectively, 1 or more Shares, or but only if it sells all of them.
  - Exceptions: When collective treatment makes no sense (Acme shall sell the Shares), the meanings narrow (11.18).
- **R-11.20-plural-subject-object-ambiguity** [sev 1] Plural-subject-and-object ambiguity: with a plural subject and a plural object (The Stockholders shall promptly submit the completed questionnaires), it can be unclear whether the object relates to each subject member separately or to all together. (11.20; PDF p. 508)
  - Look for: plural subject plus plural object
  - Test: Ask whether each member must submit one, each must submit all, or the group submits them together.
  - Fix: Say Each Stockholder shall promptly submit a completed questionnaire (or the questionnaires), or The Stockholders, acting collectively, ...
  - Exceptions: Context often makes the meaning clear (11.20).
  - Book example: The Stockholders shall promptly submit the completed questionnaires. → Each Stockholder shall promptly submit a completed questionnaire.
- **R-11.21-and-def** [sev 1] And concerns a set in its totality, and is often unambiguous (Acme and Widgetco are Delaware corporations), but it can mean "together" or "together and separately," and can leave unclear whether nouns act or are acted on individually or collectively, depending on grammatical context. (11.21, 11.22, 11.23; PDF p. 509)
- **R-11.24-and-subject-ambiguity** [sev 1] And-subject ambiguity: parties linked by and as the subject (Able and Baker shall notify Acme) can act individually or collectively; with may, it can also mean both must act, or either or both may act. (11.24, 11.25, 11.26...; PDF p. 509)
  - Look for: two or more parties joined by and as the subject of shall or may
  - Test: Ask whether each may (or must) act alone, or whether all must act together.
  - Fix: Say Able and Baker shall each notify Acme; Able or Baker, or both of them, may notify Acme; or ..., acting collectively, ...
  - Book example: TVP and SEI may extend its term by subsequent 10 year periods. → The term of this agreement, as extended in accordance with this section 10.1, will be extended by ten years if the parties so agree in writing.
- **R-11.28-and-object-ambiguity** [sev 1] And-direct-object ambiguity: nouns linked by and as direct objects (Acme shall notify Able and Baker) raise individual-versus-collective meanings; with may, whether both, one, or either is meant (Acme may dissolve Subsidiary A and Subsidiary B); with shall not, whether both are prohibited separately or only the combination. (11.28, 11.29, 11.30; PDF p. 511)
  - Look for: two or more nouns joined by and as the object of shall, may, or shall not
  - Test: For shall not: is each act prohibited, or only doing both? For may: must the party act as to both, or may it act as to one?
  - Fix: Say shall not notify Able and shall not notify Baker; may dissolve 1 or both of Subsidiary A and Subsidiary B; or both ..., as opposed to one or the other.
  - Exceptions: When the objects can't be considered collectively (Acme shall dissolve Subsidiary A and Subsidiary B), the ambiguity is reduced (11.28).
- **R-11.31-and-subject-object-ambiguity** [sev 1] Distributive-versus-joint ambiguity: with and in both subject and object (Able and Baker shall notify Acme and Widgetco), it is unclear whether each subject acts as to each object, each acts as to one object respectively, or they act collectively. (11.31; PDF p. 512)
  - Look for: and joining two subjects and and joining two objects in one sentence
  - Test: Ask whether the pairing is each-to-each, one-to-one (respectively), or joint.
  - Fix: Say Able and Baker shall each notify Acme and Widgetco; or ... notify Acme and Widgetco, respectively; or ..., acting collectively, ...
- **R-11.32-multiple-verb-phrases** [sev 1] Multiple-verb-phrase ambiguity: one may governing two verb phrases joined by and (Acme may sell assets and make capital expenditures) can mean the party may do both only together, or each separately. (11.32, 11.33; PDF p. 513)
  - Look for: may followed by two or more verb phrases joined by and
  - Test: Ask whether the party may do one without the other.
  - Fix: Repeat may (Acme may sell assets and may make capital expenditures), or say Acme may sell assets or make capital expenditures, or it may do both; with 3 or more, say may do any 1 or more of the following.
  - Exceptions: When the first act logically leads to the second (Parent may dissolve Sub and liquidate its assets), "together" is likely intended (11.33).
- **R-11.34-and-preposition-objects** [sev 1] Objects-of-preposition ambiguity: nouns joined by and as objects of a preposition alongside a direct object (Delta shall issue a promissory note to Echo and Foxtrot) can mean one to each, or one to them jointly; may and shall not multiply the meanings. (11.34, 11.35; PDF p. 513)
  - Look for: a direct object plus two or more objects of a preposition joined by and (issue a note to X and Y)
  - Test: Ask whether each named recipient gets one, or one is shared.
  - Fix: Say to each of Echo and Foxtrot, or to Echo and Foxtrot jointly.
  - Exceptions: When the objects can't be considered collectively (construct a factory in California and Florida), the scope narrows (11.35).
- **R-11.36-and-adjectives-ambiguity** [sev 1] Adjectives-linked-by-and ambiguity: two adjectives joined by and before a plural noun (temporary and part-time employees) can mean those who are temporary and those who are part-time, or only those who are both; with may there are five meanings. (11.36, 11.37, 11.38...; PDF p. 515)
  - Look for: two adjectives joined by and modifying one plural noun
  - Test: Ask whether something must have both attributes or either.
  - Fix: Repeat the noun with each adjective (temporary employees and part-time employees), or say who are both.
  - Exceptions: Mutually exclusive attributes (full-time and part-time) reduce the ambiguity (11.38).
  - Book example: Tango shall terminate the employment of Acme's temporary and part-time employees. → Tango shall terminate the employment of Acme's temporary employees and part-time employees.
- **R-11.40-every-x-and-y** [sev 1] Every-X-and-Y ambiguity: every or each before nouns linked by and (indemnify every director and officer) can mean every director and every officer, or every person who is both. (11.40; PDF p. 516)
  - Look for: every or each followed by two nouns joined by and
  - Test: Ask whether one person must hold both roles.
  - Fix: Say every director and every officer.
  - Book example: Acme shall indemnify every director and officer of Widgetco. → Acme shall indemnify every director and every officer of Widgetco.
- **R-11.41-and-any-contingency** [sev 1] Optional-element ambiguity: and linking a required element to one meant to be optional (on the basis of dues deduction authorization and other evidence) invites a fight over whether both are required. (11.41, 11.42, 11.43...; PDF p. 517)
  - Look for: and followed by other, additional, or further [noun] where that element is optional
  - Test: Ask whether the provision fails if the second element is absent.
  - Fix: Insert any after and (and any other evidence).
- **R-11.48-and-other-manifestations** [sev 1] Two-trigger ambiguity: and joining two triggering events in a time or condition provision (during the six-month period following (x) Termination and (y) a Restrictive Covenant Breach) leaves unclear whether the right runs after each event or only after both. The listed and ambiguities aren't exhaustive. (11.48, 11.49; PDF p. 518)
  - Look for: and joining two triggering events after following, after, upon, or on
  - Test: Ask whether the provision is triggered by either event or only by both.
  - Fix: State whether the right arises after either event or only after both of them.
- **R-11.50-or-def** [sev 1] Or presents alternatives and entails at least one. Its "not and" implicature (that not all alternatives are true) is implied, not part of its meaning, so or doesn't mean only one alternative is true; either strengthens the implicature but doesn't make it meaning. Under negation, an or-coordination usually equals an and-coordination of negative clauses, but wide-scope readings remain possible. (11.50, 11.51, 11.52...; PDF p. 519)
- **R-11.61-or-inclusive-exclusive** [sev 1] Inclusive-versus-exclusive or: or between alternatives that aren't mutually exclusive (Acme shall dissolve Subsidiary A or Subsidiary B) can mean one but not both, or one or both, in every category of contract language except prohibition. (11.61, 11.62, 11.63...; PDF p. 521)
  - Look for: or joining alternatives that could both occur or both be chosen
  - Test: Ask whether both alternatives could happen or be chosen, and whether that should be allowed.
  - Fix: Say ... or Subsidiary B, but not both; or ... or Subsidiary B, or both. Don't rely on the not-and implicature or on either for an exclusive meaning, or on context for an inclusive one.
  - Exceptions: Some ors can only be exclusive (Parent shall incorporate Sub in Delaware or New York) (11.61).
- **R-11.66-or-negation** [sev 1] Or-under-negation ambiguity: shall not X or Y (Acme shall not dissolve Subsidiary A or Subsidiary B) most likely prohibits each, but can be argued to prohibit only doing both, only doing one, or more; the same arises in negative statements of fact and conditional clauses. (11.66, 11.67, 11.68; PDF p. 523)
  - Look for: or inside a prohibition or negative statement
  - Test: Ask whether a court could read the prohibition as applying to only one of the alternatives.
  - Fix: Say Acme shall not dissolve Subsidiary A and shall not dissolve Subsidiary B, or Acme shall dissolve neither Subsidiary A nor Subsidiary B. Don't assume a court will apply De Morgan's laws.
- **R-11.69-or-conditional-item** [sev 1] Conditional-item-in-or-series ambiguity: when one item in an or-series is modified by a conditional clause (with Fred or, if she's in town, Nancy), it is unclear whether the conditional item is simply one more alternative or takes priority when the condition is met; setting the item apart with its own or makes the priority reading likelier. (11.69, 11.70, 11.71...; PDF p. 524)
  - Look for: or, if [condition], [item] within a series
  - Test: Ask whether the conditional item must be chosen whenever its condition is met.
  - Fix: State the intended meaning in full: X or Y; if Y is unavailable, X (alternatives), or Y if [condition]; if not, X (priority).
- **R-11.80-or-plural-nouns** [sev 1] Or-with-plural-noun ambiguity: subjects or objects of a preposition linked by or with a plural noun (Able or Baker shall submit invoices to Charlie; Acme shall sell apples or oranges) leave unclear whether one party handles all, each item is handled by one, items may be handled jointly, or the alternatives may alternate or run concurrently. (11.80, 11.81, 11.82; PDF p. 527)
  - Look for: subjects or objects joined by or together with a plural noun
  - Test: Ask who may handle which items, and whether alternatives may alternate or combine.
  - Fix: State the intended allocation expressly, using wording that tracks the intended meaning (for example, whether the items may be split, shared, or must all go to one).
- **R-11.83-cumulation-of-attributes** [sev 2] "Cumulation of attributes": an or-coordination of attributes that aren't mutually exclusive (one Acme temporary or part-time employee) raises whether it also covers something combining them (an employee who is both). (11.83, 11.84, 11.85...; PDF p. 528)
  - Look for: two non-exclusive adjectives joined by or
  - Test: Ask whether something with both attributes should be covered.
  - Fix: To preclude cumulation, say ... temporary or part-time but not both (not doing so would be reckless); to make cumulation explicit, say temporary or part-time or both, weighing certainty against wordiness.
  - Exceptions: It doesn't arise with mutually exclusive attributes (full-time or part-time employee) (11.85). | Economy of hypothesis suggests cumulation is covered, perhaps strongly enough that there is no real ambiguity (11.86).
- **R-11.88-or-adjectives-plural** [sev 1] Adjectives-linked-by-or ambiguity with plural nouns: Tango shall terminate the employment of Acme's temporary or part-time employees can mean those who are temporary or those who are part-time, or all of both groups; may adds more meanings. (11.88, 11.89; PDF p. 530)
  - Look for: two adjectives joined by or modifying one plural noun
  - Test: Ask whether the provision reaches only one group, either group, or all members of both groups.
  - Fix: Repeat the noun for each adjective (temporary employees or part-time employees).
  - Book example: Tango shall terminate the employment of Acme's temporary or part-time employees. → Tango shall terminate the employment of Acme's temporary employees or part-time employees.
- **R-11.90-no-and-or** [sev 2] Don't use and/or; say X or Y or both, one or both of X and Y, or one or both of the following: X; and Y. If and/or seems to offer significant economy, restructure. (11.90, 11.91, 11.92...; PDF p. 531)
  - Book example: Acme shall purchase Widget A and/or Widget B. → Acme shall purchase Widget A or Widget B and may purchase both.
- **R-11.96-and-or-scope** [sev 1] And-or scope ambiguity: in a string of three elements with and between two and or between the others (Acme shall hire Able and Baker or Charlie; If A and B, or C, then D), the meaning depends on which conjunction has scope over the other. (11.96, 11.97, 11.98...; PDF p. 532)
  - Look for: and and or in the same series of three or more elements
  - Test: Group the elements both ways ((A and B) or C; A and (B or C)) and ask whether both groupings make sense.
  - Fix: Enumerate (Acme shall hire (1) Able and Baker or (2) Charlie); use either to mark the or-coordination (Able and either Baker or Charlie); or use on the one hand ... on the other hand. For conditions: If A and B, or if C, then D; or If A and either B or C, then D.
- **R-11.101-and-for-or** [sev 1] And-for-or mistake: and used where or makes sense (or the converse), as in a guarantee that terminates upon (1) ..., (2) ..., and (3) ..., where requiring all three events makes no sense. (11.101, 11.102, 11.103...; PDF p. 534)
  - Look for: a list of alternative triggering events joined by and
  - Test: Ask whether the provision should operate when only one listed event occurs.
  - Fix: Use or when any 1 suffices; to prevent an argument that more than one occurring defeats the provision, put 1 or more of the following before the alternatives and and after the next-to-last.
- **R-11.105-every-each-all-discretion** [sev 1] Every/each/all-in-discretion ambiguity: in language of obligation these words are clear, but with may (Acme may purchase every vehicle included in the Lee Assets) they can mean no fewer than all, or one or more. (11.105, 11.106; PDF p. 535)
  - Look for: may followed by every, each, or all; for a single item, also the whole or the entire
  - Test: Ask whether the party may take only some.
  - Fix: Say may purchase 1 or more of the vehicles, or may purchase the vehicles, but only all of them.
  - Exceptions: For a single item, the ambiguity afflicts equivalents to all, including the whole and the entire (11.106, second printing).
- **R-11.107-any-ambiguity** [sev 1] Any ambiguity: in language of obligation, any can mean all (shall purchase any vehicle, as in "take the name of any person who comes through the door") or one ("pick any card"), and may imply there may be none; in language of discretion, it can mean only one or one or more. (11.107, 11.108, 11.109; PDF p. 536)
  - Look for: any after shall, must, or may, or any in a condition
  - Test: Ask whether any means each one, just one, or one or more.
  - Fix: Say each, 1, or 1 or more, as intended; refer to "a single term" or "1 or more terms."
- **R-11.110-failure-inability-ambiguity** [sev 1] Failure-or-inability ambiguity: every, each, all, and any in a sentence expressing failure or inability (inability to perform any duty; if all of the Conditions have not been discharged; prevents a Party from performing any of its obligations) can mean failure as to all, as to none, or as to one or more. (11.110, 11.111, 11.112...; PDF p. 537)
  - Look for: every, each, all, or any combined with failure, inability, prevention, or not
  - Test: Ask whether the provision is triggered by failure as to one item or only as to all.
  - Fix: Say inability to perform 1 or more duties, or inability to perform all duties; if 1 or more of the Conditions has not been satisfied.
  - Book example: "Disability" means the Employee's inability to perform any duty under this agreement. → "Disability" means the Employee's inability to perform one or more duties under this agreement.
- **R-11.119-dont-ignore-part-whole** [sev 1] Don't ignore part-versus-whole ambiguity; it confuses practitioners, clients, and judges. (11.119, 11.120; PDF p. 539)
- **R-11.121-meyer-case** [sev 1] Read "unable to perform any of the duties of his occupation or any occupation for which he is reasonably qualified" as a negated or-coordination: the natural meaning is unable to perform any duties of his own occupation and unable to perform any duties of any qualified occupation. The alternative reading (either inability suffices) makes half the provision redundant and so is unreasonable. (11.121, 11.122, 11.123...; PDF p. 540)
- **R-11.134-reasonable-meanings-test** [sev 1] Treat a provision as ambiguous only if each competing meaning is reasonable. (11.134, 11.135, 11.136; PDF p. 543)
  - Test: For each candidate meaning, ask whether a reasonable reader, using ordinary English usage, could adopt it.
- **R-11.147-weigh-meanings-independently** [sev 1] Weigh the reasonableness of alternative meanings independently; defects in one meaning don't bolster the reasonableness of the other. (11.147, 11.148; PDF p. 545)
- **R-11.149-stay-alert** [sev 1] Stay alert to part-versus-whole ambiguity, or you will likely miss alternative meanings until they cause a dispute; don't expect judges, increasingly reliant on dictionaries, to sort out a part-versus-whole mess sensibly. (11.149, 11.150, 11.151; PDF p. 546)
- **R-11.152-whether-to-eliminate** [sev 2] Decide how far to go in eliminating alternative meanings: they are virtually inescapable with and and or; leave language as is if the alternative meaning isn't reasonable, but consider redrafting if an unreasonable meaning could cause mischief if a court adopted it. (11.152, 11.153, 11.154...; PDF p. 547)
  - Exceptions: Revising "a medically determined sickness or accidental bodily injury" or "education, training or experience" to rule out combined readings would be outlandish (11.154).
- **R-11.156-applicable-laws-and-or** [sev 3] Balance expediency against risk: in The Seller has complied with all laws applicable to the Business and [or] the Acquired Assets, the natural meaning with and and with or is the same (each law applicable to either), and prose stylists would avoid extra verbiage; expediency might well prevail. (11.156, 11.157; PDF p. 547)
  - Book example: The Seller has complied with all laws applicable to the Business and the Acquired Assets. → The Seller has complied with all laws applicable to the Business and all laws applicable to the Acquired Assets.
- **R-11.158-broader-redrafting** [sev 2] Expect that eliminating part-versus-whole alternative meanings often becomes part of broader redrafting rather than a targeted adjustment. (11.158, 11.159, 11.160; PDF p. 548)
  - Book example: unable to perform any of the duties of his occupation or any occupation for which he is reasonably qualified by education, training or experience → (2) the member is able to perform none of the duties of the member's occupation and each other occupation for which the member is reasonably qualified by education, training, or experience

### Chapter 11: Blog: A New Variant of Ambiguity of the Part Versus the Whole

- **R-rider-each-or-aggregate** [sev 1] A new variant of part-versus-whole ambiguity: when a quantity is attributed to more than one item (or a modifier such as monthly could attach to the noun or the verb), it can be unclear whether the quantity applies to each item or to all of them in the aggregate. Say each or in the aggregate. (11.1; rider)
  - Look for: an amount or quantity attributed to plural items or periodic payments without each or in the aggregate
  - Test: Could the amount be per item or a total?
  - Fix: Say each or in the aggregate, depending on the meaning you intend.

### Chapter 12: Syntactic Ambiguity

- **R-12.1-syntactic-ambiguity-def** [sev 1] Syntactic ambiguity arises from word order and the grammatical relations among words and phrases; it features in litigation more often than part-versus-whole ambiguity. A modifier is a word or phrase that changes the meaning of a word or phrase to which it is grammatically related. (12.1, 12.2; PDF p. 550)
- **R-12.3-preceding-modifier** [sev 1] Preceding-modifier ambiguity: a modifier before two or more nouns (only children's apparel, accessories, and footwear) can modify only the first noun or all of them. (12.3, 12.4, 12.5...; PDF p. 550)
  - Look for: an adjective or noun modifier before a series of two or more nouns
  - Test: Ask whether the modifier should apply to every noun in the series.
  - Fix: If only the first: enumerate (only (1) children's apparel, (2) accessories, and (3) footwear), use semicolons, or put that noun last. If all: repeat the modifier before each noun, or restate (only the following items for children: apparel, accessories, and footwear).
  - Book example: Acme may sell in the Stores only children's apparel, accessories, and footwear. → Acme may sell in the Stores only the following items for children: apparel, accessories, and footwear.
- **R-12.7-trailing-modifier** [sev 1] Trailing-modifier ambiguity: a modifier after two or more nouns or clauses (incur any debt or make any capital expenditure in excess of $500,000) can modify only the last element or all of them. (12.7, 12.8, 12.9...; PDF p. 552)
  - Look for: a modifier after the last of two or more nouns, verbs, or clauses
  - Test: Ask whether the modifier should reach every element before it.
  - Fix: If only the last: put that element first (make any capital expenditure in excess of $500,000 or incur any debt), or use semicolons. If all: repeat the modifier after each element. Enumeration alone can't fix it; tabulation works but is disfavored for short clauses.
  - Book example: Acme shall not incur any debt or make any capital expenditure in excess of $500,000. → Acme shall not incur any debt in excess of $500,000 or make any capital expenditure in excess of $500,000.
- **R-12.14-no-last-antecedent-reliance** [sev 1] Don't rely on the rule of the last antecedent, or on the "comma test" (a comma before a modifier following a series makes it apply to the whole series), to resolve a modifier's reach; eliminate the ambiguity. (12.14, 12.26; PDF p. 553)
- **R-12.15-preceding-and-trailing** [sev 1] Preceding-and-trailing-modifier ambiguity: with modifiers both before and after two noun phrases (Delaware corporations and LLCs qualified to do business in New York), four meanings are possible. (12.15, 12.16, 12.17; PDF p. 554)
  - Look for: a series with both a leading and a trailing modifier
  - Test: List the four combinations of which noun each modifier reaches.
  - Fix: Repeat a modifier to show it reaches both nouns (Delaware corporations qualified to do business in New York and Delaware LLCs qualified to do business in New York); switch the order of the noun phrases to show it doesn't.
- **R-12.18-modifier-between-nouns** [sev 1] Medial-modifier ambiguity: a modifier after one noun in a string (the Lee Assets, excluding the Miller Assets, the Chang Assets, and the Meyer Assets) leaves unclear whether later nouns fall within it. (12.18; PDF p. 555)
  - Look for: excluding, including, other than, or except inside a series
  - Test: Ask whether the later nouns are part of the exception or additional items.
  - Fix: Use enumeration or parentheses: the Lee Assets (excluding the Miller Assets), the Chang Assets, and the Meyer Assets; or the Lee Assets (excluding the Miller Assets, the Chang Assets, and the Meyer Assets).
- **R-12.19-squinting-modifier** [sev 1] Squinting-modifier ambiguity: a modifier placed between two elements could modify what comes before or after it (If Acme rejects any Asset within 10 days the Seller shall reimburse Acme). (12.19, 12.20; PDF p. 556)
  - Look for: a time or condition phrase sitting between a conditional clause and the main clause with no comma, or with only a comma to show its attachment
  - Test: Read the modifier with the preceding element, then with the following one; if both make sense, it squints.
  - Fix: Move the modifier, and if needed use it twice: If no later than 10 days after the Closing Acme rejects any Asset, Seller shall no later than 10 days after receiving the notice of rejection reimburse Acme. Don't rely only on a comma.
- **R-12.21-uncertain-length** [sev 1] Uncertain-length ambiguity: it can be unclear whether a modifier incorporates a following relative clause (any item of apparel not constituting a Product that Widgetco has ... sold). (12.21; PDF p. 557)
  - Look for: a negative or participial modifier followed by a relative clause
  - Test: Ask whether the relative clause belongs to the modifier (not constituting a Product that Widgetco sold) or to the head noun (item of apparel that Widgetco sold).
  - Fix: Place the modifier in a conditional clause: any item of apparel, on condition that it does not constitute a Product that Widgetco has ... sold (or ... that Widgetco has sold, on condition that the item does not constitute a Product).
- **R-12.22-poorly-placed-modifier** [sev 1] Misplaced-modifier ambiguity: a modifier separated from what it modifies (... to an account designated by Galactic no later than five Business Days after the closing ...; a motor vehicle included in the Assets that is in Acme's possession) can attach to the wrong element. (12.22, 12.23; PDF p. 557)
  - Look for: a time phrase or relative clause placed after an intervening noun
  - Test: Ask what the nearest preceding element is and whether the modifier is meant for it.
  - Fix: Put the modifier next to what it modifies, or move it to the front of the sentence (No later than 5 Business Days after the closing of a sale, Sellers shall deliver the Proceeds of that sale to Galactic).
  - Book example: every certificate of title relating to a motor vehicle included in the Assets that is in Acme's possession → every certificate of title that is in Acme's possession relating to a motor vehicle included in the Assets
- **R-12.24-opening-closing-modifier** [sev 1] Opening-or-closing-modifier ambiguity: a phrase that opens or closes a sentence containing two or more clauses (Other than in the Ordinary Course of Business, Acme shall not incur debt and Acme shall not make any capital expenditures; ..., unless and until terminated by one year prior notice) can modify one clause or all. (12.24, 12.25, 12.27...; PDF p. 558)
  - Look for: an opening or closing phrase in a sentence with two or more clauses
  - Test: Ask whether the phrase should govern every clause.
  - Fix: If it modifies both and the clauses share a subject, combine them and put the phrase in front (Other than in the Ordinary Course of Business, Acme shall not incur debt or make any capital expenditures). If only the first, put it after the first clause; if only the second, reverse the clauses and put it after the new first clause.
- **R-12.33-offsetting-commas** [sev 1] Offsetting-comma ambiguity: meaning that turns on whether a closing modifier is set off by commas (100% of the Redemptive Value [,] as of the Cut-off Date [,] of the Asset; all Acme inventory, including ... fertilizer materials [,] that Widgetco sold to Acme). (12.33, 12.34, 12.35...; PDF p. 561)
  - Look for: a phrase whose attachment depends on the presence or absence of one or two commas
  - Test: Read the sentence with and without the commas; if the meaning changes, the commas carry too much.
  - Fix: Restructure so the meaning doesn't depend on commas. Be wary of ostensibly offsetting commas where the part before the first comma can stand alone.
- **R-12.39-move-shared-preposition** [sev 1] To eliminate offsetting-comma confusion where two clauses share a prepositional phrase, move the shared preposition before each comma so the reader knows something is yet to come (or use two sentences). (12.39, 12.40, 12.41...; PDF p. 563)
  - Book example: The Vendor will not be liable to Acme or any Buyer, and neither Acme nor any Buyer will be liable to the Vendor, for any damages that are not a reasonably foreseeable consequence of breach. → The Vendor will not be liable to Acme or any Buyer for, and neither Acme nor any Buyer will be liable to the Vendor for, any damages that are not a reasonably foreseeable consequence of breach.
- **R-12.44-restrictive-def** [sev 2] A restrictive clause gives essential, distinguishing information (The cakes that George baked were delicious); a nonrestrictive clause gives a supplemental aside (The cakes, which George baked, were delicious). Usage authorities recommend that for restrictive clauses and comma-which for nonrestrictive ones. (12.44, 12.45, 12.46; PDF p. 564)
- **R-12.47-which-that-ambiguity** [sev 1] Restrictive-versus-nonrestrictive ambiguity: when drafters blur that and which (which in restrictive clauses, comma-which used for that, dropped commas before which), a relative clause can be read as limiting the noun or as an aside (all Contracts other than Assumed Contracts which are subject to section 4.3). (12.47, 12.48, 12.49...; PDF p. 564)
  - Look for: which introducing a relative clause, with or without a preceding comma
  - Test: Ask whether the clause is meant to narrow the noun (restrictive) or merely add information (nonrestrictive), and whether a reader could take it the other way.
  - Fix: Use that for restrictive clauses; don't use nonrestrictive clauses; if the noun the clause modifies is unclear, use parentheses around any intervening phrase.
  - Book example: There is no fact known to any Credit Agreement Party or any of its Subsidiaries which has had, or could reasonably be expected to have, a Material Adverse Effect. → There is no fact known to any Credit Agreement Party or any of its Subsidiaries that has had, or could reasonably be expected to have, a Material Adverse Effect.
- **R-12.53-no-nonrestrictive** [sev 1] Don't use nonrestrictive clauses in contracts; either tackle an issue head-on or omit it. (12.53, 12.54, 12.55; PDF p. 566)
- **R-12.56-that-not-which** [sev 1] Use that, not which, in restrictive clauses. (12.56; PDF p. 566)
- **R-12.57-that-reach-parentheses** [sev 1] Using that may not be enough when it is unclear which noun the clause modifies (any Employee Benefit Plan, other than a Multiemployer Plan, that is subject to Title IV); put parentheses around the intervening phrase. (12.57; PDF p. 566)
  - Fix: Put parentheses around other than a Multiemployer Plan.
  - Book example: "Pension Plan" means any Employee Benefit Plan, other than a Multiemployer Plan, which is subject to the provisions of Title IV of ERISA ... → (see fix)
- **R-12.58-use-serial-comma** [sev 2] Use the serial comma (a comma before the conjunction joining the last two elements of a series of three or more). (12.58, 12.59; PDF p. 567)
- **R-12.60-combined-elements** [sev 1] Combined-element ambiguity: without a serial comma, the last two elements of a series can read as one combined element (raspberry, chocolate chip and cherry). (12.60, 12.61; PDF p. 567)
  - Look for: series of three or more with no comma before the final and/or
  - Test: Ask whether the last two elements could be one item.
  - Fix: Add the serial comma, and if an element is itself a combination, reorder or restructure so it can't be misread.
- **R-12.62-inadvertent-apposition** [sev 1] Apposition ambiguity: omitting the serial comma can make the second element read as an appositive explaining the first (To my parents, Ayn Rand and God), and the serial comma itself can create apposition (To my mother, Ayn Rand, and God). (12.62, 12.63, 12.64...; PDF p. 567)
  - Look for: a series in which the second element could be read as renaming the first
  - Test: Ask whether the second element could be read as a description of the first.
  - Fix: Add the serial comma where it prevents apposition; where it creates apposition, reorder the elements or restructure.
- **R-12.70-inadvertent-object** [sev 1] Shared-preposition ambiguity: without a serial comma, a final item can read as a second object of a preposition in the preceding item (packing for shipment or distribution of), changing who or what is covered. (12.70, 12.71, 12.72...; PDF p. 569)
  - Look for: a series whose last item contains a preposition followed by X or Y
  - Test: Ask whether the last noun is a separate item in the series or a second object of the preposition.
  - Fix: Use parentheses (packing (for shipment) or distribution), reorder, or use semicolons, enumeration, or tabulation; don't rely on the comma alone.
- **R-12.74-dont-rely-on-comma** [sev 1] Use the serial comma, but don't rely on a comma to establish meaning; instead of or in addition to it, use another technique (parentheses, reordering, semicolons, enumeration, or tabulation) to eliminate the ambiguity. (12.74, 12.75, 12.76...; PDF p. 570)
- **R-12.79-delimiting-commas** [sev 1] Delimiting-comma ambiguity: offsetting commas meant to make the part after the second comma modify both preceding parts (in redeeming, or protecting any Grantor's interest in, the Excluded Assets) work only if both outer parts are fragments; if the part before the first comma can stand alone, the hint is too subtle. (12.79, 12.80, 12.81...; PDF p. 572)
  - Look for: X, or Y, Z, where Z is meant to complete both X and Y
  - Test: Check whether the part before the first comma and the part after the second are fragments that can't be read in isolation; if either can stand alone, the structure is ambiguous.
  - Fix: Repeat the shared element: in redeeming the Excluded Assets or protecting any Grantor's interest in the Excluded Assets ("three words well spent"). Use delimiting commas only if both parts are fragments and the economy is significant.
  - Book example: in redeeming, or protecting any Grantor's interest in, the Excluded Assets → in redeeming the Excluded Assets or protecting any Grantor's interest in the Excluded Assets
- **R-12.88-multiple-instances** [sev 1] Each additional instance of syntactic ambiguity in a sentence doubles the possible meanings (three instances in one Georgia statute line yield eight). (12.88, 12.89; PDF p. 574)
  - Test: Count the ambiguous attachments in a sentence; with two or more, restructure rather than patch.
- **R-12.90-restructure** [sev 1] Sometimes, instead of remedial work on an awkward structure, start afresh; for example, eliminate an abstract noun that creates the ambiguity. (12.90, 12.91, 12.92...; PDF p. 574)
  - Book example: Upon occurrence of a Change in Law or a Force Majeure Event that adversely affects the Seller's performance under this agreement, the Buyer and the Seller shall negotiate in good faith ... → If a Change in Law or a Force Majeure Event adversely affects the Seller's performance under this agreement, the Buyer and the Seller shall negotiate in good faith ...

### Chapter 12: Blog: A New Kind of Syntactic Ambiguity

- **R-rider-rnr-pivot** [sev 1] Right-node-raising pivot ambiguity: when two coordinated clauses share a final element (right node raising), it can be unclear which words the shared element (the pivot) attaches to. If you use right node raising, use offsetting commas; they aren't optional. Better still, restructure so meaning doesn't depend on the commas. (12.79, 12.86, 12.87...; rider)
  - Look for: two coordinated clauses that share a final element, with no offsetting commas
  - Test: Identify the shared final element and ask whether it could attach to more or less of each clause.
  - Fix: Add offsetting commas around each incomplete part, or repeat the shared element in each clause (12.75-12.78: don't rely on commas alone).

### Chapter 13: Selected Usages

- **R-13.73-at-least-one-of-categories** [sev 1] If at least one of refers to categories, or to units within categories, say so explicitly, and say whether you mean units in all categories or in fewer than all; if it refers to units, nothing more is needed. (13.73, 13.77, 13.85; PDF p. 594)
  - Look for: at least one of before a list of categories that each contain units
  - Test: Could one of mean one item within a category or one category? If so, the provision is ambiguous.
  - Fix: at least 1 of the following categories: ...; at least 1 unit in each of the following categories: ...; at least 1 unit in [at least] 1 of the following categories: ...
- **R-13.163-special-and-consequential** [sev 1] Don't exclude both special damages and consequential damages; U.S. courts generally treat them as synonyms, and special damages means something else in tort, so the pairing adds confusion. (13.163; PDF p. 614)
  - Fix: Use the alternatives in R-13.167-foreseeable-damages and R-13.170-special-circumstances.
- **R-13.164-direct-and-indirect** [sev 1] Don't exclude both direct and indirect damages; that could lead to a fight over whether all damages are excluded or the contract is void. (13.164; PDF p. 614)
  - Fix: State which damages are recoverable.
- **R-13.376-including-obvious-examples** [sev 2] If you rely on the general word's everyday meaning, don't follow it with a list of obvious examples; fruit, including oranges, lemons, and grapefruit invites a court to limit fruit to citrus. (13.376; PDF p. 662)
  - Look for: general word followed by including and several obvious members of the class
  - Fix: Delete the obvious examples, or use an enlarging item.
- **R-13.399-including-class-modifier** [sev 1] When a modifier applies to the class (red fruit, including apples; any American automobile, including any truck), a court would likely apply the modifier to the items after including, but with a vague modifier (disruptive activity, including playing music) one might argue it doesn't. Be explicit about which meaning you intend. (13.399, 13.400, 13.401...; PDF p. 668)
  - Look for: modifier on the class noun before including
  - Test: Does the class modifier apply to the items after including? If the reader can't tell, the provision is ambiguous.
  - Fix: State whether the modifier applies (for example, add 'that constitute consequential damages', or use and instead of including).
- **R-13.623-termination-prior-notice** [sev 1] Don't say Acme may terminate this agreement upon (or by giving, or with) 60 days' prior notice; upon and by giving suggest termination when notice is given, and with is unclear. A date or event restriction (After X, Acme may terminate ...) leaves unclear whether it applies to terminating or to giving notice. State that if the party notifies the other that it is terminating, the agreement terminates a stated period after the other party receives that notice. (13.623, 13.624, 13.625...; PDF p. 720)
  - Fix: If [after X] Acme notifies Widgetco that Acme is terminating this agreement in accordance with this section 4, this agreement will terminate 60 days after the day Widgetco receives that notice.
- **R-13.635-notwithstanding-the-foregoing** [sev 1] Notwithstanding the foregoing is ambiguous: the foregoing might refer to the previous sentence, all preceding text, or something in between. (13.635; PDF p. 722)
  - HOUSE: partly superseded: House rule 4: where a reference is needed, name the provision by its heading, not its number (the section titled "Payment"); better, restructure so no reference is needed.
  - Test: Can the reader tell exactly which text the foregoing refers to?
  - Fix: Name the provision (subject to section 3.2).

### Chapter 13: Blog: Say Hi to "Ambiguity of the Specific Versus the General"

- **R-rider-specific-vs-general** [sev 1] Treat ejusdem generis and including as one distinct kind of ambiguity, "ambiguity of the specific versus the general": a list of specific items followed by a general term (insects, birds, rodents, or other animals), or a general term followed by including and examples, may be read as limited to things like the specific items or as covering the whole general class. (13.359, 7.5; rider)
  - Look for: specific items followed by a general catchall, or a general term followed by examples
  - Test: Could the general term be read as limited to things like the listed items?
  - Fix: Apply the including rules (13.360-13.407): define the class, put the general word last with an explicit statement of scope, or list exhaustively.

### Chapter 14: Numbers and Formulas

- **R-14.25-order-of-operations** [sev 1] When a formula mixes operations, specify the order. In equations, use parentheses even where mathematical convention would make them unnecessary ((2 x 3) + 4; (10 - 4) + 2), because a lawyer may not know the convention and left-to-right can't be counted on. (14.25, 14.26, 14.27; PDF p. 806)
  - Look for: formula combining plus/minus with multiplied by/divided by
  - Test: Could the operations be performed in a different order and give a different result?
  - Fix: Use the result of, enumeration, or parentheses in an equation.
- **R-14.32-amount-by-which** [sev 1] Whatever the context, avoid the amount by which A exceeds B (wordy), the excess of A over B (A over B can express a fraction), and the difference between A and B (5 and 7 could give 2 or -2). (14.32; PDF p. 808)
  - Fix: A minus B
- **R-14.41-formula-ambiguity** [sev 1] Watch for a percentage or multiplier followed by a phrase that could apply before or after another operation (23.4% of the price in excess of X less the Costs and Incentives); use enumeration to state the intended meaning unambiguously. Likewise watch whether a minimum or maximum modifies the whole product or only one factor. (14.41, 14.42, 14.43...; PDF p. 810)
  - Fix: Enumerate: (1) 23.4% of (A) ... minus (B) ...
- **R-14.65-no-percent-in-equation** [sev 1] Don't use the percent sign in equations (3 / 4% could mean 75% or 0.75%); if you want a percentage result, say so in the prose preamble. (14.65; PDF p. 815)
  - Look for: % inside an equation
  - Fix: State the percentage result in the lead-in.
- **R-14.67-stepped-vs-flat** [sev 1] A tiered rate schedule is ambiguous unless it says whether the rate for the band in which the total falls applies to the whole amount (a shifting flat rate) or each rate applies only to the amount within its band (a stepped rate). For a stepped rate, state increments in prose (5% of the first million dollars ...), use an IRS-style table with a cumulative base, or state in the preamble that each percentage applies only within its range; for a shifting flat rate, say the percentage for the range in which the year's revenue falls applies to all of it, or add of total gross annual revenue after each percentage. Incremental rates is not clear enough. (14.67, 14.68, 14.69...; PDF p. 816)
  - Look for: table or list of rates by revenue or volume band
  - Test: At a total in a higher band, does the higher rate apply to all of it or only to the excess?
  - Fix: ... of total gross annual revenue (flat); 5% of the first $1 million, 6% of the next $1 million ... (stepped)
- **R-14.75-range-gaps-overlaps** [sev 1] Avoid overlap between consecutive ranges (1-10 and 10-20 leave ten unclear; use 1-10 and 11-20). For ranges that can run to decimals (dollars), don't use from $1,000 to $2,000 and from $2,000 to $3,000; use over $1,000 but not over $2,000. Don't fix overlap by creating a gap (from $1,000 to $1,999 leaves $1,999.01-$1,999.99 unplaced). (14.75, 14.76, 14.77; PDF p. 818)
  - Look for: consecutive ranges sharing an endpoint, or leaving a gap
  - Test: Does every possible value fall in exactly one range?
  - Fix: over $1,000 but not over $2,000; over $2,000 but not over $3,000
  - Exceptions: A gap is appropriate if the unit comes only in whole units (1-10 / 11-20 widgets) (14.77). | Overlap matters more under a shifting flat rate than a stepped rate (14.75).
