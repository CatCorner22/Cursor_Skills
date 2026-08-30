#!/usr/bin/env python3
"""Keep ChatGPT/Codex invocation policy consistent, then write the catalog.

Idempotent. Edits only canonical files under skills/**/SKILL.md and
skills/**/agents/openai.yaml.
"""
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
    "academic": (
        "College coursework",
        "Writing, citations, and a study system for class assignments.",
        "Mention when doing homework, papers, citations, or exam prep.",
    ),
    "adobe": (
        "Adobe App Builder / Workfront",
        "Runtime actions, UI extensions, CI/CD, testing, and Workfront apps.",
        "Mention when scaffolding or shipping an App Builder or Workfront extension.",
    ),
    "ai-transfer": (
        "AI-transfer techniques",
        "Cross-domain quality gates ported from other crafts (accounting, aviation, chess, etc.).",
        "Mention a technique or router when you want a specific verification or pipeline gate.",
    ),
    "coding": (
        "Software craft",
        "Deliverable-first engineering, architecture, UI/UX, and test-while-coding.",
        "Mention when writing or reviewing application code, not vendor-platform docs.",
    ),
    "craft": (
        "Operational craft",
        "Human mise en place and OODA×lean loops; routes into domain packs.",
        "Mention for workspace prep or a decide-act loop — not AI pipeline preflight.",
    ),
    "cursor-cloud": (
        "ChatGPT / Codex host",
        "Skill load paths, Canvas/artifacts, scheduled waits, plugin marketplaces.",
        "Mention when configuring ChatGPT Skills, Codex, or this library's install paths.",
    ),
    "cursor-sdk": (
        "Programmatic agents",
        "Drive Codex or OpenAI Agents SDK from code (CI, scripts, backends).",
        "Mention when automating Codex/ChatGPT from a script or service.",
    ),
    "cursor-team-kit": (
        "GitHub PR workflow",
        "Branches, PR reviews, CI loops, merge conflicts, shipping.",
        "Mention when opening, reviewing, or landing a GitHub pull request.",
    ),
    "first-party": (
        "First-party library skills",
        "Always-on execution posture plus library audit, smolagents, and v0.",
        "proactive-agency may invoke implicitly. Mention the others by name.",
    ),
    "huggingface": (
        "Hugging Face Hub",
        "Models, datasets, Spaces, training, Gradio, SageMaker, Hub CLI.",
        "Mention when working on Hugging Face models, Spaces, or training jobs.",
    ),
    "langchain": (
        "LangChain / LangGraph",
        "Agents, RAG, persistence, human-in-the-loop, Deep Agents, LangSmith evals.",
        "Mention when building or debugging LangChain or LangGraph apps.",
    ),
    "microsoft365": (
        "Microsoft 365",
        "Word, Excel, PowerPoint, Outlook, Teams, OneDrive.",
        "Mention when producing or organizing Office documents or mail.",
    ),
    "plaud": (
        "Plaud recorder",
        "Capture, transcription, summaries, Ask Plaud, AutoFlow, lecture notes, export.",
        "Mention when working with Plaud recordings or notes.",
    ),
    "playwright": (
        "Playwright (general)",
        "Browser automation, component testing, and trace inspection outside Adobe.",
        "Mention for Playwright tests that are not Adobe App Builder E2E.",
    ),
    "projects": (
        "Project reference",
        "Character/project bibles — not capability skills.",
        "Mention when you need a loaded project reference (currently nyx).",
    ),
    "prompt-optimizer": (
        "Prompt text",
        "Author and optimize prompts: layering, few-shot, eval slices.",
        "Mention when the work is the prompt itself, not the app around it.",
    ),
    "pydantic-ai": (
        "Pydantic AI",
        "Typed Python agents: dependencies, tools, streaming outputs.",
        "Mention when building agents with pydantic-ai, not LangChain.",
    ),
    "supabase": (
        "Supabase / Postgres",
        "Auth, Storage, Edge Functions, RLS, and Postgres habits.",
        "Mention when the database or backend is Supabase.",
    ),
    "vercel": (
        "Vercel / Next.js",
        "Next.js, deployments, AI SDK/Gateway, auth, storage, sandbox, workflow.",
        "Mention when building or deploying on Vercel or Next.js.",
    ),
}

