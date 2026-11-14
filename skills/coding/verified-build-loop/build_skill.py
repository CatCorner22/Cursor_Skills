#!/usr/bin/env python3
"""Assemble SKILL.md from SKILL.core.md plus an appendix holding every template and script verbatim.

Run from the skill folder:  python3 build_skill.py
The appendix lets the skill work when only SKILL.md is installed (for example, from an account save).
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))

APPENDIX = [
    ("templates/SPEC.md", "SPEC.md (project root)", "markdown"),
    ("templates/feature_list.json", "feature_list.json (project root)", "json"),
    ("templates/progress.md", "progress.md (project root)", "markdown"),
    ("templates/init.sh", "init.sh (project root)", "bash"),
    ("templates/verify.json", ".claude/verify.json (example for a Python project; use the commands confirmed in Setup, Step 2)", "json"),
    ("templates/settings.hooks.json", "hooks block for .claude/settings.json", "json"),
    ("templates/reviewer.md", ".claude/agents/reviewer.md", "markdown"),
    ("templates/CLAUDE.section.md", "section to add to CLAUDE.md", "markdown"),
    ("scripts/vbl_common.py", ".claude/hooks/vbl_common.py", "python"),
    ("scripts/stop_check.py", ".claude/hooks/stop_check.py", "python"),
    ("scripts/protect_paths.py", ".claude/hooks/protect_paths.py", "python"),
    ("scripts/post_edit_lint.py", ".claude/hooks/post_edit_lint.py", "python"),
]


def main():
    with open(os.path.join(HERE, "SKILL.core.md"), encoding="utf-8") as handle:
        parts = [handle.read().rstrip() + "\n"]
    for number, (source, target, language) in enumerate(APPENDIX, start=1):
        with open(os.path.join(HERE, source), encoding="utf-8") as handle:
            body = handle.read().rstrip()
        fence = "````" if "```" in body else "```"
        parts.append("\n### A.{} {}\n\n{}{}\n{}\n{}\n".format(number, target, fence, language, body, fence))
    with open(os.path.join(HERE, "SKILL.md"), "w", encoding="utf-8") as handle:
        handle.write("".join(parts))
    print("Wrote SKILL.md")


if __name__ == "__main__":
    main()
