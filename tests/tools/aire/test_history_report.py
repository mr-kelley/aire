import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from aire.history_report import run_report  # noqa: E402
from aire.history import HistoryError  # noqa: E402


def _run(args, cwd, stdin=None):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True,
                          text=True, input=stdin).stdout.strip()


def _commit_file(d, path, content, msg):
    p = Path(d) / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    _run(["git", "add", "."], d)
    _run(["git", "commit", "-q", "-m", msg], d)


def _merge_branch(d, branch, path, content, msg):
    _run(["git", "checkout", "-q", "-b", branch], d)
    _commit_file(d, path, content, f"work on {branch}")
    _run(["git", "checkout", "-q", "main"], d)
    _run(["git", "merge", "--no-ff", "-q", "-m", msg, branch], d)
    return _run(["git", "rev-parse", "HEAD"], d)


def make_history_repo(d, with_finding=True):
    _run(["git", "init", "-b", "main", "-q"], d)
    _run(["git", "config", "user.email", "t@example.com"], d)
    _run(["git", "config", "user.name", "Test"], d)
    _commit_file(d, "README.md", "x", "init")

    # 1. code merge WITH a promotion record
    code_merge = _merge_branch(d, "feat-code", "tools/x.py", "print('x')\n", "Merge feat-code")
    payload = json.dumps({
        "sprint": "sprints/m/01.md", "specs": ["specs/a.md"],
        "tests": {"command": "python -m unittest", "outcome": "PASS", "sha": code_merge},
        "decisions": ["DEC-000001"], "notes": "n",
    }, sort_keys=True)
    _run(["git", "tag", "-a", "promote/code", code_merge, "-F", "-"], d, stdin=payload)

    # 2. docs-only recordless merge (expected, not a finding)
    _merge_branch(d, "docs-only", "docs/y.md", "doc\n", "Merge docs-only")

    # 3. code-changing recordless merge (the finding)
    if with_finding:
        _merge_branch(d, "feat-untracked", "tools/z.py", "print('z')\n", "Merge feat-untracked")
    return d


class TestSummary(unittest.TestCase):
    def test_classifies_finding_vs_docs(self):
        with tempfile.TemporaryDirectory() as d:
            make_history_repo(d)
            out = io.StringIO()
            rc = run_report(view="summary", ref="main", cwd=d, out=out)
            s = out.getvalue()
            self.assertIn("Tested promotions: 1", s)
            self.assertIn("findings): 1", s)
            self.assertEqual(rc, 1)                       # finding present
            self.assertIn("Merge feat-untracked", s)      # code merge surfaced
            self.assertNotIn("Merge docs-only", s)        # docs merge not a finding

    def test_no_findings_exit_zero(self):
        with tempfile.TemporaryDirectory() as d:
            make_history_repo(d, with_finding=False)
            out = io.StringIO()
            rc = run_report(view="summary", ref="main", cwd=d, out=out)
            self.assertEqual(rc, 0)
            self.assertIn("findings): 0", out.getvalue())
            self.assertIn("OK", out.getvalue())


class TestDetailAndChain(unittest.TestCase):
    def test_detail_includes_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            make_history_repo(d)
            out = io.StringIO()
            run_report(view="detail", ref="main", cwd=d, out=out)
            s = out.getvalue()
            self.assertIn("specs/a.md", s)
            self.assertIn("python -m unittest", s)
            self.assertIn("DEC-000001", s)

    def test_chain_renders_known_slug(self):
        with tempfile.TemporaryDirectory() as d:
            make_history_repo(d)
            out = io.StringIO()
            run_report(view="chain", slug="code", ref="main", cwd=d, out=out)
            self.assertIn("promote/code", out.getvalue())

    def test_chain_unknown_slug_raises(self):
        with tempfile.TemporaryDirectory() as d:
            make_history_repo(d)
            with self.assertRaises(HistoryError):
                run_report(view="chain", slug="nope", ref="main", cwd=d, out=io.StringIO())

    def test_decision_title_degrades_to_id(self):
        with tempfile.TemporaryDirectory() as d:
            make_history_repo(d)  # no claude/decisions log present
            out = io.StringIO()
            run_report(view="detail", ref="main", cwd=d, out=out)
            # ID shown, but no parenthetical title since the log is absent
            self.assertIn("DEC-000001", out.getvalue())
            self.assertNotIn("DEC-000001 (", out.getvalue())


class TestContract(unittest.TestCase):
    def test_json_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            make_history_repo(d)
            a, b = io.StringIO(), io.StringIO()
            run_report(ref="main", as_json=True, cwd=d, out=a)
            run_report(ref="main", as_json=True, cwd=d, out=b)
            self.assertEqual(a.getvalue(), b.getvalue())
            json.loads(a.getvalue())

    def test_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            make_history_repo(d)
            before = sorted(str(p.relative_to(d)) for p in Path(d).rglob("*")
                            if ".git" not in p.parts)
            run_report(ref="main", cwd=d, out=io.StringIO())
            after = sorted(str(p.relative_to(d)) for p in Path(d).rglob("*")
                           if ".git" not in p.parts)
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
