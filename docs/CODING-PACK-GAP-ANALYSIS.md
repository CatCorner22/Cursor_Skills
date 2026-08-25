# Coding pack — gap analysis (2026-08-25)

Review of the **Cursor_Skills** library before adding the **`coding`** pack (7 skills).

## What the library already covered

| Area | Existing skills | Gap |
|---|---|---|
| Execution posture | `proactive-agency` (session-start) | Says *do the work* and *verify* — but not *how* to test while coding |
| React performance | `react-best-practices` (64 rules) | Performance only; explicitly **not** accessibility or general craft |
| Next.js / shadcn | `nextjs`, `shadcn` | Framework mechanics, not deliverable-first planning |
| E2E verification | `verification`, `playwright-cli` | After-the-fact full-story checks — not continuous TDD loop |
| Unit/E2E (Adobe) | `appbuilder-testing`, `appbuilder-e2e-testing` | Adobe stack only |
| PR / CI | `cursor-team-kit` (`fix-ci`, `loop-on-ci`, `review-and-ship`) | GitHub workflow, not authoring discipline |
| Prompt text | `prompt-optimizer` | LLM prompts, not application code |
| Skill routing audit | `skill-library-audit` | Library metadata, not product code |

## What was missing (filled by `skills/coding/`)

| Missing capability | New skill |
|---|---|
| Router for general engineering craft | `coding-ecosystem-primer` |
| Begin with the end in mind; reverse-engineer from deliverable | `deliverable-first` |
| Clear, minimal lines; SOLID/YAGNI without over-abstraction | `clean-minimal-code` |
| Avoid houses of cards; boundaries and dependency direction | `stable-architecture` |
| **Real-time self-testing** (TDD, watch mode, prove every slice) | `real-time-testing` |
| Modern UI stacks (tokens, composition, Tailwind/shadcn/Radix) | `ui-engineering` |
| UX flows, heuristics, a11y, four UI states | `ux-engineering` |

## Deconfliction

| Existing skill | Coding pack boundary |
|---|---|
| `react-best-practices` | Perf waterfalls/bundle/re-renders only — coding pack does not claim those triggers |
| `shadcn` / `nextjs` | Install, RSC, App Router — `ui-engineering` handles composition/tokens then hands off |
| `verification` | Full browser narrative after slice tests green |
| `playwright-cli` | Tooling for browser automation, not UX heuristics |
| `build-agents` / agent frameworks | Agent architecture — not general app coding |

## Inventory after add

| Pack | Skills |
|---|---|
| coding (new) | 7 |
| Previous total | 106 |
| **New total** | **113** |

## Activation

Same as other packs: `./scripts/load-all.sh` → `.cursor/skills/` symlinks + local plugin. All skills **auto-trigger** on description match except none use `sessionStart` (craft skills are intentional, not injected every session — `proactive-agency` already covers execution posture).

`real-time-testing` has elevated `priority: 9` so it wins over generic review skills when the user asks to test while coding.
