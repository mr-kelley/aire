---
title: aire map Specification
version: 0.1.0
maintained_by: Aire System Architect (ASA)
domain_tags: [tooling, cli, coverage, mapping]
status: draft
platform: claude-code
license: Apache-2.0
covers:
  - tools/aire/map.py
---

# Purpose
Define the `aire map` subcommand — the CLI surface for spec coverage. This spec owns the command surface (arguments, dispatch, exit codes) and the `code` engine's extraction rules. The **coverage models, the mapper interface contract, binding declarations, and the recordless/stale/conflict semantics are owned by `claude/coverage-spec.md`** and referenced here, never restated (Rule Ownership, `claude/spec-spec.md`). `map check` (gate) and `map report` (the derived map) are both covered.

# Scope

## Covers
- `aire map check`: binding resolution, coverage verification, exit-code semantics.
- `aire map report`: the derived coverage map (Markdown for humans, `--json` for machines), deterministic ordering.
- The `code` coverage engine: how public symbols are extracted from source and cross-referenced against `covers:` declarations.

## Does Not Cover
- Coverage model definitions (`code`/`artifact`/`advisory`/`none`), the mapper interface contract, the binding-declaration homes and resolution order, and the classification of uncovered/stale/conflict units — all owned by `claude/coverage-spec.md`.
- Spec `covers:` field syntax (owned by `claude/coverage-spec.md`; consumed here).
- The `artifact` and `advisory` engines — deferred library contributions (see Engine Scope below).

# Engine Scope (v0.1)

`aire map` v0.1 implements the **`code`** engine only — the one this repo needs. Per the coverage contract's incremental-engine rule, the `artifact` and `advisory` engines are future contributions *into the shared library* (`claude/coverage-spec.md`, Mapper Library Rule), added when a governed repo first needs them.

A binding whose `model` is not yet implemented does not silently pass: `map check` **fails closed** (exit 2, naming the unimplemented model) rather than reporting false-complete coverage. The `none` model is implemented as the trivial case (zero units; the header justification is the audit's concern, not the mapper's).

# Binding Resolution

The set of bindings to evaluate is assembled per the resolution order in `claude/coverage-spec.md` (role headers first, then `.aire/config.toml` `[[coverage]]`). For this repo — role-less — bindings come from `.aire/config.toml` `[[coverage]]` (DEC-000019). When no binding is found at all, `map` reports a misconfiguration (exit 2) rather than claiming vacuous coverage.

# The `code` Engine (Normative)

## Coverage units
For each `.py` file under a binding's `paths`, the engine extracts **public** coverage units by parsing the source with the standard-library `ast` module (no third-party parser):

- module-level **functions** (`def` / `async def`) whose name does not start with `_`;
- module-level **classes** (`class`) whose name does not start with `_`;
- public **methods** (a `def` directly in a public class body) whose name does not start with `_`.

Unit identifier: `<repo-relative-path>` plus a symbol suffix — `path.py:func`, `path.py:Class`, `path.py:Class.method`. A file with no public symbols contributes zero units (it is trivially covered). Names beginning with `_` (including dunders) are private and are not units.

## Cross-reference against `covers:`
The engine reads the `covers:` list from the YAML header of every spec under `specs/` (and `claude/`). For a `code` binding it considers only `covers:` entries that fall **within that binding's `paths`**; entries outside (e.g., a non-`.py` artifact, or another binding's domain) are ignored by this engine, not treated as errors.

A `covers:` entry is either:
- a **whole-file** path (`tools/aire/cli.py`) — covers every unit extracted from that file;
- a **symbol** path (`tools/aire/cli.py:console_main`) — covers exactly that unit.

Each unit's covering spec is the spec whose `covers:` entry matches it. Intent is **declared, never inferred** (coverage-spec): the engine matches declared `covers:` against extracted symbols and never guesses a covering spec from naming or location.

## Findings and defects
Per `claude/coverage-spec.md` (Edge Cases):
- **Uncovered unit** — an extracted unit no `covers:` entry claims. Listed; fails the gate.
- **Stale declaration** — a `covers:` entry, within a binding's paths, that matches no extracted unit (file absent, or symbol gone). Listed as a spec defect; fails the gate.
- **Ownership conflict** — two specs' `covers:` entries claim the same unit (violates Rule Ownership). Listed; fails the gate.
- **Missing binding paths** — a binding `paths` entry that does not exist on disk is a *configuration error* (not a finding): `map check` fails closed with exit 2, never reporting false-complete coverage.

## Staleness (report only, best-effort)
`map report` includes a per-unit staleness indicator where derivable: a unit is **stale** when the last commit touching its covering spec predates the last commit touching the unit's source file (file granularity, via `git log -1` committer dates — deterministic canonical state). Where not derivable (uncommitted file, no git, no covering spec) the indicator is `null`. Staleness never affects `map check`'s exit code; it is advisory signal in the report.

# Invocation (Normative)

```
aire map check
aire map report [--json]
```

