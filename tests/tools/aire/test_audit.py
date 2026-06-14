"""Tests for `aire audit` — the mechanical governance liveness checks.

Governing spec: specs/tools/aire/audit-spec.md (Test Strategy). Each mechanical
check gets pass / fail / not-applicable fixtures. Stdlib unittest only
(DEC-000016); fixtures are plain temp trees (no git — git-dependent checks
report na, which these tests assert).
"""

import io
import json
import sys
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from aire.audit import (  # noqa: E402
    AuditContext, run_audit, run_checks,
    _check_spec_index, _check_digest, _check_references, _check_pins,
    _check_inventory, _check_decision_log, _check_bindings, _check_coverage,
)
from aire.config import load_config  # noqa: E402

CODE_BINDING = '[[coverage]]\nmodel = "code"\npaths = ["tools/aire/"]\n'


def _write(root, files):
    for rel, content in files.items():
        p = Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(content))


def _ctx(tmp, is_git=False):
    root = Path(tmp)
    return AuditContext(root=root, config=load_config(root), is_git=is_git)


def _sev(findings):
    return [(f.check, f.severity) for f in findings]


class TestCoverage(unittest.TestCase):
    def test_pass(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                ".aire/config.toml": CODE_BINDING,
                "tools/aire/a.py": "def foo():\n    pass\n",
                "specs/a-spec.md": "---\ntitle: A\ncovers:\n  - tools/aire/a.py\n---\n",
            })
            self.assertEqual(_check_coverage(_ctx(tmp)), [])

    def test_uncovered_is_defect(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                ".aire/config.toml": CODE_BINDING,
                "tools/aire/a.py": "def foo():\n    pass\n",
                "specs/a-spec.md": "---\ntitle: A\ncovers:\n  - tools/aire/a.py:nope\n---\n",
            })
            sev = [f.severity for f in _check_coverage(_ctx(tmp))]
            self.assertIn("defect", sev)

    def test_no_binding_is_na(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {".aire/config.toml": 'profile = "B"\n'})
            out = _check_coverage(_ctx(tmp))
            self.assertEqual([f.severity for f in out], ["na"])


class TestSpecIndex(unittest.TestCase):
    def _index(self, rows):
        body = "| Path | Title | Description | Status |\n|---|---|---|---|\n"
        body += "".join(f"| `{r}` | T | d | draft |\n" for r in rows)
        return body

    def test_pass(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                "specs/a-spec.md": "x", "specs/b-spec.md": "y",
                "specs/INDEX.md": self._index(["specs/a-spec.md", "specs/b-spec.md"]),
            })
            self.assertEqual(_check_spec_index(_ctx(tmp)), [])

    def test_missing_from_index_is_defect(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                "specs/a-spec.md": "x", "specs/b-spec.md": "y",
                "specs/INDEX.md": self._index(["specs/a-spec.md"]),
            })
            out = _check_spec_index(_ctx(tmp))
            self.assertEqual([f.severity for f in out], ["defect"])
            self.assertIn("specs/b-spec.md", out[0].location)

    def test_unsorted_index_is_drift(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                "specs/a-spec.md": "x", "specs/b-spec.md": "y",
                "specs/INDEX.md": self._index(["specs/b-spec.md", "specs/a-spec.md"]),
            })
            sev = [f.severity for f in _check_spec_index(_ctx(tmp))]
            self.assertIn("drift", sev)

    def test_no_index_is_na(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"specs/a-spec.md": "x"})
            self.assertEqual([f.severity for f in _check_spec_index(_ctx(tmp))], ["na"])


