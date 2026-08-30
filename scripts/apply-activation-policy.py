#!/usr/bin/env python3
"""Keep Grok invocation policy consistent, then write the catalog."""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
CATALOG_PATH = ROOT / "docs" / "SKILL-PLUGIN-CATALOG.md"
ALWAYS_ON = "proactive-agency"
BUNDLE = ROOT / "scripts" / "ai_plugin_bundle.py"

PACK_BLURBS = {
    "academic": ("College coursework", "Writing, citations, and a study system for class assignments.", "Mention when doing homework, papers, citations, or exam prep."),
    "adobe": ("Adobe App Builder / Workfront", "Runtime actions, UI extensions, CI/CD, testing, and Workfront apps.", "Mention when scaffolding or shipping an App Builder or Workfront extension."),
    "ai-transfer": ("AI-transfer techniques", "Cross-domain quality gates ported from other crafts.", "Mention a technique or router when you want a specific verification or pipeline gate."),
    "coding": ("Software craft", "Deliverable-first engineering, architecture, UI/UX, and test-while-coding.", "Mention when writing or reviewing application code."),
    "craft": ("Operational craft", "Human mise en place and OODA×lean loops.", "Mention for workspace prep or a decide-act loop."),
    "cursor-cloud": ("Grok host", "Skill load paths, slash commands, artifacts, scheduled waits, marketplaces.", "Mention when configuring Grok Build or this library."),
    "cursor-sdk": ("Programmatic agents", "Drive the xAI / Grok API from code.", "Mention when automating Grok from a script or service."),
    "cursor-team-kit": ("GitHub PR workflow", "Branches, PR reviews, CI loops, merge conflicts, shipping.", "Mention when opening, reviewing, or landing a GitHub pull request."),
    "first-party": ("First-party library skills", "Always-on execution posture plus library audit, smolagents, and v0.", "proactive-agency may invoke implicitly. Mention the others with /name."),
    "huggingface": ("Hugging Face Hub", "Models, datasets, Spaces, training, Gradio, SageMaker, Hub CLI.", "Mention when working on Hugging Face models, Spaces, or training jobs."),
    "langchain": ("LangChain / LangGraph", "Agents, RAG, persistence, human-in-the-loop, Deep Agents, LangSmith evals.", "Mention when building or debugging LangChain or LangGraph apps."),
    "microsoft365": ("Microsoft 365", "Word, Excel, PowerPoint, Outlook, Teams, OneDrive.", "Mention when producing or organizing Office documents or mail."),
    "plaud": ("Plaud recorder", "Capture, transcription, summaries, Ask Plaud, AutoFlow, lecture notes, export.", "Mention when working with Plaud recordings or notes."),
    "playwright": ("Playwright (general)", "Browser automation, component testing, and trace inspection outside Adobe.", "Mention for Playwright tests that are not Adobe App Builder E2E."),
    "projects": ("Project reference", "Character/project bibles — not capability skills.", "Mention when you need a loaded project reference (currently nyx)."),
    "prompt-optimizer": ("Prompt text", "Author and optimize prompts.", "Mention when the work is the prompt itself."),
    "pydantic-ai": ("Pydantic AI", "Typed Python agents.", "Mention when building agents with pydantic-ai."),
    "supabase": ("Supabase / Postgres", "Auth, Storage, Edge Functions, RLS, Postgres habits.", "Mention when the database or backend is Supabase."),
    "vercel": ("Vercel / Next.js", "Next.js, deployments, AI SDK/Gateway, auth, storage, sandbox, workflow.", "Mention when building or deploying on Vercel or Next.js."),
}

USE_SPLIT = re.compile(
    r"(?P<when>Use when|Use whenever|Use before|Use instead|Invoke(?: manually)? when)\s+",
    re.IGNORECASE,
)


def iter_skill_md() -> list[Path]:
    return sorted(SKILLS.glob("*/**/SKILL.md"))


