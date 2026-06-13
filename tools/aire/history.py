"""`aire history record` — write a promotion record as an annotated git tag.

Governing spec: specs/tools/aire/history-spec.md (command surface); the record
format and -rN uniqueness rule are owned by claude/promotion-record-spec.md.
Payload is JSON (DEC-000017). Creates a LOCAL tag only; pushing is human-only
(claude/claude.git-hygiene.md). Uses git via subprocess — local, no network.
"""

from __future__ import annotations

import json
import subprocess
import sys


class HistoryError(Exception):
    """A validation or git error that must fail the command closed (exit 2)."""


def _git(args, cwd=None, check=True, stdin=None):
    proc = subprocess.run(
        ["git", *args], cwd=cwd, check=False,
        capture_output=True, text=True, input=stdin,
    )
    if check and proc.returncode != 0:
        raise HistoryError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def current_branch(cwd=None):
    return _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)


def infer_slug(cwd=None):
    """work/<timestamp>/<slug> -> <slug>; else the last branch path segment."""
    branch = current_branch(cwd)
    if not branch or branch == "HEAD":
        return None
    return branch.rsplit("/", 1)[-1]


def resolve_commit(ref, cwd=None):
    return _git(["rev-parse", ref], cwd=cwd)


def _existing_promote_tags(slug, cwd=None):
    out = _git(["tag", "--list", f"promote/{slug}", f"promote/{slug}-r*"], cwd=cwd)
    return {t for t in out.splitlines() if t}


def next_tag_name(slug, cwd=None):
    existing = _existing_promote_tags(slug, cwd=cwd)
    base = f"promote/{slug}"
    if base not in existing:
        return base
    n = 2
    while f"{base}-r{n}" in existing:
        n += 1
    return f"{base}-r{n}"


def build_payload(*, sprint, specs, tests_command, tests_outcome, tests_sha,
                  decisions, notes):
    return {
        "sprint": sprint,
        "specs": list(specs or []),
        "tests": {
            "command": tests_command,
            "outcome": tests_outcome,
            "sha": tests_sha,
        },
        "decisions": list(decisions or []),
        "notes": notes,
    }


def validate(payload):
    outcome = payload["tests"]["outcome"]
    if outcome not in ("PASS", "N/A"):
        raise HistoryError(f"tests.outcome must be PASS or N/A, got {outcome!r}")
    if outcome == "PASS":
        if not payload["tests"]["sha"]:
            raise HistoryError("a PASS record requires tests.sha")
        if not payload["tests"]["command"]:
            raise HistoryError("a PASS record requires tests.command")


def format_message(payload):
    """Deterministic JSON: sorted keys, 2-space indent (DEC-000017)."""
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def record(*, slug=None, commit="HEAD", tests_sha=None, tests_command=None,
           tests_outcome="PASS", specs=None, sprint=None, decisions=None,
           notes=None, dry_run=False, cwd=None, out=None):
    out = out if out is not None else sys.stdout

    slug = slug or infer_slug(cwd)
    if not slug:
        raise HistoryError("could not determine slug from branch; pass --slug")

    commit_sha = resolve_commit(commit, cwd=cwd)
    tests_sha = resolve_commit(tests_sha, cwd=cwd) if tests_sha else commit_sha

    payload = build_payload(
        sprint=sprint, specs=specs, tests_command=tests_command,
        tests_outcome=tests_outcome, tests_sha=tests_sha,
        decisions=decisions, notes=notes,
    )
    validate(payload)

    tag = next_tag_name(slug, cwd=cwd)
    message = format_message(payload)

    if dry_run:
        out.write(f"# would create annotated tag {tag} -> {commit_sha}\n")
        out.write(message)
        return 0

    _git(["tag", "-a", tag, commit_sha, "-F", "-"], cwd=cwd, stdin=message)
    out.write(f"created promotion record: {tag} -> {commit_sha}\n")
    return 0
