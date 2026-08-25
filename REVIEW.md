# Line-by-line skill review

Reviewed every `SKILL.md` in [skills/](skills/) after the 2026-08-25 snapshot (63 skills). Line numbers refer to this repo, not the live plugin cache. Supporting files were read when a skill tells the agent to follow them, or when a claim had to be checked against a script.

**How to read this.** KEEP means the skill is accurate enough to leave as-is. MODIFY means a specific line will make an agent do the wrong thing. MERGE means two files say the same thing and one should be canonical. DISABLE-WHEN-UNUSED means leave the file in the snapshot but do not auto-load it on typical work.

Plugin owners must apply most fixes. This repo is a stable copy, not a live overlay.

---

## Highest-priority bugs (agent will do the wrong thing)

**Patched in this repo (2026-08-25 follow-up).** Live plugin caches may still have the old text until those packs update.

1. **`skills/vercel/nextjs/SKILL.md`** — **FIXED:** 18 body links now point at `./references/…`.
2. **`skills/vercel/vercel-sandbox/SKILL.md`** — **FIXED:** description is Chromium/`agent-browser`; `minScore` raised; `child_process` chains to this skill.
3. **`skills/huggingface/huggingface-paper-publisher/SKILL.md`** — **FIXED:** documents only `index`/`check`/`link`/`create`/`info`/`citation`; `search` is stubbed; claim/POST-index go to `huggingface-papers`.
4. **`skills/huggingface/huggingface-best/SKILL.md:133`** — **FIXED:** fallback table added; Q4 math is ×2; token via `HF_TOKEN`.
5. **`skills/cursor-cloud/canvas/SKILL.md:3`** — **FIXED:** description filled; SDK path relative to the skill + `~/.cursor/…` fallback.
6. **`skills/adobe/appbuilder-action-scaffolder/SKILL.md`** — **FIXED:** guardrail matches `_shared` (extension → `ext.config.yaml`; standalone → `application.runtimeManifest`).
7. **`skills/cursor-cloud/env-setup/references/migrate-to-builds.md`** — **FIXED:** canonical file no longer asks to Save; env-setup copy is a pointer.
8. **`skills/huggingface/hf-mcp/SKILL.md`** — **FIXED:** live tools (`hub_repo_search`, `hub_repo_details`, `gr1_z_image_turbo_generate`, `hf_fs`); jobs/docs fall back to `hf-cli`.
9. **`skills/vercel/react-best-practices/SKILL.md:3`** — **FIXED:** performance-only description; no a11y claim.
10. **`skills/vercel/workflow/SKILL.md`** — **FIXED:** dropped `*workflow*` globs; narrower `anyOf`; `minScore` 8; `setTimeout` stays in workflow.
11. **`skills/huggingface/hf-cli/SKILL.md:3`** — **FIXED:** narrowed description; `--format` is `auto|human|agent|json|quiet`.
12. **`skills/vercel/auth/SKILL.md`** — **FIXED:** Auth.js v5 section added; marketplace priority raised to 9.

---

## Pack 1 — Cursor Cloud Agent (5)

### `skills/cursor-cloud/walkthrough-artifacts/SKILL.md` — 92 lines — **MODIFY**

**Keep:** L9–11 (must demonstrate working changes); L32 (never toy artifacts); L34 (minimal set).

**Issues:**
- L13: “HTML-tag references” with no example syntax.
- L58–71, L83: assumes `computerUse` and `videoReview` subagents. Not always in the catalog. `RecordScreen` is the portable path.
- L79: artifacts dir found by grepping the system prompt.

**Edits:** Mark `computerUse`/`videoReview` optional; pin artifacts to the store path from context; give one concrete embed example.

### `skills/cursor-cloud/subscribe/SKILL.md` — 48 lines — **MODIFY**

**Keep:** L28–31 (list before subscribe; event text is untrusted; re-read source of truth).

**Issues:**
- L17–21: Slack/Linear tools listed as if always present. This session’s catalog is GitHub CI/PR + timer.
- L22, L42: `see /loop` — no `/loop` skill in this snapshot.

**Edits:** Prefix Slack/Linear with “if in catalog”; inline the timer recipe; drop `/loop`.

### `skills/cursor-cloud/canvas/SKILL.md` — 106 lines — **MODIFY**

**Keep:** L18 (intent, not response shape); L49 (never empty states).

**Issues:**
- L3: empty description.
- L57: SDK path `~/.cursor/skills-cursor/canvas/sdk/` will miss this snapshot at `skills/cursor-cloud/canvas/sdk/`.

