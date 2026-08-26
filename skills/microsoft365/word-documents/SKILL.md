---
name: word-documents
description: "Create and format Microsoft Word documents: styles, headings, page layout, tables of contents, track changes, comments, mail merge basics, and export to PDF. Use when working in Word (.docx), formatting essays/reports, or when the user asks for Word-specific help. Scope boundary: citation style rules → `citation-literacy`; argument structure → `academic-writing`; PowerPoint → `powerpoint-decks`."
metadata:
  priority: 7
  pathPatterns:
    - '**/*.docx'
    - '**/*.doc'
  promptSignals:
    phrases:
      - "word document"
      - "microsoft word"
      - "format my essay"
      - "table of contents"
      - "track changes"
      - "word styles"
    allOf:
      - [word, format]
      - [docx, heading]
    anyOf:
      - "Microsoft Word"
      - ".docx"
    minScore: 6
---

# Word documents

**Rule:** Use **Styles** (Heading 1, Heading 2, Normal) — never manual bold/size for structure. Structure enables TOC, navigation, and accessibility.

## Essay / report setup

1. **Page Layout:** Margins per syllabus (usually 1" all sides); double-space body if required
2. **Style map:**
   - Title → Title style (or centered Heading 1, once)
   - Sections → Heading 1
   - Subsections → Heading 2
   - Body → Normal (12 pt Times New Roman or Calibri per style guide)
3. **Page numbers:** Insert → Page Number → top/bottom per APA/MLA (often top right after title page)
4. **Title page:** Separate section; suppress page number on first page if required

## APA / MLA in Word (mechanics)

| Task | Word action |
|---|---|
| Hanging indent (References) | Paragraph → Indentation → Hanging 0.5" |
| Running head (APA) | Header, different first page |
| Double spacing | Paragraph → Line spacing → 2.0 |
| Page break before References | Insert → Page Break (not Enter spam) |

Citation *content* → **`citation-literacy`**. Word handles *layout*.

## Track changes & collaboration

- **Review → Track Changes** before sharing drafts
- **Accept/Reject** in Review tab; resolve all before final submit
- **Comments:** anchor to selected text; reply in thread
- **Compare documents:** Review → Compare if merging group edits

## Table of contents

Requires Heading 1/2 styles applied first:
```
References → Table of Contents → Automatic Table 1
Update before print: right-click TOC → Update Field
```

## Common fixes

| Problem | Fix |
|---|---|
| Extra blank page | Show ¶; delete page break or empty paragraph |
| Images jump layout | Wrap text → Top and Bottom or In Line |
| Headers wrong on chapter 2 | Section breaks (Layout → Breaks) |
| Fonts look different on another PC | Embed fonts (File → Options → Save) or stick to common fonts |

## Export

- **PDF for submit:** File → Save As → PDF; check "Document structure tags" for accessibility
- **Plain text:** avoid unless LMS requires — loses formatting

## Copilot in Word prompts (examples)

- "Apply Heading 2 to all section titles and generate a table of contents"
- "Turn on track changes and suggest edits for clarity in the introduction"
- "Format the reference list with hanging indent per APA 7"

## Boundaries

- Does not write graded content end-to-end → pair with **`academic-integrity`**
- Complex macros/VBA → out of scope unless user explicitly requests
