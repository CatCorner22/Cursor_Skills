# Release checklist for mscd-contracts

The skill reaches Blake in 3 places, and they must match: the GitHub master (CatCorner22/Cursor_Skills, skills/legal/mscd-contracts), the skill in his claude.ai account (Customize > Skills), and the MSCD Project's custom instructions (`project-instructions.md` in this folder, saved on November 6, 2026).

1. Run the self-tests: `python3 scripts/mscd_lint.py --self-test`, `python3 scripts/coverage.py --self-test`, and the reviewer suites; all must pass.
2. Check the description in SKILL.md: 1,000 characters or fewer.
3. Build the ZIP from a clean copy: the folder `mscd-contracts/` at the top, without `evals/` (the answer keys would leak into later blind tests), `deploy/`, or `__pycache__/`. Run `unzip -t` on it.
4. Replace the skill in claude.ai: upload the new ZIP first; remove the old version only after the new one shows in the list. Keep the previous ZIP.
5. If the house rules or the fallback file paths changed, update `project-instructions.md`, then the Project's instructions, and confirm the saved text matches this file exactly.
6. Test in a new MSCD Project chat: a 1-line shall question and a pasted clause must load the skill; a non-contract question must not. Delete the test chats.
7. Commit and push to a branch of the GitHub master, never to main, and update the pull request.
