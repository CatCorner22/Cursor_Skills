---
name: weaving-warp-weft
disable-model-invocation: true
description: "Interleave fixed structural threads (warp: required claims, compliance) with flexible expressive weft (tone, examples). Enforce both — compliant AND engaging. Use for regulated or rubric-bound outputs. Scope boundary: proofreading marks for weft edits → `proofreading-marks`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "warp weft"
      - "structure and tone"
      - "compliance and engaging"
    minScore: 6
---

# Weaving warp and weft

**#16** · **Domain:** Textile arts · **Category:** architecture · **Difficulty:** 🟡 Medium

## Core principle

Warp gives structure; weft gives pattern — fabric needs both.

## AI problem addressed

Rigid template OR free prose trade-off.

## Implementation

Define warp (non-negotiable facts, constraints) and weft (voice, examples).
Generate interleaved; auto-check warp completeness; adapt weft to audience.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-architecture`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `textile_weaving`
