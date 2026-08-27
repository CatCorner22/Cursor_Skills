---
name: canvas
disable-model-invocation: true
description: "Author standalone .canvas.tsx analytical artifacts (charts, tables, audits, metrics) using the cursor/canvas SDK. Use when the deliverable IS structured visual output — not code fixes, PRs, or external dashboards. Skip for short answers and intermediate MCP queries."
metadata:
  surfaces:
    - ide
    - cloud
---
A canvas is a single `.canvas.tsx` file. Follow the workflow below in order.

After you write the canvas: on `web`, link `{Current agent's store}/artifacts/canvases/<name>.canvas.bundle.gz` using the **Current agent's store** path from your context — that is the default preview. On `desktop` (Cursor desktop / Glass), link the `.canvas.tsx`; the local canvas server opens it. On `cli` or `sand`, call `cursor-cloud-publish-shared-canvas` and give them `shareUrl`. Presence of `cursor-cloud-publish-shared-canvas` does **not** mean you should publish. Call it only for an explicit user ask, or when this run's `cursor-cloud-run-info` `source` is `cli` or `sand`. Do not publish just in case for `web` or `desktop`.

## Workflow

### 1. Decide whether to use a canvas

The trigger is **user intent**, not response shape. Ask: would the user benefit from viewing this output as its **own standalone artifact**, separate from the chat? If the output is a means to an end (a drafted message, a code fix, a dashboard in another tool), skip the canvas.

**Use a canvas when the agent produces new standalone analytical output:**
- Quantitative analyses and metrics breakdowns (e.g. "send 500 requests and tell me how many fail")
- Billing or account investigations that surface structured findings from database queries
- Security audits or architecture reviews with categorized findings
- Cross-system data analyses and overlap reports
- Structured data from MCP tools (Databricks, Datadog, etc.) where the data IS the deliverable
- Financial analyses, margin decompositions, usage trend reports
- Tables with more than a handful of rows that the user asked to see

**Do NOT use a canvas when:**
- The user asks for work in a **specific tool** — "create a Datadog dashboard" means give them a Datadog dashboard, not a canvas
- The user has a **specific deliverable** — "draft a support response", "fix this code", "make this PR"
- The user is **working within an existing artifact** — improving an HTML dashboard, editing an existing file
- The user is doing **targeted debugging** or active development, even if structured findings emerge along the way
- Short factual answers, one-off file edits, or quick clarifying questions
- MCP tools are queried as an **intermediate step** for a different deliverable (e.g. querying Stripe to draft a support reply)

### 2. Write the canvas

**Location.** Write `~/.cursor/projects/<workspace>/canvases/<name>.canvas.tsx`. Post-write TypeScript diagnostics only pick up canvases written directly inside that exact directory. After the write, a preview gzip is stored at `{Current agent's store}/artifacts/canvases/<name>.canvas.bundle.gz`. Fill **Current agent's store** from your context. On `web`, that file is the default preview — do not call `cursor-cloud-publish-shared-canvas` as part of writing. On `desktop` (Cursor desktop / Glass), link the `.canvas.tsx`; the local canvas server opens it — do not call `cursor-cloud-publish-shared-canvas` as part of writing. On `cli` or `sand`, call the publish tool and give them `shareUrl`.

For a new canvas, always use the write file tool to create the `.canvas.tsx` file at that exact path; do not stop after telling the user the path or showing code in chat. Treat that managed `canvases/` directory as pre-provisioned by Cursor itself: write the canvas file directly there and do **not** spend turns creating the directory with `mkdir` or checking whether it exists before writing. Listing its contents for other purposes (e.g. checking for existing canvases) is fine. If you can't determine the workspace directory from absolute paths already in your environment (terminals, transcripts, recently-viewed files), list `~/.cursor/projects/` rather than guessing. Use a descriptive kebab-case filename ending in `.canvas.tsx`; preserve acronym capitalization and lowercase the rest.

**File rules:**
- Exactly one `.canvas.tsx` file per canvas. Never create helper files, style files, or supporting modules.
- Import **only** from `cursor/canvas`. No relative imports, no npm packages, no Node built-ins.
- Default-export the top-level component.
- Embed all data inline. **No `fetch()`, no network calls.**

**Never render empty states.** A canvas exists to show real content. If a section, chart, table, or component has no data to display, **omit it** — do not render it with placeholder text ("Add header here", "TODO", "Example"), a "No data" message, an empty array, zeroed rows, or an empty chart frame. If the entire canvas would be empty because you don't have the underlying data, do not produce a canvas — tell the user what's missing and ask for it instead.

