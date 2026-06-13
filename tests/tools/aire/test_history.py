import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from aire import history  # noqa: E402
from aire.history import HistoryError  # noqa: E402


def _run(args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def init_repo(d, branch=None):
    d = Path(d)
    _run(["git", "init", "-q"], d)
    _run(["git", "config", "user.email", "t@example.com"], d)
    _run(["git", "config", "user.name", "Test"], d)
    (d / "f.txt").write_text("x")
    _run(["git", "add", "."], d)
    _run(["git", "commit", "-q", "-m", "init"], d)
    if branch:
        _run(["git", "checkout", "-q", "-b", branch], d)
    return d


def tag_message(slug_tag, cwd):
    # `git tag -n` truncates; read the full annotated message via cat-file
    return subprocess.run(
        ["git", "for-each-ref", "--format=%(contents)", f"refs/tags/{slug_tag}"],
        cwd=cwd, check=True, capture_output=True, text=True,
    ).stdout


class TestSlugInference(unittest.TestCase):
    def test_infer_from_work_branch(self):
        with tempfile.TemporaryDirectory() as d:
            init_repo(d, branch="work/2026-06-13T120000Z/my-slug")
            self.assertEqual(history.infer_slug(cwd=d), "my-slug")


class TestRecord(unittest.TestCase):
    def test_creates_tag_with_json_payload(self):
        with tempfile.TemporaryDirectory() as d:
            init_repo(d, branch="work/ts/demo")
            out = io.StringIO()
            rc = history.record(
                tests_command="python -m unittest", tests_outcome="PASS",
                sprint="sprints/x/01.md", specs=["specs/a.md"],
                decisions=["DEC-000001"], notes="hi", cwd=d, out=out,
            )
            self.assertEqual(rc, 0)
            msg = tag_message("promote/demo", d)
            payload = json.loads(msg)
            self.assertEqual(payload["tests"]["outcome"], "PASS")
            self.assertEqual(payload["sprint"], "sprints/x/01.md")
            self.assertEqual(payload["decisions"], ["DEC-000001"])
            self.assertEqual(len(payload["tests"]["sha"]), 40)  # full SHA

    def test_rn_uniqueness(self):
        with tempfile.TemporaryDirectory() as d:
            init_repo(d, branch="work/ts/demo")
            kw = dict(tests_command="t", tests_outcome="PASS", cwd=d, out=io.StringIO())
            history.record(**kw)
            history.record(**kw)
            tags = subprocess.run(
                ["git", "tag", "--list"], cwd=d, check=True,
                capture_output=True, text=True,
            ).stdout.split()
            self.assertIn("promote/demo", tags)
            self.assertIn("promote/demo-r2", tags)

    def test_na_outcome_accepted_without_command(self):
        with tempfile.TemporaryDirectory() as d:
            init_repo(d, branch="work/ts/docs")
            rc = history.record(tests_outcome="N/A", cwd=d, out=io.StringIO())
            self.assertEqual(rc, 0)

    def test_dry_run_creates_no_tag(self):
        with tempfile.TemporaryDirectory() as d:
            init_repo(d, branch="work/ts/demo")
            out = io.StringIO()
            history.record(tests_command="t", dry_run=True, cwd=d, out=out)
            tags = subprocess.run(
                ["git", "tag", "--list"], cwd=d, check=True,
                capture_output=True, text=True,
            ).stdout.split()
            self.assertEqual(tags, [])
            self.assertIn("would create", out.getvalue())


class TestValidation(unittest.TestCase):
    def test_bad_outcome_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            init_repo(d, branch="work/ts/demo")
            with self.assertRaises(HistoryError):
                history.record(tests_outcome="MAYBE", cwd=d, out=io.StringIO())

    def test_pass_without_command_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            init_repo(d, branch="work/ts/demo")
            with self.assertRaises(HistoryError):
                history.record(tests_outcome="PASS", tests_command=None,
                               cwd=d, out=io.StringIO())

    def test_rejection_creates_no_tag(self):
        with tempfile.TemporaryDirectory() as d:
            init_repo(d, branch="work/ts/demo")
            try:
                history.record(tests_outcome="PASS", tests_command=None,
                               cwd=d, out=io.StringIO())
            except HistoryError:
                pass
            tags = subprocess.run(
                ["git", "tag", "--list"], cwd=d, check=True,
                capture_output=True, text=True,
            ).stdout.split()
            self.assertEqual(tags, [])


if __name__ == "__main__":
    unittest.main()
