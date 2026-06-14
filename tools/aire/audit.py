"""`aire audit` — the mechanical half of the governance liveness audit.

Governing spec: specs/tools/aire/audit-spec.md. The check set, severities,
cadence, and disposition are owned by claude/audit-spec.md; coverage mechanics
by claude/coverage-spec.md (check 1 reuses the map engine); recordless-merge
classification by claude/promotion-record-spec.md (check 7 reuses the history
report). Read-only: no writes; git is shelled read-only for checks 4 and 7.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from . import map as mapper
from .config import load_config
from .doctor import find_git_root
from .history_report import gather as history_gather


@dataclass
class Finding:
    check: str
    severity: str   # defect | drift | candidate | na
    location: str
    message: str


@dataclass
class AuditContext:
    root: Path
    config: object
    is_git: bool


SEVERITY_ORDER = {"defect": 0, "drift": 1, "candidate": 2, "na": 3}
VALID_MODELS = {"code", "artifact", "advisory", "none"}

_INDEX_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|")
_BACKTICK = re.compile(r"`([^`]+)`")
_MDLINK = re.compile(r"\]\(([^)]+)\)")
_FENCE = re.compile(r"```.*?```", re.S)
_INLINE_CODE = re.compile(r"`[^`]*`")
_PATH_EXT = (".md", ".py", ".toml", ".json", ".yml", ".yaml", ".txt", ".cfg", ".sh")


def _looks_like_path(tok: str) -> bool:
    if any(c in tok for c in "<>* \t"):
        return False
    if "/" not in tok:
        return False
    return tok.endswith(_PATH_EXT)


# --- checks: each takes ctx, returns list[Finding] ---------------------------

def _check_coverage(ctx: AuditContext) -> list:
    try:
        bindings = mapper.resolve_bindings(ctx.root, ctx.config)
    except mapper.MapError as exc:
        sev = "na" if "no coverage binding" in str(exc) else "defect"
        return [Finding("coverage", sev, ".aire/config.toml", str(exc))]
    try:
        result = mapper.build_map(ctx.root, bindings)
    except mapper.MapError as exc:
        return [Finding("coverage", "defect", "-", str(exc))]
    out = []
    for u in result.uncovered:
        out.append(Finding("coverage", "defect", u.id, "uncovered unit (no covering spec)"))
    for spec, entry in result.stale_decls:
        out.append(Finding("coverage", "defect", entry, f"stale covers: declaration in {spec}"))
    for uid, specs in result.conflicts:
        out.append(Finding("coverage", "defect", uid, f"ownership conflict: {', '.join(specs)}"))
    return out


def _check_spec_index(ctx: AuditContext) -> list:
    index = ctx.root / "specs" / "INDEX.md"
    if not index.is_file():
        return [Finding("spec-index", "na", "specs/INDEX.md", "no specs/INDEX.md")]
    rows = [m.group(1) for line in index.read_text(encoding="utf-8").splitlines()
            if (m := _INDEX_ROW.match(line))]
    indexed = set(rows)
    specs_dir = ctx.root / "specs"
    actual = {str(md.relative_to(ctx.root)) for md in specs_dir.rglob("*.md")
              if str(md.relative_to(ctx.root)) != "specs/INDEX.md"}
    out = []
    for rel in sorted(actual - indexed):
        out.append(Finding("spec-index", "defect", rel, "spec not listed in specs/INDEX.md"))
    for rel in sorted({r for r in indexed if r.startswith("specs/")} - actual):
        out.append(Finding("spec-index", "defect", rel, "INDEX row points to a missing spec"))
    if rows != sorted(rows):
        out.append(Finding("spec-index", "drift", "specs/INDEX.md", "index rows are not sorted by path"))
    return out


def _check_digest(ctx: AuditContext) -> list:
    digest = ctx.root / "claude" / "constraints-digest.md"
    if not digest.is_file():
        return [Finding("digest-agreement", "na", "claude/constraints-digest.md", "no constraints digest")]
    # Mechanical half: every spec a digest line cites must resolve. Whether a
    # given bullet is a *rule* that ought to cite a spec is judgment-tier (the
    # file also has prose/provenance bullets), so we verify citations, not their
    # presence. Semantic agreement is the judgment walk's job (claude/audit-spec.md).
    out = []
    for i, line in enumerate(digest.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if not s.startswith("- "):
            continue
        for cited in (t for t in _BACKTICK.findall(s) if t.endswith(".md")):
            if not (ctx.root / cited).is_file():
                out.append(Finding("digest-agreement", "defect", f"claude/constraints-digest.md:{i}",
                                   f"cited owning spec not found: {cited}"))
    return out


def _check_pins(ctx: AuditContext) -> list:
    claude = ctx.root / "claude"
    role_files = []
    if claude.is_dir():
        for md in sorted(claude.rglob("*.md")):
            text = md.read_text(encoding="utf-8")
            if re.search(r"^governance:", text, re.M):
                role_files.append((md, text))
    if not role_files:
        return [Finding("pin-currency", "na", "claude/", "no role with a governance: pin block in this repo")]
    out = []
    for md, text in role_files:
        rel = str(md.relative_to(ctx.root))
        for spec, pinned in _parse_pins(text):
            current = _spec_version(ctx.root / spec)
            if current is None:
                out.append(Finding("pin-currency", "defect", rel, f"pinned spec not found: {spec}"))
            elif current != pinned:
                major = current.split(".")[0] != pinned.split(".")[0]
                out.append(Finding("pin-currency", "defect" if major else "drift", rel,
                                   f"{spec} pinned {pinned}, current {current}"
                                   + (" (major — regenerate)" if major else "")))
    return out or [Finding("pin-currency", "na", "claude/", "role pins are current")]


def _parse_pins(text: str) -> list:
    """Lines like `  claude/spec.md: 0.4.0` under a `governance:` block."""
    pins, in_block = [], False
    for line in text.splitlines():
        if re.match(r"^governance:", line):
            in_block = True
            continue
        if in_block:
            if line and not line[0].isspace():
                break
            m = re.match(r"\s+(?:-\s*)?([\w./-]+\.md):\s*([0-9][\w.]*)", line)
            if m:
                pins.append((m.group(1), m.group(2)))
    return pins


def _spec_version(path: Path):
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines()[:20]:
        m = re.match(r"version:\s*([0-9][\w.]*)", line.strip())
        if m:
            return m.group(1)
    return None


def _check_references(ctx: AuditContext) -> list:
    # Markdown link targets only: a `[text](path)` link is a deliberate
    # cross-reference. Backticked path *tokens* in prose are frequently
    # illustrative examples (e.g. `src/auth/token.py`), so resolving them
    # mechanically is too noisy — that is deferred to the judgment walk.
    out, seen = [], set()
    for base in ("claude", "specs", "sprints"):
        d = ctx.root / base
        if not d.is_dir():
            continue
        for md in sorted(d.rglob("*.md")):
            rel_doc = str(md.relative_to(ctx.root))
            text = _FENCE.sub("", md.read_text(encoding="utf-8"))  # drop code fences (examples)
            text = _INLINE_CODE.sub("", text)  # drop inline code (illustrative links live here)
            for tok in set(_MDLINK.findall(text)):
                t = tok.strip().split("#", 1)[0]
                if not t or t.startswith(("http://", "https://", "mailto:")):
                    continue
                if t.startswith("./"):
                    t = t[2:]
                if any(c in t for c in "<>* "):
                    continue
                if (rel_doc, t) in seen:
                    continue
                seen.add((rel_doc, t))
                if (ctx.root / t).exists() or (md.parent / t).exists():
                    continue
                out.append(Finding("reference-resolution", "defect", f"{rel_doc} -> {t}",
                                   "broken markdown link"))
    return out


def _check_inventory(ctx: AuditContext) -> list:
    manual = ctx.root / "MANUAL.md"
    if not manual.is_file():
        return [Finding("inventory-accuracy", "na", "MANUAL.md", "no MANUAL.md inventory in this repo")]
    out = []
    for tok in sorted(set(_BACKTICK.findall(manual.read_text(encoding="utf-8")))):
        if _looks_like_path(tok) and not (ctx.root / tok).exists():
            out.append(Finding("inventory-accuracy", "defect", tok, "inventory lists a missing file"))
    return out


def _check_promotions(ctx: AuditContext) -> list:
    if not ctx.is_git:
        return [Finding("promotion-records", "na", "-", "not a git repository; cannot read merges/tags")]
    try:
        hist = history_gather(ref="main", cwd=str(ctx.root))
    except Exception as exc:  # noqa: BLE001 — surface as a defect, never crash the run
        return [Finding("promotion-records", "defect", "-", f"history gather failed: {exc}")]
    return [Finding("promotion-records", "defect", m.commit[:12],
                    f"code merge without a promotion record: {m.subject}")
            for m in hist.findings]


def _check_decision_log(ctx: AuditContext) -> list:
    ddir = ctx.root / "claude" / "decisions"
    if not ddir.is_dir():
        return [Finding("decision-log-integrity", "na", "claude/decisions/", "decision log not present (private)")]
    out, max_id = [], 0
    required = {"schema", "id", "ts", "title", "decision"}
    events = sorted((ddir / "events").glob("*.json")) if (ddir / "events").is_dir() else []
    for ev in events:
        rel = str(ev.relative_to(ctx.root))
        try:
            data = json.loads(ev.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            out.append(Finding("decision-log-integrity", "defect", rel, f"invalid JSON: {exc}"))
            continue
        missing = required - set(data)
        if missing:
            out.append(Finding("decision-log-integrity", "defect", rel,
                               f"missing fields: {', '.join(sorted(missing))}"))
        if (m := re.search(r"(\d+)", str(data.get("id", "")))):
            max_id = max(max_id, int(m.group(1)))
        outcome = data.get("outcome")
        if isinstance(outcome, dict) and outcome.get("status") == "unknown":
            out.append(Finding("decision-log-integrity", "candidate", rel,
                               "decision outcome left 'unknown' — review for closure"))
    seq_file = ddir / "SEQ.txt"
    if not seq_file.is_file():
        out.append(Finding("decision-log-integrity", "defect", "claude/decisions/SEQ.txt", "SEQ.txt missing"))
    else:
        try:
            seq = int(seq_file.read_text(encoding="utf-8").strip())
            if seq < max_id:
                out.append(Finding("decision-log-integrity", "defect", "claude/decisions/SEQ.txt",
                                   f"SEQ {seq} < highest event id {max_id}"))
        except ValueError:
            out.append(Finding("decision-log-integrity", "defect", "claude/decisions/SEQ.txt",
                               "SEQ.txt is not an integer"))
    return out


def _check_bindings(ctx: AuditContext) -> list:
    bindings = ctx.config.coverage if ctx.config else []
    if not bindings:
        return [Finding("binding-validity", "na", ".aire/config.toml", "no coverage bindings declared")]
    out = []
    needs = {"code": ("paths", "paths"), "artifact": ("globs", "globs"),
             "advisory": ("joins", "joins"), "none": ("justification", "justification")}
    for i, b in enumerate(bindings, 1):
        loc = f".aire/config.toml [[coverage]]#{i}"
        if b.model not in VALID_MODELS:
            out.append(Finding("binding-validity", "defect", loc, f"unrecognized model: {b.model!r}"))
            continue
        attr, label = needs[b.model]
        if not getattr(b, attr):
            out.append(Finding("binding-validity", "defect", loc, f"{b.model} binding missing {label}"))
    return out


def default_checks() -> list:
    return [
        ("coverage", _check_coverage),
        ("spec-index", _check_spec_index),
        ("digest-agreement", _check_digest),
        ("pin-currency", _check_pins),
        ("reference-resolution", _check_references),
        ("inventory-accuracy", _check_inventory),
        ("promotion-records", _check_promotions),
        ("decision-log-integrity", _check_decision_log),
        ("binding-validity", _check_bindings),
    ]


def run_checks(ctx: AuditContext, checks=None) -> list:
    checks = default_checks() if checks is None else checks
    findings: list = []
    for name, fn in checks:
        try:
            findings.extend(fn(ctx))
        except Exception as exc:  # noqa: BLE001 — a check names its own failure, run continues
            findings.append(Finding(name, "defect", "-", f"check raised: {exc}"))
    return findings


# --- rendering ----------------------------------------------------------------

def _counts(findings) -> dict:
    c = {"defect": 0, "drift": 0, "candidate": 0, "na": 0}
    for f in findings:
        c[f.severity] = c.get(f.severity, 0) + 1
    return c


_MANUAL_RESIDUE = ("Manual residue (judgment walk, per claude/audit-spec.md): semantic digest "
                   "agreement, and the exercised / agreement / necessity review of each rule.")


def render_md(findings, out) -> None:
    c = _counts(findings)
    out.write("# Governance Liveness Audit\n\n")
    out.write(f"{c['defect']} defect, {c['drift']} drift, "
              f"{c['candidate']} candidate, {c['na']} n/a\n\n")
    by_check: dict = {}
    for f in findings:
        by_check.setdefault(f.check, []).append(f)
    for name, _ in default_checks():
        fs = by_check.get(name, [])
        out.write(f"## {name}\n\n")
        if not fs:
            out.write("- OK — no findings\n\n")
            continue
        for f in sorted(fs, key=lambda f: (SEVERITY_ORDER[f.severity], f.location)):
            out.write(f"- **{f.severity}** `{f.location}` — {f.message}\n")
        out.write("\n")
    out.write(f"---\n{_MANUAL_RESIDUE}\n")


def render_json(findings, out) -> None:
    order = [n for n, _ in default_checks()]
    payload = {
        "summary": _counts(findings),
        "findings": [
            {"check": f.check, "severity": f.severity, "location": f.location, "message": f.message}
            for f in sorted(findings, key=lambda f: (order.index(f.check),
                                                     SEVERITY_ORDER[f.severity], f.location))
        ],
    }
    json.dump(payload, out, indent=2, sort_keys=True)
    out.write("\n")


def run_audit(as_json: bool = False, repo_root=None, out=None) -> int:
    out = out if out is not None else sys.stdout
    start = Path(repo_root).resolve() if repo_root else Path.cwd()
    git_root = find_git_root(start)
    root = git_root or start
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2
    ctx = AuditContext(root=root, config=load_config(root), is_git=git_root is not None)
    findings = run_checks(ctx)
    (render_json if as_json else render_md)(findings, out)
    return 1 if any(f.severity == "defect" for f in findings) else 0
