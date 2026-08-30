---
name: skill-library-audit
description: 'Audit a multi-vendor agent-skill library for routing pathology — greedy descriptions, cross-pack territory claims, SKILL.md vs agents/openai.yaml drift, silently disabled invocation policy, dangling references. Use when adding a skill pack, merging two libraries, or when skills fire on the wrong thing. Ships a runnable analyzer at scripts/audit_skill_library.py. Scope boundary: this audits a SKILL LIBRARY, not application code — for authoring a single new skill use skill-creator.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Audit a skill library for routing pathology

A multi-vendor skill library is two systems at once: a **routing table** (which skill claims this file, import, command, prompt?) and a **retrieval index** (which document best matches this query?). Both have mature failure theory. Apply it, then spend judgment only where the mechanical check stops.

| Library artifact | Routing / IR analogue | Inherited failure mode |
|---|---|---|
| `description`, `promptSignals`, `retrieval.*` | query-document match terms | low-IDF terms and unbounded activation clauses → false fires |
| `importPatterns`, `bashPatterns` | exact-match FIB entry | territory claims across namespaces |
| `pathPatterns` | prefix route | overlapping prefixes with no longest-match rule |
| `chainTo`, `validate[].upgradeToSkill` | next-hop | loops, dangling next-hop, no-op self-route |
| `skipIfFileContains` | negative guard | unreachable guard → permanent false-positive nag |
| `priority`, `minScore` | local preference | inversion; threshold too low to gate |
| `overlay.yaml` vs `SKILL.md` | control plane vs data plane | drift — the fix is not in force |

## When not to run this

| Condition | Why skip |
|---|---|
| Single-vendor library | Vendor steering is correct behavior; territory claims are vacuous — one pack owns everything. |
| Under ~15 skills | Prior ≈ 1/N is 7%+; a description that is over-broad at N=89 is fine at N=12. Run only the exact checks (parse, drift, dangling, duplicate name). |
| No `overlay.yaml`, no `chainTo`, no `validate` | Nothing to route. Only §2 (IDF/breadth) applies. |
| Immediately after a merge of two packs | **Do run it** — merging is the event that breaks triggers nobody edited (§1). |

## Step 0 — run the analyzer

```bash
python3 scripts/audit_skill_library.py skills/ --json > audit.json    # also: --min-severity {low,medium,high}, --only SK008,SK012
```

Exit 1 if findings remain above the threshold, 2 if the root is unreadable. A file that fails to parse is finding SK001, not a tooling failure. If the script is absent, the exact checks are still hand-runnable: parse every `SKILL.md` and `overlay.yaml`; build the `name:` index; resolve every `targetSkill`/`upgradeToSkill` against it; deep-diff each `SKILL.md`/`overlay.yaml` pair. The heuristic checks below are not worth hand-running at scale.

Calibration: a tuned run over this repo (89 skills, 9 packs, 11 overlays, 187 routing rules) emits **20 findings — 4 high, 7 medium, 9 low**. A run emitting 150 is measuring house convention, not defects.

## Detector inventory

| Code | Class | Confidence | Fires on | Deliberately silent on |
|---|---|---|---|---|
| SK001 | Invalid/missing frontmatter | exact | YAML parse failure (e.g. unquoted `- @chat-adapter`) | — |
| SK002 | Duplicate skill `name:` | exact | two skills sharing a name | — |
| SK003 | Schema-outlier key placement | **heuristic** | key nested where siblings put it at root | packs that never use the key |
| SK004 | SKILL.md ↔ overlay drift | exact | key-by-key mismatch; scalar lists compared as **sets** | slot-by-slot list reordering |
| SK005 | Dangling route reference | exact | `targetSkill`/`upgradeToSkill` not in the name index | — |
| SK006 | No-op self route | exact match, **judgment defect** | target == own `name` | aggregated to one finding when it is a house idiom (see below) |
| SK007 | chainTo cycle | exact topology, graded heuristically | 2-cycles; long cycles containing a reported 2-cycle are suppressed | — |
| SK008 | Greedy description | **heuristic** | unbounded activation clause + cross-pack rivals sharing the full anchor conjunction | routers that declare themselves routers; skills carrying a scope-boundary clause; nested children; shared-prefix family siblings |
| SK009 | Cross-pack territory claim | **heuristic** | foreign-pack token in `pathPatterns`/`bashPatterns` | `chainTo` edges pointing at the owning pack |
| SK010 | Overlapping / shadowing rules | **heuristic** | conflicting targets; same-skill pairs high, cross-skill low | same-target pairs; catalogue rules (≥4 alternatives); mutual pairs owned by SK007 |
| SK011 | Unreachable guard token | **heuristic** | guard token with a near-miss against a real name | tokens merely absent from the library |
| SK012 | Vendor steering | **heuristic** | competitor artifact + advocacy language, tiered (see §4) | — |
| SK013 | Unreachable rule (guard always fires) | exact | guard match set ⊇ pattern match set | — |
| SK014 | Dangling prose skill reference | **heuristic** | skill name in body prose with no definition; negation tested per **clause**, not per line | "there is no `X` skill" |
| SK015 | Unscoped skill | **heuristic** | ≤12-word description, no scoping metadata, **and** a cross-pack rival sharing the anchor conjunction | absence of metadata alone |
| SK016 | Priority inversion | **heuristic** | prose says "load `X` first" while `X` ranks below the library median priority | topological priority ordering along edges |
| SK017 | Path-pattern shadowing | **heuristic** | a `pathPatterns` glob with **zero literal segments** (`**/*.tsx`) while another skill claims the same extension *with* literal segments | repo-wide claims with no scoped rival — breadth alone is not a defect |

