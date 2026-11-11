# Prompt and Brief Kit: Talking to an LLM About Frontend Design

Principle (from the research): an open prompt returns the average. **Reduce the entropy of the request.** Every constraint removes probability mass from the generic result. Make the *design decisions yourself or with the model's help in a separate step*, write them down, then have the model implement inside them.

Workflow:

```
0. Intake questions (you answer)            -> Part 1
1. Design brief (one page)                  -> Part 2
2. Direction exploration (3 options, no code) -> Part 3
3. Tokens + system (written, committed)     -> Part 4
4. Build ONE screen, review with screenshots -> Part 5
5. State matrix + accessibility pass         -> Part 6
6. Remaining screens, reuse system           -> Part 7
7. Critique/fix loops and audits             -> Part 8
Cheat sheet: translate vague words          -> Part 9
```

---

## Part 1: Intake questions (answer these first; "don't know" is a valid answer)

Copy this block, fill it in, and paste it to the model. Where you answer "don't know," tell the model to propose 3 options with tradeoffs.

```markdown
## Purpose and users
1. What is this, in one sentence? (e.g., "A scheduling app for independent dog walkers.")
2. Who uses it? Role, tech comfort, device (phone/desktop), setting (office/outdoors/at night).
3. The single most important task a user must complete in under 60 seconds:
4. Top 3 other tasks, ranked:
5. What does the user feel before and after? (anxious -> relieved, bored -> curious)
6. Is this a marketing page, a web app/tool, a dashboard, content/editorial, e-commerce, or a mix?

## Success and constraints
7. What does success look like? (signups, task completion rate, time on task, trust)
8. Must-have platforms and browsers? Mobile first? Offline?
9. Tech stack constraints (framework, component library, CSS approach)? If none, say so.
10. Accessibility target (default: WCAG 2.2 AA)? Languages / RTL?
11. Performance budget (e.g., LCP < 2.5s on mid-range phone)?
12. Existing brand assets: logo, colors, fonts, voice guidelines? Attach them.

## Taste and references
13. Three sites/apps whose FEEL you want, and exactly what you like about each (type? density? motion? color? tone?).
14. Two sites/apps you do NOT want to resemble, and why.
15. Five adjectives for the brand. Then five adjectives it must NOT be.
16. Density: airy / balanced / dense? Tone: playful / calm / serious / luxurious / technical?
17. Light, dark, or both? Any color that must appear? Any color that must not?
18. One signature moment that people should remember (a hero interaction, a data visualization, a unique transition, a distinctive illustration style)? If none, ask the model for 3 ideas.

## Content
19. Real headlines, copy, product names, and sample data (or say "invent realistic ones for [domain]").
20. Real images/screenshots available? If not, what substitutes are acceptable (no blobs, no stock 3D)?
21. Voice: how does the product talk? Three example sentences in that voice.

## Scope
22. Screens/pages needed (list). Which one is the "hero" screen to design first?
23. Which states matter most (empty, loading, error, permissions, offline)?
24. What can be deferred?
```

---

## Part 2: The design brief template (one page; the source of truth)

Save as `DESIGN-BRIEF.md` in the repo and tell the model to read it at the start of every session.

```markdown
# Design Brief: [Product]

## 1. Product and audience
- One-liner:
- Primary user, context, device:
- Primary task (60 seconds):
- Emotional goal:

## 2. Design principles (3-5; each is a rule the model can use to break ties)
1. e.g., "Speed over decoration. Anything that delays the primary task is removed."
2. e.g., "Calm confidence. One accent color, generous space, no gradients."
3. e.g., "Show real data. Never lorem ipsum, never placeholder charts."

## 3. Visual direction
- Style in one sentence + reference URLs + what to take from each (not "copy it"):
- Anti-references and why:
- Density: [airy | balanced | dense]
- Theme: [light | dark | both; default = ...]
- Signature moment:

## 4. Tokens (see Part 4; paste the file or summarize)
- Type: [display font] / [text font] / [mono], scale, weights
- Color: neutrals, accent, semantic
- Space: base unit and scale
- Shape: radius personality, border and shadow rules
- Motion: durations, easing, what animates and what must not

## 5. Components and behavior
- Library to use (headless primitives + our tokens): 
- Required component list:
- Conventions: button hierarchy (1 primary per view), form validation timing, table behavior, toasts vs inline

## 6. Content and voice
- Voice rules:
- Words to use / avoid:
- Real sample content: (attach)

## 7. Accessibility and quality bar
- WCAG 2.2 AA; keyboard-complete; visible focus; reduced motion; contrast 4.5:1/3:1; targets >= 24px
- Responsive: 360, 768, 1024, 1440
- Performance: [budget]

## 8. Banned list (project-specific)
- e.g., purple/indigo gradients, nested cards, 3-equal-card feature rows, blurred blobs, emoji as icons, icon-in-tinted-square, ALL-CAPS eyebrow above every heading, centered-hero-plus-logo-strip by default, identical radius on everything, lorem ipsum

## 9. Definition of done
- Screenshots at 360/768/1440; keyboard walkthrough; axe/Lighthouse results; all states shown; no hard-coded colors or magic numbers; matches tokens
```

