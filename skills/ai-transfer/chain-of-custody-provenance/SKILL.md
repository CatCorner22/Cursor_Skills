---
name: chain-of-custody-provenance
disable-model-invocation: true
description: "Token- or block-level provenance: which inputs, tools, prompt sections, and turns produced each output segment. Use when debugging AI failures or audit requirements. Scope boundary: claim-level sources → `journalistic-attribution`; orient logging → `ooda-adaptive-context`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "provenance"
      - "chain of custody"
      - "audit trail"
      - "lineage"
    minScore: 6
---
# Chain of custody provenance

**#4** · **Domain:** Law enforcement / forensics · **Category:** quality-control · **Difficulty:** 🔴 High

## Core principle

Unbroken chain of who handled what, when, and why — tampering voids admissibility.

## AI problem addressed

Outputs lack traceability to influencing context and tools.

## Implementation

Tag each output block with:
- Source inputs consulted
- Tool calls (with version)
- Prompt section applied
- Prior turns referenced
- Timestamp and model version
Trace backward from disputed segment to breaking link.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-quality-control`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `chain_of_custody`
- Also implements: `black_box`
- Merge notes: Also absorbs `black_box`: immutable session recorder on the same chain.