Two denominators are easy to get wrong. **SK003 is sibling-scoped**: in this repo `validate:` appears in 14 files and routing metadata in 34 of 89 skills (33 of them in `vercel/`), so a library-wide majority schema is `name + description` and would flag all 33 Vercel skills. Compare per-pack, over the population that uses the key. **SK006 measures an idiom**: 56 `upgradeToSkill: <own name>` sites across 9 skills is "load me in full", not 56 bugs. Prevalence test — ≥3 skills and ≥15% of routed rules ⇒ one aggregate low finding. The genuine defect is narrower: a routing edge to self whose *pattern describes a foreign framework*.

## 1. The prior — why greedy triggers are catastrophic only at scale

A trigger is a diagnostic test for "is this skill right for this context?" With N skills the prior on any one skill is ≈ 1/N. At **N = 89**, prior = 0.0112. Sensitivity 0.90, specificity 0.95 (FPR 0.05) — a good test by ordinary standards:

```
P(right | fires) = (.90 × .0112) / (.90 × .0112 + .05 × .9888)
                 = .01008 / .05952 = 0.169
```

| Specificity | FPR | Posterior at N=89 | Wrong firings |
|---|---|---|---|
| 0.95 | 5×10⁻² | 17.0% | 5 in 6 |
| 0.99 | 1×10⁻² | 50.6% | 1 in 2 |
| 0.999 | 1×10⁻³ | 91.1% | 1 in 11 |

Required FPR for target posterior *p*: `fpr ≤ sens × prior × (1−p) / (p × (1−prior))`. For p = 0.80, sens = 0.90, N = 89: **FPR ≤ 0.0026 — wrong on fewer than 1 in 390 non-matching contexts.**

Two consequences drive the whole audit:

- **Merging packs breaks triggers nobody edited.** The same formula at N=20 permits FPR ≤ 0.0118 (1 in 84). Folding a 20-skill vendor pack into an 89-skill library tightens the bar **4.6×**. A description correctly scoped inside `vercel/` is defective in the merged library by arithmetic alone. Audit every imported pack as if newly written.
- **Loss is asymmetric.** A miss costs one explicit `Skill(x)` from the user. A false fire burns context, injects wrong-vendor guidance, and can silently redirect the task. Optimize precision; recover recall through aliases and explicit invocation.

## 2. IDF, and the thing IDF does not measure

`df(t)` = number of skills whose description + `promptSignals.phrases` + `retrieval.*` contain *t*; `idf(t) = ln(N / df(t))`. Measured over this repo's 89 descriptions — **use your own corpus's numbers, not these**:

| Band | Measured members | Read as | Required gating |
|---|---|---|---|
| df ≥ 15 (idf ≤ 1.8) | `user` 27, `vercel` 24, `skill` 23, `app` 18, `whenever` 17, `building` 17, `guidance` 17, `expert` 16, `api` 15 | no discriminative power | never load-bearing; needs a path/import gate |
| df 8–14 | `build` 14, `models` 12, `create` 11, `deployment` 10, `test` 8 | weak | `allOf` conjunction |
| df 3–7 | `deploy` 7, `agent` 6, `playwright` 5, `python` 4, `auth` 4, `zerogpu` 3 | usable | pair with one more term |
| df 1–2 | `supabase` 1, `@cursor/sdk` 1, `storage` 2, `sandbox` 2 | maximal | valid sole trigger |
| df 0 | `streamText`, `cacheComponents` | body-only; never fires | promote into `retrieval.entities` |

No content word clears df 33 here, and `storage` (df 2) outranks `playwright` (df 5) — thresholds copied from another library are wrong. **Rarity and breadth are also orthogonal:** `supabase` has this corpus's maximum idf (4.49) and *"Use when doing ANY task involving Supabase"* is still greedy, because the universal quantifier deletes every conjunction the anchor could have joined. Score both axes; an IDF floor alone reproduces none of the known cases.

