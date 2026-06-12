---
sprint: 1
title: Governance spec edits (promotion model, decision-log trim, load order)
milestone: Governance Consolidation
status: completed
---

## Goal
Land the approved spec-level changes: collapse stage/test into promotion records, remove the unbuilt SQLite/CLI machinery from the decision log spec, reorder session loading static-first.

## Deliverables
- git-hygiene v0.3.0 (DEC-000002, DEC-000007), decision-log v0.3.0 (DEC-000005), state-pack v0.3.0 + MANUAL update (DEC-000009).

## Acceptance Criteria
- No Profile C or stage/test references outside provenance; no index/CLI machinery outside provenance; load order matches MANUAL. (Profile A — docs; tests N/A.)

## Completion
Branch `work/2026-06-12T170625Z/governance-spec-edits`, commits 3be4ed5/de374a9/78d1054, merged via PR #6.
