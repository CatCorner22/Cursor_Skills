---
name: coding-ecosystem-primer
description: "Router for general software engineering in this library: deliverable-first planning, clean minimal code, stable architecture, real-time testing, and UI/UX engineering. Use when building or refactoring application code with no framework-specific pack already chosen, or when the user asks for coding standards, clean code, TDD, architecture, or how to implement a feature well. Scope boundary: framework-specific work routes out — Next.js/React UI details → `nextjs`/`shadcn`/`react-best-practices`; end-to-end product verification after a feature ships → `verification`; Playwright/browser automation → `playwright-cli`; PR/CI workflow → `cursor-team-kit`; LangChain/Python agents → those packs."
metadata:
  priority: 8
---

# Coding ecosystem primer

Pick the **smallest set of skills** that covers the task. This pack is **stack-agnostic** — it governs *how* to code, not which vendor framework to use.

## Decision table

| User intent | Load next |
|---|---|
| New feature, unclear scope, "how should I build this?" | **`deliverable-first`** |
| Code is verbose, muddy, or over-abstracted | **`clean-minimal-code`** |
| Fragile coupling, hard to change, "house of cards" | **`stable-architecture`** |
| Need tests while coding, TDD, watch mode, "verify as you go" | **`real-time-testing`** |
| Components, layout, design tokens, Tailwind/shadcn/Radix | **`ui-engineering`** → then `shadcn`/`nextjs` if Next.js |
| Flows, usability, a11y, empty/error/loading states | **`ux-engineering`** |
| React/Next **performance** only (waterfalls, bundle size) | **`react-best-practices`** (not this pack) |
| Full user-story check in browser after implementation | **`verification`** (after `real-time-testing` passes) |
| Stuck, thrashing, too much WIP | **`ooda-lean-loop`** |
| Session prep (env, tests, branch) | **`workspace-mise-en-place`** |

## Systems combinations (OODA × lean × mise)

**Developer mise:** `workspace-mise-en-place` → branch, env, test command ready.

**Coding loop:** `deliverable-first` (orient/decide) → `real-time-testing` (act + **andon** on red) → `clean-minimal-code` (kaizen) → `loop-on-ci`.

TPS mapping: small batches = vertical slices; andon = failing test/CI; kaizen = refactor pass.

## Default workflow (always)

```
1. deliverable-first  → define done (contract, UI states, acceptance checks)
2. stable-architecture → sketch boundaries before files multiply
3. implement in thin vertical slices
4. real-time-testing   → run the narrowest check after every slice
5. ui-engineering / ux-engineering as the surface demands
6. clean-minimal-code  → tighten on every pass (not a separate phase at the end)
```

**Begin with the end in mind:** Step 1 produces the artifact you would show a user or reviewer. Steps 3–4 reverse-engineer code from that artifact.

## Principles this pack encodes

- **Established craft:** SOLID, YAGNI, separation of concerns, fail fast, composition over inheritance, dependency direction toward stability.
- **Minimal surface:** Fewer lines that carry the same behavior; no speculative abstractions.
- **No houses of cards:** Each layer must stand if the layer above is removed; no hidden globals, no circular domain imports, no "works until we touch X."
- **Proof in motion:** Code is not done until the real-time test loop is green for the slice you changed.

## Boundaries (do not steal)

| Topic | Owner |
|---|---|
| Next.js App Router, RSC, Server Actions | `nextjs` |
| shadcn/ui install & registries | `shadcn` |
| React render performance rules | `react-best-practices` |
| E2E browser verification narrative | `verification`, `playwright-cli` |
| Adobe / HF / LangChain / Supabase stacks | respective packs |
| Agent prompt text optimization | `prompt-optimizer` |
