---
name: chain-of-custody-provenance
description: 'Token- or block-level provenance: which inputs, tools, prompt sections, and turns produced each output segment. Use when debugging AI failures or audit requirements. Scope boundary: claim-level sources → `journalistic-attribution`; orient logging → `ooda-adaptive-context`.'
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
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