| Axis | Signal | Detector |
|---|---|---|
| Breadth (primary) | universal quantifier (`ANY`, `whenever`, `all`), `even if they don't mention X`, no boundary clause | SK008 |
| Rarity (secondary) | idf floor over terms that can fire without conjunction | SK008 anchor scoring |
| Collision (required) | a **cross-pack** rival sharing the clause's **full** anchor conjunction | SK008 / SK015 |

All three must hold. Single shared words are not collisions — 9 descriptions contain `python`. Coherent sub-families (six `hf-cloud-*` skills sharing `sagemaker`) and a parent's own nested children are not rivals. A skill that declares itself an entry point, or carries an explicit `Scope boundary —` clause, is exempt from soft claims.

Known cases, and what actually made each one a defect: `supabase/supabase` — universal quantifier. `hf-cloud-python-env-setup` — three low-idf triggers (`python`, `install`, `environment`) with no boundary, hijacking every HF training task. `playwright-cli` — 12 words, no scoping metadata, **and** a cross-pack collision with the Adobe AEM E2E skill. Absence of metadata alone is not the defect: 55 of 89 skills here have none.

**Patterns are not scored.** The analyzer applies IDF to descriptions only. Read `pattern:` values yourself. Never quote a regex inside a table cell — the pipes and backticks corrupt it. `vercel/vercel-storage/SKILL.md:102`:

