# 08. Audit Checklist and LLM Audit Prompt

Use per screen and per flow. Tick or note a fix. Evidence links are in files 01-07.

## A. Compliance (WCAG 2.2 AA)
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

## B. Cognitive load and frustration
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

## C. Attention and scanning
- [ ] Key message and next step in the first screen and first two lines
- [ ] Headings, bold lead-ins, bullets encourage layer-cake scanning rather than F
- [ ] Important content not styled or placed like ads
- [ ] Clear grouping boundaries; one dominant region
- [ ] First-glance test (1-5 s): can a stranger name the page type and primary action?

## D. Performance
- [ ] LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at p75 in field data (mobile and desktop)
- [ ] Input feedback within 100 ms; long operations show progress; >10 s has percent and cancel
- [ ] No blank loading screens; skeleton matches layout
- [ ] Images sized, modern format, LCP image prioritized; fonts optimized; JS split
- [ ] Layout reserved for dynamic content
- [ ] Tested on a mid-range phone with throttled CPU and network

## E. Input, reading, forms
- [ ] Touch targets ~44px; larger for older or motor-impaired audiences
- [ ] 16px+ text, 1.5 line-height, ~45-75 ch measure; zoom and user settings respected
- [ ] One-column forms, top labels, correct input types, inline validation after field completion
- [ ] Mobile keyboard types correct; paste allowed

## F. Measure with people
- [ ] 5 users per key segment, including AT users where relevant
- [ ] Task success, time, errors; SUS or UEQ-S; NASA-TLX for heavy tasks (instrument facts: [13](13-ux-research-methods-and-measurement.md))
- [ ] Decision log of fixes and retests

---

## LLM audit prompt (paste into an agent with the app running)

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

## Template: research-backed design review note

```markdown
Screen: 
User goal: 
Primary action: 
Evidence used (file/section): 
Findings:
| # | Issue | Evidence | Severity | Fix | Verified by |
Residual risks and what was not tested:
```
