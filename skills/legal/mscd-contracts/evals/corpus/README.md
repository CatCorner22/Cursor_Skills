# Contract corpus: a regression suite for mscd-contracts

26 short contracts with planted problems and answer keys, built in November 2026 to test the skill end to end. 2 helpers wrote them without seeing the skill's code, so the test isn't tailored to the lint.

| Tier | Contracts | Planted problems | What it tests |
|---|---|---|---|
| obvious | 8 legacy templates (c01-c04, c14-c17) | 12 to 21 each | recitals, here-words, *shall* everywhere, spelled-out numbers, provisos, *and/or*, numbered cross-references, wrong attachments, bad formatting |
| mixed | 9 modern drafts (c05-c09, c18-c21) | 10 to 12 each | category errors, defined-term problems, attachment misclassification, time ambiguity, reduced passives, party articles |
| sneaky | 9 clean-looking drafts (c10-c13, c22-c26) | 5 or 6 each | syntactic, referential and scope ambiguity; conflicts; a hidden negative subject; nonparty duties; an obligation inside a definition |

There are 303 planted problems and 117 **traps**: text that looks wrong but is right under MSCD and the house rules (*is not required to*, *500 Third Avenue*, *work made for hire*, *the Receiving Party*, a statute-required MERCHANTABILITY disclaimer). The formats cover .docx (including 1 file with another author's tracked changes, 1 with a content control and 2 with tables), .txt and .md.

## Files

- `contracts/`: the 26 contracts.
- `keys/<id>.json`: each key lists `issues` (type, exact `anchor` text that occurs once, quote, severity, why, fix) and `traps` (anchor, why it's correct). See `../../references/rule-database.md` for the rules the keys cite.
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
| Lint after the run-2 fixes | 184 of 185 lint-detectable; 249 of 303 overall (82%) | 1 of 117 (the same correct adjacent flag) | 1 severity policy; efforts standards split by rule, plus a mixed-standards check; section headings; *this Agreement*; *within ... after* separated from *within ... of*; inventory findings now point at their 1st occurrence |