```
pattern: "sql\\s*`|from\\s+['\"]@vercel/postgres['\"].*sql"
```

The left alternate fires on any `sql` tagged template (drizzle, postgres.js, kysely) and announces `@vercel/postgres` sunset; the guard covers only the Neon migration target, so every other library nags.

## 3. Most-specific-wins, shadowing, ownership

Skill libraries have no longest-prefix rule, so a generic claim and a specific claim both win and both fire. Impose the ordering explicitly.

| Rank | Evidence class | Example |
|---|---|---|
| 1 | exact import / bash package specifier | `from '@ai-sdk/gateway'` |
| 2 | narrow path glob | `app/api/chat/**` |
| 3 | promptSignals conjunction meeting `minScore` | `allOf: [[structured, output]]` |
| 4 | bare description term | "storage" |

**Shadowing.** If match-set(A) ⊇ match-set(B), **A shadows B** — the larger match set is the subsumer. The `vercel-storage` case: a bare substring `@vercel/postgres` → `vercel-storage` is a strict superset of the anchored `from '@vercel/postgres'` → `nextjs`, so the bare rule shadowed the anchored one and both fired, to different targets. Keep the specific rule; delete or `noneOf`-exclude the general one. Regex containment is only *decidable in principle* — these are PCRE-flavored patterns and the analyzer approximates. Confirm every claimed containment with a witness string before reporting it.

**Ownership.** No pack declares the namespaces it owns; you construct that table from pack directories plus the package scopes each pack's own docs install. Then: patterns matching another pack's namespace are territory claims and get **deleted, not narrowed** — cross-pack interest is expressed as a `chainTo` edge to the owning skill. SK009 correctly reports zero on this repo (the Supabase claims were removed) and fires again the moment `supabase/**` returns to `vercel-storage`'s `pathPatterns`.

## 4. Vendor steering (multi-vendor libraries only)

A single-vendor plugin advocating its own products is correct. The same rule inside a multi-vendor library fires on a competitor the user has *already deliberately adopted* and argues against that choice. No single-vendor lint detects this: nothing is wrong with the rule in isolation, only with its placement.

**Test:** *would this message fire on a working codebase where the competitor is the user's intentional choice, and tell them to switch?*

| Shape | Example from this repo | Verdict |
|---|---|---|
| Factual migration — vendor's own package sunset by that vendor | `@vercel/kv` → `@upstash/redis` | keep |
| Interop / handoff — no pitch | `from '@supabase/supabase-js'` → `targetSkill: supabase`, "loading the Supabase skill for client, SSR, RLS, and Auth guidance" | keep |
| **Steering** — competitor works fine, message pitches ours as the "alternative" or "recommended" option | `from '@libsql/client'` → "Marketplace-native alternatives (Neon Postgres, Upstash Redis)" | **strip the pitch, keep any interop content, replace with a `chainTo`** |

Severity is not uniform — tier by what the library actually committed to:

| Tier | Condition | Example |
|---|---|---|
| HIGH | a competitor **pack exists** in the library, so the steer contradicts shipped content | the original `@supabase/supabase-js` → "Neon + Upstash alternatives" rule |
| MEDIUM | the rule's **own target skill supports the product** | `vercel/nextjs/SKILL.md:139` — "Modern Vercel apps should use Clerk, Descope, or Auth0" → `upgradeToSkill: auth`, whose entities list `NextAuth`/`Auth.js` |
| LOW | library has no content for the product; nothing is contradicted | `mongodb\|mongoose`, `convex`, `@libsql/client` → Marketplace pitch |

Procedure: enumerate every competitor product name appearing in any `message`, `description`, or `upgradeWhy`; join against the constructed ownership table; classify each hit; check `severity:` — a steering rule at `severity: error` is the highest-blast-radius variant.

## 5. Drift, and the mirror rule

Where both files exist, `overlay.yaml` is the machine-readable routing config and `SKILL.md` frontmatter is the human-edited copy. A fix applied to one and not the other **is not in force**. Live instance:

```
vercel/ai-sdk/SKILL.md:259   skipIfFileContains: 'gateway\(|@ai-sdk/gateway|@vercel/ai-gateway|ai-gateway'
vercel/ai-sdk/overlay.yaml:260 skipIfFileContains: 'gateway\(|@vercel/ai-gateway|ai-gateway'
```

The overlay never learned the real package name. `@vercel/ai-gateway` does not appear inside `@ai-sdk/gateway` as a substring, so in the overlay the guard cannot intersect the positive pattern's match set and the rule nags permanently on correct code. That is one defect wearing two codes: SK004 (drift) and SK011 (unreachable guard).

Rules: edit both files or the fix is not in force. Declare one side authoritative, regenerate the other, and gate the diff in CI — do not hand-sync. A near-miss claim needs a shared **tail** after stripping the npm scope (`@vercel/ai-**gateway**` vs `@ai-sdk/**gateway**`) or a ≥2-segment shared tail in the skill namespace (`next-**best-practices**` vs `react-**best-practices**`); "the library never mentions this token" proves nothing offline — `@vercel/otel` is a real package.

## 6. Not mechanically decidable — what you must judge

| Question | Why the script cannot answer | What to do |
|---|---|---|
| Does a referenced **tool** exist? | Requires the live MCP surface. `hf_jobs(` occurs ~79 times across the huggingface pack's bodies and `references/`, and one parent `SKILL.md` states the tool does not exist. | Confirm against the running tool list, then delete every reference or repoint it. |
| Is a self-route a bug or the idiom? | String equality is exact; intent is not. | Bug only if the rule's pattern describes a foreign framework. Otherwise leave it. |
| Which side of a drift is authoritative? | Diffing is exact; canonicity is a project decision. | Ask, or take the side whose value matches the skill body's prose. |
| Is a priority ordering intentional? | `chainTo` is unconditional — priority never suppresses it, so most "inversions" are graph shape. | Only act when prose says "load `X` first" and `X` ranks below the median. |
| Is a flagged term the skill's genuine identity? | IDF ranks; it does not decide. | Keep the term, add the gate. |

Body prose and `references/*.md` are in scope for SK014 and for tool references. Frontmatter-only auditing misses both.

## 7. Fix patterns

| Defect | Fix | Not a fix |
|---|---|---|
| Greedy description, pack **has** metadata | move identity into high-idf `retrieval.entities`; demote prose to `anyOf` scorers; raise `minScore` so no single low-idf term reaches threshold; add `noneOf` for the colliding skill | rewording the description |
| Greedy description, pack has **no** metadata (55 of 89 here) | add an explicit `Scope boundary — ...` clause naming the skill that owns the adjacent case | importing a metadata schema across pack boundaries — that is a project decision, name it and stop |
| Shadowed rule pair | keep the specific, delete or `noneOf` the general | reordering, unless the engine short-circuits — verify which, and say so in the report |
| Territory claim | delete the foreign pattern; add `chainTo` to the owning skill | narrowing the glob |
| Steering | strip the pitch, keep interop, replace with `chainTo` | deleting interop content — that is a regression |
| Dead guard | rewrite against the real package string; verify against a real file | adding more alternates |
| Silent disable | reindent to the placement its **pack siblings** use | reindenting to the library-wide majority |
| Any of the above, skill has an overlay | apply to both files | SKILL.md only |

## Output

One table, most severe first: `code | severity | skill | file:line | exact/heuristic | evidence | fix | blast radius`. Blast radius = firing frequency × `severity: error` vs `recommended`. Severity order: SK001/SK003 (silently disabled) → SK004 (fix not in force) → SK012/SK009 (user harm) → SK010/SK011/SK013/SK006/SK005 (wrong or dead routing) → SK008/SK015 (precision).

Every heuristic finding quotes the message or pattern text that drove the classification, and is labeled heuristic. Every exact finding quotes the two values that disagree. Verify before reporting: run each regex claim against a real string, parse every YAML file, resolve every target against the name index. A claimed dead guard that actually fires is worse than the guard. Metrics line: N; packs; overlay pairs and how many differ; routing rules; chainTo edges dangling / self / cyclic; unreachable guards; steering rules by pack and tier; descriptions carrying an unbounded activation clause.
