# Citation appraisal: checking critical citations and the quality of the cited studies

**Last verified: 2026-11-09.** Use this file whenever a document, memo, press release, guideline, consent form, or paper rests a claim on a citation, and whenever Blake asks "does this source say that?", "is this study any good?", or "check the references." Tags as elsewhere: [V] checked against a primary source; [S] secondary only; [M] from memory, check before stating as fact.

## Contents
1. Why citation checks matter (the evidence)
2. Which citations to check: critical citations
3. The citation audit in eight steps
4. Fidelity: does the source support the claim?
5. Choosing the quality tool for the cited study
6. The tools' overall-judgement rules
7. From one study to a body of evidence (GRADE)
8. Venue, integrity, and conflict checks
9. Lookup recipes (what works from this workspace)
10. Psychedelic-field cases
11. Output template and wording

## 1. Why citation checks matter (the evidence)

| Finding | Source | Tag |
|---|---|---|
| Across studies of medical articles, about a quarter of quotations are wrong: total quotation error rate 25.4% (95% CI 19.5 to 32.4), major errors 11.9% (8.4 to 16.6) | Jergas & Baethge, *PeerJ* 2015;3:e1364 | V |
| A reanalysis restricted to 15 methodologically comparable studies put the quotation error rate at 14.5% (10.5 to 18.6); improper secondary citations (citing a paper for what it cites) occurred at 10.4% | Mogull, *PLoS One* 2017;12(9):e0184727 | V |
| Articles with statistically significant results are cited 1.6 times (95% CI 1.3 to 1.8) as often as those with non-significant results; articles whose authors say they found support for their hypothesis, 2.7 times | Duyx et al., *J Clin Epidemiol* 2017;88:92–101 (52 studies) | V |
| Citation can create "unfounded authority": a network of 242 papers and 675 citations turned a hypothesis into accepted fact through **citation bias** (ignoring critical data), **amplification** (papers with no data on the claim spreading it), and **invention** (hypothesis restated as fact); 95% of citation paths ran through four review papers from one group | Greenberg, *BMJ* 2009;339:b2680 | V |
| Retracted papers keep being cited: of post-retraction citation contexts studied, only 722 (5.4%) acknowledged the retraction | Hsiao & Schneider, *Quant Sci Stud* 2021;2(4):1144–1169 | V |
| In 72 trials with a non-significant primary outcome, 58.3% of abstract conclusions and 50.0% of main-text conclusions contained spin | Boutron et al., *JAMA* 2010;303(20):2058–2064 | V |
| Trial reports often switch or omit pre-specified outcomes; COMPare monitored 58 misreported trials and wrote correction letters | Goldacre et al., *Trials* 2019;20:118 | V (citation); M (percentages: read the paper before quoting them) |

**Bottom line for the skill:** never repeat a cited claim as fact until the cited source has been checked. Read the source rather than the citing text's summary of it, and the full text rather than only the abstract. Expect roughly one cited claim in four to six to be wrong in some way.

## 2. Which citations to check: critical citations

A **critical citation** is one the conclusion depends on: remove it and the argument fails or weakens materially. Check every critical citation in full. Check the rest by sampling (at least 1 in 5) and whenever a number, a quotation, or a surprising claim is attached.

Signals that a citation is critical:
- It carries a number the reader will act on: an effect size, a risk, an NNT, a prevalence, a dose, a cost.
- It supports a safety claim ("well tolerated," "no serious adverse events").
- It is the only support for a causal claim, or the claim says "studies show" with one or two references.
- It supports a regulatory or legal statement ("FDA requires," "the rule says").
- It is cited as consensus ("experts agree," "guidelines recommend").

## 3. The citation audit in eight steps

Run `python3 scripts/appraise_citations.py worksheet <file>` first. It extracts DOIs, PMIDs, PMCIDs, NCT numbers, and arXiv IDs, flags preprint servers, and prints the lookup URLs to fetch.

