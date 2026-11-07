# Structure: front and back of the contract, layout, amendments, letter agreements, internal rules

Apply house style first: enumeration I., A., 1., (a), (i) with no only child; avoid cross-references and refer by heading; Schedule and Exhibit capitalized. MSCD's layout rules marked HOUSE below yield to it.

## Skeleton of an MSCD contract (with house style)

1. **Title**: the kind of contract, centered, in capitals, no article (2.2-2.12): *CONSULTING AGREEMENT*.
2. **Introductory clause**: *This consulting agreement is dated January 1, 2027, and is between ACME CORPORATION, a Tennessee corporation ("**Acme**"), and WIDGETCO, LLC, a Delaware limited liability company ("**Widgetco**").* (2.16-2.122; date form per house style; *between*, not *among*, 2.47-2.49).
3. **Recitals**, only if there's a back story: narrative sentences, no *WHEREAS*, no deal terms, *wants* (2.129-2.158).
4. **Lead-in**: *The parties agree as follows:*; after recitals, *The parties therefore agree as follows:* (2.159-2.164). No recital of consideration (2.165-2.217).
5. **Body**: articles (I.) when there are more than about 25 sections (4.7), sections (A.) with bold headings, subsections (1.), enumerated clauses ((a)), subclauses ((i)).
6. **Definitions**: an autonomous-definitions section for clear terms, on-site definitions for custom terms (6.86-6.98). Not first, and not in an attachment.
7. **Concluding clause** (optional): *The parties are signing this agreement on the date that the introductory clause states.* (5.3-5.15).
8. **Signature blocks**: 1 per party, entity name in capitals, *By:*, name and title (5.28-5.40).
9. **Schedules, then exhibits** (`attachments.md`).

> **Book examples are in MSCD5's style, not house style.** They may use lowercase *schedule*, *1 January 2024*, spelled-out numbers, 1.1 numbering, *the* before party names, or a passive that MSCD accepts. Restate any example in house style (`house-style.md`) before you put it in a contract or a comment. For the other side's drafts, the house rule is to flag everything, whatever a rule's "let-pass" or "style-only" label says.


## Contents of the rules list

- Introduction
- Chapter 1: Contract Language Should Be Accessible
- Chapter 1: Restrained in Attempting to Preempt Judicial Discretion
- Chapter 2: The Front of the Contract (opening)
- Chapter 2: The Title
- Chapter 2: The Introductory Clause
- Chapter 2: Recitals
- Chapter 2: The Lead-In
- Chapter 2: Body Heading; Cover Sheet, Table of Contents, Index
- Chapter 3: General Considerations
- Chapter 3: Expressing Conditions
- Chapter 3: Selecting Which Category
- Chapter 4: Layout
- Chapter 5: Back of the Contract
- Chapter 13: Selected Usages
- Chapter 15: Internal Rules of Interpretation
- Chapter 18: Amendments
- Chapter 19: Letter Agreements

## Rules (260, generated from `data/rules.jsonl`)

Format: id, severity (1 = ambiguity or meaning-changing; 2 = vagueness or dispute risk; 3 = style), the rule, and its MSCD paragraphs and PDF page. `HOUSE` marks a rule that Blake's house style changes: apply the house rule. For a rule's full record (test, fix, exceptions, verified book examples), run `python3 scripts/rules_query.py --id <id>`.


### Introduction

- **R-intro-clause-commonwealth** [sev 3] Dispense with the Commonwealth use of clause to refer to a numbered provision of a contract. (Introduction; PDF p. 41)

### Chapter 1: Contract Language Should Be Accessible

- **R-1.62-accessible** [sev 3] Make the contract accessible: use a sensible enumeration scheme, make blocks of text neither too long nor too short, arrange provisions sensibly, and use typography well. (1.62; PDF p. 73)

### Chapter 1: Restrained in Attempting to Preempt Judicial Discretion

- **R-1.68-restrain-preempting-courts** [sev 2] Be restrained in using the four techniques for preempting judicial discretion: stating that a judicial rule of interpretation doesn't apply; stating an internal rule of interpretation; stating how a court is to act; and stating that a particular standard applies. (1.68, 1.69; PDF p. 75)
- **R-1.70-dont-instruct-court** [sev 2] Don't tell a court how to act ('an exercise in impotence'). Instead, have the parties acknowledge that a particular outcome is appropriate or that they would want the court to interpret the contract in a specified way. (1.70; PDF p. 75)
  - Fix: The parties acknowledge that ... they would want the court to interpret this agreement as follows:
- **R-1.70-internal-rules** [sev 2] Don't rely on an internal rule of interpretation where the context suggests a different meaning; like judicial rules, internal rules are arbitrary, and a court is likely to ignore one that context contradicts. (1.70; PDF p. 75)
- **R-1.70-negating-judicial-rule** [sev 2] Expect a court to be less likely to accept a statement that a judicial rule of interpretation doesn't apply if the statement could be seen as interfering with the natural reading of the contract. (1.70; PDF p. 75)
- **R-1.70-standard-must-fit** [sev 2] Don't state that a legal standard applies unless it matches the facts; if it doesn't, a court might well hold the provision unenforceable. (1.70; PDF p. 75)

### Chapter 2: The Front of the Contract (opening)

- **R-2.1-parts-of-front** [sev 3] Recognize the front of a contract as the title, introductory clause, any recitals, and the lead-in; a longer contract might also have a cover sheet, table of contents, and index of definitions. (2.1; PDF p. 78)

### Chapter 2: The Title

- **R-2.2-title-format** [sev 3] Place the title at the top center of the first page in all capitals, and state simply the kind of contract, without a definite or indefinite article. (2.2; PDF p. 78)
- **R-2.3-title-one-perspective** [sev 3] Don't use a title that looks at the transaction from two perspectives; choose one (and omit the unnecessary of). (2.3; PDF p. 78)
- **R-2.4-informative-title** [sev 3] Make the title informative; don't use just AGREEMENT, or a bare PURCHASE AGREEMENT, if you can come up with something more specific. (2.4; PDF p. 78)
- **R-2.5-no-crammed-title** [sev 3] Don't cram several elements of the transaction into the title; consider a broader, conceptual title, perhaps reflecting the business goal. (2.5; PDF p. 78)
- **R-2.6-no-party-names-in-title** [sev 3] Don't include party names in the title. (2.6; PDF p. 78)
- **R-2.7-no-jargon-title** [sev 3] Don't use jargon in the title. (2.7; PDF p. 78)
- **R-2.8-standard-title** [sev 3] If you can give a contract a standard title, do so; contract drafting doesn't prize variety for its own sake. (2.8; PDF p. 78)
- **R-2.9-statutory-terminology** [sev 3] Don't feel bound to track statutory terminology such as plan of merger or plan of exchange in the title. (2.9, 2.10; PDF p. 78)
- **R-2.11-agreement-or-contract** [sev 3] Use agreement or contract in the title; contract is unobjectionable. (2.11, 2.12; PDF p. 78)
- **R-2.13-supplement-title** [sev 3] A company with many contracts of one kind might supplement the title, for example with information below the title or by frontloading. (2.13, 2.14; PDF p. 78)

### Chapter 2: The Introductory Clause

- **R-2.15-introductory-clause** [sev 3] After the title, include an introductory clause that states the type of contract, perhaps gives a date, and identifies the parties. (2.15; PDF p. 80)
- **R-2.16-know-all-men** [sev 3] Don't begin the introductory clause with know all men by these presents. (2.16; PDF p. 80)
- **R-2.17-single-paragraph** [sev 3] Format the introductory clause as a single paragraph; don't tabulate its elements with headings such as DATE and PARTIES. (2.17, 2.18; PDF p. 80)
- **R-2.19-begin-with-this** [sev 3] Begin the introductory clause with This plus the type of contract stated in the title, in all lowercase; thereafter refer to this agreement. (2.19, 2.20; PDF p. 80)
- **R-2.21-is-dated-is-between** [sev 3] Use is dated (if the clause contains a date) rather than is made, is entered into, or is made and entered into; and say is between. (2.21; PDF p. 80)
- **R-2.25-no-dated-signatures** [sev 3] If the parties sign on the same day or close to it, put a date in the introductory clause and don't provide for dated signatures. (2.24, 2.25, 2.26; PDF p. 83)
- **R-2.27-no-as-of-date** [sev 2] Don't make the introductory-clause date an as of date to reflect that a party signed on another date. (2.27; PDF p. 84)
- **R-2.28-dated-signatures** [sev 3] If the parties sign on different days and no one is inclined to ignore that, have them date their signatures (the date the last party signs is the contract date), and still state the date in the introductory clause, preferably inserted after signing manually or by e-signature software, with a placeholder rather than a blank. (2.28, 2.29, 2.30...; PDF p. 84)
- **R-2.31-fallback-options** [sev 2] If you won't add the signing date to the introductory clause, choose among four inconvenient fallbacks; if you use a reference date (dated for reference), don't rely on the date of this agreement for timing; say the date the parties entered into this agreement. (2.31, 2.32, 2.33...; PDF p. 85)
  - Fix: the date the parties entered into this agreement
