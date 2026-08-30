---
name: new-branch-and-pr
description: Create a fresh branch, complete work, and open a pull request
disable-model-invocation: true
user-invocable: true
when-to-use: Use when the task matches this skill. Also /new-branch-and-pr.
argument-hint: /new-branch-and-pr task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Create a fresh branch, complete work, and open a pull request
  host: grok-build
  ported_from: Cursor_Skills
---
# New branch and PR

## Trigger

Starting work that should be shipped through a clean branch and pull request workflow.

## Workflow

1. Ensure the working tree is clean or explicitly handled.
2. Create a descriptive branch from the latest main.
3. Complete implementation and tests.
4. Commit focused changes and push.
5. Create a concise PR with summary and test notes.

## Guardrails

- Keep branch scope focused on one change set.
- Include verification notes before requesting review.

## Output

- New branch name
- PR summary and test notes
- PR URL
