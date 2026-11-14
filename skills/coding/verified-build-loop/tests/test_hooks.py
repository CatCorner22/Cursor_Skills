"""Tests for the verified-build-loop hook scripts.

Each test builds a throwaway project, feeds a hook the same JSON that Claude Code sends
on stdin, and checks the exit code and messages. Run:  python3 -m unittest -v tests/test_hooks.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
PY = sys.executable


class Project:
    def __init__(self, config=None, features=None, install_hooks=True):
        self.root = tempfile.mkdtemp(prefix="vbl-project-")
        self.outside = tempfile.mkdtemp(prefix="vbl-outside-")  # counters live outside the project
        os.makedirs(os.path.join(self.root, ".claude", "hooks"))
        if install_hooks:
            for name in os.listdir(SCRIPTS):
                shutil.copy(os.path.join(SCRIPTS, name), os.path.join(self.root, ".claude", "hooks", name))
        if config is not None:
            self.write_json(".claude/verify.json", config)
        if features is not None:
            self.write_json("feature_list.json", features)

    def path(self, relative):
        return os.path.join(self.root, relative)

    def write(self, relative, text):
        os.makedirs(os.path.dirname(self.path(relative)) or self.root, exist_ok=True)
        with open(self.path(relative), "w", encoding="utf-8") as handle:
            handle.write(text)

    def write_json(self, relative, data):
        self.write(relative, json.dumps(data, indent=2))

    def read(self, relative):
        with open(self.path(relative), encoding="utf-8") as handle:
            return handle.read()

    def run_hook(self, script, payload):
        payload = dict(payload)
        payload.setdefault("cwd", self.root)
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.root)
        return subprocess.run(
            [PY, os.path.join(self.root, ".claude", "hooks", script)],
            input=json.dumps(payload), capture_output=True, text=True, env=env, timeout=120,
        )

    def counter(self, name):
        return os.path.join(self.outside, name)

    def count(self, name):
        try:
            with open(self.counter(name)) as handle:
                return len(handle.read().splitlines())
        except FileNotFoundError:
            return 0

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)
        shutil.rmtree(self.outside, ignore_errors=True)


def base_features():
    return {"features": [
        {"id": "F001", "description": "User can log in", "steps": ["open /login", "submit"], "passes": False},
        {"id": "F002", "description": "User can log out", "steps": ["click log out"], "passes": False},
    ]}


def base_config(project, fast_ok=True, full_ok=True):
    fast = "echo run >> {}{}".format(project.counter("fast"), "" if fast_ok else " && echo 'AssertionError: expected 3' && exit 1")
    full = "echo run >> {}{}".format(project.counter("full"), "" if full_ok else " && echo 'E2E failed: login button missing' && exit 1")
    return {
        "fast_checks": [{"name": "unit", "command": fast, "timeout_seconds": 60}],
        "full_checks": [{"name": "e2e", "command": full, "timeout_seconds": 60}],
        "protected": ["tests/test_login.py"],
        "feature_list": "feature_list.json",
    }


def edit(path, old, new, replace_all=False):
    return {"tool_name": "Edit", "tool_input": {"file_path": path, "old_string": old, "new_string": new, "replace_all": replace_all}}


def write(path, content):
    return {"tool_name": "Write", "tool_input": {"file_path": path, "content": content}}


def bash(command):
    return {"tool_name": "Bash", "tool_input": {"command": command}}


class ProtectPathsTests(unittest.TestCase):
    def setUp(self):
        self.p = Project(features=base_features())
        self.p.write_json(".claude/verify.json", base_config(self.p))
        self.p.write("tests/test_login.py", "def test_login():\n    assert login() == 3\n")
        self.p.write("src/app.py", "def login():\n    return 3\n")

    def tearDown(self):
        self.p.cleanup()

    def pre(self, payload):
        return self.p.run_hook("protect_paths.py", payload)

    def assertBlocked(self, result, text=None):
        self.assertEqual(result.returncode, 2, result.stderr)
        if text:
            self.assertIn(text, result.stderr)

    def assertAllowed(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_not_set_up_allows_everything(self):
        os.remove(self.p.path(".claude/verify.json"))
        self.assertAllowed(self.pre(write(self.p.path("tests/test_login.py"), "x")))

    def test_ordinary_source_edit_allowed(self):
        self.assertAllowed(self.pre(edit(self.p.path("src/app.py"), "return 3", "return 4")))

    def test_protected_test_write_blocked(self):
        self.assertBlocked(self.pre(write(self.p.path("tests/test_login.py"), "def test_login():\n    pass\n")), "is protected")

    def test_protected_test_relative_path_blocked(self):
        self.assertBlocked(self.pre(edit("tests/test_login.py", "== 3", "== 3 or True")))

    def test_new_unprotected_test_allowed(self):
        self.assertAllowed(self.pre(write(self.p.path("tests/test_logout.py"), "def test_logout():\n    assert True\n")))

    def test_hook_files_and_settings_blocked(self):
        self.assertBlocked(self.pre(write(self.p.path(".claude/hooks/stop_check.py"), "")))
        self.assertBlocked(self.pre(write(self.p.path(".claude/settings.json"), "{}")))
        self.assertBlocked(self.pre(write(self.p.path(".claude/verify-lock.json"), "{}")))
        self.assertBlocked(self.pre(write(self.p.path(".claude/agents/reviewer.md"), "")))

    def test_feature_flip_passes_allowed(self):
        old = self.p.read("feature_list.json")
        first = old.index('"passes": false')
        new_text = old[:first] + '"passes": true' + old[first + len('"passes": false'):]
        self.assertAllowed(self.pre(write(self.p.path("feature_list.json"), new_text)))

    def test_feature_flip_passes_with_edit_allowed(self):
        old = self.p.read("feature_list.json")
        snippet = '"description": "User can log in",\n      "steps": [\n        "open /login",\n        "submit"\n      ],\n      "passes": false'
        self.assertIn(snippet, old)
        self.assertAllowed(self.pre(edit(self.p.path("feature_list.json"), snippet, snippet.replace("false", "true"))))

    def test_feature_description_change_blocked(self):
        self.assertBlocked(self.pre(edit(self.p.path("feature_list.json"), "User can log in", "User sees login page")),
                           "changed a field other than 'passes'")

    def test_feature_removal_blocked(self):
        data = base_features()
        data["features"].pop()
        self.assertBlocked(self.pre(write(self.p.path("feature_list.json"), json.dumps(data))), "F002 was removed")

    def test_new_failing_feature_allowed_new_passing_feature_blocked(self):
        data = base_features()
        data["features"].append({"id": "F003", "description": "Reset password", "steps": [], "passes": False})
        self.assertAllowed(self.pre(write(self.p.path("feature_list.json"), json.dumps(data))))
        data["features"][-1]["passes"] = True
        self.assertBlocked(self.pre(write(self.p.path("feature_list.json"), json.dumps(data))), "must start with")

    def test_feature_list_invalid_json_blocked(self):
        self.assertBlocked(self.pre(write(self.p.path("feature_list.json"), "{not json")), "would not be valid JSON")

    def test_edit_with_missing_old_string_allowed(self):
        self.assertAllowed(self.pre(edit(self.p.path("feature_list.json"), "text that is not there", "x")))

    def test_config_add_protected_allowed(self):
        config = base_config(self.p)
        config["protected"].append("tests/test_logout.py")
        self.assertAllowed(self.pre(write(self.p.path(".claude/verify.json"), json.dumps(config))))

    def test_config_add_check_allowed(self):
        config = base_config(self.p)
        config["fast_checks"].append({"name": "typecheck", "command": "true"})
        self.assertAllowed(self.pre(write(self.p.path(".claude/verify.json"), json.dumps(config))))

    def test_config_remove_protected_blocked(self):
        config = base_config(self.p)
        config["protected"] = []
        self.assertBlocked(self.pre(write(self.p.path(".claude/verify.json"), json.dumps(config))), "was removed")

    def test_config_weaken_check_blocked(self):
        config = base_config(self.p)
        config["fast_checks"][0]["command"] = "true"
        self.assertBlocked(self.pre(write(self.p.path(".claude/verify.json"), json.dumps(config))), "removed or changed")

    def test_bash_reads_allowed(self):
        for command in ["cat tests/test_login.py", "python3 -m pytest tests/test_login.py 2>&1 | tail -5",
                        "grep -n passes feature_list.json", "echo hi > out.txt", "ls -la .claude",
                        "npm test > /dev/null 2>&1"]:
            self.assertAllowed(self.pre(bash(command)))

    def test_bash_writes_to_protected_blocked(self):
        for command in ["rm tests/test_login.py", "echo x > tests/test_login.py",
                        "sed -i 's/3/4/' tests/test_login.py", "sed -i 's/false/true/' feature_list.json",
                        "git checkout -- tests/test_login.py", "rm -rf .claude", "mv tests tests_old",
                        "cat /dev/null >> {}".format(self.p.path("tests/test_login.py")),
                        "python3 -c \"open('feature_list.json','w').write('{}')\""]:
            self.assertBlocked(self.pre(bash(command)))

    def test_bash_user_only_commands_blocked(self):
        self.assertBlocked(self.pre(bash("python3 .claude/hooks/vbl_common.py unlock tests/test_login.py")), "user-only")
        self.assertBlocked(self.pre(bash("python3 .claude/hooks/vbl_common.py relock")), "user-only")

    def test_glob_protected_pattern(self):
        config = base_config(self.p)
        config["protected"] = ["tests/*"]
        self.p.write_json(".claude/verify.json", config)
        self.assertBlocked(self.pre(write(self.p.path("tests/sub/test_deep.py"), "")))
        self.assertBlocked(self.pre(bash("rm tests/test_login.py")))
        self.assertAllowed(self.pre(bash("pytest tests")))


class StopCheckTests(unittest.TestCase):
    def setUp(self):
        self.p = Project(features=base_features())
        self.p.write("tests/test_login.py", "def test_login():\n    assert True\n")
        self.p.write("src/app.py", "x = 1\n")

    def tearDown(self):
        self.p.cleanup()

    def stop(self, active=False):
        return self.p.run_hook("stop_check.py", {"hook_event_name": "Stop", "stop_hook_active": active,
                                                 "last_assistant_message": "Done."})

    def configure(self, **kwargs):
        self.p.write_json(".claude/verify.json", base_config(self.p, **kwargs))

    def touch_source(self):
        time.sleep(0.01)
        with open(self.p.path("src/app.py"), "a") as handle:
            handle.write("# change\n")

    def flip(self, feature_id):
        data = json.loads(self.p.read("feature_list.json"))
        for feature in data["features"]:
            if feature["id"] == feature_id:
                feature["passes"] = True
        self.p.write_json("feature_list.json", data)

    def test_not_set_up(self):
        self.assertEqual(self.stop().returncode, 0)

    def test_pass_creates_lock_and_skips_when_unchanged(self):
        self.configure()
        self.assertEqual(self.stop().returncode, 0)
        self.assertTrue(os.path.exists(self.p.path(".claude/verify-lock.json")))
        self.assertEqual(self.p.count("fast"), 1)
        self.assertEqual(self.stop().returncode, 0)
        self.assertEqual(self.p.count("fast"), 1, "unchanged project should skip the checks")
        self.touch_source()
        self.assertEqual(self.stop().returncode, 0)
        self.assertEqual(self.p.count("fast"), 2, "changed project should rerun the checks")
        self.assertEqual(self.p.count("full"), 0, "full checks run only when a feature passes")

    def test_failing_fast_check_blocks_with_output(self):
        self.configure(fast_ok=False)
        result = self.stop()
        self.assertEqual(result.returncode, 2)
        self.assertIn("AssertionError: expected 3", result.stderr)
        self.assertIn("checks failed", result.stderr)

    def test_repeated_identical_failure_releases_with_user_message(self):
        self.configure(fast_ok=False)
        self.assertEqual(self.stop().returncode, 2)
        self.assertEqual(self.stop(active=True).returncode, 2)
        third = self.stop(active=True)
        self.assertEqual(third.returncode, 0)
        self.assertIn("systemMessage", third.stdout)
        self.assertIn("failed 3 times", third.stdout)

    def test_repeat_counter_ignores_changing_durations(self):
        config = base_config(self.p)
        config["fast_checks"] = [{"name": "unit", "command":
            "python3 -c \"import time; print('1 failed in %.4fs' % time.time()); raise SystemExit(1)\""}]
        self.p.write_json(".claude/verify.json", config)
        self.assertEqual(self.stop().returncode, 2)
        self.assertEqual(self.stop(active=True).returncode, 2)
        self.assertEqual(self.stop(active=True).returncode, 0)

    def test_repeat_counter_needs_stop_hook_active(self):
        self.configure(fast_ok=False)
        for _ in range(4):
            self.assertEqual(self.stop(active=False).returncode, 2)

    def test_flipping_passes_runs_full_checks(self):
        self.configure()
        self.assertEqual(self.stop().returncode, 0)
        self.flip("F001")
        self.assertEqual(self.stop().returncode, 0)
        self.assertEqual(self.p.count("full"), 1)
        self.assertEqual(self.stop().returncode, 0)
        self.assertEqual(self.p.count("full"), 1, "full checks should not rerun once accepted")

    def test_flipping_passes_with_failing_full_check_blocks_until_fixed(self):
        self.configure(full_ok=False)
        self.assertEqual(self.stop().returncode, 0)
        self.flip("F001")
        result = self.stop()
        self.assertEqual(result.returncode, 2)
        self.assertIn("F001", result.stderr)
        self.assertIn("login button missing", result.stderr)
        self.assertEqual(self.stop().returncode, 2, "full checks must run again on the next stop")

    def test_protected_file_change_blocks(self):
        self.configure()
        self.assertEqual(self.stop().returncode, 0)
        self.p.write("tests/test_login.py", "def test_login():\n    pass\n")
        result = self.stop()
        self.assertEqual(result.returncode, 2)
        self.assertIn("protected file 'tests/test_login.py' changed", result.stderr)

    def test_protected_file_deleted_blocks(self):
        self.configure()
        self.assertEqual(self.stop().returncode, 0)
        os.remove(self.p.path("tests/test_login.py"))
        self.assertIn("is missing", self.stop().stderr)

    def test_hook_file_tampering_blocks(self):
        self.configure()
        self.assertEqual(self.stop().returncode, 0)
        with open(self.p.path(".claude/hooks/protect_paths.py"), "a") as handle:
            handle.write("\n# disabled\n")
        self.assertIn(".claude/hooks/protect_paths.py", self.stop().stderr)

    def test_check_removed_outside_file_tools_blocks(self):
        self.configure()
        self.assertEqual(self.stop().returncode, 0)
        config = base_config(self.p)
        config["fast_checks"] = []
        self.p.write_json(".claude/verify.json", config)
        self.assertIn("was removed or changed", self.stop().stderr)

    def test_feature_rewritten_outside_file_tools_blocks(self):
        self.configure()
        self.assertEqual(self.stop().returncode, 0)
        data = base_features()
        data["features"][0]["steps"] = []
        self.p.write_json("feature_list.json", data)
        self.assertIn("changed a field other than 'passes'", self.stop().stderr)

    def test_user_relock_accepts_new_protected_content(self):
        self.configure()
        self.assertEqual(self.stop().returncode, 0)
        self.p.write("tests/test_login.py", "def test_login():\n    assert 1 == 1\n")
        self.assertEqual(self.stop().returncode, 2)
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.p.root)
        subprocess.run([PY, self.p.path(".claude/hooks/vbl_common.py"), "relock"], env=env, check=True, capture_output=True)
        self.assertEqual(self.stop().returncode, 0)

    def test_user_unlock_removes_protection(self):
        self.configure()
        self.assertEqual(self.stop().returncode, 0)
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.p.root)
        subprocess.run([PY, self.p.path(".claude/hooks/vbl_common.py"), "unlock", "tests/test_login.py"],
                       env=env, check=True, capture_output=True)
        self.assertNotIn("tests/test_login.py", json.loads(self.p.read(".claude/verify.json"))["protected"])
        self.p.write("tests/test_login.py", "def test_login():\n    assert 2 == 2\n")
        self.assertEqual(self.stop().returncode, 0)

    def test_broken_config_json_blocks(self):
        self.p.write(".claude/verify.json", "{oops")
        self.assertIn("not valid JSON", self.stop().stderr)

    def test_timeout_reported(self):
        config = base_config(self.p)
        config["fast_checks"] = [{"name": "slow", "command": "sleep 5", "timeout_seconds": 1}]
        self.p.write_json(".claude/verify.json", config)
        result = self.stop()
        self.assertEqual(result.returncode, 2)
        self.assertIn("timed out after 1 seconds", result.stderr)


class PostEditLintTests(unittest.TestCase):
    def setUp(self):
        self.p = Project()
        config = base_config(self.p)
        config["lint_on_edit"] = {
            "command": "grep -q 'TODO' {file} && echo 'lint: TODO found' && exit 1 || exit 0",
            "extensions": [".py"],
        }
        self.p.write_json(".claude/verify.json", config)

    def tearDown(self):
        self.p.cleanup()

    def post(self, relative):
        return self.p.run_hook("post_edit_lint.py", {"hook_event_name": "PostToolUse", "tool_name": "Write",
                                                     "tool_input": {"file_path": self.p.path(relative)}})

    def test_clean_file_passes(self):
        self.p.write("src/ok.py", "x = 1\n")
        self.assertEqual(self.post("src/ok.py").returncode, 0)

    def test_lint_error_reported(self):
        self.p.write("src/bad.py", "# TODO fix\n")
        result = self.post("src/bad.py")
        self.assertEqual(result.returncode, 2)
        self.assertIn("lint: TODO found", result.stderr)

    def test_other_extension_skipped(self):
        self.p.write("notes.md", "TODO\n")
        self.assertEqual(self.post("notes.md").returncode, 0)

    def test_file_name_with_space(self):
        self.p.write("src/my file.py", "# TODO\n")
        self.assertEqual(self.post("src/my file.py").returncode, 2)

    def test_no_lint_setting(self):
        self.p.write_json(".claude/verify.json", base_config(self.p))
        self.p.write("src/bad.py", "# TODO\n")
        self.assertEqual(self.post("src/bad.py").returncode, 0)


if __name__ == "__main__":
    unittest.main()
