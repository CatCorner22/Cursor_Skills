---
name: statistical-literacy
description: "Decode statistical claims: absolute vs relative risk, base rates, conditional probability, Bayes, effect sizes, confidence intervals, p-values, and what numbers actually imply for a real decision. Use when reviewing studies, health stats, A/B tests, polls, ML metrics, dashboards, news headlines, or any claim with percentages, odds, risk ratios, or significance. Scope boundary: this skill interprets and explains statistics — it does not replace domain experts for causal identification, trial design, or formal biostatistics sign-off."
metadata:
  priority: 8
  promptSignals:
    phrases:
      - "absolute risk"
      - "relative risk"
      - "what do these statistics mean"
      - "is this statistically significant"
      - "odds ratio"
      - "confidence interval"
      - "base rate"
      - "bayesian"
      - "number needed to treat"
      - "misleading statistic"
    allOf:
      - [risk, relative]
      - [risk, absolute]
      - [statistics, mean]
      - [p-value, interpret]
    anyOf:
      - "relative risk"
      - "absolute risk"
      - "hazard ratio"
      - "confidence interval"
      - "statistical significance"
      - "base rate fallacy"
      - "number needed to treat"
      - "odds ratio"
---

# Statistical literacy — what the numbers actually say

**Mandate:** Every percentage, ratio, or "significant" claim gets translated into **plain consequences for a defined population and decision** — not parroted back with jargon.

Run the **DECODE** workflow on every statistical review. Do not stop at "the study found X."

---

## DECODE workflow (mandatory)

```
D — Define the claim in one sentence (what happened, in whom, over what time?)
E — Extract the raw counts (events / exposed / total), not just ratios
C — Convert relative → absolute (and back) on the right base rate
O — Outcome framing for the decision-maker (NNT, NNH, expected value)
D — Dependencies (base rate, selection, confounding, multiple comparisons)
E — Epistemic status (exploratory vs confirmatory; CI width; replication)
```

If any step cannot be completed from the source, say what is missing — do not fill gaps with assumptions.

---

## Absolute vs relative risk (core)

Always report **both**. Relative alone is the most common public mislead.

| Term | Definition | Example |
|---|---|---|
| **Baseline / control risk** | Event rate without intervention | 2% of patients had the outcome |
| **Absolute risk (AR)** | Raw probability in a group | Treatment group: 1% |
| **Absolute risk reduction (ARR)** | Control AR − Treatment AR | 2% − 1% = **1 percentage point** |
| **Relative risk (RR)** | Treatment AR ÷ Control AR | 1% ÷ 2% = **0.5** (50% relative reduction) |
| **Relative risk reduction (RRR)** | 1 − RR (or % drop in relative terms) | **50% RRR** — sounds large |
| **Number needed to treat (NNT)** | 1 ÷ ARR | 1 ÷ 0.01 = **100** (treat 100 to prevent 1 event) |
| **Number needed to harm (NNH)** | 1 ÷ absolute risk *increase* from harm | Same math on adverse events |

**The insight:** A **50% RRR** can mean preventing 1 event per 100 people (ARR 1pp) or 1 per 10,000 (ARR 0.01pp). The relative number hides the base rate.

### Conversion rules

```
RR  = AR_treatment / AR_control
ARR = AR_control − AR_treatment   (benefit; sign flip for harm)
RRR = 1 − RR  (or (control−treatment)/control when stated as %)
NNT = 1/ARR   (only when ARR > 0)
```

**Odds ratio (OR) ≠ risk ratio** when outcomes are common (>10%). For rare events OR ≈ RR; for common events, OR exaggerates — convert to risks if cell counts are given.

---

## Base rates (without them, nothing is understood)

**Base rate fallacy:** Ignoring how common the outcome is before the test or intervention.

```
P(disease | positive test) depends on P(disease) in the population,
not just sensitivity and specificity.
```

Always ask: **"Out of 10,000 people like me, how many…?"**

Bayes template when counts exist:

```
Prior:     base rate of outcome
Likelihood: test/study sensitivity & specificity (or study design)
Posterior:  updated probability after evidence
```

If only a relative effect is given, reconstruct absolute impact:

> "RR 0.8" with 5% baseline → 4% treated (ARR 1pp, NNT 100).  
> Same RR with 0.5% baseline → 0.4% treated (ARR 0.1pp, NNT 1000).

---

## Probability — evaluate multiple ways

Do not treat "probability" as one thing. Label which kind you mean:

