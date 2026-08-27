#!/usr/bin/env python3
"""Generate ai-transfer skill pack from the AI-transferable techniques spec."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "skills" / "ai-transfer"

TECHNIQUES = [
    {
        "name": "double-entry-claims",
        "title": "Double-entry claim reconciliation",
        "domain": "Accounting",
        "category": "quality-control",
        "difficulty": "medium",
        "description": "Hallucination suppression via structural claim/evidence pairing: every factual claim must balance with a supporting source before output delivers. Use when verifying AI outputs, building RAG gates, or when the user asks for claim checking, evidence balance, or hallucination suppression. Scope boundary: human workspace prep → `workspace-mise-en-place`; source citation style → `citation-literacy`.",
        "principle": "Every entry has two sides — claim and evidence. The ledger does not close until they reconcile.",
        "problem": "Probabilistic confidence scores do not structurally block ungrounded claims.",
        "workflow": """```
FOR each factual claim C in draft:
  IF source(C) EXISTS AND supports(C):
    PASS
  ELSE:
    FLAG(C) or STRIP(C)
Do not deliver until ledger closes (all claims balanced or explicitly marked unknown).
```""",
        "phrases": ["double entry", "claim evidence", "hallucination suppression", "verify claims"],
    },
    {
        "name": "pipeline-preflight",
        "title": "AI pipeline pre-flight (mise en place)",
        "domain": "Culinary arts",
        "category": "quality-control",
        "difficulty": "low",
        "description": "Pre-execution audit before AI generation: required inputs, files, constraints, tools, and prior outputs present. Halt instead of running cold. Use before agent runs, RAG pipelines, or multi-step chains. Scope boundary: human/study prep → `workspace-mise-en-place`; craft routing → `craft-systems-primer`.",
        "principle": "No heat until ingredients are prepped, measured, and in place.",
        "problem": "Pipelines run with missing context then backfill assumptions.",
        "workflow": """Checklist before generate:
- [ ] Required input variables present and non-empty
- [ ] Referenced prior outputs exist in context
- [ ] Uploaded files attached and parsed
- [ ] System constraints loaded
- [ ] Required tools authenticated
HALT and report gaps if any fail.""",
        "phrases": ["pre-flight", "pipeline check", "before generation", "input audit"],
    },
    {
        "name": "progressive-resistance-critique",
        "title": "Progressive resistance self-critique",
        "domain": "Strength coaching",
        "category": "quality-control",
        "difficulty": "medium",
        "description": "Escalating self-critique passes: warm-up consistency, moderate alignment, working robustness, max falsifiability. Use instead of single shallow 'review your answer'. Scope boundary: post-delivery debrief → `after-action-review`; proof DAG → `proof-trees-reasoning`.",
        "principle": "Ramp critique intensity — never one-rep-max review cold.",
        "problem": "Single-pass self-review misses distinct failure modes.",
        "workflow": """| Phase | Target | Prompt |
| Warm-up | Internal consistency | Contradictions? |
| Moderate | Question alignment | Unstated assumptions? |
| Working | Core robustness | Strongest objection? |
| Max | Falsifiability | If wrong, what would we observe? |""",
        "phrases": ["self critique", "progressive review", "escalating critique"],
    },
    {
        "name": "chain-of-custody-provenance",
        "title": "Chain of custody provenance",
        "domain": "Law enforcement / forensics",
        "category": "quality-control",
        "difficulty": "high",
        "description": "Token- or block-level provenance: which inputs, tools, prompt sections, and turns produced each output segment. Use when debugging AI failures or audit requirements. Scope boundary: claim-level sources → `journalistic-attribution`; orient logging → `ooda-adaptive-context`.",
        "principle": "Unbroken chain of who handled what, when, and why — tampering voids admissibility.",
        "problem": "Outputs lack traceability to influencing context and tools.",
        "workflow": """Tag each output block with:
- Source inputs consulted
- Tool calls (with version)
- Prompt section applied
- Prior turns referenced
- Timestamp and model version
Trace backward from disputed segment to breaking link.""",
        "phrases": ["provenance", "chain of custody", "audit trail", "lineage"],
    },
    {
        "name": "sterile-cockpit-context",
        "title": "Sterile cockpit context gating",
        "domain": "Aviation",
        "category": "quality-control",
        "difficulty": "medium",
        "description": "Phase-gated context: takeoff (parse inputs only), cruise (full history), landing (validation rules only). Strip distraction during critical phases. Use for high-stakes generation steps. Scope boundary: human prioritization → `ooda-lean-loop`.",
        "principle": "Below 10,000 feet — flight ops only. No idle chatter at critical moments.",
        "problem": "Irrelevant context dilutes focus during parse/validate phases.",
        "workflow": """| Phase | Active context |
| Takeoff (parse) | Input variables + explicit constraints only |
| Cruise (generate) | Accumulated history allowed |
| Landing (validate) | Validation rules + quality checks only |
Restore full context between phases as needed.""",
        "phrases": ["sterile cockpit", "context gating", "phase context"],
    },
    {
        "name": "five-whys-failure-recovery",
        "title": "Five Whys failure recovery",
        "domain": "Toyota Production System",
        "category": "quality-control",
        "difficulty": "medium",
        "description": "On pipeline failure, drill five whys to root cause and log permanent system fixes — not prompt whack-a-mole. Use after hallucinations, format errors, or constraint misses. Scope boundary: human kaizen line → `ooda-lean-loop`; routing audit → `skill-library-audit`.",
        "principle": "Every defect is a system failure. Fix the system permanently.",
        "problem": "Retry with tweaked prompt fixes symptoms not causes.",
        "workflow": """1. Log failure artifact
2. Ask Why ×5 until schema/process gap found
3. Implement structural fix (schema, gate, preflight)
4. Add to failure case library
Example: missing file → orchestration passes text not metadata → add inter-step schema.""",
        "phrases": ["five whys", "root cause", "failure recovery", "why did this fail"],
    },
    {
        "name": "journalistic-attribution",
        "title": "Journalistic attribution (verify then write)",
        "domain": "Journalism",
        "category": "quality-control",
        "difficulty": "medium",
        "description": "Source-first generation: retrieve evidence per claim before prose, inline attribution, strip unattributable claims. Use for factual writing and RAG outputs. Scope boundary: bibliography formatting → `citation-literacy`; triple-path check → `survey-triangulation`.",
        "principle": "Every claim maps to a named on-record source at claim level — not bolted-on endnotes.",
        "problem": "Write-then-cite order produces decorative citations.",
        "workflow": """1. Parse query for claims needed
2. Retrieve source per claim BEFORE generating
3. Generate with inline attribution
4. Verify sources exist and were consulted
5. Strip unattributed claims""",
        "phrases": ["inline citation", "verify then write", "source first", "attribution"],
    },
    {
        "name": "survey-triangulation",
        "title": "Survey triangulation validation",
        "domain": "Land surveying",
        "category": "quality-control",
        "difficulty": "medium",
        "description": "Require three independent retrieval paths per factual claim; score agreement 3/3, 2/3, or contested. Use when single-source RAG is insufficient. Scope boundary: double-entry gate → `double-entry-claims`.",
        "principle": "Never trust one measurement — intersect from three known positions.",
        "problem": "Top-ranked single source and echo chambers create false confidence.",
        "workflow": """| Agreement | Action |
