# Frontend, UI and UX: A Practical Guide for People Directing LLMs

Goal: give you enough vocabulary and judgment to specify, inspect, and correct what an LLM builds. You do not need to become a designer. You need to see what is wrong and name it in terms the model can act on.

Sources: NN/g heuristics, W3C WCAG 2.2, Refactoring UI, Anthropic's frontend-design article (links in `01-research-report.md`). Rules of thumb marked **(rule of thumb)** are common practice, not standards.

---

## Part 1: The map

| Term | What it is | Question it answers |
|---|---|---|
| **UX (user experience)** | The whole journey: goals, flows, structure, feedback, errors | "Can people accomplish what they came for, without confusion?" |
| **UI (user interface)** | What is on screen: layout, type, color, components, motion | "Does it look and feel coherent, clear, and appropriate?" |
| **IA (information architecture)** | How content is organized and labeled | "Where does this live? What is it called?" |
| **Interaction design** | How things respond to input over time | "What happens when I hover, click, wait, fail?" |
| **Visual/brand design** | Identity: type, color, imagery, voice | "Who is this for, and what does it feel like?" |
| **Frontend engineering** | HTML, CSS, JS, frameworks, performance, accessibility | "Does it work in every browser and for every person?" |
| **Design system** | Reusable tokens, components, and rules | "How do we stay consistent as it grows?" |

Order of work: **people and goals → flows and structure → wireframe → visual system → components → states → polish → test.** LLMs jump straight to the visual layer. You should make them start earlier.

---

## Part 2: UX fundamentals

### 2.1 Nielsen's 10 usability heuristics (NN/g)

| # | Heuristic | Plain meaning | Prompt it as |
|---|---|---|---|
| 1 | Visibility of system status | Always show what is happening | "Show loading, saving, success, and failure states for every async action." |
| 2 | Match with the real world | Use users' words, natural order | "Use plain language; no internal jargon." |
| 3 | User control and freedom | Undo, cancel, back | "Every destructive action has undo or confirmation; every modal has a clear exit." |
| 4 | Consistency and standards | Same thing looks and works the same | "Reuse the same component for the same job; follow platform conventions." |
| 5 | Error prevention | Stop mistakes before they happen | "Disable or guard invalid actions; inline validation; sensible defaults." |
| 6 | Recognition over recall | Show options; do not make people remember | "Visible labels, recent items, autocomplete." |
| 7 | Flexibility and efficiency | Shortcuts for experts | "Keyboard shortcuts and bulk actions, hidden from beginners." |
| 8 | Aesthetic and minimalist design | Remove what does not help | "Remove any element that does not support the primary task." |
| 9 | Help users recover from errors | Plain-language errors with a fix | "Error messages say what happened and what to do next." |
| 10 | Help and documentation | Findable, task-focused help | "Put help in the same place on every page." |

### 2.2 Core UX concepts

- **Jakob's Law:** people spend most time on other products, so they expect yours to work like those. Be conventional in navigation, forms, and checkout; be original in brand and moments of delight.
- **Hick's Law:** more choices means slower decisions. Limit primary actions per screen to one.
- **Fitts's Law:** bigger, closer targets are easier to hit. Primary actions should be large and reachable, especially on mobile.
- **Cognitive load:** every extra element, word, or decision costs attention. Group related items, hide rare options, use progressive disclosure.
- **Mental model:** what the user *thinks* the system does. Mismatches cause "mistakes" (conscious errors); inattention causes "slips" (NN/g).
- **Progressive disclosure:** show the essentials first; reveal advanced options on demand.
- **Affordance and signifiers:** things that look clickable should be clickable, and vice versa.
- **Peak-end rule (rule of thumb):** people remember the high point and the ending; polish success and confirmation moments.

### 2.3 Flows and states

Every screen exists in several states. LLMs usually build only the first.

| State | Design it |
|---|---|
| **Ideal / populated** | Normal use with realistic data (long names, many items) |
| **Empty** | First use. Say what goes here and offer the next step |
| **Loading** | Skeleton or progress that matches final layout |
| **Error** | What happened, what to do, how to retry; keep user input |
| **Partial / degraded** | Offline, slow, or some data missing |
| **Success** | Confirm the outcome; offer next step |
| **Disabled** | Explain why when it is not obvious |
| **Edge** | Zero results, 10,000 results, very long text, no avatar, non-Latin text |

### 2.4 Research basics (when you can talk to humans)

- 5 users find most major usability problems in a qualitative test **(rule of thumb, NN/g popularized)**.
- Task test: give a goal, say "think aloud," do not help. Watch where they hesitate.
- Ask about behavior ("When did you last...?") not opinions ("Would you use...?").
- A/B testing needs real traffic; it is for choosing between options, not for finding problems.

---

## Part 3: UI fundamentals

### 3.1 Hierarchy

Hierarchy tells the eye where to look first, second, third. Create it with **size, weight, color/contrast, spacing, and position**, not just size.

