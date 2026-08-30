> Port note: this review was written against the Cursor_Skills snapshot. Host-specific Cursor Cloud / SDK skills were rewritten for Grok Build. See `docs/GROK-PORT.md`.

# Second-pass review — skills and plugins (2026-08-27)

Full pass over the current tree: 189 `SKILL.md` files across 19 packs, the plugin wrappers under `plugins/`, `.cursor-plugin/marketplace.json`, `scripts/`, and the docs. The original [REVIEW.md](REVIEW.md) covered the 63-skill snapshot (vercel, huggingface, adobe, cursor-cloud); this pass re-verifies the mechanical claims and reviews every pack added since: coding, academic, craft, microsoft365, plaud, ai-transfer, projects, langchain, playwright, cursor-sdk, pydantic-ai, prompt-optimizer, supabase, cursor-team-kit, first-party, and the hf-cloud-* / hf-mem Hugging Face additions.

## What was verified mechanically (all pass)

- 189 `SKILL.md` files; `.cursor/skills/` has exactly one unbroken symlink per skill; `plugins/` has one wrapper per pack; `marketplace.json` parses and lists all 19 packs.
- Activation policy holds at the frontmatter layer: exactly one skill (`first-party/proactive-agency`) lacks `disable-model-invocation: true`; counts in `README.md` and `docs/SKILL-PLUGIN-CATALOG.md` (189 / 188 / 19 / 100) all reconcile.
- Zero broken relative links in any `SKILL.md` or in the six root docs. Every referenced `references/` and `scripts/` file across all packs exists on disk. Every router→skill reference resolves (checked programmatically), with two prose-level exceptions noted below.
- `scripts/test_ai_plugin_bundle.py`: 17/17 pass. `apply-activation-policy.py` reports 0 files needing change.
- The original REVIEW.md "FIXED" items spot-checked (nextjs links, ai-sdk overlay `@ai-sdk/gateway`) are still fixed — no regressions.
- The library's own analyzer (`skill-library-audit/scripts/audit_skill_library.py skills`): 17 findings — 2 high, 6 medium, 9 low. None in the newly added packs; all in vercel/huggingface routing metadata.

## P0 — defeats the library's own design

1. **`skills/vercel/react-best-practices/AGENTS.md` (94 KB) is injected as an always-applied workspace rule in every session opened in this repo** — confirmed live in the session that produced this review. Cursor picks up `AGENTS.md` under `.cursor/skills/<name>/`, and the symlink farm exposes it. This silently violates the "only `proactive-agency` is always on" policy and burns ~25k tokens of context per session. `scripts/load-all.sh:109` also copies it into `~/.cursor/skills/react-best-practices/`, propagating the leak machine-wide. **Fix:** rename the file (e.g. `references/agents-reference.md`) or exclude `AGENTS.md` from the symlinked/copied tree; the same content already exists in `rules/` and the SKILL.md.

2. **The snapshot's patched skills do not govern auto-invocation.** In a live session the marketplace plugin caches (vercel/hf/adobe) still auto-load their *unpatched* copies, while the snapshot's patched copies are manual-only. Every P0 fix recorded in REVIEW.md is therefore inert for auto-triggered work. **Fix (choose one):** disable the three marketplace packs where this repo's snapshot is loaded, or accept that the snapshot is documentation-of-fixes rather than an overlay (and say so in README more bluntly than the current L261 warning).

3. **`skills/langchain/langchain-rag/SKILL.md:42`** — `from langchain_community.vectorstores import InMemoryVectorStore` is wrong; the class lives in `langchain_core.vectorstores`. The example fails at runtime as written.

4. **`skills/projects/nyx/SKILL.md:194`** — "Transparent bikini variant (local generation only — blocked in Cloud Agent)" is a written instruction for routing around a platform content restriction. Remove the line and the variant prompt at 196–198 regardless of where the file lives. Secondary: the bible carries ~63 MB of PNGs that `load-all.sh` copies into `~/.cursor/skills/`, and its `promptSignals` phrase `"character bible"` (L14) contradicts its own "trigger only when Nyx is named" rule (L4).