1. **Pin the claim.** Write the exact claim the citation is meant to support, including its number, population, comparator, outcome, and time frame.
2. **Resolve identity.** Fetch the Crossref record (§9). Confirm that the title, authors, journal, year, volume, and pages match the citation. A mismatch can be a typo, a wrong paper, or a fabricated reference (AI-generated reference lists can fabricate plausible citations [M]). No record and no other trace means the citation is **unverifiable**: say so and do not rely on it.
3. **Check status.** In the Crossref record, read `updated-by`: `retraction`, `correction`, or `expression_of_concern` (the source can be `publisher` or `retraction-watch`). Check the journal page too. For a preprint, search for the published version and compare the two. A retracted paper supports nothing; a corrected one may support a different number.
4. **Read the source, not the citing text's paraphrase of it.** Use the full text where available; label any judgement that rests on the abstract alone ("abstract only").
5. **Judge fidelity** (§4): does the source support the claim as stated?
6. **Trace the chain.** If the source is itself citing someone else (a review, a news story, a textbook), follow it to the primary data. Citing a secondary source for a primary finding is an "improper secondary citation" (Mogull 2017). Repeat until you reach data or a dead end.
7. **Appraise the cited study's quality** with the tool for its design (§5–6), for the specific result cited, not the paper as a whole.
8. **Grade the citation:** fidelity (§4) × study quality or certainty (§6–7) × status (§3) → one line per citation in the output table (§11).

## 4. Fidelity: does the source support the claim?

The skill's working categories, adapted from the quotation-error literature (Jergas & Baethge 2015; Mogull 2017):

| Verdict | Meaning | Example |
|---|---|---|
| **Supports** | The source states the claim, with matching numbers, population, outcome, and time frame | Source: 9 of 15 vs 3 of 15; citing text: "60% vs 20%" |
| **Partly supports** | Right direction, but the claim overstates, generalizes, drops a qualifier, or uses a different outcome or time point | Source: secondary outcome at week 3; citing text: "the trial showed" |
| **Does not support** | The source does not address the claim, or the claim comes from the source's discussion or a cited third paper, not its data | Source's introduction speculates; citing text calls it a finding |
| **Contradicts** | The source reports the opposite, or a non-significant result is cited as an effect | Source: no significant difference; citing text: "reduced relapse" |
| **Unverifiable** | The source cannot be found or read | Paywalled with no abstract; a dead link; no record |

