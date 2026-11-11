# 13. UX Research Methods and Measurement

Researched 2026-11-11. This file also **replaces the "not verified" notes** in [03](03-cognitive-load-and-frustration.md) and [08](08-audit-checklist.md) for SUS, NASA-TLX, and UEQ-S (see section 4). Grades: A standard/primary instrument, A- free peer-reviewed, B NN/g or peer-reviewed, C practitioner. **(judgment)** = inference.

## 1. Choosing a method

| Question | Method | Typical n | Source |
|---|---|---|---|
| What are the biggest usability problems in this design? | Moderated qualitative usability test | 5 per user group (see 2) | [NN/g](https://www.nngroup.com/articles/how-many-test-users/) |
| What are people's real goals and context? | Interviews, contextual inquiry, diary study | varies | NN/g studies of AI chatbots used a 2-week diary study (18 participants) [NN/g](https://www.nngroup.com/articles/ai-prompt-structure/) |
| How should content be grouped? | Open card sort (discovery) | NN/g: at least 15 per user group | [NN/g card sort vs tree test](https://www.nngroup.com/articles/card-sorting-tree-testing-differences/), [how many](https://www.nngroup.com/articles/how-many-test-users/) |
| Can people find things in this navigation? | Tree test (evaluation; text-only hierarchy, lacks visual context clues) | quantitative scale | NN/g |
| What is the success rate / time (benchmark)? | Quantitative usability study | 40 (15% margin, 95% confidence, binary metric); at least 20 for any statistics | [NN/g summary](https://www.nngroup.com/articles/summary-quant-sample-sizes/) |
| Which version performs better in production? | A/B (online controlled experiment) | thousands (see 3) | Kohavi et al. |
| Where do people look? | Eye tracking | NN/g: 39 users for stable heatmaps | NN/g (see [04](04-eye-tracking-and-attention.md)) |
| Is it usable by expert reviewers' standards? | Heuristic evaluation (Nielsen's 10) | experts | [NN/g heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) |

## 2. The 5-user rule and its critique

| Claim | Evidence | Source | Grade |
|---|---|---|---|
| Problems found by n users = N(1-(1-L)^n); typical L = 31% averaged over projects (Nielsen & Landauer, INTERCHI '93). Five users find about 85%; about 15 users to find nearly all; better to run **3 small iterative tests of 5** than one of 15. | Model from projects studied by Nielsen and Landauer | [Nielsen 2000](https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/) | B (author-originated, model-based) |
| Applies to **comparable** users; test 3-4 per group for two groups, 3 per group for three or more. | Same | Same | B |
| **Critique:** with 60 users on one task (web timesheet), random groups of 5 found on average 85% of problems but **between 55% and ~100%**; groups of 10 raised the minimum to 80%; groups of 20 to 95%. So one 5-user study can miss nearly half. | Faulkner resampling of 100 draws per size | [Faulkner 2003, PubMed](https://pubmed.ncbi.nlm.nih.gov/14587545/) | A- (one app, one task; novice/expert mix) |
| "5 users" is about **finding** problems, not **measuring** rates. 5 of 5 task completions still has a 95% interval of roughly **48% to 100%**. Small samples can show a task is bad far more easily than prove it is good. | Binomial confidence interval | [MeasuringU](https://measuringu.com/conf_intervals/), [small-n practices](https://measuringu.com/small-n/) | C+ |
| Sessions typically 60-90 minutes; fatigue after that. | NN/g | [NN/g time budgets](https://www.nngroup.com/articles/time-budgets-for-usability-sessions/) | B |

**Takeaway (judgment):** use about 5 per distinct segment per round for discovery, iterate, and never report percentages from five people as if they were rates. For rare but serious problems (e.g., accessibility barriers for a specific disability), recruit **that group** specifically. The model also assumes the problems are equally findable; Faulkner's spread shows that assumption is shaky.

## 3. A/B testing pitfalls

| Pitfall / rule | Detail | Source | Grade |
|---|---|---|---|
| **Sample Ratio Mismatch (SRM)** | If observed user counts differ from the designed split, stop analyzing. Test with chi-square, not by eyeballing; Microsoft uses p < 0.0005 as a conservative threshold. Real example: 821,588 vs 815,482 users (50.2% vs 49.8%) on a designed 50/50 split has p ≈ 1.8e-6. "Missing users are rarely just some users": in an MSN test, the heaviest users were being classified as bots and removed, flipping the result once fixed. | [Microsoft Research SRM](https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/); [Kohavi pitfalls slides](https://exp-platform.com/Documents/2017-05-17EmetricsControlledExperimentsPitfallsKohaviNR.pdf) | B |
| **Twyman's law** | "Any figure that looks interesting or different is usually wrong." Treat surprising wins as likely bugs; the most common bias is to accept good results and investigate bad ones. | [Seven Rules of Thumb](https://exp-platform.com/Documents/2014-08-27ExperimentersRulesOfthumbKDD.pdf), Kohavi slides | B |
| Validate the platform | Run A/A tests; expect a "significant" difference about 5% of the time; p-value distribution across A/As should be uniform. | Kohavi slides | B |
| Outliers | One huge buyer can skew revenue; cap per-user values (e.g., 99th percentile). | Kohavi slides | B |
| Realistic effect sizes | Most progress is 0.1%-1% improvements after a lot of work; "your mileage will vary"; stories from other companies often don't replicate. Avoid complex multi-variable designs; run many simple experiments; need thousands of users. | Seven Rules of Thumb | B |
| Not statistically tested here | Peeking/optional stopping, multiple comparisons, novelty effects, Simpson's paradox. All are well-known; I did not read a source this session. | | unverified |

Caveat: Kohavi's samples are Microsoft/Bing/Amazon scale (hundreds of thousands to millions of users). Small sites will usually lack power for tiny effects **(judgment)**; prefer qualitative tests plus bigger, bolder changes.

## 4. Standardized instruments (verified sources)

| Instrument | What it is | Verified facts | Source | Grade |
|---|---|---|---|---|
| **SUS** (System Usability Scale) | 10-item questionnaire of **perceived usability**, 0-100 score | Brooke, "SUS: A 'Quick and Dirty' Usability Scale," 1996 book chapter (Usability Evaluation in Industry, CRC Press); MeasuringU says it dates to 1986. Lewis's 2018 review: "quick but not dirty," most widely used standardized perceived-usability questionnaire. Across ~500 studies the **average score is 68**; above 68 is above average. Standard scoring: odd items (rating - 1), even items (5 - rating), sum x 2.5 (confirmed via search summary; check Brooke or Lewis before publishing). | [Brooke 1996 DOI](https://doi.org/10.1201/9781498710411-35); [Lewis 2018](https://doi.org/10.1080/10447318.2018.1455307); [MeasuringU](https://measuringu.com/sus/) | B |
| **NASA-TLX** | Subjective **workload** rating | Hart & Staveland 1988 (in *Human Mental Workload*, North Holland). Developed at NASA Ames; from **16 experiments** with 10 workload factors, reduced to **six subscales** (mental demand, physical demand, temporal demand, performance, effort, frustration). Original method weights the subscales per task to produce an overall score. NASA calls it the "gold standard" for subjective workload. Public-domain technical document available. | [NASA TLX page](https://www.nasa.gov/human-systems-integration-division/nasa-task-load-index-tlx/); [Hart & Staveland, Archive.org](https://archive.org/details/nasa_techdoc_20000004342); [NASA publication entry](https://human-factors.arc.nasa.gov/awards_pubs/publication_view.php?publication_id=2553) | A- (primary) |
| **UEQ** | User Experience Questionnaire | Six scales: attractiveness, perspicuity, efficiency, dependability, stimulation, novelty. Free in 30+ languages with analysis spreadsheets. **UEQ-S** is a short **8-item** version. Original: Laugwitz, Schrepp & Held 2008. UEQ+ is a modular extension. Authors: Hinderks, Schrepp, Thomaschewski. | [ueq-online.org](https://www.ueq-online.org/) | B (instrument site) |

Use **(judgment):** SUS for overall perceived usability comparisons over time; NASA-TLX for effortful tasks (data entry, complex workflows, AI-assisted tasks); UEQ-S when emotional/novelty aspects matter. Pair every questionnaire with behavior (success, time, errors). Questionnaires measure *perception*; the aesthetic-usability effect ([09](09-visual-design-fundamentals.md)) can inflate it.

Limits: SUS benchmarks (68) come from MeasuringU's collected studies, which skew toward software/web products from practitioners; do not treat 68 as universal. I did not independently check the UEQ benchmark dataset. Original SUS paper PDF and UEQ items were not read in full.

## 5. Heuristic evaluation

Nielsen's 10 usability heuristics are "broad rules of thumb and not specific usability guidelines." Names: visibility of system status; match between system and real world; user control and freedom; consistency and standards; error prevention; recognition rather than recall; flexibility and efficiency of use; aesthetic and minimalist design; help users recognize, diagnose, and recover from errors; help and documentation. Source: [NN/g](https://www.nngroup.com/articles/ten-usability-heuristics/) (I read excerpts of heuristics 2-7, error-message guidance, and documentation; the remaining names are standard and listed on that page). Heuristic reviews find different problems than user tests and miss real behavior **(judgment)**; do both when possible.

## 6. Information architecture

| Method | Use it for | Caveat | Source |
|---|---|---|---|
| Card sorting | Generating ideas for groupings and labels, early | Users group differently; gives *ideas*, not the final structure | [NN/g](https://www.nngroup.com/articles/card-sorting-tree-testing-differences/) |
| Tree testing | Evaluating findability of an existing/proposed structure | Isolated hierarchy; lacks placement/color cues that provide information scent | Same |
| Both | Employing both helps determine intuitive navigation | | Same |

Open tools named by NN/g: Optimal Sort, Treejack (commercial). Not researched: first-click testing, search log analysis.

## 7. Jobs To Be Done (JTBD)

| Point | Source | Grade |
|---|---|---|
| Idea: customers "hire" products to make progress in a circumstance; the milkshake story found a morning-commute job (one free hand, boredom, hunger by 10 a.m.). | [Christensen et al., MIT Sloan Management Review](https://sloanreview.mit.edu/article/finding-the-right-job-for-your-product/); [HBR 2016](https://hbr.org/2016/09/know-your-customers-jobs-to-be-done) | B (case-based) |
| Two camps disagree: Christensen/Moesta "switch interviews" (qualitative) vs Ulwick's Outcome-Driven Innovation (quantified importance vs satisfaction on 50-150 desired outcomes, surveying up to ~1000). Ulwick argues the milkshake method is "technically flawed" for segmentation. | [Ulwick](https://jobs-to-be-done.com/outcome-based-market-segmentation-outperforms-milkshake-marketing-2eadf3d07b23) (partisan); [Chugunov Advisory critique summary](https://chugunov.au/frameworks/jtbd) (D) | C/D |
| Critiques listed by one secondary source: hard to do well, mixed replication of the milkshake case, lacks trade-off mechanism. Quoted statistics (e.g., "7x sales") are **unverified** by me. | Chugunov (D) | D |

**Judgment:** JTBD is a useful interview *lens* (what progress, what circumstance, what alternatives), not a validated predictive method. Use it to reframe requirements; verify with behavior.

## 8. Analytics and measurement hygiene (judgment)

Decide questions first; instrument events deliberately; separate vanity (page views) from outcomes (task completion, errors, retention); segment by device and assistive tech where lawful; remember consent-gated analytics are a biased sample ([12](12-frontend-engineering-issues.md)). Government example of mixing methods: GSA/Digital.gov describe combining qualitative and quantitative data to evaluate websites ([Digital.gov usability](https://www.usability.gov/how-to-and-tools/methods/system-usability-scale.html), a landing page; no method details read).

## 9. Minimal research plan template

1. Decision this research informs. 2. Users/segments and recruiting criteria (include assistive tech users). 3. Tasks (realistic, not leading). 4. Metrics: success, time, errors, SUS/UEQ-S/NASA-TLX as relevant. 5. Sample and why. 6. Analysis rules written **before** looking (especially for A/B). 7. Consent and data handling. Digital.gov offers free sample research plans, scripts, consent forms (listed on its Usability page).
