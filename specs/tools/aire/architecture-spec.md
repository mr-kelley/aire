---
title: Aire CLI Architecture Specification
version: 0.1.4
maintained_by: Aire System Architect (ASA)
domain_tags: [tooling, cli, architecture]
status: draft
platform: claude-code
license: Apache-2.0
covers:
  - tools/aire/__init__.py
  - tools/aire/__main__.py
  - tools/aire/cli.py
  - tools/aire/config.py
  - tools/pyproject.toml
---

# Purpose
Define the structure, invocation model, and inviolable constraints of the `aire` command-line tool — the single system-installed reference implementation of Aire's governance tooling (per DEC-000010). The CLI hosts the subcommands that enforce and report on governance: `map` (coverage), `history` (promotion records), `audit` (liveness), `digest` (constraints), `doctor` (environment), and `hook` (harness shims). This spec owns the package skeleton, the entry point, subcommand dispatch, and the configuration model; each subcommand has its own spec.

# Scope

## Covers
- Package layout and the console entry point.
- Subcommand dispatch and the shared invocation contract (arguments, exit codes, output streams).
- The per-repo configuration model (`.aire/config.toml`) and CLI version pinning.
- The architectural constraints from DEC-000010 that every subcommand inherits.

## Does Not Cover
- Individual subcommand behavior (owned by each subcommand's spec: `doctor-spec.md`, `history-spec.md`, and future `map`/`audit`/`digest`/`hook` specs).
- What the subcommands check or produce (owned by the governance specs they implement: `claude/coverage-spec.md`, `claude/promotion-record-spec.md`, `claude/audit-spec.md`).
- Installation and packaging policy beyond the entry-point declaration.

# Architectural Constraints (Normative — from DEC-000010)

These bind every subcommand. They are the reason the tool exists in the shape it does.

1. **Never an orchestrator, never a daemon.** The CLI is a deterministic, idempotent tool invoked and exited. It runs no background process, opens no listening socket, schedules nothing. Roles orchestrate; hooks automate; this binary executes and returns.
2. **Generic binary, per-repo data.** No project-specific behavior is compiled in. All project specifics (promotion profile, CLI version floor, local-model context floor, remote classifications) live in committed repo data — primarily `.aire/config.toml` — and in artifacts the governance specs already define (role coverage bindings, spec `covers:` fields).
3. **Stateless over canonical state.** The CLI reads repo state (files, git, config) and writes only derived artifacts (reports, maps) and governance records (promotion tags). It holds no database and no state between invocations. Re-running against unchanged inputs yields observationally identical output.
4. **Deterministic output.** All machine-readable output uses stable ordering (path ascending, then symbol/id ascending) and contains no timestamps, hostnames, or run-specific identifiers in its body. Identical canonical state produces byte-identical output.
5. **Gates fail closed.** A subcommand acting as a gate (e.g., `map check`, a promotion guard) exits nonzero — denying the action — when it cannot verify the invariant, including when its own inputs are missing or malformed. Unavailability of a check is never treated as the check passing.
6. **No network.** The CLI makes no network calls. It does not push, fetch, authenticate, or contact any service. (Consistent with git hygiene: publishing is human-only.)

   This is not an absence of a collaboration story — it *is* the collaboration story. Cross-machine, inter-role collaboration in Aire flows through external, role-orchestrated, transport-agnostic **pipelines** (Forgejo PRs/Issues, MQTT, synced repos, etc.), never through direct binary-to-binary networking (per DEC-000015). The binary stays network-silent *precisely so that* inter-role communication is carried by an auditable pipeline rather than an ephemeral dark channel — the pipeline exchange becomes canonical, reviewable state, the same way decisions and promotions do. The binary's role in collaboration is to be an excellent producer of **portable, verifiable artifacts** (deterministic, self-contained output) that any pipeline can carry and any remote binary can consume. Because the binary knows nothing of transport, the transport choice stays the operator's and is swappable without touching the tool. Transport is a concern of the role and the pipeline (the judgment and automation layers), never of the deterministic primitive.

# Package Layout

```
tools/
  pyproject.toml       # package definition; console entry point `aire`
  aire/
    __init__.py        # version (single source of truth; pyproject reads it)
    __main__.py        # `python -m aire` zero-install entry
    cli.py             # entry point: argument parsing, subcommand dispatch
    config.py          # .aire/config.toml loading + version-pin check
    doctor.py          # `aire doctor`        (doctor-spec.md)
    history.py         # `aire history ...`   (history-spec.md)
    map.py             # `aire map ...`       (map-spec.md)
    audit.py           # `aire audit`         (audit-spec.md)
    digest.py          # `aire digest ...`    (digest-spec.md)
    # hook.py                                 (future sprint)
```

The console entry point `aire` maps to `aire.cli:console_main`; `python -m aire`
maps to `aire.__main__`. The package is self-contained under `tools/`
(`pip install -e tools/`), keeping the governance repo from becoming a Python
package itself. Version lives only in `aire.__init__.__version__`; `pyproject.toml`
reads it dynamically (single ownership).

# Invocation Contract (Normative)

```
aire [--version] [--help] <subcommand> [subcommand-args...]
```

- `aire` with no subcommand prints usage to stdout and exits 0.
- `aire --version` prints the CLI version (from `__init__.py`) and exits 0.
- Unknown subcommand: error to stderr, exit 2.
- Each subcommand declares its own arguments and exit codes in its spec. Shared conventions:
  - **Exit 0**: success / invariant holds.
  - **Exit 1**: a gate's invariant does NOT hold (e.g., uncovered units, missing promotion record) — a substantive negative result, not a tool error.
  - **Exit 2**: tool/usage error (bad arguments, missing/malformed inputs, misconfiguration).
- Human-readable output goes to stdout; diagnostics and errors to stderr. Machine-readable output (`--json` where a subcommand offers it) goes to stdout and is the only thing on stdout in that mode.

# Configuration Model (Normative)

Per-repo configuration lives at `.aire/config.toml` (committed). All fields optional; the CLI supplies safe defaults and `doctor` reports what is unset.

```toml
# .aire/config.toml
aire_version_min = "0.1.0"   # minimum CLI version this repo requires (DEC-000008 pattern, extended to tooling)
profile = "B"                # promotion profile A | B (claude/claude.git-hygiene.md)
local_model_floor = 8192     # smallest model context window a role here must serve (DEC-000014); informational for doctor
```

- **Version pin**: when `aire_version_min` is set and the running CLI is older, gate subcommands fail closed (exit 2) and `doctor` reports the mismatch. This extends DEC-000008's pin-and-reconcile pattern from governance specs and roles to the tooling itself.
- Config parsing uses stdlib `tomllib`. A malformed config is a misconfiguration: gates fail closed; `doctor` reports the parse error.

# Inputs
- Command-line arguments.
- `.aire/config.toml` (optional).
- Repo state as each subcommand requires (files, `git`, governance artifacts).

# Outputs
- Subcommand results on stdout (human or `--json`).
- Diagnostics on stderr.
- Process exit code per the contract above.
- Governance records / derived artifacts as each subcommand specifies (never written by the dispatch layer itself).

# Edge Cases / Fault Handling
- **No subcommand / `--help`**: usage to stdout, exit 0.
- **Unknown subcommand**: error to stderr, exit 2.
- **Not inside a repo / no `.aire/config.toml`**: not fatal at dispatch; each subcommand decides. `doctor` explicitly reports the situation; gates fail closed if they need config they cannot find.
- **Version pin unsatisfied**: gates exit 2 with a clear message naming required vs running version; non-gate informational commands (`--version`, `doctor`) still run so the user can diagnose.
- **Malformed `.aire/config.toml`**: treated as misconfiguration (exit 2 for gates); `doctor` surfaces the parse error rather than crashing.

# Test Strategy
Unit tests use the standard-library `unittest` framework (no test dependency, per DEC-000016) in `tests/tools/aire/`, runnable via `python -m unittest discover -s tests/tools/aire`:
- Dispatch: no-subcommand, `--version`, unknown-subcommand exit codes and streams.
- Config: load present/absent/malformed `.aire/config.toml`; version-pin comparison (older, equal, newer running version, uneven lengths).
- Determinism: a representative `--json` output is byte-identical across repeated runs on fixed inputs, and ordered by check registration.
- Constraint guards: assert no module imports a networking or server library (a structural test enforcing constraints 1 and 6).
Tests follow the spec-to-test mapping in `claude/spec-spec.md`. Each subcommand's own behavioral tests live with its spec.

# Completion Criteria
- `aire` is installable (`pip install -e tools/` or equivalent) and exposes the `aire` console command.
- Dispatch, config loading, and version-pin behavior match this spec; all tests pass.
- `aire --version` and `aire doctor` run on this repository.
- `covers:` units above are implemented and spec-aligned.

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-06-14 (v0.1.4)
- summary: Dispatch extended for `aire digest` (sprint 07): cli.py routes `digest render` / `digest check`. Package layout adds digest.py (digest-spec.md); only hook.py remains future. No change to the invocation contract or constraints.
- time: 2026-06-13 (v0.1.3)
- summary: Dispatch extended for `aire audit` (sprint 06): cli.py routes `audit`. Package layout adds audit.py (audit-spec.md). No change to the invocation contract or constraints.
- time: 2026-06-13 (v0.1.2)
- summary: Dispatch extended for `aire map` (sprint 05): cli.py routes `map check` / `map report`; config.py gains the `[[coverage]]` binding loader (DEC-000019). Package layout updated — map.py is implemented (map-spec.md); history.py is no longer "future". No change to the invocation contract or constraints.
- time: 2026-06-13 (v0.1.1)
- summary: Reconciled with implementation. pyproject.toml lives at tools/ (self-contained package; repo root is not a Python package); added tools/aire/__main__.py for zero-install `python -m aire`; version single-sourced from __init__ via pyproject dynamic; Test Strategy switched from pytest to stdlib unittest (DEC-000016).
- time: 2026-06-13 (v0.1.0)
- summary: Initial Aire CLI architecture spec. Implements the DEC-000010 constraints as normative inheritance for all subcommands; defines package layout, invocation contract, exit-code conventions, and the .aire/config.toml model with CLI version pinning (DEC-000008 pattern extended to tooling). First Profile B deliverable in the aire repo.