- One primary focal point per screen.
- De-emphasize secondary info with lighter weight and softer color instead of making everything big.
- Use fewer borders: separate with spacing, background tint, or subtle shadow (Refactoring UI).

### 3.2 Typography

- **Pick a type system, not a font.** A scale (for example 12/14/16/20/24/32/48) plus weights plus line-heights.
- Body text **16px+ on web**, line-height **1.4-1.6**, line length **45-75 characters** **(rule of thumb)**.
- Headings: tighter line-height (1.1-1.3); large display sizes often use slightly negative letter-spacing.
- Two families maximum (often one is enough). Contrast comes from size and weight.
- Use real weights: contrast between 400 and 700-800 reads clearer than 400 vs 500.
- Numbers in tables/dashboards: tabular figures, right-aligned.
- Avoid ALL-CAPS paragraphs; short labels only, with added letter-spacing.
- Load fonts with `font-display: swap`; avoid layout shift.

Note: popular fonts are not "wrong." Linear uses Inter, Vercel Geist, Stripe Söhne. The pros win through scale, spacing, and consistency.

### 3.3 Color

- **Structure:** neutrals (6-10 steps) + one brand/accent + semantic colors (success, warning, danger, info).
- Start in grayscale; add color for meaning and focus.
- **Contrast (WCAG 2.2 AA):** 4.5:1 for normal text, 3:1 for large text and UI component boundaries/icons.
- Never use color alone to convey meaning (add icon or text).
- Tint your neutrals slightly toward your brand hue so the page feels cohesive.
- Dark mode is a redesign, not an inversion: lower contrast extremes, lighter elevation surfaces, desaturate accents.
- One accent used sparingly beats five used everywhere.

### 3.4 Spacing and layout

- Use a **base unit (4 or 8px)** and a fixed scale: 4, 8, 12, 16, 24, 32, 48, 64, 96.
- **Proximity:** related things are closer together than unrelated things. More space between groups than within them.
- Start with too much whitespace, then remove (Refactoring UI).
- Use grid and alignment: a clear left edge beats scattered offsets.
- **Responsive:** design mobile first; test at 360-390, 768, 1024, 1440 px. Use fluid type and `clamp()`, container queries when components move between contexts.
- Constrain content width. Full-width text on a 27" monitor is unreadable.

### 3.5 Depth, shape, imagery

- Choose one elevation approach (flat with borders, subtle shadows, or glass) and keep it.
- Pick a radius personality (0, 4, 8, 16, pill) and apply it consistently. Same radius on everything is a tell.
- Real product screenshots, photography, or purposeful illustration beat blobs and stock 3D.
- Icons: one set, one stroke weight, consistent size. Labels beat icon-only in most cases.

### 3.6 Motion

- Purpose: show status, guide attention, express personality. Not decoration.
- Durations (rule of thumb): micro-feedback 100-200ms, element transitions 200-400ms, page-level moves up to 600ms.
- Prefer ease-out for entrances, ease-in for exits. Design your curves.
- One orchestrated page-load sequence beats many scattered effects (Anthropic).
- **Respect `prefers-reduced-motion`.** Animate `transform` and `opacity`, not layout properties.

### 3.7 Components you should know by name

Button (primary/secondary/ghost/destructive), input, select, checkbox/radio/switch, tabs, accordion, modal/dialog, drawer/sheet, popover, tooltip, dropdown menu, toast, banner/alert, badge/tag, card, table, pagination, breadcrumb, stepper, skeleton, empty state, command palette, data chart.

Use named, well-tested primitives (Radix, React Aria, Headless UI, shadcn/ui built on Radix) for behavior and accessibility, and **restyle them** with your own tokens so they do not look like everyone else's.

---

## Part 4: Accessibility (non-optional)

WCAG 2.2 principles: **Perceivable, Operable, Understandable, Robust.** Target **AA**. Many places legally require it.

Minimum checklist:

- [ ] Semantic HTML: `button` for actions, `a` for navigation, `nav`, `main`, headings in order, `label` tied to each input.
- [ ] Everything works by keyboard; logical tab order; no keyboard traps.
- [ ] **Visible focus indicator** on every interactive element, not obscured by sticky headers (WCAG 2.2: 2.4.11).
- [ ] Text contrast 4.5:1 (3:1 large text and UI parts).
- [ ] Touch/click targets at least 24x24 CSS px (WCAG 2.2 AA: 2.5.8); 44x44 is a friendlier mobile target **(platform guideline)**.
- [ ] Drag actions have a non-drag alternative (2.5.7).
- [ ] Help/contact appears in the same place across pages (3.2.6).
- [ ] Do not make users re-enter information they already gave (3.3.7).
- [ ] Authentication does not rely on cognitive tests like memorization or puzzles without an alternative (3.3.8).
- [ ] Images have meaningful `alt` (or empty alt if decorative); video has captions.
- [ ] Form errors identified in text, tied to fields, announced to screen readers.
- [ ] Zoom to 200-400% without losing content; no horizontal scrolling at 320px width.
- [ ] Respect `prefers-reduced-motion` and `prefers-color-scheme`.
- [ ] Language set on `<html lang>`.

