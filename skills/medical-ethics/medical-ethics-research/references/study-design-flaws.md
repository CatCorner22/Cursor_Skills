# Study Design Flaws, Biases, and Appraisal Tools

Use this file to find *what could make a reported result wrong*. Pair each flaw you raise with:
1. **where you saw it** (section, table, or registry field);
2. **which direction it likely pushes the estimate**;
3. **how large the effect could plausibly be** (minor / moderate / could overturn the result).

Tags: **[V]** verified 2026-11-09; **[M]** from training knowledge, not re-verified.

## Contents
1. Evidence hierarchy and source reliability
2. Bias catalogue (by trial stage)
3. Psychedelic-specific design problems
4. Appraisal and reporting tools (which one, when)
5. Research integrity red flags
6. Spin and hype
7. Writing up a flaw

---

## 1. Evidence hierarchy and source reliability

Design hierarchy, as a rough guide. *Quality within a design matters more than the design label.*
1. Systematic reviews and meta-analyses of well-conducted RCTs (graded with GRADE).
2. Large, preregistered, well-blinded RCTs.
3. Smaller or open-label RCTs.
4. Prospective cohort studies.
5. Case-control studies.
6. Cross-sectional surveys and case series.
7. Case reports, mechanistic reasoning, expert opinion.

Source reliability, for claims *about* a study:

| Source | Use it for | Limits |
|---|---|---|
| Peer-reviewed full paper + supplement + protocol/SAP | Methods, full results | Peer review misses a lot; check retractions |
| ClinicalTrials.gov / EU CTR / ISRCTN | Registered outcomes, dates, arms, results postings | Sponsor-entered; check the change history |
| FDA documents (briefing docs, CRLs, reviews, labels) | Independent regulatory analysis | Often redacted; review documents published only after approval |
| SEC filings (8-K, 10-K, S-1) | Company claims, under securities-law liability | Still sponsor framing |
| Company press release | What the company claims, and when | Not peer-reviewed; selective; LS means without CIs |
| Conference abstract / poster | Early signal | Often never published in full; numbers change |
| Preprint | Early full methods | Not peer-reviewed |
| Trade press (STAT, Endpoints, Fierce, BioSpace, RAPS, Psychedelic Alpha) | Discovery and context | Secondary; check against the primary source |
| Advocacy or industry-funded sites | Perspective | Interested parties |
| General media | Public framing | Frequent errors in effect size |

Always check **Retraction Watch** and the journal's article page for retractions, expressions of concern, and corrections.

## 2. Bias catalogue (by trial stage)

Names follow the Catalogue of Bias (Oxford CEBM) and Cochrane RoB 2 domains where possible.

### Design and allocation
- **Selection bias / allocation concealment failure.** Recruiters can predict the next assignment.
  - Look for: central randomization, sealed opaque envelopes, block sizes undisclosed.
- **Baseline imbalance.** By chance in small trials, or a sign of subverted randomization.
  - Look at Table 1, but don't significance-test baseline differences; that is meaningless under randomization.
- **Inappropriate comparator.**
  - An inert placebo where an active drug exists.
  - A sub-therapeutic dose of a competitor.
  - A comparator dose chosen to maximize the difference.
- **Population restriction / spectrum bias.** Narrow inclusion criteria limit generalizability. Typical exclusions: suicidality, psychosis risk, comorbid substance use, older adults.
- **Run-in / enrichment designs.** Excluding placebo responders or non-tolerators before randomization inflates the effect.
- **Prior-exposure selection.** Participants with prior positive experience of the drug class are more likely to enroll, and to guess their arm.

### Performance (during treatment)
- **Performance bias.** Care differs between arms beyond the intervention, e.g., more therapist attention.
- **Co-intervention.** Psychotherapy, concomitant medication changes, or rescue medication differ by arm.
- **Contamination.** Control participants obtain the intervention outside the trial.
- **Therapist or center effects.** Clustering of outcomes by therapist; few therapists delivering all sessions.

### Detection (measuring outcomes)
- **Unblinded outcome assessment.** A rater knows the arm. Worst for subjective scales.
- **Functional unblinding.** The participant or rater infers the arm from the drug's effects (see §3).
- **Ascertainment bias.** Harms are sought more actively in one arm. Or harms are sought only through open questions, which under-detects them.
- **Measurement bias.** Unvalidated scales, or a change of scale version mid-trial.

### Attrition
- **Differential dropout.** Dropout differs by arm, especially if it relates to the outcome (e.g., disappointment in the placebo arm).
- **Exclusions after randomization.** mITT definitions that drop people based on post-randomization events.
- **Inadequate handling of missing data.** See statistics-appraisal.md §10.

### Reporting
- **Selective outcome reporting / outcome switching.** Registered and reported primary outcomes differ.
- **Selective analysis reporting.** One of several analyses is chosen post hoc.
- **Publication bias.** Negative trials go unpublished. Look in registries for completed-but-unreported trials.
- **Time-lag bias.** Positive results are published sooner.
- **Citation bias.** Positive studies are cited more often.