USE_SPLIT = re.compile(
    r"(?P<when>Use when|Use whenever|Use before|Use instead|Invoke(?: manually)? when)\s+",
    re.IGNORECASE,
)


def iter_skill_md() -> list[Path]:
    return sorted(SKILLS.glob("*/**/SKILL.md"))


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        raise ValueError("missing opening ---")
    rest = text[3:]
    if rest.startswith("\r\n"):
        rest = rest[2:]
    elif rest.startswith("\n"):
        rest = rest[1:]
    match = re.search(r"\n---\s*\n", rest)
    if not match:
        raise ValueError("missing closing ---")
    return rest[: match.start()], rest[match.end() :]


def dump_yaml(data: dict) -> str:
    return yaml.safe_dump(
        data, sort_keys=False, allow_unicode=True, width=1000, default_flow_style=False
    ).rstrip()


def titleize(name: str) -> str:
    special = {
        "nextjs": "Next.js",
        "ai-sdk": "AI SDK",
        "ai-gateway": "AI Gateway",
        "v0": "v0",
        "shadcn": "shadcn/ui",
        "proactive-agency": "Proactive agency",
        "cursor-sdk": "Codex and OpenAI Agents SDK",
        "env-setup": "Codex environment setup",
    }
    return special.get(name, name.replace("-", " ").replace("_", " ").strip().title())


def first_sentence(text: str, limit: int = 140) -> str:
    text = " ".join((text or "").split())
    if not text:
        return "Skill for ChatGPT and Codex."
    sentence = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0].rstrip(".")
    if len(sentence) > limit:
        sentence = sentence[: limit - 1].rsplit(" ", 1)[0] + "…"
    return sentence


def apply_openai_yaml(skill_dir: Path, name: str, description: str) -> bool:
    agents = skill_dir / "agents"
    agents.mkdir(exist_ok=True)
    path = agents / "openai.yaml"
    implicit = name == ALWAYS_ON
    payload = {
        "interface": {
            "display_name": titleize(name),
            "short_description": first_sentence(description),
            "default_prompt": f"Use ${name} for this task.",
        },
        "policy": {
            "allow_implicit_invocation": implicit,
            "products": ["CHAT", "CODEX"],
        },
    }
    if path.exists():
        try:
            old = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            old = {}
        if isinstance(old, dict) and isinstance(old.get("interface"), dict):
            for key in ("display_name", "short_description", "default_prompt", "brand_color"):
                if old["interface"].get(key):
                    payload["interface"][key] = old["interface"][key]
    rendered = dump_yaml(payload) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == rendered:
        return False
    path.write_text(rendered, encoding="utf-8")
    return True


