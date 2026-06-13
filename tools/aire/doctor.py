"""`aire doctor` — read-only repository and environment validation.

Governing spec: specs/tools/aire/doctor-spec.md. Runs a registry of independent
checks, each returning (status, message); status is "ok" | "warn" | "fail".
Read-only: no writes, no network.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from . import __version__
from .config import Config, load_config, version_satisfies


@dataclass
class Context:
    """Everything the checks need, computed once per run."""

    start: Path
    git_root: Path | None
    config: Config
    running_version: str

    @property
    def root(self) -> Path:
        return self.git_root or self.start


def find_git_root(start: Path) -> Path | None:
    """Walk up from `start` looking for a .git entry; return the dir or None."""
    start = Path(start).resolve()
    for d in (start, *start.parents):
        if (d / ".git").exists():
            return d
    return None


# --- checks: each takes ctx, returns (status, message) -----------------------

def _check_repository(ctx: Context):
    if ctx.git_root is not None:
        return "ok", f"git repository at {ctx.git_root}"
    return "fail", "not inside a git repository"


def _check_config(ctx: Context):
    if ctx.config.parse_error:
        return "fail", f".aire/config.toml parse error: {ctx.config.parse_error}"
    if not ctx.config.present:
        return "warn", "no .aire/config.toml; using defaults"
    return "ok", ".aire/config.toml parsed"


def _check_version_pin(ctx: Context):
    if ctx.config.parse_error:
        return "warn", "config unreadable; cannot check version pin"
    floor = ctx.config.aire_version_min
    if not floor:
        return "ok", "no minimum CLI version declared"
    if version_satisfies(ctx.running_version, floor):
        return "ok", f"CLI {ctx.running_version} >= required {floor}"
    return "fail", f"CLI {ctx.running_version} < required {floor}"


def _check_profile(ctx: Context):
    if ctx.config.parse_error:
        return "warn", "config unreadable; cannot check profile"
    p = ctx.config.profile
    if p in ("A", "B"):
        return "ok", f"promotion profile {p}"
    if p is None:
        return "warn", "no promotion profile declared"
    return "fail", f"unrecognized promotion profile: {p!r}"


def _check_governance(ctx: Context):
    claude = ctx.root / "claude"
    needed = [claude / "claude.role.base.md", claude / "spec-spec.md"]
    if all(f.is_file() for f in needed):
        return "ok", "governance present (role base + spec-spec)"
    if claude.is_dir():
        return "warn", "claude/ present but incomplete (role base or spec-spec missing)"
    return "warn", "no claude/ governance directory (may be governed elsewhere)"


def _check_state(ctx: Context):
    if (ctx.root / "STATE.md").is_file():
        return "ok", "STATE.md present"
    return "warn", "no STATE.md (claude/state-tracker-spec.md expects one)"


def _check_floor(ctx: Context):
    if ctx.config.parse_error:
        return "warn", "config unreadable; cannot check local-model floor"
    if ctx.config.local_model_floor is not None:
        return "ok", f"local-model floor {ctx.config.local_model_floor}"
    return "warn", "no local_model_floor declared (DEC-000014 budgeting unavailable)"


def default_checks():
    """The v0.1 check registry, in stable registration order."""
    return [
        ("repository", _check_repository),
        ("config", _check_config),
        ("version-pin", _check_version_pin),
        ("profile", _check_profile),
        ("governance", _check_governance),
        ("state-tracker", _check_state),
        ("local-model-floor", _check_floor),
    ]


def build_context(repo_root=None) -> Context:
    start = Path(repo_root).resolve() if repo_root else Path.cwd()
    git_root = find_git_root(start)
    config = load_config(git_root or start)
    return Context(start=start, git_root=git_root, config=config,
                   running_version=__version__)


def run_checks(ctx: Context, checks=None):
    checks = default_checks() if checks is None else checks
    return [(name, *fn(ctx)) for name, fn in checks]


def render(results, as_json, out):
    if as_json:
        payload = [{"name": n, "status": s, "message": m} for n, s, m in results]
        json.dump(payload, out, indent=2, sort_keys=False)
        out.write("\n")
        return
    severity = {"fail": 0, "warn": 1, "ok": 2}
    for name, status, message in sorted(results, key=lambda r: (severity[r[1]], r[0])):
        out.write(f"  {status.upper():4} {name}: {message}\n")
    counts = {"ok": 0, "warn": 0, "fail": 0}
    for _, status, _ in results:
        counts[status] += 1
    out.write(f"  {counts['ok']} ok, {counts['warn']} warn, {counts['fail']} fail\n")


def run_doctor(repo_root=None, as_json=False, out=None, checks=None) -> int:
    """Run doctor; return exit code (0 = no fails, 1 = at least one fail)."""
    out = out if out is not None else sys.stdout
    ctx = build_context(repo_root)
    results = run_checks(ctx, checks=checks)
    render(results, as_json, out)
    return 1 if any(status == "fail" for _, status, _ in results) else 0