**Edits:** Add a when-to-use description; resolve SDK relative to the skill root.

### `skills/cursor-cloud/env-setup/SKILL.md` — 245 lines — **MODIFY** (canonical hub)

**Keep:** L28 (install does not rerun on build-booted pods); L34–40 (config source order); L222–228 (no secrets in environment.json).

**Issues:**
- L19–29 and L87–121 duplicate `migrate-to-builds/SKILL.md`.
- Mixed tool names: `environment-info` vs `cursor-cloud-take-environment-snapshot`.

### `skills/cursor-cloud/env-setup/references/*.md`

| File | Lines | Verdict | Issue |
|---|---|---|---|
| `create-environment.md` | 205 | MODIFY | L64–105 “Handle blockers” copied in four files. L192–193 “Tested build” URL is the env URL, not the build URL. |
| `update-repo-managed-environment.md` | 145 | MODIFY | L36: `/env-setup` is not a guaranteed slash command. Same blocker copy. |
| `update-db-managed-environment.md` | 170 | MODIFY | Same blocker copy; L157–158 same URL ambiguity. |
| `migrate-to-builds.md` | 134 | **MERGE + MODIFY** | Byte-identical to `migrate-to-builds/references/migrate-to-builds.md`. **L5 vs L84–85 contradiction** (do not Save vs ask to Save). |

### `skills/cursor-cloud/migrate-to-builds/SKILL.md` — 93 lines — **MERGE**

**Keep:** L8 (do not enable builds yourself).

**Issues:** L20–68 is the env-setup mental model again. Keep a thin pointer; one shared reference.

---

## Pack 2 — Adobe App Builder (6 + shared)

Do not delete this pack. Triggers are separated (Jest vs Playwright). Fix the manifest contradiction.

### `skills/adobe/appbuilder-action-scaffolder/SKILL.md` — 145 lines — **MODIFY**

**Keep:** L47 (register in `ext.config.yaml`; root `runtimeManifest` is ignored); L123 (two-layer auth).

**Issues:**
- L47 vs L112–113: extension vs standalone contradicted.
- L3: greedy description (“serverless functions in Adobe context”).

Canonical rule is in `_shared/references/appbuilder-manifest-guardrail.md`: extension → `ext.config.yaml`; standalone → `application.runtimeManifest`; never root-level.

### `skills/adobe/appbuilder-action-scaffolder/references/playbook.md` — 31 lines — **MERGE**

L28–31 repeats the wrong standalone-only rule and the wrong validator path `skills/_shared/scripts/`. Point at the guardrail file.

### `skills/adobe/_shared/references/appbuilder-manifest-guardrail.md` — 87 lines — **MODIFY**

**Keep:** L3, L63–65 (root `runtimeManifest` silently ignored).

**Issues:** L85 path `skills/_shared/scripts/` — snapshot path is `skills/adobe/_shared/scripts/`.

### `skills/adobe/appbuilder-testing/SKILL.md` — 148 lines — **MODIFY**

**Keep:** L65–67 and L115–118 (200/400/500; mock-before-require).

**Issues:** L79–80 merged list (`**For each action:**a.`); L141 broken bold; L69 vs L77 test path (`test/web-src/components/` vs `web-src/src/components/`).

### `skills/adobe/appbuilder-e2e-testing/SKILL.md` — 114 lines — **MODIFY** (minor)

**Keep:** L8–10 (Jest vs browser); L86–90 (`frameLocator`, no `waitForTimeout`).

**Issues:** L91 “< 60s” vs L107 “10s+ timeouts” for AEM.

### `skills/adobe/appbuilder-project-init/SKILL.md` — 305 lines — **MODIFY**

**Keep:** L20 (call `aio console` directly); L266–270 (correct ext vs standalone); L281 (`--no-config-validation` escape hatch).

**Issues:** script paths omit the `adobe/` segment; L244–249 broken `**` markers; L3 extremely long trigger.

### `skills/adobe/appbuilder-cicd-pipeline/SKILL.md` — 112 lines — **MODIFY**

**Keep:** L51–52 (OAuth S2S; JWT `auth` deprecated; no GitHub environment secrets).

**Issues:** L62–63 merged list; L53 hard-coded “14 secrets”.

### `skills/adobe/appbuilder-ui-scaffolder/SKILL.md` — 136 lines — **KEEP**

