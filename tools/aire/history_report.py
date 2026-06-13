"""`aire history report` — render the audited project history.

Governing spec: specs/tools/aire/history-spec.md (command surface); the view
definitions and recordless-merge classification are owned by
claude/promotion-record-spec.md. Read-only: no writes, no network. Reads git
tags + first-parent merges + sprint files + (best-effort) the local decision log.
Output is deterministic — canonical git commit dates only, never generation time.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from .history import HistoryError, _git

DEFAULT_CODE_PATHS = ("tools/", "src/", "tests/")


@dataclass
class Promotion:
    tag: str
    commit: str
    date: str
    payload: dict


@dataclass
class Merge:
    commit: str
    subject: str
    date: str
    promotion: "Promotion | None"
    changed_code: bool


@dataclass
class History:
    promotions: list
    findings: list      # recordless merges that changed code paths
    docs_merges: list   # recordless merges that did not (expected, Profile A)
    span: tuple


# --- gathering ---------------------------------------------------------------

def _fmt_date(unix_str):
    try:
        g = time.gmtime(int(unix_str))
    except (ValueError, TypeError):
        return "unknown"
    return f"{g.tm_year:04d}-{g.tm_mon:02d}-{g.tm_mday:02d}"


def _commit_date(commit, cwd=None):
    return _fmt_date(_git(["show", "-s", "--format=%ct", commit], cwd=cwd))


def collect_promotions(cwd=None):
    out = _git(["tag", "--list", "promote/*"], cwd=cwd)
    proms = []
    for tag in (t.strip() for t in out.splitlines() if t.strip()):
        commit = _git(["rev-list", "-n", "1", tag], cwd=cwd)
        contents = _git(["for-each-ref", "--format=%(contents)", f"refs/tags/{tag}"], cwd=cwd)
        try:
            payload = json.loads(contents)
        except json.JSONDecodeError:
            payload = {"_unparsed": contents}
        proms.append(Promotion(tag, commit, _commit_date(commit, cwd), payload))
    proms.sort(key=lambda p: (p.date, p.tag))
    return proms


def _merge_changed_code(merge_commit, code_paths, cwd=None):
    out = _git(["diff", "--name-only", f"{merge_commit}^1", merge_commit],
               cwd=cwd, check=False)
    return any(
        f.startswith(tuple(code_paths))
        for f in out.splitlines() if f
    )


def _resolve_ref(ref, cwd=None):
    if _git(["rev-parse", "--verify", "--quiet", ref], cwd=cwd, check=False):
        return ref
    return "HEAD"


def gather(ref="main", code_paths=DEFAULT_CODE_PATHS, cwd=None):
    ref = _resolve_ref(ref, cwd=cwd)
    proms = collect_promotions(cwd=cwd)
    by_commit = {p.commit: p for p in proms}

    out = _git(["log", "--merges", "--first-parent", ref, "--format=%H%x1f%ct%x1f%s"],
               cwd=cwd, check=False)
    findings, docs = [], []
    for line in (ln for ln in out.splitlines() if ln.strip()):
        h, ct, subj = line.split("\x1f", 2)
        prom = by_commit.get(h)
        if prom is not None:
            continue
        changed = _merge_changed_code(h, code_paths, cwd=cwd)
        merge = Merge(h, subj, _fmt_date(ct), None, changed)
        (findings if changed else docs).append(merge)

    dates = sorted(
        d for d in ([p.date for p in proms]
                    + [m.date for m in findings + docs]) if d != "unknown"
    )
    span = (dates[0], dates[-1]) if dates else (None, None)
    return History(promotions=proms, findings=findings, docs_merges=docs, span=span)


# --- joins (best-effort, against local canonical state) ----------------------

def _decision_title(did, cwd=None):
    f = Path(cwd or ".") / "claude" / "decisions" / "events" / f"{did}.json"
    if not f.is_file():
        return None
    try:
        return json.loads(f.read_text()).get("title")
    except (json.JSONDecodeError, OSError):
        return None


def _frontmatter_field(text, field):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith(f"{field}:"):
            return line.split(":", 1)[1].strip()
    return None


def _sprint_title(path, cwd=None):
    if not path:
        return None
    f = Path(cwd or ".") / path
    if not f.is_file():
        return None
    return _frontmatter_field(f.read_text(), "title")


# --- rendering ---------------------------------------------------------------

def _project_name(cwd=None):
    top = _git(["rev-parse", "--show-toplevel"], cwd=cwd, check=False)
    return Path(top).name if top else "project"


def _render_summary(h, cwd, out):
    out.write(f"# {_project_name(cwd)} — Project History\n\n")
    if h.span[0]:
        out.write(f"Span: {h.span[0]} .. {h.span[1]}\n\n")
    out.write(f"- Tested promotions: {len(h.promotions)}\n")
    out.write(f"- Docs/governance merges (no record expected): {len(h.docs_merges)}\n")
    out.write(f"- Code merges without a test record (findings): {len(h.findings)}\n\n")
    if not h.findings:
        out.write("OK  Every code merge into main carries a tested promotion record.\n")
    else:
        out.write(f"XX  {len(h.findings)} code merge(s) reached main without a record — see Findings.\n")
    if h.promotions:
        out.write("\n## Tested Promotions\n")
        for p in h.promotions:
            t = p.payload.get("tests", {})
            title = _sprint_title(p.payload.get("sprint"), cwd) or "—"
            out.write(f"- {p.date}  {p.tag}  [{t.get('outcome', '?')}]  {title}\n")
    if h.findings:
        out.write("\n## Findings — code merges without a record\n")
        for m in h.findings:
            out.write(f"- {m.date}  {m.commit[:9]}  {m.subject}\n")


def _render_detail(h, cwd, out):
    out.write(f"# {_project_name(cwd)} — Promotion Detail\n")
    for p in h.promotions:
        pl = p.payload
        t = pl.get("tests", {})
        out.write(f"\n## {p.tag}  ({p.date})\n")
        out.write(f"- Sprint: {_sprint_title(pl.get('sprint'), cwd) or '—'} ({pl.get('sprint') or '—'})\n")
        out.write(f"- Commit: {p.commit}\n")
        out.write(f"- Tests: {t.get('outcome', '?')} — `{t.get('command', '—')}` @ {(t.get('sha') or '')[:9]}\n")
        specs = pl.get("specs") or []
        out.write(f"- Specs: {', '.join(specs) if specs else '—'}\n")
        decs = pl.get("decisions") or []
        rendered = []
        for did in decs:
            title = _decision_title(did, cwd)
            rendered.append(f"{did} ({title})" if title else did)
        out.write(f"- Decisions: {'; '.join(rendered) if rendered else '—'}\n")
        if pl.get("notes"):
            out.write(f"- Notes: {pl['notes']}\n")


def _render_chain(h, slug, cwd, out):
    match = None
    for p in h.promotions:
        if p.tag == f"promote/{slug}" or p.tag == slug or p.tag.endswith(f"/{slug}"):
            match = p
            break
    if match is None:
        raise HistoryError(f"no promotion found for slug {slug!r}")
    pl = match.payload
    t = pl.get("tests", {})
    out.write(f"# Audit chain — {match.tag}\n\n")
    out.write(f"Sprint:    {pl.get('sprint') or '—'}\n")
    out.write("Specs:\n")
    for s in (pl.get("specs") or []):
        out.write(f"  - {s}\n")
    out.write(f"Promotion: {match.tag} -> {match.commit} ({match.date})\n")
    out.write(f"Tests:     {t.get('outcome', '?')} via `{t.get('command', '—')}` against {t.get('sha', '—')}\n")
    out.write("Decisions:\n")
    for did in (pl.get("decisions") or []):
        title = _decision_title(did, cwd)
        out.write(f"  - {did}{f' — {title}' if title else ''}\n")
    if pl.get("notes"):
        out.write(f"Notes:     {pl['notes']}\n")


def to_json(h):
    return {
        "span": {"earliest": h.span[0], "latest": h.span[1]},
        "counts": {
            "tested_promotions": len(h.promotions),
            "docs_merges": len(h.docs_merges),
            "findings": len(h.findings),
        },
        "promotions": [
            {"tag": p.tag, "commit": p.commit, "date": p.date, "payload": p.payload}
            for p in h.promotions
        ],
        "findings": [
            {"commit": m.commit, "date": m.date, "subject": m.subject}
            for m in h.findings
        ],
    }


def run_report(view="summary", slug=None, ref="main", as_json=False, cwd=None, out=None):
    out = out if out is not None else sys.stdout
    history = gather(ref=ref, cwd=cwd)
    if as_json:
        json.dump(to_json(history), out, indent=2, sort_keys=True)
        out.write("\n")
    elif view == "chain":
        _render_chain(history, slug, cwd, out)
    elif view == "detail":
        _render_detail(history, cwd, out)
    else:
        _render_summary(history, cwd, out)
    return 1 if history.findings else 0
