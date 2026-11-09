# Attachments: schedules and exhibits

Blake asked for the schedule-versus-exhibit check on every contract. Run it on every contract, in every mode.

## Decision procedure for each attachment

1. **Classify it** (5.72-5.73):
   - **Exhibit**: a stand-alone document, such as a form of agreement, certificate, note, or organizational document, often one that a party signs or delivers. A document with its own signature blocks (a signed order form) is a stand-alone document: label it Exhibit, even when the draft calls it Schedule A (house rule 6; Blake's decision).
   - **Schedule**: information that could have been in the body but the drafter moved out because it is long, or because other people prepare it on another timetable: lists, disclosure items, specifications, pricing, addresses.
   - If an attachment carries the wrong label, relabel it and update every reference.
2. **Order** (5.75-5.76): signatures, then all schedules, then all exhibits.
3. **Enumerate** (house rule 6; MSCD 5.80-5.83 differs): schedules by letter (*Schedule A, Schedule B*) and exhibits by number (*Exhibit 1, Exhibit 2*), so no schedule and exhibit share a designation. Relabel any other system, even a consistent one, and update every reference.
4. **References** (5.77-5.79, 5.95; house rule 6): *Schedule A*, *Exhibit 2*, capitalized; no *hereto*, no *to this agreement*, no *attached hereto*; no quotation marks around the letter or number; no bold, italics, or underlining. Say *in Schedule A*, not *on Schedule A*.
5. **Don't say an attachment "forms part of" the contract** (5.96-5.99): a reference in the body is enough. Exception: a self-contained schedule the body never mentions (5.100).
6. **Keep operative provisions in the body** (5.92-5.93): an obligation, condition, or remedy in a schedule is easy to miss. Move it to the body. Move it into the body section that refers to the schedule: a new last sentence, or a new last subsection when that section already has subsections (no only child). A provision no section refers to goes at the end of the body (MSCD 5.93). In a redline, track the deletion and the insertion, and say so in 1 comment. Standardized provisions that nobody negotiates may stay in a schedule (5.94): flag the choice; don't move them.
7. **Disclosure schedules**: link each disclosure to the provision it qualifies (5.86). Delete references to empty schedules (5.91).
8. **Virtual attachments** (a document at a web address): say the document is part of the contract and fix its version (5.102-5.105).

## Contingencies

- With only a few attachments, MSCD allows a single generic term (5.74). Blake wants the distinction always; apply it.
- Other jurisdictions use other terms (Australia: *annexure*), 5.73. House rule 6 applies under any governing law: relabel to *Schedule A* and *Exhibit 1*, and update every reference. Only a label that a statute or court rule requires stays (precedence 2), with a comment. Under non-U.S. law, the house rules all still apply; what changes is MSCD's own advice that turns on the governing law (*represents and warrants*, 3.416-3.450; efforts, 8.50-8.63; *calendar month*, 10.102).

> **Book examples are in MSCD5's style, not house style.** They may use lowercase *schedule*, *1 January 2024*, spelled-out numbers, 1.1 numbering, *the* before party names, or a passive that MSCD accepts. Restate any example in house style (`house-style.md`) before you put it in a contract or a comment. For the other side's drafts, the house rule is to flag everything, whatever a rule's "let-pass" or "style-only" label says.


## Rules (29, generated from `data/rules.jsonl`)

Format: id, severity (1 = ambiguity or meaning-changing; 2 = vagueness or dispute risk; 3 = style), the rule, and its MSCD paragraphs and PDF page. `HOUSE` marks a rule that Blake's house style changes: apply the house rule. For a rule's full record (test, fix, exceptions, verified book examples), run `python3 scripts/rules_query.py --id <id>`.


### Chapter 2: The Introductory Clause

- **R-2.64-lists-of-parties** [sev 3] When there are too many parties to list, refer to them collectively, for example the financial institutions listed as Lenders on the signature pages of this agreement, or those listed in a schedule if you also need their addresses or other information. (2.64, 2.65, 2.66; PDF p. 91)

### Chapter 2: The Defined Term This Agreement

- **R-2.126-no-agreement-includes-attachments** [sev 3] Don't define this agreement to include its attachments; mentioning an attachment in a provision brings it within the contract. (2.126; PDF p. 104)

### Chapter 4: Layout

- **R-4.114-attachment-page-numbering** [sev 3] For multiple attachments, number pages either consecutively (as one document, where Page x of y is more useful) or nonconsecutively (each attachment separately, for example C-5); choose for the transaction, and don't use both in one set. (4.114, 4.115, 4.116; PDF p. 299)
  - Exceptions: C-5 style numbering is awkward if attachments are enumerated by section number (5.81).

### Chapter 5: Back of the Contract

- **R-5.72-exhibit-vs-schedule** [sev 2] Follow the prevailing U.S. convention: call a stand-alone document an exhibit, and call information that could have been in the body a schedule. (5.72, 5.73; PDF p. 319)
  - HOUSE: partly superseded: House rule 6: a document with its own signature blocks is a stand-alone document: label it Exhibit, even when the draft calls it Schedule A (Blake's decision). See house-style.md section 6.
  - Test: Ask whether the attachment is a stand-alone document (exhibit) or information that could have been in the body (schedule).
  - Exceptions: Other jurisdictions differ (Australia uses annexure for stand-alone documents).
- **R-5.74-generic-attachment-term** [sev 3] With only a few attachments, don't feel bound by the exhibit/schedule distinction; a generic term (appendix, annex, attachment) works, and four attachments beats three exhibits and one schedule. (5.74; PDF p. 319)
- **R-5.75-schedules-before-exhibits** [sev 3] Put schedules before exhibits, and place attachments after the signatures (U.S. convention). (5.75, 5.76; PDF p. 319)
- **R-5.77-no-hereto-attachments** [sev 3] Don't use hereto or to this agreement in references to attachments, alone or after attached. (5.77; PDF p. 320)
- **R-5.78-no-emphasis-attachment-refs** [sev 3] Don't emphasize references to attachments (italics, bold, underlining), don't put the enumeration in quotation marks (exhibit "A"), and don't use initial capitals (use exhibit A, schedule 3.2). (5.78, 5.79; PDF p. 320)
  - HOUSE: partly superseded: Capitalize attachment references (Schedule A, Exhibit 2); the rest of 5.78 (no emphasis, no quotation marks around the enumeration) still applies. See house-style.md section 6.
- **R-5.80-enumerate-attachments** [sev 3] Enumerate attachments sequentially (1, 2, 3 or A, B, C) or by the number of the section they relate to; use section-number enumeration mainly in contracts with articles and multiple numeration. (5.80, 5.81, 5.82; PDF p. 320)
  - HOUSE: House rule 6: schedules take letters (Schedule A, Schedule B) and exhibits take numbers (Exhibit 1, Exhibit 2), so no schedule and exhibit share a designation; relabel any other system and update every reference.
- **R-5.83-hybrid-attachment-enumeration** [sev 3] Consider a hybrid: enumerate schedules by section number and exhibits by consecutive letters, so schedule 3.2 can't be confused with exhibit 3.2. (5.83; PDF p. 321)
  - HOUSE: House rule 6: schedules take letters (Schedule A, Schedule B) and exhibits take numbers (Exhibit 1, Exhibit 2), so no schedule and exhibit share a designation; relabel any other system and update every reference.
- **R-5.84-exhibit-def** [sev 3] An exhibit is a stand-alone document, either currently in effect (for example, organizational documents) or a form to be signed later (for example, an employment agreement to be signed at closing). (5.84; PDF p. 322)
- **R-5.85-schedule-def** [sev 3] A schedule holds material that could be in the body but is placed after it, such as a list of parties or banking information. (5.85; PDF p. 322)
- **R-5.86-link-disclosure-schedule** [sev 2] Link each disclosure schedule to its provision by saying that schedule X states (or lists) all instances of the thing at issue; alternatively, say that other than as stated in schedule X there are no such instances, when the thing is undesirable or present in limited quantities. (5.86; PDF p. 322)
- **R-5.87-disclosure-schedule-reasons** [sev 3] Use disclosure schedules for volume, because the party collecting the information often isn't the drafter, because collection runs on a different process and timetable, and for sensitivity (schedules can be omitted from circulated drafts and, under Regulation S-K Item 601(b)(2), often from merger-agreement filings). (5.87, 5.88, 5.89...; PDF p. 323)
- **R-5.91-no-none-schedule** [sev 3] If no scheduled information turns out to be needed, delete the reference rather than send readers to a schedule saying None or Not applicable. (5.91; PDF p. 323)
- **R-5.92-effect-provisions-in-body** [sev 3] Put provisions governing the effect of disclosure schedules in the body, not on a cover sheet to the schedules. (5.92; PDF p. 323)
  - Look for: cover sheet to disclosure schedules stating how disclosures qualify statements of fact
- **R-5.93-no-sections-in-schedules** [sev 2] Don't place contract sections in a schedule, especially contentious provisions (burying) or ostensibly routine ones. (5.93, 5.94; PDF p. 323)
  - Exceptions: Relegating standardized, non-negotiable provisions to a schedule is sometimes simplest (5.94). | Some drafters put especially sensitive terms, such as pricing, in a schedule to limit disclosure (5.94). | Don't put the definition section in a pull-out schedule; handle definitions so it is unnecessary (5.94, 6.89-.98).
- **R-5.95-in-not-on-schedule** [sev 3] Say in schedule X, not on schedule X. (5.95; PDF p. 324)
- **R-5.96-dont-say-part-of** [sev 3] Don't state that attachments are part of the contract. (5.96, 5.97, 5.98...; PDF p. 324)
  - Book example: All exhibits and schedules annexed hereto are expressly made a part of this agreement as though fully set forth herein. → (see fix)
- **R-5.100-part-of-self-contained-schedules** [sev 1] If schedules hold self-contained sets of provisions (some master-agreement structures) and the body doesn't otherwise mention them, state in the body that they are part of the contract. (5.100; PDF p. 325)
  - Look for: schedule of terms that the body never refers to
- **R-5.101-virtual-attachment-def** [sev 3] A "virtual attachment" is an ancillary document made part of a contract without being physically attached, such as an employee handbook or a web page of general terms. (5.101; PDF p. 325)
- **R-5.102-virtual-say-part** [sev 1] Say expressly that a virtual attachment is part of the contract. (5.102; PDF p. 326)
  - Look for: contract that refers to a handbook, policy, or web page of terms without saying it is part of the contract
  - Fix: State that the [document] is part of this agreement.
- **R-5.103-virtual-not-subject-to** [sev 1] Don't say the contract is subject to a virtual attachment, and don't merely say where it can be found (for example, on a specified web page). (5.103; PDF p. 326)
- **R-5.104-virtual-not-via-definition** [sev 1] Be cautious about using a definition to bring in a virtual attachment (for example, "Support Services" means services described at a website at any given time). (5.104, 5.105; PDF p. 326)
  - Look for: definition pointing to terms on a website "at any given time" or "as updated from time to time"
  - Book example: "Support Services" means Product support services described in the description of support services provided at the Acme Licenses website (http://www.acme.com/licenses) at any given time. → (see fix)
- **R-5.106-virtual-unilateral-amendment** [sev 2] Whether a party may unilaterally amend a virtual attachment, and whether and how it must notify the other party, are contentious issues outside MSCD's scope; address them deliberately. (5.106; PDF p. 326)
- **R-5.116-end-after-attachments** [sev 3] Rather than End of Agreement after attachments, number the pages of the whole set of attachments Page x of y and identify the kind of attachment in a header or footer on every page. (5.116, 5.117; PDF p. 329)

### Chapter 6: Defined Terms

- **R-6.98-no-definitions-in-attachment** [sev 3] Don't put the definition section in an attachment. (6.98; PDF p. 350)

### Chapter 13: Selected Usages

- **R-13.311-attach-the-form** [sev 2] Best, attach the document as an exhibit and require it to be in that form or, for flexibility, in a form substantially similar to the exhibit; this avoids preclosing haggling. (13.311; PDF p. 647)
  - Look for: closing deliverable described only by a satisfaction standard
  - Fix: in the form of exhibit X / in a form substantially similar to exhibit X
  - Exceptions: If the document relates to a future transaction whose terms are unknown, an exhibit may not be feasible (13.311).
- **R-13.408-incorporated-by-reference** [sev 2] Don't use incorporated by reference in a contract. Stating that schedules or exhibits are incorporated herein by reference accomplishes nothing (a reference in the body brings them in); saying one contract incorporates another because both are parts of one transaction is redundant and can have unexpected effects; and a contract can be subject to another contract's provision without incorporating it. (13.408, 13.409, 13.410...; PDF p. 670)
  - Fix: Delete; refer to the schedule in the body; state the interplay between the contracts.
