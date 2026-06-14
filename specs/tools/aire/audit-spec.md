---
title: aire audit Specification
version: 0.1.0
maintained_by: Aire System Architect (ASA)
domain_tags: [tooling, cli, audit, drift]
status: draft
platform: claude-code
license: Apache-2.0
covers:
  - tools/aire/audit.py
---

# Purpose
Define the `aire audit` subcommand — the CLI surface that runs the **mechanical** half of the governance liveness audit. This spec owns the command surface (arguments, exit codes, report format, the v0.1 check coverage, and not-applicable handling). The **check set, severities, cadence, and disposition rules are owned by `claude/audit-spec.md`** and referenced here, never restated (Rule Ownership, `claude/spec-spec.md`). The *judgment* checks (exercised / agreement / necessity) are a Claude-session walk, not CLI-automated, per that spec.

# Scope

## Covers
- `aire audit`: running the mechanical checks, aggregating findings, rendering the report, exit-code semantics.
- The per-check implementation notes specific to this CLI (how each mechanical check is computed, what it reuses).
- Not-applicable handling: a check whose inputs are absent reports `na` with a reason, never a false pass.

## Does Not Cover
- The nine mechanical checks' definitions, the judgment checks, cadence, and finding disposition (owned by `claude/audit-spec.md`).
- Coverage mechanics (owned by `claude/coverage-spec.md`; check 1 invokes `aire map`).
- Promotion-record validity rules and recordless-merge classification (owned by `claude/promotion-record-spec.md`; check 7 reuses `aire history report`).

# Findings Model (Normative)

Each check yields zero or more findings. A finding carries: the **check** name, a **severity**, a **location** (repo-relative path, optionally `:line`, or `-`), and a **message**.

Severities (from `claude/audit-spec.md`):
- **defect** — an invariant is violated; must be fixed. The only severity that fails the gate.
- **drift** — migration-pending or a non-breaking lag (e.g., a minor/patch pin gap); reported with a count, not a hard fail.
- **candidate** — a dead-letter / judgment-tier flag for human review (e.g., a decision outcome left `unknown`).
- **na** — the check's inputs are absent in this repo; reported with the reason, never silently dropped.

# Mechanical Checks — CLI Realization (Normative)

The checks are defined in `claude/audit-spec.md`; this is how `aire audit` computes each. A check that cannot run reports `na` with a reason.

1. **coverage** — invokes the `map` engine over the repo's resolved coverage bindings; each uncovered unit, stale declaration, and ownership conflict is a **defect**. No binding declared → `na`.
2. **spec-index** — every `specs/**/*.md` (excluding `INDEX.md`) appears as a row in `specs/INDEX.md` and every `specs/`-rooted row resolves to a file (**defect** on either gap); the row paths are ascending (**drift** if unsorted).
3. **digest-agreement** — every spec a `claude/constraints-digest.md` line *cites* resolves to a file (**defect** on a dangling citation). Whether a given bullet is a rule that ought to carry a citation is judgment-tier (the file also holds prose/provenance bullets), so the mechanical check verifies citations, not their presence. *Semantic* agreement (the cited spec still states the rule; every judgment-tier MUST appears) is judgment-tier and **not** mechanized — flagged in the report's manual residue.
4. **pin-currency** — each role `governance:` pin block is compared to the named spec's current version; a patch/minor gap is **drift**, a major gap is a **defect** flagged for regeneration (`claude/claude.role.base.md`). No role with a pin block present → `na`.
5. **reference-resolution** — **markdown link** targets (`[text](path)`) in `claude/`, `specs/`, and `sprints/` documents resolve to an existing file (relative to the doc or the repo root); a broken link is a **defect**. External URLs, anchors, and placeholder/glob targets (containing `< > *` or whitespace) are skipped. Backticked path *tokens* in prose are **not** resolved mechanically — specs legitimately cite illustrative example paths (`src/auth/token.py`), so that resolution is left to the judgment walk. Code fences are stripped before scanning.
6. **inventory-accuracy** — a `MANUAL.md` (or declared file-inventory) matches actual directory contents. Absent in this repo → `na`.
7. **promotion-records** — reuses `aire history report`'s classification: every code-changing first-parent merge into `main` since project start carries a `promote/*` record; an unrecorded code merge is a **defect** (a *finding* in history-report terms). Docs-only recordless merges are expected (Profile A) and are not findings.
8. **decision-log-integrity** — `claude/decisions/SEQ.txt` ≥ the highest event ID; every `events/*.json` parses and carries the required fields; an `outcome.status` of `unknown` is surfaced as a **candidate** for review. The log is private (gitignored); absent (e.g., on a CI runner) → `na`.
9. **binding-validity** — every coverage binding (role headers and `.aire/config.toml` `[[coverage]]`, per `claude/coverage-spec.md`) is well-formed: `model` recognized; `code` carries `paths`, `artifact` carries `globs`, `advisory` carries `joins`, `none` carries a `justification`. A malformed binding is a **defect**.

