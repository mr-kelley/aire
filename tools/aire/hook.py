"""aire hook — Layer 2 PreToolUse enforcement primitive.

Governing spec: specs/tools/aire/hook-spec.md
Model: claude/harness-enforcement-spec.md (Layer 2). Policy location: DEC-000023
(per-repo .aire/config.toml [harness]). Decision is carried by the exit code:
0 = allow, 2 = block (fail-closed on a guard error). No network, no writes.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import shlex
import sys
import tomllib
from pathlib import Path

ALLOW = 0
BLOCK = 2

KNOWN_CONSTRAINTS = {"push_policy", "protected_paths"}
_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_SEPARATORS = re.compile(r"&&|\|\||;|\||\n")
# structured file tools -> the tool_input key holding the target path
_FILE_TOOLS = {
    "Write": "file_path",
    "Edit": "file_path",
    "MultiEdit": "file_path",
    "NotebookEdit": "notebook_path",
}
# crude markers that a Bash command writes a file (best-effort protected-path check)
_BASH_WRITE_HINTS = (">", "tee ", "truncate ", "sed -i", "cp ", "mv ", "dd ")


class PolicyError(Exception):
    """The [harness] policy is malformed — the guard cannot be trusted, so block."""


# --------------------------------------------------------------------------- #
# policy loading
# --------------------------------------------------------------------------- #
def _load_harness(root: Path):
    """Return the validated [harness] table, or None if the repo is not enrolled.

    Raises PolicyError on an unreadable config or a malformed [harness] table.
    """
    path = root / ".aire" / "config.toml"
    if not path.is_file():
        return None
    try:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except (tomllib.TOMLDecodeError, OSError) as exc:
        raise PolicyError(f".aire/config.toml could not be read: {exc}")
    harness = data.get("harness")
    if harness is None:
        return None
    if not isinstance(harness, dict):
        raise PolicyError("[harness] must be a table")
    for key, val in harness.items():
        if key not in KNOWN_CONSTRAINTS:
            raise PolicyError(f"unknown harness constraint [harness.{key}]")
        if not isinstance(val, dict):
            raise PolicyError(f"[harness.{key}] must be a table")
    return harness


# --------------------------------------------------------------------------- #
# push_policy
# --------------------------------------------------------------------------- #
def _check_push_policy(cfg: dict, tool_name: str, tool_input: dict):
    mode = cfg.get("mode", "off")
    if not isinstance(mode, str):
        raise PolicyError("[harness.push_policy].mode must be a string")
    if mode == "off":
        return None
    if mode != "human-only":
        raise PolicyError(f"[harness.push_policy].mode unsupported: {mode!r}")
    if tool_name != "Bash":
        return None
    command = tool_input.get("command", "")
    if isinstance(command, str) and _is_git_push(command):
        return "push_policy: session git push denied — pushing is human-only (DEC-000011)."
    return None


def _is_git_push(command: str) -> bool:
    for segment in _SEPARATORS.split(command):
        segment = segment.strip()
        if not segment:
            continue
        try:
            tokens = shlex.split(segment)
        except ValueError:
            tokens = segment.split()
        if _tokens_are_git_push(tokens):
            return True
    return False


def _tokens_are_git_push(tokens: list[str]) -> bool:
    i = 0
    # skip leading VAR=val assignments and an optional `env VAR=val ...`
    while i < len(tokens) and _ASSIGN.match(tokens[i]):
        i += 1
    if i < len(tokens) and tokens[i] == "env":
        i += 1
        while i < len(tokens) and _ASSIGN.match(tokens[i]):
            i += 1
    if i >= len(tokens) or tokens[i] != "git":
        return False
    i += 1
    # skip git global options (-C <path>, -c <kv>, --git-dir=..., etc.)
    while i < len(tokens) and tokens[i].startswith("-"):
        opt = tokens[i]
        i += 1
        if opt in ("-C", "-c") and i < len(tokens):
            i += 1  # consume the option's value
    return i < len(tokens) and tokens[i] == "push"


# --------------------------------------------------------------------------- #
# protected_paths
# --------------------------------------------------------------------------- #
def _check_protected_paths(cfg: dict, root: Path, tool_name: str, tool_input: dict):
    deny = cfg.get("deny", [])
    if not isinstance(deny, list) or not all(isinstance(g, str) for g in deny):
        raise PolicyError("[harness.protected_paths].deny must be a list of strings")
    if not deny:
        return None
    if tool_name == "Bash":
        return _bash_protected(deny, tool_input.get("command", ""))
    key = _FILE_TOOLS.get(tool_name)
    if key is None:
        return None
    target = tool_input.get(key)
    if not isinstance(target, str) or not target:
        return None
    rel = _relpath(target, root)
    if rel is None:
        return None
    for glob in deny:
        if fnmatch.fnmatchcase(rel, glob):
            return f"protected_paths: writing {rel} is denied (matches {glob!r})."
    return None


def _bash_protected(deny: list[str], command):
    """Best-effort: deny a Bash command that appears to write a literal protected path."""
    if not isinstance(command, str) or not any(h in command for h in _BASH_WRITE_HINTS):
        return None
    for glob in deny:
        if any(ch in glob for ch in "*?[]"):
            continue  # only literal paths are checked on the Bash surface
        if glob in command:
            return f"protected_paths: command appears to write protected path {glob!r}."
    return None


def _relpath(target: str, root: Path):
    """Repo-relative POSIX path for `target`, or None if outside the repo. No filesystem access."""
    p = Path(target)
    if not p.is_absolute():
        p = root / p
    try:
        rel = os.path.relpath(os.path.normpath(str(p)), os.path.normpath(str(root)))
    except ValueError:
        return None
    if rel == ".." or rel.startswith(".." + os.sep):
        return None
    return Path(rel).as_posix()


# --------------------------------------------------------------------------- #
# evaluation + entry point
# --------------------------------------------------------------------------- #
def _evaluate(harness: dict, root: Path, tool_name, tool_input: dict):
    if not isinstance(tool_name, str):
        return None
    if "push_policy" in harness:
        reason = _check_push_policy(harness["push_policy"], tool_name, tool_input)
        if reason:
            return reason
    if "protected_paths" in harness:
        reason = _check_protected_paths(harness["protected_paths"], root, tool_name, tool_input)
        if reason:
            return reason
    return None


def _root(repo, event: dict) -> Path:
    if repo:
        return Path(repo)
    cwd = event.get("cwd")
    if isinstance(cwd, str) and cwd:
        return Path(cwd)
    return Path.cwd()


def run_hook(repo=None, stdin=None) -> int:
    """Read one PreToolUse event from stdin, evaluate it, return an exit code (0 allow / 2 block)."""
    stream = stdin if stdin is not None else sys.stdin
    raw = stream.read()
    try:
        event = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        print("aire hook: stdin was not valid JSON — blocking fail-closed", file=sys.stderr)
        return BLOCK
    if not isinstance(event, dict):
        print("aire hook: event was not a JSON object — blocking fail-closed", file=sys.stderr)
        return BLOCK
    root = _root(repo, event)
    try:
        harness = _load_harness(root)
        if harness is None:
            return ALLOW  # not enrolled
        tool_input = event.get("tool_input")
        if not isinstance(tool_input, dict):
            tool_input = {}
        reason = _evaluate(harness, root, event.get("tool_name"), tool_input)
    except PolicyError as exc:
        print(f"aire hook: harness policy error — blocking fail-closed: {exc}", file=sys.stderr)
        return BLOCK
    if reason:
        print(f"aire hook: {reason}", file=sys.stderr)
        return BLOCK
    return ALLOW
