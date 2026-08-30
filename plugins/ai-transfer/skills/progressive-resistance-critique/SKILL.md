---
name: progressive-resistance-critique
description: 'Escalating self-critique passes: warm-up consistency, moderate alignment, working robustness, max falsifiability. Use instead of single shallow ''review your answer''. Scope boundary: post-delivery debrief → `after-action-review`; proof DAG → `proof-trees-reasoning`.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Progressive resistance self-critique

**#3** · **Domain:** Strength coaching · **Category:** quality-control · **Difficulty:** 🟡 Medium

## Core principle

Ramp critique intensity — never one-rep-max review cold.

## AI problem addressed

Single-pass self-review misses distinct failure modes.

## Implementation

| Phase | Target | Prompt |
| Warm-up | Internal consistency | Contradictions? |
| Moderate | Question alignment | Unstated assumptions? |
| Working | Core robustness | Strongest objection? |
| Max | Falsifiability | If wrong, what would we observe? |

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-quality-control`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `progressive_critique`
- Also implements: `self_evaluation`, `confidence_calibrator`, `blind_spot_detector`, `metacognitive_monitor`
- Merge notes: Meta-cognition plugins (94–97) are critique passes, not separate skills.
