---
title: State Tracker Specification (Template)
version: 0.1
maintained_by: Lead Architect (project)
domain_tags: [system, governance, state]
status: draft
license: Apache-2.0
---

# Purpose
Define the canonical, machine-first state tracker used to make roles stateless across directives.
The tracker is the authoritative snapshot of current state for a directive and is overwritten per directive.

# File Location
`state/tracker.json`

# Required Schema (JSON)
The state tracker MUST be valid JSON and MUST include the following fields:

- `schema_version` (string)
- `project` (string)
- `repo` (string)
- `active_role` (string)
- `active_directive` (object)
  - `id` (string)
  - `file` (string)
  - `issued_at` (string, ISO-8601 timestamp with timezone offset)
- `bundle_inputs` (array of strings; paths included in the directive bundle)
- `outputs_expected` (array of strings; required artifact paths)
- `artifacts_touched` (array of objects)
  - `path` (string)
  - `checksum` (string, hex)
  - `checksum_alg` (string; default `sha256`)
  - `action` (string; one of `created|updated|deleted`)
- `decisions` (array of strings; decision IDs logged during this directive)
- `state_updates` (array of strings; paths of state files updated, including `state/tracker.json`)
- `last_commit` (string; commit SHA when known, or `null` if not yet committed)

Optional fields:
- `notes` (string; free-form summary)

Reinforcement (MUSTs):
- The tracker is valid JSON and includes all required fields.
- The tracker is overwritten on every directive.
- Every touched artifact has a checksum entry.

# Semantics
- The tracker is overwritten at the end of each directive with the current state.
- Every artifact created, updated, or deleted by the directive MUST appear in `artifacts_touched` with a checksum.
- `checksum_alg` MUST be `sha256` unless project governance explicitly defines another algorithm.
- `bundle_inputs` MUST enumerate the files provided to the role for a stateless run.
- `outputs_expected` MUST list required outputs from the directive.
- `decisions` MUST include all decision IDs created during the directive (if any).
- `state_updates` MUST include `state/tracker.json` and any other state files modified.
- `last_commit` MUST be updated after the directive completion commit is created.

Reinforcement (MUSTs):
- The tracker is overwritten per directive and lists all touched artifacts with checksums.
- `bundle_inputs` and `outputs_expected` reflect the directive bundle and required outputs.

# Validation
An implementation is compliant if:
1) The tracker is valid JSON and contains all required fields.
2) Every touched artifact has a checksum entry.
3) `state/tracker.json` appears in `state_updates`.
4) `last_commit` is updated after directive completion.

Reinforcement (MUSTs):
- JSON validity, checksum coverage, state update tracking, and commit linkage are enforced.

# Example (Non-Normative)
```json
{
  "schema_version": "state.tracker.v0.1",
  "project": "aire",
  "repo": "gits/aire",
  "active_role": "developer",
  "active_directive": {
    "id": "DEV.DRAFT/2026-01-10T140212Z",
    "file": "directives/developer/20260110-140212.md",
    "issued_at": "2026-01-10T14:02:12-06:00"
  },
  "bundle_inputs": [
    "state/tracker.json",
    "templates/ai2ai-directive-spec-v2.0.md",
    "templates/state-tracker-spec.md",
    "roles/developer.md"
  ],
  "outputs_expected": [
    "src/example.c",
    "specs/src/example.c-spec.md"
  ],
  "artifacts_touched": [
    {"path": "src/example.c", "checksum": "abc123...", "checksum_alg": "sha256", "action": "created"},
    {"path": "specs/src/example.c-spec.md", "checksum": "def456...", "checksum_alg": "sha256", "action": "created"}
  ],
  "decisions": ["DEC-000123"],
  "state_updates": ["state/tracker.json"],
  "last_commit": "3f2c6a1",
  "notes": "Created example source and spec per directive."
}
```
