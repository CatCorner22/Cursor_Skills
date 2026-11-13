# Free Plugins, Skills, MCP Servers and Hugging Face Models for Frontend Design

Checked 2026-11-11. I did **not** install or run these; descriptions come from their READMEs and third-party comparisons (grade C/D, see `01-research-report.md`). Star/install counts quoted by aggregators are volatile and unverified, so I omit them. Verify license and install commands in each repo before use.

---

## 1. Agent skills and plugins (free, open source)

| Tool | License (per aggregator) | What it does | Best for | Install (as published) |
|---|---|---|---|---|
| **Anthropic `frontend-design`** | Apache-2.0 | One SKILL.md that bans generic defaults, forces a committed aesthetic, covers type/color/motion/backgrounds. The seed of the ecosystem. | Starting a new page or component in Claude Code | `/plugin install frontend-design@claude-plugins-official` or `npx skills add anthropics/skills --skill frontend-design` |
| **Impeccable** (Paul Bakaus, `pbakaus/impeccable`) | Apache-2.0 | Grew out of frontend-design. Reference docs (type, color/OKLCH, spatial, motion, interaction, responsive, UX writing), commands like `audit`, `critique`, `polish`, `typeset`, `layout`, `bolder`, `quieter`, `clarify`, plus a rule-based "slop" detector; `/impeccable init` writes a `PRODUCT.md` of audience/purpose/voice. | Critiquing and polishing an existing UI | `npx skills add pbakaus/impeccable --skill impeccable` or `npx impeccable install` |
| **UI UX Pro Max** (`nextlevelbuilder/ui-ux-pro-max-skill`) | MIT | Searchable database: ~80 styles, ~190 palettes, ~70 font pairings, ~120 UX guidelines, reasoning rules by product type; can save a design system. Needs Python 3. | Choosing a style/palette/fonts and saving a system | `/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill` then `/plugin install ui-ux-pro-max@ui-ux-pro-max-skill`, or `npx skills add nextlevelbuilder/ui-ux-pro-max-skill --skill ui-ux-pro-max` |
| **Vercel `web-design-guidelines`** | MIT (README only) | Audits UI code against 100+ accessibility and UX rules | Last-step review before launch | `npx skills add vercel-labs/agent-skills --skill web-design-guidelines` (confirm repo path first) |
| **shadcn skill** (`shadcn-ui/ui`) | MIT | Teaches the agent to use the shadcn CLI and your `components.json` correctly | Projects already on shadcn/ui | `npx skills add shadcn-ui/ui --skill shadcn` |
| **Taste Skill** (Leon Lin) | MIT | Landing pages/portfolios/redesigns with style controls; checks in a real browser at four widths | New marketing sites | See its repo |
| **Emil Kowalski skills** | MIT | Animation and small-interaction craft | Motion polish | `npx skills add` from his repo |
| **unslop** | CC BY 4.0 | Pass-by-pass cleanup of AI-looking UI (spacing, color, icons, copy, type) | De-slopping existing output | See its repo |
| **Awwwards-mcp** (`awwwards-mcp`) | n/a | MCP server: search Awwwards sites, build a cited design brief from chosen references, score your build against a reference (structure/motion only, not visual polish) | Reference-driven briefs | `claude mcp add awwwards -- npx -y awwwards-mcp`; Playwright needed for some tools |
| **Google Stitch / Figma skills** | Apache-2.0 / Figma terms | Design in Stitch or Figma, then build; need the respective MCP | Design-tool-first workflows | See vendor docs |
| **Playwright / Lighthouse / axe** | MIT / Apache-2.0 | Not design plugins, but they give the agent *eyes*: screenshots at breakpoints, a11y and performance scores | Verification loop in every prompt | `npm i -D @playwright/test @axe-core/playwright`; Lighthouse via Chrome DevTools or `npx lighthouse` |

**Recommended stack (judgment):**
1. `frontend-design` or Impeccable for generation-time steering.
2. UI UX Pro Max for choosing/saving a system if you have no brand yet.
3. Your own `DESIGN-BRIEF.md` + `tokens.css` (from this kit) as the thing that actually prevents drift. Practitioners say a custom skill encoding your brand outperforms any generic skill on your work.
4. Playwright screenshots + axe in the loop.
5. Vercel `web-design-guidelines` as the final audit.

**Cautions:**
- Skills change the look but do not remove the "AI look." Multiple reviews say post-skill output has its own recognizable signature. Pair any skill with your own references and tokens.
- Running third-party skills means executing someone else's instructions and scripts in your agent. Read the SKILL.md and any scripts first; prefer pinned versions.
- Some skills assume Claude Code paths (`${CLAUDE_PLUGIN_ROOT}`); other agents (Cursor, Codex) need the install via the `skills` CLI or manual path edits.

