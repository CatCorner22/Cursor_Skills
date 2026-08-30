---
name: ai-transfer-ecosystem-primer
disable-model-invocation: true
description: "Router for the AI-transfer catalog (45 techniques, #1–50 with five merges) — gates, scaffolds, and pipeline stages. Use when hardening agents, RAG, multi-step chains, or when the user mentions transferable skills, discipline patterns, or AI quality plugins. Scope boundary: domain apps (college, M365) → those primers; human craft loops → `craft-systems-primer`."
metadata:
  priority: 7
  promptSignals:
    anyOf:
      - "AI transferable skills"
      - "cross domain AI"
      - "hallucination gate"
      - "pipeline stage"
    minScore: 6
---
# AI-transferable skills ecosystem

**Meta-pattern:** `[Discipline constraints] → port into [AI fuzzy workflows] → novel quality gains without new ML research.`

Forty-five loadable techniques (catalog #1–50, five merged into existing skills) plus seven category routers. Runtime: `scripts/ai_plugin_bundle.py` (100 plugins; default tier enables #1–50 plus orchestrator utilities).

## Category routers

| Category | Router |
|---|---|
| Quality control (#1–9) | **`ai-transfer-quality-control`** |
| Architecture (#10–16) | **`ai-transfer-architecture`** |
| Adaptive (#17–21) | **`ai-transfer-adaptive`** |
| Memory (#22–25) | **`ai-transfer-memory`** |
| Refinement (#26–30) | **`ai-transfer-refinement`** |
| Extension (#31–40) | **`ai-transfer-extension`** |
| Advanced (#41–50) | **`ai-transfer-advanced`** |

## Recommended starting points

| ROI | Skills |
|---|---|
| 🟢 Low effort | `pipeline-preflight`, `proofreading-marks`, `emergency-triage-compute` |
| 🟡 High impact | `double-entry-claims`, `progressive-resistance-critique`, `five-whys-failure-recovery` |
| 🔴 Innovative | `proof-trees-reasoning`, `counterpoint-perspectives`, `wine-blending-fusion` |

## Links to existing packs

| Overlap | Existing skill |
|---|---|
| Human mise en place | `workspace-mise-en-place` |
| Human OODA | `ooda-lean-loop` |
| Citations | `citation-literacy`, `journalistic-attribution` |
| Prompt craft | `prompt-optimizer` (absorbs `token_optimizer`) |
| Student pedagogy | `study-system` (absorbs `pedagogical_sequence`) |
| Agent eval | `langsmith-online-eval-engineering` |

## Runtime-only plugins (51–100)

Security scanners, creative/communication helpers, analytics, legal/medical/regulatory stubs, and orchestrator internals stay in `scripts/ai_plugin_bundle.py`. They are **opt-in** (default off except orchestrator utilities). Do not add them as skills.

## Quick reference (catalog #1–50)

| # | Skill | Domain | Category | Difficulty |
|---|-------|--------|----------|------------|
| 1 | `double-entry-claims` | Accounting | quality-control | medium |
| 2 | `pipeline-preflight` | Culinary arts | quality-control | low |
| 3 | `progressive-resistance-critique` | Strength coaching | quality-control | medium |
| 4 | `chain-of-custody-provenance` | Law enforcement / forensics | quality-control | high |
| 5 | `sterile-cockpit-context` | Aviation | quality-control | medium |
| 6 | `five-whys-failure-recovery` | Toyota Production System | quality-control | medium |
| 7 | `journalistic-attribution` | Journalism | quality-control | medium |
| 8 | `survey-triangulation` | Land surveying | quality-control | medium |
| 9 | `proofreading-marks` | Publishing | quality-control | low |
| 10 | `score-study-dual-axis` | Classical conducting | architecture | medium |
| 11 | `ooda-adaptive-context` | Combat aviation (Boyd) | architecture | high |
| 12 | `proof-trees-reasoning` | Mathematics | architecture | high |
| 13 | `counterpoint-perspectives` | Music theory | architecture | high |
| 14 | `cartographic-zoom` | Cartography | architecture | medium |
| 15 | `stage-blocking-layout` | Theater direction | architecture | medium |
| 16 | `weaving-warp-weft` | Textile arts | architecture | medium |
| 17 | `emergency-triage-compute` | Emergency medicine (START) | adaptive | low |
| 18 | `after-action-review` | Military | adaptive | medium |
| 19 | `fermentation-feedback` | Biochemistry / food science | adaptive | high |
| 20 | `wayfinding-restructure` | Urban design | adaptive | high |
| 21 | `glass-annealing-hardening` | Glassblowing | adaptive | medium |
| 22 | `stratigraphy-memory` | Archaeology | memory | high |
| 23 | `endgame-tablebase-cache` | Chess computing | memory | medium |
| 24 | `library-taxonomy-retrieval` | Library science | memory | medium |
| 25 | `wildlife-corridor-bridging` | Conservation biology | memory | high |
| 26 | `color-grading-output` | Film post-production | refinement | medium |
| 27 | `debate-adjudication-voting` | Competitive debate | refinement | high |
| 28 | `wine-blending-fusion` | Enology | refinement | high |
| 29 | `gemstone-faceting-refinement` | Gemology | refinement | medium |
| 30 | `localization-qa-filter` | Software localization | refinement | medium |
| 31 | `just-intonation-calibration` | Music theory (tuning) | extension | medium |
| 32 | `load-bearing-structure` | Architecture / structural engineering | extension | medium |
| 33 | `orchard-graft-transfer` | Horticulture | extension | medium |
| 34 | `differential-diagnosis-intent` | Clinical reasoning (method only) | extension | medium |
| 35 | `stress-test-robustness` | Structural engineering | extension | medium |
| 36 | `library-taxonomy-retrieval` (absorbs memory_palace) | Mnemonics | memory | merged |
| 37 | `tidal-pacing-rhythm` | Oceanography / rhetoric | extension | low |
| 38 | `underwriting-risk-gate` | Insurance underwriting | extension | medium |
| 39 | `endgame-tablebase-cache` (absorbs opening_theory) | Chess openings | memory | merged |
| 40 | `metamorphosis-stages` | Developmental biology | extension | medium |
| 41 | `chain-of-custody-provenance` (absorbs black_box) | Aviation forensics | quality-control | merged |
| 42 | `fermentation-feedback` (absorbs levain_culture) | Baking / fermentation | adaptive | merged |
| 43 | `seismic-flexibility` | Earthquake engineering | advanced | medium |
| 44 | `sidechain-priority` | Audio engineering | advanced | medium |
| 45 | `cross-pollination-structure` | Plant breeding / rhetoric | advanced | high |
| 46 | `containment-safety-layers` | Biosafety (BSL) | advanced | high |
| 47 | `sail-trim-tuning` | Sailing | advanced | low |
| 48 | `interaction-table` | Pharmacology / chemistry | advanced | medium |
| 49 | `stratigraphy-memory` (absorbs paleontology) | Paleontology | memory | merged |
| 50 | `parallax-depth` | Photography / surveying | advanced | medium |

## Implementation guide

1. Pick technique matching your dominant failure mode
2. Map discipline constraint → programmatic gate or pipeline stage
3. Prototype as prompt scaffold before full plugin
4. Measure on 10–20 real tasks
5. Log failures with `five-whys-failure-recovery`
6. Optional: run `python3 scripts/ai_plugin_bundle.py --profile --query "..."`
