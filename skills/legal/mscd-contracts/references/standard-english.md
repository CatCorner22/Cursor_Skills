# Standard English, writing, and typography

Aim for a specialized version of standard English: the English of educated native speakers (1.30-1.32). Apply house style first (`house-style.md`): digits for every number, U.S. dates, 2 spaces between sentences and 1 after a colon, 12-point Aptos, singular *they*, clean visual lines.

Key MSCD rules that still apply: split long sentences and keep subject, verb, and object together (17.2-17.6); unbury verbs (17.7-17.9); write gender-neutral text (17.11-17.18); use the plain alternatives in the 36-pair table at 17.19; use possessives (17.28); capitalize per *Chicago* (17.29-17.35, except attachment references, which take capitals under house style); no contractions (17.37); punctuate by standard English without making meaning depend on punctuation (17.38); the serial comma (12.59); the subjunctive only where modern usage keeps it (3.34-3.40); third person (3.10-3.12).

> **Book examples are in MSCD5's style, not house style.** They may use lowercase *schedule*, *1 January 2024*, spelled-out numbers, 1.1 numbering, *the* before party names, or a passive that MSCD accepts. Restate any example in house style (`house-style.md`) before you put it in a contract or a comment. For the other side's drafts, the house rule is to flag everything, whatever a rule's "let-pass" or "style-only" label says.


## Rules (70, generated from `data/rules.jsonl`)

Format: id, severity (1 = ambiguity or meaning-changing; 2 = vagueness or dispute risk; 3 = style), the rule, and its MSCD paragraphs and PDF page. `HOUSE` marks a rule that Blake's house style changes: apply the house rule. For a rule's full record (test, fix, exceptions, verified book examples), run `python3 scripts/rules_query.py --id <id>`.


### Blog: No Ampersands in Contracts!

- **R-rider-ampersand** [sev 3] Don't use an ampersand except where it appears in the name of a business or law firm; write and. In a heading, use a semicolon (Amendment; Waiver) or make separate sections. (Introduction; rider)

### Chapter 1: Contract Language Shouldn't Be Legalistic

- **R-1.30-standard-english** [sev 3] Write in a specialized version of standard English, the English used by educated native speakers, free of usages that gratuitously interfere with understanding. (1.30, 1.31, 1.32; PDF p. 66)

### Chapter 1: Contract Language Shouldn't Seek to Persuade

- **R-1.67-no-typographic-emphasis** [sev 3] Don't use typography (bold, italics, all capitals, underlining) for rhetorical emphasis. (1.67; PDF p. 75)

### Chapter 2: The Introductory Clause

- **R-2.47-between** [sev 3] Say the contract is between the parties, however many there are; don't use among or by and between. (2.47, 2.48, 2.49; PDF p. 87)

### Chapter 2: Defined Terms for Party Names

- **R-2.96-no-emphasis-party-terms** [sev 3] Don't use all capitals or other emphasis for party-name defined terms throughout the contract. (2.96; PDF p. 96)

### Chapter 3: General Considerations

- **R-3.38-no-subjunctive-conditions** [sev 3] Don't use the subjunctive in ordinary conditions; it's archaic. Use the indicative. (3.34, 3.35, 3.36...; PDF p. 136)
- **R-3.39-keep-subjunctive-demands** [sev 3] Keep the subjunctive where the clause expresses a demand or suggestion, even inside a conditional clause (requires that Widgetco pay; recommends that the Employee retain). (3.39, 3.40; PDF p. 136)

### Chapter 5: Back of the Contract

- **R-5.95-in-not-on-schedule** [sev 3] Say in schedule X, not on schedule X. (5.95; PDF p. 324)

### Chapter 6: Blog: An Exception to the Rule Against Also Stating Without Initial Capitals

- **R-rider-lowercase-party-noun** [sev 3] Exception to the rule that every instance of a defined term takes initial capitals: if a common noun is the defined term for a party (Company, Lender), you may also use that word without initial capitals in its ordinary sense. (6.10, 6.11; rider)

### Chapter 6: Defined Terms

- **R-6.15-a-or-an-abbreviation** [sev 3] Before an abbreviation used as a common noun, choose a or an by the sound of its first syllable, go with the pronunciation you and your colleagues use, and apply it consistently throughout the contract. (6.15; PDF p. 334)

### Chapter 10: Blog: Revisiting "Date" and "Day"