| 3/3 | Include, cite all three |
| 2/3 | Include with caveat, flag outlier |
| Contested | Label disputed explicitly |
Use different queries, source types, and time snapshots.""",
        "phrases": ["triangulation", "cross validate sources", "three sources"],
    },
    {
        "name": "proofreading-marks",
        "title": "Editorial proofreading marks",
        "domain": "Publishing",
        "category": "quality-control",
        "difficulty": "low",
        "description": "Granular annotation layer between draft and delivery: QUERY, DELETE, STET, TRANSPOSE, INSERT — not wholesale rewrite. Use for AI self-review and human-in-the-loop edit. Scope boundary: full rewrite → domain writing skills.",
        "principle": "Mark specific errors without destroying the original.",
        "problem": "Review is accept-all or total rewrite — no middle ground.",
        "workflow": """Tags: `[QUERY]` verify | `[DELETE]` remove | `[STET]` keep | `[TRANSPOSE]` move | `[INSERT]` add
Apply marks; accept/reject individually before delivery.""",
        "phrases": ["proofreading marks", "annotation layer", "QUERY DELETE STET"],
    },
    {
        "name": "score-study-dual-axis",
        "title": "Score study dual-axis reasoning",
        "domain": "Classical conducting",
        "category": "architecture",
        "difficulty": "medium",
        "description": "Horizontal pass (narrative arc) plus vertical pass (parallel considerations at each step). Synthesize output satisfying both. Use for complex analysis and long-form reasoning. Scope boundary: dependency DAG → `proof-trees-reasoning`.",
        "principle": "Read vertically (simultaneous voices) and horizontally (time) before conducting.",
        "problem": "Linear prose is organized OR thorough, rarely both.",
        "workflow": """1. Horizontal: map argument arc start→finish
2. Vertical: at each step list audience, constraints, edge cases, tone
3. Generate satisfying both axes
4. Check: flows horizontally? complete vertically at each step?""",
        "phrases": ["dual axis", "horizontal vertical", "score study", "narrative arc"],
    },
    {
        "name": "ooda-adaptive-context",
        "title": "OODA adaptive context (AI pipeline)",
        "domain": "Combat aviation (Boyd)",
        "category": "architecture",
        "difficulty": "high",
        "description": "Four-phase AI pipeline with logged Orient step: observe raw context, orient (filter/prioritize with inspectable log), decide approach, act. Use when debugging why context was ignored. Scope boundary: human OODA → `ooda-lean-loop`.",
        "principle": "Orient is explicit filtering — inspectable, not collapsed into embedding lookup.",
        "problem": "Observe+orient merged; no log of what was discarded.",
        "workflow": """1. Observe: gather all context
2. Orient: filter by task; LOG kept/discarded + why
3. Decide: select method
4. Act: generate
Debug 'ignored file' → read orient log.""",
        "phrases": ["OODA pipeline", "orient log", "context filter AI"],
    },
    {
        "name": "proof-trees-reasoning",
        "title": "Proof trees (reasoning DAG)",
        "domain": "Mathematics",
        "category": "architecture",
        "difficulty": "high",
        "description": "Declare reasoning DAG before prose: premises, claims, dependencies. Flag downstream if upstream fails. Use for multi-step arguments and agent plans. Scope boundary: dual-axis → `score-study-dual-axis`.",
        "principle": "Explicit dependencies — if a premise fails, downstream collapses visibly.",
        "problem": "Prose hides dependencies; step 3 error poisons 4–9 invisibly.",
        "workflow": """Declare: Premise P1, P2 → Claim A(P1,P2) → Claim B(A,P3) → Conclusion C(B)
Generate prose following DAG only.
Self-check: weakest premise? Downstream auto-flag if premise fails.""",
        "phrases": ["proof tree", "reasoning DAG", "dependency graph"],
    },
    {
        "name": "counterpoint-perspectives",
        "title": "Musical counterpoint perspectives",
        "domain": "Music theory",
        "category": "architecture",
        "difficulty": "high",
        "description": "Generate 2–3 independent analytical voices with own logic, then harmonize into interwoven output — not pros/cons list. Use for multi-stakeholder or multi-framework analysis. Scope boundary: debate scoring → `debate-adjudication-voting`.",
        "principle": "Independent voices complete alone yet richer in harmony.",
        "problem": "Single voice or appended 'on the other hand' hedging.",
        "workflow": """1. Voice 1: coherent framework A argument
2. Voice 2: framework B argument
3. Voice 3 (optional): framework C
4. Compose interaction — resolve intersections, not juxtaposition""",
        "phrases": ["counterpoint", "multiple perspectives", "interwoven arguments"],
    },
    {
        "name": "cartographic-zoom",
        "title": "Cartographic zoom levels",
        "domain": "Cartography",
        "category": "architecture",
        "difficulty": "medium",
        "description": "Generate country/city/street zoom levels: 1–2 sentences, 1–2 paragraphs, full deep-dive. Detect from query or offer zoom-in. Use when verbosity mismatch hurts UX. Scope boundary: stage layout → `stage-blocking-layout`.",
        "principle": "Detail adapts to viewer scale — same data, different generalization.",
        "problem": "Single-zoom outputs guess wrong depth.",
        "workflow": """| Zoom | Format | When |
| Country | 1–2 sentences | Urgent / glance |
| City | 1–2 paragraphs | Standard |
| Street | Full analysis | Follow-up / deep |
Detect from urgency, format hints, or prior context.""",
        "phrases": ["zoom level", "TLDR depth", "summary vs deep dive"],
    },
    {
        "name": "stage-blocking-layout",
        "title": "Stage blocking information layout",
        "domain": "Theater direction",
        "category": "architecture",
        "difficulty": "medium",
        "description": "Spatial emphasis: center stage = core message; flanks = evidence; opposing entrances = dialectic; center curtain = synthesis. Use for reports, docs, and structured responses. Scope boundary: warp/weft structure → `weaving-warp-weft`.",
        "principle": "Position conveys emphasis — not only bold text.",
        "problem": "Sequential dump with no spatial architecture.",
        "workflow": """Map sections: opening center (thesis) → flanks (evidence) → opposing sides (tension) → center close (synthesis)
Translate to headers, sidebars, footnotes, callouts.""",
        "phrases": ["stage blocking", "information layout", "spatial emphasis"],
    },
    {
        "name": "weaving-warp-weft",
        "title": "Weaving warp and weft",
        "domain": "Textile arts",
        "category": "architecture",
        "difficulty": "medium",
        "description": "Interleave fixed structural threads (warp: required claims, compliance) with flexible expressive weft (tone, examples). Enforce both — compliant AND engaging. Use for regulated or rubric-bound outputs. Scope boundary: proofreading marks for weft edits → `proofreading-marks`.",
        "principle": "Warp gives structure; weft gives pattern — fabric needs both.",
        "problem": "Rigid template OR free prose trade-off.",
        "workflow": """Define warp (non-negotiable facts, constraints) and weft (voice, examples).
