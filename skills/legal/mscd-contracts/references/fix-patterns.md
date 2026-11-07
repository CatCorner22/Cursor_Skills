# Fix patterns: worked fixes from blind-test failures

Read this file in Stage 2, after you draft the findings and before you write their fixes. It groups the 122 failures of blind rounds 7 and 8 (81 and 41) by the mistake behind them, most frequent first, and shows for each mistake the original sentence, the fix a reviewer wrote, the test it failed, and a fix that passes. The tests are the 6 tests in SKILL.md (Stage 2, "Check every fix"); `fix-check.md` gives the checker's form of them. Correct text that only looks wrong is in `look-alikes.md`; this file repeats a look-alike only where reviewers rewrote it anyway. Examples shorten the contracts' own sentences; "..." marks a cut.

## Index

| # | Pattern | Round 7 | Round 8 | Total | Test |
|---|---|---|---|---|---|
| 1 | The review misses the problem | 26 | 9 | 35 | finding |
| 2 | The fix silently changes the deal | 8 | 10 | 18 | 3 |
| 3 | The fix rewrites correct text (false alarms) | 9 | 7 | 16 | step 1 |
| 4 | The fix answers a different problem | 12 | 4 | 16 | 1 |
| 5 | A reading gets no wording, or the fix picks 1 silently | 8 | 5 | 13 | 5 |
| 6 | The fix gets the tense or the category wrong | 6 | 3 | 9 | 1, 3 |
| 7 | The fix leaves part of the problem in place | 8 | 1 | 9 | 2 |
| 8 | The fix creates a new problem | 4 | 2 | 6 | 4 |

Each failure counts once, under its deciding reason. Modifier reach, the largest single cause, runs through 3 patterns: 7 misses (pattern 1), 4 fixes that addressed another problem in the same sentence (pattern 4), and 3 fixes that drop a reading (pattern 5).

## 1. The review misses the problem (35)

**Rule.** Run the scans below on every sentence, including a sentence that already has a finding: a sentence can hold several problems, and a finding on 1 doesn't end its review.

**What the reviewers missed** (round 7 + round 8): a modifier before or after a list, 2 + 5; a policy in the present tense about a contingent event, 5 + 1 (see pattern 6); a money formula without *an amount equal to*, or an amount that appears twice, 4 + 1; a cap without *each* or *in the aggregate*, 3 + 0; a pronoun with 2 antecedents, 3 + 0; a vague standard with a measure the contract supplies, 3 + 0; a nonparty obligation, 3 + 0; a defined-term defect, 2 + 0; a term of art in an ordinary sense, 1 + 1 (*assigns responsibility*; a *Security Badge*); *any* under a negative, 0 + 1.

**Scan A: modifiers over a list (MSCD 12.3; 12.7; 12.14).** Find every pair or list of nouns joined by *and* or *or*. Read the word or phrase right before the 1st noun (*United States*, *defective or nonconforming*, *new or modified*) and the phrase right after the last noun (*for backup purposes*, *located in the Territory*, *that results from ...*, *who have access to ...*, *arising after the Closing*). Each one reaches 1 noun or all of them, so each one is a finding with 2 wordings unless you name the provision that rules a reading out. A comma doesn't settle the reach (MSCD 12.26: relying on the comma test is "beyond reckless"; 12.37). The fixes come from MSCD: to reach every noun, repeat the modifier for each (12.4; 12.10); to reach 1 noun, put that noun next to the modifier, last in the list for a preceding modifier (12.4) and first for a trailing one (12.10).

**Scan B: *any* under a negative (MSCD 11.110).** In a sentence about failure or inability (*does not pay any invoice*, *fails to perform any obligation*, *inability to perform any duty*), *any* can mean 1 or more or can mean every one. Offer both: *leaves 1 or more invoices unpaid*; *pays no invoice*.

*Example 1.1 (c162, preceding modifier).*
- Original: *... and shall remove all defective or nonconforming materials and equipment from the Project site.*
- Reviewer: no finding.
- Why it fails: *defective or nonconforming* can modify *materials* alone, so Subcontractor removes all its equipment, or both nouns (12.3).
- Right fix: (a) both: *... and shall remove from the Project site all defective or nonconforming materials and all defective or nonconforming equipment.*  (b) materials only: *... and shall remove from the Project site all equipment and all defective or nonconforming materials.*  Ask Blake which.

