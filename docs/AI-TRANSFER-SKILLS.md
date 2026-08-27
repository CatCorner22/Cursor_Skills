# AI-Transferable Skills — Cross-Domain Techniques for AI Model Improvement

Canonical **skill implementations** live in [`skills/ai-transfer/`](../skills/ai-transfer/). Each technique is a loadable `SKILL.md` plus seven category routers and `ai-transfer-ecosystem-primer`.

The cleaned Python runtime is [`scripts/ai_plugin_bundle.py`](../scripts/ai_plugin_bundle.py) (100 plugins, default `balanced` tier). Tests: [`scripts/test_ai_plugin_bundle.py`](../scripts/test_ai_plugin_bundle.py).

> Cross-domain discipline constraints ported into AI workflows produce quality gains unavailable through conventional ML optimization alone — without new ML research.

## Meta-pattern

```
[Discipline vocabulary + structural constraints]
        ↓ port into
[AI workflow space operating on fuzzy heuristics]
        ↓ produces
[Novel quality improvements]
```

The bottleneck is **translation**, not models.

## Category routers

| Category | Router | Techniques |
|---|---|---|
| Quality control | `ai-transfer-quality-control` | #1–9 |
| Architectural restructuring | `ai-transfer-architecture` | #10–16 |
| Adaptive & dynamic processing | `ai-transfer-adaptive` | #17–21 |
| Retrieval, memory & context | `ai-transfer-memory` | #22–25 |
| Refinement, fusion & polish | `ai-transfer-refinement` | #26–30 |
| Extension pack | `ai-transfer-extension` | #31–40 (minus merges) |
| Advanced pack | `ai-transfer-advanced` | #41–50 (minus merges) |

Start at **`ai-transfer-ecosystem-primer`** for routing.

## Complete quick-reference (catalog #1–50)

| # | Skill | Domain | Category | Difficulty |
|---|-------|--------|----------|------------|
| 1 | `double-entry-claims` | Double-entry bookkeeping | Quality control | 🟡 |
| 2 | `pipeline-preflight` | Mise en place | Quality control | 🟢 |
| 3 | `progressive-resistance-critique` | Progressive resistance training | Quality control | 🟡 |
| 4 | `chain-of-custody-provenance` | Chain of custody | Quality control | 🔴 |
| 5 | `sterile-cockpit-context` | Sterile cockpit rule | Quality control | 🟡 |
| 6 | `five-whys-failure-recovery` | Root cause analysis (5 Whys) | Quality control | 🟡 |
| 7 | `journalistic-attribution` | Journalistic attribution | Quality control | 🟡 |
| 8 | `survey-triangulation` | Survey triangulation | Quality control | 🟡 |
| 9 | `proofreading-marks` | Editorial proofreading marks | Quality control | 🟢 |
| 10 | `score-study-dual-axis` | Score study | Architecture | 🟡 |
| 11 | `ooda-adaptive-context` | OODA loop | Architecture | 🔴 |
| 12 | `proof-trees-reasoning` | Proof trees | Architecture | 🔴 |
| 13 | `counterpoint-perspectives` | Musical counterpoint | Architecture | 🔴 |
| 14 | `cartographic-zoom` | Cartographic generalization | Architecture | 🟡 |
| 15 | `stage-blocking-layout` | Stage blocking | Architecture | 🟡 |
| 16 | `weaving-warp-weft` | Textile weaving | Architecture | 🟡 |
| 17 | `emergency-triage-compute` | Emergency triage (START) | Adaptive | 🟢 |
| 18 | `after-action-review` | After-action reviews | Adaptive | 🟡 |
| 19 | `fermentation-feedback` | Fermentation science | Adaptive | 🔴 |
| 20 | `wayfinding-restructure` | Urban wayfinding | Adaptive | 🔴 |
| 21 | `glass-annealing-hardening` | Glass annealing | Adaptive | 🟡 |
| 22 | `stratigraphy-memory` | Archaeological stratigraphy | Memory | 🔴 |
| 23 | `endgame-tablebase-cache` | Chess endgame tablebases | Memory | 🟡 |
| 24 | `library-taxonomy-retrieval` | Library cataloguing | Memory | 🟡 |
| 25 | `wildlife-corridor-bridging` | Wildlife corridors | Memory | 🔴 |
| 26 | `color-grading-output` | Color grading | Refinement | 🟡 |
| 27 | `debate-adjudication-voting` | Debate adjudication | Refinement | 🔴 |
| 28 | `wine-blending-fusion` | Wine blending | Refinement | 🔴 |
| 29 | `gemstone-faceting-refinement` | Gemstone faceting | Refinement | 🟡 |
| 30 | `localization-qa-filter` | Localization QA | Refinement | 🟡 |
| 31 | `just-intonation-calibration` | Just intonation | Extension | 🟡 |
| 32 | `load-bearing-structure` | Structural engineering | Extension | 🟡 |
| 33 | `orchard-graft-transfer` | Horticulture | Extension | 🟡 |
| 34 | `differential-diagnosis-intent` | Clinical reasoning (method) | Extension | 🟡 |
| 35 | `stress-test-robustness` | Stress testing | Extension | 🟡 |
| 36 | → `library-taxonomy-retrieval` | Memory palace (merged) | Memory | merged |
| 37 | `tidal-pacing-rhythm` | Tidal pacing | Extension | 🟢 |
| 38 | `underwriting-risk-gate` | Insurance underwriting | Extension | 🟡 |
| 39 | → `endgame-tablebase-cache` | Opening theory (merged) | Memory | merged |
| 40 | `metamorphosis-stages` | Metamorphosis | Extension | 🟡 |
| 41 | → `chain-of-custody-provenance` | Black box (merged) | Quality control | merged |
| 42 | → `fermentation-feedback` | Levain culture (merged) | Adaptive | merged |
| 43 | `seismic-flexibility` | Earthquake engineering | Advanced | 🟡 |
| 44 | `sidechain-priority` | Sidechain compression | Advanced | 🟡 |
| 45 | `cross-pollination-structure` | Cross-pollination | Advanced | 🔴 |
| 46 | `containment-safety-layers` | Biosafety layers | Advanced | 🔴 |
| 47 | `sail-trim-tuning` | Sail trim | Advanced | 🟢 |
| 48 | `interaction-table` | Interaction table | Advanced | 🟡 |
| 49 | → `stratigraphy-memory` | Paleontology (merged) | Memory | merged |
| 50 | `parallax-depth` | Parallax | Advanced | 🟡 |

