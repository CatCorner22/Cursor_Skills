# Statistics for Appraising Medical Studies

This file teaches the arithmetic and the reasoning. **For any actual number in a review, run `scripts/risk_calc.py`.** Do not compute in prose. Show the command, the inputs, and where each input came from (table number, page, or "reconstructed from rounded percentages").

Tags: **[M]** marks a figure from training knowledge that has not been re-verified. Treat it as a pointer to verify, not a citation.

## Contents
1. Effect measures at a glance
2. Absolute vs. relative risk
3. NNT and NNH
4. Odds ratios, risk ratios, hazard ratios
5. Continuous outcomes: mean differences, LS means, standardized effects
6. Confidence intervals and p-values
7. Power, sample size, and small-study distortions
8. Clinical importance (MCID) in psychiatry scales
9. Implausibly large effects, regression to the mean, placebo response
10. Analysis populations, missing data, and estimands
11. Multiplicity and subgroups
12. Surrogate and composite endpoints
13. Observational evidence and causal inference
14. Meta-analysis
15. Diagnostic and screening statistics
16. Bayesian reasoning and prior plausibility
17. Checklist: reading a press release or abstract
18. Calculator recipes

---

## 1. Effect measures at a glance

The 2x2 table: group 1 (intervention) has `a` events among `n1`; group 0 (control) has `c` events among `n0`. risk1 = a/n1; risk0 = c/n0.

| Measure | Formula | Scale | Null value | Depends on baseline risk? |
|---|---|---|---|---|
| Risk difference (RD) | risk1 − risk0 | absolute | 0 | yes, by definition |
| Absolute risk reduction (ARR) | risk0 − risk1 (bad outcome reduced) | absolute | 0 | yes |
| Risk ratio (RR) | risk1 / risk0 | relative | 1 | often roughly constant across baselines |
| Relative risk reduction (RRR) | 1 − RR = ARR / risk0 | relative | 0 | often roughly constant |
| Odds ratio (OR) | (a/b) / (c/d) | relative | 1 | approximates RR only when events are rare (<10%) |
| Hazard ratio (HR) | ratio of instantaneous event rates over time | relative | 1 | assumes proportional hazards |
| NNT / NNH | 1 / \|RD\| | absolute, inverted | ∞ | yes; tied to a time frame |
| Mean difference (MD) | mean1 − mean0 | absolute, in scale units | 0 | — |
| Standardized mean difference (SMD; d, g) | MD / pooled SD | unitless | 0 | sensitive to sample homogeneity |

## 2. Absolute vs. relative risk

**Core idea.** A relative measure tells you *how much the risk changes in proportion*. An absolute measure tells you *how many people are affected*. Decisions about individual patients and policy need the absolute measure. Relative measures alone predictably exaggerate the impression of benefit (Gigerenzer et al., *Psychol Sci Public Interest* 2007 [M]).

**Worked example.**
- An outcome occurs in 2 of 100 control patients (2%) and 1 of 100 treated patients (1%).
  - RRR = 50% ("halves your risk").
  - ARR = 1 percentage point.
  - NNT = 100.
- The same 50% RRR at a 40% → 20% baseline gives ARR = 20 points and NNT = 5.
- The relative effect is identical. The clinical meaning is opposite.

**Rules for the skill:**
1. **Always report both.** Report the absolute measure first, with its time frame: "over 12 weeks."
2. **Watch for mismatched framing.** Benefits stated as relative ("cuts risk 50%") while harms are stated as absolute ("1% had side effects") is a recognized spin pattern. Restate both on the same scale.
3. **Use natural frequencies for lay readers.** "Out of 1,000 people like this, X would… with treatment vs Y without." See `risk_calc.py frequencies`.
4. **Check baseline risk.** The ARR in a trial applies to the trial's baseline risk. Patients with a lower baseline risk get less absolute benefit, and the same harms.
5. **Use percentage points for a difference between percentages.** "Response rose from 7% to 35%": that is +28 percentage points, and it is 400% in relative terms. Never write "28%" for a difference of rates without saying "points."

## 3. NNT and NNH

- **Definitions.**
  - NNT (benefit) = 1 / ARR. It is the number of patients who must receive the intervention, instead of the control, for one additional patient to benefit *over the stated time frame*.
  - NNH = 1 / absolute risk increase for a harm.