### Reusable "anti-generic" prompt from Anthropic (primary source)

Anthropic published a ~400-token prompt in *Improving frontend design through Skills*. Key ideas to reuse: tell the model it tends to converge to on-distribution output; specify typography, color/theme with CSS variables, motion (one orchestrated page load), backgrounds with depth; list defaults to avoid; and end with a reminder not to converge on a *new* default. Full text is on the article page.

---

## 2. Best models for frontend design right now

### Hosted frontier (not free, listed for calibration; WebDev Arena, 2026-11-10)
| Rank | Model | Elo | Votes |
|---|---|---|---|
| 1 | Claude Fable 5.2 (xHigh) | 1836 | 994 |
| 2 | Claude Opus 5.5 (Max) | 1814 | 4,187 |
| 3 | Claude Sonnet 5.5 (xHigh) | 1773 | 5,818 |
| 4 | Gemini 4 Carbon (High) (preliminary) | 1768 | 2,120 |
| 5 | GPT-6 Astra (Max) | 1764 | 8,425 |

Observation: Sonnet 5.5 (xHigh) sits third at a fraction of the top price ($2/$10 per M tokens as listed), so it is the value pick (judgment). A practitioner comparison found Claude's motion/story direction more coherent than open models on a landing-page task, but that is one informal test.

### Open-weight models on Hugging Face (best for general design/web work)
Ranked by WebDev Arena's open-license filter, with Design Arena (websites) as a second opinion:

