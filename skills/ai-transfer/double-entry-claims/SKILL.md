---
name: double-entry-claims
disable-model-invocation: true
description: "Hallucination suppression via structural claim/evidence pairing: every factual claim must balance with a supporting source before output delivers. Use when verifying AI outputs, building RAG gates, or when the user asks for claim checking, evidence balance, or hallucination suppression. Scope boundary: human workspace prep → `workspace-mise-en-place`; source citation style → `citation-literacy`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "double entry"
      - "claim evidence"
      - "hallucination suppression"
      - "verify claims"
    minScore: 6
---
# Double-entry claim reconciliation

**#1** · **Domain:** Accounting · **Category:** quality-control · **Difficulty:** 🟡 Medium

## Core principle

Every entry has two sides — claim and evidence. The ledger does not close until they reconcile.

## AI problem addressed

Probabilistic confidence scores do not structurally block ungrounded claims.

## Implementation

```
FOR each factual claim C in draft:
  IF source(C) EXISTS AND supports(C):
    PASS
  ELSE:
    FLAG(C) or STRIP(C)
Do not deliver until ledger closes (all claims balanced or explicitly marked unknown).
```

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-quality-control`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `ledger_gate`
- Also implements: `fact_check_deep`, `financial_audit`
- Merge notes: Also absorbs `fact_check_deep` and `financial_audit` — same claim/evidence gate.