**Label every plot.** Charts and tables must be self-describing — a reader looking at the canvas alone should know exactly what they're seeing. For every plot include:
- A title naming the **specific metric** (not "Metrics" — "API error rate by service").
- **Axis labels with units** on both axes (e.g. "Date", "Latency (ms)").
- A **legend** when more than one series is shown, with the exact series names from the source data.
- The **source and time range** in a small caption (e.g. "Source: Datadog · last 7 days"). If a value is a transformation (mean, p95, normalized, smoothed), say so in the label.

**Component discovery:** prefer built-in `cursor/canvas` components over hand-rolled markup. The full public surface (components, hooks, prop types, tokens) is declared in this skill's `sdk/index.d.ts` and its sibling `.d.ts` files (resolve relative to this SKILL.md). Prefer `~/.cursor/skills-cursor/canvas/sdk/` when that install is present. Read those files when you need exact exports, prop shapes, or hook signatures rather than guessing. Referencing an export that does not exist is the most common runtime error.

Apply the Design guidance below as you write, and complete its Pre-delivery self-check before returning the canvas.

## Design guidance

Be creative. The SDK gives you expressive building blocks — use them in whatever combination best serves the content. But avoid slop: no gradients, no emojis, no box-shadows, no rainbow coloring. Cursor canvases are flat, minimal, and purposeful.

### Visual hierarchy

Not everything deserves equal treatment. Primary content gets more space, larger headings, and accent color. Supporting content stays compact. Squint test: blur your eyes — can you tell what matters?

**Color.** All colors from `useHostTheme()` tokens — read its JSDoc in the SDK declarations for the return shape and usage pattern. No hardcoded hex. Use accent color deliberately, not on everything.

### Slop patterns — forbidden

These specific patterns produce low-quality output. If 2+ are present, redesign.

- **Gradients** — no `linear-gradient`, `radial-gradient`, `background-clip: text`.
- **Emojis** — no emoji as icons, status indicators, bullets, or section markers.
- **Box shadows** — no `box-shadow`. Flat surfaces only.
- **Wall of identical cards** — every section wrapped in the same card style with no variation. Mix open sections with cards.
- **Rainbow coloring** — a different color on every element. Most elements are neutral; color is used sparingly with purpose.
- **Giant text** — font sizes above H1 (24px), or bold text stuffed in CardHeader.
- **Decorative borders** — colored borders on every element. Borders are structural (subtle stroke tokens), not decorative.

### Pre-delivery self-check

Before returning canvas code, verify:
1. Does the layout have visual hierarchy? One thing should stand out.
2. Is there variety in the composition? Not just a single column of uniform blocks.
3. Slop check: scan for the forbidden patterns above.

## Introducing the canvas

Whenever you mention a canvas to the user — one you created, updated, or want them to open — **always** include a markdown link: choose the link from this run's `cursor-cloud-run-info` `source`. On `web`, link the preview at `{Current agent's store}/artifacts/canvases/<name>.canvas.bundle.gz` (for example, `[billing-review]({Current agent's store}/artifacts/canvases/billing-review.canvas.bundle.gz)`) using the **Current agent's store** path from your context — do **not** link the `.canvas.tsx` path. On `desktop` (Cursor desktop / Glass), link the `.canvas.tsx` using its full path (for example, `[billing-review](~/.cursor/projects/<workspace>/canvases/billing-review.canvas.tsx)`). On `cli` or `sand`, call `cursor-cloud-publish-shared-canvas` and link the returned `shareUrl`. Call `cursor-cloud-publish-shared-canvas` only when the user asked to publish or share, or when `source` is `cli` or `sand`. When you publish, also give them `shareUrl`. Pass a stable `canvasKey` (the canvas filename is fine).

When you create a canvas, add a short note in your chat response telling the user they can open it, with that link:

- **First canvas** — if no other `.canvas.tsx` files exist in the workspace's `canvases/` directory, include one sentence explaining what a canvas is.
- **Unsolicited canvas** — if the user didn't ask for a canvas, include one sentence explaining why you chose it over plain text.

Both can apply at once; one or two sentences total is enough. Skip the intro for subsequent canvases unless you are mentioning that canvas again (still link it).

## Troubleshooting

If a canvas is missing, blank, or the user cannot open it:
If the `web` preview link 404s immediately, wait a few seconds and reopen it — do not publish just to paper over that. If it still fails, the usual cause is that the file was not written under `~/.cursor/projects/<workspace>/canvases/` exactly. Re-save it there and link the gzip on `web`, or the `.canvas.tsx` on `desktop` / Glass. If the canvas is too large to preview, shrink it — do not publish to work around the limit. If the user is on CLI or Grok Bot/Sand, call `cursor-cloud-publish-shared-canvas` and give them `shareUrl`.

Do not debug this by trying to create the managed directory manually; focus on correcting the file path instead. Every canvas edit returns a `Canvas TypeScript check` line in the tool result reporting the file's current type errors (or "no errors") — treat that as the authoritative diagnostics signal.
