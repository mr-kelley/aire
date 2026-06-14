"""Tests for `aire map` — the code coverage engine.

Governing spec: specs/tools/aire/map-spec.md (Test Strategy).
Stdlib unittest only (DEC-000016). Fixtures are plain temp trees; no git is
required (staleness degrades to null without it, which these tests rely on for
determinism).
"""

import io
import sys
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from aire.map import build_map, extract_units, resolve_bindings, run_map  # noqa: E402
from aire.config import load_config  # noqa: E402

CODE_BINDING = '[[coverage]]\nmodel = "code"\npaths = ["tools/aire/"]\n'


def _write(root, files):
    for rel, content in files.items():
        p = Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(content))


def _spec(title, covers):
    lines = "\n".join(f"  - {c}" for c in covers)
    return f"---\ntitle: {title}\ncovers:\n{lines}\nstatus: draft\n---\n\nbody\n"


def _run(root, action, as_json=False):
    buf = io.StringIO()
    code = run_map(action, as_json=as_json, repo_root=str(root), out=buf)
    return code, buf.getvalue()


class TestExtraction(unittest.TestCase):
    def test_public_symbols_become_units(self):
        src = """
            def public_fn():
                pass

            async def async_fn():
                pass

            def _private_fn():
                pass

            class Public:
                def method(self):
                    pass

                def _hidden(self):
                    pass

                def __init__(self):
                    pass

            class _Private:
                pass

            X = 1
        """
        ids = sorted(u.id for u in extract_units("p.py", textwrap.dedent(src)))
        self.assertEqual(ids, [
            "p.py:Public", "p.py:Public.method", "p.py:async_fn", "p.py:public_fn",
        ])

    def test_kinds(self):
        src = "def f():\n    pass\nclass C:\n    def m(self):\n        pass\n"
        kinds = {u.symbol: u.kind for u in extract_units("p.py", src)}
        self.assertEqual(kinds, {"f": "function", "C": "class", "C.m": "method"})

    def test_no_public_symbols_yields_no_units(self):
        src = "import os\n_X = 1\ndef _p():\n    pass\n"
        self.assertEqual(extract_units("p.py", src), [])


class TestCheck(unittest.TestCase):
    def test_whole_file_coverage_passes(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                ".aire/config.toml": CODE_BINDING,
                "tools/aire/a.py": "def foo():\n    pass\nclass Bar:\n    def m(self):\n        pass\n",
                "specs/a-spec.md": _spec("A", ["tools/aire/a.py"]),
            })
            code, out = _run(tmp, "check")
            self.assertEqual(code, 0, out)
            self.assertIn("OK", out)

    def test_symbol_coverage_leaves_sibling_uncovered(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                ".aire/config.toml": CODE_BINDING,
                "tools/aire/a.py": "def foo():\n    pass\ndef bar():\n    pass\n",
                "specs/a-spec.md": _spec("A", ["tools/aire/a.py:foo"]),
            })
            code, out = _run(tmp, "check")
            self.assertEqual(code, 1, out)
            self.assertIn("tools/aire/a.py:bar", out)
            self.assertNotIn("tools/aire/a.py:foo  (", out)

    def test_stale_declaration_is_a_finding(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                ".aire/config.toml": CODE_BINDING,
                "tools/aire/a.py": "def foo():\n    pass\n",
                # foo covered; ghost has no matching unit -> stale
                "specs/a-spec.md": _spec("A", ["tools/aire/a.py:foo", "tools/aire/a.py:ghost"]),
            })
            code, out = _run(tmp, "check")
            self.assertEqual(code, 1, out)
            self.assertIn("stale declarations", out)
            self.assertIn("tools/aire/a.py:ghost", out)

    def test_ownership_conflict_is_a_finding(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                ".aire/config.toml": CODE_BINDING,
                "tools/aire/a.py": "def foo():\n    pass\n",
                "specs/a-spec.md": _spec("A", ["tools/aire/a.py:foo"]),
                "specs/b-spec.md": _spec("B", ["tools/aire/a.py:foo"]),
            })
            code, out = _run(tmp, "check")
            self.assertEqual(code, 1, out)
            self.assertIn("ownership conflicts", out)
            self.assertIn("tools/aire/a.py:foo", out)

    def test_covers_entry_outside_binding_is_ignored(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                ".aire/config.toml": CODE_BINDING,
                "tools/aire/a.py": "def foo():\n    pass\n",
                # extra entry points outside tools/aire/ -> not this engine's concern
                "specs/a-spec.md": _spec("A", ["tools/aire/a.py", "tools/pyproject.toml"]),
            })
            code, out = _run(tmp, "check")
            self.assertEqual(code, 0, out)


