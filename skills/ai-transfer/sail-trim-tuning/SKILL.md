---
name: sail-trim-tuning
disable-model-invocation: true
description: "Read user confusion/satisfaction signals and trim the next beat (more examples vs hold course). Use on multi-turn work. Scope boundary — mid-stream environment loop → `fermentation-feedback`; human OODA → `ooda-lean-loop`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "sail trim"
      - "telltales"
      - "mid response adjust"
    minScore: 6
---
# Sail trim mid-response tuning

**#47** · **Domain:** Sailing · **Category:** advanced · **Difficulty:** 🟢 Low

## Core principle

Ease or sheet based on the telltales — not on the last weather report.

## AI problem addressed

The agent keeps the same verbosity after the user says they are lost or done.

## Implementation

confused/don't understand → add examples, simplify
thanks/great/perfect → hold course
else → no trim
Log the trim; do not rewrite history.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-advanced`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `sail_trim`
