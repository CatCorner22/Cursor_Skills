## Verified build loop
This project uses verified-build-loop. Hooks enforce the checks; these lines say how to work.
- Start every session: read progress.md, run `git log --oneline -5`, run `bash init.sh`.
- Build one feature per session: the first feature in feature_list.json with "passes": false.
- Write the feature's tests first, confirm they fail for the right reason, then add them to "protected" in .claude/verify.json.
- After implementing, have the `reviewer` subagent compare the changes with SPEC.md. Fix correctness gaps; skip style.
- Set "passes": true only after the full checks pass. The Stop hook reruns them.
- Finish with a commit, a progress.md entry, and an evidence report (commands run and their output). Then tell the user to run /clear.
- Never change a protected file, a check in verify.json, or a feature's fields other than "passes". If one is wrong, stop and ask the user.
- Check commands: <fast checks>; <full checks>; <lint>.
