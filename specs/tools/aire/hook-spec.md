---
title: aire hook Specification
version: 0.1.0
maintained_by: Aire System Architect (ASA)
domain_tags: [tooling, cli, governance, enforcement, hooks]
status: draft
platform: claude-code
license: Apache-2.0
covers:
  - tools/aire/hook.py
---

# Purpose
Define the `aire hook` subcommand — the **Layer 2 enforcement primitive** of `claude/harness-enforcement-spec.md`. Invoked by Claude Code as a `PreToolUse` hook, it reads a single tool-call event on stdin, evaluates it against the repository's `.aire/config.toml [harness]` typed policy, and **allows or blocks the tool call fail-closed** via its exit code. This spec owns the command surface (invocation, the event protocol, exit codes), the typed `[harness]` schema it consumes, and the evaluation algorithm. **The enforcement model, the layer tiers, the policy-as-data convention, and the fail-closed requirement are owned by `claude/harness-enforcement-spec.md`** and referenced here, never restated. **Policy location (`.aire/config.toml [harness]`, per-repo) is owned by DEC-000023.**

# Scope

## Covers
- `aire hook`: reading a `PreToolUse` event from stdin, loading `[harness]` policy, deciding allow/block, and the exit-code protocol.
- The typed `[harness]` schema this version enforces: `push_policy` and `protected_paths`.
- The evaluation algorithm per constraint type, including command argv parsing (not substring matching) and path-glob matching.
- Fail-closed behavior on policy/guard error vs allow-on-unrestricted.

## Does Not Cover
- *Why* enforcement is layered, the tier model, and the placement rule — owned by `claude/harness-enforcement-spec.md`.
- The `.claude/settings.json` hook-registration format — owned by Claude Code, not by aire.
- Constraint types beyond `push_policy` and `protected_paths` (e.g. commit-format, working-tree/STATE freshness via a `Stop` hook, conditional public/private push classification) — deferred to later sprints.
- Best-effort detection of arbitrary shell write paths (see Edge Cases): structured file tools are the primary enforcement surface; Layer 0 (filesystem perms, push-URL disabling) covers what a hook cannot.

# Invocation (Normative)

```
aire hook [--repo PATH]
```