---

## Part 3: Direction exploration prompt (before any code)

Use this to avoid the first-guess average. Ask for *options with rationale*, not a finished page.

```text
Read DESIGN-BRIEF.md. Do not write code yet.

Propose THREE meaningfully different visual directions for [product]. They must differ in
typography, color strategy, layout structure, and motion personality, not just hue.
For each:
- Name and one-line concept
- Type pairing (display/text/mono) with reasons and a Google Fonts or open-source source
- A palette of 5-7 named colors with hex values and the role of each; state the contrast ratio of text/background pairs
- Layout idea for the hero screen (describe the grid and what is on it)
- One signature interaction
- Risks: who will dislike it and where it could fail usability
- Which famous defaults it deliberately avoids and what it replaces them with

Then recommend one and say what you would need from me to commit.
Do NOT default to Inter, Roboto, Arial, system fonts, purple/indigo gradients on white, a centered hero with three
equal cards, or tinted-square icons, unless you can justify them for this specific audience.
Also avoid replacing them with the next most common choice (for example Space Grotesk) without a reason tied to the brief.
```

---

## Part 4: Tokens and system prompt

Ask for the system as a file first, then build with it.

```text
Using the chosen direction, create these files and nothing else:
1. tokens.css with CSS custom properties, named by role not by appearance:
   --font-display, --font-text, --font-mono; --text-xs ... --text-4xl with line-heights; weights;
   --color-bg, --color-surface, --color-surface-raised, --color-border, --color-text, --color-text-muted,
   --color-accent, --color-accent-contrast, --color-success/warning/danger/info (each with a subtle background variant);
   --space-1 ... --space-12 on a 4px base; --radius-control, --radius-surface; --shadow-1/2/3;
   --duration-fast/base/slow; --ease-out, --ease-in-out; focus ring token.
   Include a dark theme override using prefers-color-scheme or a data-theme attribute.
2. A "tokens.md" explaining each choice in one line and the rules for use:
   when to use each type size, which color pairings are allowed, max one accent-filled button per view.
3. A /styleguide page that renders type scale, colors with contrast ratios, buttons in all states, inputs in all states,
   a card, a table, a modal, a toast, empty/loading/error examples.

Rules: components must consume tokens only; hard-coded hex, px values outside the scale, and inline styles are bugs.
Check every text/background pair against WCAG 2.2 AA and fix failures.
```

---

## Part 5: Build one screen, then inspect

```text
Read DESIGN-BRIEF.md, tokens.css and tokens.md.
Build ONLY the [hero screen name] using the existing tokens and [component library/headless primitives].
Rules:
- Semantic HTML first; real <button>, <a>, <label>, headings in order, landmarks.
- Use real content from [file/section]. No lorem ipsum, no placeholder charts.
- One primary action per view. Clear hierarchy: describe in comments-free code but explain in your reply what the 1st, 2nd and 3rd things the eye sees are.
- Responsive from 360px up. No fixed widths on text containers; max line length 75ch.
- Implement hover, focus-visible, active, disabled, loading for every interactive element.
- Motion: respect prefers-reduced-motion; animate transform/opacity only; one orchestrated load sequence max.

When done: run the app, take screenshots at 360, 768 and 1440 widths, and review them against the brief.
List five specific flaws you see in your own screenshots (spacing, hierarchy, contrast, alignment, content), then fix them and re-screenshot.
Do not say it is finished until the screenshots and a keyboard-only tab-through check support it.
```