Generate interleaved; auto-check warp completeness; adapt weft to audience.""",
        "phrases": ["warp weft", "structure and tone", "compliance and engaging"],
    },
    {
        "name": "emergency-triage-compute",
        "title": "Emergency triage compute budgeting",
        "domain": "Emergency medicine (START)",
        "category": "adaptive",
        "difficulty": "low",
        "description": "Classify tasks Immediate/Delayed/Minor/Deceased before processing; allocate reasoning budget by stakes. Use at router/orchestrator layer. Scope boundary: human prioritization → `ooda-lean-loop`.",
        "principle": "Treat maximum survival — not fairness of equal compute.",
        "problem": "Formatting and research questions get same budget.",
        "workflow": """| Class | Examples | Budget |
| Immediate | Safety, legal, medical | Max |
| Delayed | Research, planning | Standard |
| Minor | Format, rewrite | Minimal |
| Deceased | Out of scope, malformed | Reject early |""",
        "phrases": ["triage", "compute budget", "reasoning budget", "task classify"],
    },
    {
        "name": "after-action-review",
        "title": "After-action review (AAR)",
        "domain": "Military",
        "category": "adaptive",
        "difficulty": "medium",
        "description": "Post-generation debrief: intended vs actual vs gap vs prescription. Log for recurring pattern fixes. Use after agent tasks complete. Scope boundary: five whys on hard failures → `five-whys-failure-recovery`.",
        "principle": "What was supposed to happen? What did? Why the gap? Sustain or improve?",
        "problem": "Generate, deliver, move on — no systematic debrief.",
        "workflow": """1. Original intent (parsed from prompt)
2. Actual output
3. Delta (gap)
4. Prescription for next time
Aggregate logs → recurring failure patterns.""",
        "phrases": ["after action review", "AAR", "post debrief", "what went wrong"],
    },
    {
        "name": "fermentation-feedback",
        "title": "Fermentation environmental feedback",
        "domain": "Biochemistry / food science",
        "category": "adaptive",
        "difficulty": "high",
        "description": "Mid-generation monitoring: user activity, corrections typing, deadlines, confidence — adjust or abort mid-stream. Use for long agent runs and streaming workflows. Scope boundary: post-hoc AAR → `after-action-review`.",
        "principle": "Environment responds to the process continuously — not fire-and-forget.",
        "problem": "Batch in/out with no mid-flight sensing.",
        "workflow": """After each step/paragraph check: user active? correction started? deadline passed? confidence drop?
Adjust: pivot, accelerate, or abort mid-stream.""",
        "phrases": ["mid generation feedback", "environmental loop", "streaming adjust"],
    },
    {
        "name": "wayfinding-restructure",
        "title": "Urban wayfinding restructure",
        "domain": "Urban design",
        "category": "adaptive",
        "difficulty": "high",
        "description": "Instrument consumption behavior (scroll-back, re-prompt, abandon) to restructure future outputs. Use for productized AI interfaces with telemetry. Scope boundary: static layout → `stage-blocking-layout`.",
        "principle": "Adapt signage to how people actually move — not ideal paths.",
        "problem": "Linear output assumes logical reading; no behavior feedback.",
        "workflow": """Track: scroll-back zones → frontload; re-prompt sections → clarify; abandon zones → shorten/restructure.
Feed patterns into next output architecture.""",
        "phrases": ["wayfinding", "user behavior feedback", "scroll back restructure"],
    },
    {
        "name": "glass-annealing-hardening",
        "title": "Glass annealing output hardening",
        "domain": "Glassblowing",
        "category": "adaptive",
        "difficulty": "medium",
        "description": "Staged delivery: high temp (everything flexible) → medium (structure locked) → cool (typos only). Use for long documents and multi-pass review. Scope boundary: faceting angles → `gemstone-faceting-refinement`.",
        "principle": "Gradual cooling resolves internal stress — fast cool shatters.",
        "problem": "Hot delivery commits to flawed structure early.",
        "workflow": """| Temp | Locked | Flexible |
| High | Nothing | Structure, content |
| Medium | Major structure | Wording, examples |
| Cool | All content | Typos, format only |""",
        "phrases": ["annealing", "staged delivery", "cooling phases", "lock structure"],
    },
    {
        "name": "stratigraphy-memory",
        "title": "Archaeological stratigraphy memory",
        "domain": "Archaeology",
        "category": "memory",
        "difficulty": "high",
        "description": "Layer memory by session strata plus disturbance markers; retrieve with integrity confidence. Use for long-horizon agents. Scope boundary: flat RAG → `library-taxonomy-retrieval`; cross-session bridges → `wildlife-corridor-bridging`.",
        "principle": "Deeper layers older; disturbances mix strata — cross-reference before trusting.",
        "problem": "Flat embedding loses temporal depth and context shifts.",
        "workflow": """1. Identify relevant stratum (session cluster)
2. Check disturbance markers (tool break, constraint change)
3. Cross-reference adjacent strata
4. Return memory with confidence from stratigraphic integrity""",
        "phrases": ["stratigraphy memory", "temporal layers", "session strata"],
    },
    {
        "name": "endgame-tablebase-cache",
        "title": "Chess endgame tablebase cache",
        "domain": "Chess computing",
        "category": "memory",
        "difficulty": "medium",
        "description": "Pre-compute and cache known-correct answers for recurring boundary conditions; check tablebase before reasoning. Use for boilerplate code, legal clauses, lookup math. Scope boundary: live reasoning → `proof-trees-reasoning`.",
        "principle": "Exhaustive pre-computation for fixed configurations — reuse perfect answers.",
        "problem": "Recomputing known-correct edge cases every call.",
        "workflow": """Maintain tablebase: auth patterns, CRUD, standard clauses, timezone math.
Lookup FIRST; invoke reasoning only on cache miss with parameter match.""",
        "phrases": ["tablebase cache", "boundary cache", "known correct cache"],
    },
    {
        "name": "library-taxonomy-retrieval",
        "title": "Library taxonomy retrieval",
        "domain": "Library science",
        "category": "memory",
        "difficulty": "medium",
        "description": "Dual retrieval: embedding similarity PLUS taxonomic adjacency in task ontology. Use when related concepts use different wording. Scope boundary: triangulation for facts → `survey-triangulation`.",
        "principle": "Classification maps relationships — not just keyword proximity.",
        "problem": "Embedding-only misses structurally related but differently worded concepts.",
        "workflow": """1. Semantic search (embeddings)
2. Taxonomic browse (adjacent ontology nodes)
Merge results; dedupe; rank by task relevance.""",
        "phrases": ["taxonomy retrieval", "ontology browse", "dual retrieval"],
    },
    {
        "name": "wildlife-corridor-bridging",
        "title": "Wildlife corridor memory bridging",
        "domain": "Conservation biology",
        "category": "memory",
        "difficulty": "high",
        "description": "Detect topic overlap across sessions; inject bridge summaries connecting isolated context islands. Use for long-term personal agents. Scope boundary: strata layers → `stratigraphy-memory`.",
        "principle": "Habitats need corridors — not isolated pockets.",
        "problem": "Each conversation is an island despite conceptual overlap.",
        "workflow": """1. Detect overlap current ↔ historical sessions
