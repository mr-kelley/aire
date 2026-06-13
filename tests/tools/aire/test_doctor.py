import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from aire.doctor import (  # noqa: E402
    build_context,
    default_checks,
    run_checks,
    run_doctor,
)


def make_repo(d, *, git=True, config=None, governance=True, state=True):
    d = Path(d)
    if git:
        (d / ".git").mkdir()
    if config is not None:
        (d / ".aire").mkdir()
        (d / ".aire" / "config.toml").write_text(config)
    if governance:
        (d / "claude").mkdir()
        (d / "claude" / "claude.role.base.md").write_text("x")
        (d / "claude" / "spec-spec.md").write_text("x")
    if state:
        (d / "STATE.md").write_text("x")
    return d


class TestDoctorExitCodes(unittest.TestCase):
    def _run(self, **kw):
        with tempfile.TemporaryDirectory() as d:
            make_repo(d, **kw)
            out = io.StringIO()
            rc = run_doctor(repo_root=d, out=out)
            return rc, out.getvalue()

    def test_clean_repo_exits_zero(self):
        rc, _ = self._run(
            config='aire_version_min = "0.1.0"\nprofile = "B"\nlocal_model_floor = 8192\n'
        )
        self.assertEqual(rc, 0)

    def test_absent_config_warns_not_fail(self):
        rc, _ = self._run(config=None)
        self.assertEqual(rc, 0)

    def test_no_git_fails(self):
        rc, out = self._run(git=False, config='profile = "B"\n')
        self.assertEqual(rc, 1)
        self.assertIn("FAIL", out)

    def test_version_pin_unsatisfied_fails(self):
        rc, _ = self._run(config='aire_version_min = "99.0.0"\n')
        self.assertEqual(rc, 1)

    def test_malformed_config_fails(self):
        rc, _ = self._run(config="[[[ not toml = =")
        self.assertEqual(rc, 1)

    def test_bad_profile_fails(self):
        rc, _ = self._run(config='profile = "Z"\n')
        self.assertEqual(rc, 1)


class TestDoctorDeterminismAndContract(unittest.TestCase):
    def test_json_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(d, config='profile = "B"\n')
            a, b = io.StringIO(), io.StringIO()
            run_doctor(repo_root=d, as_json=True, out=a)
            run_doctor(repo_root=d, as_json=True, out=b)
            self.assertEqual(a.getvalue(), b.getvalue())
            json.loads(a.getvalue())  # valid JSON

    def test_json_in_registration_order(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(d, config='profile = "B"\n')
            out = io.StringIO()
            run_doctor(repo_root=d, as_json=True, out=out)
            names = [item["name"] for item in json.loads(out.getvalue())]
            self.assertEqual(names, [n for n, _ in default_checks()])

    def test_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(d, config='profile = "B"\n')
            before = sorted(str(p.relative_to(d)) for p in Path(d).rglob("*"))
            run_doctor(repo_root=d, out=io.StringIO())
            after = sorted(str(p.relative_to(d)) for p in Path(d).rglob("*"))
            self.assertEqual(before, after)

    def test_registry_extensible(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(d, config='profile = "B"\n')
            ctx = build_context(repo_root=d)
            extra = default_checks() + [("dummy", lambda c: ("ok", "dummy ran"))]
            results = run_checks(ctx, checks=extra)
            self.assertIn(("dummy", "ok", "dummy ran"), results)


if __name__ == "__main__":
    unittest.main()