---

## Part 6: State matrix and accessibility pass

```text
For [screen], produce a state matrix and implement every cell:
| Component | Default | Hover | Focus-visible | Active | Disabled | Loading | Empty | Error | Success | Long-content |
Use realistic edge data: 80-character names, 10,000 rows, zero rows, non-Latin text, missing images, slow network.
Show each state in /styleguide or in Storybook-style fixtures.

Then run an accessibility pass:
- Run axe (or Lighthouse accessibility) and list every issue with the fix.
- Tab through the whole screen: report focus order, any trap, any element without a visible focus indicator.
- Verify contrast for all text and UI boundaries (4.5:1 and 3:1).
- Confirm touch targets >= 24x24 CSS px (44px preferred on touch), forms have labels and error text tied to fields,
  drag actions have alternatives, and reduced motion is honored.
Fix everything, re-run, and show the numbers before and after.
```

---

## Part 7: Consistency prompt for later screens

```text
Build [screen 2]. Before writing code:
1. List the existing components and tokens from the repo that you will REUSE. Do not create a new component if one exists.
2. List any new component you need and why existing ones are insufficient.
3. Confirm you will use only existing tokens; if a token is missing, propose it and update tokens.md rather than hard-coding.
After building, diff against [screen 1]: check header, spacing, button hierarchy, form patterns, empty state tone, and motion for consistency, and fix mismatches.
```

---

## Part 8: Critique, polish, and audit prompts

### 8.1 Self-critique as a design reviewer
```text
Act as a senior product designer doing a ruthless critique of the attached screenshots against DESIGN-BRIEF.md.
Score 1-5 on: hierarchy, typography, color/contrast, spacing/rhythm, consistency, originality, state coverage,
accessibility, microcopy. For each score below 4, give (a) the exact problem, (b) why it hurts users, (c) a concrete CSS/markup fix.
Flag anything that looks like generic AI output (default fonts, gradient accents, equal-card rows, icon tiles, uniform radius, filler copy).
Then implement the top 5 fixes by impact.
```

### 8.2 Usability review using heuristics
```text
Review [flow] against Nielsen's 10 heuristics. For each heuristic list violations with the screen and element,
severity (cosmetic/minor/major/critical), and a fix. Pay special attention to system status, error prevention and recovery, and user control.
```

### 8.3 Anti-slop sweep
```text
Scan the UI for these defaults and replace each with a decision from DESIGN-BRIEF.md (do not just delete):
Inter/Roboto/system font; purple or indigo gradient; centered hero + logo strip; three equal rounded cards;
icons in tinted squares; blurred blobs/dot grids; same radius and shadow everywhere; nested cards; ALL-CAPS eyebrow above every heading;
vague headlines ("Build faster", "All-in-one"); uniform spacing; decorative emoji. Show before/after for each replacement.
```

### 8.4 Reference-based alignment
```text
Here is a screenshot/URL of a reference: [ref]. Do not copy it. Describe, in measurable terms, the decisions that create its feel:
type sizes and weights, line-height, spacing scale, grid, color ratios (e.g., 90% neutral / 8% surface / 2% accent), border/shadow use,
motion durations and easing, and information density. Then tell me which of these decisions fit my brief and which do not, and apply the ones that do via tokens.
```

### 8.5 Make it quieter, bolder, or more specific
```text
The screen feels [too generic / too busy / too timid]. Change exactly ONE of: type scale contrast, color ratio, spacing rhythm, or layout structure.
Explain the change, apply it, and show before/after screenshots. Do not touch anything else.
```

### 8.6 Microcopy pass
```text
Rewrite all UI text: buttons start with a verb describing the outcome; errors say what happened and how to fix it; empty states say what belongs here and the next step;
no jargon; no exclamation marks; keep to voice rules in the brief. Give a table of old vs new copy.
```

### 8.7 Performance and robustness
```text
Run Lighthouse (mobile). Report LCP, INP, CLS, and accessibility score. Fix the three largest causes. Check images have width/height and modern formats,
fonts use font-display: swap and are subset, and no render-blocking scripts. Show before/after numbers.
```

---

## Part 9: Translate vague words into instructions the model can act on