2. Generate bridge: 'Three weeks ago you X; connection to today Y'
3. Inject bridge into active context""",
        "phrases": ["memory bridge", "cross session", "conceptual corridor"],
    },
    {
        "name": "color-grading-output",
        "title": "Color grading three-axis refinement",
        "domain": "Film post-production",
        "category": "refinement",
        "difficulty": "medium",
        "description": "Grade pass on luminance (information density), chroma (emotional intensity), hue (stance consistency). Use for tone/ clarity review of drafts. Scope boundary: faceting passes → `gemstone-faceting-refinement`.",
        "principle": "Adjust density, intensity, and framing independently before final grade.",
        "problem": "Fuzzy single-judgment 'sounds good' reviews.",
        "workflow": """| Axis | Check |
| Luminance / density | Key sections clear; rest appropriately summarized? |
| Chroma / intensity | Energy matched to audience? |
| Hue / stance | Worldview framing consistent? |
Flag imbalances with specific section refs.""",
        "phrases": ["color grading", "three axis review", "tone clarity framing"],
    },
    {
        "name": "debate-adjudication-voting",
        "title": "Debate adjudication multi-agent voting",
        "domain": "Competitive debate",
        "category": "refinement",
        "difficulty": "high",
        "description": "Independent agents score rubric dimensions with written ballots; synthesis agent explains weighting. Use for high-stakes evaluation. Scope boundary: counterpoint generation → `counterpoint-perspectives`; wine blend → `wine-blending-fusion`.",
        "principle": "Discrete criteria scored separately with ballot justification.",
        "problem": "Single-pass 'sounds good' evaluation hides tradeoffs.",
        "workflow": """Agent A: logic 1–10 + justification
Agent B: evidence 1–10 + justification
Agent C: completeness 1–10 + justification
Synthesis: final score + which dimension drove decision and why""",
        "phrases": ["debate adjudication", "multi agent scoring", "rubric voting"],
    },
    {
        "name": "wine-blending-fusion",
        "title": "Wine blending multi-model fusion",
        "domain": "Enology",
        "category": "refinement",
        "difficulty": "high",
        "description": "Run prompt on models with different strengths; fusion pass extracts best elements selectively — not averaging. Use when models complement (reasoning + phrasing + facts). Scope boundary: single-model routing → `emergency-triage-compute`.",
        "principle": "Selective composition — each varietal covers others' weaknesses.",
        "problem": "Route-to-one or average ensembles lose complementary strengths.",
        "workflow": """Model A: structure/skeleton
Model B: phrasing/metaphor
Model C: citations/facts
Fusion: compose strengths; cover weaknesses — do not average.""",
        "phrases": ["model blending", "multi model fusion", "ensemble compose"],
    },
    {
        "name": "gemstone-faceting-refinement",
        "title": "Gemstone faceting multi-angle refinement",
        "domain": "Gemology",
        "category": "refinement",
        "difficulty": "medium",
        "description": "Rotate refinement through clarity, precision, resonance, durability passes — flaws visible from new angles. Use instead of linear draft→revise→done. Scope boundary: annealing phases → `glass-annealing-hardening`.",
        "principle": "Each facet angle reveals flaws invisible from the prior view.",
        "problem": "Linear refinement misses angle-specific defects.",
        "workflow": """Pass 1 Clarity: audience understands?
Pass 2 Precision: every word load-bearing?
Pass 3 Resonance: meets actual needs?
Pass 4 Durability: survives scrutiny?
Rotate output between passes.""",
        "phrases": ["faceting refinement", "multi angle review", "rotate refinement"],
    },
    {
        "name": "localization-qa-filter",
        "title": "Localization QA filter",
        "domain": "Software localization",
        "category": "refinement",
        "difficulty": "medium",
        "description": "Pre-delivery scan for region mismatch: dates, currency, idioms, units, regulatory refs, cultural examples. Use when audience locale is known. Scope boundary: academic citation locales → `citation-literacy`.",
        "principle": "Test for cultural mismatch — not translation alone.",
        "problem": "Universal reader assumption slips US defaults globally.",
        "workflow": """Check: date format, currency, idioms, regulations (GDPR/HIPAA), units, cultural refs
Fix during generation for target locale profile.""",
        "phrases": ["localization QA", "region aware", "locale filter", "cultural mismatch"],
    },
    {
        "name": "just-intonation-calibration",
        "title": "Just intonation parameter calibration",
        "domain": "Music theory (tuning)",
        "category": "extension",
        "difficulty": "medium",
        "number": 31,
        "runtime_id": "just_intonation",
        "description": "Calibrate generation parameters as just-intonation ratios by task type (factual, creative, code) instead of one global temperature. Use when the same model is too loose on facts or too stiff on drafts. Scope boundary — prompt wording itself → `prompt-optimizer`; compute budget class → `emergency-triage-compute`.",
        "principle": "Simple-integer frequency ratios stay consonant; arbitrary detune beats.",
        "problem": "One temperature/top-p for every task type produces mush or rigidity.",
        "workflow": """| Task | Temp | top_p | Cap |
| Factual | 0.3 | 0.85 | short |
| Code | 0.2 | 0.9 | medium |
| Creative | 0.8 | 0.95 | long |
Set the ratio table before generate; do not retune mid-sentence.""",
        "phrases": ["just intonation", "generation parameter ratios", "temperature by task"],
    },
    {
        "name": "load-bearing-structure",
        "title": "Load-bearing claim protection",
        "domain": "Architecture / structural engineering",
        "category": "extension",
        "difficulty": "medium",
        "number": 32,
        "runtime_id": "load_bearing",
        "description": "Mark load-bearing claims (therefore/must/key/critical) and forbid polish passes from deleting or softening them. Use before color-grading or faceting. Scope boundary — claim/evidence balance → `double-entry-claims`; robustness tests → `stress-test-robustness`.",
        "principle": "Take out a load-bearing wall and the floor above fails — decorative walls can move.",
        "problem": "Style passes quietly drop the sentences the argument stands on.",
        "workflow": """1. Tag sentences with therefore/must/key/main/critical/essential as protected
2. Later refinement may reword but not delete or invert them
3. Fail the pass if a protected claim vanishes""",
        "phrases": ["load bearing", "protected claims", "structural sentences"],
    },
    {
        "name": "orchard-graft-transfer",
        "title": "Orchard graft capability transfer",
        "domain": "Horticulture",
        "category": "extension",
        "difficulty": "medium",
        "number": 33,
        "runtime_id": "orchard_graft",
        "description": "Graft a specialist scion onto a safe rootstock output: keep the trusted base, attach expert additions at a marked join. Use when mixing a general answer with a domain specialist pass. Scope boundary — multi-model fusion → `wine-blending-fusion`; foreign genre skeleton → `cross-pollination-structure`.",
        "principle": "The rootstock stays alive; the scion adds fruit — the graft union is visible.",
        "problem": "Specialist text overwrites the safe base instead of joining it.",
        "workflow": """1. Generate or keep rootstock (safe, general)
