---
name: underwriting-risk-gate
disable-model-invocation: true
description: "Score GREEN/YELLOW/RED risk before delivery for medical, legal, or financial-advice asks; hold RED for review. Use as a pre-delivery gate, not as advice. Scope boundary — does not give legal/medical advice; claim support → `double-entry-claims`; independent safety layers → `containment-safety-layers`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "underwriting risk"
      - "pre-delivery risk"
      - "RED YELLOW GREEN gate"
    minScore: 6
---

# Underwriting pre-delivery risk gate

**#38** · **Domain:** Insurance underwriting · **Category:** extension · **Difficulty:** 🟡 Medium

## Core principle

Price the risk before you bind the policy.

## AI problem addressed

High-stakes drafts ship with the same confidence as a rewrite.

## Implementation

Scan query+output for medical / legal / financial-advice terms.
GREEN zero hits, YELLOW one, RED two or more. RED → warn and hold.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-extension`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `underwriting_risk`
