# Active voice

**House rule: active voice only, in every sentence and clause.** Read `house-style.md` section 1 for the recast patterns (unknown actor, legal fiction, amendment, party action, *solicit ... to accept employment* for *to be hired*, MSCD's concluding clause as *the date that the introductory clause states*) and the contingencies (linking verbs and adjectival participles aren't passive; quoted text stays; never change meaning to satisfy the rule).

## How to detect the passive

A passive verb is a form of *be* (or *get*) plus a past participle, with the actor either missing or in a *by* phrase: *is delivered*, *will be paid*, *has been terminated*, *shall be deemed*. `scripts/mscd_lint.py` flags candidates; confirm each one by asking "who does this?" If the sentence names no doer of the action, it is passive.

Not passive: *is void*, *is effective*, *is liable*, *is entitled*, *is responsible* (linking verb plus adjective); *the attached form* (participle as adjective).

MSCD's own rules below still matter: they explain why the passive hides the actor (3.15) and how to rephrase buried-actor policies (3.336-3.338). The MSCD allowances for the passive carry the HOUSE mark.

> **Book examples are in MSCD5's style, not house style.** They may use lowercase *schedule*, *1 January 2024*, spelled-out numbers, 1.1 numbering, *the* before party names, or a passive that MSCD accepts. Restate any example in house style (`house-style.md`) before you put it in a contract or a comment. For the other side's drafts, the house rule is to flag everything, whatever a rule's "let-pass" or "style-only" label says.


## Rules (18, generated from `data/rules.jsonl`)

Format: id, severity (1 = ambiguity or meaning-changing; 2 = vagueness or dispute risk; 3 = style), the rule, and its MSCD paragraphs and PDF page. `HOUSE` marks a rule that Blake's house style changes: apply the house rule. For a rule's full record (test, fix, exceptions, verified book examples), run `python3 scripts/rules_query.py --id <id>`.


### Chapter 3: General Considerations

- **R-3.15-active-voice** [sev 3] Use the active voice unless there's a clear benefit to the passive; in particular, use the active voice to express action by a party. The passive adds words (with a by-agent) and disrupts subject-verb-object order. (3.13, 3.15; PDF p. 131)
  - Look for: passive verb with a party as by-agent
  - Fix: Make the actor the subject.
  - Book example: The rent shall be paid by the Tenant on the first of every month. → The Tenant shall pay the rent on the first day of every month.
- **R-3.14-passive-definition** [sev 3] Recognize the passive voice: the subject is acted on (The peach was eaten by Marie); the would-be active subject becomes the 'by-agent,' which can be omitted (The peach was eaten). (3.14; PDF p. 131)
  - Look for: form of be + past participle
- **R-3.15-passive-hides-actor** [sev 1] Don't use a passive verb without a by-agent to express what a party does or must do; it hides the actor, and the consequences can be drastic. (3.15, 3.16, 3.17...; PDF p. 131)
  - Look for: passive verb with no by-agent describing party action (is terminated, shall be delivered, must be given)
  - Fix: State the actor: If Acme terminates Player's employment ...
  - Book example: If Jason Player's employment with Buyer is terminated prior to two years from the date of this Agreement for any reason other than a for cause termination, this Non-Compete Agreement will no longer be binding. → (see fix)
- **R-3.23-passive-appropriate** [sev 3] The passive may be appropriate if the by-agent is a nonparty or isn't a person, or if leading with the thing acted on keeps the focus where it belongs. (3.23, 3.24, 3.25...; PDF p. 131)
  - HOUSE: Active voice only. Recast passives: name the actor (any Person if unknown); legal fictions as 'This agreement treats X as' or a linking verb ('will be effective'; will, because a notice is a contingent future event, MSCD 3.334); amendments as 'The parties hereby amend Section 4 (Payment) of the Original Agreement to read as follows'; 'solicit any employee of Company to accept employment with a competitor', never 'to be hired' (or employed, engaged, retained). See house-style.md section 1.
  - Book example: (none) → if a Necessary Project Approval is revoked
  - Book example: (none) → No party will be bound by this amendment until the Parent, the Borrowers, and the Required Lenders have signed a counterpart.