- **R-2.37-no-performance-date** [sev 2] Don't use as the date of the contract a date that reflects timing of performance (earlier to capture past performance, later for delayed performance); use the date of the contract and address timing where it makes most sense. (2.37, 2.38, 2.39...; PDF p. 86)
  - Look for: an introductory-clause date earlier or later than signing; as of, effective date, dated for reference
- **R-2.43-precontract-performance** [sev 2] For precontract performance, describe the precontract circumstances in the recitals, address any payment in the payment provisions, state in the body that the contract governs the precontract performance, and use the date of the contract in the introductory clause. (2.43; PDF p. 87)
- **R-2.44-no-effective-date-start** [sev 2] Don't use effective date (defined or undefined) for when performance starts; consider start date or performance date. A contract is effective when all parties have signed it. (2.44; PDF p. 87)
  - Fix: start date; performance date
- **R-2.46-retroactive-effect** [sev 2] Avoid making a contract effective retroactively; retroactive effect can create problems in a series of transactions. (2.45, 2.46; PDF p. 87)
- **R-2.47-between** [sev 3] Say the contract is between the parties, however many there are; don't use among or by and between. (2.47, 2.48, 2.49; PDF p. 87)
- **R-2.50-full-names** [sev 2] Identify each individual party by full name and each entity party by its full registered name, including the entity designation (Inc., LLC, B.V., GmbH). (2.50; PDF p. 88)
  - Exceptions: If it would prevent confusion, also refer to any other name by which a party is or was known (2.50).
- **R-2.51-names-in-capitals** [sev 3] State party names in all capitals in the introductory clause. (2.51; PDF p. 88)
- **R-2.52-no-enumerated-parties** [sev 3] Don't enumerate the parties in the introductory clause. (2.52; PDF p. 88)
- **R-2.53-no-affiliates-in-party** [sev 1] Don't tack including its affiliates and direct and indirect subsidiaries (or similar) onto a party's description or defined-term parenthetical; affiliates aren't parties and wouldn't be bound. (2.53, 2.94; PDF p. 88)
  - Book example: (including its affiliates and subsidiaries, "Acme") → (see fix)
- **R-2.54-signature-block-reference** [sev 3] For a template used with little customization, you could refer to the other party named in the signature blocks below instead of naming it, but it's a nuisance for the reader. (2.54; PDF p. 88)
- **R-2.55-party-order** [sev 3] Where loose conventions govern the order of parties with defined roles, follow them (disclosing party before recipient; borrower before lender; seller before buyer). (2.55; PDF p. 89)
- **R-2.59-affiliate-benefit** [sev 2] Rather than relying on a parent's signing for nonparty group members, structure the transaction to give them the benefit of the contract while explicitly protecting the supplier or licensor (separate contracts, guarantor, agent, sublicensor, master agreement with statements of work, or written undertakings naming the supplier as third-party beneficiary). (2.56, 2.57, 2.58...; PDF p. 89)
- **R-2.60-limited-role** [sev 2] Highlight a party's limited role by inserting, before its name and between commas, and for purposes of only [specified provisions]; list that party last; and note the limited role in its signature block too. (2.60, 2.61, 2.62...; PDF p. 90)
  - Exceptions: Omitting the highlight might have no repercussions; the party's role is whatever the contract says (2.61). | A limited-role party is likely also bound by boilerplate (governing law, notices) whether or not listed (2.62).
- **R-2.67-jurisdiction-and-entity** [sev 3] After each entity party's name, state concisely its jurisdiction of organization and kind of entity. (2.67; PDF p. 91)
- **R-2.68-no-addresses** [sev 3] For a U.S. entity, don't include its address in the introductory clause; put addresses in the notices provision. Outside the U.S., include a registration number if it helps determine the party's history and status; a registered-office address is superfluous. (2.68, 2.69, 2.71...; PDF p. 91)
- **R-2.70-an-individual** [sev 3] After each individual party's name, state that he or she is an individual; don't use natural person. State after every party name what kind of legal person it is. (2.70; PDF p. 91)
- **R-2.74-administrative-capacity** [sev 2] If a party serves an administrative function or acts for others, say so; if a party serves two roles, refer to it twice, once in each capacity; don't emphasize that it acts only or solely in a capacity. (2.74, 2.75, 2.76; PDF p. 91)
  - Book example: (none) → ACME BANK, N.A., as collateral agent for the Secured Parties (in that capacity, the "Collateral Agent")
- **R-2.77-trust-party** [sev 2] Make the trustee, not the trust, the party, and have the trustee sign as trustee: not in her individual capacity but as trustee, in both the introductory clause and the signature block. (2.77, 2.78, 2.79; PDF p. 91)
  - Exceptions: Some trusts, notably Delaware statutory trusts, are legal entities that can contract (2.79).
- **R-2.80-division** [sev 2] If an unincorporated division will perform, say so in the recitals or the party description, but make the company the party and signatory; don't make the division a party or say the company is represented by the division. (2.80, 2.81; PDF p. 91)
  - Book example: (none) → ACME CORPORATION, a Delaware corporation acting through its Widgets division (that corporation, "Acme")
- **R-2.83-no-background-in-intro** [sev 3] Don't clutter the introductory clause with background information (relationships among parties, roles); put it in the recitals, or capture its essence with common-noun or collective defined terms. (2.82, 2.83, 2.84; PDF p. 91)
- **R-2.85-no-extraneous-assertions** [sev 3] Don't assert in the introductory clause that a party is represented by a duly authorized representative, that it is duly organized and validly existing, or that the agreement states the parties' binding agreement; address the first two in statements of fact if relevant, and omit the third. (2.85; PDF p. 91)
- **R-2.86-intend-legally-bound** [sev 3] Generally, don't state anywhere in the contract that the parties intend to be legally bound. (2.86, 2.87, 2.88...; PDF p. 91)

### Chapter 2: Recitals