Test with: keyboard only, a screen reader (VoiceOver/NVDA), axe DevTools or Lighthouse, browser zoom, and a contrast checker. Automated tools catch only part of the problems; manual testing is required.

---

## Part 5: Frontend engineering basics (enough to review LLM output)

- **HTML** gives structure and built-in accessibility. Prefer native elements to `div` + click handlers.
- **CSS:** custom properties (variables) for tokens; flexbox for 1-D layout; grid for 2-D; `clamp()` for fluid sizes; `:focus-visible`; `@media (prefers-reduced-motion)`; container queries.
- **JavaScript/frameworks:** React/Next.js, Vue/Nuxt, Svelte/SvelteKit, Astro (content sites). Choose by team and need, not by LLM default.
- **Design tokens:** name values by role (`--color-text-muted`, `--space-4`, `--radius-control`), not by appearance. Components consume tokens; nobody hard-codes hex.
- **State:** server data (cache, loading, error) is different from UI state (open/closed). Do not mix them.
- **Performance:** Core Web Vitals (LCP, INP, CLS). Optimize images (modern formats, width/height set), lazy-load below the fold, ship less JavaScript, avoid layout shift.
- **Forms:** labels, validation on blur/submit, preserve input on error, correct `type` and `autocomplete`.
- **Review smells:** `div onClick`, `outline: none` without replacement, fixed pixel widths, hard-coded colors, no `alt`, huge unoptimized hero image, nested scroll containers, z-index wars, missing states.

---

## Part 6: How LLMs fail here and how to compensate

| Failure | What you see | Your countermove |
|---|---|---|
| Convergence to the average | Inter, purple gradient, centered hero, 3 cards | Provide tokens and references before screens |
| Replacement defaults | Banned font → next common font | Name what to use, not only what to avoid |
| Happy-path only | No empty/loading/error states | Require a state matrix per screen |
| Drift between screens | Buttons and spacing differ | One tokens file and component library; "reuse, do not reinvent" |
| Decoration over function | Blobs, glass, gradients | "Every element must support a task; remove decoration that does not" |
| Weak accessibility | Invisible focus, divs as buttons, low contrast | Include the accessibility checklist in the prompt; run axe |
| Lorem ipsum / generic copy | "Build faster" | Give real content and voice rules |
| Over-claiming done | "Everything works!" | Require screenshots at 3 widths and a keyboard-only walkthrough |

---

## Part 7: Learning path and resources

**Week-agnostic order, about 10 steps:**

1. Read NN/g's 10 heuristics, then audit one app you use daily against them.
2. Read *Refactoring UI* (book/site tactics), then redesign one ugly screen using only spacing, weight, and color changes.
3. Learn type scales and contrast (use a contrast checker and a modular-scale tool).
4. Study 3 Tier A sites in devtools: inspect fonts, sizes, spacing, colors, transitions. Write down their tokens.
5. Skim WCAG 2.2 "What's New" and the quick reference; fix keyboard and focus on one project.
6. Build a tokens file (`tokens.css`) for a personal project.
7. Learn one headless component library (Radix or React Aria).
8. Run Lighthouse and axe on your build; fix the top 5 issues.
9. Do a 5-person task test of something you built.
10. Practice critique: take any AI output, write 5 specific problems using the vocabulary above.

**Reading and reference:**
- NN/g: nngroup.com (articles, heuristics, free poster)
- W3C WAI: w3.org/WAI (WCAG 2.2, Quick Reference, "What's New in 2.2")
- *Refactoring UI*: refactoringui.com
- Apple Human Interface Guidelines; Material Design 3; GOV.UK Design System (excellent forms and content guidance)
- Linear Method (linear.app/method); Stripe and Vercel sites for craft study
- Laws of UX (lawsofux.com), Smashing Magazine, web.dev (performance and accessibility)
- Tools: Figma, Chrome DevTools, axe DevTools, Lighthouse, WebAIM contrast checker, Stark or similar

---

## Part 8: Glossary

**Affordance** a cue about how to use something. **Breakpoint** width at which layout changes. **CLS** layout shift score. **CTA** call to action. **Design token** named design value. **Empty state** screen with no data yet. **Focus ring** visible keyboard-focus outline. **Heuristic** rule of thumb. **Hero** top section of a page. **IA** information architecture. **Kerning/tracking** letter spacing. **Leading** line height. **Microcopy** small UI text. **Modular scale** type sizes from a ratio. **Skeleton** placeholder shaped like content. **Semantic HTML** elements chosen for meaning. **Slop** generic default output. **Variable font** one file, many weights. **Visual rhythm** repeated spacing pattern. **WCAG** Web Content Accessibility Guidelines.
