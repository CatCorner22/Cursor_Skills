# Changelog h12: format and code pass (no finding changes)

Baseline: `skill-r4`. Governing rule: every change here is a pure refactor or a formatting change, and the gate
passes with 0 lost and 0 gained on every corpus. Verified 3 ways: the lint self-test (2,397 cases before, 2,415
after the 18 windowing cases), `gate.sh` (PASS, 0 lost and 0 gained on all 6 keyed corpora, no change in any
share line), and a field-by-field differential of every finding, broad trigger, inventory row, and report note
over 241 corpus documents in all 3 `--whose` modes (723 runs): 0 differences.

## 1. Code refactors from the board's review

### a. STR-005 + CLR-009 declaration moves (pure move)
- Reordered `scripts/mscd_lint.py` into 12 banner sections, top down: shared constants; text utilities; reading
  the document; the document model; severity policy and findings; house-style checks; document-level checks;
  rule-database triggers; defined-term inventory; report; self-test; running the lint.
- A script moved whole top-level blocks and changed no expression. A checker then proved that the set of
  top-level nodes is identical, that the non-blank line multiset is identical apart from the banners, and that
  no module-level statement references a name defined later. Self-test passed unchanged after the move.
- CLR-009's declaration moves landed with it: `_W`, `_M` and `_FALLBACK` now sit beside `_A` in the constants
  block, ahead of the reader functions that use them, and the severity policy (`HOUSE_SEV`, `OWN_SEV`,
  `sev_is_free`, `severity_for`) now sits with `finding()` instead of under the report banner.
- CLR-009's `re.VERBOSE` rewrite of the 7 long regex lines stayed out: it edits patterns, which this pass does not.

### b. STR-004 test extraction
- Moved the case builders (`_round8_cases`, `_round9_cases`, `_round10_cases`, `_round11_cases`,
  `_round8_docx_cases`), the helpers (`_tmp`, `lint_text`, `_read_tmp`, `_refused`, `_raises`) and `self_test()`
  into the new `scripts/_lint_tests.py`, which does `import mscd_lint as L`.
- `mscd_lint.py` fell from 5,534 lines to 4,089; `_lint_tests.py` is 1,582 lines.
- `main()` now does `from _lint_tests import self_test`, so `mscd_lint.py --self-test` keeps its name, its 1-line
  output and exit 1 on failure (checked with a deliberately failing case: it printed `FAIL:` and exited 1).
- A scope-aware rewriter qualified 122 references to mscd_lint module globals with `L.`, so no test reads a stale
  copy of module state; the 2 `global` statements (`WHOSE`, `_VARIANTS`) became attribute assignments on `L`.
- The rule-id scan reads `L.__file__` and its own file, so every id cited in either file still has to exist.

### c. STR-008, CLR-003 dead code and CLR-004 names
- `keep_sev` and `ROOT` were already gone from `mscd_lint.py` (an earlier pass removed them), so STR-008 and
  CLR-003's dead-code half needed no change. CLR-003's `fallback=` rework of `severity_for` stayed out: it
  rewrites the severity policy, which is a behavior change this pass does not take.
- CLR-004: renamed the 4 local `add` closures that take different arguments to `add_para` (`_read_docx`),
  `add_outline` (`outline_checks`), `add_mismatch` (`arithmetic_checks`) and `add_front` (`front_checks`), 24
  edits in all. The shared `house_checks` closure keeps the name `add`, which every `HOUSE_SECTIONS` function
  receives. Updated the 1 comment that named the old closure.

### d. STR-007 / CLR-001 Definition record
- `definitions()` now returns `Definition`, a `typing.NamedTuple` of `term, words, para, start, end, kind, lead`.
- `lead` is the leading autonomous definition of the paragraph a definition sits in, as `AUTON` matched it, or
  `None`. `definitions()` matches it once per paragraph and carries it on every record of that paragraph, so the
  value is the same object the 3 other sites used to re-match by hand.
- Replaced the hand-rolled `AUTON.match(def_text(...))` at all 3 sites: `nonparty_named` reads `d.lead`;
  `definition_findings` builds 1 `lead_of` map and reads it twice (the obligation-in-definition loop and the
  body-paragraph filter).
- Replaced the numeric indexing (`d[0]`, `d[2]`, `d[3]`, `d[5]`) in `definitions()`, `term_of_art_checks` and
  `collect_definitions` with field names; the 6 positional unpack sites took a 7th name.
- `term_of_art_checks(paras, defs)` now takes the shared list instead of calling `definitions(paras)` again, so
  the lint makes 1 pass over the document for definitions instead of 2.
- Proof that `lead` matches the old probe: over 254 documents, `{d.para for d in defs if d.lead}` equals
  `{p['idx'] for p in paras if AUTON.match(def_text(p['text']))}`, and every record of a paragraph carries the
  same `lead`.

### e. ROB-005 windowing
- Added `tail(t, pos, n)` and `ABBREV_REACH = 12` to the text utilities, and windowed 25 `$`-anchored prefix
  searches across `clause_start`, `spacing_list_checks`, `subject_modal_checks`, `passive_checks`,
  `signature_checks`, `party_verb_checks`, `number_checks`, `policy_checks`, `usage_checks`, `reference_checks`
  and `definition_findings`. Each window exceeds its pattern's longest possible match, so the pattern still sees
  a real character where it tests a word boundary.
