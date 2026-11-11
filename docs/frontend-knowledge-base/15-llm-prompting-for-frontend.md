# 15. LLM Prompting for Optimal Frontend Outcomes: Evidence, Patterns, Loops, and Limits

Researched 2026-11-11. Complements [../frontend-design/03-prompt-template-kit.md](../frontend-design/03-prompt-template-kit.md) (templates and brief) and [../frontend-design/04-tools-plugins-and-models.md](../frontend-design/04-tools-plugins-and-models.md) (tools/models). This file adds the **evidence**, **agentic loops**, **failure modes**, and a **proven vs folklore** ledger.

Grades: A- peer-reviewed/arXiv read in abstract or excerpt, B peer-reviewed or primary dataset, C vendor documentation (authoritative about *their* models, not independent), D secondary. **(judgment)** = my inference. **Untested** = I did not run these prompts against a model; the worked example is illustrative.

Model names in vendor docs change quickly; I cite the guidance, not rankings.

## 1. Proven vs plausible vs folklore (read this first)

| Claim | Status | Evidence |
|---|---|---|
| Prompt wording/format can change results a lot; sensitivity doesn't vanish with model size, more shots, or instruction tuning | **Supported (older open models)** | Sclar et al.: up to **76 accuracy points** difference from meaning-preserving formatting changes on LLaMA-2-13B ([arXiv 2310.11324](https://arxiv.org/abs/2310.11324)). Prompt Report summarizes more sensitivity results ([2406.06608](https://arxiv.org/html/2406.06608v4)). Caveat: classification-style tasks, not UI generation. |
| Few-shot examples help consistency | **Supported + vendor-recommended** | Anthropic: examples are "one of the most reliable ways" to steer format/tone/structure; 3-5 examples; wrap in tags ([Anthropic best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)); OpenAI: show diverse inputs/outputs ([OpenAI](https://platform.openai.com/docs/guides/prompt-engineering)). In the Prompt Report's small MMLU test, few-shot CoT scored best (gpt-3.5-turbo only). |
| Chain-of-thought helps reasoning tasks | **Supported (math/logic)** | [Wei et al. 2201.11903](https://arxiv.org/abs/2201.11903); [Kojima et al. 2205.11916](https://arxiv.org/abs/2205.11916). Not shown for visual design quality. In the Prompt Report's benchmark Zero-Shot-CoT *underperformed* plain zero-shot, "unexplained." |
| "You are a world-class designer" persona prompts raise quality | **Not supported for accuracy tasks; unknown for design** | Zheng et al. (EMNLP Findings 2024): 162 personas, 4 model families, 2,410 questions: **no improvement** vs no persona; effects "largely random" ([ACL](https://aclanthology.org/2024.findings-emnlp.888/)). Principled Personas (EMNLP 2025): expert personas usually neutral or positive, but irrelevant persona details dropped performance by almost 30 points ([ACL](https://aclanthology.org/2025.emnlp-main.1364.pdf)). For *style/voice* tasks personas may help (Prompt Report notes open-ended tasks); I found no UI-specific study. |
| Specific constraints beat vague requests | **Plausible, vendor-endorsed; UI-specific evidence thin** | Anthropic's dashboard example (be explicit; "go beyond the basics"), NN/g: vague prompts cause long funneling conversations ([NN/g](https://www.nngroup.com/articles/ai-prompt-structure/)). I found no controlled A/B of spec-vs-vague UI prompts. |
| Models converge on generic UI ("AI slop") unless steered | **Vendor-reported, widely observed, not independently measured** | Anthropic names "distributional convergence" and publishes steering text ([blog](https://claude.com/blog/improving-frontend-design-through-skills)); before/after images are Anthropic's own. |
| Self-critique loops improve output | **Mixed** | Self-Refine: preferred by humans/metrics across 7 tasks with GPT-3.5/4 ([2303.17651](https://arxiv.org/abs/2303.17651)). Huang et al.: *intrinsic* self-correction without external feedback struggles on reasoning and sometimes degrades ([2310.01798](https://arxiv.org/abs/2310.01798)). **(judgment) Loops work best when they add new information (a screenshot, test result, linter output), not just "review your work."** |
| Visual self-revision helps | **Model-dependent** | Design2Code: self-revision (compare reference vs own render) helped GPT-4V but **not** GPT-4o or Gemini Pro Vision; text-augmented prompting (give extracted text) helped weaker models ([2403.03163](https://arxiv.org/html/2403.03163v3)). |
| LLM-as-judge approximates human preference | **Supported with known biases** | Zheng et al.: strong judges reached >80% agreement with human preferences, same as human-human; documented **position, verbosity, self-enhancement** biases and limited reasoning ([2306.05685](https://arxiv.org/abs/2306.05685)). No equivalent validation for judging *visual design taste* found. |
| Long context is used evenly | **False** | Lost in the Middle: best at beginning/end, worse in the middle ([2307.03172](https://arxiv.org/abs/2307.03172)). Anthropic: "context rot," attention budget; keep context "informative, yet tight" ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). |
| AI coding tools make experienced devs faster | **Contested** | METR RCT (16 devs, 246 tasks, early-2025 tools): AI **increased** completion time by **19%**; devs predicted -24% and afterward believed -20% ([2507.09089](https://arxiv.org/abs/2507.09089)). Small, specific population (experienced maintainers of familiar large repos); not about greenfield UI. |
| AI code is secure | **Not supported** | Copilot (2021): about **40%** of 1,689 generated programs vulnerable ([2108.09293](https://arxiv.org/abs/2108.09293)); users with an assistant wrote **less secure** code and were **more confident** ([2211.03622](https://arxiv.org/abs/2211.03622)). Older tools. |
| Hallucinated packages | **Supported** | 576,000 samples, 16 LLMs: average at least 5.2% hallucinated package names for commercial models and 21.7% for open-source ([2406.10279](https://arxiv.org/abs/2406.10279)). |
| Generated UI is accessible by default | **Not supported** | See [14 section 5](14-inclusive-design-ai-ux-and-wcag-check.md): 84% of ChatGPT-built sites had issues (automated tools). |

## 2. What the official guidance says (and where it conflicts)

| Topic | Anthropic | OpenAI | Notes |
|---|---|---|---|
| Define success + evals first | "A clear definition of the success criteria... empirical tests... a first draft" before prompt engineering ([overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)) | Pin model snapshots; build evals; version prompts in code ([OpenAI](https://platform.openai.com/docs/guides/prompt-engineering)) | Agreement. **(judgment)** This is the single most transferable advice. |
| Explicit vs high-level | "Right altitude": avoid both brittle hardcoded detail and vague guidance ([context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)); give motivation, not bare rules | GPT-style models "benefit from precise instructions"; reasoning models do better with high-level goals, "like a senior co-worker" vs "junior co-worker" | Partly conflicting; depends on model type. Re-test when switching models. |
| Examples | 3-5, diverse, relevant, tagged | Diverse range of inputs with desired outputs | Agreement. Anthropic warns against laundry lists of edge cases in prompts. |
| Structure | XML tags; long documents at top, query after | Markdown/XML sections (Identity, Instructions, Examples) | Anthropic's context post: exact formatting "likely becoming less important as models become more capable." |
| Emphasis | Newer Claude models are more responsive to system prompts; **soften "CRITICAL/MUST"** or they overtrigger | (no equivalent found) | Prompts tuned on one model can misfire on the next. |
| Verification | Give the agent tools to verify UI (browser automation, computer use); "self-check" instructions help, but on one newest model they can cause over-verification | "Instruct the model to test changes"; note patch tools may report success on failure | Vendor/model-specific; test your own stack. |
| Frontend steering | `<frontend_aesthetics>` block: avoid Inter/Roboto/Arial, purple-gradient-on-white clichés; commit to cohesive theme, CSS variables, high-impact motion, atmospheric backgrounds; remind it to avoid *new* convergence (Space Grotesk) | Recommend Tailwind, shadcn/ui, Radix Themes; Lucide/Material Symbols/Heroicons; Motion. For large codebases give: principles, UI/UX (type, color, spacing, states, a11y), structure, components, pages, agent instructions. One-shot prompt: build a hidden 5-7 category rubric, iterate against it, avoid heavy dependencies | Different philosophies: Anthropic fights sameness; OpenAI standardizes on a stack. Both reasonable; choose per brand risk. |
| Google | **Gemini prompting page fetch timed out; not read.** | | Check [ai.google.dev prompting strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies) directly. |

## 3. The prompt stack: what to put in context (and in what form)

| Layer | Contents | Evidence/reason |
|---|---|---|
| 1. Persistent rules | Stack, token file path, banned patterns, a11y bar, commands to run | Rules/AGENTS.md/CLAUDE.md (section 6) |
| 2. Spec | Users, task, states, content, constraints, acceptance checks | NN/g prompt components: request, framing, format, references |
| 3. Design context | Tokens (as variables, not prose), component list, 1-2 reference screens | Design tokens give machine-readable decisions ([10](10-design-systems-and-tokens.md)); Figma MCP exposes variables and Code Connect |
| 4. Reference images | Screenshot of the target or of current UI, plus **text extracted** from it | Design2Code text-augmented prompting; screenshots helped a11y fixes (2501.03572) |
| 5. Verification tools | Playwright MCP/Playwright scripts, axe, linter, tests | Anthropic: provide verification tools for UI |
| 6. Task | One screen/component at a time | Anthropic multi-window guidance: incremental progress; keep context lean |

Keep it **small**: Anthropic says each token depletes an "attention budget." Put stable guidance in rules files and load task-specific guidance on demand (skills).

## 4. Copy-paste prompt patterns (untested; adapt to your repo)

### 4.1 Spec prompt (replaces "make it look modern")

```text
Build the {screen} for {product}.

Users and task: {who} wants to {primary task}. Success = {measurable outcome}.

Constraints
- Stack: {framework}, Tailwind using ONLY tokens from {tokens file}; components from {path or Radix/shadcn}. Do not add dependencies; if one is required, stop and ask.
- Responsive: usable at 320px and 1280px; no horizontal scroll; layout with CSS grid/flex and container queries where a component is reused.
- Accessibility: WCAG 2.2 AA. Native elements first; visible focus; targets >= 24x24 CSS px; error text associated with fields; prefers-reduced-motion honored; no color-only meaning.
- States: default, hover, focus-visible, active, disabled, loading, empty, error, success for every interactive element.
- Content: use this real copy: {copy}. No lorem ipsum, no invented statistics or logos.

Visual direction: {2-3 concrete adjectives + 1 reference}. Avoid: {project banned list}.

Done when: (1) typecheck, lint, and tests pass; (2) axe reports no violations; (3) you have screenshots at 375, 768, 1280 px and have fixed anything misaligned; (4) you list any assumption you made.
```

### 4.2 Tokens as context

```text
Use these design tokens as the only source of color, spacing, radius, and type size. If a value you need is missing, propose a new token name and value and wait.
<tokens>
{paste tokens.json or CSS variables}
</tokens>
Every text/background pair must meet 4.5:1 (large text and UI parts 3:1) in light and dark themes; show the pairs you checked.
```

### 4.3 Reference screenshot + extracted text (Design2Code-style)

```text
<reference_screenshot>{attached image}</reference_screenshot>
<text_content>{all visible text, in reading order}</text_content>
Recreate this layout as semantic HTML/CSS using our tokens. Copy text only from <text_content>. Focus on layout fidelity (grid, spacing, hierarchy). Then render it, compare with the reference, and list the three largest differences before fixing them.
```

### 4.4 Screenshot -> critique -> fix loop (agentic)

```text
Loop until the checklist passes or 4 iterations are used:
1. Start the dev server. Take screenshots at 375, 768, and 1280 px (light and dark).
2. Compare with {reference or the acceptance criteria}. Write a numbered list of defects with the element and the measurement (e.g., "CTA 36px tall, needs >= 44px on touch").
3. Fix only the listed defects. Do not refactor unrelated code.
4. Re-run typecheck, lint, tests, and the axe script. Include the outputs.
Stop and report if a fix requires a new dependency, a token change, or a design decision.
```

Rationale: Self-correction helps when the model gets **new external signal** (Huang et al. found it doesn't without it). Cap iterations; Playwright screenshot comparisons are brittle across OS/browser ([Playwright](https://playwright.dev/docs/test-snapshots)).

### 4.5 Rubric-based critique (a second, separate pass)

```text
Act as a reviewer, not the author. Score the attached screenshots 1-5 on each criterion with ONE sentence of evidence referencing a specific element, and list the top 3 fixes by impact. Criteria: hierarchy (one clear primary action), grouping (proximity), type scale, contrast, spacing consistency, states shown, copy clarity, fit with the brief. Do not praise. If you cannot judge a criterion from the image, say "cannot judge".
```

Limits: LLM judges show position, verbosity, and self-enhancement bias; **use a different model or a fresh context than the author when possible**, randomize order when comparing options, and calibrate against a few human-rated examples **(judgment from Zheng et al.)**. Never let the judge replace usability testing ([13](13-ux-research-methods-and-measurement.md)).

### 4.6 Accessibility pass

```text
Audit the component for WCAG 2.2 AA. For each item answer pass/fail with the line of code: keyboard path and focus order; focus visible and not obscured (2.4.11); name/role/value for custom controls; label in name (2.5.3); error identification and suggestion (3.3.1, 3.3.3); status messages (4.1.3); target size (2.5.8); drag alternatives (2.5.7); reflow at 320px (1.4.10); reduced motion. Prefer replacing custom widgets with native elements or Radix/React Aria. Then fix and re-run axe.
```

### 4.7 Dependency and API honesty

```text
Before writing code, list every package and API you plan to use with its version from package.json (or "not installed"). Do not import a package that is not listed in package.json. If you are unsure an API exists in the installed version, search node_modules or the docs and cite the file path. Flag anything you could not verify.
```

(Addresses package hallucination, [2406.10279](https://arxiv.org/abs/2406.10279). Still verify with `npm ls` and a lockfile review.)

### 4.8 Security pass

```text
Review for XSS and unsafe patterns: any dangerouslySetInnerHTML, innerHTML, eval, unvalidated URLs (javascript:), secrets in client code, missing output encoding, overly broad CORS. For each finding show the line, the risk, and the fix. Do not suppress findings.
```

## 5. Worked before/after (illustrative, **not run against a model**)

**Before (typical vague prompt):**

```text
Make a modern pricing page for my SaaS.
```

Likely problems **(judgment, consistent with the cited sources, not measured here)**: model samples from generic defaults (Anthropic's "distributional convergence"); invents plan names, prices, and testimonials; hand-rolls a toggle without keyboard/ARIA semantics; mixes arbitrary colors; no states; no check it works on mobile; adds an unrequested dependency.

**After (specified, verifiable):**

```text
Build /pricing for Fieldnote (a note-taking app for field researchers).
Users and task: a researcher comparing Free vs Pro wants to pick a plan in under 30 seconds. Success = one obvious primary action per plan; plan differences scannable.

Constraints: Next.js + Tailwind using only tokens in src/styles/tokens.css. Use Radix Switch (already installed) for the monthly/annual toggle; no new dependencies. 320-1280 px, container queries on the PlanCard so it works in a 2- and 3-column layout.
Content (use exactly): Free $0 - 3 notebooks, offline sync; Pro $8/mo or $80/yr - unlimited notebooks, shared libraries, export to CSV. No testimonials, no logos, no claims about customer counts.
Accessibility: WCAG 2.2 AA; toggle announces state; focus visible; price changes announced via a polite live region; 4.5:1 text contrast in both themes.
Visual direction: calm, editorial, high legibility; avoid purple-on-white gradients, glassmorphism, and generic icon-in-circle feature grids.
States: toggle on/off, button hover/focus/disabled/loading; empty/error not applicable (say so).
Done when: tests + typecheck + lint pass, axe clean, screenshots at 375/768/1280 in light and dark reviewed and defects fixed; list assumptions.
```

What changed and why: **scope** (users, success), **constraints** (stack, tokens, no new deps), **real content** (prevents invented stats), **accessibility bar** stated (models don't ask for it: CodeA11y found developers "fail to prompt AI for accessibility"), **verification** (screenshots/axe), **banned list** (steers away from convergence). Expected effect size: **unmeasured**. To learn whether it helps *you*, run both prompts 5 times each with the same model, blind-rate outputs with a rubric (4.5) plus axe results.

## 6. Rules, memory, skills, and design context

| Mechanism | Verified facts | Source |
|---|---|---|
| **Cursor rules** | Project rules in `.cursor/rules` as `.mdc` (plain `.md` there is ignored); four activation types (always, intelligent by description, by glob, manual); also User Rules, Team Rules, and `AGENTS.md` (nested supported). Best practice: keep rules under 500 lines, split, concrete examples, **reference files instead of copying**; don't copy whole style guides (use a linter); add rules when the agent repeats a mistake. Rule contents go at the start of model context. Docs warn AI guidance "should not be your only security control." | [Cursor docs](https://cursor.com/docs/context/rules) |
| **Claude Code memory** | `CLAUDE.md` (also reads `AGENTS.md`); loaded every session; treated as **context, not enforced configuration**; "more specific and concise" = more consistent; target **under 200 lines**; use path-scoped rules and skills for narrower guidance; use a PreToolUse **hook** when you must *block* an action. | [Claude Code memory docs](https://docs.anthropic.com/en/docs/claude-code/memory) |
| **Skills** | Markdown + resources loaded on demand to avoid permanent context cost; a frontend-design skill is Anthropic's example; can encode your design system. | [Anthropic blog](https://claude.com/blog/improving-frontend-design-through-skills) |
| **Figma MCP** | `get_design_context` returns React + Tailwind by default (can ask for other frameworks; can ask it to use components from a folder); `get_variable_defs` returns colors/spacing/type variables; Code Connect maps Figma components to your code (`get_code_connect_map`). Remote server recommended; desktop server needs a Dev/Full seat. | [Figma MCP docs](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/) |
| **Playwright MCP** | Works from **accessibility-tree snapshots** (refs like `e5`), not pixels by default; has `browser_take_screenshot`, resize, console and network tools; refs go stale after page changes. `browser_run_code_unsafe` is described as **RCE-equivalent**; enable only for trusted clients. Side benefit **(judgment)**: if the agent cannot find your control by role/name in the snapshot, a screen reader likely can't either. | [Playwright MCP](https://playwright.dev/docs/getting-started-mcp), [snapshots](https://playwright.dev/mcp/snapshots), [capabilities](https://playwright.dev/mcp/capabilities) |

**Starter rules file (judgment; adapt):**

```markdown
# Frontend rules
- Stack: Next.js, TypeScript strict, Tailwind. Tokens live in src/styles/tokens.css; never hard-code colors, spacing, or font sizes.
- Use native elements first; for dialogs/menus/comboboxes use Radix or React Aria. No new dependencies without asking.
- Every interactive component: keyboard operable, visible :focus-visible, name/role/value, targets >= 24px, honors prefers-reduced-motion.
- Run before finishing: `npm run typecheck && npm run lint && npm test && npm run a11y`. Paste results.
- Never invent copy, statistics, logos, or testimonials; use content from /content or leave a TODO.
- Security: never use dangerouslySetInnerHTML with untrusted data; no secrets in client code.
```

## 7. Model strengths and weaknesses for UI work (what I can and can't say)

- **Verified:** on Design2Code (484 real pages, 2024 models), models lagged most in **recalling visual elements** and **layout**, whereas text content and color were easier; human raters judged GPT-4V output replaceable for the original in 49% of cases and better than the original in 64% (judged on visual appearance and content by Prolific annotators, 100-sample subset, models now old).
- **Vendor-reported:** unguided models converge on generic aesthetics (Anthropic); recommended libraries (OpenAI).
- **Not verified:** any current head-to-head ranking of models for UI quality. Aggregator rankings (see 04) are grade D. **(judgment) Run your own 10-prompt bake-off with blind human ratings and axe scores.**

## 8. Failure modes and mitigations

| Failure | Mitigation |
|---|---|
| Generic aesthetics | Concrete visual direction + banned list; reference screens; tokens |
| Hallucinated APIs/packages | 4.7; lockfile/CI check; typecheck; read package docs |
| Inaccessible custom widgets | Radix/React Aria; 4.6; axe + manual keyboard/screen reader |
| Invented content/stats | Provide real copy; forbid inventing |
| Over-engineering/scope creep | Scope line; "do not refactor unrelated code"; small diffs |
| Security flaws and overconfidence | 4.8; code review; SAST; treat output as untrusted code |
| Context rot in long sessions | Fresh context per screen; notes file; compaction ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)) |
| Fragile visual tests in loops | Same environment; mask dynamic regions; cap iterations |
| Prompt drift across model versions | Pin versions; keep an eval set of 5-10 prompts; re-run after upgrades |
| Self-flattering reviews | Separate reviewer pass with rubric; human spot checks |

## 9. Build a small eval for your own prompts

1. Pick 5-10 representative tasks (screen/component briefs).
2. Define pass/fail checks you can automate: typecheck, lint, axe, Lighthouse budget, screenshot at 3 widths with no overflow, no banned fonts/colors, token-only CSS (grep).
3. Add a 1-5 human rubric for hierarchy, fit-to-brief, clarity (blind to which prompt produced it).
4. Run each prompt variant 3-5 times (outputs vary). Compare means and spread.
5. Re-run on every model or prompt change. This is what both Anthropic ("empirically test against criteria") and OpenAI ("build evals") recommend.

## 10. Honest summary

- **Reliably useful:** clear specs with real content, examples, tokens/constraints, verification tools, small scoped tasks, evals, human review.
- **Plausible but under-measured for UI:** steering text against generic design, rubric loops, persona framing, Figma/Playwright loops.
- **Weak or unsupported:** "magic" prompt phrases, roles as accuracy boosters, trusting self-review without external signal, assuming generated code is secure or accessible.