| You say | Say this instead |
|---|---|
| "Make it modern / clean" | "One type family, 4 sizes, 90% neutral palette with a single accent, 8px grid, no gradients, 1px borders at 8% opacity." |
| "Make it pop" | "Increase contrast between the primary action and everything else; use the accent only on the primary button and key data." |
| "Make it premium" | "Larger type contrast (display 56-96px vs 16px body), more whitespace (double current padding), restrained color, slow 300ms ease-out transitions." |
| "Make it fun" | "Rounded display type, saturated palette of 3 colors, playful empty-state illustrations, spring-like motion on success only." |
| "It feels cluttered" | "Reduce visible elements by half; group by proximity; move secondary actions into a menu; remove all borders you can replace with spacing." |
| "It feels flat / boring" | "Add hierarchy with size and weight, a surface elevation system, and one orchestrated entrance animation." |
| "It looks like AI" | "Run the anti-slop sweep and replace each default with a decision from the brief." |
| "Make it responsive" | "Design mobile-first at 360px; verify at 360/768/1024/1440; no horizontal scroll; stacking order matches reading priority; touch targets >= 44px." |
| "Make it accessible" | "WCAG 2.2 AA; semantic HTML; keyboard-complete; visible focus; 4.5:1 contrast; labels and error text tied to fields; reduced motion respected; show axe results." |
| "Match our brand" | "Use only tokens in tokens.css derived from the brand file; do not introduce new colors or fonts." |
| "Something feels off" | "Screenshot it, list misalignments, inconsistent spacings, and hierarchy conflicts with pixel values, then fix." |

---

## Part 10: Reusable system block (paste into any session or save as a rule/skill)

```text
You are building frontend UI. Follow these rules in every response.

Process: read DESIGN-BRIEF.md and tokens.css first. Ask me questions only when the answer would materially change the work; otherwise state an assumption and continue.
Never start with visual styling before purpose, flow, and structure are clear.

Design: commit to ONE coherent direction defined by the brief. Do not drift into default AI aesthetics: avoid Inter/Roboto/system fonts as a default, purple-indigo gradients on white,
centered hero + three equal cards, icon-in-tinted-square tiles, blurred blobs, uniform radius, nested cards, filler copy. Do not swap one default for another without a brief-based reason.
Typography carries hierarchy (size, weight, spacing), color is restrained (neutrals + one accent + semantics), spacing follows the scale, motion is purposeful.

Engineering: semantic HTML; native elements first; headless accessible primitives restyled with tokens; no hard-coded colors, fonts, or magic numbers; reuse existing components.

Quality: every interactive element has hover, focus-visible, active, disabled, loading; every data view has empty, loading, error, long-content states; WCAG 2.2 AA; reduced motion;
responsive at 360/768/1024/1440.

Verification: run it, screenshot at 360/768/1440, tab through with keyboard, run axe/Lighthouse, and report real results. State what you could not verify. Do not claim done otherwise.
```

---

## Part 11: Quick per-task prompt skeleton

```text
GOAL: [one sentence]
USER + CONTEXT: [who, device, situation]
PRIMARY TASK: [what must be easy]
SCREEN(S): [list]
CONTENT: [real copy/data or file]
STYLE: [reference URLs + what to borrow]; AVOID: [list]
SYSTEM: use tokens.css and existing components; no new colors/fonts
STATES: [which]
A11Y: WCAG 2.2 AA, keyboard-complete
DONE WHEN: screenshots at 360/768/1440, keyboard walkthrough, axe results, no hard-coded values
```

---

## Part 12: Your own review checklist (5 minutes per screen)

- [ ] Squint test: can I see the one most important thing?
- [ ] Is there exactly one primary action?
- [ ] Do related things sit closer together than unrelated things?
- [ ] Count fonts (<= 2), sizes (<= 6 in common use), colors (neutrals + 1 accent + semantics), radii (<= 3).
- [ ] Is every text/background pair readable (check with a contrast tool)?
- [ ] Tab through: always see where focus is? Everything reachable?
- [ ] Any state missing: empty, loading, error, disabled?
- [ ] Resize to phone width: still usable, no sideways scroll?
- [ ] Is the copy specific to this product, or could it sell anything?
- [ ] Does it look like every other AI-built app? What one decision makes it ours?
