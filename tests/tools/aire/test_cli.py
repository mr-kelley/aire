import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from aire import cli  # noqa: E402
from aire.doctor import run_doctor  # noqa: E402


class TestDispatch(unittest.TestCase):
    def test_no_subcommand_prints_help_exit_zero(self):
        out = io.StringIO()
        saved, sys.stdout = sys.stdout, out
        try:
            rc = cli.main([])
        finally:
            sys.stdout = saved
        self.assertEqual(rc, 0)
        self.assertIn("aire", out.getvalue())

    def test_version_exits_zero(self):
        with self.assertRaises(SystemExit) as cm:
            cli.main(["--version"])
        self.assertEqual(cm.exception.code, 0)

    def test_unknown_subcommand_exits_two(self):
        saved, sys.stderr = sys.stderr, io.StringIO()
        try:
            with self.assertRaises(SystemExit) as cm:
                cli.main(["frobnicate"])
        finally:
            sys.stderr = saved
        self.assertEqual(cm.exception.code, 2)

    def test_doctor_dispatches(self):
        out = io.StringIO()
        repo = Path(__file__).resolve().parents[3]
        rc = run_doctor(repo_root=str(repo), out=out)
        self.assertIn(rc, (0, 1))
        self.assertIn("ok", out.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