## P1 — analyzer + reviewer findings that will make an agent do the wrong thing

- **Dead guard token:** `skills/vercel/next-cache-components/SKILL.md:79` `skipIfFileContains: next-best-practices` — no such name anywhere in the library (typo for `react-best-practices`); the guard can never fire, so the rule nags permanently.
- **Live chainTo cycles (4):** ai-gateway↔ai-sdk (`gpt-4o`), ai-sdk↔workflow (`workflow`), eve↔vercel-connect (`@vercel/connect/eve`), nextjs↔vercel-storage (`@vercel/`). Each closes on a single literal in one file. Break one edge in each pair.
- **Greedy descriptions (analyzer HIGH/MEDIUM):** `huggingface-best/SKILL.md:4` and `adobe/appbuilder-project-init/SKILL.md:4` both claim prompts that "don't explicitly mention" their anchors — the clause this library already removed elsewhere as a defect.
- **Greedy structural claims in the coding pack:** `coding/ui-engineering/SKILL.md:11-14` claims `**/app/**/*.tsx` and bare `importPatterns: 'react'` — the exact low-IDF unbounded claim `skill-library-audit` teaches against. `microsoft365/excel-workbooks/SKILL.md:10` claims `**/*.csv`, contradicting its own scope boundary that routes CSV analysis to `coding-ecosystem-primer`.
- **Dangling prose routes to a pack-as-skill:** `microsoft365/teams-collaboration/SKILL.md:69`, `academic/academic-ecosystem-primer/SKILL.md:52,59`, `craft/ooda-lean-loop/SKILL.md:74`, `craft/workspace-mise-en-place/SKILL.md:59` route to `cursor-team-kit`, which is a pack directory, not a skill. Also `first-party/skill-library-audit/SKILL.md:4` routes to `skill-creator` and `code-review` — neither exists.
- **`skill-library-audit` fails its own audit (staleness):** L67 calibration says "89 skills, 9 packs … 20 findings"; a live run on the current 189-skill tree yields 17 (2/6/9). L187-193 presents the ai-sdk overlay drift as a "Live instance" — it is fixed on disk. Script docstring stops at SK016 though SK017 is implemented.
- **Factual errors:** `plaud/plaud-export-integrate/SKILL.md:26` invents "27+ export formats" (Plaud documents 12 type-format combinations, 8 distinct formats) and uses "27 formats" as a trigger anchor at L18. `academic/citation-literacy/SKILL.md:95` attributes `(n.p.)` to APA 7 (APA uses `para. n` / section names). `huggingface/hf-cloud-serving-image-selection/SKILL.md:30` future-dates TEI ("late 2026").
- **AI-transfer generator drift:** running `scripts/generate-ai-transfer-skills.py` dirties all 53 files (+1 blank line each) — the committed pack was not produced by the committed generator. Nine technique skills ship malformed GFM tables (header with no separator row), all traceable to `workflow` strings in the generator (e.g. `cartographic-zoom/SKILL.md:28`, `emergency-triage-compute/SKILL.md:29`). `ai-transfer-ecosystem-primer/SKILL.md:19` overclaims "default tier enables #1–50": the balanced tier's 5000 ms latency budget actually keeps 30 of 50. `TECHNIQUE_PLUGIN_IDS` ordering breaks the list-index=catalog-number property at #4–6. No test covers regeneration cleanliness, tier selection, or catalog ordering — which is why all four drifts survived a green suite.
- **Loader/manifest nits:** `load-all.sh:78` vercel pack description is garbled ("Manual except they do not include proactive-agency") and is propagated into `marketplace.json` and `plugins/vercel/.cursor-plugin/plugin.json`. `apply-activation-policy.py` ignores unknown args (`--help` runs the tool). `load-all.sh` loads the same skills three ways (project symlinks + `~/.cursor/skills/` copies + local plugins) on top of live marketplace plugins — up to four copies of one skill name in a session.
- **Vendored scaffolding shipped as content:** `supabase/supabase-postgres-best-practices/references/_sections.md:1-6` retains "Take the examples below as pure demonstrative…" template text; `_template.md` / `_contributing.md` are contributor files.

