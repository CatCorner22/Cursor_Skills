#!/usr/bin/env python3
"""Stop hook for verified-build-loop.

Runs each time Claude tries to end its turn. In order:
  1. Integrity: confirms that no protected file, check, or feature changed against the rules.
  2. Skip: if nothing in the project changed since the last passing run, lets Claude stop.
  3. Fast checks: runs every command in verify.json "fast_checks".
  4. Full checks: also runs "full_checks" when a feature changed to "passes": true.
On any failure, exits with code 2 so Claude Code sends the report back to Claude.
"""

import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vbl_common as vbl  # noqa: E402

EXCLUDED_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".tox", "dist", "build", ".next", "target", ".idea", ".vscode",
}
REPEAT_LIMIT = 3  # identical failures in a row, while already continuing, before the hook lets Claude stop
DURATION = re.compile(r"\b\d+(?:\.\d+)?\s*(?:ms|s|sec|secs|seconds)\b")


def project_files(root, extra_excludes):
    """Yield relative paths of project files, skipping dependency and cache folders."""
    excluded = EXCLUDED_DIRS | set(extra_excludes)
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in excluded)
        for name in sorted(files):
            yield vbl.rel_path(root, os.path.join(current, name))


def fingerprint(root, extra_excludes):
    digest = hashlib.sha256()
    for relative in project_files(root, extra_excludes):
        if relative == vbl.LOCK_REL or relative.endswith(".tmp"):
            continue
        try:
            info = os.stat(os.path.join(root, relative))
        except OSError:
            continue
        digest.update("{}|{}|{}\n".format(relative, info.st_size, info.st_mtime_ns).encode("utf-8"))
    return digest.hexdigest()


def check_protected_hashes(root, config, lock):
    """Compare protected files with the lock. Record files protected for the first time."""
    problems = []
    hashes = lock.setdefault("hashes", {})
    patterns = vbl.protected_patterns(config)
    seen = set()
    for relative in project_files(root, config.get("fingerprint_exclude", [])):
        if relative == vbl.LOCK_REL or not vbl.matches_any(relative, patterns):
            continue
        seen.add(relative)
        current = vbl.sha256_file(os.path.join(root, relative))
        recorded = hashes.get(relative)
        if recorded is None:
            hashes[relative] = current
        elif recorded != current:
            problems.append("protected file '{}' changed".format(relative))
    for relative in sorted(set(hashes) - seen):
        problems.append("protected file '{}' is missing".format(relative))
    return problems


def newly_passed(old_features, new_features):
    old = {f.get("id"): f.get("passes") for f in (old_features or {}).get("features", []) if isinstance(f, dict)}
    return sorted(
        f.get("id") for f in (new_features or {}).get("features", [])
        if isinstance(f, dict) and f.get("passes") is True and old.get(f.get("id")) is not True
    )


def main():
    hook_input = vbl.read_hook_input()
    root = vbl.project_dir(hook_input)
    config, error = vbl.load_config(root)
    if error:
        vbl.block("verified-build-loop: " + error + "\nFix the JSON in .claude/verify.json.")
    if config is None:
        return 0  # project not set up for verified-build-loop

    lock_path = os.path.join(root, vbl.LOCK_REL)
    lock, lock_error = vbl.load_json_file(lock_path)
    if lock_error:
        vbl.block("verified-build-loop: the lock file is not valid JSON. Ask the user to run: "
                  "python3 .claude/hooks/vbl_common.py relock")

    feature_path = os.path.join(root, vbl.feature_list_rel(config))
    features, feature_error = vbl.load_json_file(feature_path)
    if feature_error:
        vbl.block("verified-build-loop: " + feature_error)

    first_run = lock is None
    if first_run:
        lock = {"config_snapshot": config, "feature_snapshot": features, "hashes": {}}

    # 1. Integrity
    problems = []
    problems += vbl.config_violations(lock.get("config_snapshot"), config)
    problems += vbl.feature_list_violations(lock.get("feature_snapshot"), features)
    problems += check_protected_hashes(root, config, lock)
    if problems:
        vbl.block(
            "verified-build-loop integrity check failed:\n- " + "\n- ".join(problems) +
            "\nRestore the original content (for example with git), or stop and ask the user. "
            "Only the user can unprotect a file or accept a change to a protected file."
        )

    # 2. Skip when nothing changed since the last passing run
    excludes = config.get("fingerprint_exclude", [])
    passed_now = newly_passed(lock.get("feature_snapshot"), features)
    lock["config_snapshot"] = config
    if not first_run and not passed_now and lock.get("last_pass_fingerprint") == fingerprint(root, excludes):
        vbl.write_json_file(lock_path, lock)
        return 0

    # 3 and 4. Run checks
    checks = list(config.get("fast_checks", []))
    if passed_now:
        checks += list(config.get("full_checks", []))
    failures = []
    for check in checks:
        passed, report = vbl.run_check(root, check)
        if not passed:
            failures.append(report)

    if failures:
        report = "\n\n".join(failures)
        # Durations such as "in 0.08s" differ on every run; drop them so identical failures match.
        stable = DURATION.sub("", report)
        signature = hashlib.sha256(stable.encode("utf-8")).hexdigest()
        repeats = lock.get("failure_repeats", 0) + 1 if lock.get("last_failure") == signature else 1
        lock["last_failure"] = signature
        lock["failure_repeats"] = repeats
        vbl.write_json_file(lock_path, lock)  # feature_snapshot stays old, so the full checks run again next time
        if hook_input.get("stop_hook_active") and repeats >= REPEAT_LIMIT:
            print(json.dumps({"systemMessage":
                "verified-build-loop: the same checks failed {} times in a row with no change. "
                "Claude stopped without passing them. Failing output:\n{}".format(repeats, vbl.tail(report, 40))}))
            return 0
        header = "verified-build-loop: checks failed. Fix the cause, then finish your turn again."
        if passed_now:
            header += ("\nYou set \"passes\": true on {}. The full checks must pass first; "
                       "if the feature is not done, set it back to false.".format(", ".join(passed_now)))
        vbl.block(header + "\n\n" + report)

    lock["feature_snapshot"] = features
    lock["last_failure"] = None
    lock["failure_repeats"] = 0
    lock["last_pass_fingerprint"] = fingerprint(root, excludes)
    vbl.write_json_file(lock_path, lock)
    return 0


if __name__ == "__main__":
    sys.exit(main())