- `aire map` with no action: usage to stderr, exit 2.
- Read-only: `map` performs no writes (it emits reports to stdout only) and no network, per the architecture constraints and the coverage-spec mapper rules.

## `map check`
Verifies coverage across all resolved bindings. Output (stdout) lists any uncovered units, stale declarations, and ownership conflicts, in deterministic order. Suitable for hook gating (PreToolUse on commit, Stop checks).

### Exit codes (check)
- **0**: coverage is total — every unit covered, no stale declarations, no conflicts.
- **1**: findings exist — uncovered units, stale declarations, or ownership conflicts (the coverage invariant does not hold). A substantive negative, gate-style.
- **2**: misconfiguration — no binding found, a binding path missing, an unimplemented engine, or an unreadable `.aire/config.toml`. Fails closed (never reports false-complete coverage).

## `map report`
Emits the full coverage map — the derived artifact (`claude/coverage-spec.md`): regenerable, never hand-edited, never required for correctness. Default output is Markdown (human); `--json` emits the machine map and is the only thing on stdout in that mode. Per-unit fields: `id`, `kind` (function|class|method), `spec` (covering spec path or `null`), `stale` (boolean or `null`). Output is **deterministic**: units ordered by path ascending then symbol ascending; no timestamps, hostnames, or run identifiers in the JSON body.

### Exit codes (report)
- **0**: map emitted.
- **2**: the map cannot be built (misconfiguration, as for check). `map report` does not gate on findings — `map check` is the gate; `report` is the artifact.

# Inputs
- Command arguments above.
- `.aire/config.toml` `[[coverage]]` bindings (and role headers, where present).
- Spec `covers:` declarations under `specs/` and `claude/`.
- Source files under each binding's `paths`; `git` (for staleness, best-effort).

# Outputs
- `map check`: a coverage verdict on stdout + exit code.
- `map report`: the derived coverage map (Markdown or `--json`) on stdout.
- No writes to the work tree; no network.

# Edge Cases / Fault Handling
- **No `[[coverage]]` binding and no role binding**: exit 2 (misconfiguration), not vacuous exit 0.
- **Binding path missing on disk**: exit 2 (configuration error), distinct from an uncovered-unit finding.
- **Unimplemented engine** (`artifact`/`advisory` in v0.1): exit 2, naming the model; fails closed.
- **`none` model**: zero units; contributes no findings.
- **Source file with a syntax error**: exit 2 (the source cannot be parsed to extract units; fail closed rather than under-report).
- **Spec header unparseable**: its `covers:` entries are skipped with a diagnostic to stderr; a malformed spec does not crash the run, but its declared coverage is absent (so its units read as uncovered — surfaced, not hidden).
- **`aire map` with no action**: usage to stderr, exit 2.

# Test Strategy
Unit tests (stdlib `unittest`, DEC-000016) in `tests/tools/aire/test_map.py`, using temporary fixture trees (source files + spec stubs with `covers:` headers + a `.aire/config.toml`):
- **Extraction**: public functions, classes, and public methods become units; `_`-prefixed names and dunders do not; a file with no public symbols yields no units.
- **Whole-file coverage**: a `covers: path.py` entry covers all units in that file → `check` exits 0.
- **Symbol coverage**: a `covers: path.py:sym` entry covers only that unit; a sibling public symbol is then uncovered → `check` exits 1 and lists it.
- **Stale declaration**: a `covers:` entry naming a missing symbol/file (within paths) → exit 1, listed as stale.
- **Ownership conflict**: two specs covering the same unit → exit 1, listed as a conflict.
- **Misconfiguration**: no binding → exit 2; a binding path that does not exist → exit 2; an `artifact` binding (unimplemented) → exit 2.
- **Determinism**: `map report --json` is byte-identical across repeated runs on a fixed fixture; units are path-then-symbol ordered.
- **Read-only**: a `check`/`report` run leaves the fixture tree unchanged.
Tests follow the spec-to-test mapping in `claude/spec-spec.md`.

# Completion Criteria
- `aire map check` verifies coverage from declared bindings and `covers:` declarations, failing closed on misconfiguration and listing uncovered/stale/conflict units on findings.
- `aire map report` emits a deterministic Markdown/JSON coverage map.
- All tests pass.
- Demonstrated on this repo: with one `[[coverage]]` code binding over `tools/aire/`, `map check` exits 0 (every CLI source unit covered by a `specs/tools/aire/*.md` spec), and `map report` renders the map — satisfying NORTHSTAR success criterion 4 (mechanical spec coverage) on aire itself.

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-06-13 (v0.1.0)
- summary: Initial `aire map` command spec. Command surface (check/report, exit codes) and the `code` engine's extraction + cross-reference rules; coverage models, binding homes/resolution order, and uncovered/stale/conflict semantics deferred to claude/coverage-spec.md (Rule Ownership). v0.1 implements the code engine only; artifact/advisory are deferred library contributions and fail closed (exit 2) until implemented. Binding for this role-less repo comes from .aire/config.toml [[coverage]] (DEC-000019).
