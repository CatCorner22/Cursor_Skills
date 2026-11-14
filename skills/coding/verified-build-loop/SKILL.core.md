---
name: verified-build-loop
description: Sets up and repairs an enforced build loop in a Claude Code project - a written definition of done, pass-or-fail checks, hooks that block Claude from stopping until the checks pass and from weakening tests, and a read-only reviewer subagent. Use when the user invokes /verified-build-loop to start or repair a multi-session build.
disable-model-invocation: true
---
# Verified build loop

## Purpose

Claude stops when work looks done. This skill makes "done" something a check proves. It installs five layers in a project:

| Layer | What it is | Who controls it |
|---|---|---|
| 1. Definition of done | SPEC.md and feature_list.json | Instruction and file |
| 2. Checks | Test, typecheck, lint, and end-to-end commands in .claude/verify.json | Instruction and file |
| 3. Enforcement hooks | Stop, PreToolUse, and PostToolUse hooks | Claude Code enforces |
| 4. Independent reviewer | Read-only `reviewer` subagent | Fresh context |
| 5. Session discipline | progress.md, init.sh, one feature per session, one commit per feature | Instruction and file |

Claude Code enforces only layer 3. Everything else is an instruction that Claude chooses to follow. That is why layer 3 exists.

## Terms

- **Check**: a command that exits 0 on pass and nonzero on fail.
- **Fast checks**: checks the Stop hook runs each time Claude tries to end a turn after a change (for example, unit tests and typecheck).
- **Full checks**: checks the Stop hook also runs when a feature changes to `"passes": true` (for example, the whole test suite and the end-to-end test).
- **Protected file**: a file Claude may read but never change. Only the user can unprotect it.
- **Lock**: .claude/verify-lock.json. The Stop hook records hashes and snapshots there and compares against them.
- **Evidence report**: the exact commands Claude ran and their output, pasted at the end of a turn.

## When to use each phase

- The project has no .claude/verify.json: run **Phase 1 (Setup)**, then **Phase 2** for the first feature.
- The project has .claude/verify.json: skip to **Phase 2 (Feature loop)**.
- A hook misbehaves or a file is missing: run **Phase 3 (Repair)**.

---

## Phase 1: Setup (once per project)

Do every step in order. Tell the user what each step found before moving to the next step.

### Step 1. Preflight

Run these and report the result of each:

1. `git rev-parse --is-inside-work-tree`. If the folder is not a git repository, ask the user whether to run `git init`. The loop depends on git to restore files and record each feature.
2. `git status --porcelain`. If the tree has uncommitted changes, ask the user whether to commit them first, so setup changes stay separate.
3. `python3 --version`. If that fails, try `python --version`. Use whichever works in every hook command in Step 6. If neither works, stop: the hooks need Python 3.8 or later.
4. Check whether `.claude/settings.json` exists. If it exists, Step 6 merges into it instead of replacing it.
5. Check whether `.claude/verify.json` exists. If it exists, this project already has the loop; go to Phase 3.

### Step 2. Find or build the checks

1. Read the project's build files (for example, package.json, pyproject.toml, Makefile, Cargo.toml, go.mod) and any CI configuration.
2. Propose four commands to the user: fast checks, full checks, lint-on-edit (with a `{file}` placeholder), and an end-to-end test.
3. Exclude the `.claude/` folder from every check (for example, `ruff check . --extend-exclude .claude`, or an `ignorePatterns` entry for ESLint). The hooks protect their own files, so a check that reports on those files can never pass.
4. Run each proposed command once and show the output. A command that cannot run is not a check. Every check must pass on the current code before setup continues. If a check fails now (for example, old lint errors), fix the cause or narrow the command, and get the user's approval for either choice. Otherwise the Stop hook blocks every turn on problems that predate the build.
5. If the project has no tests, build the smallest working test setup first (one passing smoke test), and run it.
6. If the project has a user interface, the end-to-end check drives it the way a person would (for example, Playwright for a web app). Unit tests alone do not prove a feature works.
7. Ask the user to confirm the four commands before writing them anywhere.

Keep fast checks fast. The Stop hook runs them on every turn that changes a file. A suite that takes more than about two minutes belongs in full checks.

### Step 3. Write SPEC.md by interviewing the user

1. Ask the user questions until you could write the spec without guessing. Ask with multiple-choice questions where the tool allows. Cover: purpose, users, every requirement, edge cases for each requirement, what is out of scope, and constraints.
2. Write SPEC.md from the template in the appendix. Number every requirement.
3. Show SPEC.md to the user and get approval before Step 4.

### Step 4. Write feature_list.json

1. Turn each numbered requirement into one or more features. Each feature is small enough to build and test in one session.
2. Give each feature an `id`, a `description`, a `spec_section`, and `steps` that a person follows to test it end to end.
3. Set every feature to `"passes": false`.
4. After setup, the hooks allow only two kinds of change to this file: setting `passes`, and adding a new feature with `"passes": false`. Get every other field right now; once you install the hooks, only the user can change it.

