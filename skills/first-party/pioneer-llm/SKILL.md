---
name: pioneer-llm
description: "Interactive scoping to design a bespoke Pioneer LLM: activate this skill, answer structured questions about purpose and constraints, and receive a complete model specification (system prompt, parameters, guardrails, eval hooks). Use when the user says activate pioneer LLM, create a bespoke/custom LLM, pioneer model, scoped LLM for a purpose, or wants an interview before defining their AI. Scope boundary: this creates the LLM identity and spec — not application scaffolding (`build-agents`/`eve`), not tuning an existing prompt in place (`prompt-optimizer`), not picking a public Hub model (`huggingface-best`)."
metadata:
  priority: 8
  promptSignals:
    phrases:
      - "activate pioneer"
      - "pioneer llm"
      - "bespoke llm"
      - "custom llm for"
      - "scoping questions"
      - "design an llm for"
      - "create a model for this purpose"
    allOf:
      - [pioneer, llm]
      - [bespoke, llm]
      - [custom, llm, purpose]
    anyOf:
      - "pioneer llm"
      - "pioneer model"
      - "bespoke llm"
      - "activate pioneer"
---

# Pioneer LLM — bespoke model via scoping

**What this is:** A structured interview that turns your purpose into a **Pioneer LLM Specification** — a ready-to-deploy bespoke model definition (system prompt, behavior contract, parameters, and eval plan).

**What this is not:** Installing weights, fine-tuning jobs, or agent repo scaffolding. The deliverable is the **spec**; implementation routes to other skills if needed.

---

## Activation

When the user activates Pioneer LLM (e.g. *"activate pioneer LLM"*), **immediately acknowledge** and begin **Phase 1 — Scoping**. Do not jump to writing the spec until scoping is complete unless the user explicitly skips ("use defaults for the rest").

---

## Phase 1 — Scoping interview

Ask questions in **two batched rounds** (not one question per turn). After each round, summarize what you heard and confirm before continuing.

### Round A — Purpose & success (required)

1. **Name** — What should this Pioneer LLM be called? (working title is fine)
2. **Primary purpose** — One sentence: what job does it exist to do?
3. **User / audience** — Who talks to it? Expertise level? Stress context?
4. **Success** — How do you know it worked? Give 2–3 concrete success examples.
5. **Non-goals** — What must it refuse to do or never pretend to know?
6. **Duration** — One-shot answers, multi-turn coach, or long-running copilot?

### Round B — Behavior, constraints, deployment (required)

7. **Tone & persona** — Formal, blunt, warm, socratic, etc. Any voice to avoid?
8. **Output shape** — Prose, bullets, code, JSON schema, mixed?
9. **Tools & data** — Will it have tools (search, code, APIs, files)? What can it access?
10. **Safety & compliance** — PII, medical/legal/financial boundaries, age sensitivity?
11. **Model constraints** — Provider preference (OpenAI, Anthropic, Google, local, Vercel AI Gateway)? Latency vs quality? Budget cap?
12. **Failure mode** — When uncertain, should it ask, decline, or give best-effort with caveats?

### Round C — Optional depth (ask only if relevant)

- Domain vocabulary or sources it must cite
- Anti-patterns from bad assistants you've used
- Existing prompt/system text to inherit or replace
- Competitors or references ("like X but not Y")
- Evaluation data you already have

**Scoping rules:**
- Batch 4–6 questions per message in Round A, then Round B.
- If the user gives partial answers, **infer nothing silently** — mark gaps and ask once more in a single batch.
- When scoping is complete, print a **Scoping Summary** table and ask: *"Confirm or revise before I forge the Pioneer spec?"*

---

## Phase 2 — Forge the Pioneer LLM Specification

After confirmed scoping, produce **`Pioneer LLM Specification`** using this template. Write it as a markdown artifact the user can save (e.g. `pioneer-<slug>.md`).

```markdown
# Pioneer LLM: [Name]

## Charter
- **Purpose:** …
- **Audience:** …
- **Success criteria:** …
- **Non-goals:** …

## Identity (one paragraph)
[Who this LLM is — voice, stance, relationship to the user]

## System prompt
\`\`\`
[Complete system prompt — layered: role, rules, output format, uncertainty handling, refusals]
\`\`\`

## Developer / policy layer (optional)
[Hard constraints not shown to end users — tool policy, PII, escalation]

## Parameters
| Parameter | Value | Rationale |
|---|---|---|
| Model family | … | … |
| Temperature | … | … |
| Max tokens | … | … |
| Top-p / other | … | … |

## Tooling profile
| Tool | Allowed | When to use |
|---|---|---|
| … | yes/no | … |

## Guardrails
- Must always: …
- Must never: …
- When unsure: …

## Eval plan (minimal)
| Scenario | Input sketch | Pass condition |
|---|---|---|
| Happy path | … | … |
| Refusal | … | … |
| Edge | … | … |

## Activation snippet
[Copy-paste block: API/system message + recommended model id for their stack]

## Implementation routing
| Next step | Skill / action |
|---|---|
| Optimize prompt wording with evals | `prompt-optimizer` |
| Vercel AI SDK agent | `ai-sdk` |
| Model routing / gateway | `ai-gateway` |
| Pick public HF model | `huggingface-best` |
| Full agent app | `build-agents` / `eve` |
```

---

## Phase 3 — Offer iteration

After delivering the spec:

1. Ask which section to refine (identity, refusals, tone, parameters).
2. Run **one** targeted revision pass — do not re-run full scoping unless purpose changed.
3. Optionally offer 3 **starter user messages** that showcase the Pioneer LLM.

---

## Quality bar for the system prompt

The forged system prompt must:

- Open with **role + purpose** tied to scoping answers (not generic "helpful assistant")
- Include **explicit non-goals** from scoping
- Define **uncertainty behavior** (ask / decline / caveat — per user choice)
- Specify **output format** when the user cares about structure
- Be **testable** — each eval row maps to a sentence in the prompt
- Stay **minimal** — no boilerplate bloat; every line from scoping

---

## Deconfliction

| User need | Route to |
|---|---|
| "Improve this existing system prompt" | `prompt-optimizer` |
| "Build the Next.js chat app" | `ai-sdk`, `nextjs` |
| "Fine-tune Llama on my dataset" | `huggingface-llm-trainer` |
| "Which public model for coding?" | `huggingface-best` or `ai-gateway` |
| **"Design a bespoke LLM for my purpose"** | **this skill** |

---

## Example activation

**User:** *Activate pioneer LLM — I need a model for reviewing surgical consent forms with patients.*

**Agent:** Acknowledges Pioneer mode → Round A questions (purpose, audience, success, non-goals…) → Round B (tone, medical boundaries, output shape…) → Scoping Summary → confirmed spec with conservative medical disclaimers, plain-language output, mandatory "not medical advice" guardrail, eval rows for jargon detection and refusal of diagnosis.

---

## Quick reference

```
Activate → Batch scoping → Confirm summary → Forge spec → Iterate once
The interview IS the product definition; the system prompt IS the bespoke model.
```
