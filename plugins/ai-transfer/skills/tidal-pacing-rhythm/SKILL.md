---
name: tidal-pacing-rhythm
description: Measure sentence-length tide (high/mid/low) and even the rhythm when variance is extreme. Use on long prose that feels rushed or swampy. Scope boundary — token budget cuts → `prompt-optimizer`; zoom depth → `cartographic-zoom`.
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Tidal pacing of sentence rhythm

**#37** · **Domain:** Oceanography / rhetoric · **Category:** extension · **Difficulty:** 🟢 Low

## Core principle

Tide has a period — all-short or all-long sentences lose the reader.

## AI problem addressed

Drafts bunch into telegram bursts or 40-word swells.

## Implementation

Compute words/sentence. high_tide <12, mid 12–25, low_tide >25.
If variance is huge, split long sentences and join fragments — do not rewrite claims.

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`ai-transfer-extension`**
- Catalog: **`ai-transfer-ecosystem-primer`**
- Runtime plugin id: `tidal_pacing`