- Reads one JSON hook event from **stdin**. `--repo` sets the repository root for policy lookup and path matching (default: current working directory; the event's `cwd` is used if present and `--repo` is absent).
- Read-only and offline: `hook` performs no writes and no network (architecture constraints, `specs/tools/aire/architecture-spec.md`). It only reads the event and the policy file and emits a decision via exit code (+ stderr reason).
- Registered as a `PreToolUse` hook command in `.claude/settings.json`; aire does not own that registration format.

# Inputs (Normative)
- **stdin** — a `PreToolUse` event as a JSON object. The fields used:
  - `tool_name` (string) — e.g. `Bash`, `Write`, `Edit`, `MultiEdit`, `NotebookEdit`.
  - `tool_input` (object) — tool-specific. For `Bash`: `command` (string). For file tools: `file_path` (string), and `notebook_path` for `NotebookEdit`.
  - `cwd` (string, optional) — fallback repo root when `--repo` is absent.
  - Other fields (`session_id`, `hook_event_name`, …) are ignored.
- **`.aire/config.toml`** `[harness]` table in the repo root (see Schema). Loaded via the existing config loader.

## The `[harness]` schema (typed)
```toml
[harness.push_policy]
mode = "human-only"   # "human-only" denies all session git pushes; "off" (or table absent) imposes no push restriction

[harness.protected_paths]
deny = ["operator.md", "private/**", ".claude/settings.json"]   # repo-relative globs; writes to a match are denied
```
- Each subtable is a **constraint type** with a fixed, typed shape. An **unknown** `[harness.*]` subtable, or a known one with an unrecognized/ill-typed field, is a **policy error** (see Fault Handling) — not silently ignored.
- A repo with no `[harness]` table is **not enrolled**: every event is allowed.

# Outputs (Normative)
The decision is carried by the **exit code** (matching the mechanism verified 2026-06-14 and Claude Code's `PreToolUse` contract):

- **Exit 0 — allow.** The tool call proceeds. Used for every event that does not match a restriction (including all unrestricted tools) and for non-enrolled repos.
- **Exit 2 — block.** Claude Code stops the tool call; the human-readable reason is written to **stderr** (Claude Code feeds exit-2 stderr back to the model). Used for a positively-identified violation and for fail-closed guard errors.
- No other exit code is used for decisions. (A non-2 nonzero exit is, in Claude Code, a *non-blocking* error — which would silently allow; therefore guard errors that must block use exit 2, never another code.)
- `aire hook` writes nothing to stdout in the exit-code protocol (a future `ask` decision MAY use structured stdout JSON; not emitted by this version).

# Responsibilities — Evaluation (Normative)
For a well-formed event and a valid policy, evaluate each enrolled constraint; **deny on the first positive match**, else allow.

## push_policy (mode = "human-only")
- Applies to `tool_name == "Bash"`. Parse `tool_input.command` into commands, splitting on shell separators (`&&`, `||`, `;`, `|`, newlines). For each segment, tokenize (shell-word split) and skip leading `env`-style `NAME=val` assignments and a leading `env` command.
- A segment is a **git push** when its command word is `git` (optionally with `-C <path>` / `-c <k=v>` options) and the first non-option subcommand token is `push`. Deny if any segment is a git push.
- This is **argv parsing, not substring matching**: `echo "git push"` (command word `echo`) is allowed; `cd x && git push` is denied. Deeply obfuscated forms (e.g. `sh -c '…'`, aliases) are an acknowledged gap — Layer 0 push-URL disabling is the structural backstop (governing spec).

## protected_paths (deny = [globs])
- Applies to the structured file tools: `Write`, `Edit`, `MultiEdit` (`tool_input.file_path`) and `NotebookEdit` (`tool_input.notebook_path`). Resolve the target path repo-relative; deny if it matches any `deny` glob (`**` spanning directories, per `pathlib`/`fnmatch` semantics stated in the spec).
- For `tool_name == "Bash"`, a **conservative best-effort** check MAY deny when a protected path appears as an argument to an obvious in-place write (`>`, `>>`, `tee`, `truncate`, `sed -i`, `cp`/`mv` destination). Misses here are an acknowledged gap (Edge Cases), not a correctness failure — the structured tools are the guaranteed surface.

# Edge Cases / Fault Handling (Normative)
- **No `.aire/config.toml`, or no `[harness]` table** → not enrolled → **exit 0** (allow), silently. Enrollment is opt-in.
- **`[harness]` present but malformed** (TOML parse error, unknown constraint subtable, ill-typed field) → **policy/guard error → exit 2 (block)** with a loud stderr message naming the problem. A broken guard MUST NOT silently allow (governing spec, fail-closed). Recovery: fix the policy (or remove the hook registration). Operationally the live policy is unit-tested before wiring, so this state reflects an edit-in-progress, not normal operation.
- **stdin is not valid JSON** → integration fault → **exit 2 (block)** + loud stderr. (Correct wiring always sends a JSON object; this path should not occur in practice and is verified during dogfood.)
- **Valid-JSON event missing `tool_name`/`tool_input`, or a tool/shape no constraint covers** → this is *not* an error and *not* a violation → **exit 0** (allow). Only a positively-identified violation or a guard error blocks; unrecognized-but-well-formed events flow. This is what keeps a live hook from bricking a session on benign tool calls.
- **Multiple constraints match** → deny (first match), reason names the constraint.

# Test Strategy
Unit tests (`tests/tools/aire/test_hook.py`, stdlib `unittest`), driving `aire hook` with JSON event fixtures and `[harness]` policy fixtures in temp repos:
- **push_policy:** `git push`, `git push origin main`, `git -C /x push`, `cd x && git push` → exit 2; `git status`, `git log`, `echo "git push"`, `echogit push` → exit 0; `push_policy` absent → push allowed.
- **protected_paths:** `Write`/`Edit`/`MultiEdit`/`NotebookEdit` to a denied glob → exit 2; to a non-denied path → exit 0; nested `**` match; Bash best-effort `echo x > operator.md` → exit 2.
- **Fail-closed:** malformed `[harness]` → exit 2 + message; non-JSON stdin → exit 2; no `[harness]` → exit 0; valid event for an unrestricted tool (`Read`) → exit 0.
- **Protocol:** block path uses exit 2 (never another nonzero); reason present on stderr; nothing on stdout.

# Completion Criteria
- `tools/aire/hook.py` implements the above; `aire hook` is dispatchable; `tests/tools/aire/test_hook.py` passes.
- Coverage maps (`covers: tools/aire/hook.py`; `aire map` clean).
- aire's own `.aire/config.toml [harness]` declares `push_policy = human-only` and `protected_paths`, the hook is registered in `.claude/settings.json`, and a real protected-path write is **blocked in-session** (dogfood) with a piped real-event demonstration of push denial.
- All repo gates green.

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-06-14 (v0.1.0)
- summary: Initial spec. Defines `aire hook` as the Layer 2 PreToolUse enforcement primitive of claude/harness-enforcement-spec.md: the stdin event protocol, the typed `[harness]` schema (`push_policy`, `protected_paths`), argv-based git-push detection, protected-path glob matching on structured file tools, the exit-code decision protocol (0 allow / 2 block), and fail-closed-on-guard-error. Constraint types beyond these two and the `ask`/conditional/Stop-hook cases are deferred.
