# Vagueness

Vagueness is not ambiguity: text is vague when the circumstances decide whether a party has met it (7.46). MSCD treats vagueness, used with restraint, as an essential tool; ambiguity is never acceptable.

## Contents

- Policy
- Contents of the rules list, then Rules: every vagueness rule, by MSCD chapter

## Policy

- **Flag every vague standard** (*reasonable*, *promptly*, *material*, *substantial*, *satisfactory*, *best efforts*, and the like) and classify it: keep on purpose, replace with a specific standard, or ask Blake.
- **Rule *keep* only when no measure exists** (*reasonable efforts*, *substantially all*) and say why; otherwise offer the measure the contract supplies, or a bracketed number, and ask Blake. MSCD 7.48-7.53 give the reasons a drafter keeps vagueness (low stakes, an outcome the party can't control, the cost of negotiating precision); whether they apply is Blake's deal judgment, not yours. Even where it stays, narrow its scope.
- **Never use gradations of vagueness** such as degrees of negligence or a hierarchy of efforts (7.54; 8.3).
- **Never invent a number.** Use a bracketed blank and ask: *promptly, but no later than [__] Business Days after* (10.131).
- **Pair every efforts obligation with a performance standard**; even *promptly* is enough (8.139-8.143). Use only *reasonable efforts* (8.134).
- ***material***: decide whether the drafter means "nontrivial" or "dealbreaker" (9.21-9.32); omit it, use *nontrivial*, or use a defined *Material* (9.51-9.64).

> **Book examples are in MSCD5's style, not house style.** They may use lowercase *schedule*, *1 January 2024*, spelled-out numbers, 1.1 numbering, *the* before party names, or a passive that MSCD accepts. Restate any example in house style (`house-style.md`) before you put it in a contract or a comment. For the other side's drafts, the house rule is to flag everything, whatever a rule's "let-pass" or "style-only" label says.


## Contents of the rules list

- Chapter 3: Language of Obligation
- Chapter 3: Language of Discretion
- Chapter 3: Language of Policy
- Chapter 6: Defined Terms
- Chapter 7: Sources of Uncertain Meaning
- Chapter 8: Reasonable Efforts
- Chapter 9: Material
- Chapter 9: Material Adverse Change
- Chapter 10: References to Time
- Chapter 13: Selected Usages
- Chapter 15: Internal Rules of Interpretation

## Rules (169, generated from `data/rules.jsonl`)

Format: id, severity (1 = ambiguity or meaning-changing; 2 = vagueness or dispute risk; 3 = style), the rule, and its MSCD paragraphs and PDF page. `HOUSE` marks a rule that Blake's house style changes: apply the house rule. For a rule's full record (test, fix, exceptions, verified book examples), run `python3 scripts/rules_query.py --id <id>`.


### Chapter 3: Language of Obligation

- **R-3.132-no-will-be-expected-to** [sev 2] Don't use will be expected to (common in employment agreements); it's oddly circumspect, and the consequences of an unmet expectation are unclear. (3.132; PDF p. 161)
  - Book example: [2-1n] ××: Acme will be expected to purchase ... . → [2-1] ✓✓: Acme shall purchase ... .
- **R-3.144-no-is-responsible-for** [sev 2] Don't use is responsible for + present participle to express a duty owed to another party; it is long-winded and unclear whether it creates a duty or acknowledges one from another source. (3.144; PDF p. 162)
  - Book example: [2-1m] ××: Acme is responsible for purchasing ... . → [2-1] ✓✓: Acme shall purchase ... .
- **R-3.162-no-procure-ensure-require** [sev 2] Don't use variants of shall cause: shall procure (Commonwealth, legalistic), shall ensure (implications unclear), shall require (could mean a duty to impose a duty), shall see to it that, or shall see to + abstract noun. (3.162; PDF p. 170)
  - Book example: [3-4d] ×: Parent shall procure Sub to sell the Widget Assets ... . → [3-4c] ✓✓: Parent shall cause Sub to sell the Widget Assets ... .
  - Book example: [3-4e] ×: Parent shall ensure that Sub sells the Widget Assets ... . → [3-4c] ✓✓: Parent shall cause Sub to sell the Widget Assets ... .
- **R-3.176-prevent-undesirable-events** [sev 2] To stop an undesirable event not fully within a party's control, use two provisions: a reasonable efforts obligation to take steps to prevent it, and a risk-allocation provision making the party liable for resulting losses if it happens anyway. Avoid shall prohibit (unclear how much is required) and shall prevent (liable regardless?). (3.176, 3.178, 3.179...; PDF p. 173)
  - HOUSE: House addition: For a nonparty subject (an Authorized User, an employee, a subcontractor), restructure so a party is the subject (Blake's decision): a reasonable-efforts duty plus a risk allocation, Customer shall use reasonable efforts to prevent any Authorized User from sharing credentials, and Customer is liable for any loss that results from an Authorized User's sharing them (3.180; 8.5); shall cause only for the party's instrumentality, such as its subsidiary or its own board (3.160-3.161). In a review, bracket the liability for Blake. See house-style.md section 8.

### Chapter 3: Language of Discretion

- **R-3.255-reasonable-discretion** [sev 2] Be aware that reasonable discretion might curtail discretion: a reasonableness standard could be read as stricter than good faith. (3.255; PDF p. 190)

### Chapter 3: Language of Policy

- **R-3.338-no-subject-to-change-eligible** [sev 2] Instead of is subject to + abstract noun with an abstract-noun subject, use may + verb with a party as subject; instead of is eligible for, state the obligation. (3.338; PDF p. 213)
  - Book example: The Employee's position and assignments are subject to change. → The Company may change the Employee's position and assignments.
  - Book example: The Employee will be eligible for a bonus if ... → The Company shall pay the Employee a bonus if ...
- **R-3.341-no-policy-obfuscation** [sev 2] Don't turn provisions about party actions into opaque language of policy through jargon (lead-time, net 30); state the action and the actor, even at the cost of extra words. (3.341, 3.342, 3.343...; PDF p. 213)
  - Book example: Acme will have a lead-time of up to 45 days from accepting a Purchase Order for scheduling Services. → No later than 45 days after it receives a Purchase Order, Acme shall notify the Customer of the schedule for performing the Services requested in that Purchase Order.
  - Book example: Payment terms are net 30 from the date of the invoice. → The Customer shall pay each invoice no later than 30 days from the date of the invoice.

### Chapter 6: Defined Terms

- **R-6.38-includes-enlarging** [sev 2] An enlarging definition (part of the meaning) uses includes; a limiting definition (excluding something) uses does not include. Used alone, both leave the full scope unstated and can create mischief. (6.38; PDF p. 338)

### Chapter 7: Sources of Uncertain Meaning

- **R-7.1-six-sources** [sev 1] Distinguish six sources of uncertain meaning: ambiguity, not being sufficiently specific, mistake, conflict, not addressing an issue, and vagueness. Don't lump them all under "ambiguity," as courts and Black's Law Dictionary do. (7.1, 7.2, 7.3...; PDF p. 361)
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
- **R-7.46-vagueness-def** [sev 2] Vague words include prompt, reasonable, material, negligent, satisfactory, substantial, and related adverbs. Vagueness involves no clear demarcation (borderline cases) and dependence on context, judged by what a reasonable person would do in the circumstances. (7.46; PDF p. 371)
- **R-7.47-prefer-specific** [sev 2] Prefer a specific standard (no later than five days after) to a vague one (promptly) where you can. (7.47, 7.48; PDF p. 372)
  - Book example: promptly → no later than five days after
- **R-7.48-when-vagueness-ok** [sev 2] Use vagueness when lack of control over the future or someone else's conduct makes a precise standard senseless (for example, reimbursing reasonable legal expenses), or when addressing an issue precisely would make negotiations longer or more contentious than the parties want. (7.48, 7.49, 7.50; PDF p. 372)
- **R-7.51-limit-vagueness-risk** [sev 2] Use vagueness only if not too much is at stake and the context is commonplace enough that the parties and any court have a basis for determining what is reasonable in the circumstances. (7.51, 7.52; PDF p. 372)
- **R-7.53-reduce-vagueness-scope** [sev 2] Reduce the scope of vagueness, for example by adding specific obligations alongside a reasonable efforts obligation. (7.53; PDF p. 373)
- **R-7.54-no-gradations** [sev 2] Treat gradations of vagueness as unhelpful, as with negligent, grossly negligent, reckless, and wanton, and especially a supposed spectrum of efforts standards. (7.54, 7.55; PDF p. 373)
  - Exceptions: In the right context a spectrum can be subdivided coherently, as with MSCD's distinction between material (dealbreaker) and nontrivial (7.55).
- **R-7.56-blurred-boundaries** [sev 2] The categories blend: lexical ambiguity and insufficient specificity differ by degree, as do insufficient specificity and failing to address an issue; a usage can be both vague and ambiguous (best efforts, material). (7.56, 7.57, 7.58...; PDF p. 373)

### Chapter 8: Reasonable Efforts

- **R-8.1-no-efforts-hierarchy** [sev 1] Don't treat efforts standards as a hierarchy: best efforts, reasonable efforts, commercially reasonable efforts, and the rest all come down to reasonableness. (8.1, 8.2, 8.3...; PDF p. 374)
- **R-8.3-efforts-terms** [sev 3] An "efforts standard" is a phrase featuring the word efforts; an "efforts provision" is a contract sentence that includes an efforts standard. (8.3; PDF p. 374)
- **R-8.4-when-efforts** [sev 2] Use an efforts standard when one party wants another to further a goal that nonparties (or weather or other unpredictable natural events) have a say in achieving, such as obtaining a permit or consents, or promoting sales. (8.4, 8.5, 8.6...; PDF p. 375)
  - Look for: unqualified obligation to achieve a result outside the obligor's control (Acme shall obtain the Permits) or to promote a goal (Jones shall promote the sale of Widgets)
  - Test: Ask whether achieving the goal is entirely within the party's control. If not, an unqualified obligation makes the party liable however hard it worked.
- **R-8.8-efforts-components** [sev 2] An efforts standard has components: a noun (efforts or endeavours); "qualitative" adjectives (reasonable, best, good-faith, diligent, and others, alone or combined, as in reasonable best efforts); postpositive modifiers (efforts that are reasonable; efforts in good faith); activity adjectives; determiners; and a verb. The variety adds confusion and nothing of value. (8.8, 8.11, 8.12; PDF p. 376)
- **R-8.9-efforts-not-endeavours** [sev 3] Use efforts rather than endeavours (or endeavors); the difference is only one of style, endeavours is in long decline, and the modern choice is efforts. (8.9, 8.171; PDF p. 376)
  - Exceptions: English and Australian drafters favor endeavours; nothing suggests English judges would treat the switch as changing meaning (8.171).
- **R-8.10-no-other-nouns** [sev 3] Don't use other nouns in place of efforts (for example, actions); they offer only needless variety. (8.10; PDF p. 377)
- **R-8.13-no-activity-adjective** [sev 3] Don't use an "activity" adjective in an efforts standard (reasonable sales efforts); it inflicts abstract nouns on the reader and invites redundancy. (8.13, 8.150; PDF p. 377)
  - Book example: Acme shall use reasonable sales effort to sell ... → (see fix)
- **R-8.14-no-commercially** [sev 2] Don't use commercially (or commercial) in an efforts standard; it is redundant and invites legalistic arguments for a different meaning. If you mean something other than reasonable efforts, say so explicitly. (8.14, 8.108, 8.109...; PDF p. 378)
  - Fix: Use reasonable efforts.
- **R-8.15-no-very-all-every** [sev 2] Don't use very (very best efforts), all (all reasonable efforts), or every (every reasonable effort) in an efforts standard; they are delexicalized flourishes that invite attribution of meaning. Use efforts in the plural. (8.15, 8.16, 8.111...; PDF p. 378)
- **R-8.17-use-verb-use** [sev 3] Use the verb use with an efforts standard (use reasonable efforts); don't vary the verb and don't add a pronoun (use its reasonable efforts). (8.17, 8.149, 8.150; PDF p. 378)
  - Book example: use its reasonable efforts → use reasonable efforts
- **R-8.18-no-efforts-substitutes** [sev 3] Don't combine an efforts standard with a substitute verb (use reasonable efforts to endeavor; endeavor to use reasonable efforts), and don't say a party shall not negligently permit an act instead of requiring it to use reasonable efforts to stop the act. (8.18; PDF p. 378)
- **R-8.19-no-best-efforts-basis** [sev 3] Don't use on a best-efforts basis as a wordy alternative to a conventional efforts provision. (8.19; PDF p. 379)
  - Exceptions: On a best-efforts basis remains a securities term of art (8.19).
  - Book example: The parties shall work together on a best-efforts basis to obtain ... all necessary Work Authorizations. → The parties shall together use reasonable efforts to obtain ... all necessary Work Authorizations.
- **R-8.20-efforts-to-agree** [sev 1] If a provision makes an arrangement contingent on future agreement, use a good-faith standard (negotiate in good faith) rather than an efforts standard, and don't use future agreement to put off negotiations. (8.20, 8.21, 8.22; PDF p. 379)
  - Exceptions: Illinois holds a best-efforts promise too vague to bind if the parties fail to articulate what performance it requires (Kraftco v. Kolbus, Ill. App. Ct. 1971) (8.20). | Sometimes contingency on future agreement is unavoidable (8.22).
- **R-8.23-compliance-circumstances** [sev 2] Because efforts standards are vague, compliance depends on the circumstances of the case, with the uncertainty that entails. (8.23; PDF p. 380)
- **R-8.24-commentary-unreliable** [sev 2] Don't rely on commentary describing a hierarchy (ABA M&A Committee "general sense of a hierarchy"; Garner; Stark); much of it is insubstantial or misdescribes U.S. caselaw. English and Canadian commentators treat the hierarchy as established fact. (8.24, 8.25, 8.26...; PDF p. 380)
- **R-8.29-us-caselaw** [sev 2] U.S. courts, with a few isolated exceptions, reject the idea that best efforts requires every conceivable effort and decline to recognize a hierarchy; they variously equate best efforts with good faith, more than good faith, diligence, or reasonableness, and often with reasonable efforts. (8.29, 8.30, 8.31...; PDF p. 382)
  - Exceptions: Only three opinions suggest best efforts is more onerous, without explanation, and none has been followed: In re Hyman Cos. (Bankr. E.D. Pa. 2010); In re Chateaugay (S.D.N.Y. 1996); Krinsky v. Long Beach Wings (Cal. Ct. App. 2002) (8.37).
- **R-8.38-good-faith-efforts** [sev 2] Don't use good-faith efforts; it brings back uncertainty, because courts will likely apply whatever standard they use for the implied duty of good faith (which might require dishonesty for breach, or rest on reasonableness), and whether good faith is objective or subjective is unsettled. (8.38, 8.39, 8.40...; PDF p. 384)
- **R-8.41-delaware-caselaw** [sev 2] Delaware courts don't distinguish efforts standards in practice: Williams v. Energy Transfer (Del. 2017) read commercially reasonable efforts and reasonable best efforts alike as requiring all reasonable steps; Akorn (Del. Ch. 2018) drew no distinction; AB Stable (Del. Ch. 2020) held commercially redundant. Strine's Williams dissent is a nonbinding exception. (8.41, 8.42, 8.43...; PDF p. 385)
- **R-8.47-ucc-best-efforts** [sev 2] Under UCC § 2-306(2), a lawful exclusive-dealing agreement imposes, unless otherwise agreed, best efforts to supply and to promote; Official Comment 5 equates that with reasonable diligence and good faith, which appears to preclude treating best efforts as more onerous for Article 2. (8.47, 8.48, 8.49; PDF p. 386)
- **R-8.50-english-canadian-caselaw** [sev 1] Know that English and Canadian courts endorse a hierarchy (Rhodia v. Huntsman: reasonable endeavours "probably" requires one reasonable course, best endeavours all of them, in obiter dicta; Atmospheric Diving Systems (B.C.S.C. 1994): best efforts is higher, yet means all reasonable steps), although Jet2.com v. Blackpool Airport (EWCA 2012) treated best and all reasonable endeavours as meaning the same. (8.50, 8.51, 8.52...; PDF p. 387)
- **R-8.62-other-jurisdictions** [sev 2] The High Court of Australia reads best endeavours as requiring what a party reasonably can do "but no more" (Hospital Products, 1984; Electricity Generation v. Woodside, 2014); Singapore's Court of Appeal (KS Energy, 2014) found all reasonable endeavours not usefully distinguishable from best endeavours yet more onerous than reasonable endeavours. (8.62, 8.63; PDF p. 391)
- **R-8.64-lack-of-explanation** [sev 2] Recognize that neither side of the efforts debate offers a plausible explanation: U.S. courts reject a hierarchy without stating a rationale, and cases and commentary supporting one merely assert it (Rhodia's one-course/all-courses distinction; Brooke Homes; Atmospheric Diving Systems; law-firm newsletters), expressed in equivocal terms (probably, might, normally) that make relying on them rash. (8.64, 8.65, 8.66...; PDF p. 392)
- **R-8.80-more-than-reasonable-unworkable** [sev 2] Don't try to impose an obligation to act more than reasonably through an efforts standard; there is no basis for deciding how much more than reasonable is required, as with the chaotic degrees of negligence. (8.80, 8.81, 8.82...; PDF p. 395)
- **R-8.91-best-efforts-ambiguous** [sev 1] Don't use best efforts: in colloquial English best is a delexicalized flourish that doesn't signal acting more than reasonably, but legalistic readers attribute extra meaning to it, so best efforts is ambiguous as well as vague. (8.91, 8.92, 8.93...; PDF p. 398)
  - Fix: Use reasonable efforts, ideally as a defined term (8.155).
- **R-8.101-reasonable-efforts-construct** [sev 3] Reasonable efforts is a legal construct absent from colloquial English, best understood as the profession's response to fears that judges would ignore the idiomatic meaning of best efforts. (8.101, 8.102, 8.103...; PDF p. 400)
- **R-8.114-misinterpretation-elements** [sev 2] When interpreting efforts provisions, watch for two elements used to justify a hierarchy against the evidence: the conceptual explanation (it's valid because many think so; words mean what people think; different words express different meanings) and the semantics explanation (intuition about reasonable meaning "moderate" and best meaning "excelling all others"). (8.114, 8.115, 8.116...; PDF p. 405)
- **R-8.123-english-hierarchy-implications** [sev 2] Don't look to English endeavours caselaw for drafting guidance: because the courts can't articulate the distinction, and endeavours provisions depend on their circumstances, caselaw can tell you nothing reliable about the hierarchy. (8.123, 8.124, 8.125...; PDF p. 408)
- **R-8.130-take-control** [sev 2] Choose reason and clarity over legalistic hair-splitting; don't defer to court-interpreted "tested" language, which was tested because it was confusing. (8.130, 8.131, 8.132; PDF p. 409)
- **R-8.133-precise-over-vague** [sev 2] Use efforts provisions only if the party lacks complete control over achieving the goal; be cautious about using them as an expedient substitute for being specific. (8.133; PDF p. 410)
  - Test: Is achieving the goal entirely within the obligor's control? If so, state an unqualified obligation.
- **R-8.134-only-reasonable-efforts** [sev 1] Use only reasonable efforts, and stick with efforts rather than something more colloquial such as shall try. (8.134, 8.135; PDF p. 410)
  - Fix: Change to reasonable efforts.
- **R-8.136-add-specific-obligations** [sev 2] To reduce vagueness, supplement a reasonable efforts obligation with unqualified obligations for related tasks within the party's control (for example, require Acme to apply for the permit by a specified date). (8.136, 7.53; PDF p. 373)
  - Look for: reasonable efforts to obtain something with no specific steps or deadlines
- **R-8.137-explain-when-balked** [sev 3] If the other side balks at reasonable efforts, explain that the notion that best efforts is more onerous doesn't make sense, and that caselaw doesn't support it (U.S.) or is confused (England, Canada). (8.137; PDF p. 411)
- **R-8.138-no-best-efforts-gamesmanship** [sev 2] Don't use best efforts against an other side unaware of U.S. caselaw in the hope it will exert itself more; seek a meeting of the minds instead. (8.138; PDF p. 411)
- **R-8.139-measuring-standard** [sev 2] Always incorporate in a reasonable efforts obligation a standard for measuring performance (how many, how quickly, how soon); a vague one such as promptly suffices. (8.139, 8.140, 8.141...; PDF p. 411)
  - Look for: efforts obligation with no goal, quantity, or timing
  - Test: Ask: against what goal or deadline would a court measure whether the efforts were enough?
  - Exceptions: Some courts (New York, per TPTCC NY v. Radiation Therapy Services, S.D.N.Y. 2011) expect unrealistic detail; drafters can't be expected to offer much in the way of guidelines (8.143).
- **R-8.144-benchmarks** [sev 2] Instead of creating a new standard, consider referring to a benchmark courts have used: past performance, promises in negotiations, industry practice, the promisor's efforts under similar contracts, or how the promisor would act if promisor and promisee were one entity. (8.144, 8.145; PDF p. 412)
- **R-8.146-efforts-and-other-provisions** [sev 2] Consider how other provisions affect the performance an efforts provision requires: a right to terminate for missed sales targets may lead a court to treat the targets as minimum acceptable performance, but keep the reasonable efforts obligation, which preserves a breach claim and a basis to terminate without waiting for a missed target. (8.146, 8.147, 8.148; PDF p. 414)
- **R-8.152-no-to-extent-possible** [sev 3] Delete to the extent possible and similar phrases from an efforts provision; an efforts provision already implies the party might be unable to comply. (8.152; PDF p. 415)
  - Book example: Acme shall use reasonable efforts to cancel or mitigate, to the extent possible, each obligation that would cause Acme to incur expenses ... → Acme shall use reasonable efforts to cancel or mitigate each obligation that would cause Acme to incur expenses ...
- **R-8.153-no-mixed-standards** [sev 2] Don't refer to good faith or diligence in a reasonable efforts provision, and don't place any other modifier after efforts. (8.153; PDF p. 415)
  - Book example: Each party shall use reasonable efforts, undertaken diligently and in good faith, to obtain all Consents before Closing. → Each party shall use reasonable efforts to obtain all Consents before Closing.
- **R-8.154-one-efforts-standard** [sev 1] Don't use more than one efforts standard in a contract; harmonize a template's standards if necessary. (8.154; PDF p. 416)
  - Test: Search for every efforts standard; all should be the same phrase.
- **R-8.155-define-reasonable-efforts** [sev 2] Consider making Reasonable Efforts a defined term, stating its core meaning and anything excluded: "Reasonable Efforts" means, regarding conduct by a party, the efforts that a reasonable person in the position of that party would use to engage in that conduct competently and promptly. (8.155, 8.156; PDF p. 416)
- **R-8.157-definition-all-contexts** [sev 2] Make the Reasonable Efforts definition work in every context it appears (obligations, conditions, statements of fact); state expectations about maintaining a status or stopping something in the provision itself; otherwise customize the core definition. (8.157, 8.158, 8.159; PDF p. 416)
- **R-8.160-no-actions-in-definition** [sev 2] Don't use a Reasonable Efforts definition that lists actions a party must take; state any absolute requirement as a freestanding obligation. (8.160, 8.161; PDF p. 417)
  - Book example: "Reasonable Efforts" means, among other things, that the Company shall submit to the SEC, within two business days after ... a request for acceleration of effectiveness ... → (see fix)
- **R-8.162-efforts-carve-outs** [sev 2] Limit extreme interpretations with specific carve-outs from reasonable efforts (for example, incurring expenses over stated amounts, incurring liabilities, changing business strategy, disposing of significant assets, violating law, imperiling existence or solvency, initiating litigation), using a clearer device than the traditional proviso. (8.162, 8.163, 8.164...; PDF p. 417)
- **R-8.168-belt-and-braces-carveouts** [sev 3] Some common carve-outs (for example, actions that would result in a material adverse change in that party) likely fall outside reasonable efforts anyway, but a party may include them to make doubly sure. (8.168; PDF p. 419)
- **R-8.169-add-ins** [sev 2] If you intend compliance to require more than reasonable conduct, say so in the definition or provision (for example, acknowledging that the money and personnel a reasonable person would devote are unlimited); expect few to accept it. (8.169, 8.170; PDF p. 419)
  - Book example: (none) → Acme acknowledges that the money that a reasonable person in Acme's position would be willing to expend on, and the personnel ... devote to, complying with its obligations under this section 11 are unlimited.
- **R-8.172-clean-negotiation-record** [sev 1] Don't tolerate anything in the contract or negotiation record suggesting you accept a hierarchy of efforts standards; an unsophisticated court might find it meaningful. (8.172, 8.173, 8.174...; PDF p. 421)
- **R-8.176-record-best-efforts-concession** [sev 1] If you agree to best efforts to get the deal done, put on the record that you don't accept that it requires more than reasonable performance; if you agree to change best efforts to reasonable efforts, put on the record that you do so as a matter of clear drafting, not because it changes meaning. (8.176; PDF p. 421)

### Chapter 9: Material

- **R-9.1-material-usage** [sev 2] Drafters use material and materially (modifying adjectives and verbs) to narrow a broad provision to what matters; material also appears in material adverse change (MAC) and material adverse effect (MAE). (9.1, 9.2, 9.4; PDF p. 423)
- **R-9.3-material-ambiguous** [sev 1] Treat material as ambiguous as well as vague: it can mean "nontrivial" (worth a reasonable person's attention) or "dealbreaker" (enough to affect whether a reasonable person would do the deal), and caselaw hasn't addressed that. (9.3, 9.20, 9.21...; PDF p. 423)
  - Test: For each use, ask whether a reasonable reader could read it as nontrivial or as dealbreaker, and which the client needs.
  - Fix: Replace with nontrivial (or trivial) or dealbreaker, or use Material as a defined term (9.51-.64).
  - Book example: SFDC will not materially decrease the overall security of the Services ... → SFDC will not decrease more than trivially the overall security of the Services.
- **R-9.5-common-law-material-breach** [sev 1] Don't assume every contract use of material breach means common-law material breach (nonperformance that goes to the root of the contract); because material is ambiguous, say which meaning you intend. (9.5, 9.6; PDF p. 424)
- **R-9.7-tsc-materiality** [sev 2] Under TSC Industries v. Northway (U.S. 1976), an omitted fact is material if there is a substantial likelihood a reasonable shareholder would consider it important in deciding how to vote; courts apply this to disclosure generally and to contracts (Frontier Oil v. Holly, Del. Ch. 2005). (9.7, 9.8; PDF p. 425)
- **R-9.9-ibp-mae** [sev 2] Under IBP v. Tyson Foods (Del. Ch. 2001), a MAE closing condition protects the acquirer from unknown events that substantially threaten the target's overall earnings potential in a durationally significant manner; a buyer must make a "strong showing" (a "heavy burden," Snow Phipps, Del. Ch. 2021) to invoke it. (9.9, 9.10, 9.11; PDF p. 426)
- **R-9.12-akorn-all-material-respects** [sev 2] Under Akorn v. Fresenius Kabi (Del. Ch. 2018), in all material respects excludes "small, de minimis, and nitpicky issues" and sets a standard less onerous than common-law material breach, limited to issues significant in the context of the contract. (9.12, 9.13, 9.14...; PDF p. 426)
- **R-9.17-caselaw-unpromising** [sev 3] Don't look to caselaw for clear drafting of materiality: courts resolve disputes over dysfunctional language, and caselaw on materiality is patchwork from unrelated contexts. (9.17, 9.18, 9.19; PDF p. 428)
- **R-9.22-significant-ambiguous** [sev 1] Don't use significant to express a materiality threshold; it is ambiguous between "worthy of attention" and the weakened sense "noticeable" (in effect, not insignificant). Use nontrivial instead. (9.22, 9.28; PDF p. 429)
  - Fix: Use nontrivial (or trivial), or dealbreaker.
- **R-9.23-free-floating-vagueness** [sev 2] Don't use words of importance that show "free-floating vagueness" (minor, significant, important, substantial, essential, major) to set thresholds, and don't build a hierarchy of levels from them. (9.23, 9.24, 9.25...; PDF p. 429)
- **R-9.27-inflection-point-vagueness** [sev 2] Use "inflection-point vagueness," tying importance to a change in incentives. The first inflection point is nontrivial: something a reasonable person in the party's position would pay attention to, equating with TSC Industries and Akorn's exclusion of small, de minimis, and nitpicky issues. (9.27, 9.29; PDF p. 430)
- **R-9.30-dealbreaker-meaning** [sev 2] The second inflection point is dealbreaker: the deal depends on it, equating with common-law material breach and IBP's strong showing. Delaware applies the dealbreaker meaning to MAC, but semantics gives no basis to confine it there. (9.30, 9.31, 9.32; PDF p. 430)
- **R-9.33-location-suggests-meaning** [sev 1] To gauge what material probably means in a provision, consider what is at stake: in provisions about the economic bargain (statements of fact, obligations) it sensibly means nontrivial; in provisions that let a party call off the deal (closing conditions, termination for material breach) a committed party would want it to mean dealbreaker. (9.33, 9.34, 9.35...; PDF p. 431)
  - Book example: Alpha is not in material breach of any Gamma Contract. → (see fix)
- **R-9.46-materially-not-all-respects** [sev 3] Use materially, not in all material respects, as the adverbial form of material: is materially accurate, not is accurate in all material respects. (9.46, 9.47, 9.48...; PDF p. 434)
  - Book example: is accurate in all material respects → is materially accurate
  - Book example: is in all material respects in compliance with → is materially in compliance with
- **R-9.51-omit-material** [sev 1] Omit material from contracts; express its two meanings with nontrivial (and trivial) and dealbreaker, or use Material as a defined term for the dealbreaker meaning. (9.51, 9.64; PDF p. 435)
- **R-9.52-use-nontrivial** [sev 2] Use nontrivial for the lower threshold; no nontrivial is a legitimate double negative, equal to the two positive forms (only trivial litigation, or no litigation). (9.52, 9.53, 9.54...; PDF p. 435)
  - Book example: There is no material litigation pending against the Company. → There is no nontrivial litigation pending against the Company.
- **R-9.57-use-dealbreaker** [sev 2] Consider dealbreaker for the higher threshold; it needn't be a defined term. It has no negative form, so use it in a negative structure (not dealbreaker inaccurate). (9.57, 9.58, 9.59; PDF p. 436)
  - Book example: were materially accurate on the date of this agreement and are materially accurate at Closing → were not dealbreaker inaccurate on the date of this agreement and are not dealbreaker inaccurate at Closing
- **R-9.60-material-defined-with-mac** [sev 2] If the contract uses MAC, use Material as a defined term rather than dealbreaker, for consistency. (9.60; PDF p. 437)
- **R-9.61-material-definition** [sev 2] If you keep material, define it for the dealbreaker standard, referring to both entry and consummation: "Material" and "Materially" refer to a [dealbreaker] level of significance that would have affected the decision of a reasonable person in the Buyer's position regarding whether to enter into this agreement or would affect [that] decision regarding whether to consummate the transaction. If more than one party is subject to materiality standards, define it "regarding a given Person." (9.61, 9.62, 9.63; PDF p. 437)
- **R-9.65-which-noun** [sev 1] When a statement of fact has two nouns materiality could modify, modify the noun that is the focus of the statement of fact. (9.65, 9.66; PDF p. 439)
  - Book example: The Seller is not in default under any nontrivial contract to which it is party. → The Seller is not in nontrivial default under any contract to which it is party.

### Chapter 9: Material Adverse Change

- **R-9.67-mac-overview** [sev 3] MAC issues fall into using MAC provisions and defining MAC. MAC is entrenched, so MSCD assumes it rather than Dealbreaker Adverse Effect; where the nontrivial meaning suits, you can use nontrivial adverse effect. (9.67, 9.68; PDF p. 439)
- **R-9.69-absolute-mac** [sev 2] An "absolute MAC provision" states that no MAC has occurred since a date (Since 31 December 2021, no MAC has occurred). A court should aggregate events even without individually or in the aggregate (as in IBP). (9.69, 9.70, 9.71; PDF p. 440)
- **R-9.72-modifying-mac** [sev 2] A "modifying MAC provision" qualifies a statement of fact about some aspect of operations (contain no inaccuracies except for inaccuracies that would not reasonably be expected to result in a MAC); a mass noun or plural count noun makes individually or in the aggregate unnecessary. (9.72; PDF p. 441)
- **R-9.73-no-repeat-as-conditions** [sev 3] Don't repeat MAC statements of fact as closing conditions; the standard bringdown condition already covers them. (9.73; PDF p. 441)
- **R-9.74-mac-as-statement-of-fact** [sev 2] Draft a MAC provision as a statement of fact rather than a condition: a condition only lets a party walk, while an inaccurate statement of fact can also support a damages or indemnification claim. (9.74, 9.75; PDF p. 441)
- **R-9.76-mac-vs-material** [sev 2] As an alternative to a modifying MAC provision, use dealbreaker or defined Material (contains no Material inaccuracies); nontrivial is unlikely to fit. Use MAC where the concern is an adverse effect on the other party's fortunes, and Material where the concern is a direct effect on your client. (9.76, 9.77; PDF p. 442)
  - Exceptions: Not every Material provision can become a MAC provision; a static noun such as contract can't express change (9.77).
- **R-9.78-bringdown-materially** [sev 2] In a materiality-qualified bringdown condition, use Materially accurate (as a defined term) rather than accurate in all material respects: that individually and in the aggregate, the statements of fact made by the Seller in article 2 were Materially accurate on the date of this agreement and are Materially accurate at Closing. If both sides' bringdowns use materiality, state whose perspective applies. (9.78, 9.79, 9.80; PDF p. 443)
- **R-9.81-individually-and-aggregate** [sev 1] Use individually and in the aggregate in the bringdown to capture the cumulative effect of inaccuracies (it benefits the buyer); if you omit it, refer to each statement of fact, making clear the cumulative effect doesn't count. (9.81, 9.82; PDF p. 444)
- **R-9.83-mac-bringdown-semantics** [sev 2] In a MAC-qualified bringdown, don't say a failure to be true and correct would not reasonably be expected to have a MAC; an inaccuracy doesn't cause a MAC, the circumstances behind it might. Say: except for any statements of fact that are inaccurate such that the events or circumstances giving rise to those inaccuracies have not had and would not reasonably be expected to have a Material Adverse Effect. (9.83, 9.84, 9.85...; PDF p. 444)
- **R-9.87-bringdown-carveouts** [sev 3] Carve statements of fact (such as capitalization) out of the bringdown materiality qualification only if they have no materiality qualification of their own, and recognize the carve-out may accomplish little. (9.87; PDF p. 445)
- **R-9.88-no-double-materiality** [sev 2] Don't contort drafting to neutralize "double materiality" (stripping statement-of-fact qualifiers for bringdown purposes, or applying the bringdown qualifier only to unqualified statements); it is an illusion if the bringdown uses the dealbreaker standard, because both provisions then look to the same external standard. (9.88, 9.89, 9.90...; PDF p. 446)
- **R-9.97-double-materiality-provision** [sev 3] Optionally, state that double materiality doesn't apply: the level of inaccuracy permitted by the bringdown's materiality qualification will not be affected by a materiality qualification to which a statement of fact is subject. (9.97; PDF p. 448)
- **R-9.98-mac-verb** [sev 1] In MAC provisions, use would [or would not] reasonably be expected to result in a MAC; don't use will (inaccurate only if a MAC materializes or becomes certain), could (any remote path makes it inaccurate), could reasonably be expected, or would result. (9.98, 9.99, 9.100...; PDF p. 448)
- **R-9.102-absolute-mac-graft** [sev 2] In an absolute MAC provision use the present perfect (no MAC has occurred), and for the party with the benefit, graft on a modifying provision: Since [date], there has not occurred any MAC or any events or circumstances that would reasonably be expected to result in a MAC. (9.102; PDF p. 449)
- **R-9.103-mac-not-mae** [sev 2] Use one defined term, and make it Material Adverse Change; don't use both MAC and MAE. (9.103, 9.104, 9.105...; PDF p. 450)
- **R-9.112-baseline-date** [sev 1] Specify a baseline date in an absolute MAC statement of fact (signing date; date of the latest audited or unaudited financial statements, the buyer generally preferring audited; date of formation; a lender's commitment date). (9.112; PDF p. 452)
  - Look for: absolute MAC statement with no "since [date]"
- **R-9.113-mac-defined-spelled-out** [sev 3] Use Material Adverse Change as a defined term, spelled out rather than abbreviated. (9.113; PDF p. 452)
- **R-9.114-mac-basic-definition** [sev 2] Use a basic MAC definition such as: "Material Adverse Change" means any Material adverse change in the business, results of operations, assets, liabilities, or financial condition of the Seller, as determined from the perspective of a reasonable person in the Buyer's position. (9.114, 9.115; PDF p. 453)
- **R-9.116-change-not-expectation** [sev 2] Define MAC as a material adverse change in something, not as an event or circumstance that would reasonably be expected to result in one, nor both; put the would reasonably be expected formula in the MAC provisions instead. (9.116, 9.117, 9.118...; PDF p. 453)
- **R-9.121-no-extra-nouns** [sev 3] Say any material adverse change in ..., not any change, effect, development, or circumstance materially adverse to ...; the extra nouns are superfluous. (9.121; PDF p. 454)
- **R-9.122-mac-perspective** [sev 1] State whose perspective determines materiality in the MAC definition (from the perspective of the Buyer, or of a reasonable person in the Buyer's position). (9.122, 9.123, 9.124; PDF p. 454)
- **R-9.125-no-quantitative-thresholds** [sev 2] Generally don't add quantitative thresholds to a MAC definition: indicia are many and partial coverage is arbitrary, they complicate negotiation, illustrative indicia risk a court rejecting dissimilar changes, and quantifiable concerns belong elsewhere. (9.125, 9.126, 9.127...; PDF p. 455)
  - Exceptions: An aggressive buyer or one with ample bargaining power might want favorable thresholds (9.130).
- **R-9.131-field-of-change** [sev 2] For a buyer acquiring a company, define the "field of change" as the business, results of operations, assets, liabilities, or financial condition of the target, adjusted to the transaction (for example, the assets acquired in an asset purchase; in credit agreements, effects on lender rights or the borrower's ability to perform). (9.131, 9.132; PDF p. 456)
- **R-9.133-liabilities-broad** [sev 2] Read liabilities in the field of change in its broad sense (any legal responsibility); if the contract defines Liabilities broadly elsewhere, use that defined term. (9.133; PDF p. 457)
- **R-9.134-new-line-of-business** [sev 2] To cover a target's planned new line of business, refer in the field of change to the business as it is currently being conducted or as the target currently proposes to conduct it, or, if plans are sufficiently developed, add specific statements of fact or conditions about the expansion. (9.134, 9.149; PDF p. 457)
- **R-9.135-field-surplusage** [sev 2] Omit properties (overlaps assets), operations (within business), and capitalization (ambiguous between share structure and market value) from the field of change, and use financial condition rather than condition (financial or otherwise). Don't assume stock-price changes fall within a field that excludes capitalization; address them explicitly. (9.135, 9.136; PDF p. 457)
- **R-9.137-keep-beyond-business** [sev 2] Keep elements beyond business in the field of change despite arguable surplusage; some courts read a business-only field narrowly. (9.137; PDF p. 458)
- **R-9.138-say-so-industry-changes** [sev 1] If a party wants to walk when specific industry-wide or general developments cause a MAC, say so in the contract, preferably in a statement of fact, condition, or other provision rather than as including examples in the MAC definition. (9.138, 9.139, 9.140; PDF p. 458)
- **R-9.141-omit-prospects** [sev 2] Omit prospects from the field of change and use the "back door" instead: consistently use would [or would not] reasonably be expected to result in a MAC in modifying provisions, and add or any event or circumstance that would reasonably be expected to result in a MAC to absolute provisions. (9.141, 9.142, 9.143...; PDF p. 459)
- **R-9.148-projections-condition** [sev 2] A buyer wanting certainty about publicly announced projections should make it a closing condition that no event or circumstance exists that is reasonably expected to result in the target failing to meet any publicly announced financial projections, rather than rely on Pacheco. (9.148; PDF p. 461)
- **R-9.150-specific-concerns-elsewhere** [sev 1] Address specific concerns (matters that might fall within prospects, partly controlled or uncontrolled changes, and any issue that might support a claim or a right to walk) in statements of fact, conditions, or termination provisions, stated as broadly as possible, so the absolute MAC provision is needed only for matters unforeseeable at signing. (9.150, 9.163, 9.171; PDF p. 462)
- **R-9.151-whose-mac** [sev 1] Say whose MAC (of the Seller; or the Seller and its Subsidiaries, taken as a whole). When both sides benefit from MAC provisions, give each its own defined term (Buyer MAC, Seller MAC), use the multi-party Material definition, and don't use a MAC definition that applies to one party in a provision applying to another. (9.151, 9.152, 9.154...; PDF p. 462)
- **R-9.153-target-mac-protection** [sev 3] A target normally forgoes MAC protection when paid in cash; when paid in buyer stock, whether to seek it depends on the exchange ratio and other mechanisms addressing major changes in the buyer's business. (9.153; PDF p. 462)
- **R-9.159-no-aggregation-in-definition** [sev 2] Don't build aggregation into the MAC definition (when considered individually or together with each other such adverse change); it makes little sense for modifying provisions. Use the expanded absolute MAC provision for broad aggregation. (9.159, 9.160, 9.161...; PDF p. 463)
- **R-9.163-no-including-examples** [sev 1] Don't specify changes the buyer wants to walk over as including examples in the MAC definition; state their nonoccurrence in statements of fact, closing conditions, or termination provisions. (9.163; PDF p. 464)
- **R-9.164-mac-carve-outs** [sev 2] Word MAC carve-outs generally, not as historical facts, and introduce them with other than [or except for, or but does not include] any of the following, either alone or in combination. Common carve-outs: general economic conditions; industry-wide changes (perhaps unless disproportionate); announcement of the transaction; stock price or trading volume; labor disruptions; failure to meet estimates; actions contemplated by the agreement or requested by the buyer; actions required by law. (9.164, 9.165; PDF p. 465)
- **R-9.166-carve-out-negotiation** [sev 3] Target counsel should weigh bargaining power, the nature of the business (carve-outs are associated with technology deals), and deal practice; a restrained seller position carves out economy-wide and industry changes and changes attributable to the deal. Omitting a carve-out doesn't mean a court would find a MAC. (9.166, 9.167; PDF p. 466)
- **R-9.168-mac-other-provisions** [sev 1] Recognize that other provisions can limit a MAC: a narrower specific provision may control (Gordon v. Dolin, Ill. App. Ct. 1982), and silence on a topic can suggest it wasn't material (Northern Heel v. Compo, 1st Cir. 1988). (9.168, 9.169, 9.170; PDF p. 467)

### Chapter 10: References to Time

- **R-10.29-day-insufficiently-specific** [sev 1] Recognize that fixing a point in time by reference to a day is insufficiently specific: a beginning or ending point could fall at the midnight starting or ending the day, and a party might claim it had some other time in mind. (10.29, 10.30, 10.31...; PDF p. 474)
  - HOUSE: House addition: A no later than [date] deadline that decides a right (exercising an option, curing a breach, terminating, giving a notice that starts or ends a right) always states a time of day and a time zone: no later than 5:00 p.m. Eastern time on June 30, 2027 (Blake's decision; MSCD 10.33-10.34). See house-style.md section 7.
  - Look for: deadline or period stated by day with no time of day
  - Test: Ask at what moment on the day the period begins or ends.
  - Fix: State a time of day (10.33); or say from the beginning of 15 April 2023 to the end of 30 April 2023 (which could be read as business hours); or state inclusive or exclusive expressly (legalistic); or add a comprehensive interpretation section.
- **R-10.114-promptly-equals-immediately** [sev 2] Treat promptly and immediately (and prompt and immediate) as meaning the same thing in contracts: courts apply a reasonableness standard to both. (10.114, 10.115, 10.116...; PDF p. 493)
  - Exceptions: Immediately also means "without intermediary" (the immediately preceding Business Day); that use is not a speed standard (10.119).
- **R-10.118-no-as-promptly-as-possible** [sev 3] Don't say as promptly as possible [or practicable]; promptly already depends on the circumstances. (10.118; PDF p. 494)
- **R-10.129-omit-immediately** [sev 2] Omit immediately and use promptly; don't use both promptly and immediately in one contract. (10.129; PDF p. 497)
- **R-10.130-no-promptly-synonyms** [sev 2] Don't use synonyms of promptly (quickly, as soon as practicable, expeditiously, forthwith, right away) or without undue delay. (10.130; PDF p. 497)
  - Fix: Use promptly, or a precise deadline.
  - Exceptions: Under German law, without undue delay may be appropriate as the English equivalent of unverzüglich (10.130).
- **R-10.131-precise-deadline** [sev 2] If you can state a precise deadline, do so; if promptly may not convey enough urgency, use a precise deadline (no later than 60 minutes after learning of that event) or combine vague and absolute limits (promptly, but not later than x days after). (10.131; PDF p. 497)
  - Book example: (none) → promptly, but not later than x days after ...
- **R-10.141-at-all-times** [sev 2] Don't use at all times: an ongoing obligation applies at all times without saying so; if a provision could be read as applying only at one moment, use always; for a statement of fact, state a time period (since 1 January 2022). (10.141, 10.142, 10.143...; PDF p. 499)
- **R-10.147-no-periodically** [sev 2] Don't use periodically; be specific (state intervals, or whenever the client asks); to express that something changes over time, use then (the Agent's loan procedures then in effect). (10.147, 10.148, 10.149...; PDF p. 500)
  - Book example: the Agent's loan procedures periodically in effect → the Agent's loan procedures then in effect

### Chapter 13: Selected Usages

- **R-13.5-actively-levels** [sev 2] If you use actively to distinguish levels of activity (as in while actively employed, to exclude an employee on leave), instead state the distinction explicitly. (13.5; PDF p. 577)
  - Fix: Say explicitly what status counts, for example whether an employee on leave qualifies.
- **R-13.28-annual-meeting** [sev 2] Be specific about what qualifies as the annual meeting for a given year; for example, say that a meeting qualifies if it is held anytime in that year. (13.28, 13.29; PDF p. 582)
  - Fix: State which meeting counts as the annual meeting for each year.
- **R-13.41-arising-out-of-or-relating-to** [sev 2] Don't rely on arising out of or relating to to set the scope of dispute-resolution, liability-limitation, or release provisions; it combines two nonspecific standards. To bring in a broad but predictable set of claims, refer to the contract and to the activities the parties will engage in as part of the transaction, and drop or relating to. (13.41, 13.45, 13.47...; PDF p. 586)
  - Fix: any dispute arising out of this agreement or [named transaction activities]
- **R-13.48-subject-matter-of-this-agreement** [sev 2] Say what the subject matter is rather than arising out of the subject matter of this agreement; that phrase trades one nonspecificity for another and has generated litigation. (13.48, 13.49; PDF p. 588)
  - Fix: Name the activities (for example, ownership of any Interest, or management or operations of Company).
  - Book example: any action or proceeding brought to enforce any provision of this Agreement → any dispute arising out of this agreement, ownership of any Interest, or management or operations of the Company
- **R-13.101-because** [sev 2] Whenever you use because in a contract (typically in a conditional clause, If X because of Y, then Z), consider being specific about the type of causation required, such as sole cause or but-for cause. (13.101, 13.103; PDF p. 602)
  - Test: Must Y be the sole cause or only one of several causes? If the provision doesn't say, it invites dispute.
  - Fix: State the causation standard (solely because of; but for).
- **R-13.112-accounting-records** [sev 2] To capture the narrower accounting meaning, use accounting records (the UK Companies Act 2006 term) or financial records; a narrower term may spare a party a surprise when the other side asks to audit many kinds of records. (13.112, 13.113; PDF p. 604)
  - Look for: audit or inspection right over records
  - Fix: accounting records / financial records
- **R-13.215-potential-default** [sev 3] In the paired defined terms Default (a latent event of default) and Event of Default, use Potential Default and Default instead; the traditional pair look the same and don't signal their definitions. Don't use Incipient Event of Default. (13.215, 13.219, 13.220...; PDF p. 626)
  - Fix: Potential Default; Default
- **R-13.271-etc** [sev 2] Delete etc.; it is casual, and either redundant (after examples) or hazardous because the provision's reach is uncertain. Ideally, specify a class and nothing else or make the list exhaustive; if neither is possible, use including. (13.271, 13.272, 13.273...; PDF p. 637)
  - Fix: Name the class; make the list exhaustive; or use including
- **R-13.287-faithfully** [sev 2] Don't use faithfully and comparable adverbs (diligently, competently, industriously) to state an employee's standard of performance; be specific about the employee's duties. (13.287, 13.288, 13.290...; PDF p. 641)
  - Fix: State the employee's duties and any measurable targets.
- **R-13.320-fraud-intentional-misrepresentation** [sev 2] In exceptions to indemnification limits, referring to both fraud and intentional misrepresentation is safer than fraud alone, because the elements differ and a court might treat fraud as a distinct claim. Clearer still, avoid the terms of art and describe the conduct. (13.320, 13.323, 13.324...; PDF p. 649)
  - Fix: any claim that the Indemnifying Party intentionally supplied 1 or more Indemnified Parties with information that the Indemnifying Party knew [or, after reasonable inquiry, would have known] was inaccurate or any claim that the Indemnifying Party intentionally withheld information from 1 or more Indemnified Parties
- **R-13.330-full-time** [sev 2] Be more specific than full-time when referring to work: state the minimum hours per day and days per week, how long that level must be maintained, and whether the person must be employed (and whether volunteer or independent-contractor work counts). (13.330, 13.331, 13.332; PDF p. 651)
  - Fix: State minimum hours and days, duration, and what kinds of work count.
- **R-13.346-absolute-unconditional-guarantee** [sev 2] Omit absolutely, unconditionally, irrevocably, and the adjectives absolute, continuing, irrevocable, and unconditional from guarantees; be specific about the deal terms instead. They are unclear terms of art, add words, don't prevail over the law (a guarantor may revoke as to future advances), and don't prevail over the deal terms. (13.346, 13.347, 13.348...; PDF p. 654)
  - Fix: Delete the adverbs and adjectives; state the deal terms specifically.
  - Exceptions: A guarantee is irrevocable unless you say otherwise, subject to the law's limit on revocation as to future advances (13.348-13.349).
- **R-13.448-losses-and-liabilities** [sev 2] Address directly whether indemnification covers only losses paid or also liabilities incurred: have the indemnifying party indemnify against both losses and liabilities, or better, use a defined term (Indemnifiable Losses or a variant) that states exactly what is covered, for example including judgments so the indemnified party needn't pay a judgment first; address litigation expenses in the procedure provisions. (13.448, 13.449, 13.450; PDF p. 678)
  - Look for: indemnification provision that relies on hold harmless to cover incurred liabilities
  - Fix: Define Indemnifiable Losses to state what is covered (including judgments).
- **R-13.452-defend** [sev 2] Don't rely on adding defend; address explicitly, in the indemnification procedure provisions, how defense of nonparty claims is handled. (13.452; PDF p. 679)
  - Fix: Procedures stating who controls the defense, counsel, expenses, and settlement.
- **R-13.500-knowledge-qualifier** [sev 2] Consider a knowledge qualification in a statement of fact if the party can't determine whether the statement is accurate, usually because the matters might be hidden (contamination) or under others' control (threatened litigation). It means the party claims only that it isn't aware of anything suggesting inaccuracy; who bears unknown risk is a risk-allocation question. (13.500, 13.501, 13.502...; PDF p. 691)
  - Fix: To Seller's knowledge, ...
- **R-13.506-define-knowledge** [sev 2] Consider making Knowledge a defined term to address whose knowledge counts (narrow for the stating party, broad for the other) and the level of knowledge (actual knowledge, or knowledge after inquiry of specified employees or after reasonable investigation, using knows or should have known). In a sale of a business, consider whether to include its managers. Avoid reasonable knowledge as unclear. (13.506, 13.507, 13.508...; PDF p. 692)
  - HOUSE: partly superseded: Never should: define Knowledge with wording for actual knowledge and for knowledge after reasonable inquiry, not should have known. See house-style.md section 12.
  - Fix: Autonomous definition of Knowledge naming the individuals and the level of investigation.
- **R-13.521-likely** [sev 2] Be aware of the uncertain meaning of likely (more or less than 50%? synonymous with probable?); in some contexts you can't avoid it. You could state a percentage probability instead, though debating 49% versus 51% is often meaningless for contract provisions. (13.521, 13.522, 13.523...; PDF p. 697)
  - Fix: has a probability of greater than 50% of [result]
  - Book example: a physical or mental incapacity or disability that has rendered, or is likely to render, the Executive unable to perform → a physical or mental incapacity or disability that has rendered, or has a probability of greater than 50% of rendering, the Executive unable to perform
- **R-13.526-reasonably-likely** [sev 2] Don't say reasonably likely; it adds vagueness to a degree of probability, and reasonableness has nothing to do with likelihood. (13.526; PDF p. 698)
  - Fix: likely
- **R-13.557-moral-turpitude** [sev 2] Don't use moral turpitude; it is insufficiently specific (Black's: conduct contrary to justice, honesty, or morality), yet it is a fixture of cause definitions and loan-agreement statements. (13.557, 13.558, 13.559...; PDF p. 704)
  - Fix: Use plain criteria for a termination-for-crime provision (see R-13.571-termination-for-crime).
- **R-13.562-crime-provision-elements** [sev 2] When drafting a termination-for-crime provision, decide: what crime (crime is preferable to criminal offense; felony and misdemeanor aren't recognized everywhere and vary by state); involving what offense (labels such as dishonesty or fraud, or a crime related to the employee's employment); other criteria (carve-outs such as noncustodial penalties or DWI); at what stage (commission, arrest, indictment, charge, or conviction or plea); which jurisdiction (name one if terminology varies); and whether to combine kinds of crime or stages. (13.562, 13.563, 13.564...; PDF p. 705)
  - Fix: See R-13.571-termination-for-crime.
- **R-13.585-gross-negligence** [sev 2] Using negligence doesn't involve undue uncertainty. But unless you can research the tort law of each relevant jurisdiction, don't use gross negligence, a vague tort term of art with no settled meaning; for misconduct beyond negligence, use reckless, recklessly, or recklessness, and don't try to distinguish reckless from wanton conduct. (13.585, 13.586, 13.588...; PDF p. 711)
  - Fix: reckless / recklessly / recklessness
  - Exceptions: In jurisdictions that don't recognize degrees of negligence (Pennsylvania, for example), a negligence standard might apply (13.597, 13.601). | Courts in many jurisdictions hold advance releases of liability for gross negligence unenforceable (13.588).
- **R-13.604-tort-standards-governing-law** [sev 2] Adjust tort-based standards to the governing law; if it doesn't recognize U.S. concepts, don't insist on them. Don't define recklessness or any form of it; a definition adds verbiage without certainty. (13.604, 13.605; PDF p. 715)
  - Look for: definition of reckless or gross negligence; non-U.S. governing law
  - Fix: Delete the definition; adapt to the governing law.
- **R-13.606-tort-carve-out-cap** [sev 2] Consider not using tort-based standards for performance under the contract; the contract already gives a remedy for nonperformance. In particular, a recklessness or intentional-misconduct carve-out from an indemnification cap could undermine the cap if indemnification covers failure to comply with obligations; such a carve-out makes more sense for losses from relations with nonparties. (13.606; PDF p. 715)
  - Fix: Limit the carve-out to nonparty-related losses, or drop it.
- **R-13.676-personnel** [sev 2] Don't use personnel undefined: some read it as employees, others more broadly (even companies), which could lead to a dispute. If you mean employees, say employees; if you mean employees and other representatives, use the defined term Representative. (13.676, 13.677, 13.678...; PDF p. 733)
  - Fix: employees; Representatives
  - Exceptions: If the group includes more than employees and representatives, you could use a defined term Personnel, but consider whether you need such an unwieldy group (13.680).
- **R-13.683-prevailing-party** [sev 2] If you want to recover legal fees and other expenses, say so in the contract; in the U.S. they generally aren't recoverable otherwise. But prevailing party (or successful party) has spawned much litigation; specifying what determines prevailing (judgment or dismissal; substantially what was sought; net winner) each has tradeoffs, and the risks of setting rules in advance might outweigh the benefits. (13.683, 13.684, 13.685...; PDF p. 734)
  - Fix: State fee recovery expressly; decide deliberately whether to define prevailing.
  - Exceptions: In California, Cal. Civil Code s. 1717(b)(1) defines prevailing party for contract claims, and the definition can't be altered by contract (13.689).
- **R-13.712-reasonable-satisfaction** [sev 2] Where reasonable doesn't refer to the reasonableness of the thing modified, say what is meant: instead of to the reasonable satisfaction of Acme (or reasonably satisfactory to Acme), say to the satisfaction of Acme, determined from the perspective of a reasonable person in Acme's position. (13.712, 13.713, 13.714...; PDF p. 742)
  - Fix: to the satisfaction of Acme, determined from the perspective of a reasonable person in Acme's position
- **R-13.719-reasonableness-vs-good-faith** [sev 2] Generally prefer a reasonableness standard (objective) for a counterparty's conduct, for example reasonable efforts rather than good-faith efforts; a good-faith standard is subjective. (13.719, 13.720, 13.721; PDF p. 743)
  - Fix: reasonable / reasonably / appropriate
  - Exceptions: If your client is the one subject to the provision, you might prefer a good-faith standard (13.721).
- **R-13.749-rightfully** [sev 2] Consider replacing rightfully and rightful (and wrongfully, wrongful) with a clearer statement of the basis for entitlement; in the confidentiality exception (information the Licensee rightfully obtains), it is unclear whether the source owed no confidentiality duty, the recipient broke no law, or both. (13.749, 13.750, 13.751...; PDF p. 750)
  - Fix: State the basis (for example, from a Person that was not under a duty to keep that information confidential).
- **R-13.787-solicit** [sev 2] In no-solicit provisions, use solicit to be hired, not bare solicit (solicit them for what?) or solicit to employ (awkward); solicit employees to accept employment is clearest but wordy. (13.787, 13.788, 13.789...; PDF p. 759)
  - Fix: solicit [employees] to be hired
- **R-13.829-survival-statements** [sev 2] Instead of stating how long statements of fact survive, address time limits on indemnification claims directly and more broadly in a section entitled Time Limits; survival periods address only one basis of claims and don't limit claims for breach of obligations. (13.829, 13.830, 13.831; PDF p. 769)
  - Fix: A Time Limits section stating when indemnification claims may be brought.
- **R-13.848-termination-for-convenience** [sev 2] Leave termination for convenience in government contracts, where it refers to the government's right to terminate without breach. Elsewhere, convenience is wishy-washy and a litigator might argue it requires some burden; say Acme may terminate this agreement for any reason by giving the Vendor at least 30 days' prior notice. You may drop at any time, but don't drop both phrases. (13.848, 13.849, 13.850...; PDF p. 773)
  - Fix: may terminate this agreement for any reason by giving ... at least 30 days' prior notice
- **R-13.874-thing** [sev 2] Instead of any thing or all things, refer to the acts or pieces of property meant. (13.874; PDF p. 779)
  - Fix: Name the acts or property.
- **R-13.884-time-of-the-essence** [sev 2] Don't rely on time is of the essence (or of the essence); it is jargon, too general, silent on consequences, may have no legal effect, and courts have ignored it. Use a termination provision instead, supplemented if appropriate by an acknowledgment that breach of specified sections is material breach; for a drop-dead date, have the parties acknowledge that no time beyond that date will be required. (13.884, 13.885, 13.886...; PDF p. 781)
  - Fix: Termination provision; acknowledgment that breach of section x is material breach; drop-dead-date acknowledgment (13.895)
  - Exceptions: Termination for any tardiness might make sense in some contexts (13.892).
- **R-13.920-unless-context-requires** [sev 2] Eliminate unless the context otherwise requires (or requires otherwise); it adds uncertainty a litigator might exploit. If you want to deviate from an across-the-board convention, be specific. (13.920, 13.921; PDF p. 788)
  - Fix: Delete; state any specific deviation.
- **R-13.924-very** [sev 3] Very (like extremely and highly) is not a meaningful indication of magnitude in contracts; the reader can't tell where it falls between nothing and everything. (13.924; PDF p. 789)
  - Fix: Delete, or state the magnitude.
- **R-13.968-workmanlike** [sev 2] Unless you are referring to the implied warranty of workmanlike performance recognized in construction law, consider competent and competently instead of workmanlike, a dated, gender-specific term of art; better still, be specific about the work expected. (13.968, 13.969, 13.970...; PDF p. 800)
  - Fix: competent / competently; specific requirements
  - Exceptions: Keep it when referring to the implied warranty of workmanlike performance (13.969, 13.971).

### Chapter 15: Internal Rules of Interpretation

- **R-15.6-interpretation-unless-context** [sev 2] Don't open an internal rule of interpretation with Unless the context otherwise requires; it undercuts the certainty the provision is meant to offer. (15.6; PDF p. 821)
  - Fix: Delete the phrase.
