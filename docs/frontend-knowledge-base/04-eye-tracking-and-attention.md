# 04. Eye-Tracking and Attention Research

How to read this file: each study lists design, sample, result, limits, and the design rule it supports. Eye tracking shows *where people look*, not *what they understood*. Fixations measure attention, not comprehension or preference.

## Vocabulary

- **Fixation:** eyes pause (about 200-300 ms typical) and take in information. **Saccade:** fast jump between fixations; vision is suppressed. **Gaze plot:** ordered fixations. **Heatmap:** aggregated fixation density. **AOI:** area of interest. **Regression:** backward saccade (re-reading).
- Metrics: time to first fixation, fixation count and duration per AOI, dwell, regressions, scanpath length.

## 1. Reading and scanning patterns (Nielsen Norman Group)

| Study | Design and sample | Result | Design implication | Limits |
|---|---|---|---|---|
| **F-pattern, 2006** ([NN/g](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content-discovered/)) | Eyetracking of 232 users across thousands of pages | Dominant pattern: horizontal read across the top, a shorter second horizontal read lower, then a vertical scan down the left. Users don't read word by word; first two paragraphs matter most; first words of lines get more fixations than later ones. | Put key information first; start headings, paragraphs, bullets with information-carrying words | Vendor research (NN/g); the report is commercial, but the articles are free; participants and tasks from 2006 |
| **Text scanning patterns, 2019** ([NN/g](https://www.nngroup.com/articles/text-scanning-patterns-eyetracking/)) | Later studies | Four main text patterns: **F-pattern** (appears without subheadings and bullets), **spotted** (skipping to find specific items like numbers or links), **layer-cake** (fixating on headings and subheads, skipping body), **commitment** (reading nearly everything when motivated). Right-to-left languages show a mirrored F. | Structure content (headings, bullets) to shift users from F to layer-cake, which is easier on them | Descriptive; not a causal experiment |
| **How people read online, 2nd ed.** ([NN/g](https://www.nngroup.com/articles/how-people-read-online/)) | Five studies over 13 years, over 500 participants, 750+ hours; 2019 study in Raleigh (48) and Beijing (12) | Nearly all 2006 gaze patterns still present in 2019 (F, layer-cake, spotted, commitment, exhaustive review, bypassing, zigzag, sequential, love-at-first-sight). Patterns similar across languages and cultures. | Behavior is stable across tech eras; design for scanning | Small Beijing sample; full report paid |
| **F-pattern misunderstood** ([NN/g](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/)) | Recent revisit | F is **bad** for users and business (they miss content); good design can prevent it; exists on mobile too. | Don't design *for* an F, design to avoid needing it | Same lab |
| **Three-column vs grid, peer-reviewed** ([Springer chapter](https://doi.org/10.1007/978-3-319-91803-7_20)) | 16 participants, two search tasks of varying complexity | Participants did **not** strictly follow an F; column layouts produced more extensive reading, faster target finding (significant for easy tasks), and higher preference. | Column-based layouts with headings help information search | Small n; lab; paywall status unknown |

## 2. Where attention goes on the page

| Study | Result | Design implication | Limits |
|---|---|---|---|
| **Scrolling and Attention, 2018** ([NN/g](https://www.nngroup.com/articles/scrolling-and-attention/)) | 120 participants, 130,000+ fixations on 1920×1080 screens. **57%** of viewing time above the fold, **74%** within the first two screenfuls (2160 px); 42%+ in the top 20% of general pages; on search results pages 47% in the top 20%. The 2010 study (1024×768) found 80% above the fold. Attention drops sharply after the fold, and within the first screen the top half got 65%+. | Put the most important content and navigation toward the top; people scroll but give less attention as they go | **Desktop only**; not directly transferable to phones where the "fold" is device-specific; varied page lengths |
| **Gist at a glance** ([PMC5945715](https://pmc.ncbi.nlm.nih.gov/articles/PMC5945715/), 2018) | In a 120 ms fixation at page center, people categorized pages into one of ten types well above chance, partly via text, and could localize menus and detect ads. | First impression forms in a fraction of a second; hierarchy, layout, and first-view text matter; clear page type signals | Static screenshots, lab; not a measure of preference |
| **Way Edges** ([ACM, Validating visual elements...](https://dl.acm.org/doi/pdf/10.1145/1367497.1367500)) | Eye-tracking showed a strong relationship between page areas receiving attention and framework-identified objects; "Way Edges" (visual constructs that group content into sections) significantly affected attention distribution; the authors speculate banner blindness owes as much to Way Edges as to color and size. | Boundaries and grouping direct attention; a distinct main-content region draws focus and side columns lose it | Small study, 2008; speculative on banner blindness |

## 3. Banner blindness and ad avoidance

| Study | Result | Design implication |
|---|---|---|
| **Impact of ad location and task** (Int. J. Human-Computer Interaction 30(3), 2014; [T&F](https://www.tandfonline.com/doi/full/10.1080/10447318.2013.847762)) | Eye tracking on e-commerce home pages: significant effects of banner location and task type. **Banner blindness was strongest for right-side banners and goal-directed tasks.** Visual appeal and page familiarity did not explain the effect. | Users with a goal filter anything banner-like; don't put critical information in banner positions or banner-like styling |
| **Role of emotional information** ([PMC9128483](https://pmc.ncbi.nlm.nih.gov/articles/PMC9128483/)) | Two experiments varying valence and arousal: against classical affective science, **neutral banners were recognized better** than positive or negative ones. | Emotional intensity doesn't beat banner blindness; relevance and fit with the task matter more **(judgment)** |

**Practical rule:** content that looks like an ad is ignored. Don't style important notices (cookie choices, key calls to action, security warnings) like banners, but also never disguise ads as content (FTC concern).

## 4. Forms and eye tracking

| Study | Result | Limits |
|---|---|---|
| **Inline validation** (Wroblewski with Etre, *A List Apart*, 2009; [article](https://alistapart.com/article/inline-validation-in-web-forms/)) | 22 users, 6 randomized variants of a registration form, with standard eye-tracking metrics. Best inline variant vs. submit-only control: **+22% success rate, -22% errors, +31% satisfaction, -42% completion time, -47% eye fixations**. Validating "after" the user finishes a field was 7-10 s faster than validating "while" or "before and while" typing, which also raised errors and annoyed users. | Practitioner study, small n, 2009 form; not peer reviewed (C). Direction is consistent with CLT. |
| **Label alignment** (Penzo 2006, summarized in [LukeW slides](https://static.lukew.com/WebForms_LukeW_101209.pdf)) | Reported: top-aligned labels let users capture label and input in one eye movement; fastest of the three alignments; right-aligned reduced fixations. | Secondhand slide summary; original study not retrieved (C). Use as a hypothesis and test your own forms. |

## 5. Eye tracking and reading difficulty

| Study | Result | Limits |
|---|---|---|
| **Shorter lines facilitate reading in those who struggle** ([PMC3734020](https://pmc.ncbi.nlm.nih.gov/articles/PMC3734020/)) | Eye tracking of high-school students with dyslexia reading on e-readers: a small device (shorter lines) gave **27% faster reading rate, 11% fewer fixations, over 2× fewer regressive saccades**, with no cost to comprehension. | Small sample of students with dyslexia; effects varied with visual attention span |
| **Line length in adults with dyslexia** (ACM/Springer 2021 study) | 20 adults, eye tracking: participants **did not prefer narrow lines**; no significant effect of line length on speed or comprehension; it affected motivation not performance. | Conflicts with the study above; treat narrow-line benefit as unsettled; offer user-adjustable width |
| **Font size for older adults** (systematic review, [PMC9376262](https://pmc.ncbi.nlm.nih.gov/articles/PMC9376262/)) | Older adults prefer larger fonts, but there is a critical size beyond which readability declines; one cited study found 10.5-15 pt phone fonts preferred; larger and serif fonts improved comprehension in a tablet study; the review recommends eye tracking among evaluation methods and a visual-angle metric. | Inconsistent methods across studies |

## 6. Design rules supported by eye-tracking evidence

1. **Front-load.** Put the point, the key term, and the next step in the first two lines and the first words of each line, heading, and bullet.
2. **Structure to defeat the F.** Headings, subheadings, short paragraphs, lists, and bold lead-ins guide scanning (layer-cake instead of F).
3. **Prioritize the top.** Most attention is above and near the fold on desktop; but the second screenful still gets a meaningful share (74% cumulative). Don't bury critical info or nav.
4. **Group with boundaries.** Whitespace, background shifts, and dividers form "Way Edges" that organize attention.
5. **Don't look like an ad.** Avoid banner shapes and right-rail placement for essential content.
6. **Make the gist immediate.** A one-glance first view that states what the page is and offers the next step.
7. **Design forms for few fixations.** Top-aligned labels, one column, inline validation after the field is complete, clear error text near the field.
8. **Offer reading controls.** Adjustable text size, spacing, and width serve older adults and readers with dyslexia; test a ~45-75 character measure by default.
9. **Test on target devices.** The fold, F-patterns, and fixation counts on desktop don't automatically transfer to mobile.

## 7. Running or buying an eye-tracking study

- **Webcam eye tracking** is cheaper but less precise; lab trackers give better accuracy.
- Recruit by task and ability; include participants who use glasses, older adults, and people with low vision or dyslexia if relevant.
- Use realistic tasks, not free viewing (task changes gaze: goal-directed vs free-viewing in banner studies).
- Define AOIs before the study; report n, device, screen size, and calibration quality.
- Combine with think-aloud and success metrics; fixation does not equal comprehension.
- **Free analogs:** session replay and heatmaps (click/scroll maps) are not eye tracking, but they show behavior; mouse movement is only a weak proxy for gaze. **(judgment)**
- Do **not** present eye tracking from screen readers, keyboard users, or voice users as covering them; they navigate differently (e.g., 71.6% of surveyed screen reader users start with headings).

## 8. Evidence quality summary

| Claim | Strength |
|---|---|
| People scan rather than read word by word on the web | Strong (replicated across NN/g studies over 13 years, multiple labs) |
| Top-of-page gets more attention | Strong for desktop; mobile less studied here |
| F-pattern is the only pattern | False; several patterns |
| Banner blindness is strongest for goal-directed tasks | Moderate (peer-reviewed, e-commerce pages) |
| Inline validation after completion helps | Moderate (one study, supported by broader practice) |
| Short lines help dyslexia | Mixed |
