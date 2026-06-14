"""`aire map` — spec coverage mapping (the `code` engine).

Governing spec: specs/tools/aire/map-spec.md. The coverage models, binding
homes/resolution order, and uncovered/stale/conflict semantics are owned by
claude/coverage-spec.md and referenced, never restated.

Read-only: emits reports to stdout; performs no writes and no network. Git is
shelled only to read committer dates for best-effort staleness.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .config import load_config
from .doctor import find_git_root


class MapError(Exception):
    """Misconfiguration that makes coverage unverifiable (fail closed, exit 2)."""


# --- data ---------------------------------------------------------------------

@dataclass
class Unit:
    """A coverage unit: a public symbol extracted from source."""

    id: str       # "tools/aire/cli.py:main"
    path: str     # "tools/aire/cli.py"
    symbol: str   # "main" | "Config" | "Context.root"
    kind: str     # function | class | method


@dataclass
class CoverEntry:
    """One `covers:` declaration parsed from a spec header."""

    spec: str            # spec path that declared it
    path: str            # covered path
    symbol: str | None   # None = whole-file declaration

    @property
    def unit_id(self) -> str:
        return self.path if self.symbol is None else f"{self.path}:{self.symbol}"


@dataclass
class UnitResult:
    unit: Unit
    spec: str | None     # covering spec (first, if any)
    stale: bool | None   # spec older than source (best-effort), else None


@dataclass
class MapResult:
    results: list        # UnitResult, sorted by (path, symbol)
    uncovered: list      # Unit
    stale_decls: list    # (spec, entry_text)
    conflicts: list      # (unit_id, [specs])

    @property
    def findings(self) -> bool:
        return bool(self.uncovered or self.stale_decls or self.conflicts)


# --- extraction (the code engine) --------------------------------------------

def extract_units(rel_path: str, source: str) -> list:
    """Public functions, classes, and public methods in `source` (AST)."""
    tree = ast.parse(source)  # SyntaxError surfaces to the caller
    units: list = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                units.append(Unit(f"{rel_path}:{node.name}", rel_path, node.name, "function"))
        elif isinstance(node, ast.ClassDef):
            if node.name.startswith("_"):
                continue
            units.append(Unit(f"{rel_path}:{node.name}", rel_path, node.name, "class"))
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and not sub.name.startswith("_"):
                    sym = f"{node.name}.{sub.name}"
                    units.append(Unit(f"{rel_path}:{sym}", rel_path, sym, "method"))
    return units


def _front_matter_covers(md_text: str) -> list:
    """Extract the `covers:` block-list entries from a markdown YAML header."""
    lines = md_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return []
    covers: list = []
    in_covers = False
    for line in lines[1:end]:
        stripped = line.strip()
        if not in_covers:
            if stripped == "covers:" or stripped.startswith("covers:"):
                in_covers = True
            continue
        if stripped.startswith("- "):
            entry = stripped[2:].split("#", 1)[0].strip().strip('"').strip("'")
            if entry:
                covers.append(entry)
        elif not stripped:
            continue
        else:
            break  # a new top-level key ends the covers block
    return covers


def collect_cover_entries(root: Path) -> list:
    """All `covers:` declarations under specs/ and claude/."""
    entries: list = []
    for base in ("specs", "claude"):
        d = root / base
        if not d.is_dir():
            continue
        for md in sorted(d.rglob("*.md")):
            try:
                text = md.read_text(encoding="utf-8")
            except OSError:
                continue
            rel_spec = str(md.relative_to(root))
            for c in _front_matter_covers(text):
                if ":" in c:
                    cpath, csym = c.split(":", 1)
                else:
                    cpath, csym = c, None
                entries.append(CoverEntry(rel_spec, cpath, csym))
    return entries


# --- binding resolution -------------------------------------------------------

def resolve_bindings(root: Path, config) -> list:
    """Bindings to evaluate, per coverage-spec resolution order.

    Role headers resolve first; no role-bearing repo uses the CLI yet, so role
    discovery is a later addition. Today bindings come from .aire/config.toml
    [[coverage]] (DEC-000019).
    """
    bindings = list(config.coverage)
    if not bindings:
        raise MapError(
            "no coverage binding found "
            "(declare [[coverage]] in .aire/config.toml or a role header)"
        )
    return bindings


def _within(cpath: str, binding_paths: list) -> bool:
    cp = cpath.rstrip("/")
    for bp in binding_paths:
        b = bp.rstrip("/")
        if cp == b or cp.startswith(b + "/"):
            return True
    return False


def _iter_binding_files(root: Path, paths: list) -> list:
    """(.py file, repo-relative path) pairs for a code binding's paths."""
    files: list = []
    for p in paths:
        ap = root / p
        if not ap.exists():
            raise MapError(f"coverage binding path not found: {p}")
        if ap.is_dir():
            for f in sorted(ap.rglob("*.py")):
                files.append((f, str(f.relative_to(root))))
        elif ap.suffix == ".py":
            files.append((ap, str(ap.relative_to(root))))
        # a non-.py file listed in a code binding is ignored by this engine
    return files


# --- staleness (best-effort, git committer dates) -----------------------------

def _git_ts(root: Path, relpath: str, cache: dict):
    if relpath in cache:
        return cache[relpath]
    ts = None
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", relpath],
            cwd=str(root), capture_output=True, text=True, check=True,
        )
        s = out.stdout.strip()
        ts = int(s) if s else None
    except (subprocess.SubprocessError, OSError, ValueError):
        ts = None
    cache[relpath] = ts
    return ts


# --- map build ----------------------------------------------------------------