- **Rounding.** Report the exact value and the conventional rounded-up integer. Rounding up is conservative.
- **Confidence interval.** Invert the CI for the RD (Altman, BMJ 1998 [M]).
  - If the RD's CI crosses 0, the NNT CI runs from NNTB x "through infinity" to NNTH y. Never report a single NNT as if it were certain.
  - `risk_calc.py binary` does this automatically.
- **Caveats:**
  - NNT is specific to the comparator, the time frame, the outcome definition, and the baseline risk. Do not compare NNTs across trials with different comparators or durations.
  - A **responder NNT** from a dichotomized continuous outcome (e.g., ≥50% MADRS reduction) depends on the cut-point. Dichotomization discards information and can make small mean differences look large or small (Senn, "Disappointing dichotomies," *Pharm Stat* 2003; Altman & Royston, BMJ 2006 [M]).
  - **NNT vs NNH together.** Compare NNT for the primary benefit with NNH for each important harm. That is the beginning of a benefit-risk statement, not the end of one.

## 4. Odds ratios, risk ratios, hazard ratios

- **OR overstates RR when the outcome is common.** When the event exceeds about 10% in either group, the OR moves further from 1 than the RR does. Example: an OR of 3 with a 40% baseline risk corresponds to an RR of about 1.67 (`risk_calc.py orrr`).
  - Never paraphrase an OR as "three times as likely."
- **Adjusted ORs** from logistic regression cannot be converted exactly. The Zhang–Yu formula is approximate for adjusted estimates [M].
- **Hazard ratios:**
  - An HR summarizes relative event *rates* across follow-up. It assumes proportional hazards: check whether the Kaplan-Meier curves cross.
  - An HR is not a probability. Translate it with absolute survival or event proportions at stated time points.
  - Restricted mean survival time (RMST) differences are an absolute alternative.
- **Log-scale symmetry.** An RR of 0.5 and an RR of 2.0 are equally far from 1 on the log scale. CIs for ratios are asymmetric on the natural scale.

## 5. Continuous outcomes: mean differences, LS means, standardized effects

- **LS (least-squares) mean change.** A model-based (adjusted) estimate, usually from an MMRM or ANCOVA. It is not the raw average. Press releases nearly always report LS means.
- **"Placebo-adjusted difference."** The difference between arms in LS mean change. Pair it with its 95% CI, which press releases often omit.
- **Standardized mean difference.**
  - Cohen's d = MD / pooled SD. Hedges' g corrects small-sample bias.
  - Use an SMD to compare across scales.
  - Caveat: a homogeneous trial sample (narrow SD) inflates the SMD.
  - Cohen's 0.2/0.5/0.8 conventions are generic. They are not thresholds of clinical importance.
- **Look at the distribution, not only the mean.** A mean difference can come from a large benefit in a few people or a small benefit in many. Ask for responder distributions and cumulative distribution plots.
- **Within-group change is not a treatment effect.** "Symptoms fell 13 points" mixes natural course, regression to the mean, and placebo response. Only the *between-group* difference estimates the drug's effect.

## 6. Confidence intervals and p-values

**American Statistical Association statement on p-values** (Wasserstein & Lazar, *Am Stat* 2016 [M]), paraphrased:
1. P-values can indicate how incompatible the data are with a specified statistical model.
2. They do not measure the probability that the hypothesis is true, or that the data arose by chance alone.
3. Conclusions and decisions should not rest only on whether p passes a threshold.
4. Proper inference requires full reporting and transparency.
5. A p-value does not measure the size of an effect or the importance of a result.
6. By itself, a p-value is not a good measure of evidence.

**Common misreadings to flag** (Greenland et al., *Eur J Epidemiol* 2016 [M]):
- "p = 0.03 means a 3% chance the result is due to chance." **Wrong.**
- "p > 0.05 shows no effect." **Wrong.** Absence of evidence is not evidence of absence. Look at the CI: does it include clinically important effects?
- "A 95% CI means a 95% probability that the true value is inside this interval." **Not in frequentist terms.** Prefer: "values inside the interval are reasonably compatible with the data, given the model."
- "p < 0.0001 means a large effect." **Wrong.** Large samples make tiny effects highly "significant."
- **Comparing significance across groups.** "Significant in women, not in men" is not evidence of a difference between the groups. Test the interaction (Gelman & Stern, *Am Stat* 2006 [M]).

