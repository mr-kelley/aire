---
sprint: 1
title: Promotion-record and liveness-audit specs
milestone: Gate-Enforced Promotion
status: completed
---

## Goal
Complete the CLI's governing specs: what promotion records contain and what the audit checks (DEC-000004, DEC-000007 spec-side).

## Deliverables
- promotion-record-spec v0.1.0 (tag schema, -rN uniqueness, report generator contract); audit-spec v0.1.0 (9 mechanical checks + judgment walk, retire-or-reaffirm disposition); ROADMAP maintenance.

## Acceptance Criteria
- All four CLI subcommand contracts exist (map/history/audit/digest); both specs conform to spec-spec structure. (Profile A.)

## Completion
Branch `work/2026-06-12T200632Z/cli-governing-specs`, commit 707a641, merged via PR #9.
