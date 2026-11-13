# Frontend Master Guide: Building Accessible, Usable, Distinctive Interfaces, With and Without LLMs

**Last refreshed:** 2026-11-13 (runtime refresh of the legal, standards, performance, leaderboard and tool facts; see [Appendix F](#appendix-f-runtime-refresh-and-corrections-log)).
**Status:** a consolidation of two research sets, [`docs/frontend-design/`](frontend-design/README.md) (files 01-04) and [`docs/frontend-knowledge-base/`](frontend-knowledge-base/README.md) (files 01-17). Those files stay in place as the **deep dives**; every chapter below links to them.
**Not legal advice.** Legal and standards facts change. Re-check dates before using them in a contract, policy, or filing.

**How to read evidence labels.** Claims carry a grade from A to D, and anything I infer is marked **(judgment)**. Grades are defined in [section 4](#4-how-to-read-the-evidence-labels). Facts marked **[refreshed 2026-11-13]** were re-checked against a live source for this guide.

---

## Table of contents

**Part A: Start here**
1. [Executive summary](#1-executive-summary)
2. [Top takeaways](#2-top-takeaways)
3. [Recommended reading order](#3-recommended-reading-order)
4. [How to read the evidence labels](#4-how-to-read-the-evidence-labels)

**Part B: Topic chapters**
5. [Why LLM interfaces converge, and how close vibe-coded work can get](#5-why-llm-interfaces-converge-and-how-close-vibe-coded-work-can-get)
6. [UI, UX and frontend fundamentals](#6-ui-ux-and-frontend-fundamentals)
7. [Accessibility law: US and EU](#7-accessibility-law-us-and-eu)
8. [Accessibility engineering](#8-accessibility-engineering)
9. [Cognitive load and frustration](#9-cognitive-load-and-frustration)
10. [Eye tracking and attention](#10-eye-tracking-and-attention)
11. [Performance and perceived speed](#11-performance-and-perceived-speed)
12. [Input, reading and forms](#12-input-reading-and-forms)
13. [Visual design](#13-visual-design)
14. [Design systems and tokens](#14-design-systems-and-tokens)
15. [Responsive, mobile, localization and content](#15-responsive-mobile-localization-and-content)
16. [Frontend engineering issues](#16-frontend-engineering-issues)
17. [UX research methods and measurement](#17-ux-research-methods-and-measurement)
18. [Inclusive design and AI-feature UX](#18-inclusive-design-and-ai-feature-ux)
19. [Prompting LLMs for frontend work](#19-prompting-llms-for-frontend-work)
20. [Tools, plugins and models](#20-tools-plugins-and-models)
21. [Audit checklist and audit prompt](#21-audit-checklist-and-audit-prompt)

**Part C: Skeptical review**
22. [Skeptical notes](#22-skeptical-notes)
23. [Risk map: how a team following this guide can still fail](#23-risk-map-how-a-team-following-this-guide-can-still-fail)
24. [Evidence gaps and open problems](#24-evidence-gaps-and-open-problems)

**Part D: Appendices**
- [Appendix A: Copy-paste prompts](#appendix-a-copy-paste-prompts)
- [Appendix B: Checklists](#appendix-b-checklists)
- [Appendix C: Source log](#appendix-c-source-log)
- [Appendix D: Glossary and common misconceptions](#appendix-d-glossary-and-common-misconceptions)
- [Appendix E: Learning path](#appendix-e-learning-path)
- [Appendix F: Runtime refresh and corrections log](#appendix-f-runtime-refresh-and-corrections-log)
- [Appendix G: Deep-dive file map](#appendix-g-deep-dive-file-map)

---

# Part A: Start here

## 1. Executive summary

**The problem.** If you ask an AI model for "a modern SaaS landing page," you get the average of the public web. The model predicts the most likely next piece of code, and the most likely page is one everybody has seen. Anthropic calls this *distributional convergence* (the model drifting to the statistical center of its training data). Banning one default does not fix it: the model slides to the next most common default. Anthropic's own post says it moved from one font to another common one, and the official `frontend-design` skill was itself updated in 2026 to list the *new* clichés (cream background with a serif headline and a terracotta accent is now on its list of "tells") [refreshed 2026-11-13].

**The fix is process, not a better adjective.** Write the decisions down before any screen exists: who the users are, the one task that matters, a small token file (named colors, type sizes, spacing, radius, motion), two or three concrete references, and real content. Then build one screen, look at screenshots at three widths, test with the keyboard, run automated checks, and fix. Models are better at following a tight spec and fixing measured defects than at having taste.

**How good can it get?** My estimate (judgment, not measured) is that a well-directed, human-supervised vibe-coded build can reach roughly 70-85% of top-tier human craft on marketing pages and simple apps, and roughly 50-65% on complex product UI. The missing part is original concept, brand voice, motion choreography, and obsessive detail. Most of the gain from "default AI" to "best directed" comes from process rather than model choice.

**What you must not skip.**
- **Accessibility is a legal baseline in many places, not a nice-to-have.** Build to WCAG 2.2 AA (the international web accessibility standard, Level AA). It satisfies every rule currently in force in the US (Section 508 uses WCAG 2.0 AA; ADA Title II and HHS Section 504 use WCAG 2.1 AA) and the EU direction. Government deadlines were pushed back one year in 2026 but not cancelled ([chapter 7](#7-accessibility-law-us-and-eu)).
- **The web mostly fails.** In WebAIM's February 2026 scan, 95.9% of the top million home pages had automatically detectable WCAG failures, and the number got worse versus 2025 [refreshed].
- **Automated tools find only part of the problems.** Treat a clean axe or Lighthouse report as the floor.
- **People have limits.** Working memory holds about four things; people scan rather than read; delays of 0.1 s, 1 s and 10 s change how things feel. Design for those limits and you also reduce legal and frustration risk.
- **LLM code needs guardrails.** Accessibility, security, invented packages, and invented content are recurring failures. The best-supported mitigations are feedback from real tools (screenshots, axe, tests) and grounding in standard accessible patterns, not clever role-play wording.

## 2. Top takeaways

Each line is the strongest-evidence version, deduplicated across the source files. Chapter numbers show where to read more.

### Why AI interfaces look alike, and the fix
1. **Sameness is structural.** Next-token prediction favors the web's center ([ch. 5](#5-why-llm-interfaces-converge-and-how-close-vibe-coded-work-can-get)).
2. **Constraints beat adjectives.** "Four type sizes, one accent, 6px radius, no gradients" removes most of the generic page; "clean and modern" does not.
3. **Pair every ban with a replacement.** Banned defaults get swapped for the next default. Google's Gemini 3 guidance makes a related point: broad negative instructions ("do not guess") can make a model over-correct; tell it what to use instead (ch. 19).
4. **Fonts are not the villain.** Linear ships Inter. The pros win with a *system* (scale, spacing, consistency), not a magic typeface.
5. **Evidence for the AI "taste gap" is real but dated and small.** Direction is consistent: usable and functional, weak on originality, accessibility, and fixing aesthetics (ch. 5).

### The law
6. **US dates [refreshed]:** ADA Title II (state and local government) requires WCAG 2.1 AA by **April 26, 2027** (population 50,000+) or **April 26, 2028** (smaller and special districts). HHS Section 504 (recipients of HHS money) requires WCAG 2.1 AA by **May 11, 2027** (15+ employees) or **May 10, 2028**. Section 508 (federal) still uses **WCAG 2.0 AA**. Private businesses (ADA Title III) have no web rule, but lawsuits are frequent: one vendor counted 5,114 digital-accessibility suits in 2025.
7. **DOJ said it may reopen the substance of the Title II rule.** If it does not, it "fully anticipates" enforcing the new dates. No proposed rule had appeared as of the latest source I found (early Oct 2026, secondary). Plan for the dates; watch for changes.
8. **Accessibility overlays are not compliance.** The FTC's 2025 order against accessiBe bars claims that an automated product can make any site WCAG-compliant.
9. **EU:** the European Accessibility Act has applied since 28 June 2025. EN 301 549 v4.1.1 (based on WCAG 2.2 AA) was published September 2026 but is not yet the legal reference; v3.2.1 (WCAG 2.1 AA) is, until the Commission cites the new one.
10. **WCAG 3.0 is a Working Draft** (10 Sept 2026), not usable for compliance, and its contrast method is "yet to be determined."

### Accessibility engineering
11. **Use native HTML first**, and headless accessible components (Radix, React Aria) for dialogs, menus, and comboboxes.
12. **The same six failures dominate** for seven years running: low-contrast text (83.9% of pages), missing alt text (53.1%), missing form labels (51%), empty links (46.3%), empty buttons (30.6%), missing language (13.5%) [refreshed].
13. **More ARIA correlates with more errors** (59.1 vs 42 average errors on pages with and without ARIA; correlation, not proof). Wrong ARIA is worse than none.
14. **Automation coverage is partial:** about 57% of issues by volume (Deque), but problems found for only 16 of 50 WCAG 2.1 A/AA criteria. Always add keyboard and screen-reader passes.
15. **Screen reader reality [refreshed]:** in WebAIM's 2026 survey (n=1,780; not a random sample), JAWS 55.0% and NVDA 32.9% primary on desktop; 91.8% also use a screen reader on mobile; headings are the first navigation method for 67.8%; 85.6% say PDFs are likely to cause significant problems.

### Human factors
16. **Working memory is about 4 chunks**, not 7 (Cowan). Do not make people remember things across screens.
17. **People scan.** In NN/g eye tracking, 57% of viewing time was above the fold and 74% in the first two screens (desktop, 2018). The F-pattern is a symptom of unstructured text, not a goal.
18. **A blink is enough for a first impression** (120 ms to guess the page type; appeal ratings at 50 ms match those at 500 ms). Looks also shape trust, and can *mask* usability problems in your own research.
19. **Speed:** 0.1 s feels instant, 1 s keeps flow, 10 s loses attention. Core Web Vitals "good" is LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at the 75th percentile; unchanged in 2026 [refreshed].
20. **Never show a blank screen while waiting.** Skeletons and progress feedback help in different situations; evidence is small and mixed.
21. **Forms are where frustration lives.** Validate after the user finishes a field, not while typing; keep their input; one column; top labels; real labels (ch. 12).
22. **Touch targets:** WCAG minimum 24x24 CSS px; aim for 44 px on touch; research suggests ~9-10 mm for most adults, ~14 mm for older adults, ~18 mm for people with motor impairments.

### Working with LLMs
23. **Proven or well-supported:** explicit specs with real content, examples, tokens as the only source of style, small scoped tasks, tool feedback (screenshots, axe, tests), and your own evals.
24. **Not supported:** "you are a world-class designer" persona lines as an accuracy boost; trusting self-review with no new information; assuming generated code is secure, accessible, or uses real packages.
25. **Accessibility of generated code is mixed, not hopeless [refreshed]:** 2026 studies find models do basic things (contrast, alt text) well but struggle with ARIA and interactive widgets, and that feedback from axe plus grounding in standard patterns lifts results sharply (ch. 8, 19).
26. **AI productivity claims are unsettled.** METR's 2025 trial found experienced developers 19% slower; its late-2025 follow-up pointed the other way, but METR itself calls that data unreliable. Measure your own team (ch. 19).

## 3. Recommended reading order

Pick the row that matches you. "Min" is reading time, roughly.

| You are... | Read in this order | Min |
|---|---|---|
| **In a hurry** | Sections 1-2, then [21 (audit)](#21-audit-checklist-and-audit-prompt), then [Appendix A.1-A.3](#appendix-a-copy-paste-prompts) | 25 |
| **A non-designer building with an LLM** | 1-2 → [5](#5-why-llm-interfaces-converge-and-how-close-vibe-coded-work-can-get) → [6](#6-ui-ux-and-frontend-fundamentals) → [13](#13-visual-design) → [19](#19-prompting-llms-for-frontend-work) → Appendix A → [20](#20-tools-plugins-and-models) | 90 |
| **A developer who must ship accessibly** | 1-2 → [7](#7-accessibility-law-us-and-eu) → [8](#8-accessibility-engineering) → [14](#14-design-systems-and-tokens) → [16](#16-frontend-engineering-issues) → [21](#21-audit-checklist-and-audit-prompt) | 100 |
| **A designer or researcher** | 1-2 → [9](#9-cognitive-load-and-frustration) → [10](#10-eye-tracking-and-attention) → [12](#12-input-reading-and-forms) → [13](#13-visual-design) → [17](#17-ux-research-methods-and-measurement) → [18](#18-inclusive-design-and-ai-feature-ux) | 100 |
| **A manager or compliance owner** | 1-2 → [7](#7-accessibility-law-us-and-eu) → [23 (risk map)](#23-risk-map-how-a-team-following-this-guide-can-still-fail) → [24](#24-evidence-gaps-and-open-problems) | 40 |
| **A skeptic** | [22](#22-skeptical-notes) → [Appendix C](#appendix-c-source-log) → [Appendix F](#appendix-f-runtime-refresh-and-corrections-log) → [24](#24-evidence-gaps-and-open-problems) | 40 |
| **A beginner wanting a course** | [Appendix E](#appendix-e-learning-path), using chapters as the readings | self-paced |

## 4. How to read the evidence labels

| Grade | Meaning | Examples in this guide |
|---|---|---|
| **A** | Law, regulation, standard text, or official primary data | Federal Register, eCFR, W3C specs, FTC orders, GitHub repository metadata |
| **A-** | Peer-reviewed or preprint, full text read, replicable design | PubMed Central papers, arXiv studies read in full or abstract |
| **B** | NN/g primary studies, large surveys with disclosed limits, peer-reviewed but paywalled or small | NN/g eye tracking, WebAIM surveys, Utz 2019 |
| **C** | Practitioner articles, vendor documentation about their own product, secondary summaries | Vendor prompting docs, law-firm client alerts, MDN/web.dev reference pages |
| **D** | Aggregators, SEO blogs, single-vendor claims | Plugin comparison sites, color-tool marketing |

Rules used throughout (from the research protocol this guide follows):
- **No folklore.** If I did not read it, it is not cited as fact. Where a number comes from a search-result excerpt rather than a fetched page, the source log says so.
- **Independent agreement beats single sources.** Where several unrelated sources converge, I say so.
- **Vendor claims are graded down** unless a primary document supports them.
- **(judgment)** means my inference from the evidence. **Untested** means a prompt or procedure I did not run against a model.

---

# Part B: Topic chapters

## 5. Why LLM interfaces converge, and how close vibe-coded work can get

*Deep dives: [frontend-design/01-research-report.md](frontend-design/01-research-report.md), [frontend-design/02-education-guide.md](frontend-design/02-education-guide.md) (Part 6), [frontend-knowledge-base/15](frontend-knowledge-base/15-llm-prompting-for-frontend.md).*

**Vibe coding** means describing what you want in plain language and letting an AI write the code, often without reading it closely. It is fast, and the default results are generic.

### 5.1 Why the output is sloppy and identical

| # | Cause | Plain explanation | Evidence |
|---|---|---|---|
| 1 | Distributional convergence | The model prefers the most probable (most common) design | Anthropic's frontend skills write-up (A for the mechanism it names; its before/after images are its own) |
| 2 | Library default echo | Tailwind and shadcn/ui defaults (zinc grays, one radius, thin borders, indigo) are the most common code, so agents reuse and multiply them | Practitioner posts (C; the Tailwind-origin story is speculative) |
| 3 | Underspecified prompts | "Modern SaaS page" has no constraints, so the model has no reason to leave the average | Practitioner posts (C), NN/g on vague prompts (B) |
| 4 | Easy-path agents | Agents build what is easy to implement and verify | Practitioner (C) |
| 5 | No memory between generations | Button on screen 1 is not button on screen 4 | Practitioner (D, vendor); plausible given how models work |
| 6 | Judgment-action gap | Models can partly *score* aesthetics but struggle to *diagnose and repair* them. In AUV-Bench the best exact diagnosis was 24.7%; text-to-UI aesthetic scores were 2.78-3.18 of 5 | AUV-Bench, arXiv 2609.34854 [verified 2026-11-13: both numbers appear in the paper] (A-, preprint) |
| 7 | Pragmatic fine, hedonic flat | 92 student raters scored AI prototypes fine on usability and efficiency, neutral-to-negative on originality and innovation | "Usable but Conventional," arXiv 2605.15124 [verified 2026-11-13: abstract and sample] (A-, small, static prototypes, students) |
| 8 | Weak accessibility and interactivity | Older studies found structure good, accessibility and working interactions weak. 2026 studies are more mixed (see [8.5](#85-accessibility-of-ai-generated-code)) | arXiv 2601.22759 (B-) and 2026 studies |
| 9 | The prompter lacks vocabulary | If you cannot name hierarchy, rhythm, tokens, or states, you cannot steer or critique | Synthesis **(judgment)**, consistent with NN/g's "articulation barrier" |
| 10 | Generic copy | Headlines like "Build faster" make a page feel templated even with good visuals | Practitioner (C) |

### 5.2 The AI fingerprint (what reviewers notice)

**Classic tells (2023-2025):** Inter/Roboto everywhere; indigo-to-purple gradient; centered hero with one CTA and a logo strip; three equal rounded cards with icons in tinted squares; blurred blobs; same radius and shadow on everything; nested cards; ALL-CAPS label above every heading; uniform spacing; no empty/loading/error states; emoji as icons; copy that could sell anything.

**2026 tells [refreshed]:** Anthropic's own `frontend-design` skill (last changed 2026-09-03 in the public repository) now lists five clusters of generated-page defaults: (1) warm cream background with a high-contrast serif and a terracotta accent; (2) near-black with one acid-green or vermilion accent; (3) broadsheet layout with hairline rules and zero radius; (4) the "SaaS card kit" (identical rounded cards, one radius, same soft shadow, gradient washes); (5) template chrome (tracked-out ALL-CAPS eyebrow above every heading, middle-dot meta strings, "WORD - fragment" labels, tinted near-black, mono small labels, arrows appended to links). It adds that these are "legitimate for some briefs, but they are defaults rather than choices." Impeccable's README describes the "tasteful default" the same way: cream page, thin serif, italic accent, pill buttons (grade A for what the documents say; that models produce these is vendor-reported, C).

**What this shows (judgment):** the fingerprint *moves*. Every published ban list becomes a new default list. Only your own brief, tokens, and references produce a stable distinct result.

### 5.3 The quality ladder: what top human work actually does

| Tier | Who | What distinguishes it |
|---|---|---|
| A | Best human (Stripe, Linear, Vercel, Apple, Awwwards-grade studios) | Restraint (few colors, no decoration); one type family with a rigorous scale; monochrome base plus one accent; *interaction* density rather than visual density (hover, focus, keyboard, loading, transition states everywhere); product-as-page (Linear's homepage is a working fake issue); designed motion curves; opinionated product; a flexible system with a distinct voice |
| B | Strong human, normal budget | Refactoring UI tactics: fewer borders, hierarchy through size/weight/color, a spacing scale, readable line lengths. Solid, rarely memorable |
| C | Best AI-assisted with a human steering | Public examples exist (Anthropic's "Rick Rubin: The Way of Code" site, an Awwwards Honorable Mention; creator-reported 1618room.com). **Caveat:** winners nearly always had an experienced designer choosing concept and taste |
| D | AI + a good skill, no human | Better single screens; recognizable genre; inconsistent across screens |
| E | Default one-shot | The fingerprint above; functional, often responsive, rarely accessible |
| F | Worst AI output | Broken layouts, dead buttons, no validation, invisible focus, low contrast. WebGen-Bench (Claude-3.5-era) found only 27.8-38.2% functional accuracy; now dated |

Sources for tier A are practitioner write-ups (C) and secondhand quotes; treat them as hypotheses to check by inspecting the live sites in devtools.

### 5.4 Benchmarks, and what they actually measure

| Benchmark | Measures | Reading | Caveat |
|---|---|---|---|
| WebDev Arena (arena.ai) | Human votes on which generated web app they prefer | Snapshot below | Votes reward what looks impressive in seconds; prompts are short; rank ties |
| Design2Code (Stanford) | Screenshot to code fidelity, 484 real pages | Models lag on visual-element recall and layout | Copying a design, not creating one; 2024 models |
| AUV-Bench | Aesthetic judgment, diagnosis, repair, generation vs designers | Judgment does not reliably connect to repair | Preprint, Alibaba/HKUST authors |
| ArtifactsBench, FrontendBench, WebGen-Bench | Functional and visual checks, often by a model judge | Functionality, not taste | Older models; model judges |
| UEQ-S study (N=92) | Perceived UX, AI vs human | Pragmatic fine, hedonic weak | Students, static prototypes |

**WebDev Arena snapshot, 2026-11-11 [refreshed]:** Claude Fable 5.2 (xHigh) 1838±21; Claude Opus 5.5 (Max) 1815±12; Claude Sonnet 5.5 (xHigh) 1772±10; Gemini 4 Carbon (High) 1768±15 (preliminary); GPT-6 Astra (Max) 1764±9. The leaderboard lists rank *spreads*: ranks 3-5 overlap (spread 3-5 and 3-6), so they are statistically close. Best openly licensed models listed: Kimi K3.1 Pro 1687, DeepSeek-V4.1-Flash (Oct 2026 build) 1664, Kimi K3 1658, Inkling 2 Small (Apache 2.0, preliminary) 1647, MiMo-V2.6-Flash 1638, GLM-5.3 1622. These move weekly. **Do not infer UX quality from Elo.**

### 5.5 How close can the best vibe-coded app get? (judgment, with a rubric you can run)

My 1-5 estimates (not measured). I rechecked the arithmetic during this consolidation and corrected the averages in the source file (see [Appendix F](#appendix-f-runtime-refresh-and-corrections-log)).

| Dimension | Default AI | AI + good skill, no human | Best directed vibe-coded | Top human |
|---|---|---|---|---|
| Typography system | 2 | 3.5 | 4 | 5 |
| Color and contrast | 2.5 | 3.5 | 4 | 5 |
| Spacing and layout rhythm | 3 | 3.5 | 4 | 5 |
| Visual hierarchy | 3 | 3.5 | 4 | 5 |
| Originality and concept | 1.5 | 3 | 3.5 | 5 |
| Motion and interaction polish | 2 | 3 | 3.5 | 5 |
| States (empty, loading, error, disabled) | 2 | 2.5 | 4 | 5 |
| Accessibility (WCAG 2.2 AA) | 2 | 2.5 | 4 | 4.5 |
| UX flow and information architecture | 3 | 3 | 4 | 5 |
| Consistency across screens | 2.5 | 2.5 | 4 | 5 |
| Content and microcopy | 2 | 2.5 | 3.5 | 5 |
| **Average (corrected)** | **2.3** | **3.0** | **3.9** | **4.95** |

Reading it: default AI is about 47% of top human; AI with a good skill about 61%; best directed about 78%. Moving from default to best-directed closes about 59% of the gap. The percentages are estimates; **use the rubric on your own screens.** Compare your app and a tier-A reference at 1440 px and 390 px with the same content, and score both.

**What closes the gap, ranked by estimated impact (judgment):** (1) tokens and a written system before any screen; (2) real references instead of adjectives; (3) real content and data; (4) all states, not just the happy path; (5) a critique-and-fix loop with screenshots at several widths; (6) accessibility audit with tools and keyboard testing; (7) a human making the three to five "surprise" decisions (concept, one signature interaction, brand voice); (8) a top model.

**What probably stays human for now (judgment):** an original concept, brand voice, taste calls under ambiguity, motion that tells a story, and the invisible detail work. AUV-Bench's judgment-action gap and the "usable but conventional" study both point the same way, but both are small and use older models.

---

## 6. UI, UX and frontend fundamentals

*Deep dive: [frontend-design/02-education-guide.md](frontend-design/02-education-guide.md).*

### 6.1 The map (and the order of work)

| Term | What it is | Question it answers |
|---|---|---|
| **UX** (user experience) | The whole journey: goals, flows, feedback, errors | Can people get what they came for without confusion? |
| **UI** (user interface) | What is on screen: layout, type, color, components, motion | Does it look and feel coherent and clear? |
| **IA** (information architecture) | How content is organized and labeled | Where does this live, and what is it called? |
| **Interaction design** | How things respond to input over time | What happens when I hover, click, wait, fail? |
| **Visual and brand design** | Identity: type, color, imagery, voice | Who is this for, and what does it feel like? |
| **Frontend engineering** | HTML, CSS, JavaScript, frameworks, performance, accessibility | Does it work in every browser for every person? |
| **Design system** | Reusable tokens, components, rules | How do we stay consistent as it grows? |

**Order of work:** people and goals → flows and structure → wireframe → visual system → components → states → polish → test. LLMs jump straight to the visual layer; you should make them start earlier.

### 6.2 Nielsen's ten usability heuristics (rules of thumb) as prompts

| # | Heuristic | Prompt it as |
|---|---|---|
| 1 | Visibility of system status | "Show loading, saving, success and failure for every async action." |
| 2 | Match with the real world | "Use plain language; no internal jargon." |
| 3 | User control and freedom | "Every destructive action has undo or confirmation; every modal has a clear exit." |
| 4 | Consistency and standards | "Reuse the same component for the same job; follow platform conventions." |
| 5 | Error prevention | "Guard invalid actions; sensible defaults; inline validation after each field." |
| 6 | Recognition over recall | "Visible labels, recent items, autocomplete." |
| 7 | Flexibility and efficiency | "Keyboard shortcuts and bulk actions, hidden from beginners." |
| 8 | Aesthetic and minimalist design | "Remove any element that does not support the primary task." |
| 9 | Help recover from errors | "Say what happened and what to do next." |
| 10 | Help and documentation | "Put help in the same place on every page." |

### 6.3 Core UX ideas (named laws are rules of thumb unless a study is cited)

- **Jakob's Law:** people expect your product to work like the others they use. Be conventional in navigation, forms, and checkout; be original in brand and a few delight moments.
- **Hick's law:** decision time grows with the logarithm of the number of *equally likely* choices (a review confirms limits: practice, very large sets, and structure change the picture). Ranking and grouping choices helps more than merely cutting their number **(judgment)**.
- **Fitts's law:** bigger and nearer targets are easier to hit ([ch. 12](#12-input-reading-and-forms)).
- **Cognitive load:** every element, word, or decision costs attention ([ch. 9](#9-cognitive-load-and-frustration)).
- **Progressive disclosure:** show essentials first; reveal advanced options on demand.
- **Affordances and signifiers:** things that look clickable must be clickable, and the reverse.
- **Mistakes versus slips (NN/g):** a mismatch with the user's mental model causes mistakes; inattention causes slips.
- **Peak-end rule (rule of thumb):** people remember the high point and the ending; polish confirmation moments.

### 6.4 Every screen has many states (LLMs usually build only the first)

| State | Design it |
|---|---|
| Populated | Realistic data: long names, many items |
| Empty | Say what belongs here and offer the next step |
| Loading | Skeleton or progress matching the final layout |
| Error | What happened, what to do, retry; keep user input |
| Partial or degraded | Offline, slow, some data missing |
| Success | Confirm the outcome; offer a next step |
| Disabled | Explain why when it is not obvious |
| Edge | Zero results, 10,000 results, very long text, no avatar, non-Latin text |

### 6.5 Frontend basics needed to review LLM output

- **HTML** gives structure and built-in accessibility: prefer native elements to `div` plus click handlers.
- **CSS:** custom properties (variables) for tokens; flexbox for one-dimensional layout; grid for two-dimensional; `clamp()` for fluid sizes; `:focus-visible`; `prefers-reduced-motion`; container queries.
- **Frameworks:** React/Next.js, Vue/Nuxt, Svelte/SvelteKit, Astro (content sites). Choose by team and need, not by the LLM's default.
- **Design tokens:** name values by role (`--color-text-muted`, `--space-4`), not by appearance. Components consume tokens; nobody hard-codes hex.
- **State:** server data (cache, loading, error) differs from UI state (open/closed). Do not mix them.
- **Review smells:** `div onClick`, `outline: none` with no replacement, fixed pixel widths, hard-coded colors, no `alt`, a huge unoptimized hero image, nested scroll containers, z-index wars, missing states.

### 6.6 How LLMs fail here, and your countermove

| Failure | You see | Countermove |
|---|---|---|
| Convergence | Inter, purple gradient, centered hero, 3 cards (or the 2026 cream/serif look) | Provide tokens and references before screens |
| Replacement defaults | Banned font becomes the next common font | Name what to use, not only what to avoid |
| Happy path only | No empty/loading/error states | Require a state matrix per screen |
| Drift between screens | Buttons and spacing differ | One tokens file and component library; "reuse, do not reinvent" |
| Decoration over function | Blobs, glass, gradients | "Every element must support a task" |
| Weak accessibility | Invisible focus, divs as buttons, low contrast | Put the checklist in the prompt; run axe; test with the keyboard |
| Lorem ipsum or generic copy | "Build faster" | Give real content and voice rules |
| Over-claiming done | "Everything works!" | Require screenshots at 3 widths and a keyboard walkthrough |

---

## 7. Accessibility law: US and EU

*Deep dive: [frontend-knowledge-base/01-legal-and-compliance.md](frontend-knowledge-base/01-legal-and-compliance.md). Not legal advice. All rows re-checked 2026-11-13 unless noted.*

**Plain-language key.** *WCAG* = Web Content Accessibility Guidelines, the technical standard. *Level A/AA/AAA* = increasing strictness; AA is the common legal target. *Success criterion (SC)* = one testable requirement. *ADA* = Americans with Disabilities Act. *Title II* covers state and local governments; *Title III* covers private businesses open to the public. *Section 504* bars disability discrimination by recipients of federal money. *Section 508* governs federal agencies' own technology.

### 7.1 US summary table [refreshed 2026-11-13]

| Regime | Applies to | Standard | Deadline or status | Source (grade) |
|---|---|---|---|---|
| **ADA Title II web and app rule** (28 CFR part 35) | State and local governments, including content provided through contractors | **WCAG 2.1 AA** | Population 50,000+: **April 26, 2027**. Under 50,000 and special district governments: **April 26, 2028**. A DOJ Interim Final Rule effective **April 20, 2026** moved both dates one year (old dates April 24, 2026 and April 26, 2027); comments closed June 22, 2026. DOJ says it "plans to engage in future rulemaking" on the rule's substance and may issue a proposed rule; if it does not, it "fully anticipates implementing the regulation at the new deadline." Ongoing obligations under existing Title II apply regardless of the dates | [Federal Register 2026-07663](https://www.federalregister.gov/documents/2026/04/20/2026-07663/extension-of-compliance-dates-for-nondiscrimination-on-the-basis-of-disability-accessibility-of-web) (A); [ADA.gov first steps](https://www.ada.gov/resources/web-rule-first-steps/) (A) |
| **Section 504 (HHS)**, 45 CFR 84.84 | Recipients of HHS funding: web content and mobile apps | **WCAG 2.1 A and AA** | 15+ employees: **May 11, 2027**. Under 15: **May 10, 2028**. One-year extension announced May 7, 2026 to align with DOJ; "does not impose new obligations" | [HHS press release](https://www.hhs.gov/press-room/hhs-extends-mobile-and-web-accessibility-deadline.html) (A); [eCFR](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-84/subpart-I/section-84.84) (A) |
| **Section 508** (36 CFR 1194) | Federal agencies' own technology and procurement | **WCAG 2.0 A and AA** | In effect since Jan 18, 2018. The Access Board issued a request for information in May 2025; I found no proposed rule adopting a newer WCAG, and a bill to move to WCAG 2.2 had not become law (the last two points from secondary sources, C) | [Access Board](https://www.access-board.gov/ict/) (A); secondary summaries (C) |
| **ADA Title III** | Private businesses that are public accommodations | No finalized web rule | Courts often treat business sites as covered; WCAG 2.1/2.2 AA is the usual benchmark in settlements. UsableNet counted **5,114** digital-accessibility suits in 2025 (3,195 federal; 1,919 in New York and California state courts); 45% of federal cases named companies already sued. Vendor-run count, so treat as an order of magnitude | [UsableNet 2025 year-end report](https://info.usablenet.com/2025-year-end-report-on-web-accessibility-lawsuits) (C; vendor sells accessibility tools) |
| **Overlays and "automatic compliance" claims** | Sellers of overlay widgets | FTC Act | FTC final order (April 2025) against accessiBe: $1 million and a ban on claiming its tool can make any website WCAG-compliant without competent evidence | [FTC order text](https://search.ftc.gov/system/files/ftc_gov/pdf/d-o.222_3156_-_accessibe_final_consent_package_without_signatures-2.pdf) (A) |
| **FTC deceptive design** | Commercial interfaces | FTC Act §5, ROSCA, CAN-SPAM, COPPA | 2022 staff report defines dark patterns. The 2024 "click-to-cancel" rule was vacated by the Eighth Circuit (July 2025); the FTC restored the pre-2024 rule effective Feb 12, 2026 and has restarted rulemaking. §5 and ROSCA enforcement continue | [FTC report 2022](https://search.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf) (A); [Federal Register 2026-02866](https://www.govinfo.gov/content/pkg/FR-2026-02-12/html/2026-02866.htm) (A); law-firm summaries (C) |

### 7.2 Standards and EU [refreshed 2026-11-13]

| Item | Status |
|---|---|
| **WCAG 2.2** | W3C Recommendation 5 Oct 2023 (updated 12 Dec 2024). Adds 9 success criteria to 2.1 and removes obsolete 4.1.1 Parsing. Content that meets 2.2 also meets 2.1 and 2.0. ISO/IEC 40500:2025 equals the Oct 2023 text; W3C expects the Dec 2024 text as ISO/IEC 40500:2026 by late 2026 (A) |
| **WCAG 3.0** | Working Draft dated 10 Sept 2026, "still several years of work," "does not replace WCAG 2," contrast algorithm "yet to be determined." Not usable for compliance (A). The WCAG 3 group charter (read in the prior session, not re-fetched) lists completion around Q4 2027 |
| **European Accessibility Act (EAA)** | Applies since **28 June 2025** to companies trading in the EU, wherever based |
| **EN 301 549** | **v4.1.1** (WCAG 2.2 AA) published Sept 2026 (adopted 24 Aug 2026; ETSI text read). **Not yet the legal reference**: v3.2.1 (WCAG 2.1 AA) remains the cited standard until the European Commission cites v4.1.1 in the Official Journal. Planning dates conflict between sources (late Nov and 16 Dec 2026): treat as unsettled |

### 7.3 What to build to

**Build to WCAG 2.2 AA.** One build then satisfies Section 508 (2.0), Title II and Section 504 (2.1), and the EU direction, and matches the usual private-sector settlement benchmark **(judgment on strategy; criteria from W3C)**. The nine 2.2 additions: 2.4.11 Focus Not Obscured (Minimum, AA), 2.4.12 Focus Not Obscured (Enhanced, AAA), 2.4.13 Focus Appearance (AAA), 2.5.7 Dragging Movements (AA), 2.5.8 Target Size Minimum (AA), 3.2.6 Consistent Help (A), 3.3.7 Redundant Entry (A), 3.3.8 Accessible Authentication Minimum (AA), 3.3.9 Accessible Authentication Enhanced (AAA).

### 7.4 Practical compliance notes

1. **Conformance is per full page and per process.** A multi-step purchase fails if any step fails. Test flows, not just pages.
2. **Third-party content counts.** Title II covers content provided "directly or through contractual, licensing, or other arrangements": widgets, embedded forms, payment pages, PDFs. Put accessibility requirements in vendor contracts. Federal procurement has a free Accessibility Requirements Tool.
3. **Overlays are not compliance** (FTC order above). WebAIM and UsableNet (vendor) both report suits against sites that used widgets.
4. **Publish an accessibility statement and a feedback path, and fix reported barriers.**
5. **Use the free federal manual test methods:** Section 508 ICT Testing Baseline and DHS Trusted Tester.
6. **Keep evidence:** audit reports, remediation tickets, conformance reports (VPAT/ACR). **(judgment)**
7. **Documents count.** PDFs are the worst-rated content type in WebAIM's 2026 survey (85.6% of respondents say PDFs are likely to cause significant problems).

### 7.5 Dark patterns and consent: design for lawful clarity

The FTC defines dark patterns as design practices that trick or manipulate users into choices they would not otherwise make. Rules that follow: cancel as easily as you sign up; show total price early; no pre-checked consent or add-ons; symmetric Accept and Decline; no fake urgency or false social proof; readable disclosures near the decision point. EU regulators go further on cookie banners (see [section 16.5](#165-privacy-and-consent)).

---

## 8. Accessibility engineering

*Deep dives: [frontend-knowledge-base/02](frontend-knowledge-base/02-accessibility-engineering.md), [14](frontend-knowledge-base/14-inclusive-design-ai-ux-and-wcag-check.md).*

### 8.1 Who is affected (US data)

| Fact | Number | Source (grade) |
|---|---|---|
| US adults with at least one disability, 2022 | 1 in 4 (~61 million); cognition 13.9%, mobility 12.2%, independent living 7.7%, hearing 6.2%, vision 5.5%, self-care 3.6% | CDC (A) |
| Adults 65+ with a disability | About 2 in 5 | CDC (A) |
| Color vision deficiency | About 1 in 12 men | NEI (A) |

CDC counts "serious difficulty," so it is a conservative estimate. Temporary and situational limits (glare, noise, a broken arm, stress) create the same barriers. **(judgment)**

### 8.2 The state of the web: WebAIM Million 2026 [refreshed]

Home pages, automated scan only (WAVE), February 2026 (B for a large, transparent dataset with stated limits):

- **95.9%** had detected WCAG 2 failures (94.8% in 2025: the first reversal after six years of small gains); **56.1** errors per page (51 in 2025).
- Pages are heavier: 1,437 elements on average (+14.3% in a year).
- Six error types are 96% of all errors, the same six for seven years:

| Failure | % of home pages, 2026 | 2025 |
|---|---|---|
| Low-contrast text | 83.9% | 79.1% |
| Missing alt text on images | 53.1% | 55.5% |
| Missing form input labels | 51.0% | 48.2% |
| Empty links | 46.3% | 45.4% |
| Empty buttons | 30.6% | 29.6% |
| Missing document language | 13.5% | 15.8% |

- **ARIA:** 82.7% of pages used ARIA; pages with ARIA averaged **59.1** detected errors versus **42** without. WebAIM warns this is correlation (more complex pages use more ARIA). 22% of ARIA menus introduced barriers through missing markup and keyboard behavior.
- Headings: 41.8% of pages skipped heading levels; 18.1% had more than one `h1`.
- WebAIM states: absence of detected errors does not mean a page is accessible.

**Implication:** fixing the six classes inside your design system gets most of the way to automated cleanliness; manual testing covers the rest.

### 8.3 Assistive technology reality check [refreshed: survey #11 supersedes #10]

WebAIM Screen Reader User Survey #11 (July-August 2026, **n = 1,780**; uncontrolled sample, B-). A commentator notes more than half of respondents are in North America and about 97% rate themselves intermediate or advanced, so it reflects experienced users:

| Metric | Result |
|---|---|
| Primary desktop screen reader | JAWS 55.0%, NVDA 32.9%, VoiceOver 6.5% (JAWS 40.5%, NVDA 37.7% in survey #10, early 2024) |
| Regional split | North America JAWS 72.5% vs NVDA 15.6%; Europe about even; NVDA dominant in Africa/Middle East, Asia, South America |
| Use more than one screen reader | 70.3% |
| Mobile | 91.8% use a screen reader on mobile; 73.3% use iPhone or iPad as main mobile device |
| Finding information on long pages | Headings first for 67.8%; 88.3% find heading levels useful |
| Documents | 85.6% say PDFs are very or somewhat likely to pose significant accessibility issues (Word: 31.1%) |
| Perceived progress (past year) | 32.2% "more accessible," 44.9% "no change," 22.9% "less accessible" |
| AI | 60.1% use AI to generate image descriptions (secondary summary, C) |

**Implications (judgment):** test with NVDA plus a browser and VoiceOver plus Safari (desktop and iOS), and ideally JAWS if your audience is North American; use a real heading structure; do not gate login on CAPTCHA-only flows (survey #10 called CAPTCHA "by far the most problematic" barrier; I did not confirm the same wording for #11).

### 8.4 The checks that matter most (WCAG 2.2, grouped by the four principles)

The four principles are **Perceivable, Operable, Understandable, Robust** (POUR). WCAG 2.2 has **86 current success criteria: 31 A, 24 AA, 31 AAA** (derived from W3C's machine-readable data; so Level A plus AA is 55). Target AA.

**Perceivable**
- Text alternatives (1.1.1): meaningful `alt` for informative images, `alt=""` for decorative; icon-only buttons need an accessible name.
- Captions and transcripts for media (1.2.x).
- Structure (1.3.1): real headings, lists, tables with headers, labels, landmarks; DOM order matches visual order (1.3.2).
- Reflow (1.4.10): usable at 320 CSS px (400% zoom) without two-direction scrolling.
- Contrast (1.4.3): 4.5:1 for normal text, 3:1 for large text; non-text contrast (1.4.11) 3:1 for component boundaries, focus indicators, meaningful graphics.
- Not color alone (1.4.1); resize text to 200% (1.4.4); text-spacing overrides must not break layout (1.4.12); hover and focus content must be dismissible, hoverable, persistent (1.4.13).

**Operable**
- Everything by keyboard, no traps (2.1.1, 2.1.2); skip link (2.4.1); page titles; focus order; visible focus (2.4.7).
- **2.4.11 Focus Not Obscured (AA):** sticky headers, cookie bars, and chat widgets must not completely hide the focused element (use `scroll-padding-top`).
- **2.5.7 Dragging (AA):** a single-pointer alternative to every drag.
- **2.5.8 Target Size Minimum (AA):** 24x24 CSS px or equivalent spacing; exceptions for inline links, browser controls, essential presentation, or an equivalent control elsewhere.
- No more than three flashes per second (2.3.1, level A); pause/stop/hide for moving content over 5 seconds (2.2.2); honor `prefers-reduced-motion` (2.3.3 Animation from Interactions is AAA, but it is the right behavior).
- Time limits can be extended (2.2.1); act on pointer *up* so users can abort (2.5.2); accessible name contains the visible label (2.5.3).

**Understandable**
- `lang` on `<html>` (3.1.1) and on foreign-language parts (3.1.2); predictable behavior with no unexpected context changes (3.2.x).
- **3.2.6 Consistent Help (A):** help in the same relative place on every page.
- Input help: labels or instructions (3.3.2), errors identified in text (3.3.1), suggestions (3.3.3), and confirm, review, or undo for legal, financial, and data-deleting actions (3.3.4).
- **3.3.7 Redundant Entry (A):** do not re-ask for information already given in the same process.
- **3.3.8 Accessible Authentication (AA):** no memory, transcription, or puzzle test without an alternative; allow paste and password managers.

**Robust**
- Name, role, value for custom widgets (4.1.2); status messages announced without moving focus (4.1.3).

**Related reminders:** 2.4.13 Focus Appearance is **AAA** (some older drafts had it at AA; if you read AA elsewhere that is the draft). 2.5.5 Target Size Enhanced is AAA.

### 8.5 Accessibility of AI-generated code

The evidence has changed since 2024 and the picture is mixed, not simply bad [refreshed]:

| Study | Finding | Grade |
|---|---|---|
| W4A 2024 (88 developers, GPT-3.5) | 84% of generated sites had accessibility problems by two automated tools; when asked to fix, ChatGPT fixed 70% of violations in its own code | B (automated only; old model) |
| arXiv 2501.03572 (GPT-4o, case study) | Fixes simple issues when prompted, struggles with complex ones; screenshots alongside prompts helped | A- (single case study) |
| CodeA11y, arXiv 2502.10884 (16 developers) | Developers failed to *ask* for accessibility, skipped manual steps, could not verify | A- |
| **ACM TOSEM 2026** (GPT-4o, Qwen2.5-Coder-32B, Gemini-3-Flash vs human code) | LLMs often produced **more** accessible code than humans on basics (contrast, alt text) but struggled with ARIA; zero-shot, few-shot and self-criticism prompting helped only a little; a feedback-driven approach (FeedA11y) that feeds accessibility test results back into generation helped | A- (abstract read) |
| **AXIS-Bench pilot, 2026** (12 interactive components, axe plus Playwright tests that find elements only by role and name) | Naive baseline 0/12; zero-shot LLM 6/12; LLM given the relevant WAI-ARIA Authoring Practices pattern text **12/12**. axe on isolated components did not distinguish the LLM conditions | A- (tiny pilot, abstract read) |
| **PACE, ASSETS 2026** (58 form components, 5 LLMs, 26,100 outputs) | Accessibility moved with the amount of accessibility guidance in the prompt, the model, the component, and how you measure | A- (abstract read) |
| A11yAgent, Web4All 2026 (20 developers; authors' own system) | A closed loop that renders, tests, and repairs cut violations 71.7-91.6% versus single-pass baselines | B- (authors evaluate their own tool; automated checks) |

**Converging conclusion (independent groups, 2025-2026):** models are decent at the easy, static items and weak at keyboard behavior, ARIA, and complex widgets; the most reliable improvements come from (a) telling the model the standard, (b) grounding it in the standard accessible pattern or an accessible component library, and (c) feeding real test output back to it. Static axe runs alone miss interactive failures.

### 8.6 Implementation rules

1. **Native HTML first** (`button`, `a`, `input`, `select`, `dialog`, `details`, `fieldset/legend`, `label`). First rule of ARIA: do not use ARIA if a native element will do.
2. One `h1`, no skipped levels, headings by meaning not size.
3. **Focus management:** on route change move focus to the new `h1` or main region; in modals trap focus, restore it on close, `Esc` closes, make the background `inert`.
4. **Visible focus:** `:focus-visible` with at least 3:1 contrast; never `outline: none` without a replacement.
5. **Forms:** visible `label` bound by `for`/`id`; `autocomplete` tokens; `aria-describedby` for hints and errors; `aria-invalid`; an error summary linking to fields; placeholder is not a label.
6. **Live regions:** `role="status"` for non-urgent updates, `role="alert"` for urgent ones; keep announcements short.
7. Tables for data only, with `th scope` and a caption.
8. Names: icon buttons get `aria-label` or hidden text; links describe the destination.
9. Test color tokens in light, dark, and forced-colors modes.
10. Respect `prefers-reduced-motion`, `prefers-color-scheme`, `prefers-contrast`, text zoom, and font-size settings; use `rem`. **Never disable zoom.**
11. Media: captions, transcripts, no autoplay with sound.
12. Documents (PDF, Office): tagged, titled, reading order, or provide HTML.
13. Custom components follow WAI-ARIA Authoring Practices keyboard patterns; prefer headless libraries that implement them.

### 8.7 Testing: a layered method

| Layer | Tools | Catches |
|---|---|---|
| Automated in CI | axe-core (`@axe-core/playwright`), Lighthouse, eslint-plugin-jsx-a11y, WAVE | Missing labels, alt text, contrast, ARIA misuse: a *subset* |
| Keyboard pass | Tab, Shift+Tab, Enter, Space, Esc, arrows | Traps, order, hidden focus, unreachable controls |
| Screen reader pass | NVDA + Firefox/Chrome, VoiceOver + Safari (macOS and iOS), TalkBack | Names, roles, announcements, reading order |
| Zoom and reflow | 200% text; 400% zoom at 1280 px; 320 px width | Clipping, overlap, sideways scroll |
| Preferences | Reduced motion, forced colors, dark mode | Lost borders, invisible icons |
| Federal method | Section 508 ICT Testing Baseline, DHS Trusted Tester | Repeatable manual conformance testing |
| People | Disabled users, including screen reader, low vision, motor, cognitive | Real usability, not just conformance |

**How much do tools catch?** Deque reports about 57% of issues by *volume* in 13,000+ pages of first-time audits, but issues found for only **16 of 50** WCAG 2.1 A/AA criteria. A peer-reviewed Swedish public-sector study found tools cover about one sixth of success criteria. Both are true because they use different denominators. Automation is a floor.

### 8.8 Design-system acceptance criteria (paste into each component's definition of done)

Keyboard operable with a documented key map; accessible name, role, state, value; visible focus ≥ 3:1 and not obscured; contrast ≥ 4.5:1 text and ≥ 3:1 UI in all themes and states; target ≥ 24x24 CSS px (prefer 44 on touch); works at 320 px and 200% text; reduced-motion variant; error and status messages programmatically exposed; axe passes in CI plus manual screen reader notes.

---

## 9. Cognitive load and frustration

*Deep dive: [frontend-knowledge-base/03](frontend-knowledge-base/03-cognitive-load-and-frustration.md).*

**Cognitive load** = the mental effort a task or screen demands. **Working memory** = the small mental scratchpad.

| Concept | Finding | Source (grade) |
|---|---|---|
| Working memory size | Miller (1956) said about 7 chunks but called it rough; Cowan (2001, 2010) argues about **4 (3-5)** when rehearsal and chunking are controlled | PubMed, PMC (A-) |
| Cognitive load theory (Sweller) | Load is *intrinsic* (task difficulty), *extraneous* (poor presentation, distraction), or *germane* (productive effort). Design should cut extraneous load | PMC6694886 (A-) |
| Five strategies | Combine text and visuals; place them together; include only essentials; emphasize essentials; avoid too much transient information | PMC7940870 (A-; instructional context, applied to UI by analogy **(judgment)**) |
| Split attention | Making users consult several places to form one picture raises load | PMC6703991 (A-) |
| RCT in an interface | A hospital follow-up dashboard designed with load theory (information integrated) led to more appropriate clinician actions, **no extra visit time**, lower frustration and perceived load (simulated visit) | PMC6703991 (A-) |
| External memory | Visible state, saved items, recents, and comparison tables offload memory; hard text on mobile takes longer to comprehend | NN/g (B) |
| Hick-Hyman law | Choice time rises with log2 of the number of equally likely options; limited by practice and compatibility | Proctor & Schneider 2018 (B) |
| Gist in one fixation | In 120 ms people classify a page into one of ten categories above chance (84.6% on a two-choice task) and find the menu | PMC5945715 (A-) |

**Skeptical reading:** load theory comes from learning research; UI studies are fewer. "7±2" is a myth as a design rule. Hick's law applies to equally likely options, so ranking and grouping help more than counting.

### 9.1 W3C cognitive accessibility (COGA) objectives

Help users understand what things are and how to use them; find what they need; use clear content; avoid mistakes; stay focused; avoid relying on memory; get help and support; adapt and personalize. COGA is a W3C Working Note (2021), informative and not required for WCAG conformance, but cognition is the most common self-reported disability type in US adults (13.9%), so this is not an edge case.

### 9.2 Load reducers tied to evidence

| Rule | Why | Practice |
|---|---|---|
| One primary action per view | Hick; focus | One filled button; others secondary or ghost |
| Chunk and group | Cowan; proximity | About 3-5 related items per group; headings; whitespace between groups |
| Recognition over recall | NN/g heuristic 6 | Visible options, recents, autocomplete, persistent summary in multi-step flows |
| Progressive disclosure | Manage intrinsic load | Advanced options behind "More" |
| Integrate related information | Split attention | Label next to control; units next to numbers; error beside the field |
| Familiar patterns | Jakob; COGA | Standard navigation, search, cart; underlined links |
| Plain language | Reading load | Short sentences, active voice, key point first |
| Descriptive headings | Scanning; screen readers | Question headings when they match user questions |
| Consistency | Less learning | Same action, label, place, component |
| Reduce transient information | Load theory | No auto-advancing carousels; no vanishing toasts for important information |
| Defaults and prefill | Fewer decisions | Remember choices; WCAG 3.3.7 |
| Chunk long tasks | Working memory | Progress and back; save progress |
| Show system state | Heuristic 1 | Loading, saved, synced, offline |
| Support interruption | Real life | Autosave; resume; session warnings with extension |

### 9.3 What causes frustration, and the fix

| Trigger | Evidence or standard | Fix |
|---|---|---|
| Slow or unresponsive UI | Nielsen limits; Core Web Vitals | Optimistic UI; feedback for work over about 50-100 ms |
| Layout shift under the cursor | CLS ≤ 0.1 | Reserve space for images, ads, embeds |
| Blank screen while waiting | Small studies: blank page judged slowest | Skeletons or progress |
| Premature or cryptic errors | Validating while typing slowed completion 7-10 s | Validate on blur or submit; message beside field |
| Lost input after an error | WCAG 3.3.x | Preserve all entries; error summary |
| Hidden or tiny targets | Touch research | 24 px floor; 44 px or ~10 mm on touch |
| Dead ends | Heuristics 3 and 9 | Next steps, back, undo, empty-state actions |
| Surprise context changes | WCAG 3.2.x | No auto-submit on select; no focus jumps |
| Dark patterns | FTC 2022 | Symmetric choices; easy exit |
| Inaccessible CAPTCHAs and logins | WCAG 3.3.8; WebAIM | Alternatives; allow paste and password managers; passkeys |
| Walls of text | F-pattern research | Headings, lists, bold lead-ins |
| Intrusive pop-ups | Banner-blindness research **(judgment)** | Trigger by intent; easy dismissal |

### 9.4 Messages that reduce frustration

- **Error formula:** what happened, why (if known), what to do. Example: "Card number must be 16 digits. You entered 15. Check the number on the front of your card." No blame, no codes alone, no ALL CAPS; place beside the field and link with `aria-describedby`.
- **Empty states:** what belongs here, why it is empty, one action.
- **Confirmation:** state the outcome and what happens next; offer undo.
- **Destructive actions:** specific labels ("Delete project"), consequences summarized, undo or delayed delete; WCAG 3.3.4.

---

## 10. Eye tracking and attention

*Deep dive: [frontend-knowledge-base/04](frontend-knowledge-base/04-eye-tracking-and-attention.md).*

**Fixation** = eyes pause (about 200-300 ms) to take in information. **Saccade** = the jump between fixations. **AOI** = area of interest. Eye tracking shows *where people look*, not *what they understood*.

| Study | Result | Limits |
|---|---|---|
| NN/g F-pattern (2006; n=232) | Read across the top, a shorter second read lower, then a vertical scan down the left; first words of lines get most fixations | Vendor, 2006 |
| NN/g scanning patterns (2019) and *How people read online* (500+ participants over 13 years) | Four main patterns: **F** (appears without subheadings and bullets), **spotted**, **layer-cake** (fixate on headings), **commitment** (read nearly everything). Patterns similar across languages | Descriptive; full report paid |
| NN/g *Scrolling and Attention* (2018; n=120; 130,000+ fixations) | **57%** of viewing time above the fold, **74%** within the first two screens (2010 study: 80% above the fold) | Desktop only |
| Gist at a glance (PMC5945715) | 120 ms is enough to classify page type and locate menus | Static screenshots |
| Banner blindness (IJHCI 2014) | Strongest for right-side banners and goal-directed tasks | E-commerce pages; one lab |
| Neutral vs emotional banners (PMC9128483) | Neutral banners were recognized *better* | Two experiments |
| Inline validation (Wroblewski/Etre, 2009; n=22) | Best inline variant vs submit-only: +22% success, -22% errors, +31% satisfaction, -42% time, -47% fixations; validating while typing was 7-10 s slower | Practitioner, small, 2009, not peer reviewed (C) |
| Three-column vs grid (peer reviewed, n=16) | Column layouts led to more extensive reading and faster target finding on easy tasks | Small |

**Design rules supported:** front-load the point (first two lines and first words); structure content so people can layer-cake scan instead of F-scan (the F is a *failure* mode, not a target); prioritize the top of the page on desktop; group with whitespace and boundaries; do not make important notices look like ads; make the page's purpose clear in one glance; design forms for few fixations; offer reading controls; test on target devices (the fold and F-pattern do not transfer automatically to phones).

**Running or buying a study:** webcam trackers are cheaper but less precise; use realistic tasks, not free viewing; define AOIs beforehand; report n, device, and calibration; pair with think-aloud; session replay and heatmaps are behavior proxies, not gaze. Do not claim eye-tracking results cover screen reader, keyboard, or voice users.

---

## 11. Performance and perceived speed

*Deep dive: [frontend-knowledge-base/05](frontend-knowledge-base/05-performance-and-perceived-speed.md).*

### 11.1 Human time thresholds

| Threshold | Meaning | Source (grade) |
|---|---|---|
| ~16 ms per frame | 60 fps looks smooth; leave about 10 ms of your own work per frame | web.dev RAIL (C) |
| 0.1 s | Feels instant; the result feels caused by the user | Nielsen, NN/g (B) |
| 1 s | Flow of thought preserved; show that something is happening if longer | Nielsen (B) |
| 10 s | Limit for keeping attention; give percent-done and a way to cancel | Nielsen (B) |

### 11.2 Core Web Vitals [refreshed 2026-11-13: thresholds unchanged]

**Core Web Vitals** are Google's three field-measured user-experience metrics, judged at the **75th percentile** of real page loads, mobile and desktop separately. A page passes only if all three are "good."

| Metric | Measures | Good | Poor |
|---|---|---|---|
| **LCP** Largest Contentful Paint | When the main content has likely loaded | ≤ 2.5 s | > 4.0 s |
| **INP** Interaction to Next Paint | How quickly the page responds to input (replaced FID as a stable vital in 2024) | ≤ 200 ms | > 500 ms |
| **CLS** Cumulative Layout Shift | Unexpected movement of content | ≤ 0.1 | > 0.25 |

Sources: [web.dev vitals](https://web.dev/articles/vitals), [thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds) (C+, Google-authored).

**New in 2026:** Chrome added *experimental* versions of all three vitals that also count **soft navigations** (route changes inside single-page apps) to the Chrome UX Report (CrUX; September 2026 data, published October 13). Stable scores and thresholds are unchanged; Chrome plans to include soft navigations from **May 2027**, and the `web-vitals` library v6 (July 2026) added soft-navigation support. In the October 2026 CrUX release 56.3% of origins had good vitals on the stable metrics; 60.3% with soft navigations included. Chrome's own notes call the continued INP regression "a cause for concern" without a known cause.

**Do vitals affect search ranking?** Google's Search Central page says it "highly recommend[s]" good vitals and that this "aligns with what our core ranking systems seek to reward." It states no weight. A third-party analysis (D/C) found no Google source for a site-wide vitals assessment since a March 2026 core update. **Judgment:** vitals matter for users; treat any ranking effect as modest and unquantified.

### 11.3 Perceived-performance research (loading feedback)

| Study | Result | Limits |
|---|---|---|
| Human Factors 2009 (three experiments) | A **constant-rate progress bar** was best on both informativeness and acceptability | Students; simulated |
| Partitioned progress indicators (n=30) | More partitions reduced perceived wait; bars preferred to spinners; too many partitions annoyed | Young sample |
| OutSystems thesis | Progress bar most satisfying; experienced users liked skeleton structure | One product |
| ECCE 2018 skeleton vs spinner | Skeleton rated faster; no significant differences | Small null result |
| IHC 2025 (n=21, mostly young tech workers) | Skeleton best; **blank page worst** (52.4% judged slow) at identical real time; combining techniques did not help | Exploratory; conflicts with bar studies |

**Synthesis (judgment):** (1) never leave a blank screen; (2) give feedback for anything over about 100-300 ms; (3) for waits of several seconds, determinate progress helps people decide to wait or act; (4) skeletons help when you know the layout and the wait is short to moderate; (5) do not stack indicators; (6) keep indicator motion calm.

### 11.4 Engineering patterns

- **Loading:** ship less JavaScript (split by route, defer non-critical, avoid hydrating static content); prioritize the LCP element (`fetchpriority="high"`, preload, responsive `srcset`, AVIF/WebP, correct dimensions); fonts: subset, self-host, `font-display: swap` or `optional`, size-adjusted fallbacks; server: CDN, caching, compression, streaming HTML.
- **Stable layout:** set `width` and `height` or `aspect-ratio`; reserve slots for ads and embeds; never insert content above existing content after load; animate with `transform`.
- **Responsiveness (INP):** keep main-thread tasks under about 50 ms; yield (`scheduler.yield`); move heavy work to Web Workers; virtualize long lists; prefer CSS animation; **optimistic UI** (reflect the action at once, reconcile later; show failure and retry); pressed state within 100 ms; disable the button during submit and show "Saving..." to prevent double submission.
- **Perceived speed:** skeletons matching final layout; real progress for waits over 1-2 s and percent plus cancel past 10 s; prefetch likely next routes; stale-while-revalidate; progressive rendering; preserve state (scroll, form data, filters); motion 100-200 ms feedback, 200-400 ms transitions, with a reduced-motion variant.
- **Resilience:** offline and slow-network states; retry with backoff; timeouts with clear messages; saved drafts; test on a mid-range Android phone with throttled CPU and slow 4G **(judgment)**.

### 11.5 Measure it

| What | Tool |
|---|---|
| Lab | Lighthouse (cannot measure INP; uses Total Blocking Time as a proxy), WebPageTest, DevTools Performance |
| Field (real users) | CrUX, `web-vitals` library, real-user monitoring |
| Budgets in CI | Lighthouse CI, bundle-size limits (web.dev's old starter default was 170 KB of critical resources on a baseline phone over 3G; re-derive for your audience) |

Use **field data** for decisions: lab scores are not the 75th-percentile user experience. Accessibility and performance meet: announce loading and results with live regions, keep focus on content swaps, and make sure zoom and forced-colors modes do not trigger layout shift.

---

## 12. Input, reading and forms

*Deep dive: [frontend-knowledge-base/06](frontend-knowledge-base/06-input-reading-and-forms.md).*

### 12.1 Touch targets: three numbers, reconciled

**Fitts's law:** pointing time grows as targets get smaller or farther; fingers add blocking and imprecision.

| Number | Where it comes from | Use |
|---|---|---|
| **24x24 CSS px** | WCAG 2.5.8 (AA): a legal floor; aimed at tremor, spasticity, special input devices | Minimum, never below |
| **44x44 CSS px** | Platform guidance (about 7-10 mm depending on device density) | Default on touch **(judgment)** |
| **9-10 mm** (adults); **14 mm** (older adults); **18 mm** (motor impairments) | Studies: icon touching (change point near 6 mm; literature says 10 mm); one-handed thumb (no significant error differences at ≥ 9.6 mm discrete); older adults (accuracy lower below 14 mm); CHI 2017 (error 42.1% at 6 mm vs 7.0% at 18 mm; touch errors over 3x mouse) | Audiences that include older adults or motor impairments: public services, health, finance |

Rules: increase the hit area with padding, not only visuals; keep destructive actions away from frequent ones; avoid drag-only interactions (2.5.7) and act on pointer-up (2.5.2); never make hover the only way to reveal a control. People tap near the center of the screen and are least accurate at edges and corners (Hoober, C); "thumb zone" heat maps are **folklore-adjacent**: grip varies, so do not over-plan for one.

### 12.2 Reading comfort

| Topic | Evidence | Rule |
|---|---|---|
| Line length | A review recommends no more than about 70 characters; a 2001 experiment found 55 characters best for comprehension; Anthropic's design skill says under 80 | Body measure about 45-75 characters (`max-width: 65ch`) |
| Font size | Older adults prefer larger fonts, with a critical size beyond which readability falls (systematic review) | 16 px or more; honor browser scaling; 200% without loss; avoid fixed-px containers |
| Dyslexia | Mixed: one eye-tracking study found short lines gave 27% faster reading and halved regressions; a 2021 study of adults found no effect on speed or comprehension and no preference for narrow lines | Do not lock one layout; let users change width, spacing, font; avoid justified text and italic walls |
| Structure and plain language | Eye tracking and plainlanguage.gov | Headings, lists, short paragraphs, key point first |

Starting defaults **(judgment, then test):** 16-18 px body, 1.5-1.6 line height, paragraph spacing at least 1 em, up to about 70 characters, left-aligned for left-to-right languages, no all-caps blocks.

### 12.3 Forms: rules

1. **Fewer fields.** Ask only what you need; hide optional ones.
2. **One column,** top-aligned labels, grouped fields (`fieldset`/`legend`), logical order. (Label-alignment evidence is secondhand: test your own.)
3. **Real, always-visible labels.** Placeholders vanish and are low-contrast.
4. **Right input type and `autocomplete`** (also WCAG 1.3.5); allow paste and password managers.
5. **Mark required and optional in text,** not color alone.
6. **Hints before, errors after.** Show errors on blur or submit, not on the first keystroke; never erase input.
7. **Error summary** at the top on submit, linking to fields; focus moves to it; each error says what and how to fix.
8. **Do not make people re-enter** information (3.3.7); persist across steps.
9. **Accessible authentication** (3.3.8): no memory or transcription tests; support passkeys and magic links with alternatives.
10. **Confirm and allow undo** for destructive, legal, and financial actions (3.3.4).
11. **Multi-step forms:** named steps, back without loss, review and edit before submit.
12. **Do not time out silently;** warn and allow extension; save drafts.
13. **Disabled submit buttons hide the reason;** prefer an enabled button with clear errors, or explain why it is disabled **(judgment)**.
14. **Accept varied formats** (spaces, dashes) and normalize.
15. **Mobile:** large targets, correct keyboard, avoid wheels; use radios instead of dropdowns for short lists.

### 12.4 Navigation and findability

Conventional global navigation; visible labels over icon-only; current location indicated (`aria-current`); search for large sites with forgiving matching; breadcrumbs for deep hierarchies; descriptive link text; links distinguishable from text without color alone. The HHS/GSA *Research-Based Web Design and Usability Guidelines* (209 guidelines, each rated for importance and strength of evidence; 2006 edition, predates mobile) is a free prioritization aid.

---

## 13. Visual design

*Deep dive: [frontend-knowledge-base/09](frontend-knowledge-base/09-visual-design-fundamentals.md) and [frontend-design/02](frontend-design/02-education-guide.md) (Part 3).*

### 13.1 Why it matters beyond taste

| Finding | Detail | Grade |
|---|---|---|
| Appeal is judged in a blink | Homepage appeal ratings at 50 ms and at 500 ms correlated r = .947 (Lindgaard et al. 2006). Eight designers could not agree *why* | B; correlation of ratings, 2000s homepages, mostly students |
| Beauty shapes perceived usability | In an ATM-like app, aesthetics changed post-use perceptions of usability but **actual** usability did not (Tractinsky 2000) | B; lab surrogate |
| First impressions are partly predictable | Colorfulness and visual complexity explained about half the variance in 500 ms ratings of 450 sites (Reinecke, CHI 2013) | B |
| Looks drive credibility judgments | "Design look" appeared in 46.1% of 2,684 people's credibility comments (Fogg 2003) | B; comments, not outcomes |
| Limits | Attractive designs earn tolerance for *minor* problems, not major ones, and can **mask problems in usability tests**: watch behavior, not comments (NN/g) | B |

**Takeaway:** a poor look can cost trust before function is judged, and a good look can hide problems from your own research. It does not say pretty beats functional.

### 13.2 Hierarchy and grouping (Gestalt)

**Gestalt** principles describe how people group visual elements. Hierarchy guides the eye with **size, weight, color/contrast, spacing, and position**. Proximity (near means related) can override color or shape similarity; common region (a border or background) can override proximity but overuse creates clutter. Rules: one dominant element per view; a squint test (blur the screenshot; does the primary action survive?) **(judgment)**; consistent spacing scale; group by proximity first; add borders only if needed; fewer borders, more spacing (Refactoring UI, B-).

### 13.3 Typography

- **Pick a type system, not a font:** a scale (for example 12/14/16/20/24/32/48), weights, line heights. Popular fonts are fine; Linear ships Inter, Vercel Geist, Stripe Söhne.
- Body 16 px or more, line height 1.4-1.6, measure 45-75 characters **(rules of thumb)**; headings 1.1-1.3 line height; at most two families (one is often enough); real weight contrast (400 vs 700-800); tabular, right-aligned figures in tables; no all-caps paragraphs; `font-display: swap` and no layout shift.
- WCAG text-spacing (1.4.12), resize (1.4.4), and reflow (1.4.10) must still work.
- Not researched: modular-scale ratios, variable-font performance, pairing rules. Treat "golden ratio" claims as folklore.

### 13.4 Color and contrast

- **Structure:** neutrals (6-10 steps), one accent, semantic colors (success, warning, danger, info). Start in grayscale; add color for meaning. Tint neutrals slightly toward the brand hue.
- **Conformance contrast** is WCAG 2.2's ratio: 4.5:1 normal text, 3:1 large text and UI parts. Never rely on color alone (1.4.1).
- **APCA** (a newer perceptual contrast method) is not part of any standard: WCAG 3's draft says the algorithm is "yet to be determined." Use APCA as a second opinion and report WCAG 2.2 for conformance.
- Test every text/background pair and every border and icon, in every theme and state (hover, disabled, error).
- Not researched: hue harmony, 60-30-10, color psychology claims.

### 13.5 Dark mode

The sources I read show: dark text on light backgrounds gave better acuity and proofreading for younger and older adults (Piepenbrock 2013); at simulated night light mode still won for small text; participants performed better in light mode but did not report noticing; dark mode may help some low-vision users (for example with cataract). **Offer both,** follow `prefers-color-scheme` by default, let users override, and contrast-test each theme. **Do not claim dark mode reduces eye strain**: the sources do not show it. Dark mode is a redesign of semantic color mappings, not an inversion.

### 13.6 Depth, shape, imagery, icons

Choose one elevation approach and one radius personality, and apply them with intent (the same radius on everything is a tell). Real product screenshots or purposeful illustration beat blobs and stock 3D. Icons are ambiguous: **always add a visible text label** (NN/g); one set, one stroke weight, one size.

### 13.7 Motion

- Purpose: show status, guide attention, express personality. `prefers-reduced-motion: reduce` means *minimize* non-essential motion, not necessarily remove all animation.
- Flashing: no more than three per second (2.3.1, level A). Vestibular harm from parallax and scroll animation is why 2.3.3 exists (AAA). Moving content over 5 seconds needs pause/stop/hide (2.2.2).
- Durations (rule of thumb, not evidence): micro-feedback 100-200 ms; transitions 200-400 ms; page-level up to 600 ms. Ease-out in, ease-in out. Animate `transform` and `opacity`. One orchestrated page-load moment beats scattered effects (also Anthropic's skill: "motion that answers a person's action... is welcome").

### 13.8 Quick visual audit

| Question | Pass looks like |
|---|---|
| What is the single primary action? | Visually dominant; one per view |
| Are groups obvious without labels? | Proximity and common region make sections evident |
| Does it survive grayscale? | State and hierarchy do not depend on hue |
| Do both themes pass contrast? | 4.5:1 text, 3:1 UI in each |
| Are icons labeled? | Visible text beside every non-universal icon |
| Is motion optional? | Reduced-motion variant; no flashing; pause control |

---

## 14. Design systems and tokens

*Deep dive: [frontend-knowledge-base/10](frontend-knowledge-base/10-design-systems-and-tokens.md).*

A **design system** = tokens (named design decisions) + components (coded, accessible blocks) + guidelines + tooling **(judgment: my working definition)**. There is little controlled evidence that design systems improve outcomes; benefits are practitioner-reported.

### 14.1 Tokens

- The Design Tokens Community Group published **Format Module 2025.10** (28 Oct 2025) as a stable *Community Group report*: **not a W3C Standard.** Tokens are JSON with `$value` and a required `$type`; it adds theming, modern color spaces (Display P3, Oklch), aliases (A for spec text; adoption claims are the group's own, C). I did not re-check for a newer version in this refresh.
- **Three tiers (judgment, common practice):** *primitive* (`color.blue.600`, `space.4`), *semantic* (`color.text.default`, `color.action.primary`), *component* (`button.primary.bg`, sparingly). Components consume semantic tokens only; themes remap semantic to primitive; name by meaning (`color.danger`, not `color.red`). Dark mode is a second semantic mapping and must be contrast-checked.

### 14.2 Components

| Option | What the docs say (C) |
|---|---|
| **Radix Primitives** | Unstyled, accessible components following WAI-ARIA patterns; handle roles, focus, keyboard; self-reports testing with VoiceOver, JAWS, NVDA |
| **React Aria (Adobe)** | Components plus lower-level hooks |
| **shadcn/ui** | "Open code": a CLI copies component source into your project; you own maintenance |
| **Tailwind CSS** | Utility-first styling; OpenAI's frontend guidance names Tailwind, shadcn/ui, and Radix Themes as recommended libraries |

**Why this matters for LLM work (judgment):** headless primitives encode hard behavior (focus trap, roving tabindex, ARIA state) that models often get wrong when hand-rolling dialogs and comboboxes; the AXIS-Bench pilot supports pattern grounding (chapter 8.5). Steer the model to them and restyle with your own tokens. Library docs describe intent; **I did not run accessibility tests on Radix, React Aria, or shadcn output.**

**Component API checklist (judgment):** native elements first; composition over giant prop lists; controlled and uncontrolled usage; forward refs and spread props; document every state (default, hover, focus-visible, active, disabled, loading, error, empty); document keyboard and screen reader behavior; logical CSS properties for right-to-left support.

### 14.3 Documentation and testing in the system

| Layer | Tool and verified behavior |
|---|---|
| Interaction tests | Storybook `play` functions |
| Accessibility tests | `@storybook/addon-a11y` (built on axe-core; Storybook's wording: "automatically catches up to 57% of WCAG issues": see the Deque caveat in 8.7) |
| Visual tests | Pixel snapshots per story against a baseline (Chromatic is the vendor option) |
| Screenshot assertions in end-to-end tests | Playwright `toHaveScreenshot()`: rendering varies by OS, browser, hardware, so generate and compare in the same environment; defaults `threshold` 0.2 |
| Flakiness fixes | Wait for fonts and images, freeze time, stop animations, mask dynamic regions, same OS in CI |

**Governance (judgment):** treat tokens as an API (semver, deprecation window, changelog); assign an owner; measure adoption (share of UI using system components) rather than assuming benefit.

---

## 15. Responsive, mobile, localization and content

*Deep dive: [frontend-knowledge-base/11](frontend-knowledge-base/11-responsive-mobile-and-localization.md).*

### 15.1 Responsive layout mechanics (MDN reference, C)

- **Container queries:** set `container-type: inline-size` on an ancestor and use `@container (min-width: 400px)`; size containers cannot take size from their contents. **Judgment:** container queries for reusable components, media queries for the page shell.
- **Fluid type:** combine `clamp()` with a `rem` term so zoom still works (`clamp(1rem, 0.875rem + 0.5cqi, 1.25rem)` is an example from a search synthesis: verify before use). Pure viewport units can break zoom.
- **Logical properties** (`margin-inline-start`, `padding-block`, `inline-size`) follow writing direction so layouts adapt to right-to-left and vertical writing. Physical properties (`left`, `margin-left`) do not flip.
- Not researched: Grid vs Flexbox rules, subgrid, `dvh`/`svh` units, browser support tables (check MDN or caniuse).

### 15.2 Touch, grip, gestures

Users switch grips constantly; people prefer the center of the screen and are least accurate at corners and edges (Hoober, C); fingers cover content, so leave pressed states visible; WCAG 2.5.7 (drag alternatives, AA) and 2.5.1 (complex path gestures need alternatives, A). Mobile eye-tracking research was not covered; do not assume desktop F-pattern results transfer.

### 15.3 Progressive Web Apps

A PWA needs a web app manifest and a service worker. web.dev's checklist expects installable, fast, and accessible. **Judgment:** worth it when you need installability or offline; otherwise a fast responsive site is simpler. Service-worker stale caches are a classic cause of "my fix isn't showing."

### 15.4 Internationalization (i18n), localization, right-to-left

- **i18n** = designing for many locales; **l10n** = adapting for one.
- **Text expansion:** W3C cites IBM averages: strings up to 10 characters grow 200-300% in European translations; 11-20: 180-200%; 21-30: 160-180%; 31-50: 140-160%; over 70: 130%. Allow 2-3x growth in short labels and buttons.
- Checklist **(judgment)**: set `lang` and `dir`; logical CSS; no text in images; no concatenated sentences (word order differs); pseudo-localize with long strings and test a right-to-left language; mirror directional icons (arrows, back) but not logos, media controls, or numerals (verify per locale).
- Not researched: plurals and ICU MessageFormat, `Intl` formatting, CJK/Indic font fallback, cultural color or imagery differences.

### 15.5 Content design and plain language

- Lower-literacy users read word by word and cannot take in text at a glance (NN/g): aim for about 6th-grade level on key pages and 8th elsewhere, main point first, a single column.
- Seniors (NN/g 2013; 31 seniors on 29 sites): success 55.3% vs 74.5% for ages 21-55; time on task 7:49 vs 5:28; people 65+ were 43% slower. Larger text and links, static widgets, tolerance for imprecise pointing.
- Content checklist: user's words; point first; one idea per sentence; verbs on buttons ("Save changes," not "Submit"); errors say what happened and how to fix; test with real users, not only a reading-grade formula.

### 15.6 Cross-device test matrix **(judgment)**

| Dimension | Minimum set |
|---|---|
| Viewport | 320 px (reflow), about 768, 1280+ (and 360-390 for phones) |
| Input | Touch, mouse, keyboard only, screen reader |
| Settings | 200% zoom, large text, reduced motion, dark mode, forced colors |
| Network and device | Throttled 4G/3G, low-end Android |
| Locale | A long-text language, a right-to-left language |

---

## 16. Frontend engineering issues

*Deep dive: [frontend-knowledge-base/12](frontend-knowledge-base/12-frontend-engineering-issues.md).*

### 16.1 Rendering strategies

| Strategy | Trade-off (web.dev, C+) | Best for **(judgment)** |
|---|---|---|
| **Static (SSG)** | Built ahead; fast first byte; deployable to a CDN; cannot personalize per request | Marketing, docs, blogs |
| **Server-side (SSR)** | Fast first paint and less client JS, but server cost and slower first byte; heavy client work after SSR still hurts INP | Personalized pages that need SEO |
| **Client-side (CSR)** | Low first byte but content waits for JavaScript, which grows with the app; HTML made on the client is invisible to the preload scanner, hurting LCP | Behind-login app shells |
| **Hydration** | SSR plus client JS to make it interactive; can add blocking time | |

Default to static; add server rendering where content is dynamic and SEO matters; client rendering behind login; budget JavaScript regardless. Primary docs for incremental static regeneration and React Server Components were not read.

### 16.2 State, forms, error handling

Group related state; avoid contradictory, duplicated, deeply nested state; store IDs not objects (react.dev). Classify state before choosing a library: UI, server cache, URL, form, global **(judgment)**. Validate on the server always and mirror rules on the client for feedback. Error handling: plain language, specific cause, a way forward, preserve input, never blame the user.

### 16.3 Security basics

| Topic | Guidance (C+) |
|---|---|
| XSS (cross-site scripting: attacker script injected through unescaped input) | Main defense is output encoding plus sanitization; frameworks escape by default |
| Escape hatches | `dangerouslySetInnerHTML`, Angular `bypassSecurityTrustAs*`, Lit `unsafeHTML` disable encoding; validate URLs (`javascript:`) |
| CSP (Content Security Policy header) | A backup, not the primary defense; strict CSP with nonce or hash; `object-src 'none'`, `base-uri 'none'` |
| Trusted Types | `require-trusted-types-for 'script'` makes DOM sinks reject plain strings; does not sanitize by itself |

Passkey and session handling were not researched.

### 16.4 SEO for frontend engineers

Google crawls, renders, and indexes JavaScript but may queue rendering; dynamic rendering is "a workaround and not a long-term solution" (use SSR, static, or hydration); other engines may ignore JavaScript; Google says useful, people-first content matters most and it has no preferred word count. See 11.2 for vitals and ranking.

### 16.5 Privacy and consent

Not a lawyer; confirm with counsel.

| Finding | Source (grade) |
|---|---|
| In experiments with 80,000+ users on a German site, banner position, choice type, and nudging strongly changed outcomes; highlighted or pre-selected "accept" raised consent; privacy-by-default opt-in produced under 0.1% accepting all purposes | Utz et al., CCS 2019 (B) |
| Crawl of about 11,000 shopping sites: 1,818 dark-pattern instances on 1,254 sites (11.1%) | Mathur et al. 2019 (A-) |
| EDPB Cookie Banner Taskforce (Jan 2023): most authorities treat a missing first-layer reject option as invalid consent; withdrawing consent must be as easy as giving it | EDPB (A, regulator work) |
| CNIL (France) ordered banner changes where rejecting was harder than accepting | CNIL (A) |
| California: businesses must honor opt-out preference signals; Global Privacy Control qualifies | CPPA (A) |

Checklist **(judgment)**: reject as prominent as accept on the first layer; no pre-ticked boxes; no cookies before consent where required; easy withdrawal; detect `Sec-GPC: 1` for California visitors. Consent-gated analytics are a biased sample.

### 16.6 Testing and budgets

Test pyramid (many small tests, fewer slow UI tests; Fowler calls it "overly simplistic" but useful). Add automated accessibility checks in component and end-to-end tests, visual regression, and manual keyboard and screen reader passes. A performance budget is a limit on metrics enforced in CI (webpack warns at 250 KB by default; Lighthouse CI can fail a pull request). Browser compatibility, tech debt, and analytics ethics were not researched.

---

## 17. UX research methods and measurement

*Deep dive: [frontend-knowledge-base/13](frontend-knowledge-base/13-ux-research-methods-and-measurement.md).*

### 17.1 Choosing a method

| Question | Method | Typical n |
|---|---|---|
| Biggest problems in this design? | Moderated qualitative usability test | About 5 per user group per round |
| Real goals and context? | Interviews, contextual inquiry, diary study | Varies |
| How should content be grouped? | Open card sort | NN/g: at least 15 per group |
| Can people find things? | Tree test (text-only hierarchy) | Quantitative scale |
| Benchmark success rate and time? | Quantitative usability study | About 40 (15% margin, 95% confidence, binary metric) |
| Which version performs better live? | A/B test | Thousands |

### 17.2 "Five users" is about finding problems, not measuring rates

Nielsen's model says five users find about 85% of problems. Faulkner (2003) resampled and found five-user samples found between **55% and nearly 100%** (groups of 10 raised the minimum to 80%; 20 to 95%). Five of five task completions still has a 95% interval of roughly 48-100%. **Use about five per segment per round for discovery, iterate, and never report percentages from five people as rates.** For rare serious problems, recruit that group specifically (for example, screen reader users).

### 17.3 A/B testing pitfalls

- **Sample ratio mismatch (SRM):** if observed split differs from the design (821,588 vs 815,482 users on a 50/50 split has p ≈ 1.8e-6), stop and find the bug; test with chi-square, not by eye.
- **Twyman's law:** an interesting result is usually wrong; investigate good results as hard as bad ones.
- Validate the platform with A/A tests; cap outliers; expect most real effects to be small (0.1-1%) after much work. Kohavi's data come from Microsoft/Bing/Amazon scale; small sites usually lack power for tiny effects, so prefer qualitative tests plus bolder changes **(judgment)**.
- Not covered by a source I read: peeking and optional stopping, multiple comparisons, novelty effects.

### 17.4 Standardized instruments

| Instrument | What it measures | Verified facts (grade) |
|---|---|---|
| **SUS** (System Usability Scale) | Perceived usability, 0-100 | 10 items; odd items (rating - 1), even items (5 - rating), sum x 2.5; across about 500 studies the average is 68 (MeasuringU benchmarks skew to software/web, so 68 is not universal). Brooke's chapter is 1996; MeasuringU says 1986: unresolved, so cite 1996 (B) |
| **NASA-TLX** | Subjective workload | Hart and Staveland 1988; six subscales (mental, physical, temporal demand, performance, effort, frustration); public-domain document (A-) |
| **UEQ / UEQ-S** | User experience (six scales; UEQ-S has 8 items) | Free in 30+ languages (B) |

Pair every questionnaire with behavior (success, time, errors). Questionnaires measure perception and the aesthetic-usability effect can inflate it.

### 17.5 Other methods

- **Heuristic evaluation** (expert review against the ten heuristics) finds different problems than user tests and misses real behavior; do both when possible.
- **Information architecture:** card sorting generates grouping ideas (early); tree testing evaluates findability of a structure (isolated from visual cues).
- **Jobs To Be Done (JTBD):** a lens (what progress, in what circumstance, versus which alternatives). Two camps (Christensen's switch interviews; Ulwick's quantified outcomes) disagree; no validated predictive method **(judgment)**.
- **Minimal research plan:** (1) the decision it informs; (2) segments and recruiting (include assistive technology users); (3) realistic, non-leading tasks; (4) metrics; (5) sample and why; (6) analysis rules written *before* looking; (7) consent and data handling.

---

## 18. Inclusive design and AI-feature UX

*Deep dive: [frontend-knowledge-base/14](frontend-knowledge-base/14-inclusive-design-ai-ux-and-wcag-check.md).*

### 18.1 Beyond WCAG: audiences and what the sources say

| Audience | Verified guidance |
|---|---|
| Cognitive and neurodiverse | W3C COGA; WCAG 2.2's 3.2.6, 3.3.7, 3.3.8 target cognitive load; blinking and flashing can be problematic for people with ADHD, vestibular disorders, epilepsy, migraine (MDN) |
| Older adults | NN/g: larger text and links, avoid moving menus and sliders, static widgets, tolerate imprecise pointing |
| Low literacy | Single column, 6th-8th grade text, linear navigation |
| Low bandwidth or old devices | A performance budget and a mid-range phone test |
| Situational limits | Glare, noise, carrying items, split attention: multi-encode feedback |
| Voice and switch users | 2.5.3 Label in Name makes "click Submit" work; switch access depth not researched |
| Cultural differences | Reading direction, text expansion; cultural color and imagery not researched |
| Ethical design | Dark patterns are common (11.1% of sites in a crawl); regulators treat lopsided reject/accept as invalid consent |

**Principle (judgment):** conformance is a floor. WCAG does not guarantee comprehension, and real users with disabilities find barriers audits miss. Budget for testing with them.

### 18.2 AI-feature UX (chat, streaming, trust, errors)

| Source | What it gives you (grade) |
|---|---|
| Amershi et al., CHI 2019 | **18 guidelines** from 150+ recommendations, validated with 49 practitioners on 20 AI products; phases: initially, during interaction, when wrong, over time (B) |
| Google PAIR guidebook | Patterns for onboarding, explaining the system, calibrating trust, control vs automation, recovery (C+) |
| NN/g prompt structure (diary study, 18 participants, 425 conversations, 2023 tools) | Prompts contain request, framing, format, references; vague prompts cause long "funneling" conversations; users lack vocabulary to describe visual style (B) |
| NN/g articulation barrier and prompt controls | Mix GUI controls (recognition) with free text (B) |
| NN/g chatbot guidelines | Suggested prompts as buttons; **do not autoscroll** a long streaming response, because readers lose their place (B) |

**Checklist for AI features (judgment):** state capabilities and limits up front and show example requests; suggested prompts and clarifying questions as clickable controls; streaming: keep reading position stable, offer stop, keep partial output on failure; easy to undo, edit, regenerate, give feedback; show sources or uncertainty where wrong answers matter; failure states say what failed, what was saved, what to do; announce status changes (4.1.3) without spamming screen readers (**specific `aria-live` streaming patterns: not researched**, test with NVDA and VoiceOver); say what is sent to models and retained.

---

## 19. Prompting LLMs for frontend work

*Deep dives: [frontend-knowledge-base/15](frontend-knowledge-base/15-llm-prompting-for-frontend.md), [frontend-design/03](frontend-design/03-prompt-template-kit.md).*

### 19.1 The core idea

**Reduce the entropy of the request.** Every constraint removes probability from the generic result. Make the design decisions yourself (or with the model in a *separate, no-code step*), write them down, then have the model implement inside them.

```
0. Intake answers      → Appendix A.1
1. Design brief        → A.2   (DESIGN-BRIEF.md, the source of truth)
2. Direction options   → A.3   (3 options, no code)
3. Tokens + styleguide → A.4
4. ONE screen, then screenshots → A.5
5. State matrix + accessibility pass → A.6
6. Remaining screens, reuse the system → A.7
7. Critique, anti-slop, audit loops → A.8, section 21
```

### 19.2 What is proven, plausible, folklore, or unsettled

| Claim | Status | Evidence |
|---|---|---|
| Prompt wording and format can change results a lot | **Supported (older open models, classification tasks)** | Sclar et al.: up to 76 accuracy points from meaning-preserving formatting changes on LLaMA-2-13B (arXiv 2310.11324) |
| Few-shot examples help consistency | **Supported; all three vendors agree** | Anthropic: examples are "one of the most reliable ways" to steer, use 3-5; OpenAI: show diverse input/output; **Google [refreshed]: "always include few-shot examples"; keep their format identical; too many can overfit** |
| Chain-of-thought helps reasoning | **Supported (math, logic); not shown for design quality** | Wei et al.; Kojima et al. |
| "You are a world-class designer" persona lines raise quality | **Not supported for accuracy tasks; unknown for design** | Zheng et al., EMNLP Findings 2024 (162 personas, 2,410 questions: no gain, effects "largely random"); Principled Personas 2025 (irrelevant persona details cut performance by almost 30 points). No UI-specific study |
| Specific constraints beat vague requests | **Plausible, vendor-endorsed; no controlled UI A/B found** | Anthropic, NN/g |
| Models converge on generic UI unless steered | **Vendor-reported, widely observed, not independently measured** | Anthropic; the official skill's own 2026 list of generated-page defaults |
| Self-critique loops improve output | **Mixed: works when they add new information** | Self-Refine (GPT-3.5/4, 7 tasks) vs Huang et al. (intrinsic self-correction without external feedback struggles). The 2026 accessibility studies (8.5) show gains when test output is fed back |
| Visual self-revision helps | **Model-dependent** | Design2Code: helped GPT-4V, not GPT-4o or Gemini Pro Vision; giving extracted text helped weaker models |
| LLM-as-judge approximates human preference | **Supported, with biases** | Zheng et al.: over 80% agreement with humans; position, verbosity, self-enhancement bias. No validation for judging visual taste |
| Long context is used evenly | **False** | "Lost in the Middle": best at start and end; Anthropic: "context rot," keep context "informative, yet tight" |
| Broad negative instructions are safe | **Doubtful [refreshed]** | Google Cloud's Gemini 3 guide: blanket "do not infer/guess" can make a model fail at basic deduction; say what to use instead |
| AI makes experienced developers faster | **Unsettled [refreshed]** | METR early-2025 RCT (16 developers, 246 tasks): tasks took **19% longer** (95% CI +2% to +39%); developers predicted 24% faster. METR's late-2025 follow-up (57 developers): point estimates -18% (CI -38% to +9%) for 10 returning developers and -4% (CI -15% to +9%) for 47 new ones, i.e. faster but not significant; METR says the data are unreliable because developers refused to work without AI and withheld tasks, and believes speedups are probably larger in 2026 but gives only "very weak evidence." Narrow population (experienced maintainers of familiar repositories) |
| AI code is secure | **Not supported** | Copilot 2021: about 40% of 1,689 programs vulnerable; assistant users wrote less secure code and were more confident (older tools) |
| Models invent packages | **Supported** | 576,000 samples, 16 LLMs: at least 5.2% hallucinated package names for commercial models, 21.7% for open-source |
| Generated UI is accessible by default | **Not supported, but nuanced [refreshed]** | See 8.5: basics good, ARIA and widgets weak; guidance and feedback loops help |

### 19.3 What the vendors say, and where they differ

| Topic | Anthropic | OpenAI | Google (Gemini docs, read 2026-11-13) |
|---|---|---|---|
| Success criteria and evals first | Yes: define success, test empirically | Yes: build evals, pin versions | Experiment with example count |
| Detail level | "Right altitude": not brittle, not vague; give motivation | Precise for GPT-style models; high-level goals for reasoning models | Be precise and direct; Gemini 3 "may over-analyze verbose or overly complex prompt engineering techniques used for older models" |
| Examples | 3-5, diverse, tagged | Diverse inputs and outputs | Always include; same format; do not overdo |
| Structure | XML tags; long documents first, question after | Markdown or XML sections | Consistent delimiters; context first, instructions at the end |
| Emphasis | Soften "CRITICAL/MUST" on newer models | Not found | Avoid unnecessary persuasive language |
| Verification | Give the agent tools to check UI | "Instruct the model to test changes" | Not covered in the pages read |
| Frontend steering | `<frontend_aesthetics>` block; official skill now plan, review against brief, build, critique; **the brief's own words always win** | Recommends Tailwind, shadcn/ui, Radix Themes, Lucide; hidden-rubric one-shot | Not covered |

**Resolved conflict (judgment):** "be explicit" and "give high-level goals" are different advice for different model types. Re-test your prompts when you change models, and keep prompts short and structured.

### 19.4 The context stack: what to give the model

| Layer | Contents | Reason |
|---|---|---|
| 1. Persistent rules | Stack, token file path, banned patterns *with replacements*, accessibility bar, commands to run | Rules files (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules`) |
| 2. Spec | Users, task, states, content, constraints, acceptance checks | NN/g prompt components |
| 3. Design context | Tokens as variables (not prose), component list, 1-2 reference screens | Machine-readable decisions |
| 4. Reference images | Screenshot plus the **text extracted** from it | Design2Code text-augmented prompting; screenshots helped accessibility fixes |
| 5. Verification tools | Playwright, axe, linter, tests | Anthropic: give verification tools |
| 6. Task | One screen or component at a time | Keep context lean |

Rules-file facts (vendor docs, C): Cursor project rules live in `.cursor/rules` as `.mdc` files (plain `.md` there is ignored); keep rules under about 500 lines; reference files instead of copying; add a rule when the agent repeats a mistake. Claude Code's `CLAUDE.md` is context, not enforced configuration; aim under about 200 lines; use a PreToolUse hook to *block* an action. Figma MCP exposes design context and variables; Playwright MCP works from accessibility-tree snapshots (a useful side effect: if the agent cannot find your control by role and name, a screen reader probably cannot either, **judgment**), and its `browser_run_code_unsafe` tool is described as equivalent to remote code execution: enable only for trusted clients.

### 19.5 Agentic loops that work (and their limits)

A loop = the agent builds, looks at the result, lists defects, fixes, and re-checks. **Loops help when each cycle adds new information** (screenshot, axe output, test result, measurement). A loop of "review your own work" with no new signal is weaker.

Best-supported loop (Appendix A.5 and A.9): start the dev server → screenshots at 375, 768, 1280 px in light and dark → numbered defects with measurements → fix only listed defects → re-run typecheck, lint, tests, axe → cap at 4 iterations → stop and ask if a fix needs a new dependency, token change, or design decision. Limits: Playwright pixel comparisons are brittle across OS and browser; LLM judges are biased (use a different model or fresh context than the author; randomize order; calibrate with a few human-rated examples); a judge never replaces usability testing.

### 19.6 Build a small eval for your own prompts

1. Pick 5-10 representative screen or component briefs.
2. Define automated pass/fail checks: typecheck, lint, axe, Lighthouse budget, screenshots at three widths with no overflow, no banned fonts or colors, token-only CSS (grep).
3. Add a 1-5 human rubric (hierarchy, fit to brief, clarity), rated blind to which prompt produced the output.
4. Run each variant 3-5 times (outputs vary); compare means and spread.
5. Re-run on every model or prompt change.

This is what both Anthropic and OpenAI recommend, and it is the only way to learn whether a pattern in this guide helps *you*. **Every prompt pattern in Appendix A is untested by me.**

### 19.7 Failure modes and mitigations

| Failure | Mitigation |
|---|---|
| Generic aesthetics | Concrete direction, banned list with replacements, reference screens, tokens |
| Hallucinated APIs or packages | A.11; lockfile check; typecheck; read package docs |
| Inaccessible custom widgets | Radix or React Aria; pattern text in the prompt (A.10); axe plus manual keyboard and screen reader |
| Invented content or statistics | Provide real copy; forbid inventing |
| Scope creep | Scope line; "do not refactor unrelated code"; small diffs |
| Security flaws and overconfidence | A.12; code review; treat output as untrusted code |
| Context rot in long sessions | Fresh context per screen; notes file |
| Fragile visual tests | Same environment; mask dynamic regions; cap iterations |
| Prompt drift across model versions | Pin versions; keep an eval set |
| Self-flattering reviews | Separate reviewer pass with a rubric; human spot checks |

---

## 20. Tools, plugins and models

*Deep dive: [frontend-design/04](frontend-design/04-tools-plugins-and-models.md). Facts below were checked on 2026-11-13 through GitHub's repository API, repository files, the Hugging Face Hub, and the arena.ai leaderboard. **I did not install or run any tool or model.** GitHub stars are popularity, not quality.*

### 20.1 Skills and plugins

| Tool | License | What it does | Checked facts | Install (as published) |
|---|---|---|---|---|
| **Anthropic `frontend-design`** (`anthropics/skills`) | Apache-2.0 (LICENSE.txt in the skill folder) | One SKILL.md for distinctive design. **Now a plan, review against the brief, build, critique process**; lists the 2026 generated-page defaults to avoid; "the brief's own words always win"; sets quality floor (responsive, visible focus, reduced motion) | Repo 193,762 stars; skill last changed 2026-09-03 | `/plugin install frontend-design@claude-plugins-official` or `npx skills add anthropics/skills --skill frontend-design` |
| **Impeccable** (`pbakaus/impeccable`) | Apache-2.0 | 24 commands (`critique`, `audit`, `polish`, `typeset`, `layout`, `bolder`, `quieter`, `harden`, `adapt`, and more) and **62 deterministic slop-detection rules** (no model needed); `init` writes `PRODUCT.md`, `document` writes `DESIGN.md`; works with Claude Code, Cursor, Codex CLI, Copilot, Gemini CLI and others | 109,084 stars; pushed 2026-11-13. README says it is "strongest on interfaces that already exist" | `npx impeccable install` |
| **UI UX Pro Max** (`nextlevelbuilder/ui-ux-pro-max-skill`) | MIT | Searchable design database (80 styles, 192 reasoning rules per its README badge); needs Python 3 | 148,744 stars | `npx skills add nextlevelbuilder/ui-ux-pro-max-skill --skill ui-ux-pro-max` or the plugin marketplace |
| **Vercel `web-design-guidelines`** (`vercel-labs/agent-skills`) | No license detected by the API (check the repo) | Audits UI code against accessibility and UX rules; folder confirmed in the repo's `skills/` directory; contents not read | 33,969 stars | `npx skills add vercel-labs/agent-skills --skill web-design-guidelines` |
| **shadcn skill** (`shadcn-ui/ui`) | MIT | Teaches the agent the shadcn CLI and `components.json` | 128,046 stars | `npx skills add shadcn-ui/ui --skill shadcn` |
| Taste Skill, Emil Kowalski skills, unslop, Awwwards MCP, Google Stitch and Figma skills | Various | Marketing pages; motion craft; de-slopping; reference-driven briefs; design-tool-first flows | **Not re-verified in this refresh** (aggregator-sourced, D) | See each repo |
| **Playwright, Lighthouse, axe** | MIT / Apache-2.0 | Give the agent *eyes*: screenshots at breakpoints, accessibility and performance scores | Well-established | `npm i -D @playwright/test @axe-core/playwright`; `npx lighthouse` |

**Recommended stack (judgment):** (1) your own `DESIGN-BRIEF.md` and `tokens.css` (Appendix A.2, A.4) as the thing that prevents drift; (2) `frontend-design` or Impeccable for generation-time steering; (3) Playwright screenshots plus axe in the loop; (4) Impeccable `audit` or Vercel `web-design-guidelines` as a last-step review; (5) UI UX Pro Max only if you have no brand yet.

**Cautions:** skills change the look but do not remove the "AI look" (the official skill's own 2026 list proves defaults shift); third-party skills are someone else's instructions and scripts running in your agent: read the SKILL.md and scripts first and pin versions; some skills assume Claude Code paths and need adjusting for Cursor or Codex.

### 20.2 Models for frontend work [refreshed 2026-11-11 snapshot, see 5.4]

Hosted frontier models, with list prices per million tokens (input/output) from the leaderboard: Claude Fable 5.2 ($8/$40), Claude Opus 5.5 ($4/$20), Claude Sonnet 5.5 ($2/$10), Gemini 4 Carbon ($2/$10, preliminary), GPT-6 Astra ($10/$50). **Value pick (judgment):** Sonnet 5.5 ranks third at one-fifth of the price of the top model, and its rank overlaps ranks 4-5.

**Open-weight models on the Hub** (license and size checked on the Hub 2026-11-13):

| Model | Arena (open) | Facts checked | Run it how |
|---|---|---|---|
| Kimi K3.1 Pro (`moonshotai/Kimi-K3.1-Pro`) | 1687 | About 2.78 trillion parameters; vision; license "other" (custom); one inference provider listed | API only for almost everyone |
| DeepSeek-V4.1-Flash (`deepseek-ai/DeepSeek-V4.1-Flash`) | 1664 | MIT; about 763 billion parameters (**"Flash" is not small**); several inference providers | Hosted API |
| Qwen3.8-27B (`Qwen/Qwen3.8-27B`) | 1590 | Apache-2.0; about 27.8 billion parameters; multimodal; many providers | The most realistic strong model to run locally (judgment) |
| Others on the arena's open list | MiMo-V2.6-Flash 1638 (MIT), GLM-5.3 1622 (MIT), Kimi K3 1658 (own license), Inkling 2 Small 1647 (Apache-2.0, preliminary) | Not checked on the Hub | Check each license |

Always check the license before commercial use.

**Small UI-specialist models** (not re-checked except as noted): Tesslate UIGEN-X family (4B/8B/32B; Qwen3 base; Apache-2.0; **the 32B model was last modified 2025-07-27** and showed 51 recent downloads on the Hub API (2026-11-13), so it is stale relative to frontier models); UIGEN-T2/T3 (HTML plus Tailwind); WebSight VLM and Design2Code-18B (screenshot to code, 2024 research models). **Judgment:** these are fast spec-to-scaffold tools trained on average data; they inherit the sameness problem and do not replace a design system. For screenshot-to-code, current general frontier or large open vision models beat the 2024 specialists (Design2Code table).

### 20.3 Free resources

| Need | Resource |
|---|---|
| Accessible primitives | Radix UI, React Aria, Headless UI, Ark UI |
| Styled starting points (restyle them) | shadcn/ui, Park UI, Mantine, DaisyUI |
| Fonts | Google Fonts, Fontsource, Bunny Fonts; Geist, IBM Plex, Source Serif/Sans, Newsreader, Bricolage Grotesque, JetBrains Mono, Fraunces, Instrument Serif/Sans |
| Color | Radix Colors, OKLCH tools, Realtime Colors, WebAIM contrast checker |
| Icons | Lucide, Phosphor, Tabler, Heroicons |
| Inspiration | Awwwards, Godly, Land-book, Mobbin, Refero, Page Flows |
| Education | NN/g, web.dev, W3C WAI, Laws of UX, Refactoring UI, GOV.UK Design System |
| Testing | axe DevTools, Lighthouse, Playwright, WAVE, Chrome DevTools Rendering tab |

### 20.4 A recommended free setup (about an hour)

1. Create `DESIGN-BRIEF.md` (A.2) from your intake answers (A.1). 2. Run the direction prompt (A.3) with the best model you can afford. 3. Generate `tokens.css` and a `/styleguide` page (A.4). 4. Install one skill plus Playwright and axe. 5. Build the hero screen (A.5) and require screenshots at three widths. 6. Run the state and accessibility pass (A.6), then critique and anti-slop (A.8). 7. Reuse the system on remaining screens (A.7). 8. Final audit (section 21).

---

## 21. Audit checklist and audit prompt

*Deep dive: [frontend-knowledge-base/08](frontend-knowledge-base/08-audit-checklist.md). The full checklists are in [Appendix B](#appendix-b-checklists); the copy-paste audit prompt is [Appendix A.9](#a9-llm-audit-prompt).*

**How to use them.** Per screen and per flow. Run the automated checks first (axe, Lighthouse), then the keyboard walkthrough, then a screen reader pass, then a first-glance test with a stranger. Treat the LLM audit prompt as a *first pass* that produces a defect table with evidence; it cannot verify screen reader behavior, real-device performance, or real-user data, and says so.

**Severity vocabulary:** *blocker* (prevents a task or violates a legal baseline), *major* (significant friction or WCAG A/AA failure with a workaround), *minor* (polish).

---

# Part C: Skeptical review

## 22. Skeptical notes

Where this guide could mislead you, and what I did about it.

1. **Many "numbers" are single-source or vendor-reported.** The Anthropic claim that models converge on generic design, the Deque "57%" figure, Kohavi's rates, and arena Elo values are all reported by an interested or single party. Where I could not find independent confirmation I left the claim labeled, not upgraded.
2. **The AI taste-gap studies are small and dated.** Benchmarks (Design2Code, WebDev Arena, ArtifactsBench) rank models against each other. Leaderboard Elo measures what voters preferred in short, single-prompt sessions, not whether a design is usable or accessible.
3. **Rubric math was wrong in the earlier draft.** The design report's rubric averages did not match its own table; recomputed averages are 2.3, 3.0, 3.9 and 4.95 (Appendix F). A reminder that this guide, too, was assembled by a language model and can contain arithmetic or recall errors: verify anything you will act on.
4. **Eye-tracking findings are old and desktop-heavy.** The F-pattern is a pattern of *poorly structured text pages*, not a law. Banner blindness findings depend on task. Mobile attention data is thin.
5. **Dark mode, touch-target millimetres, line length, and "thumb zone" claims are each supported by a few small studies** that disagree at the margins. I gave ranges and defaults, not single "correct" values.
6. **Accessibility tooling numbers are contested.** Deque says automated testing catches 57% of issues by volume; at the criterion level axe-core fully covers only a minority of WCAG success criteria. Both are true because they measure different things.
7. **Law is unsettled on purpose.** The DOJ rule is an interim final rule that DOJ has said it may revisit; the HHS dates moved; Title III has no web rule and relies on litigation; EU standards are mid-update. Anything dated here is a snapshot.
8. **Personas, "act as," and similar prompt folklore are mostly untested for design.** The one rigorous test I found (Zheng et al.) shows no accuracy gain on factual tasks. That is evidence of *absence of benefit there*, not proof of harm for design critique.
9. **My percentage for "how close vibe coding gets" (70-85%) is an opinion** built from direction-of-effect evidence, not a measured result.
10. **Tools change weekly.** Stars, versions, leaderboard ranks and model names in chapter 20 were true on 2026-11-13 and will drift.

## 23. Risk map: how a team following this guide can still fail

The UI analog of "the résumé passes the ATS but a human rejects it." Each row is a case where the *automated* signal and the *human* reality disagree.

| Automated signal says | Humans experience | Why | Countermeasure |
|---|---|---|---|
| axe and Lighthouse are clean | The page is unusable with a keyboard or screen reader | Tools cannot judge focus order sense, accessible-name quality, meaning of alt text ("image"), custom widget behavior, or untested states | Manual keyboard and screen reader passes; test with disabled users |
| Lighthouse lab score is 100 | Slow on a mid-range phone on 4G | Lab is one device and network; field data is the 75th percentile of real users | Use CrUX/RUM; throttle; test on real low-end devices |
| WCAG 2.1 AA conformant (meets the 2026 US legal floor) | Fails on WCAG 2.2 items (target size, focus not obscured, redundant entry, accessible authentication) | Law lags the standard; EU and procurement may expect 2.2 | Build to 2.2 AA |
| LLM judge rates the design 9/10 | Real users cannot find the primary action | Judges favor length and polish and self-generated output; no validation for visual taste | Use judges for triage only; usability tests decide |
| Screenshot matches the reference | Content invented, claims false, copy generic | Pixel match does not check meaning | Provide real content; review copy |
| Legal text on the consent banner is present | Reject button buried, pre-ticked boxes, confusing wording | Compliance is evaluated on nudging and symmetry, not presence | Symmetric choices; counsel review; test comprehension |
| Rule-based slop detector passes | Still bland | Absence of known tells is not presence of identity | Pair with a brief, references, and a human "what makes this ours" decision |
| Design system adopted | Inconsistent screens anyway | Tokens ignored, one-off overrides, no enforcement | Lint for off-token values; track adoption |
| Overlay widget installed ("fixes accessibility") | Barriers remain; legal exposure | FTC order against accessiBe ($1M) for deceptive claims; no overlay replaces fixing code | Fix source code; never rely on overlays |
| Heavy ARIA added "for accessibility" | Screen reader experience worse | Pages with ARIA had more detected errors in WebAIM scans (correlation, not proof of causation) | Native HTML first; ARIA only to fill gaps |
| A/B test shows a win | Not real | SRM, Twyman's law, peeking, low power | Check SRM; replicate |
| Visual regression test fails | Nothing is wrong | Anti-aliasing, fonts, animations, dynamic data, different OS | Same environment; mask; freeze time |
| (reverse) axe flags an issue | A false positive on decorative or hidden elements | Rule heuristics | Verify manually before "fixing" |
| High leaderboard Elo | Poor fit for your stack and brand | Preference voting on small tasks | Run your own eval set (19.6) |
| Deadline in the guide | Date has moved | Rulemaking and agency actions change | Recheck primary sources |

## 24. Evidence gaps and open problems

**Not tested or not found (so treat related advice as judgment):**

1. No controlled study found of **detailed design briefs versus vague prompts** for generated UI quality; the whole prompt kit in Appendix A is untested by me.
2. **LLM-as-judge validity for visual taste and usability** is unproven; position and verbosity biases are documented for text.
3. **Mobile eye tracking** and attention on current interfaces.
4. **PACE** (LLM-generated UI evaluation) and **AXIS-Bench** (accessibility benchmark) were read at abstract/summary level only; their numbers should be re-verified from the full papers before being quoted.
5. **Gemini prompting documentation** was read through search excerpts (the page timed out on fetch).
6. **The status of the DOJ's possible reopening of the Title II rule** is known only from secondary reporting; check the Federal Register and ADA.gov.
7. **Section 508 refresh** status known only through secondary summaries.
8. **ISR and React Server Components** primary documentation, **Baseline** browser-support tracking, **passkeys** UX, **accessible data visualization**, **native app accessibility**, **streaming/live-region patterns** for AI chat, **plurals and ICU MessageFormat**, **A/B testing peeking and multiple comparisons**: not researched.
9. **Skills and plugin quality:** no independent, controlled comparison; star counts and README claims only. The Taste Skill and several aggregator-listed tools were not re-verified.
10. **Whether AI coding assistants speed or slow developers** (METR) is unsettled (19.2).
11. **How fast "the AI look" drifts** after each model release: observed, not measured.
12. **Accessibility of generated code** has mixed evidence (8.5); more independent, replicated studies are needed.

**Open problems (nobody knows yet):** How to specify taste in machine-checkable form; how to keep brand identity across many generated screens without a human gatekeeper; how to test screen reader experience automatically; how to evaluate cognitive load without people; whether WCAG 3 will arrive in usable form and when.

---

# Part D: Appendices

## Appendix A: Copy-paste prompts

Every prompt below is **untested by me** (see 19.6 and 24). Replace bracketed items. Run them in order for a new product; use A.8-A.9 anytime. Source: [frontend-design/03](frontend-design/03-prompt-template-kit.md), edited and extended.

### A.1 Intake questions

Copy this block, fill it in, and paste it to the model. Where you answer "don't know," tell the model to propose 3 options with tradeoffs.

```markdown
## Purpose and users
1. What is this, in one sentence? (e.g., "A scheduling app for independent dog walkers.")
2. Who uses it? Role, tech comfort, device (phone/desktop), setting (office/outdoors/at night).
3. The single most important task a user must complete in under 60 seconds:
4. Top 3 other tasks, ranked:
5. What does the user feel before and after? (anxious -> relieved, bored -> curious)
6. Is this a marketing page, a web app/tool, a dashboard, content/editorial, e-commerce, or a mix?

## Success and constraints
7. What does success look like? (signups, task completion rate, time on task, trust)
8. Must-have platforms and browsers? Mobile first? Offline?
9. Tech stack constraints (framework, component library, CSS approach)? If none, say so.
10. Accessibility target (default: WCAG 2.2 AA)? Languages / RTL?
11. Performance budget (e.g., LCP < 2.5s on mid-range phone)?
12. Existing brand assets: logo, colors, fonts, voice guidelines? Attach them.

## Taste and references
13. Three sites/apps whose FEEL you want, and exactly what you like about each (type? density? motion? color? tone?).
14. Two sites/apps you do NOT want to resemble, and why.
15. Five adjectives for the brand. Then five adjectives it must NOT be.
16. Density: airy / balanced / dense? Tone: playful / calm / serious / luxurious / technical?
17. Light, dark, or both? Any color that must appear? Any color that must not?
18. One signature moment that people should remember (a hero interaction, a data visualization, a unique transition, a distinctive illustration style)? If none, ask the model for 3 ideas.

## Content
19. Real headlines, copy, product names, and sample data (or say "invent realistic ones for [domain]").
20. Real images/screenshots available? If not, what substitutes are acceptable (no blobs, no stock 3D)?
21. Voice: how does the product talk? Three example sentences in that voice.

## Scope
22. Screens/pages needed (list). Which one is the "hero" screen to design first?
23. Which states matter most (empty, loading, error, permissions, offline)?
24. What can be deferred?
```

---

### A.2 Design brief template

Save as `DESIGN-BRIEF.md` in the repo and tell the model to read it at the start of every session.

```markdown
# Design Brief: [Product]

## 1. Product and audience
- One-liner:
- Primary user, context, device:
- Primary task (60 seconds):
- Emotional goal:

## 2. Design principles (3-5; each is a rule the model can use to break ties)
1. e.g., "Speed over decoration. Anything that delays the primary task is removed."
2. e.g., "Calm confidence. One accent color, generous space, no gradients."
3. e.g., "Show real data. Never lorem ipsum, never placeholder charts."

## 3. Visual direction
- Style in one sentence + reference URLs + what to take from each (not "copy it"):
- Anti-references and why:
- Density: [airy | balanced | dense]
- Theme: [light | dark | both; default = ...]
- Signature moment:

## 4. Tokens (see Part 4; paste the file or summarize)
- Type: [display font] / [text font] / [mono], scale, weights
- Color: neutrals, accent, semantic
- Space: base unit and scale
- Shape: radius personality, border and shadow rules
- Motion: durations, easing, what animates and what must not

## 5. Components and behavior
- Library to use (headless primitives + our tokens): 
- Required component list:
- Conventions: button hierarchy (1 primary per view), form validation timing, table behavior, toasts vs inline

## 6. Content and voice
- Voice rules:
- Words to use / avoid:
- Real sample content: (attach)

## 7. Accessibility and quality bar
- WCAG 2.2 AA; keyboard-complete; visible focus; reduced motion; contrast 4.5:1/3:1; targets >= 24px
- Responsive: 360, 768, 1024, 1440
- Performance: [budget]

## 8. Banned list (project-specific)
- e.g., purple/indigo gradients, nested cards, 3-equal-card feature rows, blurred blobs, emoji as icons, icon-in-tinted-square, ALL-CAPS eyebrow above every heading, centered-hero-plus-logo-strip by default, identical radius on everything, lorem ipsum

## 9. Definition of done
- Screenshots at 360/768/1440; keyboard walkthrough; axe/Lighthouse results; all states shown; no hard-coded colors or magic numbers; matches tokens
```

---

### A.3 Direction exploration (before any code)

Use this to avoid the first-guess average. Ask for *options with rationale*, not a finished page.

```text
Read DESIGN-BRIEF.md. Do not write code yet.

Propose THREE meaningfully different visual directions for [product]. They must differ in
typography, color strategy, layout structure, and motion personality, not just hue.
For each:
- Name and one-line concept
- Type pairing (display/text/mono) with reasons and a Google Fonts or open-source source
- A palette of 5-7 named colors with hex values and the role of each; state the contrast ratio of text/background pairs
- Layout idea for the hero screen (describe the grid and what is on it)
- One signature interaction
- Risks: who will dislike it and where it could fail usability
- Which famous defaults it deliberately avoids and what it replaces them with

Then recommend one and say what you would need from me to commit.
Do NOT default to Inter, Roboto, Arial, system fonts, purple/indigo gradients on white, a centered hero with three
equal cards, or tinted-square icons, unless you can justify them for this specific audience.
Also avoid replacing them with the next most common choice (for example Space Grotesk) without a reason tied to the brief.
```

---

### A.4 Tokens and system prompt

Ask for the system as a file first, then build with it.

```text
Using the chosen direction, create these files and nothing else:
1. tokens.css with CSS custom properties, named by role not by appearance:
   --font-display, --font-text, --font-mono; --text-xs ... --text-4xl with line-heights; weights;
   --color-bg, --color-surface, --color-surface-raised, --color-border, --color-text, --color-text-muted,
   --color-accent, --color-accent-contrast, --color-success/warning/danger/info (each with a subtle background variant);
   --space-1 ... --space-12 on a 4px base; --radius-control, --radius-surface; --shadow-1/2/3;
   --duration-fast/base/slow; --ease-out, --ease-in-out; focus ring token.
   Include a dark theme override using prefers-color-scheme or a data-theme attribute.
2. A "tokens.md" explaining each choice in one line and the rules for use:
   when to use each type size, which color pairings are allowed, max one accent-filled button per view.
3. A /styleguide page that renders type scale, colors with contrast ratios, buttons in all states, inputs in all states,
   a card, a table, a modal, a toast, empty/loading/error examples.

Rules: components must consume tokens only; hard-coded hex, px values outside the scale, and inline styles are bugs.
Check every text/background pair against WCAG 2.2 AA and fix failures.
```

---

### A.5 Build one screen, then inspect

```text
Read DESIGN-BRIEF.md, tokens.css and tokens.md.
Build ONLY the [hero screen name] using the existing tokens and [component library/headless primitives].
Rules:
- Semantic HTML first; real <button>, <a>, <label>, headings in order, landmarks.
- Use real content from [file/section]. No lorem ipsum, no placeholder charts.
- One primary action per view. Clear hierarchy: describe in comments-free code but explain in your reply what the 1st, 2nd and 3rd things the eye sees are.
- Responsive from 360px up. No fixed widths on text containers; max line length 75ch.
- Implement hover, focus-visible, active, disabled, loading for every interactive element.
- Motion: respect prefers-reduced-motion; animate transform/opacity only; one orchestrated load sequence max.

When done: run the app, take screenshots at 360, 768 and 1440 widths, and review them against the brief.
List five specific flaws you see in your own screenshots (spacing, hierarchy, contrast, alignment, content), then fix them and re-screenshot.
Do not say it is finished until the screenshots and a keyboard-only tab-through check support it.
```

---

### A.6 State matrix and accessibility pass

```text
For [screen], produce a state matrix and implement every cell:
| Component | Default | Hover | Focus-visible | Active | Disabled | Loading | Empty | Error | Success | Long-content |
Use realistic edge data: 80-character names, 10,000 rows, zero rows, non-Latin text, missing images, slow network.
Show each state in /styleguide or in Storybook-style fixtures.

Then run an accessibility pass:
- Run axe (or Lighthouse accessibility) and list every issue with the fix.
- Tab through the whole screen: report focus order, any trap, any element without a visible focus indicator.
- Verify contrast for all text and UI boundaries (4.5:1 and 3:1).
- Confirm touch targets >= 24x24 CSS px (44px preferred on touch), forms have labels and error text tied to fields,
  drag actions have alternatives, and reduced motion is honored.
Fix everything, re-run, and show the numbers before and after.
```

---

### A.7 Consistency prompt for later screens

```text
Build [screen 2]. Before writing code:
1. List the existing components and tokens from the repo that you will REUSE. Do not create a new component if one exists.
2. List any new component you need and why existing ones are insufficient.
3. Confirm you will use only existing tokens; if a token is missing, propose it and update tokens.md rather than hard-coding.
After building, diff against [screen 1]: check header, spacing, button hierarchy, form patterns, empty state tone, and motion for consistency, and fix mismatches.
```

---

### A.8 Critique, polish and anti-slop prompts

#### 8.1 Self-critique as a design reviewer
```text
Act as a senior product designer doing a ruthless critique of the attached screenshots against DESIGN-BRIEF.md.
Score 1-5 on: hierarchy, typography, color/contrast, spacing/rhythm, consistency, originality, state coverage,
accessibility, microcopy. For each score below 4, give (a) the exact problem, (b) why it hurts users, (c) a concrete CSS/markup fix.
Flag anything that looks like generic AI output (default fonts, gradient accents, equal-card rows, icon tiles, uniform radius, filler copy).
Then implement the top 5 fixes by impact.
```

#### 8.2 Usability review using heuristics
```text
Review [flow] against Nielsen's 10 heuristics. For each heuristic list violations with the screen and element,
severity (cosmetic/minor/major/critical), and a fix. Pay special attention to system status, error prevention and recovery, and user control.
```

#### 8.3 Anti-slop sweep
```text
Scan the UI for these defaults and replace each with a decision from DESIGN-BRIEF.md (do not just delete):
Inter/Roboto/system font; purple or indigo gradient; centered hero + logo strip; three equal rounded cards;
icons in tinted squares; blurred blobs/dot grids; same radius and shadow everywhere; nested cards; ALL-CAPS eyebrow above every heading;
vague headlines ("Build faster", "All-in-one"); uniform spacing; decorative emoji. Show before/after for each replacement.
```

#### 8.4 Reference-based alignment
```text
Here is a screenshot/URL of a reference: [ref]. Do not copy it. Describe, in measurable terms, the decisions that create its feel:
type sizes and weights, line-height, spacing scale, grid, color ratios (e.g., 90% neutral / 8% surface / 2% accent), border/shadow use,
motion durations and easing, and information density. Then tell me which of these decisions fit my brief and which do not, and apply the ones that do via tokens.
```

#### 8.5 Make it quieter, bolder, or more specific
```text
The screen feels [too generic / too busy / too timid]. Change exactly ONE of: type scale contrast, color ratio, spacing rhythm, or layout structure.
Explain the change, apply it, and show before/after screenshots. Do not touch anything else.
```

#### 8.6 Microcopy pass
```text
Rewrite all UI text: buttons start with a verb describing the outcome; errors say what happened and how to fix it; empty states say what belongs here and the next step;
no jargon; no exclamation marks; keep to voice rules in the brief. Give a table of old vs new copy.
```

#### 8.7 Performance and robustness
```text
Run Lighthouse (mobile). Report LCP, INP, CLS, and accessibility score. Fix the three largest causes. Check images have width/height and modern formats,
fonts use font-display: swap and are subset, and no render-blocking scripts. Show before/after numbers.
```

---

### A.9 LLM audit prompt

```text
You are a senior accessibility and UX auditor. Audit [URL or route list] against WCAG 2.2 AA, the research-based rules below, and the Core Web Vitals thresholds.
Do not guess; use tools. Steps:
1. Run the app. With Playwright, capture screenshots at 360, 768, 1440 px, and at 200% text and 400% zoom (320 CSS px equivalent).
2. Run axe-core and Lighthouse (mobile). Report violations with selector, WCAG criterion, and fix.
3. Perform a keyboard-only walkthrough of [key flows]: list focus order problems, traps, missing visible focus, and anything hidden by sticky UI.
4. Check contrast for all text and UI states including hover, focus, disabled, error, and dark mode.
5. Check target sizes (≥ 24 CSS px; flag < 44 px on touch), spacing, and drag-only interactions.
6. Review forms: labels, hints, autocomplete, errors (text, association, summary), redundant entry, authentication method, data preservation.
7. Review states: empty, loading, error, offline, long content. Flag blank loading screens and layout shift.
8. Review cognitive load: primary action per view, choice counts, grouping, plain language, consistency, memory demands across steps, dark patterns.
9. Review scanning: is the key message and next step in the first screenful and first two lines? Do headings and lists support scanning? Is anything important styled like an ad?
10. Measure performance: LCP, INP (or proxy by long tasks), CLS; list the top 3 causes and fixes.
Output a table: ID, severity (blocker/major/minor), where, evidence (screenshot or tool output), criterion or rule, fix (code-level). Then fix blockers and majors, re-run the same checks, and show before/after results. State what you could not verify (screen reader behavior, real-device performance, real-user data).
```


### A.10 Accessible custom widgets: pattern prompt

```text
Build [dialog | combobox | tabs | menu | accordion] for [stack]. Prefer Radix Primitives or React Aria; do not hand-roll focus management.
Before coding, list in 6 bullets the keyboard interactions and ARIA roles/states this pattern requires per the W3C ARIA Authoring Practices Guide (Tab/Shift+Tab, arrow keys, Escape, Home/End where relevant; focus moves in on open, returns to the trigger on close; focus is trapped only in modal dialogs).
Then implement, and write Playwright tests that perform those keystrokes and assert focus location and ARIA state. Run axe. Report anything you could not verify (screen reader announcements).
```

### A.11 Dependency and API honesty

```text
Use only packages already in package.json unless you ask first. If you need a new dependency, stop and give: name, why, weekly downloads, last publish date, license, and the official docs URL. Never invent package names, props, or CLI flags. If unsure whether an API exists in the installed version, read it from node_modules or the official docs and quote the line. After edits run typecheck, lint and tests, and paste the output.
```

### A.12 Security pass

```text
Review the diff for: unescaped user input rendered as HTML (dangerouslySetInnerHTML, innerHTML, unsafeHTML), URLs from users used in href or src without scheme validation, secrets or keys in client code, missing server-side validation (client checks are not enough), unsafe third-party scripts, missing CSP or Trusted Types where the app handles untrusted content, and cookies without HttpOnly, Secure, SameSite. Output a table: file, line, issue, severity, fix. Do not claim the code is secure; list what you did not check.
```

### A.13 Rubric critique (hidden-rubric style)

```text
Before building, write a 5-item rubric for what "excellent" means for this screen (hierarchy, fit to brief, accessibility, states, copy). After building, score your own output 1-5 per item with evidence from screenshots, list the lowest two, and fix only those. Then stop and wait for human review. A human, not you, decides whether the rubric was met.
```

### A.14 Translate vague words into instructions

| You say | Say this instead |
|---|---|
| "Make it modern / clean" | "One type family, 4 sizes, 90% neutral palette with a single accent, 8px grid, no gradients, 1px borders at 8% opacity." |
| "Make it pop" | "Increase contrast between the primary action and everything else; use the accent only on the primary button and key data." |
| "Make it premium" | "Larger type contrast (display 56-96px vs 16px body), more whitespace (double current padding), restrained color, slow 300ms ease-out transitions." |
| "Make it fun" | "Rounded display type, saturated palette of 3 colors, playful empty-state illustrations, spring-like motion on success only." |
| "It feels cluttered" | "Reduce visible elements by half; group by proximity; move secondary actions into a menu; remove all borders you can replace with spacing." |
| "It feels flat / boring" | "Add hierarchy with size and weight, a surface elevation system, and one orchestrated entrance animation." |
| "It looks like AI" | "Run the anti-slop sweep and replace each default with a decision from the brief." |
| "Make it responsive" | "Design mobile-first at 360px; verify at 360/768/1024/1440; no horizontal scroll; stacking order matches reading priority; touch targets >= 44px." |
| "Make it accessible" | "WCAG 2.2 AA; semantic HTML; keyboard-complete; visible focus; 4.5:1 contrast; labels and error text tied to fields; reduced motion respected; show axe results." |
| "Match our brand" | "Use only tokens in tokens.css derived from the brand file; do not introduce new colors or fonts." |
| "Something feels off" | "Screenshot it, list misalignments, inconsistent spacings, and hierarchy conflicts with pixel values, then fix." |

---

### A.15 Reusable system block (save as a rule or skill)

```text
You are building frontend UI. Follow these rules in every response.

Process: read DESIGN-BRIEF.md and tokens.css first. Ask me questions only when the answer would materially change the work; otherwise state an assumption and continue.
Never start with visual styling before purpose, flow, and structure are clear.

Design: commit to ONE coherent direction defined by the brief. Do not drift into default AI aesthetics: avoid Inter/Roboto/system fonts as a default, purple-indigo gradients on white,
centered hero + three equal cards, icon-in-tinted-square tiles, blurred blobs, uniform radius, nested cards, filler copy. Do not swap one default for another without a brief-based reason.
Typography carries hierarchy (size, weight, spacing), color is restrained (neutrals + one accent + semantics), spacing follows the scale, motion is purposeful.

Engineering: semantic HTML; native elements first; headless accessible primitives restyled with tokens; no hard-coded colors, fonts, or magic numbers; reuse existing components.

Quality: every interactive element has hover, focus-visible, active, disabled, loading; every data view has empty, loading, error, long-content states; WCAG 2.2 AA; reduced motion;
responsive at 360/768/1024/1440.

Verification: run it, screenshot at 360/768/1440, tab through with keyboard, run axe/Lighthouse, and report real results. State what you could not verify. Do not claim done otherwise.
```

---

### A.16 Per-task prompt skeleton

```text
GOAL: [one sentence]
USER + CONTEXT: [who, device, situation]
PRIMARY TASK: [what must be easy]
SCREEN(S): [list]
CONTENT: [real copy/data or file]
STYLE: [reference URLs + what to borrow]; AVOID: [list]
SYSTEM: use tokens.css and existing components; no new colors/fonts
STATES: [which]
A11Y: WCAG 2.2 AA, keyboard-complete
DONE WHEN: screenshots at 360/768/1440, keyboard walkthrough, axe results, no hard-coded values
```

---

### A.17 Five-minute review checklist per screen

- [ ] Squint test: can I see the one most important thing?
- [ ] Is there exactly one primary action?
- [ ] Do related things sit closer together than unrelated things?
- [ ] Count fonts (<= 2), sizes (<= 6 in common use), colors (neutrals + 1 accent + semantics), radii (<= 3).
- [ ] Is every text/background pair readable (check with a contrast tool)?
- [ ] Tab through: always see where focus is? Everything reachable?
- [ ] Any state missing: empty, loading, error, disabled?
- [ ] Resize to phone width: still usable, no sideways scroll?
- [ ] Is the copy specific to this product, or could it sell anything?
- [ ] Does it look like every other AI-built app? What one decision makes it ours?

## Appendix B: Checklists

### B.1 Master audit checklist (per screen and flow)

#### A. Compliance (WCAG 2.2 AA)
- [ ] Semantic landmarks, one `h1`, no skipped headings; real buttons and links
- [ ] All functionality by keyboard; no traps; logical order; skip link
- [ ] Visible focus, ≥ 3:1, not hidden by sticky UI (2.4.11)
- [ ] Contrast: text 4.5:1 (large 3:1); UI components and focus 3:1; verified in dark mode and hover/disabled/error states
- [ ] Not color alone; text alternatives; captions and transcripts
- [ ] Reflow at 320 px / 400% zoom; text spacing overrides; 200% text resize
- [ ] Targets ≥ 24×24 CSS px (2.5.8); drag alternatives (2.5.7); pointer cancellation
- [ ] `lang` set; consistent navigation and help (3.2.6)
- [ ] Forms: labels, instructions, error identification and suggestion, autocomplete, no redundant entry (3.3.7), accessible authentication (3.3.8)
- [ ] Status messages announced (4.1.3); names, roles, values (4.1.2)
- [ ] Reduced motion honored; no flashing; pause for moving content
- [ ] axe/Lighthouse clean; keyboard and screen-reader walkthrough done; real-user feedback channel exists
- [ ] Third-party widgets, PDFs, and embedded content reviewed; accessibility statement and contact present

#### B. Cognitive load and frustration
- [ ] One primary action per view; choices grouped and ranked
- [ ] Essentials first; advanced behind disclosure
- [ ] Nothing the user must remember across screens; persistent summary in multi-step flows
- [ ] Related info adjacent (labels, units, errors); no split attention
- [ ] Familiar patterns and consistent labels
- [ ] Plain language; front-loaded headings; short paragraphs and lists
- [ ] Every state designed: empty, loading, error, success, offline, long content
- [ ] Errors say what, why, and fix; user input preserved
- [ ] Undo, cancel, and back available; destructive actions confirmed with specific labels
- [ ] Time limits warned and extendable; autosave
- [ ] No dark patterns: symmetric choices, easy cancel, honest urgency, upfront pricing

#### C. Attention and scanning
- [ ] Key message and next step in the first screen and first two lines
- [ ] Headings, bold lead-ins, bullets encourage layer-cake scanning rather than F
- [ ] Important content not styled or placed like ads
- [ ] Clear grouping boundaries; one dominant region
- [ ] First-glance test (1-5 s): can a stranger name the page type and primary action?

#### D. Performance
- [ ] LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at p75 in field data (mobile and desktop)
- [ ] Input feedback within 100 ms; long operations show progress; >10 s has percent and cancel
- [ ] No blank loading screens; skeleton matches layout
- [ ] Images sized, modern format, LCP image prioritized; fonts optimized; JS split
- [ ] Layout reserved for dynamic content
- [ ] Tested on a mid-range phone with throttled CPU and network

#### E. Input, reading, forms
- [ ] Touch targets ~44px; larger for older or motor-impaired audiences
- [ ] 16px+ text, 1.5 line-height, ~45-75 ch measure; zoom and user settings respected
- [ ] One-column forms, top labels, correct input types, inline validation after field completion
- [ ] Mobile keyboard types correct; paste allowed

#### F. Measure with people
- [ ] 5 users per key segment, including AT users where relevant
- [ ] Task success, time, errors; SUS or UEQ-S; NASA-TLX for heavy tasks (instrument facts: [13](frontend-knowledge-base/13-ux-research-methods-and-measurement.md))
- [ ] Decision log of fixes and retests

### B.2 Pre-ship legal and compliance checklist (judgment; not legal advice)

- [ ] Know which regimes apply: ADA Title II (public entity) or III (business), Section 504 (HHS funding), Section 508 (federal), EAA (EU market), state laws
- [ ] Target WCAG 2.2 AA; confirm the contractual or legal minimum (2.1 AA for Title II and HHS 504)
- [ ] Accessibility statement with a working contact and response commitment
- [ ] VPAT/ACR if selling to government or enterprise (honest, tested)
- [ ] Third-party content, PDFs, and vendors reviewed; contracts require conformance
- [ ] No accessibility overlay used as the fix
- [ ] Consent banner: reject as prominent as accept; no pre-ticked boxes; honor Global Privacy Control where required
- [ ] No dark patterns in cancellation, pricing, urgency; cancellation as easy as sign-up
- [ ] Records: audit reports, remediation log, test dates

### B.3 Review checklist for LLM-generated code

- [ ] It runs; typecheck, lint, tests pass
- [ ] Every dependency exists, is maintained, and is licensed acceptably
- [ ] Every color, size, and spacing comes from tokens (grep for raw hex and px)
- [ ] Real content, no invented statistics, testimonials, or logos
- [ ] Native elements first; custom widgets use a primitive library
- [ ] Keyboard-only walkthrough done by a human; axe clean; screen reader spot check
- [ ] Every state exists (empty, loading, error, disabled, long content, offline)
- [ ] Security pass (A.12); no secrets client-side
- [ ] Screenshots at 375, 768, 1280 in both themes reviewed by a human
- [ ] Could this page belong to any other company? If yes, revise the direction

## Appendix C: Source log

**Grades:** **A** = primary law, regulation, standard, regulator order, or peer-reviewed/open primary dataset read directly. **B** = reputable research organization or peer-reviewed article/abstract, or well-established industry research. **C** = official vendor or standards-body documentation, practitioner source with data. **D** = secondary summaries, aggregators, blogs, search-result excerpts, unverified. "Session" = **R** (re-fetched or re-searched during the 2026-11-13 refresh) or **E** (read in the earlier research session and carried over; not re-checked).

| # | Grade | Source (URL) | Claim used | Effect on advice | Session |
|---|---|---|---|---|---|
| 1 | A | [Federal Register, DOJ ADA Title II web rule](https://www.federalregister.gov/documents/2024/04/24/2024-07758/nondiscrimination-on-the-basis-of-disability-accessibility-of-web-information-and-services-of-state) and 2026 interim final rule (FR 2026-07663), via [ADA.gov](https://www.ada.gov/resources/web-rule-first-steps/) | WCAG 2.1 AA; dates April 26, 2027 (large) and April 26, 2028 (small and special districts) | Dates in 7.2; recommends 2.2 AA anyway | R |
| 2 | D/C | Secondary law-firm reporting on possible DOJ reconsideration of Title II rule | DOJ stated it may reopen the rule | Caveat on Title II dates | R |
| 3 | A | [HHS 45 CFR 84.84](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-84/subpart-I/section-84.84) and HHS May 2026 notice | Section 504 web rule, WCAG 2.1 AA, new compliance dates | Dates in 7.3 | R |
| 4 | A | [Access Board, Revised 508 Standards](https://www.access-board.gov/ict/) / [Section508.gov](https://www.section508.gov/) | WCAG 2.0 AA for federal ICT | 7.4 | R |
| 5 | A | [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) and [What's New](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/) | 86 SC; 4.1.1 removed; new AA criteria | Build target | R |
| 6 | A | [W3C WCAG 3.0 Working Draft](https://www.w3.org/TR/wcag-3.0/) and AG WG charter | Draft only; APCA "yet to be determined" | Do not adopt for conformance | R |
| 7 | A | [FTC order against accessiBe (2025)](https://search.ftc.gov/system/files/ftc_gov/pdf/d-o.222_3156_-_accessibe_final_consent_package_without_signatures-2.pdf) | $1M; deceptive claims that an AI overlay makes sites compliant | Risk-map row; never rely on overlays | R |
| 8 | A | [FTC, Bringing Dark Patterns to Light (2022)](https://search.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf) | Deceptive design enforcement view | 16.5 | E |
| 9 | A/B | EU: European Accessibility Act (Directive 2019/882); EN 301 549 v3.2.1, v4.1.1 status via [ETSI](https://www.etsi.org/) | EAA in force since June 28, 2025; harmonised standard is v3.2.1; v4.1.1 published (status of citation under review) | 7.6; build to 2.2 | R |
| 10 | B | [WebAIM Million 2026](https://webaim.org/projects/million/) | 95.9% of home pages with detectable failures; ARIA correlation | Exec summary; risk map | R |
| 11 | B | [WebAIM Screen Reader User Survey #11](https://webaim.org/projects/screenreadersurvey11/) | Usage and heading navigation data | 8.6 | R |
| 12 | B | UsableNet/other litigation tallies | Title III suits continue (counts vary by source) | 7.5 | R/D |
| 13 | C | [web.dev Core Web Vitals](https://web.dev/articles/vitals) and [Chrome for Developers CrUX release notes](https://developer.chrome.com/docs/crux) | LCP 2.5 s, INP 200 ms, CLS 0.1 unchanged; soft-navigation experimental metrics | 11.2 | R |
| 14 | C | [Google Search Central, page experience](https://developers.google.com/search/docs/appearance/page-experience) | Vitals "aligns with" ranking systems; no weight stated | 11.2 | R |
| 15 | B | Nielsen Norman Group: [F-pattern](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content-discovered/), [scanning patterns](https://www.nngroup.com/articles/text-scanning-patterns-eyetracking/), [scrolling and attention](https://www.nngroup.com/articles/scrolling-and-attention/), [response times](https://www.nngroup.com/articles/response-times-3-important-limits/), [older adults](https://www.nngroup.com/articles/usability-for-senior-citizens/), [chatbots](https://www.nngroup.com/articles/chatbots/) | Eye-tracking and timing findings | Chapters 9-12 | E |
| 16 | A- | Cowan 2001 [(PubMed 11515286)](https://pubmed.ncbi.nlm.nih.gov/11515286/), 2010 [(PMC2864034)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2864034/) | About 4 chunks in working memory | Chapter 9 | E |
| 17 | A- | [Web pages: what can you see in a single fixation? (PMC5945715)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5945715/) | Page gist in about 120 ms | Chapter 10 | E |
| 18 | A- | [Shorter lines facilitate reading in those who struggle (PMC3734020)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3734020/); [font size for older adults review (PMC9376262)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9376262/) | Line length and font size evidence | 12.2 | E |
| 19 | B | Findlater et al., [CHI 2017](https://makeabilitylab.cs.washington.edu/media/publications/Findlater_ComparingTouchscreenAndMouseInputPerformanceByPeopleWithAndWithoutUpperBodyMotorImpairments_CHI2017.pdf) | Touch error rates by target size | 12.1 | E |
| 20 | B | Lindgaard 2006 [(doi 10.1080/01449290500330448)](https://doi.org/10.1080/01449290500330448); [Reinecke et al. CHI 2013](https://eecs.harvard.edu/~kgajos/papers/2013/reinecke13predicting.shtml); [Fogg 2003](https://credibility.stanford.edu/pdf/How_Do_People_Evaluate_a_Web_Site%27s_Credibility_v37.pdf) | Instant appeal, predicted first impressions, credibility cues | 13.1 | E |
| 21 | B | [Human Factors 2009 progress bars (doi 10.1177/0018720809345684)](https://doi.org/10.1177/0018720809345684); [IHC 2025 (doi 10.5753/ihc_estendido.2025.13255)](https://doi.org/10.5753/ihc_estendido.2025.13255) | Progress bars and skeleton screens | 11.3 | E |
| 22 | B | Utz et al. [CCS 2019 (doi 10.1145/3319535.3354212)](https://dl.acm.org/doi/10.1145/3319535.3354212); Mathur et al. [(arXiv 1907.07032)](https://arxiv.org/html/1907.07032v2) | Consent nudging; dark-pattern prevalence | 16.5 | E |
| 23 | B | Kohavi et al. [rules of thumb](https://exp-platform.com/Documents/2014-08-27ExperimentersRulesOfthumbKDD.pdf), [pitfalls](https://exp-platform.com/Documents/2017-05-17EmetricsControlledExperimentsPitfallsKohaviNR.pdf) | SRM, Twyman's law | 17.3 | E |
| 24 | B | Faulkner 2003 (Behavior Research Methods); Brooke SUS; Hart and Staveland 1988 [(NASA archive)](https://archive.org/details/nasa_techdoc_20000004342) | Sample-size and instrument facts | 17.2, 17.4 | E |
| 25 | B | [Amershi et al., CHI 2019](https://dl.acm.org/doi/fullHtml/10.1145/3290605.3300233); [Google PAIR](https://pair.withgoogle.com/guidebook/) | 18 human-AI guidelines | 18.2 | E |
| 26 | B | [Sclar et al., arXiv 2310.11324](https://arxiv.org/abs/2310.11324); [Zheng et al., EMNLP Findings 2024](https://aclanthology.org/2024.findings-emnlp.888/); [Wei et al.](https://arxiv.org/abs/2201.11903); [Kojima et al.](https://arxiv.org/abs/2205.11916); [Huang et al.](https://arxiv.org/abs/2310.01798); [Madaan et al. (Self-Refine)](https://arxiv.org/abs/2303.17651); [Liu et al. Lost in the Middle](https://arxiv.org/abs/2307.03172); [Zheng et al. LLM-as-judge](https://arxiv.org/abs/2306.05685) | Prompting evidence ledger | 19.2 | E |
| 27 | B | [Design2Code (arXiv 2403.03163)](https://arxiv.org/html/2403.03163v3) | Screenshot-to-code benchmarks; text-augmented prompting; visual revision model-dependent | 19.2, 20.2 | E |
| 28 | B/C | [METR 2025 RCT (arXiv 2507.09089)](https://arxiv.org/abs/2507.09089) and METR late-2025 follow-up | 19% slower early 2025; follow-up unreliable and unsettled | 19.2 | R |
| 29 | B | [Pearce et al. (arXiv 2108.09293)](https://arxiv.org/abs/2108.09293); package-hallucination study (576,000 samples, arXiv 2406.10279) | Insecure and invented code | 19.2 | E |
| 30 | C | [Anthropic prompt engineering docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview); [Anthropic frontend design skill](https://github.com/anthropics/skills/tree/main/skills/frontend-design) (SKILL.md read directly); [blog](https://claude.com/blog/improving-frontend-design-through-skills) (fetch timed out, not read) | Vendor guidance; skill behavior | 5, 19.3, 20.1 | R |
| 31 | C/D | [Gemini prompting strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies), via search excerpts; Google Cloud Gemini 3 guide | Examples, negatives, over-analysis | 19.3 | R (excerpt) |
| 32 | C | [OpenAI frontend and prompting guidance](https://platform.openai.com/docs/guides/prompt-engineering) | Evals, pin versions, library recommendations | 19.3 | E |
| 33 | C | [Cursor rules docs](https://cursor.com/docs/context/rules); [Claude Code memory docs](https://docs.anthropic.com/en/docs/claude-code/memory); [Figma MCP docs](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/) | Rules-file behavior; MCP | 19.4 | E |
| 34 | A/B | GitHub repository API for the skills in 20.1; Hugging Face Hub model pages in 20.2; [arena.ai WebDev leaderboard](https://arena.ai/leaderboard/code/webdev?stream=top) | Stars, licenses, sizes, Elo on 2026-11-11 / 11-13 | Chapter 20 and 5.4 | R |
| 35 | C | [Design Tokens Community Group format](https://www.designtokens.org/); [Radix philosophy](https://github.com/radix-ui/primitives/blob/main/philosophy.md); [Storybook](https://storybook.js.org/docs/writing-tests/accessibility-testing); [Playwright snapshots](https://playwright.dev/docs/test-snapshots) | Token spec, headless components, testing | 14 | E |
| 36 | C | [MDN container queries](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@container); [MDN logical properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Logical_properties_and_values); [W3C i18n text expansion](https://www.w3.org/International/articles/article-text-size) | Responsive and i18n facts | 15 | E |
| 37 | C | [Google JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics); [OWASP XSS](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html) and [CSP](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html) cheat sheets; web.dev rendering articles | Rendering, SEO, security | 16 | E |
| 38 | B | Deque coverage study (57% by volume; criterion-level coverage lower); Storybook a11y addon wording | Automated testing limits | 8.7, 22 | E |
| 39 | B/D | 2026 studies on accessibility of LLM-generated code (including AXIS-Bench; abstract/summary level) | Basics good, ARIA and widgets weak, feedback helps | 8.5 | R (summary) |
| 40 | D | Aggregator posts on skills ("best skills" lists, comparison sites) | Tool names only | Marked unverified in 20.1 | R |

## Appendix D: Glossary and common misconceptions

### D.1 Glossary

| Term | Plain meaning |
|---|---|
| **A11y** | Short for accessibility (11 letters between a and y) |
| **ADA** | Americans with Disabilities Act; Title II covers state and local governments, Title III covers businesses open to the public |
| **APCA** | A newer text-contrast calculation; not in any standard |
| **ARIA** | Attributes that tell assistive technology about custom widgets; first rule: use native HTML if you can |
| **Assistive technology (AT)** | Screen readers, switches, magnifiers, voice control |
| **CLS / INP / LCP** | Core Web Vitals: layout shift, interaction responsiveness, main content load time |
| **Cognitive load** | Mental effort demanded by a task or interface |
| **Container query** | CSS that styles a component by the size of its container |
| **CrUX** | Chrome's public dataset of real-user performance |
| **CSP** | A header limiting which scripts a page may run |
| **Design tokens** | Named design decisions (colors, sizes) stored as data |
| **Dark pattern / deceptive design** | An interface that tricks users against their interest |
| **DTCG** | Design Tokens Community Group |
| **EAA / EN 301 549** | EU accessibility law / its technical standard |
| **Fitts's law** | Pointing time depends on target size and distance |
| **Focus (visible)** | The highlighted element that receives keyboard input |
| **Gestalt** | Principles of visual grouping (proximity, similarity, common region) |
| **Headless component** | Behavior and accessibility without styles |
| **Hick's law** | Decision time grows with number of choices (limits apply) |
| **Hydration** | Making server-rendered HTML interactive in the browser |
| **i18n / l10n** | Internationalization / localization |
| **Landmark** | Page region (`header`, `nav`, `main`) that assistive technology can jump to |
| **Live region** | An element whose changes screen readers announce |
| **LLM** | Large language model |
| **MCP** | Model Context Protocol; a way to connect agents to tools |
| **p75** | 75th percentile: three of four users are as good or better |
| **Reflow** | Content fitting a 320 px wide viewport without two-way scrolling |
| **SC** | Success criterion (a testable WCAG rule) |
| **SRM** | Sample ratio mismatch in A/B tests |
| **SSR / SSG / CSR** | Server-side, static, client-side rendering |
| **Skill (agent)** | A file of instructions an agent loads for a task |
| **SUS / NASA-TLX / UEQ-S** | Questionnaires for usability, workload, user experience |
| **Trusted Types** | Browser feature blocking unsafe string-to-HTML assignment |
| **VPAT / ACR** | A vendor's accessibility conformance report |
| **WCAG** | Web Content Accessibility Guidelines |

### D.2 Common misconceptions

| Myth | Better statement |
|---|---|
| "AI UIs look the same because the models are bad." | Averaging over the web is how they work; constraints and references fix most of it |
| "A banned-word list removes slop." | The next default moves in; pair bans with replacements |
| "Inter is the problem." | Linear ships Inter; systems matter more than fonts |
| "axe clean means accessible." | It catches a subset; manual testing is required |
| "WCAG 2.2 is required by the ADA." | Title II sets 2.1 AA; build to 2.2 anyway |
| "An overlay makes me compliant." | FTC acted against such claims; fix the code |
| "Users read the F-pattern." | Poorly structured text produces it; structure changes it |
| "Miller's 7±2 is the limit." | Later work suggests about 4 chunks |
| "Five users find 85% of problems." | Averages; real groups vary widely; and five cannot measure rates |
| "Dark mode reduces eye strain." | Not shown by the sources I read |
| "Skeleton screens always beat spinners." | Evidence is mixed; blank pages are worst |
| "Core Web Vitals are a big ranking factor." | Google gives no weight; they matter for users |
| "Persona prompts make output expert." | No accuracy gain shown on tasks tested |
| "44 px is the WCAG minimum." | WCAG AA minimum is 24 CSS px; 44 is platform guidance |
| "More ARIA is more accessible." | Pages with ARIA had more detected errors; use native first |

## Appendix E: Learning path

| Stage | Read or do | Output |
|---|---|---|
| **1. Orient (half a day)** | Sections 1-6 of this guide; skim 7 | You can explain slop, WCAG AA, and the brief |
| **2. Practice with a constraint (1-2 days)** | Fill A.1-A.2; build one screen with A.5; run axe; tab through it | A brief, a token file, one audited screen |
| **3. Foundations (week 1-2)** | Chapters 8-10, 12, 13; NN/g articles in Appendix C row 15; WebAIM and W3C WAI tutorials; try a screen reader (NVDA on Windows; VoiceOver on macOS) | You can find 10 issues axe misses |
| **4. Engineering (week 2-4)** | Chapters 11, 14-16; web.dev Learn; Radix docs; Playwright tutorial | CI with axe, Lighthouse CI, visual snapshots |
| **5. Research (month 2)** | Chapter 17; run five usability sessions including an assistive-technology user; compute SUS | A findings log with fixes and retests |
| **6. Law and policy (as needed)** | Chapter 7 and primary sources in Appendix C rows 1-9; talk to counsel | An accessibility statement and a conformance plan |
| **7. LLM workflow (ongoing)** | Chapter 19; build your own eval (19.6) | A prompt and rules set whose benefit you measured |

Free, highly regarded starting resources: W3C WAI tutorials and WCAG quick reference, WebAIM articles, NN/g free articles, web.dev Learn, GOV.UK and USWDS design systems, MDN, *Refactoring UI* (paid book), Laws of UX (free site).

## Appendix F: Runtime refresh and corrections log

Refreshed on 2026-11-13 using web search, page fetches, GitHub API, Hugging Face Hub, and arena.ai.

### F.1 Facts re-verified and changed

| Area | Earlier statement | Now | Where changed |
|---|---|---|---|
| WebAIM Million | Earlier figure (about 94.8%, 2025) | **95.9%** (February 2026), worse than 2025 | Exec summary, KB README |
| WebAIM survey | Survey #10 numbers | Survey #11 numbers (see 8.6) | 8.6, KB 14 |
| ADA Title II | Dates stated without caveat | Dates April 26, 2027 / 2028 stand; DOJ has said it may reopen the rule | 7.2, KB 01 |
| HHS 504 | Dates | Updated per HHS May 2026 notice | 7.3 |
| FTC overlay case | Treated as news item | Graded A (order) | 7.5, risk map |
| EU standard | Single version cited | EN 301 549 v3.2.1 is harmonised; v4.1.1 exists and its status is flagged | 7.6, KB 01 |
| Core Web Vitals | "Check for changes" | Thresholds unchanged; soft-navigation experimental metrics added; ranking wording resolved to Google's | 11.2, KB 05, 12 |
| Arena leaderboard | Older Elo values | Snapshot 2026-11-11 (see 5.4, 20.2) | 5.4, 20.2, KB 04 |
| Models | Older sizes | Kimi K3.1 Pro about 2.78T; DeepSeek V4.1 Flash about 763B; Qwen3.8-27B Apache-2.0 | 20.2, KB 04 |
| Skills | Earlier stars | Repository API values 2026-11-13; frontend-design skill now plans, reviews against the brief, lists 2026 defaults | 20.1, KB 04, 01 |
| METR | Early 2025 result only | Added late-2025 follow-up; unsettled | 19.2, KB 15 |
| Gemini docs | Unread gap | Read via excerpts; added to vendor table | 19.3, KB 15, 17 |
| Generated-code accessibility | "Not accessible by default" | Mixed evidence (2026 studies) | 8.5, KB 14, 15 |

### F.2 Errors found in the earlier files

1. **Rubric arithmetic** in [frontend-design/01](frontend-design/01-research-report.md) section 6: recomputed averages 2.3 / 3.0 / 3.9 / 4.95 (earlier: 2.4 / ... / 4.9). Corrected there and in this guide.
2. **Stale "unverified" items** (Gemini docs, CWV ranking) resolved or re-labeled.
3. **Ambiguity:** earlier text implied a single "Brooke 1986" SUS date; sources conflict (1996 chapter vs 1986 origin), so cite 1996.
4. **Old "fingerprint":** purple gradients and Inter are no longer the main tell; cream, serif display, terracotta accents and related defaults are listed in the official skill itself.

### F.3 Not verified in this refresh

Taste Skill, Emil Kowalski skills, unslop, Awwwards MCP, Stitch and Figma skills; Tesslate model currency; PACE and AXIS-Bench full text; Section 508 refresh primary text; DOJ reopening primary text; all claims marked **(judgment)**.

## Appendix G: Deep-dive file map

| This guide | Deep dive |
|---|---|
| 5. Why LLM UIs converge | [frontend-design/01](frontend-design/01-research-report.md), [02](frontend-design/02-education-guide.md) |
| 6. Fundamentals | [frontend-design/02](frontend-design/02-education-guide.md), [KB 03](frontend-knowledge-base/03-cognitive-load-and-frustration.md) |
| 7. Law | [KB 01](frontend-knowledge-base/01-legal-and-compliance.md) |
| 8. Accessibility engineering | [KB 02](frontend-knowledge-base/02-accessibility-engineering.md) |
| 9. Cognitive load | [KB 03](frontend-knowledge-base/03-cognitive-load-and-frustration.md) |
| 10. Eye tracking | [KB 04](frontend-knowledge-base/04-eye-tracking-and-attention.md) |
| 11. Performance | [KB 05](frontend-knowledge-base/05-performance-and-perceived-speed.md) |
| 12. Input, reading, forms | [KB 06](frontend-knowledge-base/06-input-reading-and-forms.md) |
| 13. Visual design | [KB 09](frontend-knowledge-base/09-visual-design-fundamentals.md) |
| 14. Design systems | [KB 10](frontend-knowledge-base/10-design-systems-and-tokens.md) |
| 15. Responsive and i18n | [KB 11](frontend-knowledge-base/11-responsive-mobile-and-localization.md) |
| 16. Engineering | [KB 12](frontend-knowledge-base/12-frontend-engineering-issues.md) |
| 17. Research methods | [KB 13](frontend-knowledge-base/13-ux-research-methods-and-measurement.md) |
| 18. Inclusive and AI-UX | [KB 14](frontend-knowledge-base/14-inclusive-design-ai-ux-and-wcag-check.md) |
| 19. Prompting | [KB 15](frontend-knowledge-base/15-llm-prompting-for-frontend.md), [frontend-design/03](frontend-design/03-prompt-template-kit.md) |
| 20. Tools and models | [frontend-design/04](frontend-design/04-tools-plugins-and-models.md) |
| 21 / App. B. Audit | [KB 08](frontend-knowledge-base/08-audit-checklist.md) |
| App. C. Sources | [KB 07](frontend-knowledge-base/07-research-library.md) |
| App. D-E. Glossary, learning path | [KB 16](frontend-knowledge-base/16-glossary-and-learning-path.md) |
| 24. Open problems | [KB 17](frontend-knowledge-base/17-issues-and-open-problems.md) |
