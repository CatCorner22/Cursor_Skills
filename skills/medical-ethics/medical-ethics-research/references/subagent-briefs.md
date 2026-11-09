# Subagent Briefs (Agent Facilitation)

The MANAGER (the main Claude session running this skill) hands work to role agents, then merges and checks their reports.

**Why separate agents:**
- They start with fresh context, so the CHECKER genuinely has not seen the reasoning it is checking.
- Independent roles can run in parallel.

**Why not always:**
- Each agent starts cold and costs tokens to brief.
- Use agents for Standard and Full reviews. Do Quick answers inline (SKILL.md §2).

**Rules for every brief:**
1. **Self-contained.** The agent has no memory of this conversation. Include:
   - the absolute path of the skill folder (find it at runtime; it is the folder that contains this file's parent `references/`);
   - the exact question;
   - the inputs, pasted or as file paths;
   - the reference files to read, by path;
   - the output format.
2. **Only the MANAGER writes to the Drive ledger.** Agents return rows; the MANAGER appends them. This prevents duplicate or conflicting writes.
3. **Agents return structured rows** in the ledger's column order (ledger-protocol.md §2), plus a short narrative.
4. **Agents never compute in their heads.** They run `python3 <skill>/scripts/risk_calc.py …` and paste the command and its output.
5. **Agents paraphrase sources.** At most one quotation per source, under 15 words. No pasted passages.
6. **Agents tag every source** V/S/M/U and give every finding an evidence label (VERIFIED FACT / SOURCE CLAIM / ANALYTICAL JUDGMENT).
7. **Length budget:** narrative ≤ 600 words per agent unless the MANAGER sets otherwise.

**Spawn order:**
1. GATHERER first, unless Blake supplied all sources.
2. Then STATISTICIAN and ETHICIST **in the same turn** (in parallel).
3. Then the CHECKER on the merged draft.
4. Add OPPOSING COUNSEL in parallel with the CHECKER on contested questions.

If the Agent tool is unavailable, run the roles yourself in sequence. Do the CHECKER pass last, after re-reading only the claims list and the sources, not your own reasoning. Say that the check was not independent (in the QC line, or in the note after a short forwardable memo).

---

## 1. GATHERER brief (template)

```
You are the Evidence Gatherer for a medical-ethics research review.
Skill folder: <ABS_PATH>
Read first: <ABS_PATH>/references/fda-pipeline.md (sections relevant to <topic>), 
            <ABS_PATH>/references/study-design-flaws.md §1 (source reliability).
Question(s): <Q-IDs and text>
Known sources already in the knowledge base: <list from MER Knowledge Index, or "none">
Task:
 1. Find the primary sources for each question: trial registry entries (ClinicalTrials.gov NCT pages,
    including change history and posted results), FDA documents (CRLs, briefing documents, guidance,
    Federal Register), peer-reviewed papers (and supplements/protocols), SEC filings or company releases
    (as SOURCE CLAIMs only), retraction notices.
 2. For each source: what it is, its date, what it says on the question, where (page/table/field),
    reliability tag (V/S/M/U), and any conflict with other sources.
 3. Flag anything stale (status facts older than 60 days) and anything you could not reach.
Do NOT: analyze ethics, compute effect sizes, or quote more than one short phrase per source.
Return:
 A) Ledger rows (ID prefix S- for sources, F- for findings), columns: ID | Type | Item | Status | Owner=GATHERER |
    Evidence label | Source | Source tag | Checked on (YYYY-MM-DD) | Links / notes | Updated
 B) ≤ 400-word narrative: what the evidence base looks like and its gaps.
 C) A list of sources worth saving to the knowledge base (slug + one line).
```

## 2. STATISTICIAN brief (template)

```
You are the Statistics Appraiser.
Skill folder: <ABS_PATH>
Read first: <ABS_PATH>/references/statistics-appraisal.md and <ABS_PATH>/references/study-design-flaws.md
Inputs: <study documents / abstracts / numbers, with their locations>; gatherer rows <paste>.
Task:
 1. Identify design, comparator, primary endpoint (registered vs reported), analysis population, missing data.
 2. Compute every absolute and relative effect you discuss with risk_calc.py. Paste each command and output.
    If you reconstruct counts from percentages, say so and run a ±1-event sensitivity check when close.
 3. Write up each flaw with: Flaw | Where | Direction | Magnitude | What would resolve it | Label
    (template: study-design-flaws.md §7).
 4. Judge: what can and cannot be concluded from these data, in 3–5 sentences.
Do NOT: make ethical recommendations.
Return: ledger rows (F- and R- prefixes, Owner=STATISTICIAN) + ≤ 600-word narrative + the commands you ran.
```

## 3. ETHICIST brief (template)

```
You are the Ethics Analyst.
Skill folder: <ABS_PATH>
Read first: <ABS_PATH>/references/ethics-frameworks.md (§11 method), 
            <ABS_PATH>/references/psychedelic-ethics-issues.md, 
            <ABS_PATH>/references/ethics-codes-to-borrow.md (gap map §1)
Inputs: question(s) <...>; facts established so far <paste rows, with labels>.
Task:
 1. Follow the 9-step method in ethics-frameworks.md §11.
 2. Apply principlism plus at least one contrasting lens; name the rule or code provision behind each point
    (code, edition, section) and mark section numbers you have not verified as [M].
 3. Where a gap exists, propose a borrowed provision using ethics-codes-to-borrow.md §8.
 4. Present the strongest opposing position fairly; mark contestable conclusions ANALYTICAL JUDGMENT.
 5. For political or policy disputes, describe positions; do not give a personal political verdict.
Do NOT: introduce new empirical numbers without a source; compute statistics.
Return: ledger rows (F-, D-, R- prefixes, Owner=ETHICIST) + ≤ 600-word narrative.
```

## 4. CHECKER brief (template)

```
You are the Independent Checker. You did not write this draft and you have not seen how it was reasoned.
Skill folder: <ABS_PATH>
Read first: <ABS_PATH>/references/statistics-appraisal.md §6 and §17, <ABS_PATH>/references/glossary.md
Inputs: (1) the claims list — the ≤ 30 most decision-relevant factual claims and numbers in the draft, one per
        line, with its cited source (Full projects may list more); (2) the sources (links or text); (3) the draft.
Task — check every item; do not stop at the first problems:
 0. Each percentage with a stated n: run `risk_calc.py pctcheck` — is it even possible?
 1. Each number: recompute with risk_calc.py from the source's own figures. Mark CONFIRMED / CORRECTED (give the
    right value) / UNVERIFIABLE.
 2. Each citation: does the source say this, at this location, at this date? Is the tag right?
 3. Each label: is a SOURCE CLAIM presented as fact? Is a judgment presented as fact?
 4. Terminology: is each term used as defined in glossary.md (e.g., "response" ≥50% unless stated)?
 5. Absolute vs relative: are benefits and harms on the same scale?
 6. Staleness: any pipeline/regulatory fact checked more than 60 days ago?
 7. Omissions: the strongest counter-evidence or counterargument that the draft leaves out.
Return: a table — Claim | Verdict (CONFIRMED / CORRECTED / DISPUTED / UNVERIFIABLE) | Evidence | Fix —
followed by the three most important problems, ranked.
```

## 5. OPPOSING COUNSEL brief (optional; for contested questions)

```
You are Opposing Counsel. Build the strongest good-faith case AGAINST the draft's main conclusion,
using only sourced facts and recognized ethical arguments.
Skill folder: <ABS_PATH>   Read: references/psychedelic-ethics-issues.md §7, references/ethics-frameworks.md §1–2
Inputs: the draft conclusion and its key supporting rows.
Return: ≤ 400 words — (1) the best counter-case, (2) which premises it attacks, (3) what evidence would decide
between the draft and the counter-case. Label everything ANALYTICAL JUDGMENT unless sourced.
```

## 6. Merging (MANAGER's job)

1. **Append agent rows** to the ledger in one batch per agent. Renumber IDs if agents collided.
2. **Resolve conflicts between agents.**
   - Pick the better-sourced claim.
   - Mark the other row SUPERSEDED or DISPUTED.
   - Never average two conflicting numbers.
3. **Apply the CHECKER's verdicts:**

   | Verdict | Action |
   |---|---|
   | CORRECTED | Supersede the old row with the fix |
   | DISPUTED | Keep the row, mark it DISPUTED, and show the dispute in the memo |
   | UNVERIFIABLE | Downgrade the label to SOURCE CLAIM, or drop the claim |

4. **Record the check:** add a LOG row, "CHECKER pass complete: n confirmed, n corrected, n disputed."