- **R-2.130-recital-kinds** [sev 3] Use recitals only for background the parties regard as relevant: context recitals (circumstances leading up to the contract), purpose recitals (the parties' goals, succinctly and broadly), and simultaneous-transaction recitals. (2.129, 2.130, 2.131...; PDF p. 105)
- **R-2.132-no-deal-terms-in-recitals** [sev 2] Don't address deal terms or facts in any detail in the recitals; put them in the body. Courts typically look to recitals only for indications of intent. (2.132; PDF p. 105)
  - Look for: obligations, prices, or detailed facts in the recitals
- **R-2.134-dispense-with-recitals** [sev 3] If the transaction is straightforward and lacks any back story, dispense with recitals. (2.134; PDF p. 105)
- **R-2.135-no-desire-recital** [sev 3] Don't use the recital that the parties desire to enter into the agreement. (2.135; PDF p. 105)
- **R-2.137-no-witnesseth** [sev 3] Don't use WITNESSETH (or any variant) before the recitals. (2.136, 2.137, 2.138; PDF p. 107)
- **R-2.140-no-recitals-heading** [sev 3] Don't give the recitals a heading; don't use WHEREAS as one. RECITALS or BACKGROUND is better than those but still unneeded. (2.139, 2.140, 2.141; PDF p. 107)
- **R-2.142-no-recital-numbers** [sev 3] Don't number or letter the recitals. (2.142; PDF p. 107)
- **R-2.144-no-whereas** [sev 3] Write recitals as straightforward narrative prose in complete sentences and conventional paragraphs; don't begin each recital with WHEREAS or end it with a semicolon. (2.143, 2.144, 2.145; PDF p. 107)
- **R-2.146-wants** [sev 3] In purpose recitals, use wants; avoid desires to, wishes to, intends to, seeks to, would like to, is desirous of, and is agreeable to. (2.146, 2.147, 2.148...; PDF p. 109)
- **R-2.151-no-premature-reference** [sev 3] In a purpose recital, don't say the parties propose to act in accordance with or subject to the terms of this agreement, or that this agreement contemplates something; express a general intent not tied to the terms (and no broader than the body). In a context recital, don't say a party has agreed to do something subject to the terms of this agreement. (2.151, 2.152, 2.153; PDF p. 110)
- **R-2.154-no-incorporating-recitals** [sev 2] Don't incorporate the recitals by reference; keep substantive provisions out of the recitals and move any into the body. (2.154, 2.155; PDF p. 110)
- **R-2.156-no-true-and-correct** [sev 2] Don't rely on a statement that the recitals are true and correct; if recital matters might be inaccurate, state them as statements of fact in the body. (2.156; PDF p. 110)

### Chapter 2: The Lead-In

- **R-2.159-lead-in** [sev 3] Use the lead-in The parties agree as follows: or, after recitals, The parties therefore agree as follows: (2.159; PDF p. 112)
- **R-2.160-no-covenant-and-agree** [sev 3] In the lead-in, don't add extraneous verbs such as covenant and agree, don't use hereby, don't say the parties hereby enter into this agreement, and don't name the parties. (2.160, 2.161, 2.162...; PDF p. 112)
- **R-2.164-wrap-into-lead-in** [sev 3] If the body would be a single one-sentence provision (for example, a straightforward amendment), you can wrap it into the lead-in, followed by the concluding clause. (2.164; PDF p. 112)
- **R-2.165-no-recital-of-consideration** [sev 3] Don't use recitals of consideration (including 'backstop' recitals of unspecified consideration) just before the body; they don't establish consideration and serve no purpose. (2.165, 2.166, 2.167...; PDF p. 112)
- **R-2.179-no-presumption-recital** [sev 3] Don't include a backstop recital to invoke a rebuttable presumption of consideration; avoid disputes by stating the deal clearly. (2.178, 2.179, 2.180; PDF p. 112)
- **R-2.182-state-actual-consideration** [sev 2] State any actual consideration clearly in the body, not as a recital of consideration; if a transaction (such as a disadvantageous amendment) lacks consideration, arrange consideration and state it. (2.181, 2.182, 2.183; PDF p. 112)
- **R-2.184-waive-consideration** [sev 2] As alternatives for a transaction lacking consideration, the performing party could waive consideration and acknowledge the other party's reliance (research governing law first), or use a contract under seal where governing law dispenses with consideration for sealed contracts. (2.184, 2.185, 2.186; PDF p. 112)
- **R-2.188-good-and-valuable** [sev 3] Delete (other) good and valuable consideration and the receipt and sufficiency of which are hereby acknowledged. (2.188, 2.189, 2.190...; PDF p. 112)
- **R-2.194-conjoined-contracts** [sev 2] If two contracts are a package deal, describe the connection in the recitals and state in the body of each the implications for one contract of performance under the other. (2.194; PDF p. 112)
- **R-2.198-option-price** [sev 2] For an option contract, set a plausible option price, recite it, and make sure it's paid; if you rely on the Restatement § 87(1) approach, recite nominal consideration rather than a backstop recital. (2.195, 2.196, 2.197...; PDF p. 112)
  - Exceptions: You can dispense with consideration for options governed by a statute that says none is needed (New York General Obligations Law; UCC § 2-205 firm offers) (2.201).
- **R-2.204-guarantee-consideration** [sev 2] In a guarantee of an existing debt, state the guarantor's actual consideration rather than relying on pretense consideration; if you rely on the Restatements, use nominal consideration rather than a backstop recital. (2.202, 2.203, 2.204...; PDF p. 112)
- **R-2.212-no-word-consideration** [sev 3] Dispense with the word consideration and express the exchange accurately, including when payment occurs; for a release, say it is in exchange for a specified action or promise. (2.206, 2.207, 2.208...; PDF p. 112)
- **R-2.214-other-jurisdictions** [sev 3] Apply the same analysis to U.S.-style recitals of consideration in Canadian and U.S.-connected international contracts; in a contract governed by civil law, delete any recital of consideration. (2.214, 2.215, 2.216...; PDF p. 112)

### Chapter 2: Body Heading; Cover Sheet, Table of Contents, Index

- **R-2.218-no-body-heading** [sev 3] Don't insert a heading such as OPERATIVE PROVISIONS between the lead-in and the body. (2.218; PDF p. 123)
- **R-2.219-table-of-contents** [sev 3] For a contract over 20 pages, consider a table of contents (articles, sections, page numbers, attachments) from the first draft, preceded by an uncluttered cover sheet and followed by any index of defined terms. (2.219, 2.220, 2.221...; PDF p. 123)

### Chapter 3: General Considerations

- **R-3.41-shared-subject-verb** [sev 3] Think carefully before stating a shared subject and verb (Acme shall:) followed by enumerated clauses; the reader must supply them in each clause, and limiting a section to one category can be constraining. (3.41, 3.42; PDF p. 138)

### Chapter 3: Expressing Conditions

- **R-3.355-conditional-clause-position** [sev 3] Put a short conditional clause first and a long one after the matrix clause; put it first if it contains enumerated clauses; if both clauses have several elements, use two sentences. (3.355; PDF p. 216)

### Chapter 3: Selecting Which Category

- **R-3.550-no-bossing-court** [sev 2] Don't use verb structures that tell a court what it may do, may not do, or must do (the court shall/will be entitled to, shall have the power to, no court shall construe, X shall not be construed as, X is to be construed, shall be admissible); a judge is likely to think 'Says who!' Of the discretion forms, only the court may interpret is not suboptimal. (3.550, 3.551, 3.552...; PDF p. 268)
  - Book example: The courts shall be entitled to modify the duration and scope of any restriction contained herein ... . → The parties acknowledge that if a dispute ... arises ..., they would want the court to interpret this agreement as follows: ... .
  - Book example: The principle of ejusdem generis shall not be used to limit ... . → (see fix)
- **R-3.560-parties-acknowledge-court** [sev 2] To aim for a result in court without appearing to boss the court around, put the focus on the parties: The parties acknowledge that if a dispute between the parties arises out of this agreement or its subject matter, they would want the court to interpret this agreement as follows: ... . (3.560, 3.561; PDF p. 268)
  - Book example: (none) → The parties acknowledge that if a dispute between the parties arises out of this agreement or the subject matter of this agreement, they would want the court to interpret this agreement as follows:

### Chapter 4: Layout

- **R-4.1-body-components** [sev 3] The body of the contract consists of sections (which can be grouped into articles), subsections, and enumerated clauses. (4.1, 4.4, 4.5; PDF p. 272)
- **R-4.2-mscd-scheme** [sev 3] Use the MSCD enumeration scheme, in its "articles" version (sections grouped into articles) or its "sections" version. (4.2, 4.3; PDF p. 272)
- **R-4.3-no-first-line-indent** [sev 3] Don't use a first-line-indent enumeration scheme; indenting the first line of enumerated text makes no more sense than indenting the first line of unenumerated text. (4.3; PDF p. 272)
- **R-4.6-no-footnotes** [sev 3] Don't use footnotes in contracts. (4.6; PDF p. 273)
- **R-4.7-group-into-articles** [sev 3] Consider grouping sections that share a theme into articles once a contract has more than 25 or so sections. (4.7; PDF p. 273)
- **R-4.8-article-not-section** [sev 2] Use article, not section, for a group of sections. (4.8; PDF p. 274)
  - Look for: a group of sections labeled "section" (for example, section 1 containing sections 1.1 and 1.2)
  - Fix: Call the group an article.
- **R-4.9-no-clause-for-sections** [sev 3] Don't use the UK term clause for articles or sections; use article and section. Reserve clause for enumerated clauses. (4.9, 4.13; PDF p. 274)
- **R-4.10-article-heading-caps** [sev 3] Give each article a simple, all-encompassing heading in all capitals. (4.10; PDF p. 275)
- **R-4.11-article-numerals** [sev 3] Number articles with Arabic digits, not words or Roman numerals, and without multiple numeration: article 1, not article one, article I, or article 1.0. (4.11; PDF p. 275)
  - HOUSE: Hierarchy I. (articles), A. (sections), 1. (subsections), (a) (enumerated clauses), (i) (subclauses); 1 tab per level; native Word numbering; no only child at any level. See house-style.md section 3.
- **R-4.12-no-article-zero** [sev 3] Don't number the first article 0 (zero). (4.12; PDF p. 275)
- **R-4.14-omnibus-sections** [sev 2] In the boilerplate, combine unrelated provisions in one section only when they are brief enough that giving each its own section would waste space. (4.14; PDF p. 275)
  - Look for: one section addressing two or more unrelated topics
  - Fix: Give each provision its own section unless each is very brief.
- **R-4.15-omnibus-max-two** [sev 3] Don't combine more than two unrelated provisions in a single section, and give the section a heading that names each (for example, Amendment; Waiver). (4.15, 4.24; PDF p. 275)
- **R-4.15-omnibus-no-subsections** [sev 3] Don't use subsections in a section that combines unrelated provisions; if the provisions merit subsections, make them sections. (4.15; PDF p. 275)
- **R-4.16-all-text-in-section** [sev 3] Put all text in the body of the contract within a section. (4.16; PDF p. 276)
- **R-4.17-number-sections-plain** [sev 3] Number each section. Don't put Section before each section number, and don't bold section numbers. (4.17; PDF p. 276)
  - HOUSE: Hierarchy I. (articles), A. (sections), 1. (subsections), (a) (enumerated clauses), (i) (subclauses); 1 tab per level; native Word numbering; no only child at any level. See house-style.md section 3.
- **R-4.17-section-number-format** [sev 3] Without articles, number sections 1, 2, 3 (not 1.0, 2.0). With articles, use multiple numeration 1.1, 1.2 (not 1.01 or 1.1.). (4.17; PDF p. 276)
  - HOUSE: Hierarchy I. (articles), A. (sections), 1. (subsections), (a) (enumerated clauses), (i) (subclauses); 1 tab per level; native Word numbering; no only child at any level. See house-style.md section 3.
- **R-4.18-automatic-numbering** [sev 3] Use the automatic-numbering function in Word, or paragraph-numbering software, for sections, subsections, and tabulated enumerated clauses. (4.18; PDF p. 276)
- **R-4.19-no-first-second** [sev 3] Don't enumerate sections FIRST:, SECOND:, THIRD:, as some litigator-drafted settlement agreements do. (4.19; PDF p. 276)
- **R-4.20-enumerate-lone-section** [sev 3] Enumerate a section even if it is the only section in its article. (4.20; PDF p. 276)
  - HOUSE: Hierarchy I. (articles), A. (sections), 1. (subsections), (a) (enumerated clauses), (i) (subclauses); 1 tab per level; native Word numbering; no only child at any level. See house-style.md section 3.
- **R-4.21-section-heading-format** [sev 3] Give each section a heading: a bolded word or short phrase in headline-style capitalization. Don't use underlining, all capitals, or bold plus italics. (4.21, 4.22; PDF p. 277)
- **R-4.23-heading-not-misleading** [sev 2] Make any heading you create clear and brief; don't use a heading that promises more than the section delivers or is otherwise misleading. (4.23; PDF p. 277)
  - Test: Compare the heading with what the section actually provides.
  - Exceptions: A provision saying headings are for convenience only is of questionable value (15.18).
- **R-4.24-two-issue-heading** [sev 3] For a section addressing two distinct issues, you may give a word or phrase for each, separated by a semicolon (Amendment; Waiver). (4.24; PDF p. 277)
- **R-4.25-no-miscellaneous-section-heading** [sev 3] Don't use Miscellaneous as a section heading for unrelated topics; consider creating several shorter sections. (4.25; PDF p. 278)
- **R-4.26-no-etc-heading** [sev 3] Don't use etc. to broaden a heading (Notices, etc.); divide the section instead. Don't use etc. anywhere in a contract. (4.26; PDF p. 278)
- **R-4.27-no-subject-verb-heading** [sev 3] Don't use a subject and verb as a heading (Acme Agrees To) with the section made of enumerated clauses that each complete the sentence. (4.27; PDF p. 278)
- **R-4.28-no-unenumerated-paragraphs** [sev 2] Don't divide a section into unenumerated paragraphs, and don't mix an unenumerated paragraph into a section divided into subsections. (4.28; PDF p. 278)
  - Look for: section broken into paragraphs without (a), (b), or a hanging unenumerated paragraph after subsections
  - Fix: Enumerate every paragraph as a subsection, or make the unenumerated text its own section.
- **R-4.28-when-subsections** [sev 3] Divide a section into two or more enumerated subsections if each addresses a different aspect of one topic or the section would otherwise be too long to read comfortably. (4.28; PDF p. 278)
- **R-4.29-subsection-letters** [sev 3] Use the (a) hierarchy for subsections. If a section has ten or more subsections, consider grouping them into two or more sections rather than shifting to (aa). (4.29; PDF p. 278)
  - HOUSE: Hierarchy I. (articles), A. (sections), 1. (subsections), (a) (enumerated clauses), (i) (subclauses); 1 tab per level; native Word numbering; no only child at any level. See house-style.md section 3.
- **R-4.30-no-multiple-numeration-subsections** [sev 3] Don't use the multiple-numeration system for subsections (4.3.1, 4.3.2). (4.30, 4.31; PDF p. 278)
  - HOUSE: Hierarchy I. (articles), A. (sections), 1. (subsections), (a) (enumerated clauses), (i) (subclauses); 1 tab per level; native Word numbering; no only child at any level. See house-style.md section 3.
- **R-4.32-no-subsection-headings** [sev 3] Don't give subsections headings. (4.32; PDF p. 279)
- **R-4.33-enumerated-clause-def** [sev 3] "Enumerated clauses" are parts of a sentence in a section or subsection, preceded by introductory text, each designated by a number or letter in parentheses, with the next-to-last followed by and or or. (4.33; PDF p. 279)
- **R-4.34-use-enumerated-clauses** [sev 3] Use enumerated clauses whenever a list or series is anything other than a short string of brief clauses. (4.34; PDF p. 279)
- **R-4.35-max-clause-levels** [sev 3] A clause may contain subclauses and sub-subclauses, but treat three levels as generally a sign of undue complexity. (4.35; PDF p. 280)
- **R-4.36-clause-lowercase-start** [sev 3] Don't begin an enumerated clause with a capital letter unless the word otherwise requires one. (4.36; PDF p. 280)
- **R-4.36-one-period-in-clauses** [sev 3] Put the only sentence-ending period in a set of enumerated clauses at the end of the last clause; don't end one sentence and begin another inside the set. (4.36; PDF p. 280)
- **R-4.37-introductory-text** [sev 3] Always precede enumerated clauses with introductory text. (4.37, 4.54; PDF p. 280)
- **R-4.38-nothing-after-clauses** [sev 2] Don't continue a sentence after a set of enumerated clauses, whether the continuation modifies each clause or is unrelated. (4.38; PDF p. 280)
  - Look for: text after the last enumerated clause, before the period (for example, "..., or (3) X, in each case ..." or "..., and (3) Y, unless ...")
  - Fix: Move the continuation into the introductory text, or state it in a separate sentence.
- **R-4.39-colon-before-long-set** [sev 3] Use a colon to introduce any set of enumerated clauses more than about three lines long. (4.39; PDF p. 280)
- **R-4.39-full-clause-before-colon** [sev 3] Make whatever precedes a colon a full independent clause, with a subject and verb, that can stand alone; convert a fragment by adding the following or as follows. (4.39; PDF p. 280)
- **R-4.40-the-following-position** [sev 3] The following or as follows need not come last before the colon if it is in the only or last independent clause, but don't let one or more other independent clauses separate it from the colon. (4.40, 4.41; PDF p. 281)
- **R-4.42-semicolons-or-commas** [sev 3] Separate long, complex, or internally punctuated enumerated clauses with semicolons, and use semicolons whenever the clauses justify a preceding colon; otherwise, and always when no colon precedes the clauses, use commas. (4.42; PDF p. 281)
- **R-4.43-when-tabulate** [sev 3] You may tabulate enumerated clauses so each stands alone; the more clauses and the longer they are, the more likely tabulation helps. (4.43; PDF p. 281)
- **R-4.44-tabulate-consistently** [sev 3] Don't tabulate subclauses if their clauses are integrated (and likewise for sub-subclauses within integrated subclauses). (4.44; PDF p. 282)
- **R-4.45-keep-short-integrated** [sev 3] Keep integrated any clauses that are not preceded by a full independent clause and a colon and are separated by commas. (4.45; PDF p. 283)
- **R-4.46-no-dangling-text** [sev 3] Put tabulated enumerated clauses at the end of a sentence, so no "dangling" text starts flush left below the last clause; end the section or subsection after the clauses rather than adding unenumerated sentences. (4.46; PDF p. 283)
- **R-4.47-clause-hierarchy** [sev 3] Use (1) for enumerated clauses, (A) for subclauses, and (i) for sub-subclauses; reserve (a) for subsections. (4.47; PDF p. 284)
  - HOUSE: Hierarchy I. (articles), A. (sections), 1. (subsections), (a) (enumerated clauses), (i) (subclauses); 1 tab per level; native Word numbering; no only child at any level. See house-style.md section 3.
- **R-4.48-no-commingled-enumeration** [sev 3] Don't use "commingled enumeration": in a section without subsections, don't use (a) for first-level tabulated clauses. (4.48; PDF p. 284)
  - HOUSE: Hierarchy I. (articles), A. (sections), 1. (subsections), (a) (enumerated clauses), (i) (subclauses); 1 tab per level; native Word numbering; no only child at any level. See house-style.md section 3.
- **R-4.49-no-multiple-numeration-clauses** [sev 3] Don't use multiple numeration (1.1.1, 6.15.4.5.3) for tabulated enumerated clauses, and don't adopt the AIA .1 hierarchy. (4.49, 4.50, 4.51...; PDF p. 284)
  - HOUSE: Hierarchy I. (articles), A. (sections), 1. (subsections), (a) (enumerated clauses), (i) (subclauses); 1 tab per level; native Word numbering; no only child at any level. See house-style.md section 3.
- **R-4.53-no-bullets** [sev 3] Don't use bullets for tabulated enumerated clauses. (4.53; PDF p. 285)
- **R-4.54-no-hierarchy-jump** [sev 3] Don't follow enumeration from one hierarchy immediately, with no intervening text, by enumeration from the next hierarchy down (for example, (2) followed directly by (A)); restructure to fix both this and the missing introductory text. (4.54; PDF p. 285)
- **R-4.55-one-clause-set-per-subsection** [sev 3] Don't use two sets of tabulated clauses with different hierarchies in one section or subsection; remove enumeration from one set or move one set to its own section or subsection. (4.55; PDF p. 285)
- **R-4.56-no-clause-headings** [sev 3] Don't give tabulated enumerated clauses headings. (4.56; PDF p. 285)
- **R-4.57-indent-section-text** [sev 3] Indent all section text, and indent section and subsection text equally; don't move subsections one tab further in. (4.57; PDF p. 286)
- **R-4.58-subsection-enumeration-indent** [sev 3] Distinguish subsections by indenting the subsection enumeration slightly more than the section number. (4.58; PDF p. 286)
  - HOUSE: Hierarchy I. (articles), A. (sections), 1. (subsections), (a) (enumerated clauses), (i) (subclauses); 1 tab per level; native Word numbering; no only child at any level. See house-style.md section 3.
- **R-4.59-no-period-after-number-heading** [sev 3] Don't put a period after a section number or after a section heading. (4.59, 4.60; PDF p. 286)
  - HOUSE: Hierarchy I. (articles), A. (sections), 1. (subsections), (a) (enumerated clauses), (i) (subclauses); 1 tab per level; native Word numbering; no only child at any level. See house-style.md section 3.
- **R-4.61-clause-indent** [sev 3] Indent tabulated enumerated clauses one tab setting further in than sections and subsections, with the enumeration at the left edge of the text. (4.61; PDF p. 286)
- **R-4.62-word-styles** [sev 3] Adopt the MSCD scheme by setting up Microsoft Word styles; templates for both versions are at adamsdrafting.com/resources. (4.62; PDF p. 286)
  - HOUSE: Hierarchy I. (articles), A. (sections), 1. (subsections), (a) (enumerated clauses), (i) (subclauses); 1 tab per level; native Word numbering; no only child at any level. See house-style.md section 3.
- **R-4.63-long-blocks** [sev 3] If a section or subsection runs more than about 15 lines, consider dividing it into two or more sections or subsections, or tabulating its enumerated clauses. (4.63, 4.64; PDF p. 287)
- **R-4.65-over-fragmentation** [sev 3] At the other extreme, consider keeping the shortest components consolidated; gauge balance by the white space on the page. (4.65, 4.66, 4.67; PDF p. 287)
- **R-4.68-two-column-rarely** [sev 3] Use a two-column format rarely, if at all; minimizing page count ranks below concision, readability, and ease of work. (4.68, 4.69, 4.70...; PDF p. 289)
- **R-4.72-arranging-processes** [sev 3] Arranging the body involves three concurrent processes: deciding what topics sections address (custom mostly dictates this), allocating provisions to sections, and determining the sequence. (4.72, 4.73, 4.76...; PDF p. 290)
- **R-4.74-section-by-topic** [sev 3] Usually have each section address a specific deal issue; devoting a section to one party's obligations is usually too constraining, and such sections end up more mixed than advertised. (4.74, 4.75; PDF p. 290)
- **R-4.78-important-first** [sev 3] Put more-important and more-frequently consulted provisions first, balanced against the conventional sequence (for an acquisition: deal terms, statements of fact, preclosing obligations, closing conditions, termination, indemnification, miscellaneous). (4.78, 4.79, 4.80...; PDF p. 291)
- **R-4.83-dont-bury** [sev 2] Don't "bury" a contentious provision. (4.83; PDF p. 292)
  - Look for: contentious provision placed among boilerplate or in an unexpected place
- **R-4.85-frontload-if-justified** [sev 3] Frontload selected deal information (for example, in a table at the top) only if transactional and administrative benefits justify it. (4.85, 4.86, 4.87...; PDF p. 292)
- **R-4.89-move-not-repeat** [sev 2] Move frontloaded information out of the body; don't state it in two places. (4.89; PDF p. 293)
  - Look for: the same deal term stated in a cover table and in the body
  - Fix: Delete one statement and refer to the other.
- **R-4.90-frontloaded-signatures** [sev 3] Be cautious about frontloading signature blocks: it shows at once whether the contract is signed, but it may encourage signing without reading, and dissuading readers from reading the boilerplate invites later claims of ignorance. (4.90; PDF p. 293)
- **R-4.91-backending** [sev 3] "Backending" puts deal-specific information in a schedule; it makes more sense when that information is voluminous. (4.91; PDF p. 294)
- **R-4.92-master-agreement-analogy** [sev 3] A master agreement with statements of work is analogous to backending, driven by serial transactions between the same parties; purchase orders with separate terms are analogous to both frontloading and backending. (4.92, 4.93; PDF p. 294)
- **R-4.94-no-sentence-crossref** [sev 2] Don't cross-refer to a sentence or part of a sentence (the penultimate sentence of section 2.10; the proviso in the final sentence of this section 3). (4.94, 4.95; PDF p. 294)
  - Fix: Drop the sentence reference if unnecessary, or isolate the text in its own section or subsection.
- **R-4.96-fewer-crossrefs** [sev 3] Use as few cross-references as possible; each provision should be understandable on its own. Treat many prioritizing cross-references (notwithstanding, subject to, except as provided in) as a sign of inefficient structure. (4.96, 4.97, 4.98...; PDF p. 295)
- **R-4.100-crossref-name-and-number** [sev 3] In a cross-reference, say whether a section or an article is meant, plus its enumeration; don't use the section mark (§). (4.100; PDF p. 295)
  - HOUSE: Avoid internal cross-references; where one is needed refer by the provision's heading, not its number. Headings must be unique and match exactly; delete or limit any headings-for-convenience clause (15.18). See house-style.md section 4.
- **R-4.101-no-hereof-in-crossref** [sev 3] Don't add of this agreement or hereof to internal cross-references, and don't add above or below. (4.101; PDF p. 296)
- **R-4.102-no-repeat-section** [sev 3] When referring to two or more sections, don't repeat section: sections 5 and 7, not section 5 and section 7. (4.102; PDF p. 296)
  - HOUSE: Avoid internal cross-references; where one is needed refer by the provision's heading, not its number. Headings must be unique and match exactly; delete or limit any headings-for-convenience clause (15.18). See house-style.md section 4.
- **R-4.102-self-reference-number** [sev 3] When a provision refers to itself, include its enumeration (this section 4), even for a section. (4.102; PDF p. 296)
  - HOUSE: Avoid internal cross-references; where one is needed refer by the provision's heading, not its number. Headings must be unique and match exactly; delete or limit any headings-for-convenience clause (15.18). See house-style.md section 4.
- **R-4.103-subsection-crossref** [sev 3] Refer to a subsection as a section (this section 4(c)), not as subsection or this subsection (c); for two or more subsections of one section, repeat the section number (section 6(b) or 6(c)). (4.103; PDF p. 296)
  - HOUSE: Avoid internal cross-references; where one is needed refer by the provision's heading, not its number. Headings must be unique and match exactly; delete or limit any headings-for-convenience clause (15.18). See house-style.md section 4.
- **R-4.104-clause-crossref** [sev 3] Refer to an enumerated clause as clause (2) of section 4(b) or as section 4(b)(2); for multiple clauses repeat the section and subsection numbers (sections 6(b)(2) and 6(b)(3)). (4.104; PDF p. 296)
  - HOUSE: Avoid internal cross-references; where one is needed refer by the provision's heading, not its number. Headings must be unique and match exactly; delete or limit any headings-for-convenience clause (15.18). See house-style.md section 4.
- **R-4.105-crossref-lowercase** [sev 3] Don't use initial capitals for section and article in cross-references, and don't emphasize cross-references with bold, italics, or underlining. (4.105; PDF p. 297)
  - HOUSE: Avoid internal cross-references; where one is needed refer by the provision's heading, not its number. Headings must be unique and match exactly; delete or limit any headings-for-convenience clause (15.18). See house-style.md section 4.
- **R-4.106-no-heading-in-crossref** [sev 3] Don't include the heading in each cross-reference (article 12 (Indemnification)); if desired, insert the automated cross-reference as a hyperlink instead. (4.106, 4.107; PDF p. 297)
  - HOUSE: Avoid internal cross-references; where one is needed refer by the provision's heading, not its number. Headings must be unique and match exactly; delete or limit any headings-for-convenience clause (15.18). See house-style.md section 4.
- **R-4.108-auto-crossref-master** [sev 3] Use Word's automatic cross-referencing only in the master version; in copies sent for comment, convert field codes to text, and make next-draft changes in the master. (4.108, 4.109; PDF p. 297)
  - HOUSE: Avoid internal cross-references; where one is needed refer by the provision's heading, not its number. Headings must be unique and match exactly; delete or limit any headings-for-convenience clause (15.18). See house-style.md section 4.
- **R-4.110-intentionally-omitted** [sev 3] When deleting text would make cross-references inaccurate, you may replace the deleted text with [Intentionally omitted] and keep the enumeration. (4.110; PDF p. 298)
- **R-4.111-page-numbers** [sev 3] Number pages in Arabic numerals, leaving the first page unnumbered; with a cover sheet, use lowercase Roman numerals for the associated materials (table of contents, index of definitions). (4.111; PDF p. 298)
- **R-4.112-page-number-position** [sev 3] Generally center page numbers in the footer; if the footer holds other information, consider placing them flush right, perhaps with the word Page. (4.112; PDF p. 299)
- **R-4.113-page-x-of-y** [sev 3] For the contract proper, Page x of y (or x/y) is probably not worth its clutter. (4.113; PDF p. 299)
- **R-4.114-attachment-page-numbering** [sev 3] For multiple attachments, number pages either consecutively (as one document, where Page x of y is more useful) or nonconsecutively (each attachment separately, for example C-5); choose for the transaction, and don't use both in one set. (4.114, 4.115, 4.116; PDF p. 299)
- **R-4.117-footer-file-names** [sev 3] Use headers or, more usually, footers for file names and draft lines. (4.117; PDF p. 300)
- **R-4.118-confidential-legends** [sev 3] You may mark working drafts Confidential. Don't mark drafts exchanged with the other side Privileged and Confidential (it may suit drafts with explanatory notes shared only with the client), and don't mark draft contracts Attorney Work Product. (4.118; PDF p. 300)
- **R-4.119-logo-not-drafter** [sev 3] Don't fear that a logo in headers, footers, or a cover sheet makes the organization the "drafter" for contra proferentem purposes; other evidence of who drafted what is available. (4.119; PDF p. 300)

### Chapter 5: Back of the Contract

- **R-5.1-concluding-clause-def** [sev 3] The "back of the contract" is the concluding clause, the signature blocks, and any attachments; the concluding clause is the sentence that usually precedes the signature blocks. (5.1, 5.2; PDF p. 301)
- **R-5.3-concluding-clause-undated** [sev 3] If the introductory clause states the contract date and signers don't date their signatures, use: The parties are signing this agreement on the date stated in the introductory clause. Don't name the parties. (5.3; PDF p. 301)
- **R-5.4-concluding-clause-dated** [sev 3] If signers date their signatures, use: Each party is signing this agreement on the date specified for that party's signature. (5.4; PDF p. 301)
- **R-5.5-omit-concluding-clause** [sev 3] Omit the concluding clause unless you consider its modest narrative function and long tradition reason enough to use it; if you do, go ahead. (5.5, 5.6; PDF p. 301)
- **R-5.7-signing-not-executing** [sev 3] In the concluding clause, refer to signing, not to executing or executing and delivering. (5.7, 5.8, 5.9...; PDF p. 303)
- **R-5.13-concluding-clause-tense** [sev 3] Use the present progressive (the parties are signing), not the past (signed) or present perfect (have signed, have caused to be signed). (5.13, 5.14; PDF p. 304)
- **R-5.15-being-signed-statement** [sev 3] For consistency, revise a statement such as This agreement has been validly executed by Acme to This agreement is being validly signed by Acme (whether the statement serves any purpose is a separate question). (5.15; PDF p. 305)
- **R-5.16-as-of-concluding** [sev 3] Don't use as of for a date in the introductory or concluding clause; but if you use it in one, use it in the other. (5.16; PDF p. 305)
- **R-5.17-traditional-concluding-clause** [sev 3] Don't use the traditional concluding clause or its archaisms: IN WITNESS WHEREOF, these presents, the day and year first above written. (5.17, 5.18, 5.24; PDF p. 305)
- **R-5.19-no-authorization-in-concluding** [sev 2] Don't rely on a statement that the signer is authorized (in the concluding clause or elsewhere); ask for confirmation such as a board resolution or a list of authorized employees with specimen signatures. A reminder to your own people not to sign without authority belongs in the signature blocks. (5.19, 5.20; PDF p. 305)
- **R-5.21-signer-warrants-authority** [sev 3] Don't use the traditional "Each individual signing for an entity hereby personally warrants his or her legal authority to bind that entity"; it is peculiarly worded, and a remedy against the signer is a low priority. (5.21; PDF p. 306)
- **R-5.22-intending-legally-bound** [sev 3] Don't say the parties are intending to be legally bound; it is generally pointless. (5.22; PDF p. 306)
- **R-5.23-accepting-terms** [sev 3] Don't say the parties accept the terms of the agreement; signing suffices to show assent. (5.23; PDF p. 306)
- **R-5.25-effectiveness-boilerplate** [sev 3] If signers date their signatures, consider adding: This agreement will become effective when all parties have signed it. The date of this agreement will be the date this agreement is signed by the last party to sign it (as indicated by the date specified for that party's signature). (5.25, 5.26; PDF p. 307)
- **R-5.27-signature-mixups** [sev 3] If the parties are also parties to other contracts, refer in the concluding clause to the type of agreement rather than this agreement, or use a signature-page notation. (5.27; PDF p. 307)
- **R-5.28-no-division-name** [sev 2] Use a signature block for each party, and don't use the name of an unincorporated division; it lacks capacity to contract. (5.28; PDF p. 308)
  - Look for: signature block in the name of a division
- **R-5.29-entity-name-caps** [sev 3] For a legal entity, put its name in all capitals above the signature line; don't state its defined term above the name or its jurisdiction of organization after it. (5.29; PDF p. 308)
- **R-5.30-one-entity-per-block** [sev 2] Don't put two or more entity names above one signature line; use a separate signature block for each entity. (5.30; PDF p. 308)
- **R-5.31-by-and-name-title** [sev 3] Put By: next to the signature line; beneath it note the signer's name and title in lowercase with initial capitals, and any special capacity (for example, trustee). Use Name: and Title: only if you don't know who will sign; otherwise state the name and title instead of those labels. (5.31, 5.32; PDF p. 309)
- **R-5.33-authorized-signatory** [sev 3] To remind an entity party's signer to obtain management approval, add and authorized signatory (or and authorized signer) after the signer's name and title. (5.33, 5.20; PDF p. 306)
- **R-5.34-two-signers** [sev 2] Have two persons sign for a company when needed to manage risk, when organizational documents require it, when the other party wants a statutory presumption of authority (for example, California Corporations Code § 313), or when the contract isn't otherwise valid (English law in some circumstances). (5.34; PDF p. 309)
- **R-5.35-canadian-authority-line** [sev 3] The Canadian practice of placing I have authority to bind [the Corporation] under a block isn't clearly better than other approaches, except where it facilitates recording that requires a statement of signer authority. (5.35; PDF p. 310)
- **R-5.36-nested-signature-block** [sev 3] If the signer for an entity is itself an entity, use a signature block within a signature block. (5.36; PDF p. 310)
- **R-5.37-individual-block** [sev 3] For an individual party, put the individual's name in capitals under the signature line, add in his [or her] own capacity if confusion is a risk, and don't state the defined term above. (5.37; PDF p. 310)
- **R-5.38-date-line** [sev 3] If signers date their signatures, put Date: to one side of each signature line or directly beneath it. (5.38; PDF p. 311)
- **R-5.39-block-alignment** [sev 3] Align signature blocks one above the other or side by side; don't use the English arrangement with block information on the left and a vertical line of closing parentheses with the signature to the right. (5.39, 5.40; PDF p. 311)
- **R-5.41-read-before-signing** [sev 3] Use a Read before signing notation only where a party is an individual not represented by counsel; otherwise it is pointless. (5.41; PDF p. 311)
- **R-5.42-undated-signatures** [sev 3] To avoid requesting a new dated signature page, add to the effectiveness provision: If a party signs this agreement but fails to date their signature, the date the other party receives the signing party's signature will be deemed to be the date the signing party signed this agreement. With more than two parties, name one party (for example, the Company) as the recipient. (5.42, 5.43, 5.44...; PDF p. 311)
- **R-5.46-limited-role-block** [sev 3] If the introductory clause highlights a party's limited role, do so in its signature block too: add , for purposes of only [specified provisions] immediately after the party name. (5.46; PDF p. 312)
- **R-5.47-seal-background** [sev 2] Know where sealing still matters in the United States: (1) consideration (a sealed contract binds without consideration or raises a presumption of it); (2) limitation periods (for example, Delaware allows 20 years for actions on contracts under seal versus three years); (3) authorization (N.Y. Business Corporation Law § 107 makes the corporate seal prima facie evidence of authorized execution). (5.47, 5.48, 5.49...; PDF p. 313)
- **R-5.53-address-directly-not-formality** [sev 2] Rather than rely on sealing to deal with consideration or limitation periods, address those issues explicitly in the contract. (5.53, 5.54; PDF p. 314)
- **R-5.55-deeds** [sev 2] Outside the United States, observe local signing formalities: in England, a deed must be described as a deed or state it is executed as a deed, be signed by the appropriate persons, be witnessed, and be delivered; Australia also recognizes deeds; in China and Russia, practice is to sign and apply the corporate seal. (5.55, 5.56, 5.57...; PDF p. 315)
- **R-5.59-provide-required-formalities** [sev 2] If the law requires signing formalities for enforceability, or observing them gives a legal advantage, provide for them; for a required corporate seal, consider the notation Corporate seal here next to each block. (5.59; PDF p. 316)
- **R-5.60-eliminate-irrelevant-formalities** [sev 3] Otherwise, eliminate all references to sealing and other irrelevant signing formalities. (5.60; PDF p. 316)
- **R-5.61-witness-block** [sev 3] To provide for witnessing (required by law for some contracts, such as mortgages in some states), put a witness signature block preceded by Witness: next to the block being witnessed; Attest: is an alternative but obscure to many readers. (5.61, 5.62; PDF p. 316)
- **R-5.63-notarizing** [sev 3] Some U.S. state laws require signatures on certain contracts to be acknowledged before a notary or other official (for example, Colorado for independent-contractor agreements); contracts often require notarization even when the law doesn't, presumably to avoid identity disputes. (5.63, 5.64; PDF p. 316)
- **R-5.65-e-signature** [sev 3] E-signature software applies signatures and dates to signature blocks whatever their format; it differs from scanning a signature stamp. (5.65; PDF p. 317)
- **R-5.66-no-approved-as-to-form** [sev 1] Don't have counsel sign a settlement agreement under APPROVED AS TO FORM AND CONTENT; if the aim is to show the parties had legal advice, have the parties say so in the agreement. (5.66, 5.67; PDF p. 317)
- **R-5.68-consents** [sev 3] Signature blocks may be followed by a consent (or acknowledgment) in which nonparties consent to something in the contract, such as guarantors consenting to restructured debt; check whether it is necessary, because guarantees usually allow modification without guarantor consent. (5.68; PDF p. 318)
- **R-5.69-signature-page-follows** [sev 3] Keep the concluding clause and signature blocks together on one page; if that leaves blank space after the body, add [Signature page follows] rather than [The remainder of this page has been intentionally left blank]. (5.69; PDF p. 318)
- **R-5.70-signature-page-notation** [sev 3] As an alternative to naming the agreement type in the concluding clause, state at the bottom of the signature page the contract type and, as necessary, the date and party names; this is particularly useful when signature blocks span more than one page. (5.70, 5.71; PDF p. 318)
- **R-5.107-end-of-agreement-overview** [sev 3] End of Agreement (or a variant) might be useful at the end of a contract whose signatures are at the front, and after attachments, but less awkward alternatives may be preferable. (5.107; PDF p. 327)
- **R-5.108-no-end-before-signatures** [sev 3] Don't use End of Agreement right after the body and before the signature blocks; if the concern is blank space, use Signature page follows. (5.108; PDF p. 327)
- **R-5.109-no-end-after-signatures** [sev 3] Don't use End of Agreement after signature blocks at the back. (5.109, 5.110; PDF p. 327)
- **R-5.111-end-with-front-signatures** [sev 3] With frontloaded signature blocks, consider Page x of y or blank space at the bottom of the last page to signal the end, rather than the awkward End of Agreement; don't use a dinkus (* * *), which usually denotes omission or a break. (5.111, 5.112, 5.113...; PDF p. 328)
- **R-5.115-end-clickwrap** [sev 3] For clickwrap, shrinkwrap, or other unsigned contracts squeezed unformatted into a webpage, readme file, or dialog box, End of Agreement or an equivalent may be the clearest and most prudent option. (5.115; PDF p. 328)
- **R-5.116-end-after-attachments** [sev 3] Rather than End of Agreement after attachments, number the pages of the whole set of attachments Page x of y and identify the kind of attachment in a header or footer on every page. (5.116, 5.117; PDF p. 329)
- **R-5.118-no-end-of-article** [sev 3] Don't put End of Article x after every article. (5.118, 5.119; PDF p. 329)

### Chapter 13: Selected Usages

- **R-13.413-incorporate-recitals** [sev 3] Don't incorporate recitals by reference into the body of the contract. (13.413; PDF p. 671)
- **R-13.480-joinder** [sev 3] Call the document by which someone becomes party to an existing contract an amendment, not a joinder, joinder agreement, or accession agreement; repurposing an unrelated legal term of art is unnecessarily legalistic. (13.480, 13.482, 13.483...; PDF p. 686)
- **R-13.580-mutual-consent-amendment** [sev 3] Instead of by mutual consent of the parties for amendments, state that an amendment must be in writing and signed by both parties. (13.580; PDF p. 710)
- **R-13.646-novation** [sev 3] Instead of saying an amendment does not effect a novation, say it will not result in any of the Obligations being replaced; novation is a term of art many readers won't know. (13.646, 13.647, 13.648; PDF p. 726)
- **R-13.661-one-hand-intro-clause** [sev 3] Don't use on the one hand ... on the other hand in the introductory clause to group parties by role; recitals are for indicating roles. (13.661; PDF p. 730)
- **R-13.920-unless-context-requires** [sev 2] Eliminate unless the context otherwise requires (or requires otherwise); it adds uncertainty a litigator might exploit. If you want to deviate from an across-the-board convention, be specific. (13.920, 13.921; PDF p. 788)
  - Fix: Delete; state any specific deviation.

### Chapter 15: Internal Rules of Interpretation

- **R-15.1-internal-rules-types** [sev 3] Treat internal rules of interpretation skeptically. They come in three types: rules comparable to autonomous definitions (might be useful); rules that state the obvious or do what other means do better (you can do without them); and rules that overreach in trying to create order (don't rely on them). If readers can't understand basic usages without help, something is amiss. (15.1, 15.2, 15.3...; PDF p. 820)
- **R-15.6-interpretation-unless-context** [sev 2] Don't open an internal rule of interpretation with Unless the context otherwise requires; it undercuts the certainty the provision is meant to offer. (15.6; PDF p. 821)
  - Fix: Delete the phrase.
- **R-15.7-time-zone-rule** [sev 3] A rule such as All references to time are based on the time in [location] might be useful; it spares stating a time zone after each reference. It matters only for parties in different time zones or business conducted across zones. (15.7; PDF p. 821)
- **R-15.8-business-day-rule** [sev 3] A rule that an action due on a day that is not a Business Day may be taken on the next Business Day might be useful, but it is redundant in a contract that measures all periods in business days. (15.8; PDF p. 821)
- **R-15.9-rule-references-to-sections** [sev 3] Don't include a rule that references to articles, sections, exhibits, and schedules are to those of this agreement; it states the obvious. (15.9; PDF p. 821)
- **R-15.10-rule-singular-plural-definitions** [sev 3] Don't include a rule that definitions apply to the singular and plural; that is true without the provision, and defining terms in both singular and plural just adds clutter. (15.10; PDF p. 822)
- **R-15.11-rule-agreement-as-amended** [sev 3] Don't include rules that a reference to an agreement means it as amended, or that a reference to a statute includes amendments and successor provisions; adding as amended is unnecessary, so these rules are too. (15.11, 15.12; PDF p. 822)
- **R-15.13-rule-party-named** [sev 3] A rule that party refers only to a named party (to keep a no-third-party-beneficiary provision from reaching others) is unnecessary; a more economical fix exists (2.112). (15.13; PDF p. 822)
- **R-15.14-rule-pronoun-gender** [sev 3] A rule that a pronoun applies to any gender is unnecessary if you draft gender-neutrally, which is always a good idea. (15.14; PDF p. 822)
- **R-15.15-rule-here-words** [sev 3] A rule that here- words refer to the whole agreement is inaccurate for hereby in language of performance; more to the point, don't use here- words at all, except hereby in language of performance. (15.15; PDF p. 822)
- **R-15.16-rule-from-to-until** [sev 3] A rule that from means from and including and to and until mean to but excluding is fine as far as it goes but covers only a small part of time-reference ambiguity; a complete rule would be unwieldy, so purge each time reference of ambiguity instead. (15.16; PDF p. 823)
- **R-15.17-rule-contra-proferentem** [sev 3] A contra proferentem waiver (Because each party was involved in drafting ...) reflects how courts act anyway; courts would likely ignore it if it doesn't reflect how the contract was drafted. (15.17; PDF p. 823)
- **R-15.18-rule-headings** [sev 3] Don't rely on a rule that headings are for convenience only: where a heading is carelessly mismatched, it does only what a court would do anyway; where a heading arguably reflects intended scope, a court might ignore the rule. It is of questionable use. (15.18; PDF p. 824)
  - HOUSE: partly superseded: House rule 4: always delete a headings-for-convenience clause or limit it ("Headings do not affect the meaning of the provisions they introduce, but references to a provision by its heading identify that provision"), because references identify provisions by heading.
- **R-15.19-rule-including-without-limitation** [sev 3] Don't rely on a rule that including is to be read as followed by without limitation; it is unhelpful. (15.19; PDF p. 824)
- **R-15.20-rule-and-or** [sev 2] Don't rely on rules that or is disjunctive and and is conjunctive, or that or is not exclusive; they grossly oversimplify the ambiguity of and and or (chapter 11), and on or the two provisions take opposite approaches. (15.20; PDF p. 824)
  - Fix: Resolve each and/or ambiguity in context (chapter 11).
- **R-15.21-rule-will-means-shall** [sev 2] Don't rely on a rule that will means shall; it is a hopeless attempt to resolve will/shall confusion. (15.21; PDF p. 824)
  - Fix: Use shall only to impose a duty on a party that is the subject (3.89).
- **R-15.22-rule-shall-mandatory** [sev 3] A rule that shall is mandatory and may is discretionary is unnecessary if you use shall only to impose a duty on the subject of the sentence; courts have long recognized shall for obligations. Drafters who overuse shall shouldn't use the rule, since it couldn't apply to their drafting. (15.22; PDF p. 824)
- **R-15.23-rule-singular-includes-plural** [sev 2] Don't rely on a rule that the singular includes the plural and vice versa to prevent a singular/plural fight; if you mean one or more widgets, say so. (15.23; PDF p. 824)
  - Fix: one or more [nouns]
- **R-15.24-rule-successors-assigns** [sev 3] Instead of a rule that a reference to a Person includes its successors and assigns, state to what extent a party may transfer elements of its performance. (15.24; PDF p. 825)

### Chapter 18: Amendments

- **R-18.1-amend-or-restate** [sev 3] Amend (a new contract containing only the changes) when making a few discrete changes; amend and restate (the original revised to include prior and new amendments) when the changes are extensive or follow other amendments, making them hard to track. (18.1, 18.2, 18.3...; PDF p. 858)
- **R-18.5-variation** [sev 3] Don't use variation or vary for amending a contract; use amendment and amend. Synonyms cause waste and mischief, and in standard English a variation is something new, not a modified original. (18.5, 18.6, 18.7; PDF p. 859)
- **R-18.8-amendment-title** [sev 3] State in the title that the contract amends, or amends and restates, and name the type of agreement (AMENDED AND RESTATED MERGER AGREEMENT); number each amendment, at least from the second onward (AMENDMENT NO. 4 TO CREDIT AGREEMENT); don't include party names. (18.8; PDF p. 859)
- **R-18.9-amendment-intro-recitals** [sev 3] In an amendment, don't refer to the amended contract in the introductory clause; refer to it in the recitals and, if feasible, briefly state why the parties are amending. Don't create the defined term this Amendment. (18.9; PDF p. 860)
- **R-18.10-amendment-lead-in** [sev 3] Use the same lead-in as for any contract; for an amended and restated contract, say The parties therefore amend and restate the [contract] to read in its entirety as follows. (18.10, 18.11; PDF p. 860)
- **R-18.12-hereby-amended** [sev 3] Amending language is language of performance: prefer is hereby amended over is amended or is amended as of the date hereof; the passive is appropriate because it is clear who is amending. (18.12; PDF p. 860)
  - HOUSE: Active voice only. Recast passives: name the actor (any Person if unknown); legal fictions as 'This agreement treats X as' or a linking verb ('will be effective'; will, because a notice is a contingent future event, MSCD 3.334); amendments as 'The parties hereby amend Section 4 (Payment) of the Original Agreement to read as follows'. See house-style.md section 1.
- **R-18.13-amend-vs-supplement** [sev 3] An amendment changes the original; a supplement adds to it. A second agreement amends only if it says its provisions are added to the original; if its provisions are freestanding, call it a supplement, not the fusty Latinism addendum. (18.13; PDF p. 861)
- **R-18.14-change-part-provision** [sev 3] For a change to less than a whole section or subsection, either state only the exact change (by replacing '28 February 2019' with '30 April 2019') or restate the entire provision (is hereby amended to read in its entirety as follows); stating the change is concise but lacks context, restating gives context but is longer. (18.14, 18.15, 18.16...; PDF p. 861)
- **R-18.18-adding-sections** [sev 2] Add a provision with The Agreement is hereby amended by adding after section 10 the following new section 11; if the insertion isn't at the end, follow at once with a renumbering amendment. It is best to insert at the end of the agreement, section, or series, to avoid breaking internal cross-references and references in other contracts. (18.18, 18.19, 18.20; PDF p. 862)
  - Fix: (1) by adding after section 10 the following new section 11 and (2) by renumbering sections 11 through 19 as sections 12 through 20
  - Exceptions: Fine-tuning and/or and the final period when adding a last clause is strictly required, but omitting it couldn't harm a party (18.20).
- **R-18.21-deleting-sections** [sev 2] Delete a provision with The Agreement is hereby amended by deleting section 10 in its entirety; if it isn't at the end, renumber or, more simply, keep the number and replace the text with the bracketed place-filler Intentionally omitted, which leaves cross-references intact. (18.21, 18.22; PDF p. 863)
  - Fix: [Intentionally omitted]
- **R-18.23-amendment-layout** [sev 3] When adding an entire section, subsection, or tabulated enumerated clause, indent it, set it in italics, and format it as in the amended contract, to distinguish it from the amendment's own text. (18.23; PDF p. 864)

### Chapter 19: Letter Agreements

- **R-19.1-letter-of-intent-title** [sev 2] Don't give a regular contract the title letter of intent; it sends mixed signals. Letters of intent are by convention letter agreements. (19.1, 19.2; PDF p. 865)
  - Fix: Use a title that reflects a binding contract.
- **R-19.3-letter-components** [sev 3] A letter agreement consists of the sender's address, date, recipient's address, salutation, introductory sentence, substantive terms, closing sentence, sender's signature, and recipient's signature; a subject line is allowed, but a title isn't. (19.3; PDF p. 865)
- **R-19.4-letter-addresses** [sev 3] The sender is the party itself (for an entity, not its representative); its address can be typed or in letterhead. Date the letter as for an introductory clause. The recipients are the persons, other than the sender, to be bound; for an entity, usually add an Attention line naming a representative. (19.4, 19.5, 19.6; PDF p. 865)
- **R-19.7-letter-salutation** [sev 3] For an individual recipient, use Dear plus the name, reflecting the relationship; for an entity, dispense with a salutation. Don't use Dear Sirs (gender-specific, old-fashioned), Dear Sirs and Madams, Ladies and Gentlemen, or To whom it may concern. (19.7, 19.8; PDF p. 866)
- **R-19.9-letter-intro-sentence** [sev 3] Open with an introductory sentence such as The purpose of this letter agreement is to state the terms of [the transaction]. (19.9; PDF p. 866)
- **R-19.10-letter-substantive-terms** [sev 2] Phrase the substantive terms as in a regular contract; you can drop section numbers and headings, but generally keep them. Use the third person, not you and we or us. (19.10, 19.11; PDF p. 867)
  - Fix: Acme shall ...; Widgetco may ...
- **R-19.12-letter-closing** [sev 3] Use a closing sentence as in sample 14 (it can also refer to return of a signed copy). Place the sender's signature where a sender usually signs a letter; Yours sincerely isn't necessary; use regular-contract signature-block format, with an entity's block in the entity's name. (19.12, 19.13, 19.14; PDF p. 867)
- **R-19.15-letter-recipient-signature** [sev 3] Give each recipient its own signature block, usually under the sender's, flush left, preceded by Agreed to (and accepted adds nothing). Generally include a date, or a court might apply the letter's date; if a particular date matters, state it (Agreed to on the date of this letter agreement) rather than leaving it blank. Prefer not to use an as of date. (19.15, 19.16, 19.17; PDF p. 867)