### Analysis
- See statistics-appraisal.md §§6–14: p-hacking, multiplicity, unplanned subgroups, inappropriate per-protocol analysis, dichotomization, regression to the mean, and others.

## 3. Psychedelic-specific design problems

1. **Functional unblinding.**
   - Problem: intense subjective effects reveal assignment. Evidence: MDMA participants nearly all guessed correctly (Lykos AdComm); TEAE rates of 95% vs 63% (Definium Panorama).
   - **Equal-unblinding comparison.** Williams ZJ, Barnett H, Szigeti B. "Psychedelic Therapy vs Antidepressants for the Treatment of Depression Under Equal Unblinding Conditions." *JAMA Psychiatry* 2026;83(5):461–468 (online 2026-03-18; doi 10.1001/jamapsychiatry.2025.4809) [V: JAMA abstract page].
     - Logic: psychedelic trials are effectively open label, so compare them with **open-label** antidepressant trials, not placebo-controlled ones.
     - Data: 8 psychedelic-assisted-therapy trials (249 patients) vs. 16 open-label antidepressant trials (7,921 patients); a blinded-antidepressant comparison set of 144 trials (31,792 patients). Outcome: within-arm HAM-D-17 change.
     - Result: **difference 0.3 points favoring open-label antidepressants (95% CI −1.39 to 1.98; P = .73).** Blinding mattered for antidepressants (open label better by 1.3 points, 95% CI 0.07 to 2.51) but not for psychedelic therapy (printed as 0.67 points, 95% CI −3.08 to 1.73; the CI centres near −0.68, so the printed sign is probably a typo in the source), which supports "effectively always open label."
     - Critiques to report alongside it [S: published reader comments; expert reactions]: the psychedelic samples skew toward treatment-resistant patients; the sample sizes are very unequal; there is no patient-level adjustment for severity or treatment history; and within-arm comparisons across trials are observational.
     - Use: when a source claims psychedelics beat SSRIs, cite this paper and Hieronymus 2025 (below) together, with their limitations. Neither shows psychedelics are ineffective; both show the size of the advantage is not established.
   - **Control arms underperform.** Hieronymus, López, Sjögren & Lundberg, *JAMA Netw Open* 2025 (doi 10.1001/jamanetworkopen.2025.24119; 17 double-blind MADRS trials, n=4,960): control-arm improvement was about half as large in psilocybin trials (standardized mean change 0.50) as in SSRI (1.00) and esketamine (1.12) trials; control-arm response 19% vs 33% vs 42%. Part of psilocybin's large between-group effect comes from control groups that did poorly, likely from disappointment once participants realize they did not get the drug [V: Technology Networks and AJMC summaries of the paper; the mechanism is the authors' hypothesis]. Hsu et al., *BMJ* 2024;386:e078607 (Bayesian network meta-analysis) reached a similar conclusion: against the placebo response seen in antidepressant trials, high-dose psilocybin's advantage shrank to a small effect [V: AAFP POEM]. Use both when a press release compares psilocybin's effect size with SSRIs'.
   - Mitigations, none complete:
     - active placebo (niacin, diphenhydramine, methylphenidate);
     - low-dose comparators (1 mg COMP006; 5 mg uAspire; 50 µg Panorama);
     - blinded central or remote raters;
     - blinding-integrity indices (Bang; James) and expectancy measures (e.g., the Stanford Expectations of Treatment Scale [M]);
     - masking of study hypotheses;
     - dose-response designs.
   - The 2026 FDA final guidance endorses this menu.
   - **Ask:** was blinding assessed? With what result, and in which arm? Were the outcomes rated by someone who never met the participant?
2. **Expectancy and allegiance.**
   - Participants and investigators often hold strong prior beliefs. Media hype raises expectancy further.
   - Investigator allegiance can shape therapy delivery and rating.
3. **Psychotherapy as co-intervention.**
   - In drug-plus-therapy designs, the "treatment" is a package. A two-arm trial (drug+therapy vs placebo+therapy) estimates the drug's effect *in the presence of* therapy, under unblinding that may change how the therapy works in each arm.
   - FDA regulates the drug, not the therapy. Ask how therapy adherence was measured, and whether the therapy manual was followed.
4. **Set, setting, and music.** Environmental elements are part of the intervention, and they are rarely standardized or reported in detail.
5. **Placebo-arm disappointment ("resentful demoralization" / nocebo).** Participants who realize they got placebo may do worse than they would have outside a trial. This widens the difference.
6. **Responder-conditioned durability.** Long-term claims in open-label extensions, or among week-6 responders only, lose randomization. Survivors look durable.
7. **Crossover and open-label extension contamination.** Placebo participants cross over to the drug, so long-term randomized comparisons vanish.
8. **Prior psychedelic use.** Experienced users are more likely to enroll, to guess their arm, and to have a favorable prior experience. The Lykos CRL raised selection concerns about this.
9. **Adverse event capture of "positive" effects.** Euphoria and other "positive" psychoactive effects are abuse-relevant adverse events. Under-recording them hides abuse liability. This was a main ground of the Lykos CRL, and the 2026 final guidance now expects these effects to be recorded.
10. **Session-level safety events.** Boundary violations, touch, and sexual misconduct are adverse events too. Were they monitored (video review) and reported?
11. **Small, single-site early trials with charismatic investigators.** High risk of inflated effects and of conduct problems.
12. **Short primary endpoints for single-dose drugs.** The primary endpoint at week 3–6 says nothing about months.
13. **Concomitant medication washout.** Tapering antidepressants before dosing creates a withdrawal-affected baseline, and a selected population. Adjunctive designs (e.g., HLP003) avoid this but change the question.

