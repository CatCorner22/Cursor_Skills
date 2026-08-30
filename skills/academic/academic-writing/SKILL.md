---
name: academic-writing
disable-model-invocation: true
description: "Structure and revise academic prose: thesis statements, outlines, paragraphs, introductions/conclusions, argument flow, and tone by assignment type (analytic, argumentative, reflective, compare-contrast, lab IMRaD). Use when writing or editing essays, discussion posts, reading responses, or when the user asks for help organizing a paper. Scope boundary: citation formatting → `citation-literacy`; named sources and attribution → `journalistic-attribution`; lecture-to-notes → `plaud-lecture-notes`; slides → `powerpoint-decks`."
metadata:
  priority: 8
  promptSignals:
    phrases:
      - "write an essay"
      - "thesis statement"
      - "outline for paper"
      - "revise my draft"
      - "introduction paragraph"
      - "argumentative essay"
      - "discussion post"
    allOf:
      - [essay, thesis]
      - [paper, outline]
      - [revise, paragraph]
    anyOf:
      - "academic writing"
      - "reading response"
    minScore: 6
---
# Academic writing

**Rule:** Every draft serves a **claim** — a sentence you could disagree with. If no one could disagree, it is description, not argument.

## CRAFT workflow

```
C — Claim: one-sentence thesis (debatable, specific, scoped to assignment)
R — Reasons: 3–5 supporting points (each needs evidence)
A — Arrangement: outline with one idea per paragraph
F — Flow: topic sentence → evidence → analysis → link back to thesis
T — Trim: cut throat-clearing, passive filler, and duplicate points
```

## Thesis checklist

- **Specific:** names the topic, stance, and scope ("In X, Y because Z" — not "X is important")
- **Debatable:** a reasonable reader could push back
- **Provable:** matchable to evidence within page limit
- **One sentence** (two only if the prompt requires a complex claim)

## Paragraph template (TEAL)

| Part | Job |
|---|---|
| **T**opic sentence | Mini-claim for this paragraph |
| **E**vidence | Quote, data, or example (introduced, not dropped) |
| **A**nalysis | *Why* this evidence supports the topic sentence — your voice |
| **L**ink | Tie to thesis or transition to next paragraph |

**Never end a paragraph on a quote.** Analysis is where grades live.

## Assignment types

| Type | Structure |
|---|---|
| **Argumentative** | Intro + thesis → 2–3 body (counterargument optional) → conclusion that synthesizes, not repeats |
| **Analytic** | Thesis on *how/why* the text works → body by element (theme, form, context) → conclusion on significance |
| **Compare/contrast** | Point-by-point or block; thesis names the meaningful difference, not "both are similar and different" |
| **Reflective** | Concrete moment → insight → connection to course concept (still needs structure, not diary) |
| **Discussion post** | Claim in first 2 sentences → one piece of evidence → question to peers |

## Revision passes (in order)

1. **Argument:** Does every paragraph serve the thesis? Cut orphans.
2. **Evidence:** Is every claim backed? Flag `[NEED SOURCE]` rather than invent.
3. **Analysis:** Replace summary with "so what?"
4. **Clarity:** Short sentences; define jargon once; active voice default
5. **Mechanics:** Grammar last — do not polish a hollow argument

## Tone

- Third person or discipline norm unless prompt says "I"
- No inflated diction ("utilize" → "use")
- No hedge stacks ("might possibly perhaps")
- Confidence proportional to evidence

## Boundaries

| This skill | Not this skill |
|---|---|
| Structure and revise *your* draft | Write the entire graded submission to submit unchanged |
| Teach argument craft | Replace reading the assigned texts |
| Suggest where evidence is needed | Fabricate citations — use `citation-literacy` + real sources |

Always confirm the course AI-use rules and pair **`citation-literacy`** before generating long draft text. Do not fabricate sources.
