# 16. Glossary and Learning Path

Definitions are standard usage; where a term comes from a file in this knowledge base, the file is linked for sources. Learning-path resources are ones cited elsewhere in this knowledge base; I did not re-verify that every link is free beyond what the cited file says.

## 1. Glossary

| Term | Plain meaning | See |
|---|---|---|
| **WCAG** | W3C Web Content Accessibility Guidelines; 2.2 has 86 current success criteria (31 A, 24 AA, 31 AAA) | [14](14-inclusive-design-ai-ux-and-wcag-check.md) |
| **Success criterion (SC)** | One testable WCAG requirement with a level (A/AA/AAA) | 14 |
| **AT** | Assistive technology: screen readers, switch devices, speech recognition | 14 |
| **COGA** | W3C cognitive and learning disabilities task force guidance | [03](03-cognitive-load-and-frustration.md) |
| **Cognitive load** | Mental effort demanded by a task or interface | 03 |
| **Hick's law** | Decision time grows with log of number of choices | 03 |
| **Fitts's law** | Pointing time depends on distance and target size | [06](06-input-reading-and-forms.md) |
| **Above the fold** | Content visible without scrolling | [04](04-eye-tracking-and-attention.md) |
| **LCP / INP / CLS** | Core Web Vitals: loading, interaction responsiveness, layout stability | [05](05-performance-and-perceived-speed.md) |
| **Aesthetic-usability effect** | Attractive designs are perceived as easier to use, which can hide real problems | [09](09-visual-design-fundamentals.md) |
| **Gestalt principles** | Proximity, similarity, etc.: how people group visual elements | 09 |
| **Visual hierarchy** | Making important things look more important via size, weight, contrast, position | 09 |
| **Design token** | Named design decision (color, spacing, etc.) stored as data | [10](10-design-systems-and-tokens.md) |
| **DTCG** | Design Tokens Community Group; format module 2025.10 (stable, **not** a W3C Standard) | 10 |
| **Semantic token** | Token named by purpose (`color.text.danger`) rather than value (`red-500`) | 10 |
| **Design system** | Shared tokens, components, patterns, and rules | 10 |
| **Headless component** | Behavior and accessibility with no styling (Radix, React Aria) | 10 |
| **Container query** | CSS that adapts a component to its container, not the viewport | [11](11-responsive-mobile-and-localization.md) |
| **Logical properties** | `margin-inline-start` etc., direction-aware CSS (RTL support) | 11 |
| **PWA** | Web app with manifest and service worker; installable/offline | 11 |
| **i18n / l10n** | Internationalization (design for many locales) / localization (adapting for one) | 11 |
| **Text expansion** | Translated strings often longer than English; leave room | 11 |
| **SSR / SSG / CSR** | Render on server per request / at build / in browser | [12](12-frontend-engineering-issues.md) |
| **Hydration** | Attaching JavaScript behavior to server-rendered HTML | 12 |
| **XSS** | Injecting script into a page via unescaped input | 12 |
| **CSP** | Content Security Policy header restricting what a page can load/run | 12 |
| **Performance budget** | Limit on size/time metrics enforced in CI | 12 |
| **Heuristic evaluation** | Expert review against usability heuristics | [13](13-ux-research-methods-and-measurement.md) |
| **Think-aloud** | Users speak while doing tasks | 13 |
| **SUS / UEQ / NASA-TLX** | Questionnaires for usability, UX, and workload | 13 |
| **A/B test** | Randomized comparison of two variants; watch for sample ratio mismatch | 13 |
| **JTBD** | Jobs To Be Done framing of user needs (contested) | 13 |
| **Dark pattern / deceptive design** | UI that steers users against their interest | [01](01-legal-and-compliance.md), 12 |
| **Prompt** | Instruction + context given to an LLM | [15](15-llm-prompting-for-frontend.md) |
| **Few-shot** | Giving examples inside the prompt | 15 |
| **Context engineering** | Curating what the model sees (rules, tokens, tools) | 15 |
| **Rules file** | `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`: persistent project instructions | 15 |
| **MCP** | Model Context Protocol: standard way to connect tools (Figma, Playwright) to agents | 15 |
| **LLM-as-judge** | Using a model to score outputs; has position/verbosity/self biases | 15 |
| **Hallucination (package)** | Model invents a library or API that does not exist | 15 |