- In `spacing_list_checks` and `clause_start` the initial test became `(?:^|\W)[A-Z]\.$` over a 3-character
  window, exactly as ROB-005 gives it: in a 3-character window the `^` branch can only match where the full
  prefix also starts there, so the decision is unchanged.
- 6 prefix searches stayed whole, each for a reason: `serial_lists` and `reference_checks` test whether the whole
  prefix is empty or is an enumerator; `party_verb_checks` and `number_checks` have patterns with a `^` branch
  that a window would let fire early; `number_checks` and `usage_checks` read the prefix's last word after
  `rstrip()`, which a window could empty; and `in_quotation` needs the whole prefix, as ROB-005 says.
- Renamed the local `tail` in `policy_checks` to `after`, which the helper's name would otherwise shadow.
- 18 self-test cases (`_round12_cases`), 1 per windowed site, put the trigger at the far edge of its window and
  pair it with the same text without the trigger. Every expected value comes from the lint as it ran before the
  windows went in, so a window someone shrinks later fails here.
- Timing on a 200 KB single-paragraph .docx (3 runs, median): 15.00 s before, 3.36 s after, same 8 findings.

### Skipped, as the brief directs
STR-001, STR-002, STR-003, STR-006, STR-010 and CLR-002, CLR-006, CLR-007, CLR-008, CLR-010 are larger design
changes (a `DocContext` object, a data object for the loaders, a reader split, named party scopes), not refactors.

## 2. Code quality
- `ruff check scripts/`: 199 findings before, 183 after. Fixed 16: 1 unused local (`act`), 2 unused unpacked
  names (`idx`, `missing`), 1 f-string with no placeholder, 1 leaked file handle in the rule-id scan, 1
  `subprocess.run` without an explicit `check`, 1 slice that `removesuffix` says better, 1 unsorted `__slots__`,
  2 lambdas called in place (now the named `_points` helper), and 6 unparenthesized implicit string
  concatenations inside collection literals (the "did you forget a comma?" smell; the strings are unchanged).
- Left on purpose, with the reason: 133 `FURB167` (`re.I` is a standard-library alias for `re.IGNORECASE`, used
  consistently at 133 sites; swapping it is churn, not a defect fix); 11 `BLE001` and 4 `S110`/`S112` (the
  documented best-effort policy of the .docx reader, which records the failure in `meta` instead of stopping);
  11 `I001` (ruff's isort fix would rewrite every compact 1-line import into a multi-line block, against the
  file's style); 10 `SIM905` (the word tables are written as 1 string on purpose); 8 `RUF100` (the
  `# noqa: E402` comments are needed wherever E402 is enabled, and this invocation does not enable it); 5
  `EXE001` (the scripts run as `python3 scripts/<name>.py`, so the executable bit buys nothing); 1 `UP012` (the
  explicit `'utf-8'` is what the mixed-encoding test is about). No bare `except:` and no shadowed builtin exist.
- Every script keeps its module docstring, and `mscd_lint.py`, `coverage.py`, `rules_query.py` and
  `build_references.py` each keep a working `--help`. `_lint_tests.py` is an internal module, like `_cli.py` and
  `_rules_data.py`, so it has a docstring and no CLI.

## 3. Format: SKILL.md and the references
- SKILL.md: 187 lines before, 190 after, under the 200-line cap. All 20 reference files appear in its "Read it
  when" table, each with a sentence saying when to open it; no wording changed.
- Contents lists for the 5 generated references over 300 lines (`verbs.md`, `words-to-avoid.md`,
  `ambiguity-catalog.md`, `structure.md`, `vagueness.md`) went into their `scripts/ref_headers/` headers, not the
  generated files. `look-alikes.md`, which is hand-written, already had one.
- Markdown hygiene, SKILL.md and `references/*.md`: added a blank line before 48 lists and 1 table (3 in
  SKILL.md, 7 in `comment-templates.md`, 29 in `fix-patterns.md`, 8 plus the table in `house-style.md`, 1 in the
  `time-and-numbers.md` header); tagged 4 untagged fenced blocks as `text` (3 in `comment-templates.md`, 1 in
  `rule-database.md`). No trailing whitespace, no tab, 1 `# h1` per file, and no heading level skips remain.
- 2 flags left alone as false alarms: the 2-line bullets in `look-alikes.md` whose second line starts `A. `,
  which Markdown reads as a lazy continuation of the list item, not a new list.

## 4. Gate output
- `mscd_lint.py --self-test`: 2,415/2,415 passed (2,397 before, plus 18 windowing cases).
- `coverage.py --self-test`: 13/13 passed.
- `build_references.py` then `diff -rq` against the copy taken first: the only differences are the contents
  lists added to the 5 headers and the 1 blank line in the `time-and-numbers.md` header. A second rebuild
  changes nothing.
- `gate.sh skill-r4-h12 skill-r4`: **PASS**. All 6 keyed corpora read `lost 0, gained 0`, every trap count is
  unchanged, and all 3 share lines are identical. The description is 991 characters.
- `build_zip.sh`: builds and lists 50 entries, 1 more than the baseline's 49, the new `scripts/_lint_tests.py`.
