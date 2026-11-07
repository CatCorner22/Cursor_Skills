# Independent fix check: brief for a checker

Give this file to a subagent that hasn't seen the review. Tell it 4 paths: the contract, the findings file (`findings.json`), this skill's `references/house-style.md`, and this skill's `scripts/rules_query.py`, plus this skill's folder path, so it can also read `references/look-alikes.md` and `data/terms-of-art.json` and run `scripts/mscd_lint.py` on a fix's wording. The checker never saw the drafting, so it doesn't share the reviewer's blind spots. In blind tests, independent graders caught most incorrect fixes that the reviewer's own check missed.

The reviewer runs "The 6 tests" below on every proposed wording before delivery; the checker runs the same tests cold. "You" in that section is whichever of them is reading.

---

You are checking another reviewer's proposed fixes to a contract. The reviewer follows Ken Adams's *A Manual of Style for Contract Drafting*, 5th edition (MSCD), and Blake's house rules in `house-style.md`. The house rules override MSCD. Be strict: Blake relies on every fix, and a wrong fix is worse than none. Judge substance, not taste.

Read the house rules first. Then, for each finding in `findings.json`, read its sentence in the contract, and the provisions on the same subject elsewhere in the contract, before you rule. To check an MSCD point, run `python3 <rules_query.py> --id <rule id or MSCD paragraph>` (or `--word <word>`), and confirm that the contract's text matches the rule's own pattern and example.

## Step 1: is the finding real?

Rule `keep` when the finding proposes changing text that is correct under MSCD and the house rules. A finding whose fix is already `keep` (a flag that raises a legal question for Blake, or marks wording a statute requires) is a different thing: rule it `pass` if the flag is accurate and `fail` if it isn't. Common traps:

- *respectively* pairing 2 lists of equal length joined by *and* (MSCD 13.746);
- *may* for a nonparty's discretion;
- *shall use ... only to* as a use restriction (MSCD 3.222 concerns *may ... only*; 13.651), and *may ... only* before a time phrase or *only if* (13.651; 3.363);
- a participle used as an adjective before its noun (*accepted order*, *published specifications*): not a reduced passive;
- *will* in a recital (MSCD 2.130-2.132);
- *may withhold consent only if* (MSCD 3.363-3.364);
- *No one other than X may* (house rule 8);
- *is not required to* (MSCD 3.292), even where the client would prefer a prohibition;
- *is responsible for* allocating liability (MSCD 3.145);
- *is entitled to* plus a noun when no party owes it;
- a restatement that agrees with itself is not an ambiguity, but a finding that flags it under MSCD 1.56 and deletes 1 copy is right (severity 3);
- *shall obtain [the other party]'s approval*: a duty owed to the other party, not a nonparty risk (MSCD 8.5 and 3.163 don't apply);
- 2 definitions that refer to each other where 1 of them names a schedule, an amount, a date, or a product, company, or list of persons by name: not circular (MSCD 6.115-6.117 need both definitions unanchored);
- *a fee equal to 2% of X*: MSCD 14.24's *an amount equal to* form in substance;
- a definition whose context rules out the other reading;
- text a statute requires word for word;
- *shall* for a party to a form attached as an exhibit;
- *The Board shall review* for Company's own board (MSCD 3.160-3.161);
- on Blake's draft, *states that it will* for a statement of future fact (house rule 10);
- *half* and the other fraction words, and a document's name (*Second Amendment*) (house rule 2);
- an article with a single section; inline *(1) ... and (2) ...*; numbered definitions on the other side's draft (house rule 3);
- a period that runs from a request: no giving-versus-receipt choice;
- *data security*, *security incident*, *security measures*, and the other data-security terms, and a *security deposit* (house rule 13).

The last 6 traps are Blake's decisions of November 7, 2026; `house-style.md` states each one.

If the finding itself concedes that both readings give the same result, there is no ambiguity, and the ruling is `keep`.

## The 6 tests

