# 02. Accessibility Engineering

## 1. Who is affected (US data)

| Fact | Number | Source (grade) |
|---|---|---|
| US adults reporting at least one disability, 2022 | 1 in 4 (~61 million) | [CDC](https://cdc.gov/disability-and-health/articles-documents/disabilities-health-care-access.html) (A) |
| By type (2022 BRFSS model) | Cognition 13.9%, mobility 12.2%, independent living 7.7%, hearing 6.2%, vision 5.5%, self-care 3.6% | [CDC PLACES](https://www.cdc.gov/places/measure-definitions/disability.html) (A) |
| Adults 65+ with a disability | About 2 in 5 | CDC (A) |
| Color vision deficiency | About 1 in 12 men; up to 8% of men and 0.5% of women of Northern European ancestry have common red-green type | [NEI](https://www.nei.nih.gov/eye-health-information/eye-conditions-and-diseases/color-blindness) (A) |
| Screen reader users find info on long pages by | Headings 71.6%, Find 13.6%, reading through 6.4%, links 4.8%, landmarks 3.7%; 88.8% say heading levels are very or somewhat useful (n=1,539, Dec 2023-Jan 2024; self-selected respondents) | [WebAIM Survey #10](https://webaim.org/projects/screenreadersurvey10/) (B/C) |

Note CDC counts "serious difficulty" only, so it is a conservative estimate. Also, temporary and situational limits (broken arm, glare, noisy room, stress) cause similar barriers. **(judgment, consistent with USWDS "design generously")**

## 2. The state of the web (WebAIM Million, Feb 2025, home pages, automated WAVE only)

- 94.8% of 1,000,000 home pages had detectable WCAG 2 failures; average 51 errors per page.
- Six failure types made up 96% of errors, unchanged for 5 years:

| Failure | % of home pages |
|---|---|
| Low-contrast text | 79.1% |
| Missing alt text on images | 55.5% |
| Missing form input labels | 48.2% |
| Empty links | 45.4% |
| Empty buttons | 29.6% |
| Missing document language | 15.8% |

- Caveat from WebAIM: automated tools catch only a subset; zero detected errors does not mean accessible.
- Source: https://webaim.org/projects/million/2025/ (B).

**Implication:** fixing these six classes in your design system and components gets most of the way to automated cleanliness. Manual testing covers the rest.

## 3. POUR and the checks that matter most

W3C: four principles (Perceivable, Operable, Understandable, Robust); levels A, AA, AAA; 13 guidelines. Target AA.

### Perceivable
- **Text alternatives (1.1.1):** informative images get meaningful alt; decorative images get `alt=""`. Icons-only buttons get an accessible name.
- **Captions and transcripts** for media (1.2.x).
- **Structure (1.3.1):** use real headings, lists, tables with headers, form labels, landmarks. Info conveyed by style must exist in markup.
- **Meaningful sequence (1.3.2):** DOM order matches visual and reading order.
- **Reflow (1.4.10):** content works at 320 CSS px wide (400% zoom) without two-dimensional scrolling (except data tables, maps, etc.).
- **Contrast (1.4.3):** 4.5:1 normal text; 3:1 large text (18.66px bold or 24px). **Non-text contrast (1.4.11):** 3:1 for UI component boundaries, focus indicators, meaningful graphics.
- **Use of color (1.4.1):** never color alone.
- **Resize text (1.4.4)** to 200%; **text spacing (1.4.12)** overrides do not break layout.
- **Content on hover or focus (1.4.13):** dismissible, hoverable, persistent.

### Operable
- **Keyboard (2.1.1, 2.1.2):** everything works by keyboard; no traps.
- **Skip links / bypass blocks (2.4.1)**; **page titles (2.4.2)**; **focus order (2.4.3)**; **link purpose (2.4.4)**; **headings and labels (2.4.6)**; **focus visible (2.4.7)**.
- **2.4.11 Focus Not Obscured (Minimum, AA):** sticky headers, cookie banners, and chat widgets must not completely hide the focused element. Use `scroll-padding-top`.
- **2.5.7 Dragging Movements (AA):** provide a single-pointer alternative to drag (e.g., up/down buttons for reorder).
- **2.5.8 Target Size (Minimum, AA):** 24×24 CSS px, or spacing so a 24px circle centered on each undersized target doesn't intersect another. Exceptions: inline text links, user-agent controls, essential presentation, equivalent control available.
- **Motion and flashes:** no more than three flashes per second (2.3.1); provide pause/stop/hide for moving content over 5 seconds (2.2.2); honor `prefers-reduced-motion`.
- **Timing (2.2.1):** let users extend or disable time limits.
- **Pointer cancellation (2.5.2):** act on pointer up so users can abort; **label in name (2.5.3):** accessible name contains visible label.

### Understandable
- `lang` on `<html>` (3.1.1), and on parts in other languages (3.1.2).
- **Predictable (3.2.x):** no unexpected context changes on focus or input. **3.2.6 Consistent Help (A):** help mechanisms appear in the same relative place across pages.
- **Input assistance (3.3.x):** labels or instructions (3.3.2); error identification in text (3.3.1); suggestions (3.3.3); error prevention for legal/financial/data actions (3.3.4: reversible, checked, or confirmed).
- **3.3.7 Redundant Entry (A):** don't ask again for info already given in the same process, except where essential or for security. **3.3.8 Accessible Authentication (Minimum, AA):** no cognitive function test (memorizing, transcribing, puzzles) unless an alternative or assistance exists; allow paste and password managers.

### Robust
- **Name, role, value (4.1.2):** custom widgets expose correct semantics via native elements or ARIA. **Status messages (4.1.3):** announce toasts, validation results, loading and result counts with live regions without moving focus.

## 4. Implementation rules (engineering)

1. **Native HTML first.** `button`, `a`, `input`, `select`, `dialog`, `details`, `fieldset/legend`, `label`. First rule of ARIA: don't use ARIA if native will do. Bad ARIA is worse than none. **(widely accepted practice; W3C ARIA Authoring Practices)**
2. **One `h1`, no skipped levels, headings by meaning not size.** (VA.gov design system guidance; WebAIM survey shows why.)
3. **Focus management:** on route change, move focus to the new `h1` or main region; in modals, trap focus, restore on close, `Esc` closes; use `inert` for background.
4. **Visible focus:** `:focus-visible` with at least 3:1 contrast and a 2px-ish indicator; never `outline: none` without replacement.
5. **Forms:** visible `label` bound by `for`/`id`; `autocomplete` tokens; `aria-describedby` for hints and errors; `aria-invalid`; error summary at top linking to fields; don't rely on placeholder as label.
6. **Live regions:** `role="status"` (polite) for non-urgent updates; `role="alert"` for urgent errors; keep announcements short.
7. **Tables for data only,** with `th scope`, caption; avoid layout tables.
8. **Names:** icon buttons `aria-label` or visually hidden text; links describe destination; avoid "click here".
9. **Color tokens** tested for contrast in light and dark themes and for forced-colors mode (`forced-colors: active`, use system colors for borders and focus).
10. **Respect user preferences:** `prefers-reduced-motion`, `prefers-color-scheme`, `prefers-contrast`, text zoom, and font-size settings. Use `rem`.
11. **Do not disable zoom** (`user-scalable=no`).
12. **Media:** captions, transcripts, no autoplay with sound; controls keyboard accessible.
13. **Documents (PDF, Office):** tagged, titled, with reading order; or provide HTML equivalents. Title II covers documents that are web content. **(see rule text for exceptions)**
14. **Custom components:** follow W3C WAI-ARIA Authoring Practices patterns for keyboard behavior (tabs, menus, combobox, dialog). Prefer headless libraries that implement them (Radix, React Aria).

## 5. Testing: a layered method

| Layer | Tools | Catches |
|---|---|---|
| Automated, in CI | axe-core (`@axe-core/playwright`), Lighthouse, eslint-plugin-jsx-a11y, WAVE | Missing labels, alt, contrast, ARIA misuse (only a subset of failures) |
| Keyboard pass | Tab, Shift+Tab, Enter, Space, Esc, arrows | Traps, order, hidden focus, unreachable controls |
| Screen reader pass | NVDA + Firefox/Chrome (Windows), VoiceOver + Safari (macOS/iOS), TalkBack | Names, roles, announcements, reading order |
| Zoom and reflow | 200% text, 400% zoom at 1280px, 320 px width | Clipping, overlap, horizontal scroll |
| Visual preferences | Reduced motion, forced colors, dark mode, high contrast | Lost borders, invisible icons |
| Federal method | Section 508 ICT Testing Baseline, DHS Trusted Tester | Repeatable manual conformance testing |
| People | Test with disabled users, including screen reader, low vision, motor, and cognitive | Real usability, not just conformance |

Section 508 and USWDS both state that tool results need checking for accuracy and that manual testing is required.

## 6. Design-system acceptance criteria (copy into component definitions of done)

- Keyboard operable with documented key map.
- Accessible name, role, state, value via native or ARIA.
- Visible focus with ≥ 3:1 contrast; not obscured.
- Contrast ≥ 4.5:1 text, ≥ 3:1 UI, in all themes and states (hover, active, disabled-with-info, error).
- Target ≥ 24×24 CSS px (prefer 44px on touch).
- Works at 320 px width and 200% text.
- Reduced-motion variant.
- Error and status messages programmatically exposed.
- Passes axe with zero violations in Storybook or CI, plus manual screen reader notes.

## 7. Sources
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/ (A)
- What's New in WCAG 2.2: https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/ (A)
- Understanding 2.5.8: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum (A)
- CDC, NEI, WebAIM, USWDS links as above.
- VA.gov heading guidance: https://design.va.gov/content-style-guide/plain-language/structure-your-content (B, federal agency)

## Refresh note (2026-11-13)

WebAIM Million 2026 (February 2026): 95.9% of home pages had detectable failures (94.8% in 2025); pages with ARIA again had more detected errors (correlation, not proof). WebAIM screen reader survey #11 supersedes #10. See [master guide, chapter 8](../FRONTEND-MASTER-GUIDE.md#8-accessibility-engineering).