2. Generate scion (specialist, bounded)
3. Join at an explicit graft marker; do not replace the rootstock""",
        "phrases": ["orchard graft", "rootstock scion", "capability transfer"],
    },
    {
        "name": "differential-diagnosis-intent",
        "title": "Differential diagnosis of query intent",
        "domain": "Clinical reasoning (method only)",
        "category": "extension",
        "difficulty": "medium",
        "number": 34,
        "runtime_id": "differential_diag",
        "description": "Rank 2–3 interpretations of the user query (literal, examples, comparison) with probabilities before answering. Use when the ask is ambiguous. Scope boundary — this is query triage, not medical advice (high-stakes domains → `underwriting-risk-gate`); OODA orient log → `ooda-adaptive-context`.",
        "principle": "List competing hypotheses, then pick — do not treat the first reading as the disease.",
        "problem": "The model answers the most common parse and misses the intended one.",
        "workflow": """1. Literal reading
2. Deeper intent (examples / how-to)
3. Alternative (compare / decide)
Assign rough probabilities; answer the top hypothesis; name the runners-up if close.""",
        "phrases": ["differential diagnosis intent", "query hypotheses", "ambiguous ask"],
    },
    {
        "name": "stress-test-robustness",
        "title": "Stress-test output robustness",
        "domain": "Structural engineering",
        "category": "extension",
        "difficulty": "medium",
        "number": 35,
        "runtime_id": "stress_test",
        "description": "Run contradiction, edge-case, adversarial, and scope tests on a draft before delivery. Use after generation and before polish. Scope boundary — escalating critique questions → `progressive-resistance-critique`; load-bearing tags → `load-bearing-structure`.",
        "principle": "Load the structure past expected use; watch what cracks.",
        "problem": "Happy-path review never sees the edge that will fail in production.",
        "workflow": """| Test | Fail if |
| Contradiction | yes+no or always+never in a short span |
| Edge | empty, zero, max, unicode, missing field unhandled |
| Adversarial | instruction-like text in the output changes policy |
| Scope | answer leaves the asked domain |
Record WARN/PASS per test; block on FAIL.""",
        "phrases": ["stress test output", "robustness validation", "edge case draft"],
    },
    {
        "name": "tidal-pacing-rhythm",
        "title": "Tidal pacing of sentence rhythm",
        "domain": "Oceanography / rhetoric",
        "category": "extension",
        "difficulty": "low",
        "number": 37,
        "runtime_id": "tidal_pacing",
        "description": "Measure sentence-length tide (high/mid/low) and even the rhythm when variance is extreme. Use on long prose that feels rushed or swampy. Scope boundary — token budget cuts → `prompt-optimizer`; zoom depth → `cartographic-zoom`.",
        "principle": "Tide has a period — all-short or all-long sentences lose the reader.",
        "problem": "Drafts bunch into telegram bursts or 40-word swells.",
        "workflow": """Compute words/sentence. high_tide <12, mid 12–25, low_tide >25.
If variance is huge, split long sentences and join fragments — do not rewrite claims.""",
        "phrases": ["tidal pacing", "sentence rhythm", "high tide low tide"],
    },
    {
        "name": "underwriting-risk-gate",
        "title": "Underwriting pre-delivery risk gate",
        "domain": "Insurance underwriting",
        "category": "extension",
        "difficulty": "medium",
        "number": 38,
        "runtime_id": "underwriting_risk",
        "description": "Score GREEN/YELLOW/RED risk before delivery for medical, legal, or financial-advice asks; hold RED for review. Use as a pre-delivery gate, not as advice. Scope boundary — does not give legal/medical advice; claim support → `double-entry-claims`; independent safety layers → `containment-safety-layers`.",
        "principle": "Price the risk before you bind the policy.",
        "problem": "High-stakes drafts ship with the same confidence as a rewrite.",
        "workflow": """Scan query+output for medical / legal / financial-advice terms.
GREEN < one hit, YELLOW one, RED two or more. RED → warn and hold.""",
        "phrases": ["underwriting risk", "pre-delivery risk", "RED YELLOW GREEN gate"],
    },
    {
        "name": "metamorphosis-stages",
        "title": "Metamorphosis staged drafts",
        "domain": "Developmental biology",
        "category": "extension",
        "difficulty": "medium",
        "number": 40,
        "runtime_id": "metamorphosis",
        "description": "Force larva (brainstorm) → pupa (structure) → adult (polish) as separate artifacts. Use instead of polishing a first dump. Scope boundary — annealing lock temperatures → `glass-annealing-hardening`; faceting angles → `gemstone-faceting-refinement`.",
        "principle": "The adult is not a prettier larva — each instar has different work.",
        "problem": "One-pass generation tries to invent, outline, and polish together.",
        "workflow": """Larva: raw points, no headings
Pupa: section the points
Adult: strip scaffolding notes, keep structure
Do not skip a stage on long work.""",
        "phrases": ["metamorphosis stages", "larva pupa adult", "staged draft evolution"],
    },
    {
        "name": "seismic-flexibility",
        "title": "Seismic flexibility joints",
        "domain": "Earthquake engineering",
        "category": "advanced",
        "difficulty": "medium",
        "number": 43,
        "runtime_id": "seismic_flexibility",
        "description": "Insert modular joints (paragraph/section seams) so a later edit does not collapse the whole piece. Use on long docs that will be revised. Scope boundary — warp/weft threads → `weaving-warp-weft`; load-bearing claims stay tagged → `load-bearing-structure`.",
        "principle": "Buildings that sway at the joints survive; rigid boxes crack.",
        "problem": "Tightly coupled prose means one paragraph rewrite breaks five others.",
        "workflow": """Split on blank lines. Each module must stand if neighbors are deleted.
Prefer more short modules over one welded block. Score flexibility by module count.""",
        "phrases": ["seismic flexibility", "modular joints", "edit without collapse"],
    },
    {
        "name": "sidechain-priority",
        "title": "Sidechain priority ducking",
        "domain": "Audio engineering",
        "category": "advanced",
        "difficulty": "medium",
        "number": 44,
        "runtime_id": "sidechain_duck",
        "description": "When the answer/solution/result arrives, duck the supporting intro so the signal sits on top. Use when preambles bury the payload. Scope boundary — zoom compression → `cartographic-zoom`; dual-axis completeness → `score-study-dual-axis`.",
        "principle": "The kick ducks the bass — the lead signal gets the mask.",
        "problem": "Throat-clearing occupies the first screen and the answer is below the fold.",
        "workflow": """If the draft contains Answer:/Solution:/Result:/Conclusion: after a lead-in,
