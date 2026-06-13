---
title: aire doctor Specification
version: 0.1.1
maintained_by: Aire System Architect (ASA)
domain_tags: [tooling, cli, doctor, validation]
status: draft
platform: claude-code
license: Apache-2.0
covers:
  - tools/aire/doctor.py
---

# Purpose
Define `aire doctor` — the environment and repository validation subcommand. `doctor` answers one question: *is this repository correctly set up to be governed by Aire, and can the tooling operate here?* It is read-only, advisory, and the natural first thing to run in any Aire repo. It is the surface where misconfigurations (including the kind that silently blocked PR #6 — see DEC-000012) become visible.

# Scope

## Covers
- The check set `doctor` runs and how it reports them.
- Exit-code semantics for a diagnostic (non-gate) command.
- The check registry pattern that lets future checks be added without restructuring.

## Does Not Cover
- The deep governance checks owned by `claude/audit-spec.md` (that is `aire audit`; `doctor` is environment-level, audit is governance-level).
- Coverage verification (`aire map`, `claude/coverage-spec.md`).
- Fixing anything — `doctor` never modifies the repository.

# Responsibilities (Normative)

`doctor` runs a registry of independent checks, each returning a status and a message, and prints a grouped report. It is **read-only**: it makes no writes and no network calls.

## Check statuses
- **ok** — the condition holds.
- **warn** — a non-blocking concern (something unset, a soft recommendation).
- **fail** — a condition that would block governed operation (e.g., version pin unsatisfied, malformed config).

## Check set (v0.1)
1. **Repository present** — the working directory is inside a git repository. (fail if not)
2. **Config readable** — `.aire/config.toml` is absent (warn: using defaults) or parses (ok); a parse error is fail.
3. **CLI version pin** — if `aire_version_min` is set, compare to the running CLI version: satisfied (ok) or unsatisfied (fail, naming required vs running).
4. **Promotion profile** — `profile` is a recognized value A or B (ok), unset (warn: defaulting per project), or unrecognized (fail).
5. **Governance present** — a `claude/` governance directory exists with at least the role base and spec-spec (ok), or is absent/partial (warn — the repo may govern from a parent or copied location).
6. **State tracker present** — `STATE.md` exists at repo root (ok) or is absent (warn — `claude/state-tracker-spec.md` expects it).
7. **Local-model floor** — `local_model_floor` is set (ok, echo the value) or unset (warn — DEC-000014 governance-load budgeting cannot be checked without it).

The registry is extensible: future checks (coverage binding validity, pin currency against governance, branch-protection sanity) register here without changing the dispatch or report code.

## Reporting
- Human mode (default): one line per check — `STATUS  name: message` — grouped ok/warn/fail, with a summary tail (`N ok, M warn, K fail`).
- `--json`: a deterministic JSON array of `{name, status, message}` objects ordered by check registration, with no timestamps or host data (per architecture-spec constraint 4).

## Exit codes
`doctor` is diagnostic, not a gate, but its exit code is scriptable:
- **Exit 0**: no `fail` results (warns allowed).
- **Exit 1**: one or more `fail` results.
- **Exit 2**: `doctor` itself could not run (e.g., invoked with bad arguments).

This lets a hook or CI call `aire doctor` as a soft precondition while keeping the gate semantics (exit 1 = substantive negative) consistent with the architecture spec.

# Inputs
- Optional `--json` flag.
- Repository working directory; `.aire/config.toml`; presence of `claude/`, `STATE.md`; the running CLI version.

# Outputs
- Grouped check report on stdout (human or JSON).
- Exit code per above.
- No writes, no network.

# Edge Cases / Fault Handling
- **Not in a repo**: check 1 fails; remaining checks still run where meaningful (config/version are repo-independent), so the report is maximally useful in one pass.
- **Malformed config**: check 2 fails with the parse error; checks depending on config (3, 4, 7) report `warn: config unreadable` rather than crashing.
- **Partial governance**: check 5 warns rather than fails — a repo may legitimately reference governance copied elsewhere.
- **`--json` requested**: only JSON on stdout; any diagnostics go to stderr.

# Test Strategy
Unit tests (stdlib `unittest`, per DEC-000016) in `tests/tools/aire/test_doctor.py`, using temporary-directory fixtures simulating repo states:
- Each check independently: ok / warn / fail paths (e.g., missing repo, absent vs malformed vs valid config, satisfied vs unsatisfied version pin, each profile value, governance present/absent, STATE.md present/absent, floor set/unset).
- Aggregate exit code: 0 with only warns, 1 with any fail.
- `--json` output is valid JSON, ordered by registration, and byte-identical across repeated runs on fixed inputs (determinism).
- Read-only guarantee: a check run against a fixture leaves the fixture's file tree unchanged.

# Completion Criteria
- `aire doctor` runs on this repository and reports the seven v0.1 checks.
- Exit codes and `--json` determinism match this spec; all tests pass.
- The check registry accepts a new check via registration alone (verified by a test adding a dummy check).

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-06-13 (v0.1.1)
- summary: Test Strategy switched from pytest to stdlib unittest (DEC-000016). Behavior unchanged; verified against implementation (22-test suite green; `aire doctor` reports 6 ok / 1 warn / 0 fail on this repo, the warn being the undeclared local-model floor).
- time: 2026-06-13 (v0.1.0)
- summary: Initial `aire doctor` spec. Read-only environment/repo validation with an extensible check registry; seven v0.1 checks including the CLI version pin (architecture-spec) and the DEC-000014 local-model floor. Diagnostic exit-code semantics (0 warns-only / 1 any-fail / 2 tool-error). Motivated in part by DEC-000012: misconfigurations should be visible, not silent.
