# Contract corpus: a regression suite for mscd-contracts

50 contracts with planted problems and answer keys, built in November 2026 to test the skill end to end, in 2 rounds. Helpers who never saw the skill's code wrote them, so the test isn't tailored to the lint. Round 1 (c01-c26) shaped the fixes; round 2 (c27-c50) was written afterward, aimed at what round 1 didn't cover, and run blind before any round-2 fix.

| Tier | Contracts | Planted problems | What it tests |
|---|---|---|---|
| obvious | 8 legacy templates (c01-c04, c14-c17) | 12 to 21 each | recitals, here-words, *shall* everywhere, spelled-out numbers, provisos, *and/or*, numbered cross-references, wrong attachments, bad formatting |
| mixed | 9 modern drafts (c05-c09, c18-c21) | 10 to 12 each | category errors, defined-term problems, attachment misclassification, time ambiguity, reduced passives, party articles |
| sneaky | 9 clean-looking drafts (c10-c13, c22-c26) | 5 or 6 each | syntactic, referential and scope ambiguity; conflicts; a hidden negative subject; nonparty duties; an obligation inside a definition |
| round 2: obvious | 6 legacy templates (c27-c32) | 16 to 19 each | the round-1 kinds, plus money in words and digits that disagree, a date in a page header, Word automatic numbering with an only child, a price table with problems in its cells |
| round 2: mixed | 8 drafts (c33-c40) | 10 to 13 each | an existing reviewer's comments, a form labeled as a schedule, mixed efforts standards, *may not* with an affirmative subject, *is entitled to* hiding a duty, an impossible date, a wrong weekday, *he or she*, a wrong total in a fee table |
| round 2: sneaky | 10 drafts (c41-c50), 2 of them 1,700 to 1,900 words | 4 to 6 each | each-or-aggregate caps, *respectively* misused, circular and conflicting definitions, a schedule that uses a defined term differently from the body, *or* versus *and* in a prohibition, an escrow agent that does sign, a numeric date in a footer |

Round 1 has 303 planted problems and 117 **traps**; round 2 has 240 and 106 (543 and 223 in all). Traps are text that looks wrong but is right under MSCD and the house rules (*is not required to*, *500 Third Avenue*, *work made for hire*, *the Receiving Party*, a statute-required MERCHANTABILITY disclaimer; in round 2 also *Twelve Oaks Mall*, *February 29, 2028*, a section I. after H., the house section line). The formats cover .docx (including 1 file with another author's tracked changes, 1 with a content control and 2 with tables), .txt and .md.

## Files

- `contracts/`: the 26 contracts.
- `keys/<id>.json`: each key lists `issues` (type, exact `anchor` text that occurs once, quote, severity, why, fix; a conflict may add `alt_anchors` for its other end) and `traps` (anchor, why it's correct). An issue in a page header or footer has `"where": "header"` or `"footer"`. See `../../references/rule-database.md` for the rules the keys cite.
- `score.py`: the scorer.
- `results/`: scores from earlier runs, with what each run changed.

## Running it

```
python3 evals/corpus/score.py check                # every anchor occurs exactly once
python3 evals/corpus/score.py lint                 # score scripts/mscd_lint.py on all 26
python3 evals/corpus/score.py findings <runs-dir>  # score skill runs: <runs-dir>/<id>/findings.json
```

For a skill run, give each contract to the skill in Review mode and have it write `findings.json`: a list of `{"quote", "type", "severity", "fix", "source"}`, where `quote` is exact contract text and `fix` is the proposed wording or `keep`.

**Trap scores need a human look, and so do misses.** A document-level finding (decimal numbering, say) may quote a different spot than the key's anchor, and the scorer counts it as a miss. The scorer counts a trap as wrongly flagged when a finding aimed at it (the trap is at least half of the quote) proposes wording without the trap's words. A correct finding about a *different* problem in the same words (a party article in *The Company is not required to*, say) still counts, so read each flagged trap before treating it as a real false alarm.

## Key corrections

The generators listed 4 traps that MSCD treats as problems; the keys now list them as issues: *third party* twice (MSCD 13.875), and *is entitled to* used to hide another party's duty twice (MSCD 3.169).

## Results, November 6, 2026

| Run | Problems found | Traps wrongly flagged | Notes |
|---|---|---|---|
| Lint before the corpus fixes | 115 of 131 lint-detectable (88%) | 36 of 119 | |
| Lint after | 184 of 185 lint-detectable (99%); 241 of 303 overall | 1 of 117 (a correct flag next to the trap) | 32 signature-phrase checks, outline check, front checks, inventory upgrades |
| Full skill, run 1 (all 26) | 303 of 303 after reading each miss (the scorer's strict match said 301) | 1 real (*promises to pay* changed in a negotiable note), 3 minor (*one-time* dropped twice while fixing another problem; *date* changed to *day*); the other 22 flagged were correct findings on other problems in the same words | 6 helpers; about 84,000 tokens and 5.8 minutes per contract |
| Full skill, run 2 (8 of the 26, after the run-1 fixes) | 114 of 114 after reading each miss (the scorer said 112; both misses were document-level enumeration findings quoted at another spot) | 0 real; 1 minor (an acceptable *must take place* still got a suggested recast); the other 8 flagged were correct findings on other problems in the same words | 2 helpers; about 72,000 tokens and 4.4 minutes per contract, but the brief no longer asked for `report.md`. 3 real problems the keys didn't plant: an amortization gap, a lease that expires before its amendment takes effect, and a trailing-modifier ambiguity. Details: `results/2026-11-06-skill-run-2.md` |
| Lint after the run-2 fixes (stricter scorer: a finding must answer the problem's type) | 184 of 185 lint-detectable; 245 of 303 overall (81%) | 1 of 117 (the same correct adjacent flag) | 1 severity policy; efforts standards split by rule, plus a mixed-standards check; section headings; *this Agreement*; *within ... after* separated from *within ... of*; inventory findings now point at their 1st occurrence |
| Round 2, lint, blind | 110 of 125 lint-detectable; 177 of 240 overall (74%) | 2 of 106 (*Twelve Oaks Mall*; a schedule heading read as an undefined term) | the skill as it stood before round 2 |
| Round 2, full skill, run 3 (all 24, blind; 2 as redlines) | 240 of 240 | 0 real; 1 borderline (*Client shall terminate the campaign if* got a question about its category); the other 8 flagged were correct findings on other problems in the same words | 6 helpers; about 83,000 tokens and 5.0 minutes per contract. Both redlines passed validation. Details: `results/2026-11-06-skill-run-3.md` |
| Lint after the round-2 fixes | 309 of 310 lint-detectable; 466 of 543 overall (86%): 255 of 303 in round 1, 211 of 240 in round 2 | 1 of 223 (the same correct adjacent flag) | reads headers, footers and Word's automatic numbering; 11 new checks (words and digits that disagree, impossible dates and wrong weekdays, nonparty duties, obligations inside definitions, lowercase defined terms, termination by notice and others); fixes for the false alarms the reviewers reported |