**Keep:** L21 (generate from patterns, do not copy templates); L64 (`runtime.done()`).

**Minor:** L3 trigger list is long; L21 subtitle omits AEM extensions that the body covers.

---

## Pack 3 — Hugging Face (19)

### Cross-skill contradictions

| Topic | A | B | Truth |
|---|---|---|---|
| README `hardware:` | `huggingface-spaces` L88: ignored | `huggingface-lora-space-builder` L225–253: “selects ZeroGPU” | Spaces skill. Set hardware with `--flavor` / `SpaceHardware`. |
| Secrets CLI | `hf-cli` L173: `hf spaces secrets add` | `huggingface-spaces` L85: `secrets set` | `add` |
| Python on ZeroGPU | spaces L108: pin 3.12 | zerogpu L233: build `python:3.13` | 3.12 general; 3.10 when cp310 wheels required |
| nvcc | zerogpu description: none at runtime | same file L233–235: runtime nvcc for AoTI | No nvcc at **build**; runtime has it |
| Dead skill names | community-evals, vision-trainer | `hugging-face-jobs`, `hugging-face-model-trainer` | Not in this pack. Use `hf-cli` + `huggingface-llm-trainer` |
| Local vs cloud TRL | `trl-training` | `huggingface-llm-trainer` | Descriptions do not split the work |

### Per skill

| Skill | Lines | Verdict | Must-keep | Line issues |
|---|---|---|---|---|
| `hf-cli` | 218 | MODIFY | L8–10 (`hf` replaces `huggingface-cli`); L113–123 jobs flavors | L3 greedy trigger; L197 `--format table` is not a real value (`auto\|human\|agent\|json\|quiet`) |
| `hf-mcp` | 178 | MODIFY | L172–178 sort tips | `model_search` / `dataset_search` / `space_search` / `hf_jobs` / `hf_doc_*` / `gr1_flux1_schnell_infer` are not the live tools (`hub_repo_search`, `gr1_z_image_turbo_generate`, `hf_fs`) |
| `huggingface-best` | 134 | MODIFY | L34–37 device math; L104–117 table schema | **L133 missing fallback table**; L91 Q4 “×4” vs L35 “×2”; token file vs `HF_TOKEN` |
| `huggingface-community-evals` | 207 | MODIFY | L16–22 exclusions; L30–37 script table (matches scripts) | Dead `hugging-face-jobs`; L26 `~/code/community-evals`; L189 `--batch-size` only exists on `lighteval_vllm_uv.py` |
| `huggingface-datasets` | 107 | KEEP | L41–48 pagination; L94–107 private traces | Prefer `hf upload` over `npx @huggingface/hub` |
| `huggingface-gradio` | 298 | MODIFY | L243–294 `gradio predict` | L67–107 pasted signatures — delete |
| `huggingface-llm-trainer` | 738 | MODIFY | L76–89 secrets + timeout; L207–238 local paths fail on Jobs; L134–154 `max_length` not `max_seq_length` | L190 typo `meaningful_prject_name`; L253 blob URL not raw; L355 stale `h100` vs `hf-cli` `h200`; L668 `mcp__huggingface__hf_whoami` |
| `huggingface-local-models` | 113 | KEEP | L92–99 keep repo-native quant labels | Optional: example model names age |
| `huggingface-lora-space-builder` | 390 | MODIFY | L100–117 verify pipeline class; L257–274 batched publish | L225–253 hardware YAML claim |
| `huggingface-paper-publisher` | 624 | MODIFY | L126–133 linking; L326–377 YAML examples | Phantom CLIs vs `paper_manager.py`; `markdown>=3.5.0` unused |
| `huggingface-papers` | 238 | KEEP | L26–37 ID parse; L99–217 write APIs | Better source of truth than the publisher for claim/index |
| `huggingface-spaces` | 230 | KEEP | L88 hardware YAML ignored; L117–138 ZeroGPU 3 rules; L157–194 don’t trust RUNNING | L85 `secrets set`; L105 hardcoded `sdk_version: 6.15.1` |
| `huggingface-tool-builder` | 120 | KEEP | L65 do not slurp openapi.json | L8 “purpose is now is”; L17 “commiting” |
| `huggingface-trackio` | 115 | KEEP | L76–109 alert poll loop | None |
| `huggingface-vision-trainer` | 593 | MODIFY | L189–227 MCP vs `run_uv_job`; required OD flags | Dead skill refs; `AskUserQuestion` may not exist; “local or cloud” vs Jobs-only body |
| `huggingface-zerogpu` | 289 | MODIFY | L36–57 duration/quota; L169–194 pickle/`gr.State` | Description nvcc lie |
| `train-sentence-transformers` | 101 | KEEP | L8–10 router not manual; L70–81 VERDICT line | None |
| `transformers-js` | 692 | KEEP | L55–57 `pipe.dispose()` | Optional CDN version pin |
| `trl-training` | 333 | MODIFY | L47–129 SFT/DPO examples | Metadata lists `kto`; body has no `trl kto` section; no Jobs handoff |