### Step 5. Write progress.md and init.sh

1. Write progress.md from the template.
2. Write init.sh with the project's real install and smoke-check commands. Run `bash init.sh` and confirm it exits 0.

### Step 6. Install the hooks and the reviewer

Write the files in this order. The order matters: once .claude/verify.json exists, the PreToolUse hook protects the other files, so verify.json goes last.

1. **Hook scripts.** Create `.claude/hooks/` and put four files in it: `vbl_common.py`, `stop_check.py`, `protect_paths.py`, `post_edit_lint.py`. If this skill's folder holds a `scripts/` folder, copy the files from there. Otherwise write each file exactly as the appendix gives it, with no changes.
2. **Reviewer.** Write `.claude/agents/reviewer.md` from the appendix.
3. **Settings.** Add the `hooks` block from the appendix to `.claude/settings.json`. If the file exists, merge: keep every existing setting and hook, and append these three hook groups. If Step 1 found `python` instead of `python3`, change the commands to match. Show the user the final file.
4. **verify.json.** Write `.claude/verify.json` with the commands confirmed in Step 2. Leave `"protected": []` for now; Phase 2 fills it as tests get written.
5. **CLAUDE.md.** Add the "Verified build loop" section from the appendix to CLAUDE.md (create the file if needed), with the real check commands filled in. Keep the section short.
6. **.gitignore.** Add `.claude/verify-lock.json` to .gitignore. The lock holds timestamps that differ on each machine; each machine builds its own lock on its first Stop hook run.

### Step 7. Smoke-test the hooks

1. Ask the user to type `/hooks` and confirm that PreToolUse, PostToolUse, and Stop entries appear for this project. If they do not appear, ask the user to restart the Claude Code session and check again. Project hooks also wait until the user accepts the workspace trust prompt for the folder.
2. Run each script by hand with a sample input and show the exit code:
   - `echo '{"tool_name":"Write","tool_input":{"file_path":"'"$PWD"'/.claude/verify-lock.json","content":"{}"}}' | python3 .claude/hooks/protect_paths.py; echo "exit $?"` must print `exit 2`.
   - `echo '{"stop_hook_active":false}' | python3 .claude/hooks/stop_check.py; echo "exit $?"` must print `exit 0` if the fast checks pass. This first run also creates the lock.
3. If either result differs, go to Phase 3.

### Step 8. Commit the setup

Commit everything from Phase 1 in one commit with the message `Set up verified build loop`. Then tell the user to run `/clear` and say "build the next feature."

---

## Phase 2: Feature loop (once per feature, one feature per session)

### Startup
1. Read progress.md (newest entry first) and run `git log --oneline -5`.
2. Run `bash init.sh`. If it fails, fix the project before starting new work; a broken start means the last session ended badly.
3. Pick the first feature in feature_list.json with `"passes": false`. State its ID and description.

### Build
4. **Tests first.** Write tests for the feature, including its edge cases from SPEC.md and an end-to-end test that follows the feature's `steps`. Run them and confirm they fail for the right reason (the feature is missing), not for a broken test. Fix every lint error in the test files now.
5. **Protect the tests.** Add each new test file to `"protected"` in .claude/verify.json. From then on, nobody but the user can change those tests, so a defect that remains in a test at this point (a typo, a lint error, a wrong expected value) blocks the build until the user unlocks it.
6. **Implement.** Write the code. The PostToolUse hook lints each edited file; fix what it reports right away.
7. **Run the fast checks** yourself and fix every failure. Do not wait for the Stop hook to find them.

### Verify
8. **Independent review.** Ask the `reviewer` subagent to compare the changed files with SPEC.md for this feature. Give it the feature ID, the changed files (`git diff --name-only`), and the SPEC.md path. Fix every correctness gap it reports. Do not act on style comments.
9. **Run the full checks**, including the end-to-end test. Fix every failure.
10. **Set `"passes": true`** for this one feature only. When you end the turn, the Stop hook runs the full checks again. If they fail, the hook sends you back: fix the cause, or set the feature back to `false` if it is not done.

### Finish
11. Commit with a message that names the feature ID.
12. Add an entry to progress.md (use the template).
13. End with an evidence report: each command you ran in steps 7 through 10 and the last lines of its output, plus the reviewer's findings and what you did about each one.
14. Tell the user the next feature ID and to run `/clear` before starting it.

---

## Phase 3: Repair

Use this when a hook blocks something it should allow, allows something it should block, or a setup file is missing.

1. Run `python3 -m unittest -v` on the skill's tests if the skill folder holds a `tests/` folder.
2. Compare each file in `.claude/hooks/` with the appendix or the skill's `scripts/` folder. A difference means something changed the file; tell the user. Claude cannot replace these files itself while the hooks are active, because the hooks protect them. The user replaces them, then runs `python3 .claude/hooks/vbl_common.py relock`.
3. If .claude/verify.json is missing, rebuild it from Phase 1, Step 2, and show it to the user before writing it.