### Chapter 3: Language of Performance

- **R-3.56-performance-active** [sev 1] Always use the active voice in language of performance, to make the actor clear. (3.56; PDF p. 143)
  - Look for: hereby + passive verb
  - Book example: [1-1c] ××: The Assets are hereby purchased from Jackson. → [1-1] ✓✓: Acme hereby purchases the Assets from Jackson.

### Chapter 3: Language of Obligation

- **R-3.148-passive-missing-actor** [sev 1] Don't express a party's obligation with a passive verb that omits the by-agent (The Consultant must be reimbursed); state who owes the duty, preferably in the active voice. (3.148, 3.158, 3.159; PDF p. 166)
  - Look for: passive obligation (must/shall/will be + past participle) with no by-agent
  - Book example: [3-2] ×: The Consultant must be reimbursed for all authorized expenses. → [3-2f] ✓✓: The Company shall reimburse the Consultant for all authorized expenses.
  - Book example: [3-2a] ××: The Consultant shall be reimbursed for all authorized expenses. → [3-2f] ✓✓: The Company shall reimburse the Consultant for all authorized expenses.
- **R-3.168-no-receive** [sev 1] Don't use receive to impose a duty on someone other than the subject (Jones shall receive a salary); like the passive, it doesn't say who pays. Use shall on the actor. (3.151, 3.168; PDF p. 172)
  - Book example: [3-7a] ××: Jones shall receive a salary of $100,000 a year. → [3-7d] ✓✓: Widgetco shall pay Jones a salary of $100,000 a year.
  - Book example: [3-7b] ××: Jones will receive a salary of $100,000 a year. → [3-7d] ✓✓: Widgetco shall pay Jones a salary of $100,000 a year.
- **R-3.159-active-voice-obligation** [sev 3] Usually better than must: don't impose a duty on someone other than the subject; use the active voice with the obligated party as subject. (3.158, 3.159; PDF p. 166)
  - Look for: passive obligation with a party as by-agent
  - Book example: [3-1] ✓: Notice of any claim must be given by the Indemnified Party to the Indemnifying Party. → [3-1e] ✓✓: The Indemnified Party shall notify the Indemnifying Party of any claim.

### Chapter 3: Language of Discretion

- **R-3.206-may-active-voice** [sev 3] Don't use may with a passive verb; make the party with discretion the subject. (3.206; PDF p. 180)
  - Book example: [4-2] ✓: The Option may be exercised by Smith before 1 January 2024. → [4-2b] ✓✓: Smith may exercise the Option before 1 January 2024.
  - Book example: [4-2a] ✓: The Option may be exercised before 1 January 2024. → [4-2b] ✓✓: Smith may exercise the Option before 1 January 2024.
- **R-3.295-active-after-not-required** [sev 3] Use the active voice after is not required to. (3.295; PDF p. 199)
  - Book example: [6-3] ×: Amounts collected from Participants are not required to be held in a segregated account. → [6-3a] ✓✓: Widgetco is not required to hold in a segregated account any amounts collected from Participants.

### Chapter 3: Language of Policy

- **R-3.336-buried-actor-policies** [sev 1] Rephrase buried-actor policies (exercisable, payable, recoverable) as language of obligation, language of discretion, or a conditional clause; they often omit the responsible party, and The fee is payable by 20 April could mean an obligation, discretion, or a condition. (3.336; PDF p. 213)
  - Book example: [8-7] ✓: Interest is payable at a rate of 8% per year. → [8-7b] ✓✓: The Borrower shall pay interest ... .
  - Book example: [8-7a] ××: Interest shall be payable ... . → [8-7b] ✓✓: The Borrower shall pay interest ... .