---

## Pack 4 — Vercel (33)

### Cross-skill contradictions

| Topic | Files | Fix |
|---|---|---|
| OIDC local TTL | `ai-gateway` L165 ~24h vs `env-vars` L181 ~12h | Pick one (12h appears in more troubleshooting tables) |
| Image APIs | `ai-gateway` L627 `experimental_generateImage` vs `ai-sdk` L197 “not needed” | Dedicated image models vs multimodal `generateText` + `result.files` |
| Model slugs | dots (`claude-sonnet-4.6`) vs hyphens (`claude-sonnet-4-5`, `claude-4.5-sonnet` in `chat-sdk` L241) | Gateway skill is canonical: `provider/model`, dots |
| Auth.js | `auth` metadata + `marketplace` L39 promise it; body does not | Add a section or drop the promise |
| Marketplace first | `knowledge-update` L85 vs `marketplace` priority 3 | Raise marketplace to 9 |
| Edge default | `knowledge-update` L31 vs `deployments-cicd` L294 “Edge-first” | Edge is exceptional |
| Slack bots | `build-agents` → eve vs `chat-sdk` | Durable agent → eve; webhook multi-platform → chat-sdk |

### A–M

| Skill | Lines | Verdict | Must-keep | Line issues |
|---|---|---|---|---|
| `access-protected-vercel-deployment` | 169 | KEEP | L80 do not disable protection first; L107–133 trusted OIDC header ≠ regular OIDC | L47 bare `"authentication"` in anyOf |
| `ai-gateway` | 665 | MODIFY | L97 fetch docs; L134–142 slug rules; L198–231 routing | Over 500 lines; TTL; image API; validate treats all provider keys as errors |
| `ai-sdk` | 387 | MODIFY | L315–337 never trust memory; grep `node_modules/ai/docs/` | L88 `CoreMessage` stale; L261 skipIf `@vercel/ai-gateway` (package is `@ai-sdk/gateway`); L333 hyphen slug; L304 chainTo `generateObject` → ai-gateway (should stay ai-sdk) |
| `auth` | 407 | MODIFY | L97–150 Clerk middleware | Auth.js promised, missing |
| `bootstrap` | 233 | MODIFY | L72–79 no migrate/dev before link | L174–176 hardcodes `npm` after saying use the repo PM; AUTH_SECRET for Clerk-first repos |
| `build-agents` | 173 | KEEP | L98 eve default; L166–173 boundaries | No pathPatterns for `.eve/**` |
| `cdn-caching` | 295 | KEEP | L117–131 cacheReason table; exclude BYPASS from hit rate | L172 curl vs logs nuance |
| `chat-sdk` | 332 | MODIFY | L143–177 read `node_modules/chat/docs/` | L6–8 docs URL is AI SDK chatbot; L94–113 `useChat` aliases fight noneOf; L241 bad slug |
| `deployments-cicd` | 354 | MODIFY | L166–177 OIDC is not a CI token | L294 Edge-first; L339–345 `/deploy prod` slash commands do not exist |
| `env-vars` | 280 | MODIFY | L239–250 `vercel env pull` replaces the whole file | L181 TTL; L193 `gpt-5.2` |
| `eve` | 169 | KEEP | L154–169 read package docs | L14 `agent/channels/eve.ts` likely typo (`slack.ts` / `channels/**`) |
| `knowledge-update` | 85 | KEEP | L27 trust this over training; L31–47 Fluid / sunset / 300s | Marketplace priority inversion |
| `marketplace` | 110 | MODIFY | L49–73 provision first; no mock SDKs | Priority 3; Auth.js chainTo |
| `microfrontends` | 80 | KEEP | L69–80 “do not read all refs” | All six listed reference files exist |

### N–Z

