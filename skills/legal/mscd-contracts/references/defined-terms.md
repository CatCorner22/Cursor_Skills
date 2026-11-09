# Defined terms

Read this file in pass 2 (the defined-term inventory). `scripts/mscd_lint.py --inventory` lists every defined term, where the contract defines it, and every use, and flags terms that are unused, undefined, or used in 2 forms.

Key points: definitions are autonomous (*"X" means*) or integrated (*(the "X")*; for a party name, no article: *("Company")*, house rule 11) (6.21); *means* for a full definition, *includes* to enlarge, *does not include* to limit (6.32-6.39); never *shall mean* or *shall be* in a definition (6.33-6.42); don't stuff a definition with obligations or conditions (6.49-6.56); capitalize every use (6.10), except that a party's common-noun defined term may also appear in lowercase in its ordinary sense (rider, July 2026); party names take no article: *Company*, *Apple* (house rule 11; 2.105 and 6.63 differ).

A capitalized defined term used inside its own definition (*"Obligations" means all Obligations of Borrower under the Loan Documents*) is a circular definition of 1 term: severity 1, MSCD 6.3 notwithstanding (Blake's choice; `house-style.md` section 10). The word in lowercase, in its ordinary sense, isn't circular (*"Trademark" means a registered trademark ...*). Numbered definitions on the other side's draft keep their numbers (house rule 3); in a draft you write, list definitions without markers (6.27). Check every term against the terms of art (house rule 13): *Security* keeps its legal meaning, but data-security terms (*data security*, *security incident*, *security measures*) and a *security deposit* stay; a bare defined *Security* becomes *Security Interest* or *Collateral*.

> **Book examples are in MSCD5's style, not house style.** They may use lowercase *schedule*, *1 January 2024*, spelled-out numbers, 1.1 numbering, *the* before party names, or a passive that MSCD accepts. Restate any example in house style (`house-style.md`) before you put it in a contract or a comment. For the other side's drafts, the house rule is to flag everything, whatever a rule's "let-pass" or "style-only" label says.


## Rules (117, generated from `data/rules.jsonl`)

Format: id, severity (1 = ambiguity or meaning-changing; 2 = vagueness or dispute risk; 3 = style), the rule, and its MSCD paragraphs and PDF page. `HOUSE` marks a rule that Blake's house style changes: apply the house rule. For a rule's full record (test, fix, exceptions, verified book examples), run `python3 scripts/rules_query.py --id <id>`.


### Chapter 1: Contract Language Should Express Ideas Without Redundancy

- **R-1.47-however-referred-to** [sev 3] In an autonomous definition, instead of a long string of synonyms, consider however referred to to show the definition refers to a concept. (1.47, 1.48; PDF p. 68)

### Chapter 2: The Introductory Clause

- **R-2.23-no-effective-date-term** [sev 3] Don't create a defined term such as Effective Date or Date of Execution for the introductory-clause date; refer to the date of this agreement. (2.23; PDF p. 82)

### Chapter 2: Defined Terms for Party Names

- **R-2.91-define-party-names** [sev 3] Create in the introductory clause a defined term for each party name. (2.90, 2.91; PDF p. 96)
- **R-2.92-party-term-format** [sev 3] Use an integrated definition with the defined term in parentheses, in quotation marks and bold (don't bold the quotation marks or the), without introductory text such as hereinafter referred to as. (2.92; PDF p. 96)
- **R-2.93-parenthetical-position** [sev 3] For an entity, place the defined-term parenthetical after the jurisdiction reference. (2.93; PDF p. 96)
- **R-2.95-no-successors** [sev 2] Don't state in a defined-term parenthetical that the defined term includes the party's successors; cover succession by default rules or targeted provisions. (2.95; PDF p. 96)
- **R-2.97-name-or-common-noun** [sev 3] Base a party defined term on the party's name (slightly more accessible) or on a common noun (the Company, the Shareholder); common nouns work well for standard roles, single-entity contracts, or unknown signers. (2.97, 2.98, 2.103; PDF p. 98)
- **R-2.99-individual-name-term** [sev 3] For an individual, use the last name (or the first name if two individuals share a last name); add an honorific if the last name alone is too stark or to show respect. (2.99; PDF p. 98)
- **R-2.100-company-name-term** [sev 3] For a company, use a word or two from its name rather than an abbreviation where possible, and avoid abbreviations with unrelated meanings or connotations (DOG, SAD). (2.100, 2.101, 2.102; PDF p. 98)
- **R-2.104-final-syllable-pairs** [sev 2] Don't use paired defined terms that differ only in their final syllable. (2.104; PDF p. 98)
- **R-2.105-definite-article** [sev 3] Use the definite article with a common-noun party defined term (the Purchaser, not Purchaser), and be consistent. (2.105; PDF p. 98)
  - HOUSE: No article before a defined party name, including common-noun terms: Company shall pay Employee, not the Company shall pay the Employee (house-style.md section 11).
- **R-2.106-no-alternative-terms** [sev 2] Don't offer alternative defined terms for a party. (2.106; PDF p. 98)
  - Book example: "Widgetco" or the "Company" → (see fix)
  - Book example: "Widgetco," sometimes referred to herein as the "Company" → (see fix)
- **R-2.107-vendor-seller-supplier** [sev 3] Choose among Vendor, Seller, and Supplier deliberately: vendor suggests a party in the business of selling the goods; seller suggests it isn't; supplier suggests it is and is supplying over time. (2.107; PDF p. 98)
- **R-2.108-employee-term** [sev 3] Consider the Employee as the default defined term for an employee; the Executive seems unnecessary and perhaps old-fashioned. (2.108; PDF p. 98)
- **R-2.109-collective-terms** [sev 2] Define a collective party term in the singular or the plural but not both, and don't use a singular defined term (the Lender) for two or more parties via collectively or together with. (2.109; PDF p. 101)
- **R-2.110-no-the-parties-term** [sev 3] Don't define the Parties for all the parties; say the parties, and drop the pair individually a "Party" and collectively the "Parties." (2.110, 2.113; PDF p. 101)
- **R-2.112-signatories-enforcement** [sev 2] In a provision saying only the parties may enforce the contract, refer to the parties by name or to the signatories, because a court might read the parties to include intended third-party beneficiaries. (2.111, 2.112; PDF p. 101)
- **R-2.114-party-of-first-part** [sev 2] Don't use party of the first part and party of the second part, even only in the introductory clause. (2.114, 2.115; PDF p. 101)
- **R-2.116-party-a-party-b** [sev 3] Avoid Party A and Party B as party defined terms; they say nothing about each party's role. (2.116; PDF p. 101)
- **R-2.117-role-labels** [sev 2] Where either party might play a given role, use generic labels that describe the role (the withdrawing member, the Indemnifying Party), defined if used often; avoid that party / the other party in complex provisions and contextless labels like X and Y. Choose labels carefully: a label can carry unintended consequences. (2.117, 2.118, 2.119...; PDF p. 101)
  - Book example: the non-breaching party → the party claiming breach

### Chapter 2: The Defined Term This Agreement

- **R-2.123-no-this-agreement-term** [sev 3] Don't create the defined term this Agreement; refer to this agreement, lowercase, without defining it (likewise this amendment, this assignment). (2.123, 2.124, 2.125; PDF p. 104)
- **R-2.127-no-title-abbreviation** [sev 3] Don't use an abbreviation of the title (APA, NDA, MSA) as the contract's reference to itself. (2.127, 2.128; PDF p. 104)

### Chapter 2: Recitals

- **R-2.157-defined-terms-in-recitals** [sev 3] You may define terms in the recitals, but don't use autonomous definitions there, don't overload them, and don't use terms defined only later in the contract. (2.157, 2.158; PDF p. 110)

### Chapter 6: Defined Terms

- **R-6.1-defined-term-types** [sev 3] Treat words and phrases for which the contract provides definitions as "defined terms"; each definition is either autonomous (linked to the defined term by a definitional verb) or integrated (part of a regular sentence, with the defined term in a parenthetical). (6.1, 6.21; PDF p. 331)
- **R-6.2-purpose** [sev 3] Use a defined term to make the contract easier to read (a short term replaces a longer definition) and to ensure that whatever is defined is expressed consistently. (6.2; PDF p. 331)
- **R-6.3-term-in-own-definition** [sev 3] You may repeat the defined term inside its own definition; a contract defined term is only a convenient substitute for its definition in that contract, so this isn't circular. (6.3, 9.120; PDF p. 331)
  - HOUSE: partly superseded: Blake's choice: a capitalized defined term used inside its own definition ("Obligations" means all Obligations of Borrower under the Loan Documents) is a circular definition of 1 term, severity 1; the word in lowercase, in its ordinary sense, stays ("Trademark" means a registered trademark ...). See house-style.md sections 0 and 10.
- **R-6.4-parts-of-speech-terms** [sev 3] Defined terms are usually nouns (common or proper) or noun phrases; occasionally a verb (transfer) or a prepositional phrase (to Acme's knowledge). (6.4; PDF p. 331)
- **R-6.5-no-singular-and-plural** [sev 3] Don't define a term in both singular and plural forms ("Note" and "Notes" mean ...; each a "Member" and collectively the "Members"). (6.5; PDF p. 332)
- **R-6.5-no-singular-plural-rule** [sev 3] Don't address in an internal rule of interpretation the practice of defining in the singular and using in the plural, or vice versa. (6.5; PDF p. 332)
- **R-6.5-singular-definition** [sev 3] Define a common-noun defined term in the singular, unless the plural is simpler. (6.5; PDF p. 332)
- **R-6.6-no-alternative-abbreviation** [sev 3] Don't use as alternative defined terms both a word or phrase and its abbreviation ("Customer Service Request" or "CSR" means ...); use one or the other. (6.6; PDF p. 332)
- **R-6.7-initial-capitals** [sev 2] Use initial capitals for every defined term, even routine ones such as Person or Subsidiary, with no exceptions; if many instances make the text harder to read, find a way to omit the defined term rather than drop the capitals. (6.7, 6.8; PDF p. 332)
  - Look for: a defined term appearing in lowercase
- **R-6.7-no-emphasis-on-use** [sev 3] Don't use bold, italics, all capitals, or quotation marks each time you use a defined term. (6.7; PDF p. 332)
- **R-6.9-define-all-abbreviations** [sev 3] Provide definitions for all abbreviations, even widely known ones such as SEC. (6.9; PDF p. 332)
- **R-6.10-every-instance-capitalized** [sev 1] Make sure every instance of a defined term uses initial capitals; use case-sensitive search to check. (6.10, 6.11; PDF p. 333)
  - Test: Search case-sensitively for the lowercase form of each defined term.
  - Fix: Capitalize the instance, or use a different word if a different meaning is intended.
- **R-6.11-no-lowercase-different-meaning** [sev 1] Don't use a lowercase version of a defined word or phrase to express a different meaning; use a different word or phrase. (6.11; PDF p. 333)
  - Exceptions: Unavoidable if the defined term is a common word, for example Bank.
- **R-6.12-no-near-miss-terms** [sev 1] Don't use a word or phrase that differs from a defined term but is close enough to make the reader wonder whether it refers to the defined term. (6.12; PDF p. 333)
  - Look for: phrase resembling a defined term (for example, "services are substantially completed" alongside defined "Substantial Completion")
- **R-6.13-single-item-term** [sev 1] Don't use a defined term that refers to a single item in a way that suggests there are more than one (for example, any Note when Note is a specific note). (6.13; PDF p. 333)
- **R-6.14-abbreviations-ok** [sev 3] You may use abbreviations (acronyms, read as words, like ERISA; initialisms, read as letters, like SEC) as defined terms. (6.14; PDF p. 334)
- **R-6.15-a-or-an-abbreviation** [sev 3] Before an abbreviation used as a common noun, choose a or an by the sound of its first syllable, go with the pronunciation you and your colleagues use, and apply it consistently throughout the contract. (6.15; PDF p. 334)
- **R-6.16-abbreviation-excess** [sev 3] Don't use acronyms and initialisms to excess; they turn contracts into alphabet soup. (6.16; PDF p. 334)
- **R-6.17-conventional-terms** [sev 3] If a conventional defined term exists for the meaning (Business Day, the Code, GAAP, Indemnifiable Losses), use it. (6.17; PDF p. 334)
- **R-6.18-modify-unorthodox-conventional** [sev 2] If you give a conventional defined term an unorthodox definition, modify the term to alert the reader (Adjusted Net Operating Income instead of Net Operating Income). (6.18; PDF p. 335)
- **R-6.19-concise-informative-terms** [sev 3] For a definition unique to the transaction, use a term that is concise yet informative and specific enough to distinguish it from other defined terms in that contract (the Property; the Acmetown Property; the 144 Ninth Street Acmetown Property). (6.19, 6.20; PDF p. 335)
- **R-6.22-autonomous-def** [sev 3] An autonomous definition links the defined term to the definition by a definitional verb; the term also covers the whole sentence. (6.22; PDF p. 335)
- **R-6.23-term-before-definition** [sev 3] Place the defined term before the definition ("Exchange Act" means the Securities Exchange Act of 1934), not after (Any such transfer is referred to in this agreement as a "Permitted Transfer"). (6.23; PDF p. 336)
- **R-6.24-no-article-before-autonomous** [sev 3] In an autonomous definition, don't put the, a, an, or The term before the defined term. (6.24; PDF p. 336)
- **R-6.25-in-this-agreement-intro** [sev 3] Introduce a single autonomous definition with In this agreement, followed by a comma; introduce a set with In this agreement, the following definitions apply, followed by a colon. Don't use wordier alternatives such as For purposes of this agreement, the following terms have the following meanings. (6.25; PDF p. 336)
- **R-6.26-definition-paragraphs** [sev 3] In a set, state each autonomous definition as a separate paragraph without first-line indent, end each with a period (not a semicolon), and put the set in alphabetical order. (6.26; PDF p. 336)
- **R-6.26-no-text-after-autonomous** [sev 2] Don't add text at the end of the paragraph that constitutes an autonomous definition, including another sentence that builds on the definition; address that topic elsewhere. (6.26, 6.55; PDF p. 336)
  - Look for: a second sentence in a definition paragraph
- **R-6.27-no-enumerated-definitions** [sev 3] Don't enumerate a set of autonomous definitions. (6.27; PDF p. 336)
  - HOUSE: partly superseded: In a document Blake drafts, list definitions without markers. On a draft that already numbers its definitions, keep the numbers and don't flag them (Blake's decision). See house-style.md section 3.
- **R-6.28-autonomous-placement** [sev 3] Place an autonomous definition either in a definition section or on-site; put on-site autonomous definitions (a sentence among others, or their own subsection if more than a couple of lines) right after the provisions that use the defined terms. (6.28, 6.29, 6.30; PDF p. 337)
- **R-6.31-quote-and-bold** [sev 3] Put the defined term in quotation marks and bold, in both autonomous definitions and defined-term parentheticals; don't bold the quotation marks. (6.31, 6.66; PDF p. 337)
- **R-6.32-means-full** [sev 3] If the definition is full (it gives the entire meaning), use means. (6.32; PDF p. 337)
- **R-6.33-not-mean** [sev 3] Don't use mean as the definitional verb, even when the defined term is plural; treat the defined term as a label. (6.33, 6.34; PDF p. 337)
- **R-6.35-not-is-are** [sev 3] Don't use is or are as the definitional verb. (6.35, 6.36, 6.37; PDF p. 338)
- **R-6.38-includes-enlarging** [sev 2] An enlarging definition (part of the meaning) uses includes; a limiting definition (excluding something) uses does not include. Used alone, both leave the full scope unstated and can create mischief. (6.38; PDF p. 338)
- **R-6.39-full-plus-enlarging-limiting** [sev 2] To avoid the uncertainty of enlarging or limiting definitions used alone, combine a full definition with either or both: W means X [and includes Y] [but does not include Z]. (6.39; PDF p. 338)
  - Fix: Rewrite as "W" means X and includes Y but does not include Z.
- **R-6.40-no-means-and-includes** [sev 2] Don't use means and includes, and don't use includes only. (6.40; PDF p. 339)
- **R-6.41-no-dash-colon** [sev 3] Don't use a dash or a colon instead of a definitional verb. (6.41; PDF p. 339)
- **R-6.42-no-shall-mean** [sev 3] State the definitional verb in the present tense; don't use shall mean or shall have the meaning. (6.42; PDF p. 339)
- **R-6.43-part-of-speech-match** [sev 2] With means, includes, or does not include, make the part of speech of the defined term match that of the definition; otherwise use refers to (for example, "Register", "Registered", and "Registration" refer to ...). (6.43, 6.44; PDF p. 339)
  - Look for: a verb or adjective form defined with means by a noun phrase
  - Test: Substitute the definition for the defined term in a sentence that uses it; if the grammar breaks, the parts of speech don't match.
- **R-6.45-noun-verb-forms** [sev 3] If a term has identical noun and verb forms (Control, Transfer), you may define each separately: "[Defined Term]" means, when used as a noun, [first definition], and when used as a verb, [second definition]. (6.45; PDF p. 339)
- **R-6.46-corresponding-meanings-rule** [sev 2] Be wary of an internal rule of interpretation giving defined terms corresponding meanings in other parts of speech; it could have unexpected consequences. If confusion is possible, define each form, and if you have an alternative to defining several forms, use it. (6.46, 6.47, 6.48; PDF p. 340)
- **R-6.49-no-stuffing** [sev 2] Don't include in an autonomous definition anything beyond what the defined term means. (6.49, 6.56; PDF p. 340)
  - Fix: Move conditions, obligations, makeup, and function into operative provisions.
- **R-6.50-stuffing-verbs** [sev 2] Treat shall, must, may, or will in a definition as a symptom of stuffing; state the obligation elsewhere using language of obligation. (6.50; PDF p. 340)
  - Book example: "Acme Financial Statements" means ... which Acme shall deliver no later than three months after the end of each Acme fiscal year. → (see fix)
- **R-6.51-stuffing-conditions-makeup** [sev 2] Address conditions, requirements, and prohibitions (such as trustee approval not to be unreasonably withheld), and the makeup and function of a thing, separately from the definition of its identity. (6.51, 6.52, 6.53...; PDF p. 340)
- **R-6.57-no-integrated-in-autonomous** [sev 3] Don't put an integrated definition inside an autonomous definition (... declared effective by the Securities and Exchange Commission (the "SEC")); define the term elsewhere and use just the defined term. (6.57, 6.58; PDF p. 341)
- **R-6.59-integrated-def** [sev 3] An integrated definition is part of a regular sentence, with the defined term stated in parentheses after the definition, in a "defined-term parenthetical." (6.59, 6.60; PDF p. 342)
- **R-6.61-parenthetical-after-list** [sev 1] If a defined-term parenthetical at the end of a list creates syntactic ambiguity about how far back the definition goes, consider prefacing the list with the following plus a colon, with the parenthetical between the following and the colon; or clarify the scope (6.75), or use an autonomous definition. (6.61; PDF p. 342)
  - Look for: defined-term parenthetical after the last item in a series
  - Book example: (none) → the Promoter shall supply the Band with the following (the "Requirements"): (1) ...
- **R-6.62-no-hereinafter** [sev 3] Don't use hereafter, hereinafter referred to as, or similar legalistic fluff in a defined-term parenthetical. (6.62; PDF p. 342)
- **R-6.63-article-in-parenthetical** [sev 3] In a defined-term parenthetical, include the, a, or an as appropriate (needed only for common nouns), and put it before (outside) the opening quotation mark. (6.63, 6.67; PDF p. 342)
  - HOUSE: partly superseded: A party-name definition takes no article: ("Company"), not (the "Company"). For other common-noun defined terms, 6.63 still applies: (the "Shares").
- **R-6.64-no-parenthetical-after-possessive** [sev 3] Don't put a defined-term parenthetical after a possessive. (6.64; PDF p. 343)
- **R-6.65-no-parenthetical-in-heading** [sev 3] Don't put a defined-term parenthetical in a section heading, and don't nest parentheses inside one. (6.65; PDF p. 343)
- **R-6.68-parenthetical-at-end** [sev 1] Put the defined-term parenthetical at the end of the definition, not in the middle; mid-definition placement is usually awkward but can change meaning. (6.68, 6.69, 6.70; PDF p. 343)
  - Test: Ask whether the words after the parenthetical are meant to be part of the definition.
  - Book example: all contracts, oral or written ("Contracts"), to which Dynaco is a party → all contracts, oral or written, to which Dynaco is a party (each such contract, a "Contract")
- **R-6.71-parenthetical-not-beyond** [sev 3] Don't place a defined-term parenthetical beyond the end of the definition. (6.71; PDF p. 345)
- **R-6.72-parenthetical-money** [sev 2] For an amount of money, put the defined-term parenthetical after the description of what the amount represents, not after the amount. (6.72; PDF p. 345)
  - Book example: The purchase price for the Shares is $3 million (the "Purchase Price"). → The purchase price for the Shares (the "Purchase Price") is $3 million.
- **R-6.73-parenthetical-after-jurisdiction** [sev 3] When creating the party-name defined term for an entity, place the defined-term parenthetical after the jurisdiction reference (see 2.93). (6.73; PDF p. 345)
- **R-6.74-clarify-scope** [sev 1] If it might be unclear how far back an integrated definition goes, put in the parenthetical, just before the defined term, a reference to the pertinent noun (that litigation, the "Acme Litigation"; each such consent, a "Required Consent"). (6.74; PDF p. 345)
  - Look for: defined-term parenthetical after a long noun phrase or series with no scope-clarifying noun
  - Book example: (none) → (those documents, the "Dynaco SEC Documents")
- **R-6.75-scope-enumerated** [sev 1] If the definition consists of enumerated clauses, say so in the parenthetical: (the litigation listed in clauses (1) through (4) of this section 4(b), the "Acme Litigation"). (6.75; PDF p. 345)
- **R-6.76-collectively** [sev 1] If an integrated definition covers a whole string of nouns, you may add collectively to the parenthetical, just before the defined term and after any scope-clarifying language; if the last element is a plural noun, consider whether readers might apply collectively only to it. (6.76; PDF p. 345)
  - Book example: (none) → the Company, the Parent, and their respective subsidiaries and affiliates (collectively, the "Acme Entities")
- **R-6.77-boosting** [sev 2] You may supplement an integrated definition by adding language (generally together with) in the parenthetical, just before the defined term and after any scope language and collectively ("boosting"); don't use boosting inappropriately to add affiliates or subsidiaries to a party-name defined term. (6.77, 6.78; PDF p. 346)
  - Book example: (none) → ... and other Affiliates (collectively, together with the Company, the "Company Group")
- **R-6.79-stacking** [sev 3] You may define more than one term in one parenthetical, separated by a semicolon and each with its scope clarified ("stacking"); don't stack more than two, and you may boost the second term. (6.79, 6.80, 6.81; PDF p. 346)
- **R-6.82-integrated-part-of-speech** [sev 2] In integrated definitions, match the part of speech of the defined term to the definition, adding transition language before the defined term if needed, or restructure the provision or define the term elsewhere. (6.82, 6.83; PDF p. 347)
- **R-6.84-which-type** [sev 3] Choose between integrated and autonomous definitions partly by length: a short definition is probably more efficient as an integrated definition, a long one as an autonomous definition; also consider where you create the term. (6.84; PDF p. 347)
- **R-6.85-definition-section-heading** [sev 3] Put a definition in a definition section or on-site. A definition section lists autonomous definitions alphabetically; head it Definitions, not Glossary. (6.85, 6.86; PDF p. 348)
- **R-6.87-no-two-column-definitions** [sev 3] Don't use the Commonwealth two-column format for a definition section, or a variant that omits the definitional verb. (6.87, 6.88; PDF p. 348)
- **R-6.89-define-where-most-used** [sev 3] To define a term on-site, place the definition where the contract makes most use of the term, not merely where it is first used; put an on-site autonomous definition right after the provision that uses it. (6.89, 6.90; PDF p. 348)
- **R-6.91-section-or-onsite** [sev 3] Decide where to define a term by how far it can be understood without its definition: define entirely clear terms (SEC, ERISA, GAAP) and largely clear terms (Affiliate, Business Day) in the definition section; define custom-built terms (Equity Infusion, Excess Insurance Proceeds) on-site. (6.91, 6.92, 6.93...; PDF p. 349)
- **R-6.96-definition-section-at-back** [sev 3] Don't put the definition section at the beginning of the body; pare it down to inherently familiar terms and move it toward the back, among the miscellaneous provisions (or dispense with it and define the few terms on-site). (6.96, 6.97; PDF p. 350)
- **R-6.98-no-definitions-in-attachment** [sev 3] Don't put the definition section in an attachment. (6.98; PDF p. 350)
- **R-6.99-no-has-meaning-given** [sev 3] Avoid cross-references in the definition section to terms defined elsewhere ("Material Permits" has the meaning given that term in section 3.4). (6.99, 6.100; PDF p. 351)
- **R-6.101-index-of-definitions** [sev 3] Use an index of definitions listing all defined terms alphabetically in two columns with the page number (not section number) of each definition; call it an index of definitions, not an index of defined terms, and place it after the table of contents. (6.101, 6.102, 6.103; PDF p. 351)
- **R-6.104-index-alternatives** [sev 3] Create the index with Word's indexing feature early, not just before signing; an index at the end of the definition section listing only on-site terms is less useful. (6.104, 6.105; PDF p. 352)
- **R-6.106-no-defined-in-section-1** [sev 3] Don't say in the first section that some or all defined terms are defined in the definition section. (6.106; PDF p. 352)
- **R-6.107-no-as-defined-in** [sev 3] Don't put a cross-reference parenthetical such as (as defined in section x) after a defined term; use an index of definitions instead. (6.107, 6.108, 6.109; PDF p. 352)
- **R-6.110-definition-same-as-term** [sev 3] If the definition is the same as the defined term, supplement the definition or eliminate the defined term. (6.110; PDF p. 353)
- **R-6.111-meaning-expressed-separately** [sev 3] Eliminate a defined term whose meaning is already expressed in the sentence that uses it. (6.111, 6.112; PDF p. 353)
- **R-6.113-no-component-after-term** [sev 3] Don't follow a defined term with something that is already a component of its definition. (6.113, 6.114; PDF p. 354)
- **R-6.115-no-circular-definitions** [sev 1] Don't define term A by reference to term B and term B by reference to term A; anchor one definition to an external reality. (6.115, 6.116, 6.117; PDF p. 355)
  - Test: For each definition that uses another defined term, check whether that term's definition refers back.
  - Book example: "Bonus Date" means a date on which Acme determines that a Bonus Period concludes. / "Bonus Period" means a period that ... concludes on a Bonus Date. → (see fix)
- **R-6.118-overlapping-definitions** [sev 2] Avoid defined terms that a reader might think combine other defined terms (Licensor, Software, and Licensor Software; Control and Change of Control); usually you can choose terms that eliminate the overlap. (6.118, 6.119, 6.120; PDF p. 356)
- **R-6.121-no-improvised-definitions** [sev 3] Use autonomous and integrated definitions, not improvised alternatives. (6.121; PDF p. 356)
- **R-6.122-defined-not-used** [sev 2] As you revise, check that no defined term is defined but not used, or used but not defined; technology can help. (6.122; PDF p. 357)
  - Test: List every defined term; search for each one's uses; list every capitalized term in use and confirm it is defined.
- **R-6.123-value-exceeds-cost** [sev 3] Weigh each defined term's benefit (the economy it offers and how often it is used) against its cost (breaks in the text, parenthetical clutter, capitals, and the mental link to the definition); a short definition needs frequent use to justify a defined term. (6.123, 6.124, 6.125...; PDF p. 357)
- **R-6.131-no-dictionary-provisions** [sev 2] Don't rely on provisions that tie meaning to a dictionary, whether general (Oxford English Dictionary) or for a specific term (disparage). (6.131, 6.132, 6.133...; PDF p. 358)
- **R-6.135-no-herein-so-called** [sev 3] Don't use herein so called; it serves no evident purpose. (6.135, 6.136, 6.137; PDF p. 359)

### Chapter 6: Blog: An Exception to the Rule Against Also Stating Without Initial Capitals

- **R-rider-lowercase-party-noun** [sev 3] Exception to the rule that every instance of a defined term takes initial capitals: if a common noun is the defined term for a party (Company, Lender), you may also use that word without initial capitals in its ordinary sense. (6.10, 6.11; rider)

### Chapter 13: Selected Usages

- **R-13.215-potential-default** [sev 3] In the paired defined terms Default (a latent event of default) and Event of Default, use Potential Default and Default instead; the traditional pair look the same and don't signal their definitions. Don't use Incipient Event of Default. (13.215, 13.219, 13.220...; PDF p. 626)
- **R-13.227-default-event** [sev 3] If you won't shorten event of default to default, say default event, which is more concise. (13.227; PDF p. 628)
- **R-13.313-avoidance-of-doubt-definition** [sev 3] Where for the avoidance of doubt adds a second sentence to a definition, restructure the definition as a single sentence. (13.313; PDF p. 648)
- **R-13.379-including-specialized-word** [sev 2] If the general word has a specialized meaning (different from everyday use, or created by the contract, such as excluded liabilities), don't use including; provide an exhaustive list, perhaps as a definition with the noun as the defined term. In any event, select the general word with care; the more specific it is, the less mischief including can cause. (13.379, 13.380; PDF p. 663)
  - Look for: including after a term the contract itself creates
  - Fix: exhaustive definition ('Excluded Liabilities' means ...)
- **R-13.448-losses-and-liabilities** [sev 2] Address directly whether indemnification covers only losses paid or also liabilities incurred: have the indemnifying party indemnify against both losses and liabilities, or better, use a defined term (Indemnifiable Losses or a variant) that states exactly what is covered, for example including judgments so the indemnified party needn't pay a judgment first; address litigation expenses in the procedure provisions. (13.448, 13.449, 13.450; PDF p. 678)
  - Look for: indemnification provision that relies on hold harmless to cover incurred liabilities
  - Fix: Define Indemnifiable Losses to state what is covered (including judgments).
- **R-13.506-define-knowledge** [sev 2] Consider making Knowledge a defined term to address whose knowledge counts (narrow for the stating party, broad for the other) and the level of knowledge (actual knowledge, or knowledge after inquiry of specified employees or after reasonable investigation, using knows or should have known). In a sale of a business, consider whether to include its managers. Avoid reasonable knowledge as unclear. (13.506, 13.507, 13.508...; PDF p. 692)
  - HOUSE: partly superseded: Never should: define Knowledge with wording for actual knowledge and for knowledge after reasonable inquiry, not should have known. See house-style.md section 12.
  - Fix: Autonomous definition of Knowledge naming the individuals and the level of investigation.
- **R-13.509-rule-405** [sev 3] Use a rule 405 (Securities Act) reference to define executive officers in a knowledge definition only if the party benefiting from the qualification is a U.S. public company. (13.509; PDF p. 694)
- **R-13.694-units-of-product** [sev 2] Use the defined term Product for a product line and refer to units of the Product for individual samples; Product alone is ambiguous between the two. (13.694; PDF p. 737)
  - Fix: units of the Product
- **R-13.695-proprietary** [sev 2] Don't use proprietary in defining Confidential Information: proprietary information sweeps in nonconfidential information, and proprietary and confidential excludes confidential information that isn't proprietary (such as information a third person disclosed under a confidentiality agreement). (13.695, 13.696, 13.697; PDF p. 737)
  - Fix: confidential

### Chapter 15: Internal Rules of Interpretation

- **R-15.5-autonomous-definitions-placement** [sev 3] Put autonomous definitions in the definition section, if the contract has one, not among the internal rules of interpretation. (15.5; PDF p. 821)
