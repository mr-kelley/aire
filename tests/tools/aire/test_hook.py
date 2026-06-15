"""Tests for `aire hook` — the Layer 2 PreToolUse enforcement primitive.

Governing spec: specs/tools/aire/hook-spec.md (Test Strategy). The hook reads a
tool-call event on stdin, evaluates the repo's .aire/config.toml [harness] typed
policy, and returns an exit code (0 allow / 2 block), fail-closed on guard error.
Stdlib unittest only (DEC-000016); fixtures are plain temp trees.
"""

import io
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from aire.hook import ALLOW, BLOCK, run_hook  # noqa: E402


def _run(root, event, policy_toml=None):
    """Write an optional [harness] policy, feed `event` on stdin, return the exit code."""
    if policy_toml is not None:
        cfg = Path(root) / ".aire" / "config.toml"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text(policy_toml)
    stdin = io.StringIO(json.dumps(event) if not isinstance(event, str) else event)
    # silence the stderr reason during tests
    err, sys.stderr = sys.stderr, io.StringIO()
    try:
        return run_hook(repo=str(root), stdin=stdin)
    finally:
        sys.stderr = err


def _bash(command):
    return {"tool_name": "Bash", "tool_input": {"command": command}}


def _write_tool(tool_name, path):
    key = "notebook_path" if tool_name == "NotebookEdit" else "file_path"
    return {"tool_name": tool_name, "tool_input": {key: path}}


PUSH_HUMAN_ONLY = '[harness.push_policy]\nmode = "human-only"\n'
PROTECTED = '[harness.protected_paths]\ndeny = ["operator.md", "private/**", ".claude/settings.json"]\n'


class TestPushPolicy(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_denies_bare_push(self):
        self.assertEqual(_run(self.root, _bash("git push"), PUSH_HUMAN_ONLY), BLOCK)

    def test_denies_push_with_args(self):
        self.assertEqual(_run(self.root, _bash("git push origin main"), PUSH_HUMAN_ONLY), BLOCK)

    def test_denies_push_with_dash_C(self):
        self.assertEqual(_run(self.root, _bash("git -C /x push"), PUSH_HUMAN_ONLY), BLOCK)

    def test_denies_push_with_dash_c(self):
        self.assertEqual(_run(self.root, _bash("git -c k=v push origin"), PUSH_HUMAN_ONLY), BLOCK)

    def test_denies_chained_push(self):
        self.assertEqual(_run(self.root, _bash("cd x && git push"), PUSH_HUMAN_ONLY), BLOCK)

    def test_denies_env_prefixed_push(self):
        self.assertEqual(_run(self.root, _bash("GIT_TRACE=1 git push"), PUSH_HUMAN_ONLY), BLOCK)

    def test_allows_git_status(self):
        self.assertEqual(_run(self.root, _bash("git status"), PUSH_HUMAN_ONLY), ALLOW)

    def test_allows_git_log(self):
        self.assertEqual(_run(self.root, _bash("git log --oneline -5"), PUSH_HUMAN_ONLY), ALLOW)

    def test_allows_echo_of_git_push(self):
        # argv parsing, not substring: command word is `echo`
        self.assertEqual(_run(self.root, _bash('echo "git push"'), PUSH_HUMAN_ONLY), ALLOW)

    def test_allows_echogit_push(self):
        self.assertEqual(_run(self.root, _bash("echogit push"), PUSH_HUMAN_ONLY), ALLOW)

    def test_push_allowed_when_policy_absent(self):
        self.assertEqual(_run(self.root, _bash("git push"), PROTECTED), ALLOW)

    def test_mode_off_allows_push(self):
        self.assertEqual(
            _run(self.root, _bash("git push"), '[harness.push_policy]\nmode = "off"\n'), ALLOW
        )


class TestProtectedPaths(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_denies_write_to_protected_file(self):
        self.assertEqual(_run(self.root, _write_tool("Write", "operator.md"), PROTECTED), BLOCK)

    def test_denies_edit_to_protected_file(self):
        self.assertEqual(_run(self.root, _write_tool("Edit", "operator.md"), PROTECTED), BLOCK)

    def test_denies_nested_glob_match(self):
        self.assertEqual(
            _run(self.root, _write_tool("MultiEdit", "private/sub/secret.txt"), PROTECTED), BLOCK
        )

    def test_denies_notebook_edit_to_protected(self):
        self.assertEqual(
            _run(self.root, _write_tool("NotebookEdit", ".claude/settings.json"), PROTECTED), BLOCK
        )

    def test_denies_absolute_path_inside_repo(self):
        event = _write_tool("Write", str(Path(self.root) / "operator.md"))
        self.assertEqual(_run(self.root, event, PROTECTED), BLOCK)

    def test_allows_write_elsewhere(self):
        self.assertEqual(_run(self.root, _write_tool("Write", "README.md"), PROTECTED), ALLOW)

    def test_allows_write_outside_repo(self):
        self.assertEqual(_run(self.root, _write_tool("Write", "/tmp/elsewhere.md"), PROTECTED), ALLOW)

    def test_bash_best_effort_redirect_to_protected(self):
        self.assertEqual(_run(self.root, _bash("echo x > operator.md"), PROTECTED), BLOCK)

    def test_bash_allows_redirect_elsewhere(self):
        self.assertEqual(_run(self.root, _bash("echo x > notes.md"), PROTECTED), ALLOW)


class TestFailClosed(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_config_allows(self):
        self.assertEqual(_run(self.root, _bash("git push"), None), ALLOW)

    def test_no_harness_section_allows(self):
        self.assertEqual(_run(self.root, _bash("git push"), 'profile = "B"\n'), ALLOW)

    def test_malformed_toml_blocks(self):
        self.assertEqual(_run(self.root, _bash("git push"), "[harness.push_policy\nmode = x"), BLOCK)

    def test_unknown_constraint_blocks(self):
        self.assertEqual(
            _run(self.root, _bash("ls"), '[harness.no_such_thing]\nx = 1\n'), BLOCK
        )

    def test_bad_mode_blocks(self):
        self.assertEqual(
            _run(self.root, _bash("git push"), '[harness.push_policy]\nmode = "shout"\n'), BLOCK
        )

    def test_bad_deny_type_blocks(self):
        self.assertEqual(
            _run(self.root, _write_tool("Write", "x"), '[harness.protected_paths]\ndeny = "operator.md"\n'),
            BLOCK,
        )

    def test_non_json_stdin_blocks(self):
        self.assertEqual(_run(self.root, "not json at all", PUSH_HUMAN_ONLY), BLOCK)

    def test_json_array_blocks(self):
        self.assertEqual(_run(self.root, "[1, 2, 3]", PUSH_HUMAN_ONLY), BLOCK)

    def test_unrestricted_tool_allows(self):
        event = {"tool_name": "Read", "tool_input": {"file_path": "operator.md"}}
        self.assertEqual(_run(self.root, event, PUSH_HUMAN_ONLY + PROTECTED), ALLOW)

    def test_missing_tool_input_allows(self):
        self.assertEqual(_run(self.root, {"tool_name": "Bash"}, PUSH_HUMAN_ONLY), ALLOW)


if __name__ == "__main__":
    unittest.main()