- **R-rider-date-day** [sev 3] Use date for the point on a calendar that a given day occupies and day for a unit of time; but because using date for day can't cause confusion, don't insist on either. Closing date is fine; don't change closing day to closing date either. (10.15, 10.16; elaboration)

### Chapter 12: Syntactic Ambiguity

- **R-12.44-restrictive-def** [sev 2] A restrictive clause gives essential, distinguishing information (The cakes that George baked were delicious); a nonrestrictive clause gives a supplemental aside (The cakes, which George baked, were delicious). Usage authorities recommend that for restrictive clauses and comma-which for nonrestrictive ones. (12.44, 12.45, 12.46; PDF p. 564)
- **R-12.47-which-that-ambiguity** [sev 1] Restrictive-versus-nonrestrictive ambiguity: when drafters blur that and which (which in restrictive clauses, comma-which used for that, dropped commas before which), a relative clause can be read as limiting the noun or as an aside (all Contracts other than Assumed Contracts which are subject to section 4.3). (12.47, 12.48, 12.49...; PDF p. 564)
  - Look for: which introducing a relative clause, with or without a preceding comma
  - Test: Ask whether the clause is meant to narrow the noun (restrictive) or merely add information (nonrestrictive), and whether a reader could take it the other way.
  - Fix: Use that for restrictive clauses; don't use nonrestrictive clauses; if the noun the clause modifies is unclear, use parentheses around any intervening phrase.
  - Book example: There is no fact known to any Credit Agreement Party or any of its Subsidiaries which has had, or could reasonably be expected to have, a Material Adverse Effect. → There is no fact known to any Credit Agreement Party or any of its Subsidiaries that has had, or could reasonably be expected to have, a Material Adverse Effect.
- **R-12.53-no-nonrestrictive** [sev 1] Don't use nonrestrictive clauses in contracts; either tackle an issue head-on or omit it. (12.53, 12.54, 12.55; PDF p. 566)
- **R-12.56-that-not-which** [sev 1] Use that, not which, in restrictive clauses. (12.56; PDF p. 566)
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

### Chapter 13: Selected Usages

- **R-13.71-at-least-one-of** [sev 2] Use at least one of X and Y (with and), never at least one of X or Y; or say one or more of X and Y, which is simpler. Courts and drafters should ignore SuperGuide's suggestion that or changes the result. (13.71, 13.81, 13.85...; PDF p. 594)
  - Look for: at least one of / one or more of followed by a list joined by or
  - Test: Is the list after at least one of joined by or? If so, change or to and.
  - Fix: at least one of X, Y, and Z; one or more of X, Y, and Z
- **R-13.107-between-or-among** [sev 3] Instead of between or among, use just between; there is no basis in English usage for reserving between for two and among for more than two. To avoid any confusion about contracts between the parties, say agreements between two or more of the parties. (13.107, 13.108; PDF p. 603)
- **R-13.129-the-closing** [sev 3] When closing means the moment a transaction is consummated, it is a gerundial noun; use it with the definite article (on or before the Closing). (13.129, 13.130, 13.137...; PDF p. 607)
- **R-13.514-latinisms** [sev 3] Omit Latinisms, including those the book lists from EDGAR contracts, and express the meaning in standard English. (13.514, 13.515; PDF p. 695)
- **R-13.608-no-later-than** [sev 3] Use no later than (not not later than), no earlier than, and no more than; they are less formal and more natural. (13.608, 13.609, 13.610; PDF p. 716)
- **R-13.611-not-less-than** [sev 3] Use not less than, not no less than; no less connotes surprise, while not less is matter-of-fact. (13.611, 13.612; PDF p. 717)
- **R-13.628-days-notice-apostrophe** [sev 3] When referring to prior notice, use an apostrophe with the period of time: one week's notice, five days' notice. (13.628; PDF p. 721)
- **R-13.629-notify-sense** [sev 3] Use notify in the sense 'to inform someone' (Acme shall promptly notify Widgetco of any Security Incident), not the English sense 'to make known' (notify any Security Incident to Widgetco). (13.629, 13.630; PDF p. 721)
- **R-13.649-only-placement** [sev 2] Place only immediately before the words it is meant to limit, not by reflex before the verb; the farther it sits from its correct position, the greater the risk of ambiguity. (13.649, 13.650, 13.651...; PDF p. 726)
  - Test: Which words does only limit? Move it immediately before them.
  - Fix: The Tenant may move furniture ... only during nonbusiness hours
  - Book example: The Tenant may only move furniture ... during nonbusiness hours → The Tenant may move furniture, fixtures, and equipment into and out of the Premises only during nonbusiness hours unless Landlord gives approval otherwise
