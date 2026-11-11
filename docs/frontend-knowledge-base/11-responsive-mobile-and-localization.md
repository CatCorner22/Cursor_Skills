# 11. Responsive, Mobile, Cross-Device, PWA, Localization, and Content Design

Researched 2026-11-11. Grades: A standard, B NN/g primary or peer-reviewed, C reference docs/practitioner, D secondary. **(judgment)** = inference. **(not researched)** = unverified general knowledge.

## 1. Responsive layout mechanics (verified in MDN)

| Tool | Verified behavior | Source | Grade |
|---|---|---|---|
| Container queries | Set `container-type: inline-size` (or `size`) on an ancestor; apply `@container (min-width: 400px) { ... }` to descendants. Size containers get **size containment**, so they cannot take size from their contents (prevents infinite loops); if the container has no contextual or explicit size it collapses. Descendants can use container query length units. | [MDN @container](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@container), [container-type](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/container-type) | C (reference) |
| Component-level vs page-level | Media queries respond to the viewport; container queries respond to the component's container. **(judgment: use container queries for reusable components, media queries for page shell.)** | MDN | C |
| Fluid type | Combine `clamp()` with container/viewport units, e.g. `clamp(1rem, 0.875rem + 0.5cqi, 1.25rem)` (the example appears in the search-tool synthesis of MDN, not copied from a fetched page; verify before use). **Pure viewport units can break zoom behavior; keep a rem term** (WCAG 1.4.4 Resize Text) **(judgment)**. | MDN (synthesis) | C / unverified detail |
| Logical properties | `margin-inline-start`, `padding-block`, `inset-inline-end`, `inline-size`, etc. follow writing direction, so layouts adapt to RTL and vertical writing modes. Physical properties (`left`, `margin-left`) do **not** flip. Grid `start`/`end` keywords are flow-relative. | [MDN logical properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Logical_properties_and_values), [MDN grid + writing modes](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Grid_layout/Logical_values_and_writing_modes) | C |

Not researched: CSS Grid vs Flexbox decision rules, subgrid, `dvh`/`svh` mobile viewport units, browser support tables (check caniuse/MDN baseline yourself).

## 2. Touch, grip, and gestures