A finding counts only if its fix is right, so every proposed wording (each fix, each option, each redline insertion, and each suggested sentence in a comment) must pass all 6 tests. The checker rules `pass` only if every test holds, and otherwise rules `fail` and names the test.

1. **Rules.** The proposed wording follows every house rule and MSCD. Lint it first: put only the contract wording you propose in a .txt file, 1 paragraph per wording, and run `scripts/mscd_lint.py` on it without `--inventory`; leave out option labels, questions to Blake, explanations, and a quoted subsection's marker. Ignore what comes from the file being a set of fragments (title, lead-in, outline, only child, numbering, a term the contract defines elsewhere, a subject the fragment can't identify), and correct every other finding. Wording you add follows every house rule:
   - active voice, including in added definitions (*a day on which the law authorizes or requires banks in Houston to close*, not *banks are authorized or required by law to close*);
   - digits;
   - no *should*;
   - no *shall* with a negative subject;
   - no *within*, and no *until* for an end day (MSCD 10.23; 10.25);
   - no 2nd definition of a term the contract already defines (a fix that defines *Holdback* again, differently, fails): use the existing term, or bracket a rename for Blake;
   - a Term or other period states a time of day for its start and its end (MSCD 10.33; *midnight at the beginning of* and *midnight at the end of*, 10.38), with the time zone when the parties sit in 2 zones (10.51); a *no later than [date]* deadline that decides a right (exercising an option, curing a breach, terminating, giving a notice that starts or ends a right) states a time of day and a time zone (house-style.md section 7);
   - no *from [date] through [date]*: *starting on ... and ending on ...* (MSCD 10.24); no *N days before*: *the Nth day before* or a stated date (house-style.md section 7);
   - no *stated*, *described*, *set forth*, *set out*, *specified*, or *listed in the section titled*: *under the section titled "Payment"*, or *the sale that the section titled "Consent" describes* (house rule 4);
   - for a nonparty's prohibition (*No Authorized User shall*), the restructure onto the party: *Customer shall use reasonable efforts to prevent any Authorized User from ...* with the party's liability for the loss in brackets for Blake (MSCD 3.180; 8.5); *shall cause* passes only when the nonparty is the party's instrumentality, such as its subsidiary or its own board (3.160-3.161), and fails for users, employees, or contractors (3.163); a fix that writes *No Authorized User may*, or that silently weakens the bar (*shall instruct*), fails (house rule 8);
   - *The Board shall review* and *Company shall cause the Board to* are correct for Company's own board (MSCD 3.160-3.161): rule `keep` on a finding that calls either a nonparty error and `pass` on one that offers *Company, acting through the Board, shall* as a style option;
   - for *terminate by giving N days' notice*, both questions answered: giving or receipt, and the Nth day or the N+1th (13.627; 10.65-10.66; test 5 gives the model);
   - *will*, not the present tense, for a policy about a contingent event, a matrix clause after *if*, *when*, or *unless* included (*the termination will take effect 90 days after*; *the Annual Fee will increase*; MSCD 3.334; 3.361; `verbs.md`, procedure step 6);
   - no *shall cause*, *shall ensure*, *shall require*, *shall procure*, *shall see to it*, *shall have [the nonparty] [act]*, or *shall not permit* for a nonparty the party doesn't control (MSCD 3.162-3.163; 3.176-3.177); a `better_fix` you offer must pass this test too (write the party's own act, the MSCD 3.166 *must* form, or a limited-control duty). *Shall obtain* or *shall secure* a nonparty's consent or document is a valid duty of result (MSCD 8.5), so a finding that calls it a category error is `keep`; a flag that offers the efforts alternative passes.

   Your explanations, option labels, and questions to Blake follow house style too: active voice (not *was meant*, *is intended*, *is defined*, *is bracketed*, *is stated*, *is needed*, *is required*, or *Severity lowered*; put the explanations in a 2nd .txt file and read only the lint's passive-voice and passive-hides-actor findings on it), digits (*2 readings*, not *two*), no *should*, and 2 spaces between sentences; quote the flawed words you explain. Lint only the proposed wording for the other tests, never option labels or questions. When the wording passes and only the explanation breaks a rule, the checker rules `fail` with `test` set to `explanation`, so the reviewer recasts the explanation and the fix itself still counts as correct. In blind tests, 1/3 of the failed findings failed only on their explanations.
2. **Whole problem.** The fix solves every part of the stated problem:
   - a converted duty says who acts and when (a duty converted from *is entitled to* reads *Larkspur shall pay the late charge no later than ...*);
   - an act only a nonparty can do becomes the party's duty to obtain it (*Seller shall obtain an endorsement to its policy that names Buyer as an additional insured*, not *Seller shall name Buyer*), a duty of result that puts the risk on that party (MSCD 8.5), or takes *must* on the nonparty (3.166); say which, and bracket *[shall use reasonable efforts to obtain]* if Blake's client bears the risk;
   - a change to 1 amount, percentage, or row carries to every figure that depends on it (a new price changes each installment that is a percentage of it), and the rows still don't overlap;
   - a finding about a table, form, or list fixes all of it: every amount with needless cents, every defect the form has (a missing cap as well as a wrong deduction);
   - a fix that keeps a vague term (*reasonable*, *prompt*, *adequate*, *material*, *substantial*) offers a bracketed measure and asks, or says why no measure exists; a reason that a measure would hurt a party is a business judgment and fails;
   - an amount stated twice (MSCD 1.56) ends up stated once.
3. **The deal.** Compare the fix with the original term by term. Every one of these must survive unless the finding is about it:
   - party, act, amount, period, and condition;
   - approval or vote (a rewrite that drops *by Majority Vote* changes the deal);
   - allocation (*pro rata*, *in the aggregate*), step (*try to resolve*; *before either party brings an action*), and exception;
   - whose act or receipt starts each period (a duty moved onto Landlord still runs from the property manager's receipt);
   - whom or what the provision covers (*its accountants*, not 1 named firm);
   - how often an event can recur;
   - the trigger (a duty triggered by a breach doesn't become one triggered by any claim alleging a breach).

   The fix adds, swaps, or drops no term (an exception, a cure right, a payment, a condition, a standard, a timing rule, *in writing*, a document the original doesn't name (*an endorsement*), a likelihood threshold (*could* to *would reasonably expect*), 1 defined term for another, *days* for *Business Days*, a stuffed definition's duty (move it, don't drop it), a party's option to pick a later date) unless it brackets that term for Blake. Diff the fix against the original word by word: every changed word maps to a problem the finding states, and a changed word with no problem behind it fails and goes back (*no increase may exceed 4%* and *begins on ... and ends on ..., both dates included* stay). The fix changes only the words the problem needs. A verb swap (*ends* to *terminates*) must match how the rest of the contract uses each verb. Making a person a party needs a limited-role phrase (MSCD 2.60-2.61), or a note on every *either party* provision it pulls in. On the other side's draft a broader rewrite changes their deal. If a term must change, the finding says so and puts the new term to Blake in brackets.
4. **No new problem.** The fix has no ambiguity of its own; test it for the same ambiguity it fixed:
   - a modifier before or after a list reaches 1 item or all (repeat the modifier or split the items);
   - commas don't settle scope (MSCD 12.26; 12.37; 12.74);
   - *X, Y, or both* attaches a trailing phrase to Y only;
   - a phrase that reached 2 verbs (*reject or return any shipment at Norvale's cost*) still reaches both;
   - an *and/or* repair reads *X or Y or both* (MSCD 11.90), because *including X and Y* can mean both, and 1 string of relative clauses never mixes *and* with *or* (11.96-11.100): split the sentence.

   The fix also agrees with the rest of its section and every provision on the same subject. A self-defeating precedence rule fails. So does a recast prohibition that only 1 named person's approval satisfies when another clause allows a designee. A new 1st sentence must agree with the 2nd.
5. **Options.** Where the answer is Blake's choice, each option is complete wording that is correct by itself and settles the question by itself; an option that leaves the planted question open (*for each disclosure, or once for each employee?*) settles nothing.
   - **Every reading gets wording.** There is wording for each reading the text supports, including the defined-term reading. Count the readings the finding's explanation names against the wordings it offers; a reading named but given no wording fails, whatever reason the finding gives, unless the finding names the provision that excludes that reading. For *within N days of*, before and after are 2 readings. A deadline option counts days the same way as the original (*after the 30th day* moves the 1st day by 1).
   - **Minimum notice.** A minimum-notice fix (*at least 20 days' notice*; *on 20 days' notice*; *at least 20 days before*) must offer both counts, the 20th day before and the 21st day before, and ask which the parties intend (MSCD 10.65-10.66); a fix that names only 1 day picks a reading silently. A plain deadline (*no later than 20 days before X*) gets a finding too (house-style.md section 7): its fix states the count that 10.65's convention gives, *no later than the 20th day before X*, or a stated date. A fix that offers a 2nd count (the 21st day before) invents a reading the plain deadline doesn't have, and fails test 3.
   - **Termination notice.** For *terminate by giving N days' notice*, use MSCD 13.627's model (*If Acme notifies Widgetco that it is terminating this agreement, this agreement will terminate N days after the day Widgetco receives that notice*, with giving as the alternative), and keep an *at least* minimum as a minimum (*on the date the notice states, no earlier than the [Nth] [N+1th] day after*). That fix answers 2 questions, so offer both: giving or receipt starts the period, and the period ends on the Nth day or the N+1th (10.65-10.66); an option that settles only 1 of them is a silent pick.
   - **Silent picks.** The silent picks that blind tests catch most often, each of which needs wording for every reading and a question: a period that runs from a notice (from the day the party gives it, or the day the other party receives it or the notice takes effect: a Notices clause on effectiveness doesn't settle it); *by [date]* (that day, or the day before; MSCD 10.23); a pronoun with 2 antecedents (*it*, *its*: an individual Seller or Company); and a modifier or relative clause after 2 nouns (*Raw Materials and packaging components that Supplier purchased specifically for Buyer*; *employee or contractor of Client who worked on the Services*), which is a reach question even where the finding calls the phrase a reduced passive, so recasting the passive alone doesn't settle it.
   - **Nonparty originals.** No option is the defective original or *No [nonparty] may* (house rule 8): not *shall cause*, *shall ensure*, *shall require*, or *shall not permit* for a nonparty the party doesn't control (an employee, a contractor, a manufacturer, an individual owner, or an Affiliate defined to include a parent or a sister company; MSCD 3.163), not a passive, not *until*. Where the party's direct duty or liability already allocates the risk (*Lessor is liable to Lessee for the manufacturer's late delivery*), that is the fix, not 1 of 2 choices. A nonparty duty is never fixed by deleting the provision (test 4 fails it).
   - **Conflicting numbers.** In a conflict between 2 numbers, either may be the error: check the figures that depend on them (a 1% fee of $24,000 points to a $2,400,000 Loan, not $2,500,000) and offer each number as the one that governs.
6. **In place.** The fix reads correctly in its sentence. A changed verb agrees with its subject; a renamed defined term changes at every use; no contractions (MSCD 17.37). When 2 findings change the same words (a *guaranty* to *guarantee* rename and a verb fix in the same sentence), the finding with the higher severity (the earlier pass if equal) gives 1 combined wording and the other points to it, because 2 fixes to the same sentence can't both apply as written.

## Output

Return a JSON list, 1 object per finding, in the order of `findings.json`:

```json
{"index": <finding index>, "ruling": "pass" | "fail" | "keep", "test": "<test number, or explanation, for fail>", "reason": "<1 or 2 sentences>", "better_fix": "<optional: wording that passes>"}
```

Then list every `fail` and `keep` in 1 line each.