## Pack verdicts (new packs)

| Pack | Verdict | One-line judgment |
|---|---|---|
| langchain (12) | KEEP (1 MODIFY) | Internally consistent; one broken import is the only substantive defect. |
| playwright (3) | KEEP | Accurate, cleanly partitioned. |
| cursor-sdk (1) | KEEP | All 7 references exist; safe defaults (`autoCreatePR: false`). |
| pydantic-ai (1) | KEEP | Strongest provenance in the repo (vendored from the wheel it documents). |
| supabase (2) | KEEP (1 trivial MODIFY) | Accurate, falsifiable version gates; leftover template text. |
| cursor-team-kit (8) | KEEP | Safety-exemplary: no merge/main-push instructions; force-push gated twice; `--no-verify` prohibited in three places. |
| hf-cloud-* + hf-mem (7) | KEEP | Best-engineered set reviewed: every script flag verified against argparse; explicit spend gate before endpoint creation. |
| coding (7) | KEEP (1 MODIFY) | Coherent, closed reference graph; fix `ui-engineering` metadata. |
| academic (4) | KEEP (1 small MODIFY) | Right integrity posture; one APA error. |
| craft (3) | KEEP | `ooda-lean-loop` earns its place; primer is thin and duplicates its leaf's triggers. |
| microsoft365 (7) | MODIFY (2 QUESTIONABLE) | Factually careful but written as ribbon-menu click paths a Cursor agent cannot execute; never mentions `python-docx`/`openpyxl`/`python-pptx`/`pandoc` (zero hits in the library). Outlook/Teams have no agent-executable content. |
| plaud (8) | QUESTIONABLE (2 MODIFY) | Accurate, safety-conscious *product documentation* for hardware/app the agent cannot operate; only `plaud-export-integrate` (post-export file work) is agent-relevant. |
| ai-transfer (53) | KEEP core, TRIM rest | Well-engineered and safety-clean, but 28% of the library spent on metaphor-wrapped heuristics that are manual-only; ~10–12 techniques are concretely executable, 7 routers are pure indirection over the primer's own table, ~5 skills presuppose infrastructure (multi-model fusion, telemetry, cross-session memory) a Cursor session lacks. |
| projects/nyx (1) | RELOCATE | Structurally well-isolated, but it is 63 MB of project data — belongs in the consuming project, and L194 must go either way. |

## Recommendations, in order

1. Kill the `AGENTS.md` always-on leak (P0.1) — one rename plus a `load-all.sh` exclusion.
2. Decide the live-plugin question (P0.2): the snapshot's 40+ documented fixes protect nothing while the unpatched marketplace copies auto-load beside them.
3. Apply the one-line factual fixes: langchain import, dead guard token, `(n.p.)`, "27 formats", TEI date, garbled vercel description.
4. Remove nyx L194/196–198; move the pack (with its 63 MB of images) out of the shared library.
5. Fix the ai-transfer generator (tables + trailing newline), regenerate, and add three tests: regeneration-clean, tier-selection, catalog-ordering. Then decide whether the pack should shrink to primer + the executable dozen.
6. Refresh `skill-library-audit`'s self-referential numbers and drop its two dangling routes — an audit skill should survive its own audit.
7. For microsoft365: either add a "programmatic path" section per document skill (`python-docx`/`openpyxl`/`python-pptx`/`pandoc`) or mark the pack as Copilot-upload reference material. For plaud: reclassify as reference or shrink to two rewritten agent procedures (process exported transcript; convert-and-file exports).
8. Break the four live chainTo cycles and narrow the greedy descriptions/globs — cheap edits, all locations pinned above.