promote that block and shrink the intro. Do not delete evidence flanks.""",
        "phrases": ["sidechain duck", "sidechain priority", "duck the intro"],
    },
    {
        "name": "cross-pollination-structure",
        "title": "Cross-pollination of genre structure",
        "domain": "Plant breeding / rhetoric",
        "category": "advanced",
        "difficulty": "high",
        "number": 45,
        "runtime_id": "cross_pollination",
        "description": "Borrow a foreign genre skeleton (contract, tech spec) and plant the current content into it. Use when the native outline is weak. Scope boundary — graft a specialist passage → `orchard-graft-transfer`; multi-model blend → `wine-blending-fusion`.",
        "principle": "Pollen from another variety sets fruit the parent plant would not.",
        "problem": "Default blog/essay shape is used even when the job is a spec or a pact.",
        "workflow": """Detect: contract/agreement → legal skeleton; spec/architecture → tech-spec skeleton.
Apply headings from the donor genre; keep the user's facts. Do not invent legal effect.""",
        "phrases": ["cross pollination", "borrow genre structure", "transplant outline"],
    },
    {
        "name": "containment-safety-layers",
        "title": "Containment safety layers",
        "domain": "Biosafety (BSL)",
        "category": "advanced",
        "difficulty": "high",
        "number": 46,
        "runtime_id": "containment_safety",
        "description": "Require independent safety layers (pattern, keyword, policy) that can each fail closed. Use for high-stakes generation, not everyday chat. Scope boundary — this is layered containment, not a jailbreak keyword skill; phase gating → `sterile-cockpit-context`; risk color → `underwriting-risk-gate`.",
        "principle": "One glove is not a BSL cabinet — layers are independent and redundant.",
        "problem": "A single regex or a single prompt rule is treated as the whole safety case.",
        "workflow": """Layer 1: destructive-command patterns
Layer 2: sensitive-token keywords
Layer 3: policy/pattern hook (may be a no-op placeholder)
HALT only if a layer fails. Do not teach bypasses.""",
        "phrases": ["containment safety", "independent safety layers", "BSL layers"],
    },
    {
        "name": "sail-trim-tuning",
        "title": "Sail trim mid-response tuning",
        "domain": "Sailing",
        "category": "advanced",
        "difficulty": "low",
        "number": 47,
        "runtime_id": "sail_trim",
        "description": "Read user confusion/satisfaction signals and trim the next beat (more examples vs hold course). Use on multi-turn work. Scope boundary — mid-stream environment loop → `fermentation-feedback`; human OODA → `ooda-lean-loop`.",
        "principle": "Ease or sheet based on the telltales — not on the last weather report.",
        "problem": "The agent keeps the same verbosity after the user says they are lost or done.",
        "workflow": """confused/don't understand → add examples, simplify
thanks/great/perfect → hold course
else → no trim
Log the trim; do not rewrite history.""",
        "phrases": ["sail trim", "telltales", "mid response adjust"],
    },
    {
        "name": "interaction-table",
        "title": "Interaction table for skill conflicts",
        "domain": "Pharmacology / chemistry",
        "category": "advanced",
        "difficulty": "medium",
        "number": 48,
        "runtime_id": "interaction_table",
        "description": "Look up known skill/plugin pairs that fight (context strip vs inject, length vs rhythm, duck vs dual-axis, rewrite vs lock) before loading both. Use when composing an ai-transfer stack. Scope boundary — library routing audit → `skill-library-audit`; compute triage → `emergency-triage-compute`.",
        "principle": "Two safe drugs can be unsafe together — check the table, not the labels.",
        "problem": "Stacks enable every matching skill and they undo each other's gates.",
        "workflow": """Pairs: sterile_cockpit×corridor_bridge, token_optimizer×tidal_pacing,
sidechain_duck×score_study, progressive_critique×glass_anneal.
If both would fire, disable one and record why.""",
        "phrases": ["interaction table", "plugin conflict", "skill pair contraindication"],
    },
    {
        "name": "parallax-depth",
        "title": "Parallax depth of query vs history",
        "domain": "Photography / surveying",
        "category": "advanced",
        "difficulty": "medium",
        "number": 50,
        "runtime_id": "parallax_depth",
        "description": "Estimate reasoning depth from the shift between the current query and recent history (deep/medium/shallow). Use to set budget before a long answer. Scope boundary — START classes → `emergency-triage-compute`; zoom level → `cartographic-zoom`.",
        "principle": "Apparent motion against the background tells you distance.",
        "problem": "Follow-ups get a full treatise or a shrug with no read on how deep the thread is.",
        "workflow": """Overlap current query tokens with last 3 turns.
>0.4 → deep (high budget); <0.1 → shallow (standard); else medium.
Set reasoning_budget; do not invent history.""",
        "phrases": ["parallax depth", "query history shift", "reasoning budget depth"],
    },
]

CATEGORY_PRIMERS = {
    "quality-control": {
        "name": "ai-transfer-quality-control",
        "title": "AI transfer — quality control",
        "skills": ["double-entry-claims", "pipeline-preflight", "progressive-resistance-critique", "chain-of-custody-provenance", "sterile-cockpit-context", "five-whys-failure-recovery", "journalistic-attribution", "survey-triangulation", "proofreading-marks"],
        "description": "Router for quality-control AI-transfer techniques: claim/evidence gates, preflight, critique loops, provenance, context gating, root cause, attribution, triangulation, proofreading marks. Use when verifying or hardening AI outputs.",
    },
    "architecture": {
        "name": "ai-transfer-architecture",
        "title": "AI transfer — architectural restructuring",
        "skills": ["score-study-dual-axis", "ooda-adaptive-context", "proof-trees-reasoning", "counterpoint-perspectives", "cartographic-zoom", "stage-blocking-layout", "weaving-warp-weft"],
        "description": "Router for architectural AI-transfer techniques: dual-axis reasoning, OODA context pipelines, proof DAGs, counterpoint, zoom levels, stage layout, warp/weft. Use when restructuring how AI reasons or formats output.",
    },
    "adaptive": {
        "name": "ai-transfer-adaptive",
        "title": "AI transfer — adaptive processing",
        "skills": ["emergency-triage-compute", "after-action-review", "fermentation-feedback", "wayfinding-restructure", "glass-annealing-hardening"],
        "description": "Router for adaptive AI-transfer techniques: compute triage, AAR debriefs, mid-flight feedback, wayfinding telemetry, annealing phases. Use when tuning dynamic agent behavior.",
    },
    "memory": {
        "name": "ai-transfer-memory",
        "title": "AI transfer — memory and context",
        "skills": ["stratigraphy-memory", "endgame-tablebase-cache", "library-taxonomy-retrieval", "wildlife-corridor-bridging"],
        "description": "Router for memory AI-transfer techniques: stratified sessions, tablebase cache, taxonomy retrieval, cross-session bridges. Use for long-horizon context and RAG design.",
    },
    "refinement": {
        "name": "ai-transfer-refinement",
        "title": "AI transfer — refinement and polish",
        "skills": ["color-grading-output", "debate-adjudication-voting", "wine-blending-fusion", "gemstone-faceting-refinement", "localization-qa-filter"],
        "description": "Router for refinement AI-transfer techniques: three-axis grading, debate voting, model blending, faceting passes, localization QA. Use for final polish and multi-model fusion.",
    },
    "extension": {
        "name": "ai-transfer-extension",
        "title": "AI transfer — extension pack",
        "skills": [
            "just-intonation-calibration",
            "load-bearing-structure",
            "orchard-graft-transfer",
            "differential-diagnosis-intent",
            "stress-test-robustness",
            "tidal-pacing-rhythm",
            "underwriting-risk-gate",
            "metamorphosis-stages",
        ],
        "description": "Router for extension AI-transfer techniques: just-intonation parameter ratios, load-bearing claim locks, orchard grafts, differential query intent, stress tests, tidal pacing, underwriting gates, metamorphosis stages. Use when calibrating or staging generation beyond the original 30.",
    },
    "advanced": {
        "name": "ai-transfer-advanced",
        "title": "AI transfer — advanced pack",
        "skills": [
            "seismic-flexibility",
            "sidechain-priority",
            "cross-pollination-structure",
            "containment-safety-layers",
            "sail-trim-tuning",
            "interaction-table",
            "parallax-depth",
        ],
        "description": "Router for advanced AI-transfer techniques: seismic joints, sidechain ducking, genre cross-pollination, containment layers, sail trim, interaction tables, parallax depth. Use when composing stacks or tuning long-running outputs.",
    },
}