class TestDigest(unittest.TestCase):
    def test_resolving_citation_passes(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                "claude/spec-spec.md": "x",
                "claude/constraints-digest.md": "- a rule — `claude/spec-spec.md`\n",
            })
            self.assertEqual(_check_digest(_ctx(tmp)), [])

    def test_dangling_citation_is_defect(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/constraints-digest.md": "- a rule — `claude/ghost-spec.md`\n"})
            out = _check_digest(_ctx(tmp))
            self.assertEqual([f.severity for f in out], ["defect"])

    def test_prose_bullet_without_spec_is_not_flagged(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/constraints-digest.md": "- time: 2026-06-12\n- summary: notes\n"})
            self.assertEqual(_check_digest(_ctx(tmp)), [])


class TestReferences(unittest.TestCase):
    def test_broken_link_is_defect(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/d.md": "see [x](missing.md)\n"})
            out = _check_references(_ctx(tmp))
            self.assertEqual([f.severity for f in out], ["defect"])

    def test_valid_link_passes(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/d.md": "see [y](other.md)\n", "claude/other.md": "z"})
            self.assertEqual(_check_references(_ctx(tmp)), [])

    def test_inline_code_example_link_skipped(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/d.md": "for example `[z](alsomissing.md)`\n"})
            self.assertEqual(_check_references(_ctx(tmp)), [])

    def test_external_url_skipped(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/d.md": "see [home](https://example.com/x.md)\n"})
            self.assertEqual(_check_references(_ctx(tmp)), [])


class TestPins(unittest.TestCase):
    def test_no_pin_block_is_na(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"claude/role.md": "no pins here\n"})
            self.assertEqual([f.severity for f in _check_pins(_ctx(tmp))], ["na"])

    def test_major_stale_pin_is_defect(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                "claude/spec-spec.md": "---\ntitle: S\nversion: 1.0.0\n---\n",
                "claude/role.md": "governance:\n  claude/spec-spec.md: 0.1.0\n",
            })
            out = _check_pins(_ctx(tmp))
            self.assertTrue(any(f.severity == "defect" for f in out), _sev(out))


class TestInventory(unittest.TestCase):
    def test_no_manual_is_na(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual([f.severity for f in _check_inventory(_ctx(tmp))], ["na"])

    def test_missing_listed_file_is_defect(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {"MANUAL.md": "inventory: `tools/aire/ghost.py`\n"})
            out = _check_inventory(_ctx(tmp))
            self.assertEqual([f.severity for f in out], ["defect"])


class TestDecisionLog(unittest.TestCase):
    def _event(self, did, **over):
        data = {"schema": "aire.decisions.v0.2", "id": did, "ts": "t",
                "title": "x", "decision": "y"}
        data.update(over)
        return json.dumps(data)

    def test_no_log_is_na(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual([f.severity for f in _check_decision_log(_ctx(tmp))], ["na"])

    def test_seq_behind_max_is_defect(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                "claude/decisions/SEQ.txt": "1\n",
                "claude/decisions/events/DEC-000005.json": self._event("DEC-000005"),
            })
            out = _check_decision_log(_ctx(tmp))
            self.assertTrue(any("SEQ" in f.location for f in out if f.severity == "defect"), _sev(out))

    def test_malformed_event_is_defect(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                "claude/decisions/SEQ.txt": "5\n",
                "claude/decisions/events/DEC-000005.json": "{ not json",
            })
            self.assertTrue(any(f.severity == "defect" for f in _check_decision_log(_ctx(tmp))))

    def test_unknown_outcome_is_candidate(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {
                "claude/decisions/SEQ.txt": "5\n",
                "claude/decisions/events/DEC-000005.json":
                    self._event("DEC-000005", outcome={"status": "unknown"}),
            })
            self.assertTrue(any(f.severity == "candidate" for f in _check_decision_log(_ctx(tmp))))


class TestBindings(unittest.TestCase):
    def test_well_formed_code_passes(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {".aire/config.toml": CODE_BINDING})
            self.assertEqual(_check_bindings(_ctx(tmp)), [])

    def test_none_without_justification_is_defect(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {".aire/config.toml": '[[coverage]]\nmodel = "none"\n'})
            out = _check_bindings(_ctx(tmp))
            self.assertEqual([f.severity for f in out], ["defect"])

    def test_no_binding_is_na(self):
        with TemporaryDirectory() as tmp:
            _write(tmp, {".aire/config.toml": 'profile = "B"\n'})
            self.assertEqual([f.severity for f in _check_bindings(_ctx(tmp))], ["na"])


class TestRunAudit(unittest.TestCase):
    def _clean_repo(self, tmp):
        _write(tmp, {
            ".aire/config.toml": CODE_BINDING,
            "tools/aire/a.py": "def foo():\n    pass\n",
            "specs/a-spec.md": "---\ntitle: A\ncovers:\n  - tools/aire/a.py\n---\n",
            "specs/INDEX.md": "| Path | T | d | S |\n|---|---|---|---|\n| `specs/a-spec.md` | T | d | draft |\n",
        })

    def _run(self, tmp, as_json=False):
        buf = io.StringIO()
        code = run_audit(as_json=as_json, repo_root=str(tmp), out=buf)
        return code, buf.getvalue()

    def test_clean_repo_exits_zero(self):
        with TemporaryDirectory() as tmp:
            self._clean_repo(tmp)
            code, _ = self._run(tmp)
            self.assertEqual(code, 0)

    def test_defect_exits_one(self):
        with TemporaryDirectory() as tmp:
            self._clean_repo(tmp)
            # break a markdown link -> reference-resolution defect
            _write(tmp, {"claude/d.md": "see [x](missing.md)\n"})
            code, _ = self._run(tmp)
            self.assertEqual(code, 1)

    def test_not_a_directory_exits_two(self):
        code = run_audit(repo_root="/no/such/path/here", out=io.StringIO())
        self.assertEqual(code, 2)

    def test_json_is_deterministic(self):
        with TemporaryDirectory() as tmp:
            self._clean_repo(tmp)
            _, a = self._run(tmp, as_json=True)
            _, b = self._run(tmp, as_json=True)
            self.assertEqual(a, b)
            self.assertIn('"summary"', a)

    def test_read_only(self):
        with TemporaryDirectory() as tmp:
            self._clean_repo(tmp)
            before = {p: p.read_bytes() for p in Path(tmp).rglob("*") if p.is_file()}
            self._run(tmp, as_json=True)
            after = {p: p.read_bytes() for p in Path(tmp).rglob("*") if p.is_file()}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
