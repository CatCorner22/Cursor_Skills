# 09. Visual Design Fundamentals (what the evidence supports)

Researched 2026-11-11. Grades follow the README scale (A standard, A- free peer-reviewed, B primary NN/g or peer-reviewed/paywalled, C practitioner, D vendor/aggregator). **(judgment)** = my inference. **(not researched)** = I did not read a source this session; treat as general knowledge to verify.

## 1. Why visual design matters beyond taste

| Finding | Detail | Source | Grade |
|---|---|---|---|
| Visual appeal is judged in a blink | Participants rated homepage appeal after 50 ms and again at 500 ms; the two sets of ratings correlated at r = .947 (means) across 3 studies at Carleton University. Authors suggest a possible "mere exposure" account. | [Lindgaard et al. 2006, Behaviour & IT 25(2)](https://www.makinggood.ac.nz/media/1265/lindegaardetal_2006_attention.pdf) (full text mirror); [DOI](https://doi.org/10.1080/01449290500330448) | B |
| Designers disagreed on *why* | Eight designers asked to name the design features behind the ratings "disagreed so vehemently" that no principles could be isolated. | Same paper | B |
| Beauty shapes perceived usability | ATM-like app: perceived aesthetics and perceived usability strongly correlated before and after use; aesthetic level affected post-use perceptions of both, **actual usability level did not**. | [Tractinsky, Katz & Ikar 2000](https://academic.oup.com/iwc/article-abstract/13/2/127/898608) | B |
| First impressions are partly predictable | Colorfulness + visual complexity (+ age, education) explained about half the variance in 500 ms appeal ratings of 450 sites rated by 548 volunteers. Authors say first impression later affects usability and trust opinions. | [Reinecke et al., CHI 2013](https://eecs.harvard.edu/~kgajos/papers/2013/reinecke13predicting.shtml) | B |
| Looks drive credibility judgments | 2,684 people compared live sites; "design look" appeared in 46.1% of credibility comments (information design 28.5%, information focus 25.1%). Looks mattered less to experts judging health/finance sites in a parallel study (as reported by the Stanford report). | [Fogg et al. 2003 (ACM)](https://dl.acm.org/doi/10.1145/997078.997097); [Stanford report](https://credibility.stanford.edu/pdf/How_Do_People_Evaluate_a_Web_Site%27s_Credibility_v37.pdf) | B |
| Aesthetic-usability effect has limits | Attractive designs earn tolerance for **minor** problems, not major ones; the effect can **mask problems in usability testing**, so watch behavior, not comments. | [NN/g, Aesthetic-Usability Effect](https://www.nngroup.com/articles/aesthetic-usability-effect/) | B |

**Skeptical notes**
- Lindgaard is a *correlation between ratings*, not proof that 50 ms impressions determine behavior or purchases. Stimuli were 2000s homepages; participants were mostly students **(judgment)**.
- Tractinsky's ATM was a lab surrogate; the "beauty bias" is real in that study, but effect size in real products with real money at stake is not established by it.
- Fogg's credibility data are *comments*, from a self-selected online sample in 2002; they show what people say they notice. They do not prove design look changes outcomes.
- None of this says "pretty beats functional." It says: a poor look can cost you trust before function is ever evaluated, and a good look can hide problems from your own research.

## 2. Hierarchy and grouping (Gestalt)

| Principle | Practical rule | Source | Grade |
|---|---|---|---|
| Visual hierarchy | Guide the eye in order of importance using scale, value, color, spacing, placement. NN/g suggests 2-3 type sizes and a small/medium/large mix. | [NN/g, Visual Hierarchy](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/), [5 Principles of Visual Design](https://www.nngroup.com/articles/principles-visual-design/) | B/C |
| Proximity | Near = related. It "can overpower" color or shape similarity. Put less space between a heading and its content than between groups. | [NN/g, Proximity](https://www.nngroup.com/articles/gestalt-proximity/) | B/C |
| Common region | A border or background groups its contents and can override proximity. Overuse creates clutter; spacing is often enough. | [NN/g, Common Region](https://www.nngroup.com/articles/common-region/) | B/C |
| Gestalt list | Similarity, continuation, closure, proximity, common region, figure/ground, symmetry. | NN/g 5 Principles page | C |

Checklist: one dominant element per view; squint test (blur the screenshot and see if the primary action survives) **(judgment, common practice, not sourced)**; consistent spacing scale; group by proximity first, add borders only if needed.

Note: the Gestalt principles are well-established perceptual psychology, but the NN/g pages are interpretive summaries. I did not read primary Gestalt literature. Grade C for "how much each rule matters in UI."

## 3. Typography

Already covered with evidence in [06-input-reading-and-forms.md](06-input-reading-and-forms.md) (line length, font size, dyslexia) and [02](02-accessibility-engineering.md). Additions this session:

| Topic | Finding | Source |
|---|---|---|
| Seniors | NN/g recommends at least 12-point default fonts for sites targeting seniors, and always letting users enlarge text. Large link text helps readability and targeting. | [NN/g, Seniors](https://www.nngroup.com/articles/usability-seniors-improvements/) |
| Dark text size interaction | Positive-polarity advantage grew as font size shrank (Human Factors study as summarized by NN/g). | [NN/g, Dark mode](https://www.nngroup.com/articles/dark-mode/) |
| WCAG text spacing | 1.4.12 Text Spacing (AA) requires content to survive user overrides of line height, paragraph/letter/word spacing; 1.4.4 Resize Text (AA) and 1.4.10 Reflow (AA). | WCAG 2.2 list in [14](14-inclusive-design-ai-ux-and-wcag-check.md) |
| "Interesting fonts" for LLM output | Anthropic's own guidance says unguided models default to Inter/Roboto-style choices and recommends naming distinctive alternatives. This is about *LLM defaults*, not user outcomes. | [Anthropic blog](https://claude.com/blog/improving-frontend-design-through-skills) (C) |

**Not researched this session:** type scales and modular ratios, variable fonts performance, font-pairing rules, x-height/legibility lab studies. Treat any "golden ratio" claim as folklore: NN/g mentions the golden ratio was historically used in typesetting, but offers no experiment here.

## 4. Color

| Topic | What I verified | Source | Grade |
|---|---|---|---|
| Conformance contrast | WCAG 2.2 ratios: 4.5:1 normal text, 3:1 large text and UI components (as stated by secondary guide; the SC text itself is in WCAG 1.4.3 and 1.4.11). | [WCAG 2 Overview](https://www.w3.org/WAI/standards-guidelines/wcag/); [Lucky Graphics](https://lucky.graphics/learn/apca-vs-wcag-contrast-ratio-guide-2026/) | A / D |
| WCAG 3 contrast | WCAG 3 Working Draft (10 Sept 2026) says the contrast algorithm is **"yet to be determined"**; WCAG 3 "does not replace WCAG 2." | [W3C WCAG 3.0 WD](https://www.w3.org/TR/wcag-3.0/) | A |
| APCA | Separate, beta, promoted by its authors; pulled from the WCAG 3 draft as exploratory in 2023 (per Adrian Roselli, citing W3C comment). Its author says it is draft guidance and no one should drop WCAG 2 conformance. Use as a second opinion, report WCAG 2.2 for conformance. | [Roselli, Apr 2026](https://adrianroselli.com/2026/04/wcag3-contrast-as-of-april-2026.html); [GitHub issue 2099](https://github.com/w3c/wcag/issues/2099) | C |
| WCAG 2 mid-tone quirk | On saturated mid-tones WCAG 2's formula often favors black text even when white looks more readable to many; some dark-on-dark pairs rated too generously. | [Colourwise](https://colourwise.app/accessibility/apca-and-wcag-3-draft) | D (single vendor) |
| Don't rely on color alone | 1.4.1 Use of Color (A). 1 in 12 men have CVD (see README takeaway 2). | WCAG list; NEI (see 07) | A |
| Credibility | "Soothing green vs jarring purple" is a participant comment in Fogg, not a finding. | Fogg report | B (anecdote) |

**Not researched this session:** color theory (hue harmony, 60-30-10), palette generation, OKLCH perceptual uniformity in practice, cultural meaning of colors (see conflicts in [17](17-issues-and-open-problems.md)). The DTCG token spec supports Display P3 and Oklch ([10](10-design-systems-and-tokens.md)), which is the one verified fact here.

**Practical palette recipe (judgment):** neutral ramp (about 10 steps) + one brand hue ramp + semantic hues (success/warn/danger/info) + checked pairs. Test every text/background pair for 4.5:1 and every border/icon for 3:1; test both themes.

## 5. Dark mode

| Finding | Source | Grade |
|---|---|---|
| Positive polarity (dark text on light) gave better visual acuity and proofreading for both younger (18-33) and older (60-85) adults with normal or corrected vision. Older adults benefited less in acuity. | [Piepenbrock et al. 2013, Ergonomics](https://pubmed.ncbi.nlm.nih.gov/23654206/); [NN/g summary](https://www.nngroup.com/articles/dark-mode/) | B |
| Ambient light x polarity: no polarity effect in simulated daytime; at simulated night, light mode still won, especially for small text (as summarized by NN/g). | NN/g | B |
| Participants performed better in light mode but did **not report** perceiving a readability difference. | NN/g | B |
| Dark mode may help some low-vision users, e.g. with cloudy ocular media such as cataract. | NN/g | B |
| In an NN/g mobile survey (n = 115) the reasons for liking dark mode included battery savings, aesthetics, and accessibility perceptions. | [NN/g, Dark mode users](https://www.nngroup.com/articles/dark-mode-users-issues/) (search excerpt only) | C |

**Takeaway (judgment):** offer both, follow `prefers-color-scheme` by default, let users override, and test contrast in each theme. Do not claim dark mode "reduces eye strain": the sources I read do not show that. Dark mode is a preference and context feature, not a performance win for most normal-vision readers.

## 6. Iconography

| Rule | Source | Grade |
|---|---|---|
| Icons are ambiguous; **always add a visible text label**, never hover-only; labels matter most for navigation. | [NN/g, Icon Usability](https://www.nngroup.com/articles/icon-usability/) | B |
| If designing icons: simple, schematic; test recognition and memorability (retest after ~2 weeks). "5-second rule": if you cannot name an icon in 5 s, an icon probably will not work. | Same | C |
| Four quality criteria: findability, recognition, information scent, attractiveness. Test recognition out of context with no label. | [NN/g, Icon Testing](https://www.nngroup.com/articles/icon-testing/) | B |

## 7. Motion and microinteractions

| Topic | Verified fact | Source | Grade |
|---|---|---|---|
| Reduced motion | `prefers-reduced-motion: reduce` means *minimize* non-essential motion, not necessarily remove all animation. Users expect interaction-triggered motion to be disabled unless essential. | [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Media_queries/Using_for_accessibility) | C+ (reference) |
| Vestibular harm | Non-essential scroll/parallax animation can trigger dizziness, nausea, headaches; 2.3.3 Animation from Interactions is **AAA**. | [W3C Understanding 2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions) | A |
| Flashing | Nothing may flash more than 3 times per second (or must be below thresholds): 2.3.1 is **A** and applies to all content. | [W3C Understanding 2.3.1](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold) | A |
| Auto-moving content | 2.2.2 Pause, Stop, Hide (A) for auto-starting motion; carousels and loops need a real control (stylesheet alone cannot do it). | WCAG list; [css-animation.com](https://www.css-animation.com/accessible-motion-architecture/) (C, secondary) | A / C |
| Perceived performance | See [05](05-performance-and-perceived-speed.md). | | |

Rules of thumb **(judgment)**: motion should explain a change (where something went, what happened), stay short, never block input, and have a reduced-motion variant; avoid large-area movement.

**Not researched:** microinteraction research (e.g., Saffer), easing/duration lab studies. Do not cite specific millisecond values as evidence-based.

## 8. Imagery and content

Only verified: NN/g's lower-literacy research says such users miss page elements outside the main text flow (see [11](11-responsive-mobile-and-localization.md)); WCAG 1.1.1 requires text alternatives. Stock-photo effects, image trust, and hero-image eye-tracking were **not researched** here (see [04](04-eye-tracking-and-attention.md) for existing eye-tracking coverage).

## 9. Quick audit table

| Question | Pass looks like |
|---|---|
| What is the single primary action? | Visually dominant, only one per view |
| Are groups obvious without labels? | Proximity/common region make sections evident |
| Does it survive greyscale? | State and hierarchy do not rely on hue alone |
| Do both themes pass contrast? | 4.5:1 text / 3:1 UI in each |
| Are icons labeled? | Visible text beside every non-universal icon |
| Is motion optional? | Reduced-motion variant; no flashing; pause control for auto-motion |
