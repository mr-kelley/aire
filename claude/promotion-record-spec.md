---
title: Promotion Record Specification
version: 0.2.0
maintained_by: Aire System Architect (ASA)
domain_tags: [system, governance, git, promotion, audit]
status: draft
platform: claude-code
license: Apache-2.0
---

# Purpose
Define the structure and semantics of promotion records — the auditable evidence that nothing reached `main` untested. Git hygiene (`claude/claude.git-hygiene.md`, the owning spec for *when* records are required) mandates a record for every Profile B promotion; this spec owns *what the record contains* and how reports are generated from it.

This spec also governs the `history` subcommand of the Aire CLI (see DEC-000010): the gate that enforces records and the report generator that renders them.

# Scope

## Covers
- The promotion record format (annotated tag, structured payload).
- Tag naming and uniqueness rules.
- The history report generator: required views and derivation rules.

## Does Not Cover
- When promotion is permitted (owned by `claude/claude.git-hygiene.md`).
- Sprint structure (owned by `claude/planning-spec.md`).
- Decision event format (owned by `claude/decision-log-spec.md`).

# Record Format (Normative)

A promotion record is an **annotated git tag** on the merge commit that lands a sprint on `main`.

**Tag name:** `promote/<slug>` where `<slug>` matches the work branch slug. If the same slug is promoted again (e.g., after a revert), suffix with `-r2`, `-r3`, … — tag names are immutable and never reused.

**Tag message:** a JSON payload (per DEC-000017 — JSON, not YAML, for stdlib round-trip on both the write and read sides and consistency with decision events). Serialized deterministically with sorted keys and 2-space indent:

```json
{
  "sprint": "sprints/<milestone-slug>/<nn>-<slug>.md",
  "specs": [
    "specs/<governing-spec-1>.md",
    "specs/<governing-spec-2>.md"
  ],
  "tests": {
    "command": "<how the tests were invoked>",
    "outcome": "PASS",
    "sha": "<the exact commit SHA the tests ran against>"
  },
  "decisions": ["DEC-000123", "DEC-000124"],
  "notes": "<optional one-liner, or null>"
}
```

Rules:
- `tests.sha` MUST be the work-branch tip that was actually tested. If the merge produces a different tree than the tested SHA (e.g., non-trivial merge), the tests MUST be re-run against the merge result and the record updated before tagging.
- `tests.outcome` MUST be `PASS` — a record with any other outcome is invalid; failed runs are never recorded as promotions.
- `decisions` lists decision IDs implemented or materially touched by the sprint; empty list is valid.
- Profile A promotions (docs/policy) MAY carry records with `tests: {outcome: N/A}`; they are encouraged for milestone-significant merges and not required otherwise.
- Tags are local until the human pushes them (per git hygiene: Claude never pushes).

# History Report Generator (Normative)

The generator walks `main`'s merge commits and `promote/*` tags, joins sprint files and decision events, and renders derived views:

1. **Summary view** (non-technical audience): totals and assertions — sprints completed, tested promotions, untested merges (target: zero), escalations resolved by human decision, span dates. One screen.
2. **Sprint detail view** (engineering audience): per sprint — goal, governing specs, test command and outcome, tested SHA, merge SHA, decision IDs with titles.
3. **Audit chain view**: for any given promotion, the full traceable chain: issue (if any) → sprint → spec(s) → commits → test record → promotion tag → decisions.

Rules:
- Reports are **derived artifacts**: regenerated from canonical state (git + tags + sprint files + decision events) on demand; never hand-edited; deterministic output (stable ordering by promotion date, then tag name).
- A merge commit on `main` without a promotion record is itself a finding the report MUST surface (Profile B projects), not silently skip.
- The generator reads repo state only: no network, no writes beyond the report files.

# Inputs
- Git history of `main`; `promote/*` annotated tags.
- Sprint files (`sprints/`), decision events (`decisions/events/`).

# Outputs
- Promotion records (annotated tags, written at promotion time by the gate flow).
- History reports (derived; default `docs/history/` or stdout).

# Edge Cases / Fault Handling
- **Malformed tag payload**: report flags it as an invalid record; the audit (per `claude/audit-spec.md`) lists it as a defect to repair via a corrected `-rN` tag (originals are never deleted).
- **Squash merges**: the record's `tests.sha` references the pre-squash tested tip, which remains reachable via branch retention (git hygiene); the tag itself sits on the squash commit.
- **Sprint file missing/moved**: report renders the record with a dangling-reference warning rather than failing.
- **Tag exists but merge was reverted**: the record stands as history; the revert appears as subsequent history. Records are append-only evidence, not current-state claims.

# Test Strategy
Implemented and tested in the Aire CLI project. Tests MUST verify: payload parse/validation (valid, malformed, non-PASS rejection), `-rN` uniqueness handling, report determinism (identical canonical state → identical reports), unrecorded-merge detection, and dangling-reference tolerance — against fixture repositories. Until the CLI exists, records are written manually per this format and verified by the liveness audit.

# Completion Criteria
- Profile B promotions carry valid records; the gate refuses merges without them (CLI-enforced once built).
- Reports regenerate deterministically from canonical state and surface unrecorded merges.
- Relevant CLI tests pass.

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-06-13 (v0.2.0)
- summary: Implements DEC-000017. Tag-message payload changed from YAML to JSON (deterministic: sorted keys, 2-space indent) for stdlib round-trip on both write (`aire history record`) and read (`aire history report`) sides — preserving the zero-dependency thesis (DEC-000016) — and for consistency with the JSON decision log. Fields unchanged.
- time: 2026-06-12 (v0.1.0)
- summary: Initial promotion record schema per DEC-000007/DEC-000010. Owns the record format and report generator; git-hygiene owns when records are required. Designed for the management-transparency goal: evidence generated by a gate the process cannot skip, rendered for non-technical decision-makers.