---

## What to do when a check cannot pass

- **The code is wrong:** fix the code. That is the normal case.
- **The test is wrong** (it tests something SPEC.md does not require, or it has a defect): stop. Tell the user which test, which line, and why. Only the user can unprotect it, with `python3 .claude/hooks/vbl_common.py unlock <path>`.
- **The environment is broken** (a missing dependency, a service that is not running): fix the environment if it is inside the project. Otherwise stop and tell the user exactly what is missing.
- **The same failure repeats:** after three identical failures in a row with no change, the Stop hook lets the turn end and shows the user a message with the failing output. Do not hide this. Explain what you tried.

Never weaken a check to make it pass: no skipping tests, no loosening assertions, no deleting checks, no editing lint configuration to silence a rule.

## User-only commands

The PreToolUse hook blocks Claude from running these. The user runs them in a terminal:

- `python3 .claude/hooks/vbl_common.py unlock <path>`: stop protecting one file.
- `python3 .claude/hooks/vbl_common.py relock`: accept the current state of every protected file, check, and feature. The next Stop hook run records it.

## What each hook enforces

| Hook | When it runs | What it blocks |
|---|---|---|
| PreToolUse (`protect_paths.py`) | Before every Write, Edit, MultiEdit, NotebookEdit, and Bash call | Writes to protected files, the hook files, `.claude/settings.json`, the reviewer, and the lock; feature-list changes other than `passes` or a new failing feature; verify.json changes that remove or change a check, a protected path, or a setting; Bash commands that name a protected path and also write, move, or delete; the user-only commands |
| PostToolUse (`post_edit_lint.py`) | After every Write, Edit, and MultiEdit call | Nothing (the edit already happened). Shows lint errors to Claude. |
| Stop (`stop_check.py`) | Each time Claude tries to end a turn | Ending the turn while: a protected file, a check, or a feature changed against the rules (by any route, including scripts); any fast check fails; or a feature changed to `"passes": true` and any full check fails |

The Stop hook skips the checks when no project file changed since the last passing run. Claude Code ends the turn anyway after eight consecutive blocks with no tool call in between.

## Contingencies

| Situation | What happens | What to do |
|---|---|---|
| The PreToolUse hook blocks a Bash command by mistake (for example, `cp tests/test_a.py /tmp/`) | The PreToolUse heuristic blocks any write-type command that names a protected path | Split the command so the protected path and the write are separate, or read the file instead |
| Claude changes a protected file through a route the PreToolUse hook cannot see (a script, `git stash`, `git reset`) | The Stop hook's hash check catches it and blocks | Restore the file with git, or ask the user |
| Something deletes the lock file | The next Stop hook run treats the project as new and records the current state | The user should check `git diff` for protected files; the hooks block Claude from deleting the lock through file tools and recognized Bash commands |
| A check reports problems in a protected file (a hook script, or a locked test) | Claude cannot fix the file, so the check fails on every turn | Exclude `.claude/` from checks (Setup, Step 2); for a locked test, stop and ask the user to unlock it |
| Fast checks are slow | Every turn that changes a file waits for them | Move slow checks to full checks; the user edits verify.json (Claude may only add checks) |
| Python is missing on the machine | Hooks fail; Claude Code treats a failed command hook as a non-blocking error, so the action proceeds without the check | Install Python 3.8 or later; run Phase 1, Step 7 again |
| Windows | Tested on Linux. Quoting in `lint_on_edit` uses POSIX rules | Run the Step 7 smoke test before relying on the hooks |
| A determined workaround | Local hooks cannot stop every possible workaround by a program that can run code | The reviewer, the git history, and the user's review of the diff are the backstop |
| Checks pass but the feature is wrong | Checks prove only what they cover | The reviewer compares with SPEC.md; the user tries the feature |

## Optional step map to the user's other skills

If the user has these skills, call them at these steps. They are optional instructions; the hooks do not depend on them.

| Step | Skill |
|---|---|
| Phase 1, Step 3 (interview and spec) | `premise-check`, `ask-or-assume`, `unambiguous-language` |
| Phase 2, step 4 (designing the end-to-end test) | `validation-design` |
| Phase 2, step 6, when a change touches many files | `scope-and-blast-radius-check` |
| Phase 2, step 13 (evidence report) | `completion-evidence-gate` |
| Reviewing SPEC.md or a plan before building | `backward-review-gate` |

## Settings that help

- Use `/effort high` for feature work. Save `max` for a hard problem Claude works through alone.
- Use `/rename <project>-<feature>` and `claude --resume` to pick up multi-day work.
- After two failed corrections of the same problem, run `/clear` and write one better prompt.

---

## Appendix: file contents

Write these files exactly as shown when the skill folder has no `scripts/` or `templates/` folder.