def split_frontmatter(text: str) -> tuple[str, str]:
    rest = text[3:]
    if rest.startswith("\n"):
        rest = rest[1:]
    match = re.search(r"\n---\s*\n", rest)
    if not match:
        raise ValueError("missing closing ---")
    return rest[: match.start()], rest[match.end() :]


def parse_description(desc: str) -> tuple[str, str]:
    desc = " ".join(desc.split())
    match = USE_SPLIT.search(desc)
    if match:
        purpose = desc[: match.start()].strip().rstrip(".")
        when = desc[match.start() :].strip()
        if purpose:
            return purpose, when
    parts = re.split(r"(?<=\.)\s+", desc, maxsplit=1)
    purpose = parts[0].rstrip(".")
    when = parts[1] if len(parts) > 1 else "Run /name when you need it."
    return purpose, when


def load_skill_rows() -> list[dict]:
    rows = []
    for path in iter_skill_md():
        text = path.read_text(encoding="utf-8")
        front, _ = split_frontmatter(text)
        data = yaml.safe_load(front) or {}
        name = data.get("name")
        desc = data.get("description") or ""
        if not isinstance(name, str) or not isinstance(desc, str):
            raise SystemExit(f"bad frontmatter: {path}")
        pack = path.relative_to(SKILLS).parts[0]
        purpose, when = parse_description(desc)
        disabled = bool(data.get("disable-model-invocation"))
        if name == ALWAYS_ON:
            activation = "Implicit (no disable-model-invocation)"
        elif disabled:
            activation = "Explicit (/name)"
        else:
            activation = "Explicit flag missing — treat as explicit"
        rows.append(
            {
                "pack": pack,
                "name": name,
                "purpose": purpose,
                "when": when,
                "activation": activation,
            }
        )
    return rows


