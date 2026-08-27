#!/usr/bin/env python3
"""Make every skill manual except proactive-agency, then write the catalog.

Idempotent. Edits only canonical files under skills/**/SKILL.md.
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
        "Cursor Cloud Agents",
        "Environment setup, snapshots, subscriptions, canvases, walkthroughs.",
        "Mention when configuring or debugging a Cloud Agent environment.",
    ),
    "cursor-sdk": (
        "Cursor SDK",
        "Drive Cursor agents from code (CI, scripts, backends).",
        "Mention when automating Cursor via @cursor/sdk.",
    ),
    "cursor-team-kit": (
        "GitHub PR workflow",
        "Branches, PR reviews, CI loops, merge conflicts, shipping.",
        "Mention when opening, reviewing, or landing a GitHub pull request.",
    ),
    "first-party": (
        "First-party library skills",
        "Always-on execution posture plus library audit, smolagents, and v0.",
        "proactive-agency is always on. Mention the others by name.",
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

KNOWLEDGE_UPDATE_DESCRIPTION = (
    "Corrects outdated LLM knowledge about the Vercel platform and introduces "
    "new products. Invoke manually when working on Vercel products, Fluid "
    "Compute, vercel.ts, or when platform facts may be stale."
)

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


def skill_name_from_front(front: str) -> str:
    for line in front.splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    raise ValueError("no name:")


def apply_skill(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    front, body = split_frontmatter(original)
    name = skill_name_from_front(front)
    lines = front.splitlines()

    def without_key(key: str) -> list[str]:
        return [ln for ln in lines if not re.match(rf"^{re.escape(key)}\s*:", ln)]

    if name == ALWAYS_ON:
        lines = without_key("disable-model-invocation")
        if not any(ln.strip() == "sessionStart: true" for ln in lines):
            # Keep sessionStart under metadata; insert after the metadata: line.
            out = []
            inserted = False
            for ln in lines:
                out.append(ln)
                if ln.strip() == "metadata:" and not inserted:
                    out.append("  sessionStart: true")
                    inserted = True
            lines = out
        # Strengthen the always-on sentence if the older wording is still there.
        new_lines = []
        for ln in lines:
            if ln.startswith("description:") and "Sole always-on skill" not in ln:
                ln = ln.replace(
                    "Injected at session start; not trigger-matched.",
                    "Sole always-on skill in this library: injected at session start, not trigger-matched.",
                )
            new_lines.append(ln)
        lines = new_lines
    else:
        if not any(ln.startswith("disable-model-invocation:") for ln in lines):
            out = []
            inserted = False
            for ln in lines:
                out.append(ln)
                if ln.startswith("name:") and not inserted:
                    out.append("disable-model-invocation: true")
                    inserted = True
            lines = out
        # Strip sessionStart so nothing else auto-injects.
        lines = [ln for ln in lines if ln.strip() != "sessionStart: true"]
        if name == "knowledge-update":
            out = []
            for ln in lines:
                if ln.startswith("description:"):
                    out.append(f"description: {KNOWLEDGE_UPDATE_DESCRIPTION}")
                else:
                    out.append(ln)
            lines = out

    new_front = "\n".join(lines)
    new_text = f"---\n{new_front}\n---\n{body}"
    if new_text != original:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


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
        meta = data.get("metadata") or {}
        session = bool(isinstance(meta, dict) and meta.get("sessionStart"))
        disabled = bool(data.get("disable-model-invocation"))
        if name == ALWAYS_ON:
            activation = "Always on"
        elif disabled:
            activation = "Manual"
        else:
            activation = "Manual (flag missing — treat as manual)"
        if name == ALWAYS_ON and (disabled or not session):
            activation = "Always on (check sessionStart)"
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
    # Extract DEFAULT_CANDIDATE_IDS membership from the two lists.
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
        in_default = pid in default_ids
        rows.append(
            {
                "id": pid,
                "class": cls,
                "category": category,
                "purpose": doc,
                "default": in_default,
            }
        )
    return rows


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def write_catalog(skill_rows: list[dict], runtime: list[dict]) -> None:
    by_pack: dict[str, list[dict]] = defaultdict(list)
    for row in skill_rows:
        by_pack[row["pack"]].append(row)

    always = [r for r in skill_rows if r["activation"].startswith("Always on")]
    manual = [r for r in skill_rows if r["activation"] == "Manual"]
    other = [r for r in skill_rows if r not in always and r not in manual]

    lines = [
        "# Skill and plugin catalog",
        "",
        "Generated from `skills/**/SKILL.md` and `scripts/ai_plugin_bundle.py`.",
        "Regenerate with `python3 scripts/apply-activation-policy.py --catalog-only`.",
        "",
        "## Activation policy",
        "",
        f"- **Always on (1):** `{ALWAYS_ON}` — `metadata.sessionStart: true`. Injected every session so the agent does the work instead of describing it.",
        f"- **Manual ({len(manual)}):** every other Cursor skill. Frontmatter `disable-model-invocation: true`. The model will not auto-invoke these; mention the skill by name, attach it, or ask for that capability explicitly.",
        "- **Cursor plugin packs (19):** installed wrappers. They do not run themselves. Enabling a pack only makes its skills *available*; those skills stay manual except `proactive-agency`.",
        "- **Python runtime plugins (100):** a separate pipeline in `scripts/ai_plugin_bundle.py`. Not Cursor skills. Default tier considers catalog #1–50 plus orchestrator utilities; security scanners and the rest stay off unless you pass `--enable-all` or `enabled_plugins`.",
        "",
        "How to invoke a manual skill: say the skill name (`` `nextjs` ``), ask for the job it covers, or attach the `SKILL.md` in Cursor.",
        "",
        f"**Counts:** {len(skill_rows)} Cursor skills, {len(by_pack)} plugin packs, {len(runtime)} runtime plugins.",
    ]
    if other:
        lines += ["", "### Activation anomalies", ""]
        for row in other:
            lines.append(f"- `{row['name']}` in `{row['pack']}`: {row['activation']}")

    lines += [
        "",
        "## Cursor plugin packs",
        "",
        "Each pack is a Cursor plugin under `plugins/<pack>/` (and `~/.cursor/plugins/local/<pack>/` after `./scripts/load-all.sh`).",
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
            "Installed wrapper; `proactive-agency` inside is Always on, other skills Manual"
            if pack == "first-party"
            else "Installed wrapper — skills inside are Manual"
        )
        lines.append(
            f"| `{pack}` ({count}) — {md_escape(title)} | {md_escape(purpose)} | {md_escape(when)} | {activation} |"
        )

    lines += ["", "## Cursor skills", ""]
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
        "These are **not** Cursor skills. They run only when you execute the bundle.",
        "",
        f"- **Default candidate set ({len(default_rt)}):** catalog techniques #1–50 plus orchestrator utilities. A default `--tier` run may still drop some of these via `quality_cost_tradeoff`.",
        f"- **Opt-in ({len(opt_rt)}):** security/ethics, creative, conversation, analytics, domain, personalization, metacognition, and extra efficiency plugins. Off unless `--enable-all` or an explicit enable list.",
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
    if "--help" in argv or "-h" in argv:
        print(
            "Usage: apply-activation-policy.py [--catalog-only]\n"
            "  (default)  mark every skill except proactive-agency as manual, then rewrite the catalog\n"
            "  --catalog-only  rewrite docs/SKILL-PLUGIN-CATALOG.md only; do not edit SKILL.md files"
        )
        return 0
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
    always = [r for r in rows if r["name"] == ALWAYS_ON]
    manual = [r for r in rows if r["name"] != ALWAYS_ON]
    missing_flag = [
        r for r in manual if r["activation"] != "Manual"
    ]
    print(
        f"skills={len(rows)} always_on={len(always)} manual={len(manual)} "
        f"runtime={len(runtime)} files_changed={changed} catalog={CATALOG_PATH.relative_to(ROOT)}"
    )
    if not always:
        print("ERROR: proactive-agency missing", file=sys.stderr)
        return 1
    if missing_flag:
        print("ERROR: skills without manual flag:", missing_flag, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
