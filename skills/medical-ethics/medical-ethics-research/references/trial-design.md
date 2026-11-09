# Study and trial design: choosing, auditing, and predicting bias

**Last verified: 2026-11-09.** Methods content is textbook material and carries no tag; regulatory facts and empirical bias estimates carry [V], [S], or [M] tags. Use this file to answer three questions about any study: **What design does this question need? What design was used? What does the gap do to the result, and in which direction?**

## Contents

1. The audit in seven steps
2. Matching the question to the design
3. Randomized designs: when each is optimal and how each fails
4. Non-randomized and observational designs
5. Diagnostic, prognostic, and real-world program designs
6. Suboptimal design → consequence → direction of bias
7. The optimal psychedelic trial
8. Regulatory and reporting anchors

## 1. The audit in seven steps

1. **State the question in PICOTS form:** population, intervention, comparator, outcome, time frame, setting. Add the **estimand** (ICH E9(R1)): which intercurrent events (rescue medication, dropout, a second dose) are handled how. A study can answer a different question from the one its press release claims.
2. **Name the optimal design for that question** (§2). If it is infeasible or unethical, name the best feasible one.
3. **Name the design actually used,** in plain words: "single-arm, open-label, 3-month before/after," not "real-world study."
4. **List the gaps** between the optimal and the actual design.
5. **For each gap, give the consequence and its usual direction** (§6). "Toward benefit" means the gap tends to make the treatment look better than it is.
6. **Check what reduces each gap:** sensitivity analyses, blinding checks (`risk_calc.py blinding`), E-values (`evalue`), retrodesign (`retrodesign`), and pre-registration compared with the report.
7. **Grade the conclusion:** what the design *can* support (causal effect, association, feasibility, safety signal) vs. what the source *claims*. Mismatches are spin (study-design-flaws.md §6).

Always pair the design verdict with the **absolute-vs-relative framing table** (SKILL.md principle 3). A biased design and a relative-only headline compound each other.

## 2. Matching the question to the design

| Question | Optimal design | Acceptable alternatives | Never enough on its own |
|---|---|---|---|
| Does the treatment work under ideal conditions (efficacy)? | Parallel-group, double-blind RCT with concealed allocation, pre-registered primary outcome and estimand | Crossover RCT (only for stable chronic conditions with short-acting, reversible treatments) | Single-arm before/after; historical controls |
| Does it work in ordinary practice (effectiveness)? | Pragmatic RCT (rated with PRECIS-2) | Cluster or stepped-wedge RCT; target trial emulation with rich data | Uncontrolled program data |
| Is it better than, or as good as, an existing treatment? | Head-to-head RCT; non-inferiority design when the goal is "not worse" | Network meta-analysis of RCTs (indirect, weaker) | Comparing separate placebo-controlled trials ("cross-trial comparison") |
| What dose? | Randomized parallel dose-response with at least 3 doses plus placebo | Adaptive dose-finding (MCP-Mod; Bayesian) | One dose vs placebo |
| Does the benefit last? | Long-term randomized follow-up of all randomized patients; or a randomized-withdrawal phase with a pre-specified relapse definition | Delayed-start design | Open-label extension in responders only |
| Rare or late harms? | Large simple RCT (rarely feasible); active-comparator new-user cohort; self-controlled case series | Pharmacovigilance with disproportionality analysis (signal only) | Trial safety tables alone (too small, too short) |
| Is the effect caused by the drug, the therapy, or expectation? | 2×2 factorial (drug × therapy) with active placebo and expectancy measurement | Dismantling designs; therapy-only arm | Drug-plus-therapy vs placebo-plus-therapy alone |
| Diagnostic accuracy | Cross-sectional study of consecutive patients, every patient gets the index test and the reference standard, blind reading (QUADAS-2) | Diagnostic RCT for effect on outcomes | Case-control ("two-gate") accuracy study |
| Prognosis | Inception cohort with complete follow-up | Registry with validated outcomes | Cross-sectional data |
| Does a policy or program help a population? | Cluster RCT or stepped-wedge rollout | Interrupted time series with a control series; difference-in-differences; regression discontinuity | Before/after with no comparison |
| Which treatment works for this one patient? | N-of-1 crossover series (CENT reporting) | — | Anecdote |

## 3. Randomized designs: when each is optimal and how each fails

