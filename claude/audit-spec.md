---
title: Governance Liveness Audit Specification
version: 0.1.0
maintained_by: Aire System Architect (ASA)
domain_tags: [system, governance, audit, drift]
status: draft
platform: claude-code
license: Apache-2.0
---

# Purpose
Define the recurring audit that detects stale governance: dead-letter rules, cross-document inconsistency, and doc drift. Aire's forward governance gates new work; this audit is the backward verification that what's already written is still true, exercised, and internally consistent. Its origin is a demonstrated failure mode: rules persisting as dead letters for months, undetected (regenerate-not-patch; the Profile C residue).

This spec also governs the `audit` subcommand of the Aire CLI (see DEC-000010).

# Scope

## Covers
- The mechanical check set (scriptable, run by the CLI or by hand until it exists).
- The judgment check set (run by a Claude session against a checklist).
- Cadence, output format, and disposition rules for findings.

## Does Not Cover
- Coverage verification mechanics (owned by `claude/coverage-spec.md`; the audit invokes them).
- Promotion record validity rules (owned by `claude/promotion-record-spec.md`; the audit invokes them).
- Fixing the findings (each finding routes to normal sprint work).

# Mechanical Checks (Normative)

Each check is deterministic and produces findings with file/line references:

1. **Coverage**: `map check` passes for the active role's binding (per `claude/coverage-spec.md`).
2. **Spec index**: every file in `specs/` appears in `specs/INDEX.md` and vice versa; index is sorted per `claude/documentation-spec.md`.
3. **Digest agreement**: every line in `claude/constraints-digest.md` has an owning spec that still states the rule; every judgment-tier MUST in the governance set appears in the digest.
4. **Pin currency**: each role's `governance:` block compared against current spec versions; mismatches listed with semver delta (patch/minor noted, major flagged for regeneration per `claude/claude.role.base.md`, Governance Version Pinning).
5. **Reference resolution**: every relative path cited in governance docs, roles, and CLAUDE.md files points at a file that exists.
6. **Inventory accuracy**: MANUAL.md (and any file-inventory listings) match the actual directory contents.
7. **Promotion records**: every merge commit on `main` since the last audit carries a valid `promote/*` record (Profile B), per `claude/promotion-record-spec.md`.
8. **Decision log integrity**: `SEQ.txt` ≥ highest event ID; every event is valid JSON with required fields; `outcome.status` of `unknown` older than the project-defined staleness window is flagged.
9. **Binding validity**: every role's `coverage_model`/`coverage_config` is well-formed per `claude/coverage-spec.md`; `none` carries justification.

# Judgment Checks (Normative)

Run by a Claude session walking each governance document, asking per rule:

- **Exercised**: has this rule observably applied since the last audit (commits, decisions, halts citing it)? Rules with no observable exercise across two consecutive audits are dead-letter candidates.
- **Agreement**: do all documents referencing this rule say the same thing (one-clause summaries vs owning statement)?
- **Necessity**: would anything break if the rule vanished? If nothing would, retirement is proposed.

Disposition: every dead-letter candidate is **explicitly retired or reaffirmed** via a logged decision — never silently left. Retirement removes the rule from the owning spec with a provenance note.

# Cadence
- After every governance-spec change (mechanical set, at minimum checks 2–6).
- Every N sprints (full set, mechanical + judgment); N is project-defined, default 5.
- Before any bulk role regeneration (pin currency informs the worklist).

# Inputs
- The governance set (`claude/*.md`), roles, CLAUDE.md files, sprint files, decision events, git history and tags.

# Outputs
- Audit report (derived, deterministic, Markdown): findings grouped by check, each with location, severity (defect / drift / candidate), and proposed disposition. Default `docs/audit/<date>.md` or stdout.
- Findings route to sprint work or logged retirement decisions; the report itself changes nothing.

# Edge Cases / Fault Handling
- **Check inputs missing** (no sprints/ dir, no tags yet): the check reports not-applicable with reason, never false-passes.
- **Repo predates a mechanism** (e.g., roles without pin blocks): reported as migration-pending drift, severity drift not defect, with a count — silent truncation of findings is itself a defect.
- **Audit tooling unavailable**: the judgment set still runs manually; mechanical checks degrade to documented manual commands.

# Test Strategy
Implemented and tested in the Aire CLI project: each mechanical check gets fixtures for pass, fail, and not-applicable cases; report determinism verified (identical state → identical report). Judgment checks are not automatable — their checklist is verified by audit-of-the-audit during milestone reviews. Until the CLI exists, the mechanical checks run as documented manual commands.

# Completion Criteria
- An audit run produces a report covering all nine mechanical checks plus the judgment walk.
- Every finding reaches a disposition (fixed, scheduled, or logged retirement/reaffirmation).
- CLI tests pass once the `audit` subcommand exists.

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-06-12
- summary: Initial liveness audit spec per DEC-000004/DEC-000010. Mechanical checks consolidate the session's accumulated drift-detection needs: digest agreement (DEC-000003), pin currency (DEC-000008), binding validity (DEC-000006), promotion records (DEC-000007), plus the original dead-letter review that motivated the decision.