| Model | WebDev Arena (open) | Notes | HF |
|---|---|---|---|
| **Kimi K3.1 Pro** | 1688 (#1 open) | Vision-capable, 1M context; custom license ("other"); very large; needs serious hardware or an API | [moonshotai/Kimi-K3.1-Pro](https://hf.co/moonshotai/Kimi-K3.1-Pro) |
| **Kimi K3** | 1658; also #1 open on Design Arena websites (1331) | 2.8T-parameter, native vision, 1M context; license "other" | [moonshotai/Kimi-K3](https://hf.co/moonshotai/Kimi-K3) |
| **DeepSeek-V4.1-Flash** | 1664 | MIT; cheap | search `deepseek-ai` on HF |
| **MiMo-V2.6-Flash** | 1638 | MIT; very cheap | search `XiaomiMiMo` on HF |
| **GLM-5.3 / GLM-5.3-Flash** | 1622 / 1609 | MIT; practical to self-host or call cheaply | search `zai-org` on HF |
| **Qwen3.8-27B** | 1590 | Apache-2.0; most realistic to run locally among strong models | search `Qwen` on HF |

Caveat: these giant models are API-first for most people. Self-hosting a multi-trillion-parameter model is not realistic on consumer hardware. Use hosted inference (Hugging Face Inference Providers, OpenRouter, or the vendor) and check the license for commercial use.

### Small/specialized Hugging Face UI models (can run locally)

| Model | Task | Size | License | Notes |
|---|---|---|---|---|
| [Tesslate/UIGEN-X-32B-0727](https://hf.co/Tesslate/UIGEN-X-32B-0727), [UIGEN-X-8B](https://hf.co/Tesslate/UIGEN-X-8B), [UIGEN-X-4B-0729](https://hf.co/Tesslate/UIGEN-X-4B-0729) | Text/spec → UI code with reasoning (plan, architecture, design system, implementation) across modern stacks | 4B / 8B / 32B (Qwen3 base) | Apache-2.0 | Most active UI-specific family. 8B card suggests 8GB+ VRAM (quantized), 16GB RAM. Says accessibility needs manual testing. Examples: uigenoutput.tesslate.com |
| [Tesslate/UIGEN-T3-14B-Preview](https://hf.co/Tesslate/UIGEN-T3-14B-Preview) (+ [GGUF](https://hf.co/Tesslate/UIGEN-T3-14B-Preview-Q8_0-GGUF)) | HTML + Tailwind | 14B | see card | Preview |
| [Tesslate/UIGEN-T2-7B](https://hf.co/Tesslate/UIGEN-T2-7B) (+ [GGUF](https://hf.co/Tesslate/UIGEN-T2-7B-Q8_0-GGUF)) | HTML + Tailwind with UI reasoning; 50k-sample training | 7B (Qwen2.5-Coder base) | Apache-2.0 | Light; ~16GB VRAM unquantized; complex JS needs manual work |
| [Tesslate/UIGEN-T1.1-Qwen-14B](https://hf.co/Tesslate/UIGEN-T1.1-Qwen-14B) | Earlier UI reasoning model | 14B | Apache-2.0 | Older |
| [HuggingFaceM4/VLM_WebSight_finetuned](https://hf.co/HuggingFaceM4/VLM_WebSight_finetuned) | Screenshot → HTML/CSS | 8B | Apache-2.0 | Self-described alpha; trained on synthetic sites |
| [SALT-NLP/Design2Code-18B-v0](https://hf.co/SALT-NLP/Design2Code-18B-v0) | Screenshot → HTML | 18B (CogAgent + LoRA) | Apache-2.0 (also must follow base model/data licenses) | Research; heavy GPU, SAT format |
| [saadxsalman/Liquid-WebSight](https://hf.co/saadxsalman/Liquid-WebSight) | Image → Tailwind code | small (LFM2-VL) | Apache-2.0 | Community model, low usage; unverified quality |
| [Asanshay/websight-2-7B-kto](https://hf.co/Asanshay/websight-2-7B-kto) (+ [GGUF](https://hf.co/mradermacher/websight-2-7B-kto-GGUF)) | Screenshot → code (Qwen2.5-VL base) | 7B | unspecified | Community; unverified |

**Datasets for training or evaluation:**
- [HuggingFaceM4/WebSight](https://hf.co/datasets/HuggingFaceM4/WebSight) (synthetic HTML/CSS + screenshots, CC-BY-4.0, ~823k)
- [SALT-NLP/Design2Code](https://hf.co/datasets/SALT-NLP/Design2Code), [Design2Code-HARD](https://hf.co/datasets/SALT-NLP/Design2Code-HARD), and human-eval sets
- [smirki/UI_Reasoning_Dataset](https://hf.co/datasets/smirki/UI_Reasoning_Dataset) (used for UIGEN-T1)

**Benchmarks to read:** Design2Code (arXiv 2403.03163), WebGen-Bench, ArtifactsBench, AUV-Bench.

**Honest assessment (judgment):**
- Small UI-specialist models are good at fast HTML/Tailwind scaffolds from a spec. They are **trained on synthetic/average data**, so they inherit and may even amplify the sameness problem. They do not substitute for a design system.
- For screenshot-to-code, current general frontier or large open VLMs (Qwen-VL family in the Design2Code table scored ~88) beat the original 2024 specialist models.
- Hugging Face `Spaces` and the `hf` CLI are useful for trying models without a GPU; running anything with a GPU endpoint costs money, so check pricing first.

---

## 3. Free resources for references, tokens, and components

| Need | Resource |
|---|---|
| Accessible primitives | Radix UI, React Aria (Adobe), Headless UI, Ark UI |
| Styled starting point (restyle it!) | shadcn/ui, Park UI, Mantine, DaisyUI |
| Fonts (free) | Google Fonts, Fontsource, Bunny Fonts; Geist (Vercel, OFL), IBM Plex, Source Serif/Sans, Newsreader, Bricolage Grotesque, JetBrains Mono, Fraunces, Instrument Serif/Sans |
| Color | Radix Colors, OKLCH tools, Coolors, Realtime Colors, WebAIM contrast checker |
| Icons | Lucide, Phosphor, Tabler, Heroicons |
| Inspiration | Awwwards, Godly, Land-book, Mobbin (mobile/web flows), Refero, Page Flows, Dribbble |
| Education | NN/g, web.dev, W3C WAI, Laws of UX, Refactoring UI |
| Testing | axe DevTools, Lighthouse, Playwright, WAVE, Chrome DevTools Rendering tab (reduced motion, forced colors) |

---

## 4. A recommended free setup, step by step (about an hour to configure)

1. Create `docs/DESIGN-BRIEF.md` from kit Part 2 and answer the intake questions (Part 1).
2. Use the exploration prompt (Part 3) with the best model you can afford; pick a direction.
3. Generate `tokens.css` + `/styleguide` (Part 4).
4. Install one skill (Impeccable or frontend-design) and Playwright + axe.
5. Build the hero screen with Part 5; require screenshots at three widths.
6. Run Part 6 (states + accessibility), Part 8.1 and 8.3 (critique, anti-slop).
7. Reuse system on remaining screens (Part 7).
8. Final audit with Vercel `web-design-guidelines` and Lighthouse.

## Refresh note (2026-11-13)

Values re-checked 2026-11-13 (GitHub API, Hub, arena.ai 2026-11-11): Kimi K3.1 Pro about 2.78T parameters; DeepSeek-V4.1-Flash about 763B parameters (MIT); Qwen3.8-27B Apache-2.0; skill star counts and the updated frontend-design skill behavior are in [master guide, chapter 20](../FRONTEND-MASTER-GUIDE.md#20-tools-plugins-and-models), which supersedes numbers here if they differ.
