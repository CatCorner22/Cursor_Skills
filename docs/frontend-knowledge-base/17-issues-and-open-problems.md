# 17. Issues, Open Problems, Conflicts, and Research Limits

Use this file to know what is **settled**, **contested**, or **not researched**. Details and sources are in the linked files.

## 1. Conflicts and unresolved debates

| Issue | Positions | Status / what I recommend |
|---|---|---|
| Contrast math | WCAG 2 ratio vs APCA (perceptual, polarity-aware); WCAG 3 is a Working Draft and not a replacement yet | Conform to WCAG 2.2 for compliance; APCA as extra insight only ([09](09-visual-design-fundamentals.md)) |
| Dark mode | Positive polarity advantaged for many tasks vs preference/low-light/cataract cases | Offer both; don't claim dark mode is healthier ([09](09-visual-design-fundamentals.md)) |
| 5-user testing | Nielsen model (~85%) vs Faulkner (55% to ~100% across samples of 5) | Use 5 for iterative qualitative rounds, not for rates ([13](13-ux-research-methods-and-measurement.md)) |
| SUS origin date | 1996 chapter vs MeasuringU's 1986 claim | Unresolved; cite the 1996 publication, avoid origin year ([13](13-ux-research-methods-and-measurement.md)) |
| Automated a11y coverage | 57% by issue volume (Deque) vs 16/50 criteria vs one sixth in a study | Different denominators; automation is necessary, not sufficient ([10](10-design-systems-and-tokens.md)) |
| DTCG standing | "Stable" spec vs not a W3C Standard | Adopt with awareness; tool support varies ([10](10-design-systems-and-tokens.md)) |
| Thumb-zone maps | Popular diagrams vs Hoober's own caveats (grip varies) and NN/g target-size research | Treat as folklore-adjacent; test with your users ([11](11-responsive-mobile-and-localization.md)) |
| Pure viewport units in type | Fluid type convenience vs zoom/resize issues | Use `clamp()` with rem, test 200% zoom ([11](11-responsive-mobile-and-localization.md)) |
| JTBD | Christensen vs Ulwick definitions; empirical critiques | Use as a lens, not a method with proof ([13](13-ux-research-methods-and-measurement.md)) |
| Progress bars vs skeletons; line length and dyslexia; F-pattern | See [07](07-research-library.md) section G | Mixed evidence |
| Persona prompting | No gain on accuracy tasks vs vendor/practitioner lore; irrelevant persona detail can hurt | Don't rely on it ([15](15-llm-prompting-for-frontend.md)) |
| Self-correction | Self-Refine gains vs intrinsic self-correction failing | Add external signals ([15](15-llm-prompting-for-frontend.md)) |
| AI productivity | METR 19% slowdown (16 devs) vs vendor claims | Measure on your team; METR sample is narrow ([15](15-llm-prompting-for-frontend.md)) |
| Prompt style by model | "Be explicit" (GPT-style) vs "give high-level goals" (reasoning models) vs "soften emphasis" (newer Claude) | Re-test per model |
| Core Web Vitals and ranking | Search-tool summaries asserted a ranking effect; I did not verify in primary docs | Marked unverified in [12](12-frontend-engineering-issues.md) |

## 2. Where research is weak (structural limits)

- **Small samples, old devices:** many cited UX studies have 16-123 participants and 2006-2018 data; modern behavior may differ.
- **Vendor-authored evidence:** Anthropic, OpenAI, Deque, Figma, NN/g (sells reports) all publish findings that favor their products or services; independent replication is rare.
- **LLM research ages fast:** studies tested GPT-3.5/GPT-4/Copilot-2021-era models; effects on current models are unknown. Benchmarks like Design2Code use screenshot-to-code, not original UI design.
- **No controlled evidence** I found on: spec-vs-vague UI prompts, frontend-specific persona prompts, "anti-slop" steering effectiveness beyond vendor demos, LLM-judge validity for visual taste.
- **Accessibility generation studies** relied on automated checkers (AChecker, WAVE), which miss most WCAG criteria.
- **Surveys self-select:** WebAIM screen reader survey is not a random sample.
- **Legal facts change:** US rules in [01](01-legal-and-compliance.md) have dated deadlines; I am not a lawyer.
- **Standards moving:** WCAG 3.0 is a Working Draft; ISO 40500 and EN 301 549 updates are recent; recheck.

## 3. Coverage gaps (not researched)

| Area | What's missing |
|---|---|
| Color theory | Palette generation, color psychology claims, brand color evidence |
| Typography | Type scales, variable fonts, font loading trade-offs beyond [05](05-performance-and-perceived-speed.md) |
| Rendering | Primary sources for ISR and React Server Components (flagged in [12](12-frontend-engineering-issues.md)) |
| Libraries | Form libraries, state libraries, comparison data |
| Browser support | Baseline, compat testing practice |
| Auth UX | Passkeys, password manager behavior, CAPTCHA alternatives |
| Analytics ethics | Partial in 12 only |
| Mobile | Mobile eye-tracking research |
| Localization | Pseudo-localization, cultural color/imagery, voice/switch access depth |
| AI UX | Specific `aria-live` patterns for streaming; AI disclosure regulation |
| LLM | Google Gemini prompting docs (fetch failed; not read); current model head-to-heads; open-source and local models |
| Org practice | Design ops, technical debt, team workflows, content governance |
| Games/3D/data-viz | Charts, dashboards, accessible data visualization |
| Native apps | iOS/Android platform guidelines beyond what's cited |

## 4. How to keep this knowledge base honest

- [ ] Re-fetch any claim before using it in legal, medical, or contractual documents
- [ ] Add a date and grade to each new source ([07](07-research-library.md))
- [ ] Prefer replication or independent sources for vendor claims
- [ ] Move items from section 3 to a file only after reading the primary source
- [ ] Re-run the prompt eval ([15](15-llm-prompting-for-frontend.md) section 9) when the model changes

## Refresh note (2026-11-13)

Closed in the 2026-11-13 refresh: Gemini prompting docs (read via excerpts), Core Web Vitals ranking wording. Still open: see [master guide, section 24](../FRONTEND-MASTER-GUIDE.md#24-evidence-gaps-and-open-problems).
