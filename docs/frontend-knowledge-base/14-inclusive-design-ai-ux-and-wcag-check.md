# 14. Inclusive Design Beyond WCAG, AI-Feature UX, and a Verified WCAG 2.2 Check

Researched 2026-11-11. Grades: A standard, A- free peer-reviewed, B NN/g/peer-reviewed/survey, C practitioner. **(judgment)** = inference; **(not researched)** = unverified.

## 1. WCAG 2.2: verified facts and criteria count

| Fact | Source | Grade |
|---|---|---|
| WCAG 2.2 became a W3C Recommendation on **5 Oct 2023**; an update was published 12 Dec 2024. 13 guidelines under 4 principles. | [WCAG 2 Overview](https://www.w3.org/WAI/standards-guidelines/wcag/) | A |
| WCAG 2.2 adds **9** success criteria to 2.1; 2.1 added 17 SC and 1 guideline to 2.0; **4.1.1 Parsing is obsolete and removed** in 2.2. Criteria are unchanged across versions; content meeting 2.2 also meets 2.1 and 2.0. | WCAG Overview | A |
| WCAG 2.2 is **ISO/IEC 40500:2025** (identical to the Oct 2023 version). The **2026 version of EN 301 549 uses WCAG 2.2** (relevant to the European Accessibility Act). | WCAG Overview | A |
| WCAG 3.0 is a **Working Draft** on the Recommendation track; "does not replace WCAG 2"; "still several years of work." | [WCAG 3 WD](https://www.w3.org/TR/wcag-3.0/) | A |

**Count (derived by me from W3C's quickref data, [wai-wcag-quickref](https://github.com/w3c/wai-wcag-quickref) `wcag22.json`):** the file lists 87 entries including 4.1.1; excluding the obsolete 4.1.1 gives **86 current success criteria: 31 level A, 24 level AA, 31 level AAA**. A+AA = **55**. (Deque's "50 criteria" figure in 10 refers to WCAG 2.1 A/AA.)

| Guideline | A | AA | AAA |
|---|---|---|---|
| 1.1 Text Alternatives | 1 | 0 | 0 |
| 1.2 Time-based Media | 3 | 2 | 4 |
| 1.3 Adaptable | 3 | 2 | 1 |
| 1.4 Distinguishable | 2 | 7 | 4 |
| 2.1 Keyboard Accessible | 3 | 0 | 1 |
| 2.2 Enough Time | 2 | 0 | 4 |
| 2.3 Seizures and Physical Reactions | 1 | 0 | 2 |
| 2.4 Navigable | 4 | 4 | 5 |
| 2.5 Input Modalities | 4 | 2 | 2 |
| 3.1 Readable | 1 | 1 | 4 |
| 3.2 Predictable | 3 | 2 | 1 |
| 3.3 Input Assistance | 3 | 3 | 3 |
| 4.1 Compatible | 1 | 1 | 0 |
| **Total** | **31** | **24** | **31** |

### The nine WCAG 2.2 additions (verified against W3C "What's New")

| SC | Level | Plain meaning |
|---|---|---|
| 2.4.11 Focus Not Obscured (Minimum) | **AA** | Focused item not *entirely* hidden by author content (e.g., sticky footer) |
| 2.4.12 Focus Not Obscured (Enhanced) | AAA | No part hidden |
| 2.4.13 Focus Appearance | AAA | Indicator at least a 2 CSS px perimeter, 3:1 contrast change |
| 2.5.7 Dragging Movements | **AA** | Single-pointer alternative to dragging |
| 2.5.8 Target Size (Minimum) | **AA** | 24x24 CSS px, or spacing/equivalent/inline/UA/essential exceptions |
| 3.2.6 Consistent Help | **A** | Help mechanisms in same relative order across pages |
| 3.3.7 Redundant Entry | **A** | Don't re-ask for info in the same process (exceptions) |
| 3.3.8 Accessible Authentication (Minimum) | **AA** | No cognitive function test unless alternative, mechanism, object recognition, or personal content |
| 3.3.9 Accessible Authentication (Enhanced) | AAA | Also no object recognition/personal content tests |

Source: [W3C, What's New in WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/) (A). **Check against existing docs:** 01, 02, 06, 08 are consistent with this list (focus-not-obscured and target size as AA; consistent help and redundant entry as A). Note 2.4.13 Focus Appearance is **AAA**, not AA; if you read it elsewhere as AA, that is a mix-up with the earlier draft **(judgment: drafts changed; I did not read the drafts)**.

Related AA criteria people forget: 1.4.10 Reflow, 1.4.11 Non-text Contrast, 1.4.12 Text Spacing, 1.4.13 Content on Hover or Focus, 1.3.4 Orientation, 1.3.5 Identify Input Purpose, 4.1.3 Status Messages. **2.3.3 Animation from Interactions is AAA**; **2.3.1 Three Flashes is A**; **2.5.5 Target Size (Enhanced) is AAA**.

## 2. Assistive technology reality check

**WebAIM Screen Reader User Survey #10** (Dec 2023-Jan 2024, 1,539 valid responses; uncontrolled sample, may not represent all users) ([results](https://webaim.org/projects/screenreadersurvey10/), grade B-):

| Metric | Result |
|---|---|
| Primary desktop screen reader | JAWS 40.5%, NVDA 37.7%, VoiceOver 9.7%, other ~12% |
| Commonly used (any) | NVDA 65.6%, JAWS 60.5%, VoiceOver 43.9%, Narrator 37.3% |
| Use more than one screen reader | 71.6% (43% use three or more) |
| Top combos | JAWS+Chrome 24.7%, NVDA+Chrome 21.3%, JAWS+Edge 11.4%, NVDA+Firefox 10.0%, VoiceOver+Safari 7.0% |
| Regional split | JAWS > NVDA in North America (55.5% vs 24.0%); NVDA dominant in Europe, Africa/Middle East, Asia |
| Mobile | 91.3% use a screen reader on mobile; VoiceOver 70.6% |
| Navigation | Headings are the most common way to explore long pages (71.6%); landmark use up to 31.8% |
| Barriers | CAPTCHA "by far the most problematic"; only 34.6% said accessibility improved in the last year |
| JavaScript | 99.8% had it enabled (so "users have JS off" is not a screen-reader reason to avoid JS) |

Implications **(judgment):** test with at least NVDA+Firefox/Chrome and VoiceOver+Safari (desktop and iOS), use real heading structure, and never gate login on CAPTCHA-only flows.

Automated tools: Deque 57% by issue volume vs 16 of 50 criteria; Springer study "one sixth" of WCAG criteria covered ([10](10-design-systems-and-tokens.md)). Source on testing practice: [Storybook a11y docs](https://storybook.js.org/docs/writing-tests/accessibility-testing).

## 3. Beyond WCAG: audiences and what the sources say

| Audience | Verified guidance | Source | Grade |
|---|---|---|---|
| **Cognitive / neurodiverse** | W3C COGA coverage in [03](03-cognitive-load-and-frustration.md). WCAG 2.2 additions 3.2.6, 3.3.7, 3.3.8 target cognitive load. MDN notes blinking/flashing can be problematic for people with ADHD and some motion triggers vestibular disorders, epilepsy, migraine. | [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Media_queries/Using_for_accessibility); [W3C What's New](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/) | A / C |
| **Older adults** | 65+ were 43% slower; success 55.3% vs 74.5%. Larger text/links, avoid moving menus and sliders, static widgets, tolerate imprecise pointing. Dropdowns and sliders hard on touch. | [NN/g](https://www.nngroup.com/articles/usability-seniors-improvements/), [NN/g report summary](https://www.nngroup.com/reports/senior-citizens-on-the-web/) | B (123 seniors across 3 rounds over 19 years) |
| **Low literacy** | Word-by-word reading, narrow field of view; 6th-8th grade text, single column, linear nav. | [NN/g](https://www.nngroup.com/articles/writing-for-lower-literacy-users/) | B |
| **Low bandwidth / old devices** | web.dev starter budget: under 5 s TTI, under 170 KB critical resources on baseline mobile + 3G. | [web.dev](https://web.dev/articles/performance-budgets-101) | C |
| **Situational disability** | "All people are temporarily disabled": noise, glare, rain, distraction, carrying items; multi-encode feedback (visual + other cues); phones are not flat and attention is split. | [Hoober, ACM Interactions](https://interactions.acm.org/archive/view/may-june-2015/fingers-thumbs-and-people) | C |
| **Voice / switch / speech recognition** | W3C persona (reporter with RSI using speech recognition) illustrates obscured focus; 2.5.3 Label in Name (A) requires visible label text to be in the accessible name (needed so "click Submit" works). Switch access depth: not researched. | W3C What's New; WCAG list | A |
| **Aging eyes / dark mode** | Positive polarity still advantaged for older adults, though smaller benefit in acuity; cataract is an exception where dark mode may help. | [09](09-visual-design-fundamentals.md) | B |
| **Cultural differences** | Reading direction (RTL), text expansion, touch-side behavior flips for RTL (Hoober). Cultural color meaning, imagery, trust cues: **not researched**; Reinecke et al. found age and education affected first-impression ratings. | [11](11-responsive-mobile-and-localization.md) | |
| **Ethical design** | Dark patterns are prevalent (11.1% of ~11K shopping sites in a crawl); consent design strongly steers choices; regulators treat asymmetrical reject/accept as invalid consent. | [12](12-frontend-engineering-issues.md) | A-/B |

**Judgment-level principle:** accessibility conformance is a floor. WCAG doesn't guarantee comprehension; real users with disabilities find barriers audits miss. Budget for testing with them (digital.gov publishes sample personas for people with disabilities, per its Usability page).

## 4. AI-feature UX (chat, streaming, trust, error recovery)

| Source | What it gives you | Grade |
|---|---|---|
| [Amershi et al., Guidelines for Human-AI Interaction, CHI 2019](https://dl.acm.org/doi/fullHtml/10.1145/3290605.3300233) | **18 guidelines** distilled from 150+ recommendations over 20 years; validated in a study with 49 practitioners across 20 AI products; organized by phase: initially, during interaction, when wrong, over time. | B (peer-reviewed, Honorable Mention) |
| [Google PAIR People + AI Guidebook](https://pair.withgoogle.com/guidebook) | Patterns for onboarding to AI features, explaining the system, calibrating trust, control vs automation, and **supporting users when something goes wrong**. A comparative analysis says the guidebook has **113** guidelines and lacks the open validation study of Microsoft's set. | C+ ([comparative analysis arXiv:2010.11761](https://arxiv.org/pdf/2010.11761), A-) |
| [NN/g, Prompt Structure](https://www.nngroup.com/articles/ai-prompt-structure/) | Diary study: 18 participants, 425 conversations (ChatGPT 4.0, Bard, Bing Chat, May-June 2023). Prompts contain request, framing context, format, references. Vague prompts create long "funneling" conversations. Users lack vocabulary (e.g., describing a visual style), effort, or privacy comfort to frame fully. | B (small, 2023 tools) |
| [NN/g, Articulation barrier](https://www.nngroup.com/articles/ai-articulation-barrier/), [Prompt controls](https://www.nngroup.com/articles/prompt-controls-genai/) | Hybrid interfaces: use GUI controls (recognition over recall) alongside free text to reduce typing and articulation effort. | B |
| [NN/g, 10 guidelines for AI chatbots](https://www.nngroup.com/articles/ai-chatbots-design-guidelines/) | Suggested prompts as **buttons**; **do not autoscroll** to the end of a long (especially streaming) response, because users who started reading lose their place. | B |

**Design checklist for AI features (judgment, built from the sources above):**
- [ ] State capabilities and limits up front; show examples of good requests
- [ ] Suggested prompts and clarifying questions as clickable controls
- [ ] Streaming: keep reading position stable; offer stop; preserve partial output on failure
- [ ] Make it easy to undo, edit, regenerate, give feedback; keep user in control
- [ ] Show sources/uncertainty where wrong answers matter; avoid false precision
- [ ] Failure states: say what failed, what was saved, what to do next (same bar as any error)
- [ ] Accessibility: announce status changes (WCAG 4.1.3 AA) in a way that doesn't spam screen readers; keyboard access to every control; consistent help location (3.2.6). **Specific `aria-live` streaming patterns: not researched**; test with NVDA and VoiceOver.
- [ ] Privacy: say what is sent to models and retained

## 5. Accessibility of AI-*generated* UI code (what research shows)

| Study | Finding | Grade |
|---|---|---|
| [Does ChatGPT Generate Accessible Code? (W4A 2024)](https://dl.acm.org/doi/full/10.1145/3677846.3677854) | 88 developers prompted ChatGPT (GPT-3.5) to build sites; **84%** had accessibility problems (checked with AChecker and WAVE, two automated tools). When prompted to fix, ChatGPT fixed **70%** of violations in its own code and **73%** in 88 open-source GitHub projects. | B (automated-only checking; older model) |
| [From Code to Compliance (arXiv 2501.03572)](https://arxiv.org/abs/2501.03572) | GPT-4o: default code often lacks WCAG compliance; fixes simple issues when prompted but struggles with complex ones, needing human oversight; **giving screenshots alongside prompts helped** (e.g., choosing contrast colors). Case study. | A- (single case study) |
| [CodeA11y (arXiv 2502.10884)](https://arxiv.org/html/2502.10884) | Formative study with 16 developers without a11y training: failure to **prompt AI for accessibility**, omitting manual steps like replacing placeholders, and inability to verify compliance. | A- |
| [Metric-driven comparison, ChatGPT vs Copilot (2024)](https://dl.acm.org/doi/full/10.1145/3696593.3696614) | Similar accessibility results across both; stresses well-crafted prompts. | B |
| [Human or LLM? (arXiv 2503.15885)](https://arxiv.org/html/2503.15885) | Compared GPT-4o and Qwen2.5-Coder with human-written code; I saw only a partial snippet. | unverified details |

**Takeaway (judgment):** models are better than not-asking, worse than a reviewed result. State the accessibility bar in the prompt, use accessible primitives (Radix/React Aria), run automated checks, then do keyboard and screen-reader checks yourself. See [15](15-llm-prompting-for-frontend.md).