- **R-3.337-no-is-due** [sev 2] Rephrase is due as language of obligation. (3.337; PDF p. 213)
  - Book example: The First Installment is due by 1 March 2024. → The Purchaser shall pay the First Installment by 1 March 2024.
- **R-3.339-passive-in-policy** [sev 3] The passive voice in language of policy is unremarkable; where the missing by-agent is the world at large, prevent any implication that someone must act by adding automatically or by switching to an active verb with the same subject. (3.339, 3.340; PDF p. 213)
  - HOUSE: Active voice only. Recast passives: name the actor (any Person if unknown); legal fictions as 'This agreement treats X as' or a linking verb ('will be effective'; will, because a notice is a contingent future event, MSCD 3.334); amendments as 'The parties hereby amend Section 4 (Payment) of the Original Agreement to read as follows'; 'solicit any employee of Company to accept employment with a competitor', never 'to be hired' (or employed, engaged, retained). See house-style.md section 1.
  - Exceptions: Don't switch will be deemed to the active voice (3.340; 13.209-.210).
  - Book example: the Option Price will be increased → the Option Price will increase

### Chapter 10: References to Time

- **R-10.19-no-date-notified** [sev 3] Don't use the date notified; say the date that ABC specifies by notice to XYZ. (10.19, 10.20; PDF p. 472)
  - Book example: "First Hand Date" means the date notified by ABC to XYZ upon which the first hand of poker is played ... → (see fix)

### Chapter 13: Selected Usages

- **R-13.209-deem-will-passive** [sev 3] Use deem with will, not shall (Any notice will be deemed to have been received on delivery), and in the passive, not the active voice (not The parties will deem). (13.209, 13.210; PDF p. 624)
  - HOUSE: Active voice only. Recast passives: name the actor (any Person if unknown); legal fictions as 'This agreement treats X as' or a linking verb ('will be effective'; will, because a notice is a contingent future event, MSCD 3.334); amendments as 'The parties hereby amend Section 4 (Payment) of the Original Agreement to read as follows'; 'solicit any employee of Company to accept employment with a competitor', never 'to be hired' (or employed, engaged, retained). See house-style.md section 1.
  - Test: Has-a-duty test: substitute 'has a duty to'; shall be deemed fails.
  - Fix: will be deemed
- **R-13.730-regard-shall-be-had** [sev 3] Don't use regard shall be had to (passive, with a shall that fails the has-a-duty test); one approach is the active voice with take into account, consider, or include. (13.730, 13.731; PDF p. 745)
  - Fix: [the actor] shall take into account / consider / include
- **R-13.840-referring-to-termination** [sev 1] Be careful how you refer to termination. If the contract states its term with the noun term, refer explicitly to both the end of the term and party termination if you mean both (better, refer to the sections). If you mean only termination without party action, refer to those sections. If you mean only termination by a party, use the active voice (if either party terminates this agreement), not if this agreement is terminated. (13.840, 13.841, 13.842...; PDF p. 771)
  - Test: Does the reference mean end of term, termination by a party, or both? Can a disgruntled party argue end of term is expiration?
  - Fix: if either party terminates this agreement; on termination of this agreement under section 9.2 or 9.3

### Chapter 17: Drafting as Writing

- **R-17.7-buried-verbs** [sev 3] Whenever possible, use strong verbs instead of abstract nouns (buried verbs, nominalizations) or adjectives; they make prose bureaucratic, add prepositions and weak verbs, and let the drafter drop the actor. (17.7, 17.8, 17.9; PDF p. 847)
  - Look for: abstract noun ending -tion/-ment/-ance with a weak verb
  - Fix: Immediately after Acme issues the Notes; If Smith fails to timely pay the Purchase Price; If this section violates any law; is liable
  - Exceptions: Buried verbs are useful when dropping the actor helps (Upon exercise of the Option) (17.10).
  - Book example: Immediately following issuance of the Notes → Immediately after Acme issues the Notes
  - Book example: If this section is violative of any law → If this section violates any law
