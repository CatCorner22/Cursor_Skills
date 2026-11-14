#!/usr/bin/env python3
"""Shared helpers for the verified-build-loop hooks.

Standard library only. Python 3.8 or later.

The hooks read two files in the project:
  .claude/verify.json       the check configuration (Claude may add to it, never remove)
  .claude/verify-lock.json  the integrity record (only the Stop hook and the user write it)

User-only commands (run these yourself in a terminal; the PreToolUse hook blocks Claude from running them):
  python3 .claude/hooks/vbl_common.py unlock <path>   stop protecting one file
  python3 .claude/hooks/vbl_common.py relock          accept the current state of every protected file
"""

import fnmatch
import hashlib
import json
import os
import subprocess
import sys

CONFIG_REL = ".claude/verify.json"
LOCK_REL = ".claude/verify-lock.json"

# Paths that Claude may never change through a file tool or a Bash command.
ALWAYS_PROTECTED = [
    ".claude/verify-lock.json",
    ".claude/hooks/*",
    ".claude/settings.json",
    ".claude/agents/reviewer.md",
]

OUTPUT_TAIL_LINES = 150


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def project_dir(hook_input=None):
    """Return the absolute project root."""
    root = os.environ.get("CLAUDE_PROJECT_DIR")
    if not root and hook_input:
        root = hook_input.get("cwd")
    return os.path.abspath(root or os.getcwd())


def rel_path(root, path):
    """Return path relative to root with forward slashes, or None if outside root."""
    if not path:
        return None
    absolute = os.path.abspath(path if os.path.isabs(path) else os.path.join(root, path))
    try:
        relative = os.path.relpath(absolute, root)
    except ValueError:  # different drive on Windows
        return None
    if relative == ".." or relative.startswith(".." + os.sep):
        return None
    return relative.replace(os.sep, "/")


def matches_any(relative, patterns):
    """True if relative matches a pattern. A pattern ending in '/' covers that whole folder.
    In fnmatch, '*' also matches '/', so 'tests/*' covers nested folders."""
    for pattern in patterns:
        pattern = pattern.replace("\\", "/")
        if pattern.startswith("./"):
            pattern = pattern[2:]
        if pattern.endswith("/"):
            if relative.startswith(pattern):
                return True
        elif fnmatch.fnmatchcase(relative, pattern):
            return True
    return False


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------

def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError:
        return None


def load_json_file(path):
    """Return (data, error). data is None when the file does not exist."""
    text = read_text(path)
    if text is None:
        return None, None
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, "{} is not valid JSON: {}".format(path, exc)


def write_json_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temp_path, path)


def sha256_file(path):
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            for block in iter(lambda: handle.read(65536), b""):
                digest.update(block)
    except FileNotFoundError:
        return None
    return digest.hexdigest()


def load_config(root):
    """Return (config, error). config is None when the project has no verify.json."""
    return load_json_file(os.path.join(root, CONFIG_REL))


def protected_patterns(config):
    patterns = list(ALWAYS_PROTECTED)
    if config:
        patterns.extend(config.get("protected", []))
    return patterns


def feature_list_rel(config):
    return (config or {}).get("feature_list", "feature_list.json")


# ---------------------------------------------------------------------------
# Change rules
# ---------------------------------------------------------------------------

def _features_by_id(data):
    features = (data or {}).get("features")
    if not isinstance(features, list):
        return None, "feature list must hold a 'features' array"
    by_id = {}
    for feature in features:
        if not isinstance(feature, dict) or "id" not in feature:
            return None, "every feature needs an 'id'"
        if feature["id"] in by_id:
            return None, "feature id {} appears twice".format(feature["id"])
        by_id[feature["id"]] = feature
    return by_id, None