| Design | Optimal when | Main failure modes |
|---|---|---|
| **Parallel-group RCT** | The default for efficacy | Poor concealment; unblinding; attrition; outcome switching; underpowered for harms |
| **Placebo-controlled** | No proven therapy exists, or adding to standard care | Unethical when withholding effective care risks serious harm (the Declaration of Helsinki's placebo paragraph limits placebo use [M: check the 2024 paragraph number]); functional unblinding when the drug's effects are obvious |
| **Active placebo** | The drug has noticeable side effects | A poor mimic (niacin flush vs a psychedelic experience) only partly protects the blind |
| **Crossover** | Stable chronic disease; short-acting, reversible treatment; washout possible | **Carryover:** invalid when the treatment's effects persist (psychedelics, psychotherapy, any learning effect); period effects; dropouts after period 1 |
| **Factorial (2×2)** | Two interventions whose separate and joint effects matter (drug × therapy) | Interaction lowers power for main effects; needs a larger sample |
| **Cluster RCT** | The intervention acts on groups (clinics, wards), or contamination between patients is likely | Few clusters (fewer than about 10 per arm) → imbalance and wrong CIs; recruitment after randomization → selection bias; ignoring the intracluster correlation overstates precision |
| **Stepped-wedge** | Rollout to everyone is planned anyway | Confounding by calendar time; complex analysis |
| **Non-inferiority / equivalence** | The new treatment has other advantages (safety, cost, convenience) | A margin too wide; **no assay sensitivity** (both arms ineffective look "equivalent"); sloppy conduct *favours* a finding of no difference; biocreep across successive trials |
| **Group-sequential** (pre-planned interim analyses) | Long trials with important outcomes; ethical need to stop early | Stopping early for benefit overestimates effects, especially with few events (Bassler et al., *JAMA* 2010 [M]) |
| **Adaptive** (sample-size re-estimation, response-adaptive randomization, enrichment, seamless Phase II/III) | Uncertainty about effect size or population; efficiency matters | Type I error inflation unless pre-specified and simulated; operational bias when interim results leak; enrichment narrows who the result applies to. ICH E20 (adaptive designs) is a **draft**: Step 2b endorsed 2025-06-25; as of the 2026-07-10 ICH workplan, review of consultation comments was due for completion by December 2026 [V: ICH workplan; EMA Step 2b PDF]. FDA's adaptive-design guidance (2019) is final [M]. |
| **Platform / basket / umbrella** (master protocols) | Several treatments or subgroups under one infrastructure | Non-concurrent controls; shared-control multiplicity; drift over time |
| **Pragmatic** | Effectiveness in usual care | Less control over adherence and outcome measurement; open label is common, so outcomes need to be objective or assessed blind |
| **Randomized withdrawal** | Testing maintenance of benefit after open-label response | **Enriched for responders and tolerators;** the effect applies only to responders; withdrawal effects can masquerade as relapse |
| **Delayed-start** | Separating symptomatic from disease-modifying effects | Assumes the delayed arm can "catch up"; attrition differs by arm |
| **N-of-1** | Chronic, stable conditions; individual treatment choice | Same carryover limits as crossover |

## 4. Non-randomized and observational designs

| Design | Best use | Key threats | Tools that help |
|---|---|---|---|
| **Prospective cohort** | Prognosis; harms; long-term outcomes | Confounding (by indication and by healthy-user effects); loss to follow-up | Active-comparator, new-user design; propensity methods; E-value |
| **Retrospective cohort / database** | Harms; utilization; large samples | Misclassification; missing confounders; **immortal time bias**; **prevalent-user bias** | Target trial emulation (Hernán & Robins, *Am J Epidemiol* 2016 [M]): define time zero, eligibility, and treatment strategies as a trial would |
| **Case-control** | Rare outcomes | Recall and selection bias; control choice | Population controls; nested case-control within a cohort |
| **Self-controlled designs** (case-crossover; self-controlled case series) | Transient exposures and acute outcomes | Time-varying confounding; event-dependent exposure | Each person is their own control, which removes fixed confounders |
| **Single-arm before/after** | Feasibility; safety signals; hypothesis generation | **Regression to the mean, natural recovery, placebo response, expectancy, and selection all push toward benefit;** no counterfactual | Compare with a contemporaneous control; pre-registered outcomes; report the within-person RR as *not* a treatment effect |
| **Interrupted time series** | Policy changes with long pre- and post-periods | Co-interventions at the same time; too few time points | Control series; segmented regression with autocorrelation |
| **Difference-in-differences** | A policy in one place, not another | Parallel-trends assumption fails | Event-study plots of pre-trends |
| **Regression discontinuity** | Treatment assigned by a cutoff (score or age) | Manipulation around the cutoff; applies only near the cutoff | Density tests at the cutoff |
| **Instrumental variable** | Unmeasured confounding with a valid instrument | Weak or invalid instruments | Report instrument strength; sensitivity analyses |
| **Registry** | Real-world safety and outcomes over years | Voluntary enrolment selects patients; inconsistent follow-up | Mandatory, consecutive enrolment; validated outcomes |

## 5. Diagnostic, prognostic, and real-world program designs

- **Diagnostic accuracy:** two-gate (case-control) sampling inflates sensitivity and specificity; partial verification (only test-positives get the reference standard) inflates sensitivity; an unblinded reference reading inflates agreement. Use QUADAS-2 and STARD [M].
- **Prediction models:** development without external validation overstates performance; use TRIPOD+AI and PROBAST [M].
- **Real-world programs** (Oregon, Australia's prescriber scheme): the strongest feasible design is usually a **prospective cohort with a concurrent comparison** (waitlist, matched non-users, or a stepped rollout across sites) plus mandatory adverse-event reporting. A single-arm cohort such as OPEN can show safety rates and feasibility; it cannot show that psilocybin caused the improvement (international-access.md §10).

## 6. Suboptimal design → consequence → direction of bias

| Gap | What it does | Usual direction |
|---|---|---|
| No randomization | Confounding by indication, healthy-user, and channelling effects | Usually toward benefit (sicker patients get the comparator) — but can go either way; state the mechanism |
| Inadequate allocation concealment | Recruiters steer patients; baseline imbalance | Toward benefit; meta-epidemiological studies show exaggerated effects, especially for subjective outcomes (Savović et al., *Ann Intern Med* 2012 [M]) |
| No blinding, or functional unblinding | Expectancy, performance, and detection bias; "know-cebo" disappointment in control arms | **Toward benefit**, strongest for subjective outcomes such as MADRS; control arms underperform (Hieronymus 2025; Williams 2026: study-design-flaws.md §3) |
| Rater not blind, or the therapist rates | Detection bias | Toward benefit |
| Single arm / historical control | Regression to the mean, natural history, placebo | Toward benefit |
| Small sample with a significant result | Imprecision plus selection by significance | Toward benefit (Type M exaggeration; run `retrodesign`) |
| Stopping early for benefit | Truncation at a random high | Toward benefit |
| Per-protocol or completer analysis only | Excludes non-responders and those harmed | Usually toward benefit |
| High or unequal attrition | Missing-not-at-random outcomes | Toward benefit when dropouts are the non-responders |
| Short follow-up | Misses relapse and late harms | Toward benefit |
| Responder-only durability ("90% stayed well") | Conditions on the outcome | Toward benefit; not a randomized estimate |
| Surrogate endpoint | The surrogate may not track the outcome patients care about | Unpredictable; often toward benefit |
| Outcome switching / multiple endpoints | Picks the best-looking result | Toward benefit; compare with the registry entry |
| Nonstandard responder threshold (≥25% vs ≥50%) | Inflates response rates | Toward benefit in absolute terms |
| Enrichment (prior responders, psychedelic-experienced participants) | Narrows applicability; may inflate effects | Toward benefit for the general population |
| Crossover with lasting effects | Carryover contaminates period 2 | Toward the null (or unpredictable) |
| Non-inferiority trial with poor conduct | Blurs differences | **Toward "no difference,"** which favours the new drug |
| Too few clusters | Chance imbalance; CIs too narrow | Unpredictable; overconfident |
| Immortal time | Treated patients get event-free time for free | Toward benefit |
| Prevalent users | Survivors of early harms | Toward benefit, and harms are missed |
| Adverse events captured only when "unexpected" | Positive psychoactive effects go unrecorded | Understates harm and abuse liability (the Lykos lesson; the 2026 FDA guidance requires capture) |

## 7. The optimal psychedelic trial

Measure every psychedelic trial against this standard; each missing element is a named gap in §6.
1. **Comparator:** an active placebo or a low dose (for example, 1 mg psilocybin, 50 µg LSD), plus a third arm where feasible. The 2026 FDA final guidance encourages innovative control groups, active comparators, and blinded central raters (fda-pipeline.md §2.1).
2. **Dose-response:** at least 3 doses. A monotonic dose-response is harder to explain by expectancy alone.
3. **Separation of roles:** the outcome rater is remote, central, and blind, and is not the therapist.
4. **Measure the blind:** ask participants and raters to guess the arm at fixed times; report the Bang and James indexes (`risk_calc.py blinding`) and expectancy at baseline.
5. **Separate drug from therapy:** a 2×2 factorial (drug × therapy) or a therapy-only arm, with therapy manualized and fidelity rated.
6. **Estimand and intercurrent events** (ICH E9(R1)): pre-specify how antidepressant tapering, rescue medication, and second doses are handled. A washout before enrollment selects patients who can tolerate it.
7. **Durability:** randomized long-term follow-up of everyone randomized, or a pre-specified randomized retreatment design. Open-label extensions in responders do not count.
8. **Harms:** systematic capture of all adverse events, including positive psychoactive effects; the C-SSRS at fixed times; cardiac (5-HT2B) monitoring; challenging-experience and abuse-liability measures.
9. **Population and setting:** stratify by prior psychedelic use; report setting per **ReSPCT**; recruit a representative population.
10. **Governance:** an independent DSMB, video recording with independent review (consent-review-checklist.md), and pre-registration with the full protocol and statistical analysis plan public.
11. **Report:** CONSORT 2025 plus ReSPCT, with absolute and relative effects and NNT.

## 8. Regulatory and reporting anchors

- ICH E9(R1), estimands and sensitivity analysis (2019) [M]; ICH E10, choice of control group [M]; ICH E6(R3), GCP (final; EMA consolidated version August 2026 [S]); ICH E20, adaptive designs (draft; see §3) [V].
- FDA psychedelic final guidance, 2026 (fda-pipeline.md §2.1) [S].
- CONSORT 2025 and SPIRIT 2025; ReSPCT (Nat Med 2025) [V]. Extensions: cluster, non-inferiority, crossover, pragmatic, N-of-1 (CENT), harms [M].
- Risk-of-bias tools: RoB 2 (randomized), ROBINS-I V2 (non-randomized), QUADAS-2 (diagnostic), PROBAST (prediction) [M].
- PRECIS-2 for pragmatic vs explanatory design choices [M].