def build_map(root: Path, bindings: list) -> MapResult:
    code_paths: list = []
    units: list = []
    source_files: set = set()

    for b in bindings:
        if b.model == "none":
            continue
        if b.model != "code":
            raise MapError(
                f"coverage model not implemented: {b.model!r} "
                "(v0.1 implements 'code' only)"
            )
        code_paths.extend(b.paths)
        for ap, rel in _iter_binding_files(root, b.paths):
            source_files.add(rel)
            try:
                src = ap.read_text(encoding="utf-8")
            except OSError as exc:
                raise MapError(f"cannot read source {rel}: {exc}")
            try:
                units.extend(extract_units(rel, src))
            except SyntaxError as exc:
                raise MapError(f"cannot parse {rel}: {exc}")

    unit_ids = {u.id for u in units}
    cover_by_unit: dict = {}      # unit_id -> set(specs)
    stale_decls: list = []        # (spec, entry_text)

    for ce in collect_cover_entries(root):
        if not ce.path.endswith(".py") or not _within(ce.path, code_paths):
            continue  # outside this engine's domain
        if ce.symbol is None:
            if ce.path not in source_files:
                stale_decls.append((ce.spec, ce.path))
                continue
            for u in units:
                if u.path == ce.path:
                    cover_by_unit.setdefault(u.id, set()).add(ce.spec)
        else:
            if ce.unit_id not in unit_ids:
                stale_decls.append((ce.spec, ce.unit_id))
                continue
            cover_by_unit.setdefault(ce.unit_id, set()).add(ce.spec)

    uncovered = [u for u in units if u.id not in cover_by_unit]
    conflicts = [
        (uid, sorted(specs)) for uid, specs in cover_by_unit.items() if len(specs) > 1
    ]

    ts_cache: dict = {}
    results: list = []
    for u in sorted(units, key=lambda u: (u.path, u.symbol)):
        specs = sorted(cover_by_unit.get(u.id, ()))
        spec = specs[0] if specs else None
        stale = None
        if spec is not None:
            st, su = _git_ts(root, spec, ts_cache), _git_ts(root, u.path, ts_cache)
            stale = (st < su) if (st is not None and su is not None) else None
        results.append(UnitResult(u, spec, stale))

    return MapResult(results=results, uncovered=uncovered,
                     stale_decls=stale_decls, conflicts=conflicts)


# --- rendering ----------------------------------------------------------------

def render_check(result: MapResult, out) -> None:
    if not result.findings:
        n = len(result.results)
        out.write(f"coverage: OK — {n} unit{'' if n == 1 else 's'} covered, "
                  "0 uncovered, 0 stale, 0 conflicts\n")
        return
    if result.uncovered:
        out.write(f"uncovered units ({len(result.uncovered)}):\n")
        for u in sorted(result.uncovered, key=lambda u: (u.path, u.symbol)):
            out.write(f"  {u.id}  ({u.kind})\n")
    if result.stale_decls:
        out.write(f"stale declarations ({len(result.stale_decls)}):\n")
        for spec, entry in sorted(result.stale_decls):
            out.write(f"  {entry}  declared by {spec} — no matching unit\n")
    if result.conflicts:
        out.write(f"ownership conflicts ({len(result.conflicts)}):\n")
        for uid, specs in sorted(result.conflicts):
            out.write(f"  {uid}  claimed by {', '.join(specs)}\n")


def render_report_json(result: MapResult, out) -> None:
    payload = {
        "units": [
            {"id": r.unit.id, "kind": r.unit.kind, "spec": r.spec, "stale": r.stale}
            for r in result.results
        ],
        "uncovered": [
            u.id for u in sorted(result.uncovered, key=lambda u: (u.path, u.symbol))
        ],
        "stale_declarations": [
            {"entry": e, "spec": s} for s, e in sorted(result.stale_decls)
        ],
        "conflicts": [
            {"unit": uid, "specs": specs} for uid, specs in sorted(result.conflicts)
        ],
    }
    json.dump(payload, out, indent=2, sort_keys=True)
    out.write("\n")


def render_report_md(result: MapResult, out) -> None:
    total = len(result.results)
    covered = sum(1 for r in result.results if r.spec)
    out.write("# Coverage Map\n\n")
    out.write(f"{covered}/{total} units covered.\n\n")
    out.write("| Unit | Kind | Covering spec | Stale |\n")
    out.write("|---|---|---|---|\n")
    for r in result.results:
        spec = r.spec or "—"
        stale = "—" if r.stale is None else ("yes" if r.stale else "no")
        out.write(f"| `{r.unit.id}` | {r.unit.kind} | {spec} | {stale} |\n")
    if result.stale_decls:
        out.write("\n## Stale declarations\n\n")
        for s, e in sorted(result.stale_decls):
            out.write(f"- `{e}` declared by `{s}` — no matching unit\n")
    if result.conflicts:
        out.write("\n## Ownership conflicts\n\n")
        for uid, specs in sorted(result.conflicts):
            out.write(f"- `{uid}` claimed by {', '.join(specs)}\n")


def run_map(action: str, as_json: bool = False, repo_root=None, out=None) -> int:
    out = out if out is not None else sys.stdout
    start = Path(repo_root).resolve() if repo_root else Path.cwd()
    root = find_git_root(start) or start
    try:
        config = load_config(root)
        if config.parse_error:
            raise MapError(f".aire/config.toml parse error: {config.parse_error}")
        bindings = resolve_bindings(root, config)
        result = build_map(root, bindings)
    except MapError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if action == "check":
        render_check(result, out)
        return 1 if result.findings else 0
    if action == "report":
        (render_report_json if as_json else render_report_md)(result, out)
        return 0
    print("usage: aire map {check|report}", file=sys.stderr)
    return 2
