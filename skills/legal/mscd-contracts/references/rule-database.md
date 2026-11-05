# The rule database (`data/rules.jsonl`)

One JSON object per line, one MSCD rule per object: 1,338 records built from a full reading of MSCD5 (first printing, with the second-printing correction to 11.106 applied) plus the verified blog riders and proposals. The lint script and the lookup script read it at runtime, so a new record takes effect at once.

## Fields

| Field | Meaning |
|---|---|
| `id` | `R-<first paragraph>-<slug>`; riders `R-rider-...`; proposals `R-proposal-...` |
| `paras`, `pdf_pages`, `chapter`, `section` | Where the rule lives in MSCD5 (PDF page numbers of the first printing) |
| `topic`, `key_items` | Grouping; `key_items` marks active-voice, words-to-avoid, verbs, attachments, standard-english, ambiguity, vagueness |
| `kind` | rule, test, exception, definition, usage-verdict, ambiguity-cause, method |
| `statement` | The rule as one instruction |
| `trigger` | `words` (literal phrases that should prompt a check), `signal` (what to look for when no word triggers it), `regex_hint` (Python regex for candidate text) |
| `test`, `fix`, `exceptions` | How to decide; what to write instead; every condition that changes the outcome |
| `severity` | 1 ambiguity or meaning-changing error; 2 vagueness or dispute risk; 3 style |
| `counterparty_review` | MSCD's advice for the other side's draft (`flag`, `let-pass`, `style-only`). Blake's house rule treats every rule as `flag` |
| `examples` | The book's own before-and-after text. `verified: true` means the text was found in the book's page text or image transcriptions; otherwise don't quote it as the book's wording |
| `status` | `book`, `rider`, `proposal`, `elaboration` |
| `notes` | Book errors, rating-legend caveats, sources and post dates |

`data/house-overrides.json` lists every record a house rule supersedes or adds to; both scripts apply it.

## Querying

```
python3 scripts/rules_query.py --id R-11.90-no-and-or
python3 scripts/rules_query.py --word "provided that"
python3 scripts/rules_query.py --para 5.95
python3 scripts/rules_query.py --kind ambiguity-cause --brief --limit 80
python3 scripts/rules_query.py --key attachments
```

## Adding a rider (the refresh step)

1. Read the new post and confirm it changes or adds to MSCD5 (not just floats an idea).
2. Append a record with `status: "rider"`, the post's URL, date and a verbatim key quotation in `notes`, and the MSCD paragraphs it changes in `paras`.
3. If it supersedes a book rule, say so in that rule's `notes`.
4. Run `python3 scripts/build_references.py` to regenerate the reference lists, and add the rider to `references/riders.md` with the new swept-through date.
5. Run `python3 scripts/mscd_lint.py --self-test`.