Common distortions to look for, each with a question:
- **Number drift:** does every number match, including the denominator and the time point?
- **Population drift:** was the finding in the same population (TRD vs MDD; healthy volunteers vs patients; animals vs humans)?
- **Outcome or subgroup swap:** is the cited result the primary outcome, or a secondary, post hoc, or subgroup result?
- **Certainty inflation:** "may be associated with" becomes "causes"; "pilot" becomes "trial"; a hypothesis becomes a finding (Greenberg's "invention").
- **Relative-only reporting:** the citing text gives a relative effect the source paired with an absolute one. Run `risk_calc.py binary` and restore both.
- **Spin carried forward:** the citing text repeats the source's abstract spin rather than its results (Boutron 2010).
- **Selective citation:** supportive studies are cited and contrary ones are not (citation bias). Search for the contrary evidence before accepting a one-sided reference list.

## 5. Choosing the quality tool for the cited study

| Cited study's design | Tool | Output scale | Tag |
|---|---|---|---|
| Randomized trial (parallel, cluster, or crossover variants) | **RoB 2** (Sterne et al., *BMJ* 2019;366:l4898) | Low / Some concerns / High, per result | V |
| Non-randomized study of an intervention (cohort, case-control, before-after, registry, "real-world") | **ROBINS-I** (Sterne et al., *BMJ* 2016;355:i4919); **version 2 released 2025**, with algorithms and immortal-time bias added | Low / Moderate / Serious / Critical / No information | V |
| Non-randomized study of an exposure (environmental, occupational, lifestyle) | **ROBINS-E** (Higgins et al., *Environ Int* 2024;186:108602) | Low / Some concerns / High / Very high | V (citation); M (scale labels) |
| Diagnostic accuracy study | **QUADAS-2** (Whiting et al., *Ann Intern Med* 2011;155(8):529–536) | Low / High / Unclear, per domain, for bias and applicability | V |
| Prediction model (including AI models) | **PROBAST+AI** (Moons et al., *BMJ* 2025;388:e082505) | Low / High / Unclear | V |
| Systematic review or meta-analysis | **AMSTAR 2** (Shea et al., *BMJ* 2017;358:j4008); ROBIS is an alternative | High / Moderate / Low / Critically low confidence | V |
| A body of evidence on one outcome | **GRADE** (Guyatt et al., *BMJ* 2008;336:924–926) | High / Moderate / Low / Very low certainty | V |
| Case series, case report, qualitative study | JBI checklists; CASP checklists | Checklist, no validated overall score | M |
| Animal study | SYRCLE risk-of-bias tool | Per domain | M |

The Cochrane Handbook version 6.5 (2024; 6.5.1 corrections 2025) is the reference text for how these tools are applied [V]. Psychedelic-specific design problems that every tool should pick up (functional unblinding, expectancy, therapist-rater overlap, responder-only extensions) are in study-design-flaws.md and trial-design.md §6.

**Shortcut for a quick check:** answer five questions for the cited result. Was it randomized? Was the outcome assessor blind (and does the blinding hold for a psychedelic)? Was everyone randomized analyzed? Was the outcome pre-specified (check the registry)? Is the sample big enough that the interval excludes trivial effects? Two or more "no" answers mean the citation cannot carry a strong claim.

## 6. The tools' overall-judgement rules

Run the matching subcommand of `scripts/appraise_citations.py`; each prints the rule it applied.

- **RoB 2** (`rob2 --d1 … --d5`): low only if all five domains are low; high if any domain is high, or if several domains raise some concerns in a way that substantially lowers confidence in the result; otherwise some concerns. The domains: randomization process; deviations from intended interventions; missing outcome data; measurement of the outcome; selection of the reported result. Assess one result (outcome and time point), not the trial. [V: Sterne 2019; Cochrane Handbook ch. 8]
- **ROBINS-I 2016** (`robins-i --d1 … --d7`): low if low in all domains; moderate if low or moderate in all; serious if serious in at least one and critical in none; critical if critical in at least one; no information if nothing points to serious or critical but key domains lack information (a judgement). The domains: confounding; selection of participants; classification of interventions; deviations from intended interventions; missing data; measurement of outcomes; selection of the reported result. Say whether the source used version 1 or version 2. [V: Sterne 2016, Table 2]
- **AMSTAR 2** (`amstar2 --failed-items …`): high if no critical flaw and at most one non-critical weakness; moderate if no critical flaw but more than one non-critical weakness; low if one critical flaw; critically low if more than one. The suggested critical items are 2 (protocol registered before the review), 4 (comprehensive search), 7 (excluded studies listed and justified), 9 (risk of bias of included studies assessed), 11 (appropriate meta-analytic methods), 13 (risk of bias considered when interpreting results), and 15 (publication bias investigated). [V: Shea 2017, via several agreeing summaries]
- **GRADE** (`grade --start high|low …`): see §7.

An overall judgement is never an average. One high-risk domain makes the result high risk, however good the other domains are.

## 7. From one study to a body of evidence (GRADE)

- **Start:** randomized trials start at high certainty; non-randomized studies start at low. [V]
- **Rate down** one or two levels each for risk of bias, inconsistency, indirectness, imprecision, and publication bias. [V]
- **Rate up** (normally only non-randomized evidence with no serious limitation) for a large effect (one level for roughly a twofold change in risk, two for roughly fivefold), a dose-response gradient, or plausible confounding that would reduce the observed effect. [V]
- **Meaning** (Guyatt 2008): high, further research is very unlikely to change confidence in the estimate; moderate, likely to have an important impact; low, very likely to; very low, any estimate is very uncertain. [V]

Use GRADE language when a citation stands for a body of evidence ("psilocybin works for depression"): the answer is a certainty rating for a specific outcome, not "proven" or "unproven." The skill's FACT, CLAIM, and JUDGMENT labels say how well a *statement* is verified; GRADE says how much confidence the *evidence* deserves. Report both when they differ: "[FACT] the trial reported X; [JUDGMENT] low certainty, because…"

## 8. Venue, integrity, and conflict checks

- **Peer review status.** A preprint has not been peer reviewed; the worksheet flags preprint-server DOIs (10.1101 bioRxiv/medRxiv, 10.31234 PsyArXiv, 10.2139 SSRN, 10.21203 Research Square, and others). Check for a published version and whether the results changed.
- **Predatory or low-quality venues.** No single list is authoritative. The consensus definition calls predatory journals entities that prioritize self-interest at the expense of scholarship, marked by false or misleading information, deviation from best editorial and publication practice, a lack of transparency, and aggressive, indiscriminate solicitation (Grudniewicz et al., *Nature* 2019;576:210–212 [V: citation; M: wording, check before quoting]). Check whether the journal is indexed in MEDLINE, has a named editor and board, states its peer-review process, and is a Crossref member; none of these alone proves quality.
- **Registration vs report.** For a trial, compare the registry's primary outcome and time point with the paper's. A switched outcome is a red flag (COMPare).
- **Funding and conflicts.** Record who funded the study and the authors' declared conflicts. A conflict does not make a result wrong; it raises the bar for independent replication.
- **Retractions elsewhere.** An author or site with retracted work is a signal to check the cited paper more closely, not proof of a problem.
- **Data and protocol availability.** Public protocol, analysis plan, and data make claims checkable; their absence lowers the weight a citation can carry.

## 9. Lookup recipes (what works from this workspace)

The shell's network allowlist blocks Crossref, PubMed, OpenAlex, Europe PMC, and ClinicalTrials.gov (tested 2026-11-09). Use **WebFetch** instead:
- **Crossref record by DOI:** `https://api.crossref.org/works/<DOI>`. Ask for the title, authors, journal, year, volume, pages, and the `update-to`, `updated-by`, and `relation` fields. Crossref includes Retraction Watch data: `updated-by` entries carry `source: retraction-watch` or `source: publisher`. Crossref acquired the Retraction Watch database in 2023 and opened it [V: Crossref announcement].
- **Find a paper without a DOI:** `https://api.crossref.org/works?query.bibliographic=<title words>&rows=5`.
- **Find retracted items in a journal on a topic:** `https://api.crossref.org/works?query.bibliographic=<words>&filter=issn:<ISSN>,from-pub-date:<YYYY-MM-DD>&rows=15&select=DOI,title,published,updated-by`.
- **PubMed or PMC page:** `https://pubmed.ncbi.nlm.nih.gov/<PMID>/` (abstract, "Retraction in" notices, comments).
- **Registry:** `https://clinicaltrials.gov/study/<NCT>` (registered outcomes and history of changes).
- Publisher pages may be blocked or may need approval in a given session; when a fetch is refused, record "not reachable" and use Crossref plus PubMed.

## 10. Psychedelic-field cases

- **Retracted MDMA papers.** On 2024-08-10, *Psychopharmacology* retracted three MAPS-sponsored papers, citing "protocol violations amounting to unethical conduct" at the MP4 Phase 2 site [V: Crossref `updated-by` entries, source publisher and Retraction Watch; S: news reports for the reason]:
  - Mithoefer et al. 2019, study design and rationale (doi 10.1007/s00213-019-05249-5; notice 10.1007/s00213-024-06666-x);
  - Jerome et al. 2020, long-term follow-up outcomes (doi 10.1007/s00213-020-05548-2; notice 10.1007/s00213-024-06665-y);
  - Feduccia et al. 2021, discontinuing reuptake-inhibitor medications before MDMA therapy (doi 10.1007/s00213-020-05710-w; notice 10.1007/s00213-024-06671-0).
  Any document citing these for durability or for the SSRI-washout effect cites retracted work. Say so, and say what the retraction concerned: conduct at one site, not a finding of data fabrication. Some authors disputed the retraction, and Lykos said the papers were not part of its FDA application [S].
- **Press releases cited as evidence.** Phase 3 psilocybin results (COMP005, COMP006) were public only through company releases as of 2026-11-09 [V: fda-pipeline.md]. A citation to a release is a citation to an unreviewed claim: label it CLAIM.
- **Self-report surveys cited for rates.** Online-report studies (for example, the lithium seizure signal) cannot give a rate; a citing text that turns "47% of reports" into "47% risk" fails fidelity.
- **Open-label extensions cited for durability.** Responder-only follow-up cannot support a durability claim against control (trial-design.md §6).

## 11. Output template and wording

| # | Claim as cited | Source (verified identity) | Status | Fidelity | Study design and tool rating | Certainty for this claim | What to do |
|---|---|---|---|---|---|---|---|
| 1 | "MDMA's benefit lasts at least a year" | Jerome et al. 2020 (doi 10.1007/s00213-020-05548-2) | **Retracted 2024-08-10** | Not evaluable: retracted | Long-term follow-up, open label | Not usable | Remove; cite current evidence or say none exists |

Wording rules:
- State the verdict first, then the reason: "Does not support: the source reports a non-significant difference (p = 0.20)."
- Name the exact place in the source: table, figure, page, or section.
- When the citation fails, say what evidence would support the claim, or that none was found.
- Keep the labels: the existence of a paper is a [FACT] once checked; what it claims is a [CLAIM] unless independently verified; the quality rating is a [JUDGMENT] made with a named tool.