def feature_list_violations(old_data, new_data):
    """Rules: keep every old feature; change no field except 'passes'; add new features only with passes false."""
    if old_data is None:
        return []
    old, error = _features_by_id(old_data)
    if error:
        return []  # the old file was already malformed; do not block repairs
    new, error = _features_by_id(new_data)
    if error:
        return [error]
    problems = []
    for feature_id, old_feature in old.items():
        new_feature = new.get(feature_id)
        if new_feature is None:
            problems.append("feature {} was removed".format(feature_id))
            continue
        old_rest = {k: v for k, v in old_feature.items() if k != "passes"}
        new_rest = {k: v for k, v in new_feature.items() if k != "passes"}
        if old_rest != new_rest:
            problems.append("feature {} changed a field other than 'passes'".format(feature_id))
    for feature_id, new_feature in new.items():
        if feature_id not in old and new_feature.get("passes") is not False:
            problems.append("new feature {} must start with \"passes\": false".format(feature_id))
    return problems


def _checks_by_name(config, key):
    return {check.get("name"): check for check in (config or {}).get(key, []) if isinstance(check, dict)}


def config_violations(old_config, new_config):
    """Rules: keep every old check unchanged; keep every protected path; keep lint and feature-list settings."""
    if old_config is None:
        return []
    if not isinstance(new_config, dict):
        return ["verify.json must hold a JSON object"]
    problems = []
    for key in ("fast_checks", "full_checks"):
        old_checks = _checks_by_name(old_config, key)
        new_checks = _checks_by_name(new_config, key)
        for name, check in old_checks.items():
            if new_checks.get(name) != check:
                problems.append("{} check '{}' was removed or changed".format(key, name))
    removed = set(old_config.get("protected", [])) - set(new_config.get("protected", []))
    for path in sorted(removed):
        problems.append("protected path '{}' was removed".format(path))
    for key in ("lint_on_edit", "feature_list"):
        if key in old_config and new_config.get(key) != old_config.get(key):
            problems.append("setting '{}' was changed".format(key))
    return problems


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def tail(text, lines=OUTPUT_TAIL_LINES):
    parts = (text or "").rstrip().splitlines()
    if len(parts) <= lines:
        return "\n".join(parts)
    return "[... {} earlier lines cut ...]\n".format(len(parts) - lines) + "\n".join(parts[-lines:])


def run_check(root, check):
    """Run one check. Return (passed, report_text)."""
    name = check.get("name", "unnamed check")
    command = check.get("command")
    if not command:
        return False, "Check '{}' has no command.".format(name)
    timeout = int(check.get("timeout_seconds", 600))
    try:
        result = subprocess.run(
            command, shell=True, cwd=root, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return False, "Check '{}' timed out after {} seconds: {}".format(name, timeout, command)
    if result.returncode == 0:
        return True, ""
    output = tail((result.stdout or "") + "\n" + (result.stderr or ""))
    return False, "Check '{}' failed (exit {}): {}\n{}".format(name, result.returncode, command, output)


# ---------------------------------------------------------------------------
# Hook input and output
# ---------------------------------------------------------------------------

def read_hook_input():
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def block(message):
    """Exit code 2: Claude Code shows stderr to Claude and blocks the action or the stop."""
    sys.stderr.write(message.rstrip() + "\n")
    sys.exit(2)


# ---------------------------------------------------------------------------
# User-only commands
# ---------------------------------------------------------------------------

def _user_unlock(root, target):
    config, error = load_config(root)
    if error or config is None:
        print(error or "No .claude/verify.json in this project.")
        return 1
    relative = rel_path(root, target) or target
    config["protected"] = [p for p in config.get("protected", []) if p != relative]
    write_json_file(os.path.join(root, CONFIG_REL), config)
    lock, _ = load_json_file(os.path.join(root, LOCK_REL))
    if lock:
        lock.get("hashes", {}).pop(relative, None)
        lock["config_snapshot"] = config
        write_json_file(os.path.join(root, LOCK_REL), lock)
    print("Unprotected {}.".format(relative))
    return 0


def _user_relock(root):
    lock_path = os.path.join(root, LOCK_REL)
    if os.path.exists(lock_path):
        os.remove(lock_path)
    print("Removed the lock. The next Stop hook run records the current state of every protected file.")
    return 0


def main(argv):
    root = project_dir()
    if len(argv) == 3 and argv[1] == "unlock":
        return _user_unlock(root, argv[2])
    if len(argv) == 2 and argv[1] == "relock":
        return _user_relock(root)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
