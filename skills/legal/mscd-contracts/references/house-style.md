# Blake's house style

These rules come from Blake Reagan, the user. They override MSCD5 and Adams's blog wherever they conflict, because Blake's own rules come first in the precedence list. Where a house rule is silent, MSCD5 as updated by the riders governs. `data/house-overrides.json` lists every rule-database record a house rule supersedes; `scripts/mscd_lint.py` and `scripts/rules_query.py` apply it automatically.

Apply these rules to everything the skill writes: redlines, comments, drafts, and suggested wording in a review. When you apply one against MSCD, say so in the finding ("house rule; MSCD 14.15 differs"), so Blake can see the departure.

## Contents
1. Active voice only
2. Digits for every number
3. Enumeration: I., A., 1., (a), (i); no only child
4. Cross-references: avoid; refer by heading
5. Spacing: two spaces between sentences, one after a colon
6. Attachments: Schedule and Exhibit, capitalized
7. Dates: January 1, 2027
8. Prohibition: never shall with a negative subject
9. Typography: 12-point Aptos, clean visual lines
10. Other settled choices
11. Party names: no article

**Severity of a house-rule finding.** Rule 8 (*shall* with a negative subject) and an undefined or 2-form defined term are severity 1. Typography (rules 5 and 9: spacing, font, size, alignment, underlining, bold definitions) and reduced passives (rule 1) are severity 3. Every other house rule is severity 2. A finding under an MSCD rule that the house style doesn't change takes the severity in its rule record.

## 1. Active voice only

**Rule.** Every sentence and every clause uses the active voice. Supersedes the MSCD allowances for the passive (3.23-3.26, 3.339-3.340, 13.209, 18.12, and the ✓✓ passive examples in Figure 1 and Table 1).

**Why it works with MSCD.** MSCD already requires the active voice for anything a party does (3.15). The house rule extends that to the cases where MSCD tolerates the passive. The reader then always sees who acts.

**How to recast the hard cases:**
| Passive form | Active recast | Note |
|---|---|---|
| *if any Necessary Project Approval is revoked* | *if any Person revokes a Necessary Project Approval* | Name a catchall actor when the actor is unknown or plural. Use the contract's defined term for persons if it has one. |
| *Any notice will be deemed received on delivery* | *This agreement treats any notice as received on delivery*, or *Any notice is effective on delivery* | A legal fiction: make the agreement the subject, or use a linking verb. *is effective* is not passive. |
| *Section 4 is hereby amended to read as follows:* | *The parties hereby amend the section titled "Payment" to read as follows:* | Amendments become language of performance with the parties as subject (and refer by heading; see 4). |
| *The Shares will be issued at Closing* | *Acme shall issue the Shares at Closing* | A party's action: name the party and pick the category (here, obligation). |
| *is payable*, *is exercisable*, *is due* | *Acme shall pay*, *Lee may exercise* | MSCD agrees (3.336-3.338). |