## 4. Appraisal and reporting tools (which one, when)

| Situation | Tool | Notes |
|---|---|---|
| Reporting set and setting in psychedelic trials | **ReSPCT** (Reporting of Setting in Psychedelic Clinical Trials): 30 extra-pharmacological items in four domains (physical environment, dosing-session procedure, therapeutic framework and protocol, subjective experiences); 4-round Delphi, 89 experts from 17 countries, consensus at ≥70% | Pronovost-Morgan C, Greenway KT, Roseman L, et al. *Nat Med* 2025;31(7):2186–2195 (doi 10.1038/s41591-025-03685-9) [V: PubMed]. Use it with CONSORT 2025 to check whether a trial reports therapy hours, music, room, touch policy, and therapist training. |
| Reporting of a completed RCT | **CONSORT 2025** (30-item checklist + flow diagram; new open-science section) [V] | Published April 2025 in BMJ, JAMA, Lancet, Nat Med, PLOS Med. Replaces CONSORT 2010. |
| Trial protocol completeness | **SPIRIT 2025** (34 items + schedule diagram) [V] | Replaces SPIRIT 2013 |
| Harms reporting | CONSORT Harms (2022 extension) [M] | |
| Risk of bias in an RCT result | **Cochrane RoB 2** [M] | Five domains: randomization; deviations from intended interventions; missing outcome data; outcome measurement; selection of the reported result |
| Risk of bias in a non-randomized study of interventions | **ROBINS-I V2** (launched November 2024; refined 2025; adds algorithms and immortal-time questions) [V] | |
| Systematic review reporting | PRISMA 2020 [M] | |
| Systematic review quality | AMSTAR 2 [M]; ROBIS [M] | |
| Certainty of a body of evidence | **GRADE** [M] | Starts high for RCTs; downgraded for risk of bias, inconsistency, indirectness, imprecision, publication bias |
| Observational study reporting | STROBE [M] | |
| Diagnostic accuracy | STARD (reporting) [M]; QUADAS-2 (bias) [M] | |
| Quick structured appraisal | CASP checklists [M] | Useful for lay-accessible memos |
| Subgroup credibility | ICEMAN [M] | |
| Good clinical practice in conduct | **ICH E6(R3)** (adopted 2025-01-06; Annex 2 endorsed 2026-06) [V] | Risk-based quality management; critical-to-quality factors |
| Estimands | ICH E9(R1) [M] | |

## 5. Research integrity red flags

- No registration, or retrospective registration after enrollment began.
- Primary outcome changed without a dated, justified protocol amendment.
- Numbers that don't add up: arm totals, percentages that don't match the counts, impossible SDs. GRIM/SPRITE-style checks [M].
- Results too good, and too consistent across small trials.
- Data or the protocol unavailable on request.
- Undisclosed conflicts of interest; sponsor employees as authors without a role statement; ghost-writing.
- Retractions or expressions of concern involving the same team, site, or dataset. The 2024 *Psychopharmacology* retractions of MAPS/Lykos-affiliated MDMA papers are an example.
- Misconduct reports at sites (see psychedelic-ethics-issues.md §3).

## 6. Spin and hype

**Spin** is reporting that makes results look more favorable than the data justify (Boutron et al., JAMA 2010 [M]). Patterns:
- Emphasizing secondary endpoints, subgroups, or within-group change when the primary endpoint failed.
- "Trend toward significance" for p = 0.08.
- Relative benefits next to absolute harms (see statistics-appraisal.md §2).
- Causal language in observational studies.
- Superlatives: "unprecedented," "breakthrough," "paradigm-changing," "cure."
- Calling a regulatory "Breakthrough Therapy designation" or a "priority voucher" proof of efficacy. These are *process* designations based on preliminary evidence or policy priority.
- Calling an unconventional threshold "response," e.g., ≥25% instead of ≥50%.

**Psychedelic hype.** Commentators have warned about a hype cycle in psychedelic medicine (e.g., Yaden, Potash & Griffiths, *JAMA Psychiatry* 2022, "Preparing for the bursting of the psychedelic hype bubble" [M]). The 2026 political environment (EO 14401, CNPVs) adds momentum. Momentum is not evidence. The skill's job is to separate them.

## 7. Writing up a flaw

Use this structure in a memo:
> **Flaw:** [name, in the catalogue's term]
> **Where:** [source, section/table/registry field]
> **Direction:** [likely overstates / understates / unclear]
> **Magnitude:** [minor / moderate / could overturn the conclusion] — [one sentence of reasoning]
> **What would resolve it:** [the data, analysis, or study that would settle it]
> **Label:** [VERIFIED FACT / SOURCE CLAIM / ANALYTICAL JUDGMENT]