def parse_runtime_plugins() -> list[dict]:
    text = BUNDLE.read_text(encoding="utf-8")
    tech = re.search(r"TECHNIQUE_PLUGIN_IDS = \[(.*?)\]", text, re.S)
    orch = re.search(r"ORCHESTRATOR_PLUGIN_IDS = \[(.*?)\]", text, re.S)
    default_ids = set()
    for block in (tech, orch):
        if block:
            default_ids.update(re.findall(r'"([^"]+)"', block.group(1)))
    rows = []
    class_pat = re.compile(
        r'^class (\w+)\(BasePlugin\):\n'
        r'    """(.*?)"""\n'
        r'    plugin_id = "([^"]+)"\n'
        r'    category = "([^"]+)"',
        re.M | re.S,
    )
    for match in class_pat.finditer(text):
        _cls, doc, pid, category = match.groups()
        rows.append(
            {
                "id": pid,
                "category": category,
                "purpose": " ".join(doc.split()),
                "default": pid in default_ids,
            }
        )
    return rows


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def write_catalog(skill_rows: list[dict], runtime: list[dict]) -> None:
    by_pack: dict[str, list[dict]] = defaultdict(list)
    for row in skill_rows:
        by_pack[row["pack"]].append(row)
    implicit = [r for r in skill_rows if r["name"] == ALWAYS_ON]
    explicit = [r for r in skill_rows if r["name"] != ALWAYS_ON]
    lines = [
        "# Skill and plugin catalog",
        "",
        "Generated from `skills/**/SKILL.md` and `scripts/ai_plugin_bundle.py`.",
        "Regenerate with `python3 scripts/apply-activation-policy.py --catalog-only`.",
        "",
        "## Activation policy",
        "",
        f"- **Implicit (1):** `{ALWAYS_ON}` — no `disable-model-invocation`. Also summarized in `AGENTS.md`.",
        f"- **Explicit ({len(explicit)}):** every other skill. `disable-model-invocation: true`. Run `/name` in Grok.",
        f"- **Grok plugin packs ({len(by_pack)}):** wrappers under `plugins/<pack>/`. Enable a pack to make its skills available.",
        "- **Python runtime plugins (100):** `scripts/ai_plugin_bundle.py`. Not Grok skill folders.",
        "",
        "How to invoke an explicit skill: type `` `/nextjs` `` in Grok Build, or ask for the job it covers.",
        "",
        f"**Counts:** {len(skill_rows)} Grok skills, {len(by_pack)} plugin packs, {len(runtime)} runtime plugins.",
        "",
        "## Grok plugin packs",
        "",
        "Each pack is a plugin under `plugins/<pack>/` (and `~/.grok/plugins/<pack>/` after `./scripts/load-all.sh`).",
        "",
        "| Pack | What it is for | When to use | Activation |",
        "|---|---|---|---|",
    ]
    for pack in sorted(by_pack):
        title, purpose, when = PACK_BLURBS.get(
            pack, (pack, f"Skill pack {pack}.", f"Run a skill from `{pack}`.")
        )
        count = len(by_pack[pack])
        activation = (
            "Installed wrapper; `proactive-agency` Implicit, other skills Explicit"
            if pack == "first-party"
            else "Installed wrapper — skills inside are Explicit"
        )
        lines.append(
            f"| `{pack}` ({count}) — {md_escape(title)} | {md_escape(purpose)} | {md_escape(when)} | {activation} |"
        )
    lines += ["", "## Grok skills", ""]
    for pack in sorted(by_pack):
        title, purpose, when = PACK_BLURBS.get(pack, (pack, "", ""))
        lines += [
            f"### `{pack}` — {title}",
            "",
            f"{purpose} {when}".strip(),
            "",
            "| Skill | What it is for | When to use | Activation |",
            "|---|---|---|---|",
        ]
        for row in sorted(by_pack[pack], key=lambda r: r["name"]):
            lines.append(
                f"| `{row['name']}` | {md_escape(row['purpose'])} | {md_escape(row['when'])} | {row['activation']} |"
            )
        lines.append("")
    default_rt = [r for r in runtime if r["default"]]
    opt_rt = [r for r in runtime if not r["default"]]
    lines += [
        "## Python runtime plugins (`scripts/ai_plugin_bundle.py`)",
        "",
        "These are **not** Grok skill folders. They run only when you execute the bundle.",
        "",
        f"- **Default candidate set ({len(default_rt)}):** catalog techniques #1–50 plus orchestrator utilities.",
        f"- **Opt-in ({len(opt_rt)}):** remaining runtime plugins.",
        "",
        "### Default candidate set",
        "",
        "| Plugin id | Category | What it is for | Activation |",
        "|---|---|---|---|",
    ]
    for row in default_rt:
        lines.append(
            f"| `{row['id']}` | {row['category']} | {md_escape(row['purpose'])} | Manual (bundle default candidate) |"
        )
    lines += [
        "",
        "### Opt-in runtime plugins",
        "",
        "| Plugin id | Category | What it is for | Activation |",
        "|---|---|---|---|",
    ]
    for row in opt_rt:
        lines.append(
            f"| `{row['id']}` | {row['category']} | {md_escape(row['purpose'])} | Manual (opt-in) |"
        )
    lines.append("")
    CATALOG_PATH.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str]) -> int:
    rows = load_skill_rows()
    runtime = parse_runtime_plugins()
    write_catalog(rows, runtime)
    implicit = [r for r in rows if r["name"] == ALWAYS_ON]
    missing = [r for r in rows if r["name"] != ALWAYS_ON and "missing" in r["activation"]]
    print(
        f"skills={len(rows)} implicit={len(implicit)} explicit={len(rows) - len(implicit)} "
        f"runtime={len(runtime)} catalog={CATALOG_PATH.relative_to(ROOT)}"
    )
    if not implicit:
        print("ERROR: proactive-agency missing", file=sys.stderr)
        return 1
    if missing:
        print("ERROR: skills without disable-model-invocation:", missing, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
