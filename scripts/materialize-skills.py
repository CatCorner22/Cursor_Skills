#!/usr/bin/env python3
"""Copy every skill into the paths Cursor actually scans.

Cursor skips plugin `skills/` directories that are symlinks pointing outside
the plugin folder (documented for ~/.cursor/plugins/local, and the same
walker is used for marketplace plugins). The Skills pop-out therefore never
saw this repo's 189 skills while they were only reachable through outbound
symlinks.

This script writes real copies to:
  .cursor/skills/<name>/
  .agents/skills/<name>/
  plugins/<pack>/skills/<name>/
  plugins/all-skills/skills/<name>/

and writes valid plugin + marketplace manifests (no outbound symlinks).
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
CURSOR_SKILLS = ROOT / ".cursor" / "skills"
AGENTS_SKILLS = ROOT / ".agents" / "skills"
PLUGINS = ROOT / "plugins"
ALL_SKILLS = PLUGINS / "all-skills"

PACK_BLURBS = {
    "academic": "College coursework: writing, citations, study system.",
    "adobe": "Adobe App Builder and Workfront: actions, UI, CI/CD, testing.",
    "ai-transfer": "Cross-domain AI quality gates.",
    "coding": "Software craft: deliverable-first, architecture, UI/UX, test-while-coding.",
    "craft": "Operational craft: mise en place and OODA×lean.",
    "cursor-cloud": "Cursor Cloud Agent environment, snapshots, subscriptions, canvases.",
    "cursor-sdk": "Drive Cursor agents from code via @cursor/sdk.",
    "cursor-team-kit": "GitHub PR workflow: branches, reviews, CI, conflicts, shipping.",
    "first-party": "proactive-agency is always on. Other first-party skills are Agent Decides.",
    "huggingface": "Hugging Face Hub: models, Spaces, training, Gradio, SageMaker.",
    "langchain": "LangChain/LangGraph agents, RAG, persistence, Deep Agents.",
    "microsoft365": "Microsoft 365: Word, Excel, PowerPoint, Outlook, Teams, OneDrive.",
    "plaud": "Plaud recorder: capture, transcription, summaries, AutoFlow, export.",
    "playwright": "Playwright browser automation, component tests, traces (non-Adobe).",
    "projects": "Project reference material (nyx).",
    "prompt-optimizer": "Author and optimize prompt text.",
    "pydantic-ai": "Pydantic AI typed Python agents.",
    "supabase": "Supabase Auth, Storage, Edge Functions, Postgres.",
    "vercel": "Vercel and Next.js platform skills.",
    "all-skills": "All 189 Cursor skills from this repository, as one installable plugin.",
}


def iter_skills() -> list[tuple[str, str, Path]]:
    rows = []
    for skill_md in sorted(SKILLS.rglob("SKILL.md")):
        skill_dir = skill_md.parent
        name = skill_dir.name
        pack = skill_dir.relative_to(SKILLS).parts[0]
        rows.append((pack, name, skill_dir))
    return rows


def reset_dir(path: Path) -> None:
    if path.exists() or path.is_symlink():
        if path.is_symlink() or path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_skill(src: Path, dest: Path) -> None:
    reset_dir(dest)
    dest.rmdir()
    dest.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        ["tar", "-C", str(src), "--exclude", "AGENTS.md", "-cf", "-", "."],
        stdout=subprocess.PIPE,
    )
    subprocess.run(["tar", "-C", str(dest), "-xf", "-"], check=True, stdin=proc.stdout)
    proc.wait()
    if proc.returncode:
        raise SystemExit(f"copy failed: {src} -> {dest}")


def write_plugin_manifests(dest: Path, name: str, description: str) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    cursor_plugin = dest / ".cursor-plugin"
    cursor_plugin.mkdir(exist_ok=True)
    body = {
        "name": name,
        "version": "1.0.0",
        "description": description,
        "author": {"name": "CatCorner22"},
        "skills": "skills",
    }
    (cursor_plugin / "plugin.json").write_text(json.dumps(body, indent=2) + "\n")
    agent = {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        **body,
    }
    (dest / "plugin.json").write_text(json.dumps(agent, indent=2) + "\n")


def write_marketplace(packs: list[str]) -> None:
    plugins = []
    for pack in packs:
        plugins.append(
            {
                "name": pack,
                "source": pack,
                "description": PACK_BLURBS.get(pack, f"Skill pack {pack}."),
            }
        )
    data = {
        "name": "cursor-skills-snapshot",
        "owner": {"name": "CatCorner22"},
        "metadata": {
            "description": "All vendored skill packs from this repo, loaded as Cursor plugins.",
            "version": "1.0.0",
            "pluginRoot": "plugins",
        },
        "plugins": plugins,
    }
    market = ROOT / ".cursor-plugin"
    market.mkdir(exist_ok=True)
    (market / "marketplace.json").write_text(json.dumps(data, indent=2) + "\n")


def main() -> int:
    rows = iter_skills()
    if len(rows) != 189:
        # Still proceed, but make the mismatch obvious.
        print(f"WARNING: expected 189 skills, found {len(rows)}")

    reset_dir(CURSOR_SKILLS)
    reset_dir(AGENTS_SKILLS)
    reset_dir(ALL_SKILLS / "skills")

    packs: dict[str, list[tuple[str, Path]]] = {}
    for pack, name, src in rows:
        packs.setdefault(pack, []).append((name, src))
        copy_skill(src, CURSOR_SKILLS / name)
        copy_skill(src, AGENTS_SKILLS / name)
        copy_skill(src, ALL_SKILLS / "skills" / name)

    pack_names = sorted(packs)
    for pack in pack_names:
        wrapper = PLUGINS / pack
        skills_dest = wrapper / "skills"
        reset_dir(skills_dest)
        for name, src in packs[pack]:
            copy_skill(src, skills_dest / name)
        write_plugin_manifests(wrapper, pack, PACK_BLURBS.get(pack, f"Skill pack {pack}."))

    write_plugin_manifests(
        ALL_SKILLS,
        "all-skills",
        PACK_BLURBS["all-skills"],
    )
    write_marketplace(pack_names + ["all-skills"])

    cursor_n = len(list(CURSOR_SKILLS.glob("*/SKILL.md")))
    agents_n = len(list(AGENTS_SKILLS.glob("*/SKILL.md")))
    all_n = len(list((ALL_SKILLS / "skills").glob("*/SKILL.md")))
    print(
        f"materialized cursor={cursor_n} agents={agents_n} "
        f"all-skills={all_n} packs={len(pack_names)}"
    )
    if cursor_n != len(rows) or all_n != len(rows):
        return 1
    # Guard: no outbound skill-dir symlinks left in discovery paths.
    for root in (CURSOR_SKILLS, AGENTS_SKILLS, ALL_SKILLS / "skills"):
        for child in root.iterdir():
            if child.is_symlink():
                print(f"ERROR: leftover symlink {child}")
                return 1
    for pack in pack_names:
        skills_link = PLUGINS / pack / "skills"
        if skills_link.is_symlink():
            print(f"ERROR: leftover plugin symlink {skills_link}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
