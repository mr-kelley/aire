"""Tests for `aire digest` — the derived constraints digest.

Governing spec: specs/tools/aire/digest-spec.md (Test Strategy). The digest is
a derived artifact: owning specs declare `digest:` clauses; `render` emits the
canonical file, `check` regenerates and compares (fail closed). Stdlib unittest
only (DEC-000016); fixtures are plain temp trees.
"""

import io
import sys
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from aire.digest import (  # noqa: E402
    DIGEST_REL, DigestError, run_digest, collect_clauses,
    render_digest, _front_matter_digest,
)


def _write(root, files):
    for rel, content in files.items():
        p = Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(content))


def _spec(*clauses):
    block = "\n".join(f'  - "{c}"' for c in clauses)
    return f"---\ntitle: S\ndigest:\n{block}\n---\n\nbody\n"


def _render(tmp):
    buf = io.StringIO()
    code = run_digest("render", repo_root=str(tmp), out=buf)
    return code, buf.getvalue()


def _check(tmp):
    buf = io.StringIO()
    code = run_digest("check", repo_root=str(tmp), out=buf)
    return code, buf.getvalue()


def _regen(tmp):
    """Write the committed digest from a render (the canonical maintenance step)."""
    _, text = _render(tmp)
    (Path(tmp) / DIGEST_REL).parent.mkdir(parents=True, exist_ok=True)
    (Path(tmp) / DIGEST_REL).write_text(text)


class TestParse(unittest.TestCase):
    def test_block_list_clauses(self):
        self.assertEqual(
            _front_matter_digest('---\ntitle: x\ndigest:\n  - "a"\n  - "b"\n---\n'),
            ["a", "b"],
        )

    def test_no_block_is_empty(self):
        self.assertEqual(_front_matter_digest("---\ntitle: x\n---\n"), [])

    def test_inline_value_is_malformed(self):
        with self.assertRaises(DigestError):
            _front_matter_digest("---\ndigest: not-a-list\n---\n")

    def test_block_ends_at_next_key(self):
        txt = '---\ndigest:\n  - "a"\ntitle: x\n---\n'
        self.assertEqual(_front_matter_digest(txt), ["a"])


class TestRender(unittest.TestCase):
    def test_clause_appears_with_owning_spec(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/a-spec.md": _spec("rule one")})
            code, text = _render(tmp)
            self.assertEqual(code, 0)
            self.assertIn("- rule one — `claude/a-spec.md`", text)

    def test_spec_without_block_contributes_nothing(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                "claude/a-spec.md": _spec("rule one"),
                "claude/b-spec.md": "---\ntitle: B\n---\n\nno digest here\n",
            })
            _, text = _render(tmp)
            self.assertEqual(text.count("\n- "), 1)

    def test_ordering_spec_path_then_declaration(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                "specs/b-spec.md": _spec("b-first", "b-second"),
                "specs/a-spec.md": _spec("a-only"),
            })
            _, text = _render(tmp)
            order = [ln for ln in text.splitlines() if ln.startswith("- ")]
            self.assertEqual(
                order,
                [
                    "- a-only — `specs/a-spec.md`",
                    "- b-first — `specs/b-spec.md`",
                    "- b-second — `specs/b-spec.md`",
                ],
            )

    def test_deterministic(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/a-spec.md": _spec("one", "two"),
                         "specs/c-spec.md": _spec("three")})
            _, a = _render(tmp)
            _, b = _render(tmp)
            self.assertEqual(a, b)

    def test_malformed_block_fails_closed(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/a-spec.md": "---\ndigest: oops\n---\n"})
            code, _ = _render(tmp)
            self.assertEqual(code, 2)


class TestCheck(unittest.TestCase):
    def test_match_passes(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/a-spec.md": _spec("rule one", "rule two")})
            _regen(tmp)
            code, out = _check(tmp)
            self.assertEqual(code, 0, out)
            self.assertIn("OK", out)

    def test_added_clause_is_drift(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/a-spec.md": _spec("rule one")})
            _regen(tmp)
            _write(tmp, {"claude/a-spec.md": _spec("rule one", "rule two")})
            code, out = _check(tmp)
            self.assertEqual(code, 1)
            self.assertIn("rule two", out)

    def test_removed_clause_is_drift(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/a-spec.md": _spec("rule one", "rule two")})
            _regen(tmp)
            _write(tmp, {"claude/a-spec.md": _spec("rule one")})
            code, _ = _check(tmp)
            self.assertEqual(code, 1)

    def test_edited_clause_is_drift(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/a-spec.md": _spec("rule one")})
            _regen(tmp)
            _write(tmp, {"claude/a-spec.md": _spec("rule ONE")})
            code, out = _check(tmp)
            self.assertEqual(code, 1)
            self.assertIn("rule ONE", out)

    def test_missing_digest_file_fails_closed(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/a-spec.md": _spec("rule one")})
            code, _ = _check(tmp)  # never wrote the committed digest
            self.assertEqual(code, 2)

    def test_malformed_block_fails_closed(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/a-spec.md": _spec("rule one")})
            _regen(tmp)
            _write(tmp, {"claude/a-spec.md": "---\ndigest: oops\n---\n"})
            code, _ = _check(tmp)
            self.assertEqual(code, 2)


class TestContract(unittest.TestCase):
    def test_no_action_is_usage_error(self):
        with TemporaryDirectory() as tmp:
            code = run_digest("bogus", repo_root=str(tmp), out=io.StringIO())
            self.assertEqual(code, 2)

    def test_digest_file_is_not_a_source(self):
        # a stray `digest:` block in the output file must not feed back in
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/a-spec.md": _spec("rule one")})
            _regen(tmp)
            self.assertEqual([c.text for c in collect_clauses(Path(tmp))], ["rule one"])

    def test_read_only(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/a-spec.md": _spec("rule one")})
            _regen(tmp)
            before = {p: p.read_bytes() for p in Path(tmp).rglob("*") if p.is_file()}
            _check(tmp)
            _render(tmp)
            after = {p: p.read_bytes() for p in Path(tmp).rglob("*") if p.is_file()}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