| Lens | Question it answers | When to use |
|---|---|---|
| **Frequentist long-run** | If we repeated this experiment, how often…? | A/B tests, RCTs, polls with sampling frame |
| **Conditional** | P(A\|B) — probability *given* subgroup or evidence | Risk in *your* age group, not the whole trial |
| **Joint / marginal** | P(A and B) vs P(A) — Simpson's paradox lives here | Aggregated vs stratified tables |
| **Expected value** | Σ outcome × probability | Cost-benefit, policy, portfolio decisions |
| **Bayesian posterior** | Belief after data + prior | Diagnostics, sparse data, sequential updates |
| **Calibrated uncertainty** | CI or credible interval width | "How precise is this, not just which side of zero?" |

**Simpson's paradox check:** If a trend reverses when combining groups, **stratify** before concluding.

---

## Effect size vs significance (different questions)

| Question | Tool | Misread if you only look at… |
|---|---|---|
| Is there *any* signal? | p-value, CI excludes null | Ignoring effect size → "significant but trivial" |
| How *big* is it? | ARR, Cohen's d, OR/RR, lift, R² | p-value alone |
| How *precise* is the estimate? | CI width, standard error, n | Point estimate alone |
| Does it matter for *this* decision? | NNT, cost, thresholds, MCID | Statistical significance |

**p-value is not:**
- P(hypothesis is true)
- P(result was fluke)
- Proof of importance

**It is:** P(data this extreme \| null model). Small p + tiny effect = statistically significant, practically meaningless.

Always pair: **estimate + CI + absolute impact at relevant base rate.**

---

## Reading a headline or abstract (checklist)

1. **Population** — who, where, eligibility (generalize carefully)
2. **Time horizon** — 6 weeks vs 10 years changes AR entirely
3. **Outcome definition** — surrogate vs hard outcome (cholesterol ↓ vs death ↓)
4. **Numerators/denominators** — demand cell counts; reject "50% increase" without baseline
5. **Comparator** — vs placebo, vs standard care, vs nothing?
6. **Absolute numbers** — compute ARR/NNT even if paper only gives RR
7. **Harms** — same absolute/relative treatment for side effects
8. **Multiple comparisons** — many endpoints → expect some p<0.05 by chance
9. **Selection & survivorship** — who dropped out; who wasn't enrolled
10. **Confounding** — observational data cannot prove causation without design/tools
11. **Funding & pre-registration** — exploratory fishing vs confirmatory test

---

## Domain quick notes

### Medicine / epidemiology
- Prefer **ARR, NNT, NNH** for patient decisions; RRR for headlines only with base rate beside it.
- Hazard ratios are **instantaneous** — not the same as cumulative risk over follow-up.

### A/B tests & product metrics
- **Relative lift** `(B−A)/A` vs **absolute lift** `B−A` on conversion rate.
- Small sample + peeking → inflated false positives; pre-specify n or use sequential methods.
- Statistical significance ≠ business significance (0.01pp on billions may be worthless).

### ML / data science metrics
- Accuracy misleading on imbalanced classes → precision, recall, F1, AUROC, calibration.
- **Calibration:** predicted 70% should happen ~70% of the time.
- Confidence intervals on offline metrics before shipping.

### Polls & surveys
- Margin of error applies to **whole sample**, not subgroups (MOE widens).
- Non-response bias can dominate sampling error.

---

## Output template (use in reviews)

```markdown
## What they claim
[One sentence]

## What the numbers actually say
- Baseline risk: …
- Absolute effect: … (… percentage points)
- Relative effect: … (only meaningful alongside baseline)
- For 10,000 people like [population]: ~… would …

## Precision & limits
- CI / sample size: …
- Confounding / generalizability: …

## Decision implication
- If you care about [outcome]: …
- What would change my mind: …
```

---

## Anti-patterns (never do these)

| Wrong | Right |
|---|---|
| "50% less risk!" without baseline | "From 2% to 1% — 1 fewer per 100" |
| Treat OR as RR for common outcomes | Convert with cell counts or use risk ratio |
| p < 0.05 → "proven" | Effect size + CI + replication |
| Average without distribution | Median, quartiles, or who the average excludes |
| Ignore time horizon | State period explicitly |
| Subgroup cherry-pick without correction | Pre-specified or labeled exploratory |

---

## Boundaries

| This skill does | This skill does not |
|---|---|
| Interpret presented statistics | Design trials or power analyses from scratch |
| Convert relative ↔ absolute | Replace IRB / biostatistician sign-off |
| Flag misleading framing | Prove causal claims from observational data alone |
| Bayes with given inputs | Invent priors without labeling them as assumptions |

For **coding** experiment analysis pipelines → implement with domain tools; this skill governs **interpretation** of results.

For **HF/community evals** metric choice → `huggingface-community-evals` builds; this skill reads the leaderboard.

---

## Quick reference card

```
Relative impresses. Absolute decides.
Base rate first. Then update with evidence.
Significance ≠ size ≠ importance.
Show me the cells: a / b vs c / d.
What happens to 10,000 people like me?
```