| Finding | Source | Grade |
|---|---|---|
| Users switch grips constantly; one-hand and thumb use is common, but don't plan for one fixed grip. | [Hoober, Fingers, Thumbs, and People (ACM Interactions 2015)](https://interactions.acm.org/archive/view/may-june-2015/fingers-thumbs-and-people) | B-/C (practitioner field observation) |
| People prefer to touch the **center** of the screen; most taps land in about the center half to two-thirds. They also scroll content toward the middle. | Same | C |
| Accuracy is lowest at screen edges and corners; the biggest accuracy variable was **tap position**, not age or familiarity. Corners need about twice the spacing of the center. | Same | C |
| Fingers cover content; leave room for visible pressed states and a scroll gutter. In RTL languages the empty side is the opposite one. | Same | C |
| Minimum physical size about **1 cm x 1 cm** (Parhi, Karlson, Bederson study via NN/g). Already reconciled with WCAG's 24 CSS px in [06](06-input-reading-and-forms.md). | [NN/g, Touch Targets](https://www.nngroup.com/articles/touch-target-size/) | B |
| WCAG 2.5.7 Dragging Movements (AA): every drag needs a single-pointer alternative. WCAG 2.5.1 Pointer Gestures (A): complex path gestures need alternatives. | [W3C What's new 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/) | A |

**Skeptical:** "thumb zone" heat maps circulate widely; the Hoober piece says to *not* over-plan for one grip. Treat green/red thumb-zone diagrams as folklore unless they cite measurement **(judgment)**.

**Mobile eye tracking, not researched this session.** Desktop eye-tracking summarized in [04](04-eye-tracking-and-attention.md). Do not assume F-pattern conclusions transfer to phones.

## 3. Progressive Web Apps (PWA)

| Fact | Source | Grade |
|---|---|---|
| A PWA needs a **web app manifest** (JSON: entry URL, icons, display behavior) and a **service worker** (script running independent of the page, enabling caching, background sync, push). | [web.dev AEM/Workbox case study](https://web.dev/case-studies/aem-with-workbox) | C |
| web.dev's PWA checklist lists installable, fast (Core Web Vitals), and **fully accessible (WCAG)** as expectations; says most accessibility testing must be manual. | [web.dev PWA checklist](https://web.dev/articles/pwa-checklist) | C |
| Caching strategies (cache-first, network-first, cache with network fallback) trade freshness for speed. | web.dev case study | C |

**Judgment:** a PWA is worth it when you need installability or offline; otherwise a fast responsive site is simpler. Service worker bugs (stale caches) are a real source of "my fix isn't showing" support issues, but I did not source a rate.

## 4. Internationalization (i18n), localization, RTL

| Fact | Source | Grade |
|---|---|---|
| Translated text expands. W3C cites IBM's average expansion from English into European languages: up to 10 chars 200-300%; 11-20: 180-200%; 21-30: 160-180%; 31-50: 140-160%; 51-70: 151-170% (as printed); over 70: 130%. Shorter source strings expand more. | [W3C i18n, Text size in translation](https://www.w3.org/International/articles/article-text-size.en) | B/C |
| Design for reflow: avoid fixed-width containers and tight fits; separate content from presentation so font size/line height can adapt per language. English and Chinese are compact sources. | Same | C |
| Writing directions: English/Portuguese LTR; Hebrew/Arabic RTL; CJK traditionally vertical top-to-bottom in some contexts; Mongolian vertical with lines flowing left to right. | [MDN logical properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Logical_properties_and_values) | C |
| WCAG 2.2 added Notes about different languages; 3.1.1 Language of Page (A) and 3.1.2 Language of Parts (AA) are the baseline. | [WCAG 2 Overview](https://www.w3.org/WAI/standards-guidelines/wcag/), list in [14](14-inclusive-design-ai-ux-and-wcag-check.md) | A |

Checklist: set `lang` and `dir`; logical CSS; no text in images; no concatenated sentences (word order differs); allow 2-3x growth in buttons and labels; test pseudo-localization with long strings and an RTL language **(judgment, standard practice, not individually sourced)**. Mirror directional icons (arrows, back) but not logos, media controls, or numerals **(judgment; verify per locale)**.

Not researched: plural rules/ICU MessageFormat, date/number formatting (`Intl`), font fallback for CJK/Indic scripts, cultural color or imagery differences (see [17](17-issues-and-open-problems.md)).

## 5. Content design and plain language

| Finding | Source | Grade |
|---|---|---|
| Lower-literacy users **cannot understand text at a glance**: they read word by word, "plow" lines, have a narrow field of view, and satisfice on little information. | [NN/g, Lower-Literacy Users](https://www.nngroup.com/articles/writing-for-lower-literacy-users/) | B |
| Recommended: about **6th-grade** reading level on homepage and key landing pages, **8th-grade** elsewhere; main point first; single main column; linear navigation; avoid scrolling where practical. | Same | B |
| Seniors: success rate 55.3% vs 74.5% for ages 21-55; time on task 7:49 vs 5:28; errors 2.4 vs 1.1 in NN/g's 2013 round (31 seniors, 29 sites; control 20 users). Seniors 65+ were 43% slower. | [NN/g, Seniors](https://www.nngroup.com/articles/usability-seniors-improvements/) | B (small samples, 2013) |
| Errors: plain language, precisely indicate the problem, suggest a fix (Nielsen heuristic). | [NN/g, 10 Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) | B |
| Search engines reward "people-first" original content; Google says no preferred word count. | [Google Search Central](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) | C |

**Content-design checklist (judgment, consistent with sources):** user's words, not internal jargon; front-load the point; one idea per sentence; verbs on buttons ("Save changes", not "Submit"); error = what happened + how to fix; test with the reading-grade check but also with real users.

## 6. Cross-device testing matrix (judgment)

| Dimension | Minimum set |
|---|---|
| Viewport | 320 px wide (reflow), ~768, ~1280+ |
| Input | Touch, mouse, keyboard only, screen reader |
| Settings | 200% zoom, large text, reduced motion, dark mode, forced colors |
| Network/device | Throttled 4G/3G, low-end Android (see budgets in [12](12-frontend-engineering-issues.md)) |
| Locale | Long-text language, RTL language |
