---
name: citation-literacy
description: 'Format and check academic citations: APA 7, MLA 9, and Chicago (notes-bibliography), in-text vs bibliography, common mistakes, and when to use which style. Use when the user asks how to cite a source, format references, or fix bibliography entries. Scope boundary: writing the paper body → `academic-writing`; claim-level attribution → `journalistic-attribution`; DOI/URL lookup mechanics only when tied to a citation question.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Citation literacy

**Rule:** Cite to **credit**, **locate**, and **support** — not to decorate. Every in-text cite must appear in the reference list and vice versa.

## Pick the style

| Style | Typical disciplines | In-text | List title |
|---|---|---|---|
| **APA 7** | Psychology, nursing, education, sciences | (Author, Year) | References |
| **MLA 9** | Humanities, literature, some composition | (Author page) | Works Cited |
| **Chicago NB** | History, some humanities | Footnote + bib | Bibliography |

When unsure: **syllabus wins** → department guide → APA as default for sciences.

## APA 7 quick patterns

**Journal article:**
```
Author, A. A., & Author, B. B. (Year). Title of article. Title of Periodical, volume(issue), pages. https://doi.org/xxxxx
```
In-text: `(Author, Year)` or `(Author, Year, p. 12)` for direct quote.

**Book:**
```
Author, A. A. (Year). Title of work: Subtitle. Publisher.
```

**Website (no author):**
```
Title of page. (Year, Month Day). Site Name. URL
```

**Common APA fixes:**
- Sentence case for article titles; italicize journal name and volume
- DOI as URL when available
- `Retrieved from` dropped in APA 7 for most URLs
- Et al.: 3+ authors from first cite in APA 7

## MLA 9 quick patterns

**Book:**
```
Author Last, First. Title of Book. Publisher, Year.
```
In-text: `(Author page)` — no comma between name and page.

**Article:**
```
Author Last, First. "Article Title." Journal Name, vol. X, no. Y, Year, pp. XX-XX.
```

**Website:**
```
Author Last, First. "Page Title." Website Name, Day Month Year, URL.
```

## Chicago notes-bibliography (short)

First footnote: full cite. Later notes: shortened. Bibliography: full entries alphabetically.

## In-text rules (all styles)

| Do | Don't |
|---|---|
| Cite paraphrases, not just quotes | Cite only at end of paragraph without mapping to source |
| Introduce quotes ("According to X…") | Drop block quotes without analysis |
| Use `et al.` per style rules | Invent page numbers |

## Missing metadata workflow

If author/date/page unknown, say so and use style-specific placeholder (e.g., APA: `(n.d.)`, `(n.p.)`) — **never guess** a year or page.

## Output format

When asked to cite, return:
1. **In-text example** for the sentence context given
2. **Full reference-list entry**
3. **Style note** if ambiguous (e.g., preprint vs published)

## Boundaries

- Verify against the current style manual for edge cases (legal, social media, AI-generated sources — many institutions ban citing a chatbot as a source)
- This skill formats; **`journalistic-attribution`** and **`huggingface-papers`** help find and name real sources