## 2. Learning path (judgment: ordering is mine; contents are sourced in the linked files)

### Stage 0: orientation (1 sitting)
- Read [README](README.md) takeaways and [08 audit checklist](08-audit-checklist.md).
- Goal: know what "good" looks like.

### Stage 1: foundations (beginner)
1. HTML semantics, keyboard use, and one screen reader (NVDA free; VoiceOver built in). Try your product with your **keyboard only**.
2. [02 accessibility engineering](02-accessibility-engineering.md), then [14](14-inclusive-design-ai-ux-and-wcag-check.md) section 1.
3. [09 visual design](09-visual-design-fundamentals.md): hierarchy, type, color contrast.
4. [06 input/reading/forms](06-input-reading-and-forms.md) and [11 responsive](11-responsive-mobile-and-localization.md).
- Practice: rebuild one form so it is keyboard-operable, labeled, and usable at 320 px.

### Stage 2: practice (intermediate)
1. [03 cognitive load](03-cognitive-load-and-frustration.md), [04 attention](04-eye-tracking-and-attention.md), [05 performance](05-performance-and-perceived-speed.md).
2. [10 design systems](10-design-systems-and-tokens.md): create a 3-tier token set and 5 components.
3. [13 research methods](13-ux-research-methods-and-measurement.md): run 5 think-aloud sessions and report with SUS.
- Practice: ship a component with Storybook a11y checks and a Playwright screenshot test.

### Stage 3: engineering depth (advanced)
1. [12 engineering](12-frontend-engineering-issues.md): rendering strategy, state, security, privacy, budgets.
2. [01 legal](01-legal-and-compliance.md) for your jurisdiction; get counsel.
3. [14](14-inclusive-design-ai-ux-and-wcag-check.md) sections 3-5: inclusive design and AI-feature UX.

### Stage 4: working with LLMs
1. [../frontend-design/03-prompt-template-kit.md](../frontend-design/03-prompt-template-kit.md) for templates; [15](15-llm-prompting-for-frontend.md) for evidence and loops.
2. Write a rules file, wire tokens in, set up a verification loop (typecheck, lint, axe, screenshots).
3. Build the small eval in 15 section 9. Treat every prompt like code: version it and test it.

### Stage 5: stay current
- Re-check legal dates, WCAG 3 progress, and vendor prompting docs every few months ([17](17-issues-and-open-problems.md) lists what's unsettled).

## 3. Common misconceptions (with the correction)

| Misconception | Correction |
|---|---|
| "Passing an automated scan means accessible" | Tools find a subset: Deque reports 57% of issues by volume but only 16 of 50 WCAG 2.1 A/AA criteria; one study found about one sixth of criteria covered ([10](10-design-systems-and-tokens.md)) |
| "5 users find 85% of problems, always" | A model result, contested; best for qualitative iteration, not statistics ([13](13-ux-research-methods-and-measurement.md)) |
| "Working memory holds 7 items" | About 4 under controlled conditions ([03](03-cognitive-load-and-frustration.md)) |
| "Pretty designs are more usable" | They are *perceived* as more usable and can mask problems ([09](09-visual-design-fundamentals.md)) |
| "Dark mode is better for everyone's eyes" | Evidence favors positive polarity for many tasks and users; offer both ([09](09-visual-design-fundamentals.md)) |
| "Design tokens are a W3C standard" | DTCG format is stable but a Community Group report, not a W3C Standard ([10](10-design-systems-and-tokens.md)) |
| "Prompt a model as an expert designer and it gets better" | Persona prompts showed no reliable gain on accuracy tasks; no UI-specific evidence ([15](15-llm-prompting-for-frontend.md)) |
| "AI code is production-ready" | Studies show security, accessibility, and hallucinated-dependency problems; review it |
| "Longer prompts are better" | Context is a budget; long context is used unevenly ([15](15-llm-prompting-for-frontend.md)) |
| "WCAG AA is the ceiling" | It is a floor; real users find more ([14](14-inclusive-design-ai-ux-and-wcag-check.md)) |
