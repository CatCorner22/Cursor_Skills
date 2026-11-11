# 03. Cognitive Load and End-User Frustration

## 1. The science in brief

| Concept | Finding | Source (grade) |
|---|---|---|
| **Working memory capacity** | Miller (1956) said ~7 chunks, but described it as a rough estimate. Cowan (2001) argued the real limit on the focus of attention is about **4 chunks (3-5)** when rehearsal, chunking, and long-term memory help are controlled. | [Cowan 2001, PubMed](https://pubmed.ncbi.nlm.nih.gov/11515286/); [Cowan 2010, PMC2864034](https://pmc.ncbi.nlm.nih.gov/articles/PMC2864034/); [Miller retrospective, PMC4486516](https://pmc.ncbi.nlm.nih.gov/articles/PMC4486516/) (A-) |
| **Cognitive load theory (Sweller)** | Working memory is limited in capacity and duration; load comes from **intrinsic** (task complexity and element interactivity), **extraneous** (poor presentation, distraction), and **germane** (productive learning effort). Design should cut extraneous load. | [Practical implications, PMC6694886](https://pmc.ncbi.nlm.nih.gov/articles/PMC6694886/); [Sweller et al. 20 years later](https://link.springer.com/article/10.1007/s10648-019-09465-5) (A-/B) |
| **Five strategies** | Combine text and visuals; present them contiguously/integrated; include only essential info; emphasize essential info; avoid too much transient visual information. | [PMC7940870](https://pmc.ncbi.nlm.nih.gov/articles/PMC7940870/) (A-; instructional context, applied to UI by analogy **(judgment)**) |
| **Split attention** | Having to consult several sources to build one picture raises extraneous load. | PMC6703991 |
| **RCT in an interface** | A posthospital dashboard designed with CLT (information integrated to avoid split attention) increased appropriate clinician actions, with **no increase in visit time**, **lower frustration**, lower perceived task load, and better detection of patient-safety risks versus usual care (randomized controlled non-clinical trial, simulated visit). | [Using CLT to improve follow-up visits, PMC6703991](https://pmc.ncbi.nlm.nih.gov/articles/PMC6703991/) (A-) |
| **External memory** | Interface features (visible task state, notes, saved items, recently viewed, comparison tables) offload working memory. Reading difficult text on mobile takes longer to reach the same comprehension, likely because the small screen holds less "external memory." | [NN/g Working Memory and External Memory](https://www.nngroup.com/articles/working-memory-external-memory/) (B) |
| **Hick-Hyman law** | Choice reaction time rises with the logarithm of the number of equally likely alternatives: RT = a + b·log2(n). Limits: practice, stimulus-response compatibility, very large sets, and sequential effects change the picture. | [Proctor & Schneider 2018 review](https://web.ics.purdue.edu/~dws/pubs/ProctorSchneider_2018_QJEP.pdf) (B, free PDF) |
| **Gist in one fixation** | Observers fixating the center of a page shown for only 120 ms classified it into one of 10 categories well above chance, partly using text they could read at a glance, and could reliably localize the menu bar and detect ads (ad detection was harder than menu localization). The paper reports 84.6% accuracy on its main task (two-choice, chance 50%). | [PMC5945715](https://pmc.ncbi.nlm.nih.gov/articles/PMC5945715/) (A-) |

**Reading the evidence skeptically:** CLT is from learning research; UI studies are fewer. The "7±2" rule is a myth as a design rule (Cowan). Hick's law applies to equally likely alternatives, so organizing and ranking choices helps more than counting them. **(judgment)**

## 2. W3C cognitive accessibility (COGA), a design checklist with legal relevance

"Making Content Usable for People with Cognitive and Learning Disabilities" (W3C Working Group Note, 2021; supplemental to WCAG, not required for conformance). Objectives:

1. Help users understand what things are and how to use them: familiar icons, terms, and patterns; standard link styling.
2. Help users find what they need: clear layout, headings, boundaries, regions.
3. Use clear content: easy words, short sentences and blocks of text, clear images and video.
4. Help users avoid mistakes: ask only for what you need; make correction easy.
5. Help users focus: remove distractions; avoid interruptions.
6. Avoid reliance on memory: show information instead of making users recall it.
7. Provide help and support: findable, contextual, human contact.
8. Support adaptation and personalization.

Source: https://www.w3.org/TR/coga-usable/ and https://www.w3.org/WAI/cognitive/ (A, informative). Cognition is the most prevalent self-reported disability type in US adults (CDC 13.9%), so this is not an edge case.

## 3. Cognitive load reducers (design rules tied to evidence)

| Rule | Why | Concrete practice |
|---|---|---|
| **One primary action per view** | Hick; focus | One filled button; the rest secondary or ghost |
| **Chunk and group** | Cowan; Gestalt proximity | Groups of ~3-5 related items; headings; whitespace between groups |
| **Show, don't make them remember** | Recognition over recall (NN/g heuristic 6) | Visible options; recent items; autocomplete; persistent summary in multi-step flows |
| **Progressive disclosure** | Intrinsic load management | Advanced options behind "More"; reveal fields as relevant |
| **Integrate related info** | Split attention | Put the label next to its control; units next to numbers; error beside the field; avoid sending users to another tab to complete one decision |
| **Use familiar patterns** | Jakob's Law; COGA | Standard nav, search, cart, form patterns; underlined links |
| **Plain language** | Reading load | Short sentences, active voice, common words, front-load key info; federal plain language guidelines (plainlanguage.gov, digital.gov) |
| **Descriptive question or topic headings** | Scanning; screen reader navigation | digital.gov: question headings help users who come with questions; shorter than the content below them |
| **Consistency** | Reduces learning | Same action, same label, same location, same component |
| **Reduce transient information** | CLT strategy 5 | Avoid auto-advancing carousels, disappearing toasts for important info, hover-only content (see WCAG 1.4.13) |
| **Defaults and smart prefill** | Fewer decisions | Sensible defaults; remember choices; WCAG 3.3.7 redundant entry |
| **Chunk long tasks** | Working memory | Multi-step with clear progress and the ability to go back; save progress |
| **Make the system state visible** | NN/g heuristic 1 | Loading, saved, synced, offline indicators |
| **Support interruption** | Real life | Autosave; resume; session timeout warnings with extension (WCAG 2.2.1) |

## 4. What causes frustration (and the fixes)

| Frustration trigger | Evidence or standard | Fix |
|---|---|---|
| Slow or unresponsive UI | Nielsen limits; Core Web Vitals (file 05) | Optimistic UI, responses within 100 ms, feedback for >50ms work (RAIL) |
| Layout shift under the cursor | CLS metric (≤ 0.1) | Reserve space for images/ads/embeds; no late-inserted banners above content |
| Blank screens while waiting | Perceived-wait studies: blank page worst (21 participants, exploratory) | Skeletons or progress feedback |
| Premature or cryptic errors | Wroblewski: validating while typing slowed completion 7-10 s and annoyed users | Validate on blur or after a pause; clear message beside the field |
| Losing input after an error | WCAG 3.3.1-3.3.4, 3.3.7 | Preserve all entries; show an error summary |
| Hidden or tiny targets | Touch research (file 06) | ≥ 24 px minimum; 44 px or ~10 mm on touch; 18 mm for motor-impaired users |
| Dead ends | NN/g heuristics 3 and 9 | Always provide next steps, back, undo, empty-state actions |
| Surprise context changes | WCAG 3.2.x | No auto-submit on select; no focus jumping |
| Dark patterns (hard cancellation, fake urgency) | FTC 2022 | Symmetric choices; easy exit |
| Inaccessible CAPTCHAs and logins | WCAG 3.3.8 | Offer alternatives; allow paste and password managers; passkeys |
| Walls of text | Eye-tracking: F-pattern in unstructured text | Headings, lists, bolded keywords, short paragraphs |
| Intrusive popups | Banner-blindness research and user annoyance **(judgment)** | Delay and trigger by user intent; make dismissal easy; don't cover content on mobile |
| Form length | Redundant fields raise load (WCAG 3.3.7; COGA "ask only for what you need") | Remove fields; use autofill; split by logic |

## 5. Designing messages that reduce frustration

**Error message formula:** what happened, why (if known), what to do. Example: "Card number must be 16 digits. You entered 15. Check the number on the front of your card." Avoid blame, codes alone, and ALL CAPS. Place next to the field, associate with `aria-describedby`, and set focus appropriately.

**Empty states:** what belongs here, why it's empty, one action.

**Confirmation:** state the outcome and what happens next; provide undo for reversible actions.

**Destructive actions:** specific button labels ("Delete project"), summarize consequences, offer undo or a delayed delete. WCAG 3.3.4 requires reversibility, checking, or confirmation for legal, financial, and data-deleting submissions.

## 6. Measuring cognitive load and frustration

| Method | Notes |
|---|---|
| **NASA-TLX** (public-domain NASA instrument) | Self-reported workload across six dimensions; 16-experiment development, six subscales; verified in [13](13-ux-research-methods-and-measurement.md) |
| **UEQ-S** | Short UX questionnaire (8 items) from the UEQ family (six scales); used in the 2026 AI-vs-human study; details in [13](13-ux-research-methods-and-measurement.md) |
| **SUS** | 10-item usability scale; average score about 68; see [13](13-ux-research-methods-and-measurement.md) (origin-date conflict noted) |
| **Task success, time on task, errors, rage clicks, backtracking** | Behavioral signals from usability tests and analytics |
| **Eye tracking: fixation counts and regressions** | Inline-validation study: 47% fewer fixations indicated easier processing |
| **Think-aloud with 5 users per segment** | Cheap, qualitative |
| **Accessibility testing with real users** | Finds issues automated tools miss |

## 7. Sources
See file 07 for the full list and access status.
