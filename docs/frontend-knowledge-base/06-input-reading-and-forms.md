# 06. Input, Reading, and Forms

## 1. Pointing and touch targets

**Fitts's law:** time to hit a target grows as targets get smaller or farther. Finger touch adds occlusion and imprecision, so classic Fitts predictions underestimate error on touchscreens **(judgment; consistent with the studies below)**.

| Study | Population | Finding |
|---|---|---|
| Smartphone icon touching ([doi 10.3390/tae1010006](https://doi.org/10.3390/tae1010006)) | Adults, 75 size/spacing combinations, 2-11 mm | Hit rate rose and touch time fell with icon size; change point in hit rate around **6 mm**; the literature recommends **10 mm**; spacing had **no significant effect** here; roughly 10-15 ms saved per 1 mm. |
| One-handed thumb use (MobileHCI 2006, [ACM](https://dl.acm.org/doi/10.1145/1152215.1152260)) | Adults, thumb | No significant error differences for targets ≥ **9.6 mm** (discrete) and ≥ **7.7 mm** (serial); **9.2 mm** discrete and **9.6 mm** serial sufficient. |
| Older adults (smartphone, [doi 10.5555/2821679.2831275](https://doi.org/10.5555/2821679.2831275)) | Older adults | Accuracy significantly lower below **14 mm**; no differences above 14 mm. |
| Motor impairments (CHI 2017, [PDF](https://makeabilitylab.cs.washington.edu/media/publications/Findlater_ComparingTouchscreenAndMouseInputPerformanceByPeopleWithAndWithoutUpperBodyMotorImpairments_CHI2017.pdf)) | 16 with, 16 without upper-body motor impairments | Tapping errors on touch were over **3× higher than with a mouse** for the impairment group; at 6 mm error was **42.1%**, at 18 mm **7.0%**; authors recommend **at least 18 mm**. Spurious touches common. |
| WCAG 2.5.8 ([Understanding](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)) | Standard | Minimum **24×24 CSS px** or spacing offset; aimed at hand tremor, spasticity, quadriplegia, and specialized input devices. |

**Design rules**
- Meet 24×24 CSS px as a floor (AA); aim for **44×44 CSS px** on touch (platform guidance) which is roughly 7-10 mm depending on device density **(judgment: CSS px to mm varies by device)**.
- Use larger targets, 14-18 mm, for audiences that include older adults or people with motor impairments (public services, health, finance).
- Increase hit area with padding, not just visuals; keep distinct destructive actions away from frequent ones.
- Place primary touch actions in thumb reach on large phones; avoid tiny corner targets.
- Avoid drag-only interactions (2.5.7); support tap, click, keyboard alternatives; act on pointer-up (2.5.2).
- Don't make hover the only way to reveal controls.

## 2. Reading comfort

| Topic | Evidence | Rule |
|---|---|---|
| **Line length** | Literature review (Visible Language): recommendations that lines shouldn't exceed about **70 characters**; very short and very long lines both slow reading by disrupting eye movements. Experimental study (Int. J. Human-Computer Studies, 2001): **55 characters** per line gave the highest comprehension and was read faster than short lines. | Body text measure about **45-75 characters** (`max-width: 65ch`) **(rule of thumb consistent with evidence)** |
| **Font size, older adults** | Systematic review ([PMC9376262](https://pmc.ncbi.nlm.nih.gov/articles/PMC9376262/)): older adults prefer larger fonts; there is a critical size beyond which readability declines; studies report 10.5-15 pt preferred on phones; reading time and comprehension improve with larger text in tablet study; spacing helped. | Base 16px minimum; support browser text scaling; allow 200%+ without loss; avoid fixed-px containers |
| **Dyslexia** | Mixed: PMC3734020 found shorter lines improved speed 27% and halved regressions for students with dyslexia on small devices; a 2021 adult study found no effect on speed or comprehension and that readers did not prefer narrow lines. | Don't lock one layout; let users change width, spacing, and font; avoid justified text, tight spacing, and italic walls; moderate line length |
| **Structure** | Eye tracking (file 04) shows scanning | Headings, lists, short paragraphs, front-loaded sentences |
| **Plain language** | plainlanguage.gov, digital.gov | Short sentences, common words, active voice; question headings when they match user questions |
| **Contrast and color** | WCAG; NEI color deficiency | 4.5:1; never color alone |

Typography defaults to start from (judgment, then test): 16-18px body, 1.5-1.6 line-height, paragraph spacing ≥ 1em, ≤ 70ch, left-aligned (LTR), avoid all-caps text blocks, sufficient letter-spacing for small caps.

## 3. Forms

Evidence summary: inline validation after completion improved success, speed, satisfaction, and reduced fixations (file 04); validating mid-typing hurt. Label alignment evidence is secondhand.

### Form rules
1. **Fewer fields.** Ask only for what you need (COGA); remove optional fields or hide behind a link.
2. **One column.** Top-aligned labels; group related fields (`fieldset`/`legend`); logical order.
3. **Real labels, always visible.** No placeholder-only labels (placeholders vanish and test poorly for memory and contrast).
4. **Right input type and autocomplete.** `type=email|tel|url|number`, `inputmode`, `autocomplete` tokens (also WCAG 1.3.5 Identify Input Purpose AA); allow paste; allow password managers.
5. **Mark required and optional** clearly in text, not color only.
6. **Hints before, errors after.** Put format hints beside the field (`aria-describedby`); show errors after blur or submit, not on first keystroke; never erase user input.
7. **Error summary** at top on submit with links to fields; move focus to it; each error says what and how to fix.
8. **Don't make people re-enter** information (3.3.7). Persist across steps; prefill.
9. **Accessible authentication** (3.3.8): no memory or transcription tests; support passkeys and magic links with alternatives.
10. **Confirm and allow undo** for destructive, legal, and financial actions (3.3.4).
11. **Multi-step forms:** progress indicator with step names, back without loss, summary and edit before submit.
12. **Don't time out silently.** Warn and allow extension; save drafts.
13. **Disabled submit buttons** hide the reason; prefer enabled buttons plus clear errors, or explain why disabled. **(judgment, practitioner consensus)**
14. **Input masks and formatting:** accept varied formats (spaces, dashes) and normalize.
15. **Mobile:** large targets, correct keyboard, avoid horizontal wheels; avoid dropdowns for short lists (use radios).

## 4. Navigation and findability

- Use conventional global navigation; visible labels over icon-only; current location indicated (`aria-current`).
- Provide search for large sites; forgiving matching; helpful no-results state.
- Breadcrumbs for deep hierarchies; consistent placement of help (3.2.6).
- Descriptive link text; avoid "click here"; distinguish links from text (not color alone).
- HHS Research-Based Web Design & Usability Guidelines (209 guidelines, each rated for Relative Importance and Strength of Evidence, free PDF) cover homepage, layout, navigation, scrolling, headings, links, text, lists, widgets, graphics, writing, content organization, search, and usability testing. Use its importance and evidence ratings to prioritize. Source: https://www.hhs.gov/sites/default/files/research-based-web-design-and-usability-guidelines_book.pdf (A/B). Note: 2006 edition; predates mobile and modern frameworks.

## 5. Sources
See file 07.