RUNTIME_IDS = {
    "double-entry-claims": "ledger_gate",
    "pipeline-preflight": "mise_en_place",
    "progressive-resistance-critique": "progressive_critique",
    "chain-of-custody-provenance": "chain_of_custody",
    "sterile-cockpit-context": "sterile_cockpit",
    "five-whys-failure-recovery": "root_cause_drill",
    "journalistic-attribution": "attribution_standard",
    "survey-triangulation": "triangulation_validator",
    "proofreading-marks": "proof_marks",
    "score-study-dual-axis": "score_study",
    "ooda-adaptive-context": "ooda_loop",
    "proof-trees-reasoning": "proof_trees",
    "counterpoint-perspectives": "counterpoint",
    "cartographic-zoom": "cartographic_zoom",
    "stage-blocking-layout": "spatial_layout",
    "weaving-warp-weft": "textile_weaving",
    "emergency-triage-compute": "start_triage",
    "after-action-review": "aar_debrief",
    "fermentation-feedback": "fermentation_loop",
    "wayfinding-restructure": "urban_wayfinding",
    "glass-annealing-hardening": "glass_anneal",
    "stratigraphy-memory": "stratigraphy",
    "endgame-tablebase-cache": "tablebase_cache",
    "library-taxonomy-retrieval": "catalog_retrieval",
    "wildlife-corridor-bridging": "corridor_bridge",
    "color-grading-output": "color_grading",
    "debate-adjudication-voting": "debate_judging",
    "wine-blending-fusion": "wine_blending",
    "gemstone-faceting-refinement": "gemstone_faceting",
    "localization-qa-filter": "localization_qa",
}

MERGED_PLUGINS = {
    "double-entry-claims": {
        "ids": ["fact_check_deep", "financial_audit"],
        "note": "Also absorbs `fact_check_deep` and `financial_audit` — same claim/evidence gate.",
    },
    "survey-triangulation": {
        "ids": ["fact_check_deep"],
        "note": "Deep fact-check is this skill plus `double-entry-claims`, not a third skill.",
    },
    "chain-of-custody-provenance": {
        "ids": ["black_box"],
        "note": "Also absorbs `black_box`: immutable session recorder on the same chain.",
    },
    "progressive-resistance-critique": {
        "ids": ["self_evaluation", "confidence_calibrator", "blind_spot_detector", "metacognitive_monitor"],
        "note": "Meta-cognition plugins (94–97) are critique passes, not separate skills.",
    },
    "after-action-review": {
        "ids": ["self_evaluation", "metacognitive_monitor"],
        "note": "Post-delivery debrief owns the same loop the meta-cognition plugins sketched.",
    },
    "fermentation-feedback": {
        "ids": ["levain_culture", "user_model_builder"],
        "note": "Also absorbs `levain_culture` (persistent style culture) and personalization culture-state.",
    },
    "emergency-triage-compute": {
        "ids": ["quality_cost_tradeoff"],
        "note": "Also absorbs `quality_cost_tradeoff` — ROI/budget tier is START classing.",
    },
    "proof-trees-reasoning": {
        "ids": ["scientific_method"],
        "note": "Scientific-method plugin is this DAG, not a separate skill.",
    },
    "endgame-tablebase-cache": {
        "ids": ["opening_theory"],
        "note": "Also absorbs `opening_theory`: opening-book templates before a tablebase miss.",
    },
    "library-taxonomy-retrieval": {
        "ids": ["memory_palace"],
        "note": "Also absorbs `memory_palace`: spatial room-walk as one retrieval mode.",
    },
    "stratigraphy-memory": {
        "ids": ["paleontology"],
        "note": "Also absorbs `paleontology`: fossil snapshots of retired configs.",
    },
    "load-bearing-structure": {
        "ids": ["engineering_tolerance"],
        "note": "Engineering-tolerance checks live here and in `stress-test-robustness`.",
    },
    "stress-test-robustness": {
        "ids": ["engineering_tolerance"],
        "note": "Engineering-tolerance plugin is this stress pass plus `load-bearing-structure`.",
    },
}