def apply_skill(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    front, body = split_frontmatter(original)
    data = yaml.safe_load(front) or {}
    name = data.get("name") or path.parent.name
    description = data.get("description") or ""
    if not isinstance(name, str):
        name = path.parent.name
    if not isinstance(description, str):
        description = str(description)
    changed = apply_openai_yaml(path.parent, name, description)
    return changed


def parse_description(desc: str) -> tuple[str, str]:
    desc = " ".join(desc.split())
    match = USE_SPLIT.search(desc)
    if match:
        purpose = desc[: match.start()].strip().rstrip(".").rstrip()
        when = desc[match.start() :].strip()
        if purpose:
            return purpose, when
    parts = re.split(r"(?<=\.)\s+", desc, maxsplit=1)
    purpose = parts[0].rstrip(".")
    when = parts[1] if len(parts) > 1 else "Mention this skill by name when you need it."
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
        yaml_path = path.parent / "agents" / "openai.yaml"
        implicit = False
        if yaml_path.exists():
            policy = (yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}).get("policy") or {}
            implicit = bool(policy.get("allow_implicit_invocation"))
        if name == ALWAYS_ON:
            activation = "Implicit (allow_implicit_invocation: true)"
        elif implicit:
            activation = "Implicit (unexpected — should be explicit)"
        else:
            activation = "Explicit (@ / $)"
        rows.append(
            {
                "pack": pack,
                "name": name,
                "purpose": purpose,
                "when": when,
                "activation": activation,
                "path": str(path.relative_to(ROOT)),
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
        cls, doc, pid, category = match.groups()
        doc = " ".join(doc.split())
        rows.append(
            {
                "id": pid,
                "class": cls,
                "category": category,
                "purpose": doc,
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
        f"- **Implicit (1):** `{ALWAYS_ON}` — `agents/openai.yaml` → `policy.allow_implicit_invocation: true`. Also summarized in `AGENTS.md` so Codex loads the posture in this repo.",
        f"- **Explicit ({len(explicit)}):** every other ChatGPT/Codex skill. `allow_implicit_invocation: false`. Mention with `@name` in ChatGPT or `$name` in Codex.",
        f"- **ChatGPT/Codex plugin packs ({len(by_pack)}):** installable wrappers under `plugins/<pack>/`. Enabling a pack only makes its skills *available*.",
        "- **Python runtime plugins (100):** a separate pipeline in `scripts/ai_plugin_bundle.py`. Not ChatGPT skill folders. Default tier considers catalog #1–50 plus orchestrator utilities.",
        "",
        "How to invoke an explicit skill: type `` `@nextjs` `` in ChatGPT, `` `$nextjs` `` in Codex, or ask for the job it covers.",
        "",
        f"**Counts:** {len(skill_rows)} ChatGPT/Codex skills, {len(by_pack)} plugin packs, {len(runtime)} runtime plugins.",
        "",
        "## ChatGPT/Codex plugin packs",
        "",
        "Each pack is a plugin under `plugins/<pack>/` (and `~/.codex/plugins/<pack>/` after `./scripts/load-all.sh`).",
        "",
        "| Pack | What it is for | When to use | Activation |",
        "|---|---|---|---|",
    ]
    for pack in sorted(by_pack):
        title, purpose, when = PACK_BLURBS.get(
            pack, (pack, f"Skill pack {pack}.", f"Mention a skill from `{pack}`.")
        )
        count = len(by_pack[pack])
        activation = (
            "Installed wrapper; `proactive-agency` inside is Implicit, other skills Explicit"
            if pack == "first-party"
            else "Installed wrapper — skills inside are Explicit"
        )
        lines.append(
            f"| `{pack}` ({count}) — {md_escape(title)} | {md_escape(purpose)} | {md_escape(when)} | {activation} |"
        )

    lines += ["", "## ChatGPT/Codex skills", ""]
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
        "These are **not** ChatGPT skill folders. They run only when you execute the bundle.",
        "",
        f"- **Default candidate set ({len(default_rt)}):** catalog techniques #1–50 plus orchestrator utilities.",
        f"- **Opt-in ({len(opt_rt)}):** security/ethics, creative, conversation, analytics, domain, personalization, metacognition, and extra efficiency plugins.",
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
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str]) -> int:
    catalog_only = "--catalog-only" in argv
    changed = 0
    if not catalog_only:
        for path in iter_skill_md():
            if apply_skill(path):
                changed += 1
                print(f"updated {path.relative_to(ROOT)}")
    rows = load_skill_rows()
    runtime = parse_runtime_plugins()
    write_catalog(rows, runtime)
    implicit = [r for r in rows if r["name"] == ALWAYS_ON]
    unexpected = [
        r
        for r in rows
        if r["name"] != ALWAYS_ON and "unexpected" in r["activation"]
    ]
    print(
        f"skills={len(rows)} implicit={len(implicit)} explicit={len(rows) - len(implicit)} "
        f"runtime={len(runtime)} files_changed={changed} catalog={CATALOG_PATH.relative_to(ROOT)}"
    )
    if not implicit:
        print("ERROR: proactive-agency missing", file=sys.stderr)
        return 1
    if unexpected:
        print("ERROR: unexpected implicit skills:", unexpected, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