# Invocation (Normative)

```
aire audit [--json]
```

- Default output: a deterministic **Markdown** report to stdout, findings grouped by check, with a summary header (counts by severity). Redirect to persist (e.g., `> docs/audit/<date>.md`); the tool writes no files itself (no timestamps in the body — determinism, per the architecture spec).
- `--json`: the machine report on stdout (the only thing on stdout in that mode); deterministic ordering (check order, then severity, then location).
- Read-only: `aire audit` performs no writes and no network (git is shelled read-only for checks 7 and 4).

## Exit codes
- **0**: no **defect** findings (the audit's invariants hold; drift/candidate/na may be present and are reported).
- **1**: at least one **defect** finding (a governance invariant is violated). Gate-style negative.
- **2**: tool error (not a git repo, an unreadable governance tree, an internal check failure that prevents a verdict — fail closed rather than under-report).

# Inputs
- The governance set (`claude/*.md`), `specs/` + `specs/INDEX.md`, `.aire/config.toml`, sprint files, decision events, `git` history and `promote/*` tags.

# Outputs
- The audit report (Markdown or `--json`) on stdout + the exit code above.
- No writes to the work tree; no network.

# Edge Cases / Fault Handling
- **Check inputs missing** (no `specs/INDEX.md`, no tags, no decision log): that check reports `na` with the reason; the run continues and other checks still produce a verdict.
- **A single check raising unexpectedly**: caught and reported as a **defect** for that check (the audit names its own failure) rather than aborting the whole run — except a missing git repository, which is a tool error (exit 2).
- **Repo predates a mechanism** (roles without pin blocks, no `MANUAL.md`): reported as `na` or `drift` with a count, never a false pass — silent truncation of findings is itself a defect (`claude/audit-spec.md`).
- **`--json` determinism**: identical canonical state yields byte-identical output; no timestamps, hostnames, or counts-of-time in the body.

# Test Strategy
Unit tests (stdlib `unittest`, DEC-000016) in `tests/tools/aire/test_audit.py`, using temporary fixture trees (and temp git repos where a check needs history/tags). Per `claude/audit-spec.md`, each mechanical check gets **pass, fail, and not-applicable** fixtures:
- coverage: a covered tree (no findings) vs an uncovered symbol (defect) vs no binding (na).
- spec-index: a spec missing from INDEX (defect); an unsorted index (drift); a complete sorted index (pass).
- digest-agreement: a digest line citing a missing spec (defect) vs all citations resolving (pass).
- reference-resolution: a dangling backticked path (defect); a placeholder token skipped; a valid reference (pass).
- pin-currency: a role with a stale major pin (defect) vs no pin block (na).
- promotion-records: a code merge without a record (defect) vs all merges recorded (pass) — reusing the history fixture pattern.
- decision-log-integrity: SEQ behind the max ID (defect); a malformed event (defect); an `unknown` outcome (candidate); no log (na).
- binding-validity: a `none` binding without justification (defect); a well-formed `code` binding (pass).
- determinism: `--json` byte-identical across runs on a fixed fixture.
- exit codes: defect → 1, only drift/candidate/na → 0, not-a-repo → 2.
- read-only: an audit run leaves the fixture tree unchanged.

# Completion Criteria
- `aire audit` runs all nine mechanical checks, each producing findings or a reasoned `na`, and renders a deterministic Markdown/JSON report.
- Exit code reflects defect presence (1) vs absence (0), tool error (2).
- All tests pass.
- Demonstrated on this repo: `aire audit` runs clean of defects — checks 1/2/3/5/7/9 pass, checks 4/6/8 report `na` with reasons appropriate to a role-less repo with a private decision log.

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-06-13 (v0.1.0)
- summary: Initial `aire audit` command spec. Command surface (single verb, --json, exit codes), the findings/severity model, and per-check CLI realization for the nine mechanical checks; check definitions, cadence, and disposition deferred to claude/audit-spec.md (Rule Ownership). Reuses the map engine (check 1) and history report (check 7). v0.1 mechanizes the mechanical set; semantic digest-agreement and the judgment walk remain manual residue, flagged in the report.
