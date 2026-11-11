# Why LLM-Built Frontends All Look the Same, and How Far They Can Get

Research date: 2026-11-11. Everything marked **(judgment)** is my inference, not a sourced fact. Leaderboard numbers move weekly; re-check them before relying on them.

---

## 1. Bottom line

1. **The sameness is structural, not a bug.** A model picks the most probable continuation. For an open design request, the most probable page is the average of the public web: Inter, an indigo/purple gradient, a centered hero, three rounded cards with icons, soft shadows. Anthropic calls this *distributional convergence*.
2. **Adjectives do not fix it. Constraints do.** "Clean, modern, premium" is satisfied by the generic page. "Four type sizes, one accent, 6px radius, no gradients" makes most of the generic page illegal.
3. **Fixes that only ban things create a new sameness.** Anthropic's own testing found that banning one font moves the model to the next common one (Space Grotesk). Users report the official `frontend-design` skill now has its own recognizable look (bold display type, dramatic gradients, asymmetric grids).
4. **Where AI is already good:** usability basics, layout structure, speed, and pragmatic UX scores. **Where it is weak:** originality, accessibility, multi-screen consistency, interaction depth, and taste judgment.
5. **Closing the gap:** a well-directed, human-supervised vibe-coded app can plausibly reach roughly **70-85% of top-tier human craft on marketing pages and simple apps**, and roughly **50-65% on complex product UI** **(judgment, see section 6)**. The last stretch is original concept, brand voice, motion choreography, and obsessive detail. That remains human-directed.

---

## 2. Why LLM frontends are sloppy and identical