- **R-13.662-parentheses** [sev 3] Don't use parentheses for explanations or asides. Use them to eliminate syntactic ambiguity, with enumeration, to create a defined term after an integrated definition, for paired alternative arrangements that apply in different circumstances, and for two alternative scenarios of even modest complexity instead of delimiting commas. (13.662, 13.663, 13.664; PDF p. 730)
- **R-13.665-parentheses-within-words** [sev 3] Don't use parentheses within a word, such as (s) on a singular noun (say one or more), (sub)licensee, (sub)contractor, (self)insured, or (s)he. (13.665, 13.666; PDF p. 731)
- **R-13.763-setoff** [sev 3] The nouns setoff and offset mean the same thing, as do the verbs set off and offset; pick one noun, use it consistently with the corresponding verb, and spell the noun setoff (not set-off or set off) and the verb set off (two words). (13.763, 13.764, 13.765...; PDF p. 754)
- **R-13.862-earlier-of-x-and-y** [sev 2] Use and between the alternatives (the later of (1) ... and (2) ...); you are selecting one item from a group. With three or more items, use earliest, latest, greatest, or least. (13.862, 13.863, 13.864...; PDF p. 776)
  - Look for: the earlier/later/greater/lesser of ... or ...
  - Fix: the later of (1) ... and (2) ...
- **R-13.903-trademark-references** [sev 3] Drop the registration symbol in contracts. In trademark license agreements and other contracts about rights in a trademark, use all capitals for that trademark; where a trademark simply identifies goods or services, use initial capitals. (13.903, 13.906, 13.907...; PDF p. 784)
- **R-13.904-trademark-guidelines** [sev 3] If your client has strict rules on referring to its trademarks (all capitals and the symbol every time), follow them even if they add clutter, but use judicious defined terms (the Licensed Mark; the Product) to limit references to the trademark. (13.904, 13.916, 13.917; PDF p. 785)
- **R-13.910-registration-symbol** [sev 3] Contracts can drop the registration symbol: they aren't disseminated publicly, and a party is unlikely to need notice in a contract for Lanham Act recovery (15 U.S.C. s. 1111). A concerned owner should address unauthorized use expressly. (13.910, 13.911, 13.912...; PDF p. 786)
- **R-13.927-virgule** [sev 2] Don't use the virgule (forward slash) in contracts other than to state a fraction; writers use it for per, or, and, or a vague disjunction, and there is almost always a better choice. (13.927, 13.928; PDF p. 790)
  - Look for: slash between words
  - Fix: or; and; per; one or more of

### Chapter 16: Typography

- **R-16.2-fonts** [sev 3] Unless you are subject to institutional requirements, be open to alternatives to the default fonts; Times New Roman (designed for narrow newspaper columns) and Arial are overexposed and criticized, and Calibri and Constantia were designed for screen reading. (16.2, 16.4, 16.5...; PDF p. 826)
- **R-16.9-system-fonts** [sev 3] Use system fonts rather than purchased professional fonts; an unrecognized font displays in a fallback font, which disrupts signature-page exchanges and negotiations. For law firms and law departments you can assume Microsoft Office fonts. (16.9, 16.10, 16.11...; PDF p. 829)
- **R-16.13-serif-optional** [sev 3] There is no requirement to use a serif font; studies cast doubt on the assumption that serif fonts are easier to read. (16.13, 16.14; PDF p. 830)
- **R-16.15-ragged-right** [sev 3] Don't justify the margins of word-processed contracts; use ragged-right (flush-left) text. Word processors lack the spacing and hyphenation algorithms to make justified text readable; the professional look is a phony professionalism. (16.15, 16.16, 16.17; PDF p. 830)
- **R-16.18-caps-headings-names** [sev 3] Use all capitals for article headings and for party names in the introductory clause and signature blocks; don't use all capitals for continuous body text. (16.18, 16.19; PDF p. 831)
- **R-16.20-bold-headings-defined-terms** [sev 3] Bold all section headings and each defined term where it is defined; don't use underlining for emphasis (a typewriter convention that overlaps descenders). (16.20, 16.21; PDF p. 834)
- **R-16.22-no-emphasis-cross-refs** [sev 3] Don't emphasize cross-references or references to attachments; it doesn't help the reader, and Word's find-and-replace is quicker and more reliable for checking them. (16.22; PDF p. 834)
- **R-16.23-emphasize-provisions** [sev 2] Don't emphasize any part of the provisions unless a statute or caselaw requires it (for example, statutes requiring capitals or 'conspicuous' text, such as UCC s. 2-316(2) for disclaimers of the implied warranty of merchantability), or unless you're counterbalancing a substantial disparity of bargaining power or sophistication. A provision needn't be emphasized to be conspicuous. (16.23, 16.24, 16.25...; PDF p. 835)
  - Look for: emphasized provisions in the body
  - Fix: Emphasize only where law requires or bargaining power is unequal.
