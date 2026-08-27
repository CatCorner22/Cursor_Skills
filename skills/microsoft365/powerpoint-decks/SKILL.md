---
name: powerpoint-decks
description: "Structure and design Microsoft PowerPoint presentations: slide layouts, master slides, visuals, speaker notes, animations restraint, and export. Use when building .pptx decks for class, work, or conferences. Scope boundary: argument craft for speaker notes → `academic-writing`; Word handouts → `word-documents`; Copilot custom skill upload format → compatible with this SKILL.md structure."
metadata:
  priority: 7
  pathPatterns:
    - '**/*.pptx'
    - '**/*.ppt'
  promptSignals:
    phrases:
      - "powerpoint"
      - "slide deck"
      - "presentation slides"
      - "speaker notes"
      - "pptx"
    allOf:
      - [powerpoint, slide]
      - [presentation, deck]
    anyOf:
      - "Microsoft PowerPoint"
      - ".pptx"
    minScore: 6
---

# PowerPoint decks

**Rule:** **One idea per slide.** If the slide needs a paragraph, split it or move detail to speaker notes.

## Deck architecture

```
1. Title — topic, your name, course/date
2. Hook / question — why care (optional for class)
3. Agenda — 3–5 bullets max
4. Body slides — one claim each, evidence visual
5. Summary — restate takeaways (not copy-paste of body)
6. Q&A or references
```

Narrative depth → **`academic-writing`**. This skill covers **PowerPoint mechanics**.

## Design defaults (class-friendly)

- **Theme:** built-in simple (Office / Ion / Facet) — avoid busy templates
- **Font:** 28–32 pt titles, 18–24 pt body minimum
- **Contrast:** dark text on light background (projectors wash out pastels)
- **Images:** full-bleed only when intentional; credit sources in notes
- **Animations:** appear on click for complex builds; never gratuitous spin

## Slide layouts

| Layout | Use |
|---|---|
| Title Slide | Opening |
| Title and Content | Standard bullet + optional figure |
| Section Header | Chapter breaks |
| Two Content | Compare/contrast |
| Picture with Caption | Evidence slide |
| Blank | Custom diagram only |

## Slide Master

View → Slide Master → set fonts/colors once; child slides inherit.
Fix recurring logo/footer here, not slide-by-slide.

## Speaker notes

- Write what you'd **say**, not what's on the slide
- Timing cue: `~2 min` per major section
- Citation for quotes/images in notes if not on slide

## Charts from Excel

Insert → Chart → prefer **Edit Data in Excel** link so updates propagate.
Label axes; cite data source in footnote.

## Export & present

- **PDF:** File → Export → PDF (fonts embed reliably)
- **Presenter View:** Slide Show → Use Presenter View (notes + next slide)
- **Record:** Slide Show → Record for async class submissions

## Copilot in PowerPoint

- Upload custom skills via **Manage skills** (OneDrive sync)
- Invoke with **Choose skills** or `@skill-name` in prompt box
- Skill folder name must match `name` in SKILL.md frontmatter

Example Copilot prompts:
- "Add a section header slide and three content slides from this outline"
- "Suggest a simpler layout for the chart slide"
- "Generate speaker notes for slide 4"

## Accessibility

- Review → Check Accessibility
- Alt text on every image (right-click → Edit Alt Text)
- Don't rely on color alone for meaning

## Boundaries

- Prezi/Keynote/Google Slides → different apps
- Video editing → out of scope
