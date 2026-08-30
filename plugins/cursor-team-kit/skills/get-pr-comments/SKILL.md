---
name: get-pr-comments
description: Fetch and summarize review comments from the active pull request
disable-model-invocation: true
user-invocable: true
when-to-use: Use when the task matches this skill. Also /get-pr-comments.
argument-hint: /get-pr-comments task
compatibility: Grok Build (CLI, TUI, IDE). Also readable as Agent Skills / AGENTS.md.
metadata:
  author: CatCorner22
  short-description: Fetch and summarize review comments from the active pull request
  host: grok-build
  ported_from: Cursor_Skills
---
# Get PR comments

## Trigger

Need a concise, actionable summary of feedback on the active pull request.

## Workflow

1. Resolve the active PR for the current branch.
2. Fetch review comments and discussion comments.
3. Group feedback by severity and actionability.
4. Return a concise action list.

## Output

- Grouped feedback summary
- Action list ordered by priority
- Open questions that still need clarification