- **R-16.28-jury-waiver-conspicuous** [sev 2] Jury-trial-waiver caselaw on conspicuousness is inconsistent; unless you can research it, make jury-trial waivers conspicuous regardless of the governing law. (16.28; PDF p. 836)
  - Fix: Set the waiver off with bold italics and/or a border.
- **R-16.29-how-to-emphasize** [sev 3] Unless a statute requires it, don't use all capitals to emphasize a provision; readers skim capitals and they may not even be conspicuous. Use bold italics and/or a border instead (also for stock-certificate legends), and don't use italics for emphasis, except perhaps in amendments. (16.29, 16.30, 16.31...; PDF p. 836)
- **R-16.34-conspicuous-acknowledgment** [sev 2] Don't rely on an acknowledgment that text is conspicuous; it sits inside the provision, so if the provision is inconspicuous, so is the acknowledgment. (16.34, 16.35; PDF p. 837)
  - Fix: Make the provision conspicuous instead.
- **R-16.36-rhetorical-typography** [sev 3] Don't emphasize selected words for rhetorical emphasis (The Licensor shall NOT indemnify ...). (16.36; PDF p. 838)
- **R-16.37-font-size** [sev 3] Font size depends on the typeface: 12 point Times New Roman and 10 point Arial are standard; 11-point Calibri is a safe choice, but you can experiment. Different sizes apply with a two-column format. (16.37, 16.38; PDF p. 838)
  - HOUSE: 12-point Aptos. See house-style.md section 9.
