---
name: containment-safety-layers
description: "Require independent safety layers (pattern, keyword, policy) that can each fail closed. Use for high-stakes generation, not everyday chat. Scope boundary — this is layered containment, not a jailbreak keyword skill; phase gating → `sterile-cockpit-context`; risk color → `underwriting-risk-gate`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "containment safety"
      - "independent safety layers"
      - "BSL layers"
    minScore: 6
---

# Containment safety layers

**#46** · **Domain:** Biosafety (BSL) · **Category:** advanced · **Difficulty:** 🔴 High

## Core principle

One glove is not a BSL cabinet — layers are independent and redundant.

## AI problem addressed

A single regex or a single prompt rule is treated as the whole safety case.

## Implementation

Layer 1: destructive-command patterns
Layer 2: sensitive-token keywords
Layer 3: policy/pattern hook (may be a no-op placeholder)
HALT only if a layer fails. Do not teach bypasses.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-advanced`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `containment_safety`