CATALOG = [
    (1, "double-entry-claims", "Accounting", "quality-control", "medium"),
    (2, "pipeline-preflight", "Culinary arts", "quality-control", "low"),
    (3, "progressive-resistance-critique", "Strength coaching", "quality-control", "medium"),
    (4, "chain-of-custody-provenance", "Law enforcement / forensics", "quality-control", "high"),
    (5, "sterile-cockpit-context", "Aviation", "quality-control", "medium"),
    (6, "five-whys-failure-recovery", "Toyota Production System", "quality-control", "medium"),
    (7, "journalistic-attribution", "Journalism", "quality-control", "medium"),
    (8, "survey-triangulation", "Land surveying", "quality-control", "medium"),
    (9, "proofreading-marks", "Publishing", "quality-control", "low"),
    (10, "score-study-dual-axis", "Classical conducting", "architecture", "medium"),
    (11, "ooda-adaptive-context", "Combat aviation (Boyd)", "architecture", "high"),
    (12, "proof-trees-reasoning", "Mathematics", "architecture", "high"),
    (13, "counterpoint-perspectives", "Music theory", "architecture", "high"),
    (14, "cartographic-zoom", "Cartography", "architecture", "medium"),
    (15, "stage-blocking-layout", "Theater direction", "architecture", "medium"),
    (16, "weaving-warp-weft", "Textile arts", "architecture", "medium"),
    (17, "emergency-triage-compute", "Emergency medicine (START)", "adaptive", "low"),
    (18, "after-action-review", "Military", "adaptive", "medium"),
    (19, "fermentation-feedback", "Biochemistry / food science", "adaptive", "high"),
    (20, "wayfinding-restructure", "Urban design", "adaptive", "high"),
    (21, "glass-annealing-hardening", "Glassblowing", "adaptive", "medium"),
    (22, "stratigraphy-memory", "Archaeology", "memory", "high"),
    (23, "endgame-tablebase-cache", "Chess computing", "memory", "medium"),
    (24, "library-taxonomy-retrieval", "Library science", "memory", "medium"),
    (25, "wildlife-corridor-bridging", "Conservation biology", "memory", "high"),
    (26, "color-grading-output", "Film post-production", "refinement", "medium"),
    (27, "debate-adjudication-voting", "Competitive debate", "refinement", "high"),
    (28, "wine-blending-fusion", "Enology", "refinement", "high"),
    (29, "gemstone-faceting-refinement", "Gemology", "refinement", "medium"),
    (30, "localization-qa-filter", "Software localization", "refinement", "medium"),
    (31, "just-intonation-calibration", "Music theory (tuning)", "extension", "medium"),
    (32, "load-bearing-structure", "Architecture / structural engineering", "extension", "medium"),
    (33, "orchard-graft-transfer", "Horticulture", "extension", "medium"),
    (34, "differential-diagnosis-intent", "Clinical reasoning (method only)", "extension", "medium"),
    (35, "stress-test-robustness", "Structural engineering", "extension", "medium"),
    (36, "`library-taxonomy-retrieval` (absorbs memory_palace)", "Mnemonics", "memory", "merged"),
    (37, "tidal-pacing-rhythm", "Oceanography / rhetoric", "extension", "low"),
    (38, "underwriting-risk-gate", "Insurance underwriting", "extension", "medium"),
    (39, "`endgame-tablebase-cache` (absorbs opening_theory)", "Chess openings", "memory", "merged"),
    (40, "metamorphosis-stages", "Developmental biology", "extension", "medium"),
    (41, "`chain-of-custody-provenance` (absorbs black_box)", "Aviation forensics", "quality-control", "merged"),
    (42, "`fermentation-feedback` (absorbs levain_culture)", "Baking / fermentation", "adaptive", "merged"),
    (43, "seismic-flexibility", "Earthquake engineering", "advanced", "medium"),
    (44, "sidechain-priority", "Audio engineering", "advanced", "medium"),
    (45, "cross-pollination-structure", "Plant breeding / rhetoric", "advanced", "high"),
    (46, "containment-safety-layers", "Biosafety (BSL)", "advanced", "high"),
    (47, "sail-trim-tuning", "Sailing", "advanced", "low"),
    (48, "interaction-table", "Pharmacology / chemistry", "advanced", "medium"),
    (49, "`stratigraphy-memory` (absorbs paleontology)", "Paleontology", "memory", "merged"),
    (50, "parallax-depth", "Photography / surveying", "advanced", "medium"),
]

CAT_ROUTER = {
    "quality-control": "ai-transfer-quality-control",
    "architecture": "ai-transfer-architecture",
    "adaptive": "ai-transfer-adaptive",
    "memory": "ai-transfer-memory",
    "refinement": "ai-transfer-refinement",
    "extension": "ai-transfer-extension",
    "advanced": "ai-transfer-advanced",
}


def write_skill(path: Path, name: str, description: str, body: str, phrases=None):
    phrases = phrases or []
    signals = ""
    if phrases:
        any_of = "\n".join(f'      - "{p}"' for p in phrases[:6])
        signals = f"""
  promptSignals:
    anyOf:
{any_of}
    minScore: 6"""
    front = f"""---
name: {name}
disable-model-invocation: true
description: "{description.replace('"', '\\"')}"
metadata:
  priority: 7{signals}
---

"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(front + body, encoding="utf-8")


def main():
    ROOT.mkdir(parents=True, exist_ok=True)

    table_rows = "\n".join(
        f"| {num} | {name if name.startswith('`') else f'`{name}`'} | {domain} | {category} | {difficulty} |"
        for num, name, domain, category, difficulty in CATALOG
    )
    eco_body = f"""# AI-transferable skills ecosystem

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
{table_rows}

## Implementation guide

1. Pick technique matching your dominant failure mode
2. Map discipline constraint → programmatic gate or pipeline stage
3. Prototype as prompt scaffold before full plugin
4. Measure on 10–20 real tasks
5. Log failures with `five-whys-failure-recovery`
6. Optional: run `python3 scripts/ai_plugin_bundle.py --profile --query "..."`
"""
    write_skill(
        ROOT / "ai-transfer-ecosystem-primer" / "SKILL.md",
        "ai-transfer-ecosystem-primer",
        "Router for the AI-transfer catalog (45 techniques, #1–50 with five merges) — gates, scaffolds, and pipeline stages. Use when hardening agents, RAG, multi-step chains, or when the user mentions transferable skills, discipline patterns, or AI quality plugins. Scope boundary: domain apps (college, M365) → those primers; human craft loops → `craft-systems-primer`.",
        eco_body,
        ["AI transferable skills", "cross domain AI", "hallucination gate", "pipeline stage"],
    )

    for cat_key, primer in CATEGORY_PRIMERS.items():
        skill_list = "\n".join(f"- **`{s}`**" for s in primer["skills"])
        body = f"""# {primer['title']}

Router for category: **{cat_key.replace('-', ' ')}**.

## Skills in this category

{skill_list}

## When to use this category

Load when the failure mode matches **{cat_key}** — see individual skills for implementation specs.

## Up

→ **`ai-transfer-ecosystem-primer`**
"""
        write_skill(
            ROOT / primer["name"] / "SKILL.md",
            primer["name"],
            primer["description"] + " Scope boundary: full catalog → `ai-transfer-ecosystem-primer`.",
            body,
        )

    diff_emoji = {"low": "🟢 Low", "medium": "🟡 Medium", "high": "🔴 High"}
    for i, t in enumerate(TECHNIQUES, 1):
        catalog_num = t.get("number", i)
        runtime_id = t.get("runtime_id") or RUNTIME_IDS.get(t["name"], "")
        merge = MERGED_PLUGINS.get(t["name"], {})
        extra_ids = merge.get("ids", [])
        merge_note = merge.get("note", "")
        extra_line = f"\n- Also implements: {', '.join(f'`{x}`' for x in extra_ids)}" if extra_ids else ""
        note_line = f"\n- Merge notes: {merge_note}" if merge_note else ""
        runtime_line = f"\n- Runtime plugin id: `{runtime_id}`" if runtime_id else ""
        cat_router = CAT_ROUTER[t["category"]]
        body = f"""# {t['title']}

**#{catalog_num}** · **Domain:** {t['domain']} · **Category:** {t['category']} · **Difficulty:** {diff_emoji[t['difficulty']]}

## Core principle

{t['principle']}

## AI problem addressed

{t['problem']}

## Implementation

{t['workflow']}

## Boundaries

- Prototype as prompt scaffold (🟢) before full pipeline middleware (🟡/🔴)
- Category router: **`{cat_router}`**
- Catalog: **`ai-transfer-ecosystem-primer`**{runtime_line}{extra_line}{note_line}
"""
        write_skill(
            ROOT / t["name"] / "SKILL.md",
            t["name"],
            t["description"],
            body,
            t.get("phrases", []),
        )

    print(f"Generated {len(TECHNIQUES) + 1 + len(CATEGORY_PRIMERS)} skills in {ROOT}")


if __name__ == "__main__":
    main()