## Recommended starting points

| ROI | Skills |
|---|---|
| 🟢 Highest ROI, lowest effort | `pipeline-preflight`, `proofreading-marks`, `emergency-triage-compute` |
| 🟡 Highest impact, moderate effort | `double-entry-claims`, `progressive-resistance-critique`, `five-whys-failure-recovery` |
| 🔴 Most innovative, highest effort | `proof-trees-reasoning`, `counterpoint-perspectives`, `wine-blending-fusion` |

## Overlap with other packs

| Technique | Also see |
|---|---|
| Mise en place (#2) | `workspace-mise-en-place` (human prep), `pipeline-preflight` (AI preflight) |
| OODA (#11) | `ooda-lean-loop` (human), `ooda-adaptive-context` (AI pipeline) |
| 5 Whys (#6) | `ooda-lean-loop` kaizen, `five-whys-failure-recovery` (system log) |
| Attribution (#7) | `citation-literacy`, `journalistic-attribution` |
| Token cutting | `prompt-optimizer` (absorbs runtime `token_optimizer`) |
| Pedagogy | `study-system` (absorbs runtime `pedagogical_sequence`) |

## Runtime

```bash
python3 scripts/ai_plugin_bundle.py --list-plugins
python3 scripts/ai_plugin_bundle.py --test --tier balanced
python3 scripts/ai_plugin_bundle.py --profile --query "What is quantum computing?"
python3 scripts/test_ai_plugin_bundle.py
```

Plugins 51–100 (security scanners, creative/communication helpers, analytics, legal/medical stubs, extra personalization) stay **runtime-only** and default off. Similarity in the bundle is word-overlap, not a production NLP stack.

## Implementation guide

1. Pick one technique matching your dominant failure mode
2. Map the discipline constraint → gate, filter, annotation, or pipeline stage
3. Prototype as prompt scaffold before full plugin
4. Measure before/after on 10–20 real tasks
5. Log failures with `five-whys-failure-recovery`

Regenerate skill files: `python3 scripts/generate-ai-transfer-skills.py`

---

*Document version 2.0 — pack expanded 2026-08-27 from the 100-plugin bundle*