class TestMisconfiguration(unittest.TestCase):
    def test_no_binding_fails_closed(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {".aire/config.toml": 'profile = "B"\n',
                         "tools/aire/a.py": "def foo():\n    pass\n"})
            code, _ = _run(tmp, "check")
            self.assertEqual(code, 2)

    def test_missing_binding_path_fails_closed(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {".aire/config.toml": '[[coverage]]\nmodel = "code"\npaths = ["tools/nope/"]\n'})
            code, _ = _run(tmp, "check")
            self.assertEqual(code, 2)

    def test_unimplemented_engine_fails_closed(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                ".aire/config.toml": '[[coverage]]\nmodel = "artifact"\nglobs = ["vms/*.xml"]\n',
                "vms/x.xml": "<domain/>\n",
            })
            code, _ = _run(tmp, "check")
            self.assertEqual(code, 2)

    def test_syntax_error_in_source_fails_closed(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                ".aire/config.toml": CODE_BINDING,
                "tools/aire/a.py": "def foo(:\n    pass\n",
            })
            code, _ = _run(tmp, "check")
            self.assertEqual(code, 2)


class TestReport(unittest.TestCase):
    def _fixture(self, tmp):
        _write(tmp, {
            ".aire/config.toml": CODE_BINDING,
            "tools/aire/a.py": "def foo():\n    pass\ndef bar():\n    pass\n",
            "tools/aire/b.py": "class C:\n    def m(self):\n        pass\n",
            "specs/a-spec.md": _spec("A", ["tools/aire/a.py"]),
            "specs/b-spec.md": _spec("B", ["tools/aire/b.py"]),
        })

    def test_json_is_deterministic(self):
        with TemporaryDirectory() as tmp:
            self._fixture(tmp)
            _, first = _run(tmp, "report", as_json=True)
            _, second = _run(tmp, "report", as_json=True)
            self.assertEqual(first, second)

    def test_json_ordering_is_path_then_symbol(self):
        with TemporaryDirectory() as tmp:
            self._fixture(tmp)
            code, out = _run(tmp, "report", as_json=True)
            self.assertEqual(code, 0)
            import json
            ids = [u["id"] for u in json.loads(out)["units"]]
            self.assertEqual(ids, sorted(ids))
            self.assertEqual(ids[0], "tools/aire/a.py:bar")  # a before b, bar before foo

    def test_markdown_report_renders(self):
        with TemporaryDirectory() as tmp:
            self._fixture(tmp)
            code, out = _run(tmp, "report")
            self.assertEqual(code, 0)
            self.assertIn("# Coverage Map", out)
            self.assertIn("`tools/aire/a.py:foo`", out)

    def test_report_is_read_only(self):
        with TemporaryDirectory() as tmp:
            self._fixture(tmp)
            before = {p: p.read_bytes() for p in Path(tmp).rglob("*") if p.is_file()}
            _run(tmp, "report", as_json=True)
            after = {p: p.read_bytes() for p in Path(tmp).rglob("*") if p.is_file()}
            self.assertEqual(before, after)


class TestBindingResolution(unittest.TestCase):
    def test_config_binding_loaded(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {".aire/config.toml": CODE_BINDING})
            cfg = load_config(Path(tmp))
            bindings = resolve_bindings(Path(tmp), cfg)
            self.assertEqual(len(bindings), 1)
            self.assertEqual(bindings[0].model, "code")
            self.assertEqual(bindings[0].paths, ["tools/aire/"])

    def test_build_map_counts_units(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                ".aire/config.toml": CODE_BINDING,
                "tools/aire/a.py": "def foo():\n    pass\n",
                "specs/a-spec.md": _spec("A", ["tools/aire/a.py"]),
            })
            cfg = load_config(Path(tmp))
            result = build_map(Path(tmp), resolve_bindings(Path(tmp), cfg))
            self.assertEqual(len(result.results), 1)
            self.assertFalse(result.findings)


if __name__ == "__main__":
    unittest.main()