| # | Cause | Mechanism | Evidence |
|---|---|---|---|
| 1 | **Distributional convergence** | Next-token prediction favors the high-probability center of training data. Safe choices "work universally and offend no one" and dominate web data. | Anthropic, *Improving frontend design through Skills* (A) |
| 2 | **Tailwind/shadcn default echo** | Tailwind docs shipped `bg-indigo-500` prominently for years; shadcn defaults (zinc grays, one radius, thin borders) are the most common component code. Agents reuse the defaults already in your repo and multiply them. | Superdesign, VP0 (C, plausible, partly speculative on the Tailwind origin story) |
| 3 | **Underdetermined prompts** | "Make a modern SaaS landing page" has no constraints, so the model has no reason to leave the centroid. | nyk.dev, Livery (C) |
| 4 | **Agent takes the easy path** | A coding agent builds what is easy to implement and verify, so it avoids ambitious layouts and motion. | Superdesign (C) |
| 5 | **No memory across generations** | Each screen is a fresh sample. Button on screen 1 is not the button on screen 4. Instructions like "never repeat yourself across generations" are unactionable. | dMaya (D, vendor with a competing product; claim is plausible and matches Anthropic's design) |
| 6 | **Judgment-action gap** | Models can partly *score* aesthetics but struggle to *repair* or *generate* them. Exact diagnosis-chain success peaked at 24.7%; absolute text-to-UI aesthetic scores were only 2.78-3.18 / 5. | AUV-Bench, arXiv (B, preprint with professional designers) |
| 7 | **Pragmatic good, hedonic flat** | 92-person study: AI prototypes scored fine on usability/efficiency but neutral-to-negative on originality and innovation. Authorship did not predict overall UX. | "Usable but Conventional", arXiv (B-, small, student raters, static prototypes) |
| 8 | **Accessibility and interactivity gaps** | Expert review of early-2025 models found structure was good but accessibility and working interactivity were weak. | "Qualitative Evaluation of LLM-Designed GUI", arXiv 2601.22759 (B-, older models, small) |
| 9 | **Vibe-coder is not specifying** | The person prompting often lacks the vocabulary (hierarchy, rhythm, tokens, states), so they cannot steer or critique. This is the gap the guide and template in this folder target. | Synthesis **(judgment)** |
| 10 | **Content is generic too** | Headlines like "Build faster" and stock features make the page feel templated even if the visuals are fine. | illos.dev (C) |

### The "AI fingerprint" checklist (what everyone has noticed)

- Inter/Roboto/system font everywhere, even headings
- Purple-to-indigo gradient, often on the headline or hero; white or light-gray page
- Centered hero + single CTA + "trusted by" logo row
- Three equal rounded cards with tiny icons in tinted squares
- Blurred blobs, dot grids, or stock 3D shapes where the product screenshot should be
- Same radius and shadow on every element; nested cards
- ALL-CAPS tiny label above every heading
- Uniform spacing (no rhythm), no real empty/loading/error states
- Emoji or generic line icons as feature art
- Vague copy that could sell anything

---

## 3. Reverse-engineering the quality spectrum

Ordered from best human work down to worst AI default. The point: each step down removes a specific layer of decisions.

### Tier A: Best human work (Stripe, Linear, Vercel, Apple, editorial studios; Awwwards-grade)

What the research says they actually do:

| Principle | How it shows up | Source |
|---|---|---|
| **Restraint** | Stripe's homepage: three colors, no body gradients, no card shadows, no decorative illustration. Vercel: grayscale chrome, color reserved for real product output. | Plinth (C) |
| **One typeface family, systemic scale** | Linear uses Inter, Vercel uses Geist, Stripe uses Söhne. The lesson is discipline (scale, weight, tracking), not a magic font. Note: Linear uses Inter. **The font was never the problem; the absence of a system is.** | Mantlr (C) |
| **Monochrome base + one accent** | One color "does all the work." | Pixel Darts (C) |
| **Interaction density, not visual density** | Sparse visually, but every element has hover, focus, keyboard, loading, and transition states. | Mantlr (C) |
| **Product-as-page** | Linear's homepage is a working fake issue + thread, not a description of the product. | Plinth (C) |
| **Designed motion and edges** | "Motion curves are designed, not defaulted. Shape edges match brand personality." | Linear's Karri Saarinen via Mantlr (C, secondhand) |
| **Opinionated product** | "Opinionated software beats flexible software." | Linear Method via Mantlr (C, secondhand) |
| **Flexible system, distinct voice** | Stripe Press: grid and framing system lets each book keep its own look. | Art director case study (C) |
| **Craft has ROI** | Stripe's design head frames craft as competitive differentiation in crowded markets. | Figma blog (B-/C) |

### Tier B: Strong human work without superstar budgets
Follows Refactoring UI-style tactics: fewer borders, clear hierarchy through size/weight/color, spacing scale, readable line lengths, grouped content (Refactoring UI, B-). Solid, accessible, consistent, usually not memorable.

### Tier C: Best AI-assisted work (human-directed)
Examples cited publicly: 1618room.com (Claude Code, infinite grid, depth, gesture control; self-reported by creator), Anthropic's own "Rick Rubin: The Way of Code" (Awwwards Honorable Mention, 15/20 design/usability/creativity/content/overall vote bar shown), curated galleries like VibeMode and The Vibest. **(Caveat: "vibe-coded" winners nearly always had an experienced designer steering concept and taste; this is human design with AI as the hands.)**

### Tier D: AI with a good skill/prompt but no human direction
Distinct fonts, committed palette, atmosphere, some motion. Better single screens. Still recognizable as its own genre, and inconsistent across screens (dMaya, D, plausible).

### Tier E: Default AI one-shot
The fingerprint in section 2. Functional, often responsive, rarely accessible by default, flat in originality.

### Tier F: Worst AI output
Broken layouts, non-functional buttons, missing validation and error states, invisible focus, low contrast, placeholder everything. WebGen-Bench found best open-source-agent combos at only 27.8-38.2% functional accuracy with appearance scores around 3.0 / 5 (B, Claude-3.5-era models; now dated).

---

## 4. Benchmarks and what they actually measure

| Benchmark | Measures | Key reading | Grade / caveat |
|---|---|---|---|
| **WebDev Arena** (arena.ai, Nov 10 2026) | Human preference votes on generated web apps | Top: Claude Fable 5.2 (xHigh) 1836, Claude Opus 5.5 (Max) 1814, Claude Sonnet 5.5 (xHigh) 1773, Gemini 4 Carbon (High) 1768, GPT-6 Astra (Max) 1764. Best open-license: Kimi K3.1 Pro 1688, DeepSeek-V4.1-Flash 1664, Kimi K3 1658, MiMo-V2.6-Flash 1638, GLM-5.3 1622. | A-/B. Preference of voters, who may favor flashy output; prompts are short. |
| **Design Arena: websites** (via llmbenchmark.ai) | Open-weight design taste | Kimi K3 1331, Kimi K3.1 Pro 1320, DeepSeek V4.1 Flash 1305 | C. Aggregator. |
| **Design2Code** (Stanford) | Screenshot → code fidelity on 484 real pages | Models lag on recalling visual elements and layout. GPT-4o 90.2 avg; Qwen2.5-VL-72B ~88; 7B VisRefiner ~89. | A- (paper); results are for copying a design, not creating one. |
| **AUV-Bench** | Aesthetic score / diagnose / repair / generate, with professional designers | Generation aesthetics 2.78-3.18 / 5; diagnosis-chain exact success max 24.7%. | B (preprint). The most relevant evidence for "AI lacks taste." |
| **ArtifactsBench** (Tencent) | Rendered artifact judged by MLLM + checklist | Top open model GPT-OSS-120B 57.69 | B-. MLLM-judge. |
| **FrontendBench** | Functional tests on 148 tasks | Auto-eval agrees with humans ~90.5% | B. Functionality, not design. |
| **UEQ-S study** (N=92) | Perceived UX, AI vs human prototypes | Pragmatic fine; hedonic weak; authorship not decisive | B-. Static prototypes, students. |

**Skeptical note:** WebDev Arena votes reward what looks impressive in seconds. Strong scores there do not prove good UX, accessibility, or consistency across a real product.

---

## 5. The best benchmarks to copy (human) and to beat (vibe-coded)

**Human benchmarks (study these live, with devtools open):**
- Linear (linear.app), Stripe (stripe.com, stripe.com/press), Vercel (vercel.com, Geist), Apple product pages, Notion, Figma, Raycast, Arc, Framer sites, Awwwards Sites of the Day.
- Design systems: Material 3, Apple Human Interface Guidelines, GOV.UK Design System, IBM Carbon, Radix Themes, Atlassian.

**Best vibe-coded benchmarks (public, mixed quality; verify yourself):**
- 1618room.com (Claude Code; creator-reported)
- Anthropic "Rick Rubin: The Way of Code" (Awwwards Honorable Mention)
- Galleries: [VibeMode](https://www.vibemode.site/), [The Vibest](https://thevibest.com/)
- Open-source examples from Tesslate's UIGEN outputs (https://uigenoutput.tesslate.com)

**A practical test:** Take your own app and a Tier A reference. Compare screenshots at 1440px and 390px with the same content. Score both on the rubric in section 6.

---

## 6. How close can the best vibe-coded app get? (judgment, with rubric)

Scores are my estimates on a 1-5 scale. They are not measured. Confidence is moderate on direction and low on exact values. Use the rubric to run your own comparison.

| Dimension | Default AI one-shot | AI + good skill, no human | Best directed vibe-coded | Top human |
|---|---|---|---|---|
| Typography system | 2 | 3.5 | 4 | 5 |
| Color and contrast | 2.5 | 3.5 | 4 | 5 |
| Spacing/layout rhythm | 3 | 3.5 | 4 | 5 |
| Visual hierarchy | 3 | 3.5 | 4 | 5 |
| Originality / concept | 1.5 | 3 | 3.5 | 5 |
| Motion and interaction polish | 2 | 3 | 3.5 | 5 |
| States (empty/loading/error/disabled) | 2 | 2.5 | 4 | 5 |
| Accessibility (WCAG 2.2 AA) | 2 | 2.5 | 4 | 4.5 |
| UX flow and information architecture | 3 | 3 | 4 | 5 |
| Consistency across screens | 2.5 | 2.5 | 4 | 5 |
| Content/microcopy | 2 | 2.5 | 3.5 | 5 |
| **Average** | **2.4** | **3.0** | **3.9** | **4.9** |

**Reading it:** default AI is ~49% of top human; AI with a good skill ~61%; best directed vibe-coded ~80%. Gap closure from default to best-directed: about **(3.9-2.4)/(4.9-2.4) = 60%** of the total distance, with most of the gain coming from process, not model choice.

**What closes the gap, ranked by estimated impact (judgment):**
1. Design tokens and a written system before any screen (type, color, space, radius, motion).
2. A real reference (screenshots, URLs) instead of adjectives.
3. Real content and real data, not lorem ipsum.
4. Designing all states, not just the happy path.
5. A critique-and-fix loop using screenshots at multiple widths.
6. Accessibility audit with tools (axe, Lighthouse) and keyboard testing.
7. A human making the 3-5 "surprise" decisions (concept, one signature interaction, brand voice).
8. Using a top model (WebDev Arena leaders are all Claude/Gemini/GPT at this moment).

**What probably stays human for now (judgment):** an original concept, brand voice, taste calls under ambiguity, motion choreography that tells a story, and the "invisible" detail work Linear describes. AUV-Bench's judgment-action gap supports this.

---

## 7. Source log

| Grade | Source | Claim used | Effect |
|---|---|---|---|
| A | Anthropic, [Improving frontend design through Skills](https://claude.com/resources/articles/improving-frontend-design-through-skills) | Name and mechanism of distributional convergence; fonts/color/motion/background prompting; skills load on demand; models still converge on Space Grotesk | Core explanation and prompt blocks |
| A | NN/g, [10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) | Ten heuristics | Education guide |
| A | W3C, [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and [What's new](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/) | Four principles; nine new criteria | Accessibility checklist |
| A- | Stanford SALT, [Design2Code](https://arxiv.org/html/2403.03163v3) | 484 pages; models lag in visual element recall and layout | Benchmarks |
| B | [AUV-Bench](https://arxiv.org/html/2609.34854v1) | Judgment-action gap; 2.78-3.18/5 generation | Gap evidence |
| B | [Usable but Conventional](https://arxiv.org/html/2605.15124) | Pragmatic fine, hedonic weak | Gap evidence |
| B- | [Qualitative Evaluation of LLM-Designed GUI](https://arxiv.org/abs/2601.22759) | Accessibility and interactivity weak (Jan-2025 models) | Gap evidence, dated |
| B | [WebGen-Bench](https://doi.org/10.52202/085713-2419), [FrontendBench](https://arxiv.org/html/2506.13832v2), [ArtifactsBench](https://github.com/Tencent-Hunyuan/ArtifactsBenchmark) | Functional vs visual scoring | Benchmarks |
| B- | [WebDev Arena](https://arena.ai/leaderboard/code/webdev?stream=top) | Rankings above | Model choice |
| B- | [Refactoring UI](https://refactoringui.com/) | Tactics (fewer borders, spacing, hierarchy) | Guide |
| C | [Superdesign](https://superdesign.dev/blog/why-ai-design-looks-generic), [Livery](https://www.livery.site/guides/why-ai-generated-ui-looks-the-same), [nyk.dev](https://www.nyk.dev/blog/design-with-ai), [VP0](https://vp0.com/blogs/why-does-my-ai-app-look-generic), [illos.dev](https://illos.dev/guides/vibe-coded-websites) | Practitioner explanations; constraints > adjectives; shadcn default echo | Causes 2-4, 10 |
| C | [Plinth](https://plinthstudio.dev/blog/stripe-linear-loom-design-lessons), [Mantlr](https://mantlr.com/blog/stripe-linear-vercel-premium-ui), [Pixel Darts](https://www.pixeldarts.com/post/four-design-principles-behind-stripe-linear-and-vercel), [Stripe Press case](https://thisoldmachine.com/stripe-press) | What Stripe/Linear/Vercel do | Tier A |
| D | [dMaya](https://dmaya.ai/blog/claude-code-frontend-design-skill) | Skills have their own signature; multi-screen drift; A/B fork claim (75%) | Used only where independently plausible; vendor of a competing product |
| D | Aggregators: [cookiesforai](https://cookiesforai.app/compare/frontend-design-agent-skills), [dropthehassle](https://dropthehassle.com/guides/design-skills-claude-code-cursor), [crewmark](https://crewmark.ai/skills/website-design), [llmbenchmark.ai](https://llmbenchmark.ai/best/open-weight-for-design) | Plugin lists, star counts, licenses, open-model design rankings | Tools list; star counts are volatile and unverified |

## 8. Skeptical notes and conflicts

- **"Ban Inter" is a trap.** Linear itself ships Inter. The Anthropic skill bans Inter, yet Anthropic's own post says banned defaults get replaced by the next default. Treat font bans as a starting nudge, not a fix.
- **Skills trade one sameness for another.** Multiple practitioners report the post-skill look is also recognizable. The durable fix is *your* system plus *your* references.
- **Vendor bias:** several sources sell design tools or skills. I used their claims only for mechanism descriptions that Anthropic's primary post also supports.
- **Academic evidence is thin and dated.** Studies use older models, small samples, static prototypes, and student raters. Direction (functional yes, original/accessible no) is consistent across them. Magnitudes are not reliable for 2026 models.
- **Leaderboards measure preference, not product quality.** Do not infer UX from Elo.
- **The percentages in section 6 are my estimates.** No study measures "% of top human design." Run the rubric yourself.
- **Star counts and installs** (hundreds of thousands cited) are unverified and volatile.

## 9. Evidence gaps

- No controlled study of multi-screen consistency or long-lived products built by agents.
- No peer-reviewed comparison of "with skill" vs "without skill" outputs with blind designer raters.
- I did not run any of the plugins or models myself. Recommendations come from documentation and third-party reviews.
