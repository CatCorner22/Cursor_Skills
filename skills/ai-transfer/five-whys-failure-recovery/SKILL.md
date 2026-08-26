---
name: five-whys-failure-recovery
description: "On pipeline failure, drill five whys to root cause and log permanent system fixes — not prompt whack-a-mole. Use after hallucinations, format errors, or constraint misses. Scope boundary: human kaizen line → `ooda-lean-loop`; routing audit → `skill-library-audit`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "five whys"
      - "root cause"
      - "failure recovery"
      - "why did this fail"
    minScore: 6
---

# Five Whys failure recovery

**#6** · **Domain:** Toyota Production System · **Category:** quality-control · **Difficulty:** 🟡 Medium

## Core principle

Every defect is a system failure. Fix the system permanently.

## AI problem addressed

Retry with tweaked prompt fixes symptoms not causes.

## Implementation

1. Log failure artifact
2. Ask Why ×5 until schema/process gap found
3. Implement structural fix (schema, gate, preflight)
4. Add to failure case library
Example: missing file → orchestration passes text not metadata → add inter-step schema.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-quality-control`**
- Catalog: **`ai-transfer-ecosystem-primer`**