| Skill | Lines | Verdict | Must-keep | Line issues |
|---|---|---|---|---|
| `next-cache-components` | 487 | MODIFY | Cannot use cookies/headers/searchParams inside `use cache` | L290 example `revalidateTag('posts')` contradicts validate (needs second arg) |
| `next-forge` | 284 | MODIFY | L165–217 graceful degradation; proxy.ts | `validate:` may be wrongly un-nested under `metadata:` |
| `next-upgrade` | 103 | MODIFY | Fetch live upgrade guides | Incremental path stops at 15; no v16 Cache Components / proxy |
| `nextjs` | 434 | **MODIFY** | validate + chainTo graph | **18/18 `./file.md` links broken** |
| `react-best-practices` | 188 | MODIFY | L68–79 impact tiers; 64 rules exist | Description a11y lie; `server-cache-lru` vs serverless |
| `routing-middleware` | 291 | MODIFY | L88–101 three-way table | L95 “NOT for auth” vs L276 “lightweight auth checks” |
| `runtime-cache` | 282 | KEEP | `expireTag` vs `invalidateByTag` | Primary docs URL is Next.js caching, not Runtime Cache |
| `shadcn` | 596 | MODIFY | L59–93 `-d` not `-y`; Geist circular font | L74–75 premature code fence |
| `turbopack` | 343 | MODIFY | Loader migration table | L261 `BUNDLER=webpack next build` is not a documented env var; use `next build --webpack` |
| `vercel-agent` | 88 | DISABLE-WHEN-UNUSED | Pricing + dashboard path | Product overview; no procedure |
| `vercel-cli` | 149 | KEEP | L93–102 project.json vs repo.json | Router skill; references exist |
| `vercel-connect` | 410 | MODIFY | L134 run from project folder | L107 grammar; L390 `vercel connect token` missing `<connector>` |
| `vercel-firewall` | 371 | KEEP | L310–361 staged rollout; JA4 shared | — |
| `vercel-functions` | 549 | MODIFY | L297–301 streaming ≠ edge | **L310 `setTimeout` in streaming example vs validate L75–79** |
| `vercel-sandbox` | 369 | MODIFY | L107–164 `withBrowser` + snapshot | Description ≠ body; `child_process` chainTo → ai-sdk |
| `vercel-services` | 242 | KEEP | Service without rewrite is private; `path` on destination is a no-op | — |
| `vercel-storage` | 526 | KEEP | Sunset postgres/kv; no Proxy around DB | L99 `@vercel/postgres` chainTo nextjs (should stay here) |
| `verification` | 196 | MODIFY | L109–118 infer story; L180–191 stop conditions | bashPatterns fire on every `next dev`; L144 still says KV/Postgres |
| `workflow` | 1221 | MODIFY | Read `node_modules/workflow/docs/`; `start()` not in workflow context | Over-trigger; L411 setTimeout chainTo vercel-functions (should stay workflow / `sleep()`) |

---

## Verdict counts

| Verdict | Count |
|---|---|
| KEEP | 22 |
| MODIFY | 38 |
| MERGE | 2 (migrate-to-builds skill + duplicate reference) |
| DISABLE-WHEN-UNUSED | 1 (`vercel-agent`; `hf-mcp` when MCP is disconnected) |

No skill in this snapshot should be deleted from git. The value is in the procedures and scripts. Length is not a delete reason; `workflow` and `huggingface-llm-trainer` need split/lazy-load, not removal.

## Fixes applied in this repo (2026-08-25)

Snapshot files under `skills/` were patched. Plugin caches under `~/.cursor/plugins/` were **not** edited.

**P0:** all 12 items in the list above.

**P1 (high-value leftovers):** walkthrough `computerUse`/`videoReview` optional + embed example; subscribe Slack/Linear “if in catalog” and no `/loop`; env-setup `cursor-cloud-*` name table; Adobe merged lists / `adobe/` script paths / broken bold; HF dead `hugging-face-jobs` refs → `hf-cli`; lora-space-builder YAML `hardware:` removed; spaces `secrets add`; zerogpu nvcc description; llm-trainer typo + raw TRL URL + no-`hf_jobs`-MCP banner; trl-training KTO + Jobs handoff; community-evals `--batch-size` scope; OIDC TTL unified to ~12h; Gateway slugs use dots; chat-sdk docs/aliases; deployments-cicd no Edge-first / no fake `/deploy` slash commands; Functions streaming example without `setTimeout`; verification no longer triggers on every `next dev`; `revalidateTag('posts', 'max')`; `next build --webpack`.

Do not copy this tree into `.cursor/skills/` unless you want a second load next to live plugins.