*Example 1.2 (c152, trailing phrase).*
- Original: *Licensee may make copies of the Software and the Documentation for backup purposes.*
- Reviewer: no finding.
- Why it fails: *for backup purposes* can limit only the Documentation copies, which leaves Software copies unlimited, or both (12.7).
- Right fix: (a) both: *Licensee may make copies of the Software for backup purposes and copies of the Documentation for backup purposes.*  (b) Documentation only: *Licensee may make copies of the Documentation for backup purposes and may make copies of the Software.*  Ask Blake which.

*Example 1.3 (c156, trailing relative clause in an exculpation).*
- Original: *Landlord is not liable for any damage to Tenant's property or injury to Tenant's employees or invitees that results from the acts of other tenants of the Building.*
- Reviewer: no finding.
- Why it fails: the *that* clause can limit only the injury, so Landlord escapes all property damage, or both (12.7).
- Right fix: (a) both: *Landlord is not liable for any damage to Tenant's property that results from the acts of other tenants of the Building or for any injury to Tenant's employees or invitees that results from those acts.*  (b) injury only: *Landlord is not liable for any damage to Tenant's property, and Landlord is not liable for any injury to Tenant's employees or invitees that results from the acts of other tenants of the Building.*  Ask Blake which.

*Example 1.4 (c151, any under a negative).*
- Original: *If Distributor does not pay any invoice when due, Solterra may suspend shipments until Distributor pays the overdue amount.*
- Reviewer: no finding.
- Why it fails: the condition can mean 1 late invoice or no paid invoice at all (11.110), and the 2 readings differ sharply on when Solterra may stop shipping.
- Right fix: (a) *If Distributor leaves 1 or more invoices unpaid after their due dates, Solterra may suspend shipments until Distributor pays [the] [each] overdue amount.*  (b) *If Distributor pays no invoice when due, ...*  Ask Blake which; Distributor is his client, so the trigger is also a business point.  Avoid *fails to pay 1 or more*: MSCD 13.285 calls invoking failure "never necessary", and *does not pay 1 or more* brings back the scope question.

## 2. The fix silently changes the deal (18)

**Rule.** Diff the fix against the original word by word: every party, act, condition, standard, form term, and allocation of risk survives unless the finding is about it, and every term you add or drop goes to Blake in brackets with a sentence that says what it changes (test 3).

**Source.** A nonparty provision gets the restructure onto the party and a statement of who bears the risk (MSCD 3.165), *must* on the nonparty only "if such restructuring isn't possible" (3.166), and, for conduct the party can't control, a reasonable-efforts duty plus a risk-allocation provision, 2 provisions in all (3.180; 3.173). *Is entitled to* invites the claim that the obligor "didn't have to perform until" asked (3.169), so a fix that adds *at X's request* builds in that very defense.

**Where it happened.** In nonparty fixes (8), reviewers weakened a prohibition to a duty to instruct (c149), narrowed a bar to the party's own purchases (c150), kept *must* where a restructure was possible (c162), replaced *shall cause* with a no-disclosure-unless-they-agree condition and dropped the risk allocation (c164; c167), demoted the party's answerability to an optional add-on (c169), wrote *shall obtain an endorsement* (c140), and added *agreed in writing* (c126). In other fixes (10), they added *At Licensee's request* and *up to 2* (c152) and a new duty to deliver a proposed certificate (c156); raised *could* to *would reasonably expect* (c144); cut *10 business days* to *10 days* (c140); dropped an Owner's option to set a later date (c144) and a stuffed definition's duty instead of moving it (c128); swapped the defined *Service Level* for another phrase (c138); widened *attorneys' fees* to *legal fees* on the other side's draft (c170; MSCD 13.517 says *legal fees* "would cover paralegal fees too"); wrote *warrants* and *may use* for *states* and *has the right to use* on Blake's draft (c150; house rule 10); and turned *may ... only* into *shall use ... only*, a duty to use (c145; MSCD 3.226).

