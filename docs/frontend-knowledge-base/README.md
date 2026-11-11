# Frontend Knowledge Base: Accessibility, Low Frustration, Low Cognitive Load, Intuitive Performance

Built 2026-11-11. Every fact below came from a source I read in search results or fetched text; each carries a source link and an evidence grade. Anything I infer is marked **(judgment)**. Re-verify legal dates before relying on them. I am not a lawyer.

## Contents

| File | Topic |
|---|---|
| [01-legal-and-compliance.md](01-legal-and-compliance.md) | US law and standards: ADA Title II, Section 508, HHS Section 504, ADA Title III, FTC dark patterns, WCAG 2.2 vs 3 |
| [02-accessibility-engineering.md](02-accessibility-engineering.md) | How to build accessible UI: who is affected, the common failures, criterion-by-criterion practice, testing |
| [03-cognitive-load-and-frustration.md](03-cognitive-load-and-frustration.md) | Working memory, cognitive load theory, Hick's law, COGA, forms, errors, dark patterns, frustration reducers |
| [04-eye-tracking-and-attention.md](04-eye-tracking-and-attention.md) | Eye-tracking and attention research, with design implications and limits |
| [05-performance-and-perceived-speed.md](05-performance-and-perceived-speed.md) | Response-time limits, Core Web Vitals, loading feedback research, motion |
| [06-input-reading-and-forms.md](06-input-reading-and-forms.md) | Touch targets, Fitts's law, line length, font size, dyslexia, forms |
| [07-research-library.md](07-research-library.md) | Annotated bibliography with free-access status and evidence grades |
| [08-audit-checklist.md](08-audit-checklist.md) | One-page checklist and an LLM audit prompt that ties everything together |

## Top 12 takeaways

1. **Legal baseline in the US:** federal ICT (Section 508) requires WCAG 2.0 A/AA. State and local government web content and apps (ADA Title II) require WCAG 2.1 AA by **April 26, 2027** (population 50,000+) or **April 26, 2028** (smaller). HHS-funded recipients (Section 504): WCAG 2.1 AA by **May 11, 2027** (15+ employees) or **May 10, 2028**. Private businesses (ADA Title III) have no finalized web rule, but courts and DOJ settlements use WCAG as the benchmark. Build to **WCAG 2.2 AA**, which satisfies 2.1 and 2.0 AA.
2. **Accessibility is mainstream:** 1 in 4 US adults report a disability (CDC, 2022); cognition is the most common type (13.9%). About 1 in 12 men have color vision deficiency (NEI).
3. **The web mostly fails:** 94.8% of the top 1M home pages had detectable WCAG failures in 2025; six issue types account for 96% of errors, led by low-contrast text (79.1%) (WebAIM Million 2025).
4. **Working memory is tiny:** about 4 chunks when rehearsal and chunking are controlled (Cowan 2001), not Miller's 7. Do not make people remember things across screens.
5. **Choice costs time:** reaction time grows with the log of the number of alternatives (Hick-Hyman).
6. **People scan, then leave the top:** in NN/g eye tracking, about 57% of viewing time was above the fold and 74% in the first two screenfuls (desktop, 2018). F-pattern is one of several scanning patterns and mostly appears when content lacks structure.
7. **A glance is enough for gist:** people classify a page into one of 10 categories well above chance from a 120 ms fixation and can locate the menu, so layout and first-view text carry the first impression.
8. **Banner blindness is task-driven:** strongest for right-side banners and goal-directed tasks. Ad-like elements get ignored, including your own.
9. **Speed thresholds:** 0.1 s feels instantaneous, 1 s keeps flow, 10 s loses attention (Nielsen). Core Web Vitals "good": LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at the 75th percentile.
10. **Perceived speed beats actual speed:** blank screens feel slowest; skeletons, progress bars, and spinners each help in different conditions. Evidence is mixed and small-sample.
11. **Forms are where frustration lives:** inline validation after the user finishes a field improved success 22%, cut errors 22%, cut completion time 42%, and cut fixations 47% in one 22-user eye-tracking study; validating while typing hurt.
12. **Touch targets:** WCAG 2.2 AA minimum is 24×24 CSS px, but research suggests about 9-10 mm for most adults, 14 mm for older adults, and 18 mm for users with motor impairments.

## Evidence grades used

| Grade | Meaning |
|---|---|
| A | Law, regulation, or standard text (Federal Register, eCFR, W3C, Section508.gov) |
| A- | Peer-reviewed, free full text (PMC, PubMed, university repositories) |
| B | Government research-synthesis (HHS guidelines), NN/g primary eye-tracking reports, peer-reviewed but paywalled or small |
| C | Practitioner articles, conference slides, single-lab results, secondary summaries |
| D | Vendor or aggregator claims, used only for context |
