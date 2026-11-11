# 10. Design Systems, Tokens, Components, and Visual Regression

Researched 2026-11-11. Evidence here is mostly **documentation and standards**, not controlled studies; there is very little peer-reviewed evidence that design systems improve outcomes (see skeptical notes). Grades: A standard/spec, C vendor or project docs, D secondary blog.

## 1. What a design system is (working definition)

A design system = **tokens** (named design decisions) + **components** (coded, accessible building blocks) + **guidelines** (when/why) + **tooling** (docs, tests, release). **(judgment: my synthesis; the DTCG abstract defines tokens as "indivisible pieces of a design system such as colors, spacing, typography scale.")**

## 2. Design tokens

| Fact | Source | Grade |
|---|---|---|
| The Design Tokens Community Group (DTCG) published **Format Module 2025.10** on 28 Oct 2025 as a "stable" Community Group report. **It is not a W3C Standard and not on the W3C Standards Track.** | [W3C CG report](https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/) | A (spec text) |
| Tokens are JSON; every token needs a `$value`; `$type` is required (explicit, inherited from a group, or via alias). Tools "MUST consider the token invalid" if no type can be resolved; they must not guess a type from the value. | [DTCG types](https://github.com/design-tokens/community-group/blob/main/technical-reports/format/types.md) | A |
| 2025.10 adds theming and multi-brand support (light/dark, accessibility variants), modern color spaces (Display P3, Oklch, CSS Color 4), aliases/inheritance, and cross-platform output (iOS, Android, web, Flutter). | [DTCG announcement](https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/) | C (self-announced) |
| Reference tools named: Style Dictionary, Tokens Studio, Terrazzo; adopters named include Penpot, Figma, Sketch, Framer, Knapsack, Supernova, zeroheight ("support or are implementing"). | Same | C (vendor claim, I did not test) |
| The term "design tokens" is credited on the DTCG site to the Salesforce design system team. | [DTCG TR](https://www.designtokens.org/tr/2025.10/) | C |

### Tiered naming (judgment, common practice, not from a verified source)

| Tier | Example | Purpose |
|---|---|---|
| Primitive / global | `color.blue.600`, `space.4` | Raw palette and scale values |
| Semantic / alias | `color.text.default`, `color.action.primary` | Meaning; the layer themes override |
| Component | `button.primary.bg` | Local overrides, use sparingly |

Rules: components consume semantic tokens only; themes remap semantic to primitive; never name by appearance when meaning matters (`color.danger` not `color.red`). Dark mode = a second mapping of semantic tokens, and must be contrast-checked (see [09](09-visual-design-fundamentals.md)).

## 3. Component architecture and libraries

| Option | What the docs say | Source | Grade |
|---|---|---|---|
| **Radix Primitives** | Low-level, accessible, **unstyled** components; follow WAI-ARIA patterns; handle aria/role attributes, focus management, keyboard navigation. Principles: accessible, functional, interoperable, composable (1 component = 1 DOM element where possible), customizable. Tested with VoiceOver, JAWS, NVDA per their philosophy doc (self-reported). | [Radix intro](https://www.radix-ui.com/primitives/docs/overview/introduction), [philosophy](https://github.com/radix-ui/primitives/blob/main/philosophy.md) | C |
| **shadcn/ui** | "Open Code": a CLI copies component source into your project; a starting point to build your own library, not an npm dependency. Trade-off per one practitioner write-up: you own maintenance; no `npm update` for improvements. | [shadcn-ui/ui](http://github.com/shadcn/ui); [practitioner post](https://bryanortiz.me/journal/shadcn-ui-the-component-library-that-isnt-a-library) | C / D |
| **React Aria (Adobe)** | Two APIs: React Aria Components (start here) and lower-level hooks (when you need DOM control or to retrofit existing components). Components are built on the hooks. | [React Aria hooks](https://react-aria.adobe.com/hooks) | C |
| **Tailwind CSS** | Utility-first styling; shadcn pairs Radix + Tailwind (per the practitioner post). OpenAI's frontend guidance lists Tailwind, shadcn/ui, Radix Themes as recommended libraries for its models. | [OpenAI prompt guide](https://platform.openai.com/docs/guides/prompt-engineering) | C |

**Why this matters for LLM work (judgment):** headless accessible primitives encode hard behavior (focus trap, roving tabindex, ARIA state) that LLMs frequently get wrong when hand-rolling dialogs/comboboxes; steering the model to use them is an accessibility mitigation. See [15](15-llm-prompting-for-frontend.md) and the a11y-in-generated-code studies in [14](14-inclusive-design-ai-ux-and-wcag-check.md).

### Component API design checklist (judgment, practitioner consensus; not individually sourced)

- [ ] Prefer native elements first (`button`, `dialog`, `details`); custom only when necessary
- [ ] Composition (slots/children) over a giant props list; avoid boolean-prop explosions
- [ ] Support controlled and uncontrolled usage (Radix does by default)
- [ ] Forward refs, accept `className`/props spread, expose the DOM node
- [ ] Every interactive state documented: default, hover, focus-visible, active, disabled, loading, error, empty
- [ ] Keyboard and screen-reader behavior documented per WAI-ARIA pattern
- [ ] Logical CSS properties so RTL works (see [11](11-responsive-mobile-and-localization.md))

## 4. Documentation and testing in the system

| Layer | Tool and verified behavior | Source |
|---|---|---|
| Interaction tests | Storybook `play` functions simulate user interactions and assert output | [Storybook docs](https://storybook.js.org/docs/writing-tests) |
| Accessibility tests | `@storybook/addon-a11y` is built on Deque's axe-core and "automatically catches up to 57% of WCAG issues" (Storybook's wording; see Deque caveat below). Results show Violations / Passes / Incomplete (manual-check list). | [Storybook a11y](https://storybook.js.org/docs/writing-tests/accessibility-testing) |
| Visual tests | Pixel snapshots of every story vs a baseline; Storybook supports this via Chromatic (a cloud service by the Storybook team, i.e. vendor). Snapshot (HTML) tests can false-positive because markup changes may not change pixels. | [Storybook visual](https://storybook.js.org/docs/writing-tests/visual-testing) |
| Screenshot assertions in E2E | Playwright `expect(page).toHaveScreenshot()`: creates baselines on first run; **rendering varies by OS, browser version, hardware, headless mode**, so generate and compare in the same environment; defaults `threshold` 0.2, `maxDiffPixels` unset. | [Playwright docs](https://playwright.dev/docs/test-snapshots) |
| Flakiness | Causes: dynamic content, async loading, rendering differences, third parties, animations, scaling. Fixes: wait for ready state/fonts/images, freeze time, stop animations, mask dynamic regions, same OS in CI. | [Argos](https://argos-ci.com/docs/learn/reliability-and-flakiness/flaky-tests) (vendor docs) |

**Deque caveat (important):** the "57%" is Deque's figure from 13,000+ pages / ~300,000 issues in first-time audits, counted **by issue volume**. By **success-criteria coverage**, automated checks found issues for only **16 of 50** WCAG 2.1 A/AA criteria. A peer-reviewed Swedish public-sector study found tools "cover only one sixth" of WCAG success criteria. Both are true; they measure different things. Automated tests are a floor, never proof of accessibility. Sources: [Deque report](https://www.deque.com/automated-accessibility-coverage-report/) (B-/C, vendor with large dataset); [Springer, Universal Access in the Information Society](https://link.springer.com/article/10.1007/s10209-025-01263-x) (A-).

## 5. Governance and versioning (judgment)

- Treat tokens as an API: semver, deprecation window, changelog.
- A design system with no owner decays. Assign a maintainer and a contribution path.
- Measure adoption (percentage of UI using system components) rather than assuming benefit.

## 6. Skeptical notes

- I found **no controlled study** here showing design systems reduce defects or increase speed. Claims are practitioner reports **(judgment: plausible, unmeasured)**.
- The shadcn "copy the code" model trades upgrade convenience for control; the "no version to upgrade" benefit is also the maintenance burden.
- Library docs describe intent; I did not run accessibility tests on Radix, React Aria, or shadcn output.
- DTCG status can be misread: "stable" in a Community Group is **not** a W3C Recommendation.

## 7. What to learn first

1. Semantic tokens + a 2-theme mapping. 2. One headless library (Radix or React Aria). 3. Storybook with a11y addon. 4. One visual-regression flow in a fixed CI environment.