*Example 2.1 (c149, a nonparty prohibition).*
- Original: *Customer shall keep its login credentials confidential, and no Authorized User shall share credentials with another person.*
- Reviewer: *... and shall instruct each Authorized User not to share credentials with another person.  [Option, adverse to Customer: Customer is liable to Lumenbright for an Authorized User's sharing of credentials.]*
- Why it fails: a duty to instruct replaces the bar on sharing, and Blake never sees the change (test 3): the bar forbids the sharing, but Customer meets a duty to instruct once it gives the instruction.
- Right fix: (a) house rule 8 form: *Customer shall keep its login credentials confidential, and no Authorized User may share credentials with another person.*  (b) restructure onto Customer (3.180): *Customer shall keep its login credentials confidential and shall use reasonable efforts to prevent each Authorized User from sharing credentials with another person[, and Customer is liable to Lumenbright for losses that result if an Authorized User nevertheless shares credentials].*  Ask Blake which.

*Example 2.2 (c164 and c167, shall cause for persons the party doesn't control).*
- Original: *Each Member shall keep the Company's nonpublic information confidential, and the Members shall cause their respective Affiliates and advisors to do so.*
- Reviewer: *... and shall not disclose it to any of that Member's Affiliates or advisors unless that Affiliate or advisor has agreed [in writing] to keep it confidential.*
- Why it fails: the fix adds a condition the original lacks and drops the Member's answerability for its Affiliates and advisors, which *shall cause* gave; only *in writing* went to Blake (test 3). c167 made the same change for an Employee's spouse, attorney, and tax advisor.
- Right fix: *Each Member shall keep Company's nonpublic information confidential and shall inform each of its Affiliates and advisors that receives that information of this obligation[, and each Member is liable to Company for any disclosure of that information by any of its Affiliates or advisors].*  Tell Blake that the bracketed sentence carries over the risk that *shall cause* put on the Member (3.165; 3.173), so leaving it out shifts that risk to Company.

*Example 2.3 (c169, the default wording drops the risk).*
- Original: *The Receiving Party shall cause its Representatives to comply with this agreement.*
- Reviewer: *Each of the Receiving Party's Representatives must comply with this agreement.  [Added option for Blake: The Receiving Party is liable to the Disclosing Party for any act or omission of its Representatives ...]*
- Why it fails: the default leaves no party answerable for the Representatives, and the sentence that keeps the original allocation appears as a new business term (test 3); *must* is the fallback only where the restructure isn't possible (3.166), and here it is possible.
- Right fix: *The Receiving Party shall inform each of its Representatives of the terms of this agreement before disclosing Confidential Information to that Representative, and the Receiving Party is liable to the Disclosing Party for any act or omission of any of its Representatives that would breach this agreement if the Receiving Party committed it.*  The same test decides c162: Subcontractor controls who works on site, so the fix is *Subcontractor shall keep off the Project site any of its employees who is not wearing a hard hat, safety glasses, and a high-visibility vest[, and shall furnish that equipment to its employees]*, not *Each of Subcontractor's employees must wear*.

*Example 2.4 (c152, a recast of is entitled to).*
- Original: *Licensee is entitled to 2 training sessions each Contract Year.*
- Reviewer: *At Licensee's request, Quillon shall conduct up to 2 training sessions in each Contract Year, ... [and each on a date that the parties agree].*
- Why it fails: *At Licensee's request* adds the request condition 3.169 warns about, and *up to 2* turns a fixed 2 into a ceiling; neither goes to Blake (test 3).
- Right fix: *Quillon shall provide Licensee with 2 training sessions in each Contract Year[, each on a date that the parties agree].*  The bracket is the only new term, and Blake decides it.

## 3. The fix rewrites correct text (16)

**Rule.** Before you write a fix, confirm that the text breaks the rule's own pattern (`rules_query.py --id`) and search `look-alikes.md`; a preference (*a city is simpler than a zone*), a reading the text doesn't support, or a deal you would like better is not a problem, and a fix to correct text fails even when it keeps the meaning.

**What reviewers rewrote** (round 7 + round 8): a plain backward deadline, as 2 counts, 4 + 0; *is not required to*, 1 + 1; *must* with a thing as subject, 1 + 1; a negative subject with *may*, 1 + 1; a correct tense, 0 + 2; *both dates included*, 1 + 0; *will* in a recital, 1 + 0; an integrated definition, 0 + 1; *Central time*, 0 + 1.

| Correct text (contract) | Why it is correct | Source |
|---|---|---|
| *no later than 10 Business Days before the audit* (c127; also c128, c129) | A plain deadline names its day under the counting convention; only a minimum-notice period (*at least 20 days' notice*) needs 2 counts | MSCD 10.65-10.66 |
| *Neither Company nor any Consenting Holder is required to obtain any other consent ...* (c171); *Licensor is not required to suspend* (c142) | Absence of obligation; the negative subject goes with *is required*, not *shall*. Wanting a prohibition is Blake's deal point | MSCD 3.292; house rule 1 fixed exception |
| *the policies must name Lender as lender loss payee* (c158); *Each policy must name Contractor and the Owner* (c141) | *Must* for a subject that can't assume a duty | MSCD 3.149; 3.154; 3.156 |
| *No person may enter the Project site without completing Contractor's site orientation* (c162); *no increase may exceed 4%* (c127) | House rule 8's form; *may* with a negative subject prohibits | MSCD 3.324; house rule 8 |
| *Each party's liability ... is limited, in the aggregate, to ...* (c149) | A standing allocation keeps the present tense; the final ruling held the change to *will not exceed* a tense error, whatever the merit of a passive point | MSCD 3.334 |
| *The kickoff meeting will take place on ...* (c153) | *Will* for a policy about a future event; the sentence's problem was the weekday | MSCD 3.334 |
| *which begins on December 1, 2026, and ends on February 28, 2027, both dates included* (c125) | The end days are explicit | MSCD 10.23-10.24 |
| *Manager will do so through the Operator* (a recital, c144) | Recitals state background; *will* there states the future | MSCD 2.130 |
| *(that work, the "Custom Modifications")* (c152) | MSCD's technique for "clarifying the scope" of an integrated definition | MSCD 6.74 |
| *2:00 p.m. Central time* (c158) | Names the zone without the standard-time error of *CST*; a city is only "a simple way" | MSCD 10.51; 10.55-10.56 |

*Example 3.1 (c171).*
- Original: *Neither Company nor any Consenting Holder is required to obtain any other consent for the Series B Closing under the Rights Agreement.*
- Reviewer: *The parties acknowledge that the Rights Agreement does not require Company or any Consenting Holder to obtain any other consent ...*
- Why it fails: the original uses the form 3.292 prescribes, and the rewrite turns a policy into an acknowledgment of a fact about another agreement; MSCD 3.293 rejects the *does not require* forms, because *is not required to* "is sufficient".
- Right fix: none; leave the sentence.

*Example 3.2 (c162).*
- Original (Contractor's site rules, which Subcontractor complies with as a whole): *No person may enter the Project site without completing Contractor's site orientation.*
- Reviewer: *Subcontractor shall not send onto the Project site any person who has not completed Contractor's site orientation.*
- Why it fails: house rule 8's form is correct, and the rewrite narrows a site rule into 1 party's duty.
- Right fix: none.  Contrast c162's hard-hat sentence (Example 2.3): *employees shall wear* puts *shall* on a nonparty, which is a real problem.

*Example 3.3 (c127, a plain deadline).*
- Original: *... if Buyer notifies Supplier no later than 10 Business Days before the audit.*
- Reviewer: Option A *the 10th Business Day before the audit*; Option B *the 11th Business Day before the audit*.
- Why it fails: *no later than N days before X* already names its day (10.65's convention); 2 counts belong only to a minimum-notice period (10.66).
- Right fix: none.

**Disputed in round 8, resolved for the reviewer (c149).** The key called *Customer must request a Service Credit ...* correct; the final ruling held that a bare *must* in a condition is the problem (MSCD 3.389: "it would be reckless to rely on must and nothing more") and that the reviewer's *To receive a Service Credit, Customer must request it ...* is the cure (3.391: add a to-infinitive clause). So a *must* condition that already has its to-infinitive clause is correct; leave it.

## 4. The fix answers a different problem (16)

**Rule.** Before you write the fix, state the planted problem in 1 line in the finding's own words, then check that the fix's wording removes it; a sentence with 2 problems gets wording for both, in 1 combined fix (test 1; SKILL.md Stage 2: run the remaining passes on the same sentence).

**Where it happened** (round 7 + round 8). Reviewers fixed another point in a sentence whose real problem was modifier reach, 3 + 1 (c136, c140 twice; c162); a cap with no *each* or *in the aggregate*, 2 + 0 (c124; c140); a money formula without *an amount equal to*, 2 + 0 (c125; c138); *per year*, 1 + 1 (c132; c166); a conflict between 2 sections, 2 + 0 (c140; c147, whose deadline fell before signing); a vague *prompt*, 1 + 0 (c140, where the fix dropped a party article instead); a termination on notice, 1 + 0 (c140, where the fix counted days only); a list after *including*, 0 + 1 (c149, where the fix treated a pronoun); or a definition that defeats a threshold, 0 + 1 (c156, where the fix called the conflict harmless).

*Example 4.1 (c162).*
- Original: *Subcontractor shall indemnify Contractor and Owner against all claims for bodily injury or property damage that Subcontractor's negligence causes and that arise out of the Work.*
- Reviewer: options on whether Subcontractor's negligence must be the sole cause or 1 of several causes.
- Why it fails: the planted problem is the reach of the 2 *that* clauses (12.7): they limit property damage alone, so Subcontractor indemnifies every bodily-injury claim regardless of fault, or both. Both options keep the ambiguous structure (test 1).
- Right fix: (a) both: *... against all claims, whether for bodily injury or for property damage, that arise out of the Work and that Subcontractor's negligence causes.*  (b) property damage only: *... against (a) all claims for bodily injury that arise out of the Work and (b) all claims for property damage that arise out of the Work and that Subcontractor's negligence causes.*  Ask Blake which; the sole-cause question can ride along as a 2nd decision.

*Example 4.2 (c166 and c132, per year).*
- Original: *"Base Salary" means $310,000 per year for the Initial Term, as the Board adjusts it under the section titled "Salary Review."*
- Reviewer: options on the Renewal Term rate, each keeping *per year*.
- Why it fails: *year* can mean a calendar year or each 12-month period from a start date, and the sentence doesn't address a short period (10.98-10.101); the fix never asks (test 1).
- Right fix: (a) *"Base Salary" means $310,000 for each 12-month period of the Term that begins on January 4 (prorated for any shorter period at the end of the Term), as the Board adjusts it under the section titled "Salary Review."*  (b) *... $310,000 for each calendar year (prorated for 2027 and for any shorter final year) ...*  Ask Blake which.  Don't flag *8% per year* for interest: a rate isn't an apportioning provision (`look-alikes.md`).

*Example 4.3 (c149, including).*
- Original: *Lumenbright may use Usage Data for its internal purposes, including improving the Service and training its models.*
- Reviewer: 2 readings of the 2nd *its*, each keeping *internal purposes, including ...*.
- Why it fails: the question is whether the list is illustrative or exhaustive (13.363-13.364: courts let *including* introduce a list that limits the general noun); the fix answers a pronoun question instead (test 1).
- Right fix: (a) illustrative: *Lumenbright may use Usage Data for any internal purpose of Lumenbright, including to improve the Service and to train Lumenbright's models.*  (b) exhaustive: *Lumenbright shall not use Usage Data other than to improve the Service and to train Lumenbright's models* (the prohibition form, because *may ... only* stays ambiguous; 3.226).  Ask Blake which uses Customer accepts.

*Example 4.4 (c138, a money formula).*
- Original: *Provider shall credit Customer, against the next invoice, the Monthly Fee multiplied by the Downtime Percentage for that month.*
- Reviewer: options on which Monthly Fee the credit uses, each keeping *the Monthly Fee multiplied by*.
- Why it fails: the planted problem is the formula's form (14.22; 14.24: *an amount equal to*); the fix answers another question (test 1).
- Right fix: *Provider shall credit Customer, against the next invoice, an amount equal to the Monthly Fee [for the hosted analytics platform] multiplied by the Downtime Percentage for that month.*  The bracket keeps the reviewer's real 2nd question for Blake.

## 5. A reading gets no wording, or the fix picks 1 silently (13)

**Rule.** List every candidate before you write: for a pronoun, every noun of the right number in the sentence and the sentence before, the nearer noun included; for a modifier, each noun it can reach; for a notice period, giving or receipt and each count; for a conflict, each provision as the one that governs; then write 1 complete wording per reading, or name the provision that rules a reading out (test 5).

**Where it happened** (round 7 + round 8). The missing reading came from a pronoun, *the same*, or *such contact*, 2 + 3 (c126; c142; c152; c153 twice), and in c153 the missing reading was the nearer noun; a modifier's reach, 3 + 0 (c134; c135; c140, whose reviewer dismissed a reading as nonsense); a minimum-notice count, 1 + 1 (c127; c151); *within N days of*, 1 + 0 (c135); an illustrative or exhaustive schedule, 1 + 0 (c135); or a conflict with 2 resolutions, 0 + 1 (c154, where the fix offered 1).

*Example 5.1 (c153, the nearer noun).*
- Original: *Client shall provide Consultant with the Baseline Data and the Survey Results no later than January 15, 2027, and Consultant may rely on it without independent verification.*
- Reviewer: (1) both data sets; (2) the Baseline Data alone.
- Why it fails: the singular *it* most naturally takes the nearer noun, the Survey Results, and that reading gets no wording (7.16; test 5).
- Right fix: (a) both: *... and Consultant may rely on the Baseline Data and the Survey Results without independent verification.*  (b) *... and Consultant may rely on the Survey Results without independent verification.*  (c) *... and Consultant may rely on the Baseline Data without independent verification.*  Ask Blake which.  MSCD 3.547 separately bars *may rely on* (a party may rely anyway; allocate the risk of bad information instead): make that its own finding with its own question, and carry the chosen reading into it.

*Example 5.2 (c151, termination on notice).*
- Original: *Either party may terminate this agreement for convenience on 90 days' notice to the other party.*
- Reviewer: giving or receipt, each with *90 days after*.
- Why it fails: *on 90 days' notice* is a minimum-notice period, so the 90th day and the 91st day are both readings (10.65-10.66), and the fix picks 1 count (test 5).
- Right fix (MSCD 13.627's model): (a) receipt: *Either party may terminate this agreement for convenience by notifying the other party, and this agreement will terminate on the [90th] [91st] day after the day the other party receives that notice.*  (b) giving: *... on the [90th] [91st] day after the day the terminating party gives that notice.*  Ask Blake which start and which count.

*Example 5.3 (c153, the same).*
- Original: *Consultant shall submit the draft report and the data appendix for each Assignment to Client, and Client shall return comments on the same no later than 10 Business Days after Client receives them.*
- Reviewer: *... and Client shall return comments on them ...*
- Why it fails: *them* adopts the both-items reading; whether Client comments on the report alone never reaches Blake (7.16; 13.760 on *same* as a pronoun; test 5).
- Right fix: (a) *... and Client shall return its comments on the draft report and the data appendix no later than 10 Business Days after Client receives them.*  (b) *... and Client shall return its comments on the draft report no later than 10 Business Days after Client receives it.*  Ask Blake which.

*Example 5.4 (c154, a conflict).*
- Original: *Customer shall pay the Fees for the period that begins on January 1, 2027, and ends on June 30, 2028, in equal monthly installments* (the Term section runs to December 31, 2028).
- Reviewer: (a) the installments run to December 31, 2028; (b) a 2nd schedule for July 1 through December 31, 2028.
- Why it fails: both options keep the Term to December 31, 2028, so the other resolution, a Term that ends on June 30, 2028, gets no wording (7.37; test 5).
- Right fix: (a) *Customer shall pay the Fees for the period that begins on January 1, 2027, and ends on December 31, 2028, in equal monthly installments.*  (b) *The parties amend the section of the Master Agreement titled "Term" so that the Term ends on June 30, 2028.*  Ask Blake which date the parties intend.

## 6. The fix gets the tense or the category wrong (9)

**Rule.** For every policy you write or keep, ask whether it applies on effectiveness or at a stated time (present tense) or depends on an event that might not happen or whose timing is uncertain (*will*), and never turn a policy into a duty or a duty into a policy to fix something else (MSCD 3.334: "if the policy relates to contingent future events ... use will"; 3.361: *will* in a matrix clause after a conditional clause; 3.335: no *shall* in language of policy).

**Where it happened** (round 7 + round 8). Reviewers wrote or kept the present tense for a termination or a fee increase that follows notice or *if*, 3 + 0 (c124 *takes effect*; c135 *is effective*; c142 *increases*); kept or wrote it for another contingent event, 3 + 2 (c127 *passes*; c127 *binds*; c132 *becomes due*; c166 *remains*; c166 *continues to bind*); and turned a correct *will* policy into a *shall* duty, 0 + 1 (c153).  The review missed 6 more tense problems (pattern 1), and 2 false alarms (pattern 3) changed a correct tense.

*Example 6.1 (c166, survival).*
- Original: *The article titled "Restrictive Covenants" continues to bind Executive after the Term for the periods it states.*
- Reviewer: delete the section, and "if Blake keeps it, it stays as written".
- Why it fails: the end of the Term has uncertain timing (renewals, early termination), so the policy takes *will* (3.334; MSCD 13.823's own example reads *will not relieve*); the fallback endorses the present tense (test 1).
- Right fix: *The article titled "Restrictive Covenants" will continue to bind Executive after the Term for the periods it states.*  Deleting the section stays a valid 2nd option, because each covenant states its own period.

*Example 6.2 (c166, a consequence of an assignment).*
- Original: *Company may assign this agreement to a successor to all or substantially all of its business, and it remains liable for Company's obligations that accrued before the assignment.*
- Reviewer: 2 antecedent options, both in the present tense (*remains*, *is liable*).
- Why it fails: the liability rule applies only if an assignment happens, a contingent event (3.334; 3.361).
- Right fix: (a) *... and Company will remain liable for its obligations that accrued before the assignment.*  (b) *... and the successor will be liable for Company's obligations that accrued before the assignment.*  Ask Blake which.

*Example 6.3 (c153, the reverse: a correct will made a duty).*
- Original: *The kickoff meeting will take place on Tuesday, January 4, 2027, at Client's Franklin, Tennessee, office.*  (January 4, 2027, is a Monday.)
- Reviewer: *The parties shall hold the kickoff meeting on [January 4] [January 5], 2027, ...*
- Why it fails: the weekday options are right, but *shall hold* adds a joint duty and replaces a correct policy (test 3).
- Right fix: (a) *The kickoff meeting will take place on January 4, 2027, at Client's Franklin, Tennessee, office.*  (b) *... on January 5, 2027, ...*  Ask Blake which.  Change only the date.

*Example 6.4 (c135, termination after notice).*
- Original: *Either party may terminate this agreement by giving 10 days' notice to the other party if the Closing has not occurred by March 31, 2027, ...*
- Reviewer: *... the termination is effective 10 days after the other party receives that notice.*
- Why it fails: the termination is a contingent future consequence, so it takes *will* (3.334; 13.627 writes *will terminate*).
- Right fix: *... and this agreement will terminate 10 days after the day the other party receives that notice*, and put to Blake the giving alternative and the *by March 31* question (that day or the day before; 10.23).

The present tense stays for a standing allocation or a policy in force on signing: *Each party's liability ... is limited, in the aggregate, to ...* (c149); *No Member is liable for the Company's debts*; *Tennessee law governs this agreement*.

## 7. The fix leaves part of the problem in place (9)

**Rule.** Fix every part of the problem the finding names: a vague standard gets a bracketed measure and a question, an amount stated twice ends up stated once, both ends of a period get their days, and a reduced passive gets its active form (test 2).

**Where it happened** (round 7 + round 8). Reviewers kept a vague term on their own judgment, 4 + 0 (c125 *reasonable notice*; c129 *adequate inventory*; c142 *materially*; c146 *substantially complete*); left an amount in 2 places, 3 + 0 (c141; c142; c145); fixed only 1 end of a period, 1 + 0 (c145); and kept a reduced passive, 0 + 1 (c156).

*Example 7.1 (c146, vagueness kept).*
- Original: *Advisor shall deliver a substantially complete draft of the market study no later than February 1, 2027, ...*
- Reviewer: keep, because "a draft has no sensible precise measure of completeness".
- Why it fails: the contract can state what the draft contains, and MSCD favors the specific standard where 1 exists (7.47-7.48); whether vagueness helps a party is Blake's call (test 2).
- Right fix: *Advisor shall deliver a draft of the market study that contains [every section of the final market study, with findings for each section,] no later than February 1, 2027, ...*  Ask Blake to set the content.  Keep a vague term only when no measure exists (*reasonable legal expenses* across litigation of every size, 7.48), and say why.

*Example 7.2 (c145, an amount stated twice).*
- Original: *Schedule B: 2027 Festival: $80,000.  2028 Festival: $70,000.  Total: $150,000.* (the definition also states $150,000)
- Reviewer: options on which figure governs, each keeping the figure in the definition and in the Total line.
- Why it fails: MSCD 1.56 says never "say the same thing twice", and the fix leaves both copies (test 2).
- Right fix: delete the Total line from Schedule B, or define the term by the schedule: *"Sponsorship Fee" means the total of the amounts that Schedule B states.*  When the copies disagree, each option both reconciles and deletes 1 copy.

*Example 7.3 (c156, a reduced passive).*
- Original: *"Premises" means Suite 400 of the Building, as shown on Schedule B, which the parties stipulate ...*
- Reviewer: *... as shown in Schedule B*, and moves the stipulation to the body.
- Why it fails: *as shown* stays a reduced passive with a clean active form (house rule 1), and the move rewrites more than the problem on the other side's draft (tests 2 and 3).
- Right fix: *"Premises" means Suite 400 of the Building, as Schedule B shows, ...*, with the rest of the sentence unchanged.  The comma-*which* stipulation inside the definition is a separate problem (MSCD 12.53 bars nonrestrictive clauses): give it its own finding and put the move to the body to Blake.

## 8. The fix creates a new problem (6)

**Rule.** Run every check on the fix's own words that you ran on the original: a list under a modifier, *and* mixed with *or*, a time of day, a definition's noun, and every provision on the same subject (test 4).

**Where it happened** (round 7 + round 8). Reviewers repaired *and/or* as *and*, which a reader can take to require both, 1 + 0 (c145; MSCD 11.90-11.91: *X or Y or both*); joined 2 relative clauses with *and* and *or*, 1 + 0 (c131; 11.96-11.100); kept, in an option, the trailing modifier that the option set out to settle, 1 + 0 (c137); tacked an integrated definition onto a sentence with no noun for it to name, 1 + 0 (c144; 6.74); added a time of day without a zone, 0 + 1 (c151; 10.51); and wrote an option that leaves a schedule in conflict with a definition, 0 + 1 (c156).  The other checks in test 4 (a phrase that reached 2 verbs, a 2nd definition, a noun with no antecedent, an only child, a reference to a heading that doesn't exist) caused no failure in rounds 7 and 8; keep running them.

*Example 8.1 (c151, a time with no zone).*
- Original: *The initial term of this agreement runs from January 1, 2027, to December 31, 2029 (the "Initial Term").*
- Reviewer: *... begins on January 1, 2027, and ends at midnight at the end of December 31, 2029 ...*
- Why it fails: the parties sit in Oregon and Georgia, and a time of day across time zones needs its zone (10.51); the fix adds a new gap (test 4).  *Midnight at the end of* is itself MSCD's form (10.38); the key's *11:59 p.m.* is the form 10.38 calls "clumsy".
- Right fix: *The initial term of this agreement begins on January 1, 2027, and ends at midnight at the end of December 31, 2029, [Eastern] time (the "Initial Term").*  Ask Blake which zone.

*Example 8.2 (c145, an and/or repair).*
- Original: *Sponsor shall provide the marketing collateral for its booth, including print and/or digital displays, at its own expense.*
- Reviewer: *... including print displays and digital displays ...*
- Why it fails: a reader can take *and* to require both kinds, a reading the original lacked (11.90-11.91).
- Right fix: *Sponsor shall provide the marketing materials for its booth, including print displays or digital displays or both, at its own expense* (*marketing materials* for *collateral*, house rule 13).

*Example 8.3 (c131, mixed and and or).*
- Original: *Vantage releases Harlow, and Harlow releases Vantage, from all claims that it asserted or could have asserted in the Action, including all claims arising out of the Project, ...*
- Reviewer, meaning 1: *... from all claims, whether known or unknown, that exist on the date of this agreement and that the releasing party asserted or could have asserted in the Action or that arise out of the Project.*
- Why it fails: *that ... and that ... or that* lets either conjunction take scope over the other (11.96-11.100), so the fix creates a scope ambiguity.
- Right fix, meaning 1: *Each party releases the other party from the following claims, whether known or unknown, that exist on the date of this agreement: (a) each claim that the releasing party asserted or could have asserted in the Action; and (b) each other claim that arises out of the Project.*  Meaning 2: *Each party releases the other party from each claim, whether known or unknown, that exists on the date of this agreement and that the releasing party asserted or could have asserted in the Action.*  Ask Blake which.  The enumerated form puts nothing after the clauses (house rule 3; MSCD 4.37-4.38).

## Before you hand over a fix: 8 questions

1. Did the scans for modifiers over a list and *any* under a negative run on this sentence, after the easier finding? (pattern 1)
2. Does every word the fix adds or drops map to the named problem, with every new term in brackets and explained to Blake? Does a nonparty fix keep both the bar and the party's answerability? (pattern 2)
3. Does the original break the rule's own pattern, or only a preference? (pattern 3)
4. Does the fix's wording remove the problem stated in its 1st line? (pattern 4)
5. Do the readings named equal the wordings offered, the nearer noun and every count included? (pattern 5)
6. Is each policy in the tense its event calls for, and did any *will* or present tense become *shall*? (pattern 6)
7. Is any part of the problem still standing: the vague word, the 2nd copy, the other end of the period, the passive? (pattern 7)
8. Does the fix pass the same scans as the original? (pattern 8)