**Practice:** report the effect estimate with its CI first. Report the p-value second, as an exact value.

## 7. Power, sample size, and small-study distortions

- **Error types.**
  - Type I error (α): a false positive.
  - Type II error (β): a false negative. Power = 1 − β.
  - Trials are usually designed for 80–90% power at α = 0.05 (two-sided) for a pre-specified effect.
- **Underpowered trials** produce:
  - wide CIs;
  - exaggerated effect estimates among the "significant" results (the winner's curse; Type M error);
  - occasional estimates in the wrong direction (Type S error) (Gelman & Carlin, *Perspect Psychol Sci* 2014 [M]).
- **Most early psychedelic RCTs had fewer than 100 participants per arm.** Expect later and larger trials to show smaller effects. Compare: Phase 2 COMP360 vs its Phase 3 differences of about 3.6–3.8 MADRS points (see fda-pipeline.md).
- **Blinded sample-size re-estimation.** Adjusting n using pooled variance without unblinding is accepted practice when pre-specified, as in Definium's Panorama. **Unblinded** re-estimation needs a pre-specified alpha-protection method. Check which one was used.
- **Stopping early for benefit** overestimates effects, especially with few events (Bassler et al., JAMA 2010 [M]).

## 8. Clinical importance (MCID) in psychiatry scales

- **Statistical vs clinical significance.** Statistical significance is not clinical importance. The MCID (also called MID) is the smallest change patients perceive as beneficial.
- **MCID estimates vary by method** (anchor-based vs distribution-based), population, and baseline severity. **They are contested. Never present one MCID as settled.** Points to verify before citing [M]:
  - **MADRS.** Anchor-based estimates around 1.6–1.9 points (Duru & Fantino 2008) and higher values in other work. Sponsors in TRD cite about 2–3 points.
  - **HAM-D.** NICE (2004) used a 3-point / SMD 0.5 criterion, later dropped. Antidepressant-vs-placebo differences average about 2 HAM-D points in large meta-analyses (e.g., Kirsch 2008; Cipriani 2018 SMD ≈ 0.3).
  - **HAM-A and CAPS-5.** Minimal important differences are less established. CAPS-5 thresholds of about 10 points (within-person) and about 5–6 points (between-group) appear in the literature.
- **Comparator context.** Compare a new drug's effect with the effect of established treatments in similar populations and designs. Do not compare it with an idealized benchmark.

## 9. Implausibly large effects, regression to the mean, placebo response

- **Implausibly large effects.** A Cohen's d near 2 (e.g., GH001 Phase 2b, company-reported) in a psychiatric RCT is extraordinary. Ask:
  1. How small is n?
  2. Was the endpoint early (day 8)?
  3. Could participants tell which arm they were in?
  4. Was the rater blinded and independent?
  5. Was the placebo arm unusually poor (a "nocebo" or disappointment effect)?
  6. Is there a large-trial replication?
- **Regression to the mean.**
  - Mechanism: enrollment requires high symptom scores, so scores fall on retest without any treatment.
  - Consequence: only a randomized control arm addresses it.
  - Implication: uncontrolled "before and after" psychedelic studies cannot separate drug effect from regression and natural course.
- **Placebo response in psychiatry** is large and has grown over decades. Psychedelic trials invert the usual problem:
  - **Functional unblinding** inflates the expectancy effect in the active arm.
  - It may deflate the placebo arm, through "resentful demoralization."
  - Both distortions widen the observed difference (see study-design-flaws.md §3).

## 10. Analysis populations, missing data, and estimands

- **Analysis populations.**
  - **ITT** (intention-to-treat): analyze everyone as randomized. It preserves randomization and is the primary analysis for superiority.
  - **mITT** (modified ITT): definitions vary, e.g., "dosed participants" or "at least one post-baseline assessment." Check exactly who was excluded, and whether exclusion could depend on assignment.
  - **Per-protocol:** completers only. Biased toward the treatment when dropouts differ by arm. Appropriate as a sensitivity analysis, or as co-primary in non-inferiority trials.
- **Missing data.**
  - Ask how much is missing per arm, and why.
  - LOCF (last observation carried forward) is outdated and can bias in either direction.
  - MMRM assumes data are missing at random (MAR).
  - Ask for sensitivity analyses under missing-not-at-random assumptions (tipping-point and reference-based imputation).
- **Estimands (ICH E9(R1), 2019).** A trial must say *what* it estimates, including how it handles intercurrent events: rescue medication, discontinuation, or a second dose. For psychedelic trials, ask:
  - Does the estimand count post-randomization psychotherapy, a redose, or a change in antidepressant as part of "treatment"?
  - Is the open-label phase part of the estimand? It should not be.

## 11. Multiplicity and subgroups

- **Multiplicity.**
  - Problem: many endpoints, time points, doses, or analyses inflate the chance of false positives.
  - What protects against it: a pre-specified primary endpoint, a hierarchical (fixed-sequence) testing order for key secondaries, or alpha-splitting.
  - Check whether "met all key secondary endpoints" refers to a pre-specified hierarchy.
- **Outcome switching.** Compare the registered primary outcome (ClinicalTrials.gov, protocol, SAP) with the reported one. A changed endpoint, time point, or analysis is a major flag (COMPare project, Goldacre et al. 2019 [M]).
- **Subgroups.** Credible only if *all* of the following hold:
  - pre-specified, with a hypothesized direction;
  - few in number;
  - supported by a significant *interaction* test;
  - consistent across studies;
  - biologically plausible.
  - Use ICEMAN (Schandelmaier et al., CMAJ 2020 [M]).
- **Garden of forking paths / p-hacking.** Flexible analysis choices produce significant results without any fraud. Pre-registration and a public statistical analysis plan are the defense.

## 12. Surrogate and composite endpoints

- **Surrogate endpoints.** A biomarker or rating change is a surrogate unless it is itself what patients care about. Ask whether the surrogate has been validated at the trial level for this drug class. Psychiatric rating scales are clinical outcome assessments, but:
  - a 6-week score change is not the same thing as durable recovery;
  - it is not the same thing as functioning or survival.
- **Composite endpoints.**
  - Check whether the components carry similar importance and similar effect sizes.
  - Check whether the least important component drives the result.

## 13. Observational evidence and causal inference

- **Confounding by indication.** People who receive a treatment differ from those who do not, for the very reason they got it.
- **Selection and collider bias.** Conditioning on a common effect (e.g., studying only clinic attendees) can create spurious associations.
- **Immortal-time bias.** Follow-up time during which, by design, the outcome could not occur is misattributed to the exposed group. ROBINS-I V2 added questions on it.
- **Healthy-user / adherer effect.** Adherent people do better on placebo too.
- **Reverse causation.**
- **Tools:**
  - **DAGs** (directed acyclic graphs) to state assumptions.
  - **The E-value** (VanderWeele & Ding 2017 [M]): how strong unmeasured confounding would need to be to explain away the association.
  - **Bradford Hill considerations** as a structured argument, not a checklist score.
- **Psychedelic-specific.** Surveys of naturalistic users ("people who used psilocybin report lower depression") suffer heavy self-selection and survivorship bias. They cannot establish therapeutic efficacy.

## 14. Meta-analysis

- **Fixed vs random effects.** A random-effects model assumes the true effects differ between studies. Report τ² and the *prediction interval*: the range of effects expected in a new setting. It is often much wider than the CI.
- **I² measures inconsistency.** It is the proportion of variability due to heterogeneity rather than chance. It does not measure the *size* of heterogeneity. A small I² across 3 tiny studies means little.
- **Publication bias and small-study effects.** Funnel-plot asymmetry and Egger's test (need roughly 10 or more studies). Compare with registries to find unpublished trials.
- **Garbage in, garbage out.** Pooling high-risk-of-bias trials yields a precise biased estimate. Check risk-of-bias stratification and GRADE certainty.

## 15. Diagnostic and screening statistics

- **Accuracy measures.**
  - Sensitivity and specificity are properties of the test.
  - PPV and NPV depend on prevalence: base rates matter.
  - Example: sensitivity 90%, specificity 90%, prevalence 1% → PPV ≈ 8% (`risk_calc.py diagnostic`).
- **Likelihood ratios** (LR+, LR−) carry over across prevalences better than predictive values do.
- **Screening biases.**
  - Lead-time bias: earlier diagnosis makes survival look longer.
  - Length-time bias: screening catches slow-growing disease.
  - Overdiagnosis.
  - Only randomized trials of screening with mortality endpoints address all three.
- **Relevance to this skill.** Psychedelic programs screen out people at psychosis risk (personal or family history). Ask how accurate that screening is in the community, and what the PPV is outside a trial.

## 16. Bayesian reasoning and prior plausibility

- **The prior matters.** A "significant" result for an implausible hypothesis is more likely to be a false positive. The false-positive risk depends on the prior probability of a real effect, not only on α (Colquhoun, *R Soc Open Sci* 2014/2017 [M]).
- **Bayesian trial reports** give posterior probabilities, e.g., "probability the effect exceeds the MCID." Check the prior: skeptical, neutral, or enthusiastic. Check whether the conclusions survive a skeptical prior.
- **Base rates for drug development.** Only 28.9% of Phase 2 programs advance to Phase 3 (26.8% in psychiatry), and the likelihood of approval from Phase 2 is 15.1% (BIO/Informa 2011–2020) [V]. See fda-pipeline.md §2c. Use these to answer "is it a sure thing?" questions with a calibrated prior.
- **Expect effects to shrink.** Effect estimates usually fall from Phase 2 to Phase 3. Example: COMP360 went from −6.6 MADRS (Phase 2b) to −3.6 and −3.8 (Phase 3) [V].
- **Use this to calibrate, not to dismiss.** Strong prior skepticism should yield to repeated, well-blinded, preregistered, adequately powered replications.

## 17. Checklist: reading a press release or abstract

1. Is the trial registered? Do the primary endpoint and time point match the registration?
2. What is the comparator: inert placebo, active placebo, low dose, or standard care?
3. Effect on the primary endpoint: point estimate, **95% CI**, and units. Are these LS means?
4. Absolute numbers. Response and remission counts per arm, the definitions used, and the NNT with its CI.
5. Who was analyzed (ITT, mITT, completers)? What was the dropout per arm?
6. Harms. All adverse events, serious adverse events, and dropouts for adverse events. NNH. "Positive" psychoactive effects.
7. Blinding. Was it assessed? Were raters independent? What were the expectancy measures?
8. Durability. Randomized or open-label? Conditioned on response?
9. Peer review. Is there a full paper, or only a press release? Are data available?
10. Funding and conflicts. Sponsor role, author ties, and who wrote the paper.
11. Language. "Breakthrough," "unprecedented," "cure," and "paradigm" are flags. See study-design-flaws.md §6, "Spin."

## 18. Calculator recipes

```bash
S=scripts/risk_calc.py   # path relative to the skill folder
# Response counts (good event): 26/75 vs 5/74
python3 $S binary --events1 26 --n1 75 --events0 5 --n0 74 --event good
# Relapse counts (bad event)
python3 $S binary --events1 12 --n1 100 --events0 20 --n0 100 --event bad
# OR -> RR at baseline 40%
python3 $S orrr --or 3 --baseline 0.40
# Screening PPV
python3 $S diagnostic --sens 0.9 --spec 0.9 --prev 0.01
# Effect size from means and SDs (HYPOTHETICAL SDs: Emerge did not report SDs; do not cite the output as Emerge's d)
python3 $S smd --mean1 -13.3 --sd1 9.5 --n1 75 --mean0 -5.2 --sd0 9.5 --n0 74
# If a source gives a 95% CI for a mean difference but no SDs: SE = (upper - lower) / (2 * 1.96);
# pooled SD ≈ SE / sqrt(1/n1 + 1/n0). Label the result "derived from the reported CI".
# Relative claim -> natural frequencies
python3 $S frequencies --baseline 0.02 --relative-change -0.5
```

```bash
# Is "64% of 60" even possible? (GRIM-style denominator check)
python3 $S pctcheck --percent 64 --n 60
# SD and approximate SMD when only a mean difference and its CI are reported
python3 $S ci2smd --md -3.6 --lo -5.7 --hi -1.5 --n1 171 --n0 87
```

**Reconstructing counts.**
- When a source gives only percentages and arm sizes, reconstruct counts as round(% × n).
- Say so in the memo: "counts reconstructed from rounded percentages; ±1 participant."
- Run a sensitivity check with ±1 event if the conclusion is close.
- Always run `pctcheck` first. An impossible percentage means the analysis population differs from the randomized population, and that is a finding in itself.