**Contingencies.**
- A linking verb plus an adjective is not passive: *is void*, *is effective*, *is liable*, *is entitled*, and *is dated* in the introductory clause (MSCD 2.21), where *dated* describes the agreement and no actor is missing. Don't flag these as passive. (But *is entitled to* has its own MSCD problems; see `verbs.md`.)
- A past participle used as an adjective before a noun is not passive (*the attached form*, *the Excluded Assets*).
- **Fixed exception: *is not required to*** (Blake's decision). It is passive in form, but it is MSCD's verb structure for the absence of obligation (3.292), and it hides no actor: the party is the subject (*Acme is not required to repair the Equipment*). Its active alternative, *this agreement does not require Acme to*, is a form MSCD rejects. Use it as is, and use the active voice after it (3.295).
- **Reduced passives** (a past participle after a noun, standing for a shortened relative clause: *the notice given under this section*, *the Shares issued at Closing*, *the Units listed in Schedule A*). Recast in the active when a clean active form exists (*the notice that Acme gives under this section*, *the Units that Schedule A lists*); otherwise leave it (Blake's decision). Why: *given* is short for *that is given*, a passive with the actor dropped; the recast puts the actor back. The lint flags candidates as `reduced-passive`.
- Quoted text (a statute, a defined name, a quotation from another document) stays as it is. Note the passive in a comment only if it matters.
- If recasting a sentence in the active voice would change its meaning (for example, because naming an actor narrows who can act), keep the meaning, flag the sentence, and ask Blake. Never change meaning to satisfy a style rule.

## 2. Digits for every number

**Rule.** State every number in Arabic digits: *2 days*, *the 3rd anniversary*, *10 Business Days*, *$5,000*. Never spell a number out, and never use words and digits together (*five (5)*). Supersedes 14.15-14.16 and 14.19-14.21. Keeps 14.5-14.11 (no words and digits) and 14.12 (digits for the big number).

**Contingencies.**
- Don't start a sentence with a digit. Restructure the sentence (*Within 30 days...* becomes *Acme shall ..., no later than 30 days after ...*), rather than spelling the number out.
- **When *one* is a number** (Blake's decision). Write a digit whenever the word counts something: *1 or more Units*, *1 of the parties*, *1 party*, *any 1 Lender*. Keep the word where *one* is a pronoun or part of another word: *no one*, *one another*, *each one*, *the one that*, *anyone*, *one-time*, *one-way*. The test: if you could replace the word with *2* and the sentence would still make sense, it counts something, so use the digit.
- Ordinals: write *1st*, *2nd*, *3rd* where the word counts something (*the 1st anniversary*, *the 2nd installment*). Words such as *first* that don't count (*first-priority lien*, *at first*) and fixed terms (*right of first refusal*, *first-class mail*) aren't numbers; leave them.
- Fractions: *1/2* or *50%* by context; MSCD prefers a percentage when other percentages appear nearby (13.670-13.671).
- Money and percentages follow MSCD 13.544-13.556 and 14.53-14.55, in digits.
- A number inside a proper name or quotation stays as written (*Fifth Third Bank*).

## 3. Enumeration: I., A., 1., (a), (i); no only child

**Rule.** Use this hierarchy, one tab further in for each level, with Word's native multilevel numbering:

| Level | Marker | What it numbers |
|---|---|---|
| 1 | I., II., III. | Articles (groups of sections), with a heading in capitals |
| 2 | A., B., C. | Sections, each with a bold heading |
| 3 | 1., 2., 3. | Subsections (distinct aspects of the section's topic) |
| 4 | (a), (b), (c) | Enumerated clauses within a sentence |
| 5 | (i), (ii), (iii) | Subclauses |

Supersedes 4.11, 4.17, 4.29-4.30, 4.47-4.49 and 4.58-4.59 (MSCD's numbering scheme). If a short contract has no articles, start at level 2 (A., B., C.) and say so in the intake summary.

**Section line.** The section letter takes a period, and the bold heading runs into the text and also ends with a period, followed by 2 spaces: **A. Purchase and Sale.**  Seller shall sell the Assets to Buyer. (Blake's decision; MSCD 4.59 puts no period after either.)

**Every letter.** Section letters run through the whole alphabet, I and O included (Blake's decision). An article I. and a section I. can share a label; the level tells them apart: an article sits at the margin with its heading in capitals, and a section sits one tab in with a bold heading. The lint reads I. after H. as a section.

**No only child.** Never create a single item at any level (a lone A. under I., a lone 1. under A., a lone (a)). If a parent has only one sub-concept, put that text directly under the parent with no marker. Supersedes 4.20.

**MSCD rules that still apply within the house scheme:** give every section a heading (4.21-4.27); don't use unenumerated paragraphs in a section that has subsections (4.28); always use introductory text before enumerated clauses and put nothing after them (4.37-4.38); don't use bullets (4.53); don't follow a number at one level directly by the first item of the next level down with no text between them (4.54); one set of enumerated clauses per provision (4.55); about 15 lines per block before dividing (4.63).

**Renumbering.** When you renumber an existing contract into this scheme, keep an old-to-new map and give it to Blake with the redline.

## 4. Cross-references: avoid; refer by heading

**Rule.** Avoid internal cross-references; restructure so each provision stands on its own (MSCD agrees: "the fewer cross-references in a contract, the better," 4.98). Where a reference is unavoidable, refer to the provision by its heading, not its number: *as stated in the section titled "Indemnification"* or *under the Indemnification section*. Supersedes 4.100-4.106 (references by number and the rule against headings in references).

**Contingencies.**
- **Headings become operative.** Every heading used in a reference must be unique in the contract and must match the reference word for word. Check every reference against the headings after every edit; renaming a heading breaks a reference just as renumbering would.
- **The headings clause.** A clause saying headings "are for convenience only and do not affect" meaning (MSCD 15.18) undercuts references that identify provisions by heading. Under the house rule every reference is by heading, so always delete that clause or limit it ("Headings do not affect the meaning of the provisions they introduce, but references to a provision by its heading identify that provision"), and explain why in a comment.
- References to attachments name the attachment (*Schedule A*), which is not an internal cross-reference.
- References to other agreements or statutes are unaffected.

## 5. Spacing

**Rule.** Two spaces after a sentence-ending period, question mark or exclamation mark within a paragraph. One space after a colon. Supersedes 16.44-16.46.

**Contingencies.** Abbreviations inside a sentence (*Inc.*, *U.S.*, *No.*) take one space. Apply the rule consistently across the document; mixed spacing is the problem MSCD 16.45 warns about, and consistency avoids it.

## 6. Attachments

**Rule.** Write references to attachments with initial capitals: *Schedule A*, *Exhibit 2*. Schedules take letters (*Schedule A, Schedule B*) and exhibits take numbers (*Exhibit 1, Exhibit 2*), so no schedule and exhibit share a designation; relabel any other system and update every reference. MSCD allows sequential letters or numbers, or section numbers, and suggests a hybrid of schedules by section number and exhibits by letter (5.80-5.83); this house rule supersedes those options. Supersedes MSCD's lowercase convention (5.79, 17.35). Every other MSCD attachment rule applies in full; see `attachments.md`. Blake asked that the schedule-versus-exhibit distinction be built in: check every attachment, every time.

## 7. Dates

**Rule.** *January 1, 2027*. Supersedes 2.22 and 10.7-10.10. MSCD's other date rules still apply: no *this 24th day of October*, no numerical dates such as *10/9/2027*, no *A.D.* (10.11-10.14).

## 8. Prohibition: never shall with a negative subject

**Rule.** Never write *Neither party shall*, *No Shareholder shall*, *Nobody shall*. Under the *has a duty* test, a negative subject with *shall* reads as an absence of duty, not a prohibition (MSCD 3.324: "it would appear to express the absence of duty rather than expressing prohibition"). Write *Neither party may assign* or *No Shareholder may transfer* (MSCD 3.324: "using may is the better option"). With a positive subject, the prohibition is *shall not*: *Acme shall not assign*.

Blake reports that Tina Stark has described litigation in which *neither party shall assign* was read as imposing no duty. The case has not been verified; cite MSCD 3.324 for the rule, not the case.

## 9. Typography and layout

- 12-point Aptos throughout (supersedes the size guidance at 16.37-16.38).
- Clean, clear visual lines: ragged-right text, never justified (16.16-16.17); no underlining (16.21); bold only for section headings and for defined terms where they are defined (16.20); capitals only for article headings and party names where MSCD uses them, or where a statute requires (16.19, 16.24-16.31); consistent indents (one tab per level); white space between blocks; native Word numbering, never typed numbers.
- Render every delivered .docx to images and look at it before delivery.

## 10. Other settled choices

| Topic | Choice | MSCD |
|---|---|---|
| Precedence | Blake's rules always prevail | (precedence list in SKILL.md) |
| The other side's drafts | Full MSCD conformance by default ("We need to start educating people"); separate meaning changes from style changes so the other side sees what matters | Differs from MSCD's review advice (Introduction, PDF pp. 54-55) |
| *states* versus *represents and warrants* | *states* on Blake's drafts; on the other side's drafts, keep their verb and suggest in a comment the remedies-neutral sentence (3.459-3.463) | Agrees |
| *intends that* | MSCD5 3.491-3.500 as printed; Adams's "language of state of mind" proposal noted only | Agrees |
| Articles with party names | No article: *Company*, *Buyer*, *Apple* (section 11) | Differs (2.105; 6.63) |
| Singular *they* | Use it | Optional under 17.15-17.16 |
| *knows or should have known* | Flag it every time; don't rewrite it. Changing the words can change the legal knowledge standard. Offer a defined *Knowledge* term (MSCD 13.506: whose knowledge counts, and actual knowledge or knowledge after inquiry) for Blake's decision | Agrees (13.506) |
| Wording a statute or rule requires | Keep it, even where a house rule would change it, and flag it. Examples: a UCC disclaimer naming MERCHANTABILITY in capitals; *promises to pay to the order of* in a negotiable note; *work made for hire* | Agrees (16.24-16.31) |
| The remedies-neutral sentence | In the active: *The verb that this agreement uses to introduce a statement of fact does not affect the remedies available for inaccuracy of that statement of fact.* | Recast of 3.463 (house rule 1) |
| Tracked-change author | *Blake's AI Agent* | n/a |
| Adams's floated proposals | Note only | n/a |

## 11. Party names: no article

**Rule.** No article before a defined term that names a party: *Company shall pay Employee*, not *The Company shall pay the Employee*. The definition takes no article either: ACME WIDGETS, INC., a Tennessee corporation ("**Company**"). MSCD 2.105 and 6.63 use *the* with common-noun party terms; this rule supersedes them.

**Why it works.** In English a singular common noun needs a determiner (*the company*). A word used without one reads as a name, the way *Apple* does. Dropping the article makes each party term work as a name, so it reads the same whether the term is a common noun (*Company*) or a trade name (*Apple*).

**Scope and contingencies.**
- Covers every defined term that names a party in the introductory clause: *Company*, *Buyer*, *Employee*, *Licensee*, and plurals (*Sellers shall deliver*).
- Doesn't cover role labels, which keep *the* (Blake's decision): *the Receiving Party*, *the Disclosing Party*, *the Indemnifying Party*. A role label (MSCD 2.117) points to whichever party plays a role, so it works as a common noun, not a name.
- Doesn't cover other defined terms (*the Shares*, *the Purchase Price*, *the Closing*) or generic references to parties (*the other party*, *each party*, *either party*, *the parties*). Those keep their articles and determiners.
- An article that belongs to another noun stays: *the Company Plan*, *a Company employee*. There *the* or *a* goes with *Plan* or *employee*, not with *Company*.
- Possessives drop the article too: *Company's obligations*.
- A legal name that includes *The* keeps it in the introductory clause (*THE UNIVERSITY OF TENNESSEE*); the defined term (*University*) takes no article.
- On the other side's drafts, flag *the Company* like any other house-rule departure, and change every instance, including the definition, so the contract stays consistent.
- The lint flags candidates as `party-article`. It reads the party names from the introductory clause; for a fragment without one, it uses a default list of common party nouns.

