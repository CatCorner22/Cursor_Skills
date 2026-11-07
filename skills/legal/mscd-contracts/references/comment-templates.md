# Comment and report templates

Blake wants to understand why each change is right, so internal comments always explain the grammar or mechanism behind a fix, not just the fix. External comments (to the other side) stay short and neutral, but still cite MSCD so the reader can look it up: Blake's aim is to educate.

**2 forms, never mixed.** Every comment in a file uses the internal form (for Blake) or the external form (for the other side), never both. The internal form opens with a bracketed label: `[Sev N · effect · source]`, where the effect is 1 of *Clarifies meaning*, *Decision needed*, *Style only*, or *Flag; keep*. The external form has no label, no severity, and no internal reasoning about positions; it cites the rule as *MSCD 3.324* (spell out *A Manual of Style for Contract Drafting (MSCD)* in the 1st comment of the file). When a file with internal comments is going to the other side, deliver a 2nd copy with external comments.

## Internal comment (to Blake)

```
[Sev 2 · Clarifies meaning · MSCD 11.90-11.95] "and/or"
"Acme shall purchase Widget A and/or Widget B" states the duty 2 ways at once: Acme must buy at least 1 widget, and it may buy both (11.93).
Fix: "Acme shall purchase Widget A or Widget B and may purchase both."
Why: X and/or Y means X or Y or both (11.90). In an obligation, that meaning splits into a duty (buy 1) and a discretion (buy both); giving each its own verb states each category plainly. With 3 or more items, and/or is also ambiguous between the inclusive and exclusive or (11.94), and that is severity 1.
```

Fields, in this order: severity; effect (*Clarifies meaning*, *Decision needed*, *Style only*, or *Flag; keep*); source; the quoted words; for an ambiguity, each meaning; the fix; the mechanism. Add `Decision needed:` when the fix needs a business term or a choice of meaning, and offer 1 wording per option.

## External comment (to the other side)

```
Suggest "Acme shall purchase Widget A or Widget B and may purchase both," so the sentence states the duty and the choice separately (A Manual of Style for Contract Drafting (MSCD) 11.93).
```

1 or 2 sentences; no labels; no lecture; never "you should." Use the suggestion form ("Suggest ...", "We propose ...").

## Examples

**Negative subject with shall (house rule; 3.324)**
- Internal: `[Sev 1 · Clarifies meaning · MSCD 3.324; house rule 8] "Neither party shall assign" — Under the has-a-duty test this reads "neither party has a duty to assign," which states an absence of duty, not a prohibition. Fix: "Neither party may assign". Why: with a negative subject, may negates the permission itself, so the sentence forbids the act.`
- External: `Suggest "Neither party may assign," so the sentence prohibits assignment rather than stating that neither party has a duty to assign (MSCD 3.324).`

**should (3.360)**
- Internal: `[Sev 2 · Style only · MSCD 3.358-3.360; house rule 12] "If Acme should exercise the Option" — should adds only tentativeness to a condition. Fix: "If Acme exercises the Option". Why: a conditional clause states a future event in the simple present; the modal adds nothing but doubt.`

**Passive voice that hides the actor (house rule 1; MSCD 3.15)**
- Internal: `[Sev 2 · Clarifies meaning · MSCD 3.15; house rule 1] "The Shares will be issued at Closing" — the sentence hides who issues them, so it doesn't say who has the duty. Fix: "Acme shall issue the Shares at Closing". Why: in the passive the actor drops out; naming Acme as subject also lets the verb carry the category (shall = Acme has a duty to).`

**Number words (house rule)**
- Internal: `[Sev 2 · Style only · house rule 2] "five (5) Business Days" — words and digits say the same thing twice and can conflict (MSCD 14.5-14.11). Fix: "5 Business Days".`

**Schedule versus exhibit (5.72-5.73)**
- Internal: `[Sev 2 · Style only · MSCD 5.72-5.73; house rule 6] "Schedule C (Form of Escrow Agreement)" — a form of agreement is a stand-alone document, so it is an exhibit. Fix: "Exhibit 1 (Form of Escrow Agreement)", update every reference, and move it after the schedules (5.75).`

**represents and warrants on the other side's draft (3.459-3.463)**
- External: `To make clear that the choice of verb doesn't limit remedies, suggest adding: "The verb that this agreement uses to introduce a statement of fact does not affect the remedies available for inaccuracy of that statement of fact." (MSCD 3.459-3.463)`

**Repeated change**
- `[Sev 2 · Style only · house rule 2] Changed 14 spelled-out numbers to digits: sections titled "Term", "Payment", "Notices" ... (1 comment covers all).`

## Review report (Review mode)

```
# MSCD review: <contract name>
As of <date> · rules: MSCD5 with riders through <swept-through date>; Blake's house style
Summary: <n> findings (<n1> must fix, <n2> fix, <n3> style); the 3 to 5 findings that matter most, in 1 line each.

| # | Where | Text | Problem (meanings, for an ambiguity) | Fix | Why (mechanism) | Source | Sev | Decision? |
|---|---|---|---|---|---|---|---|---|

House-rule departures from MSCD applied: <list>.
Open questions for Blake: <list>.
```

Sort by severity, then by location. Group a repeated finding into 1 row with every location. Keep wording cleanup, ambiguity fixes, and substantive changes in separate groups, so a reader can see what changes meaning.