- **R-16.39-line-length** [sev 3] Keep line length within the recommended 45 to 90 characters; the simplest fix is 1.5- to 2-inch side margins, though keeping blocks of text short mitigates long lines. (16.39, 16.40, 16.41; PDF p. 840)
- **R-16.42-line-spacing** [sev 3] Single spacing has been standard; consider experimenting with extra space (Typography for Lawyers recommends Word's Multiple at 1.03 to 1.24). (16.42, 16.43; PDF p. 841)
- **R-16.44-one-space** [sev 3] Use one space, not two, after periods, question marks, exclamation marks, and colons. (16.44, 16.45, 16.46; PDF p. 842)
  - HOUSE: 2 spaces after sentence-ending punctuation within a paragraph; 1 space after a colon. See house-style.md section 5.
- **R-16.47-curly-quotes** [sev 3] Make all quotation marks and apostrophes curly; mixed marks are a hallmark of a sloppy copy-and-paste job. Turn on Word's AutoFormat As You Type replacement and convert straight marks with Find and Replace. (16.47, 16.49, 16.50...; PDF p. 842)
- **R-16.54-first-line-indents** [sev 3] Don't use both first-line indents and space between paragraphs; the manual's samples use no first-line indents. (16.54, 16.55; PDF p. 843)

### Chapter 17: Drafting as Writing

- **R-17.2-sentence-length** [sev 3] Whittle down unnecessarily long sentences (contract sentences will usually exceed 20-25 words): a sentence is too long if it strings together clauses that would read better separately or includes unwieldy exceptions, qualifications, or conditions. Break it into components, state how they relate, and tabulate long lists of enumerated clauses. (17.2, 17.3, 17.4...; PDF p. 845)
- **R-17.6-subject-verb-object** [sev 3] Keep subject, verb, and object close together and, if possible, at the start of the sentence; move intervening words to the beginning or end, or into a separate sentence. (17.6; PDF p. 847)
- **R-17.7-buried-verbs** [sev 3] Whenever possible, use strong verbs instead of abstract nouns (buried verbs, nominalizations) or adjectives; they make prose bureaucratic, add prepositions and weak verbs, and let the drafter drop the actor. (17.7, 17.8, 17.9; PDF p. 847)
- **R-17.10-buried-verb-exception** [sev 3] Like the passive, a buried verb is useful when dropping the actor helps: Upon exercise of the Option rather than When one or more Optionholders exercise the Option. (17.10; PDF p. 849)
- **R-17.11-gender-neutral** [sev 2] For a group that includes or might include women and men, don't use exclusively he, his, him. Use a plural pronoun with conforming changes, repeat the noun, or add a feminine or neuter pronoun or both; singular they is acceptable but each drafter decides. Don't use singular they for a member of a group made up only of entities (use it), and be accurate however you handle pronouns. (17.11, 17.12, 17.13...; PDF p. 849)
  - HOUSE: partly superseded: Singular they is acceptable and preferred for an individual of unspecified gender; the rest of 17.11-17.18 applies.
  - Fix: The Stockholders must surrender their stock certificates; Each Stockholder must surrender that Stockholder's stock certificate; his, her, or its
  - Book example: Each Stockholder must surrender his stock certificates → The Stockholders must surrender their stock certificates
- **R-17.19-wordy-phrases** [sev 3] Replace wordy phrases with simpler ones: prior to -> before; subsequent to -> after; in lieu of -> instead of; in the event that / in the event of -> if; pursuant to -> under, in accordance with, authorized by; set forth in -> stated in, in; until such time as -> until; in order to -> to; for the purpose of [verb]ing -> to [verb]; by reason of -> because of; due to the fact that -> because; despite the fact that -> although; is unable to -> cannot; is binding upon -> binds; per annum -> a year; with the exception of -> except for; and the other entries in the 17.19 table. (17.19, 17.20; PDF p. 851)
- **R-17.21-to-the-extent-that** [sev 2] Use to the extent that only when the degree of application depends on a variable (except to the extent that the federal securities laws apply); use if when satisfying a condition applies the provision in full. (17.21; PDF p. 852)
  - Test: Does the provision apply partly, in proportion to a variable? If it applies fully once the condition is met, use if.
  - Fix: If any document is required to be filed ..., the Seller shall prepare and sign that document.
  - Book example: To the extent that any document is required to be filed → If any document is required to be filed
- **R-17.22-the-fact-that** [sev 3] The fact that can almost always be improved (by virtue of the fact that -> because; The fact that there may be no Loans outstanding -> Whether any Loans are outstanding); notwithstanding the fact that and regardless of the fact that can always be replaced by although, even though, or even if. (17.22, 17.23; PDF p. 852)
- **R-17.24-there-is-there-are** [sev 3] Don't start a clause with there or it plus a form of to be; find the real subject and verb. (17.24; PDF p. 853)
- **R-17.25-with-respect-to** [sev 3] Replace with respect to with regarding or a single preposition (in, for, on), a shorter phrase (as to), or a bigger fix (a Fund's Borrowing Instructions). (17.25, 17.26, 17.27; PDF p. 854)
- **R-17.28-possessives** [sev 3] Use possessives to make prose less wooden: Acme's board of directors; Smith's shares; the Lender's obligation to make Loans under this agreement. (17.28; PDF p. 854)
- **R-17.29-initial-capitals** [sev 3] Be restrained with initial capitals (following The Chicago Manual of Style): use lowercase for a particular contract unless it is a defined term, board of directors, officer and other titles (the president of Acme), organizational documents (certificate of incorporation, bylaws), capital stock (common stock), and article and section cross-references and references to exhibits, schedules, and other attachments. (17.29, 17.30, 17.31...; PDF p. 855)
  - HOUSE: partly superseded: Capitalize attachment references (Schedule A, Exhibit 1); the rest of MSCD's restraint with initial capitals applies.
- **R-17.36-extraneous-the** [sev 3] Drop the before abstract nouns where it is extraneous (upon satisfaction; for purposes of calculating; caused by willful misconduct). (17.36; PDF p. 856)
- **R-17.37-contractions** [sev 3] Don't use contractions in business contracts; contract prose is devoid of tone and rhythm. (17.37; PDF p. 856)
- **R-17.38-punctuation** [sev 2] Use punctuation consistent with standard English without relying on it unduly. If a contract says punctuation is for ease of reference only and does not affect interpretation, insist that the provision be deleted. (17.38; PDF p. 857)
  - Fix: Delete the punctuation-disclaimer provision.
