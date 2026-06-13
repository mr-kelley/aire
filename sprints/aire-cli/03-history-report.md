---
sprint: 3
title: aire history report — the audited project history
milestone: Gate-Enforced Promotion
status: completed
---

## Completion
Merged via PR #14 (merge commit `35552b0`). Promotion record `promote/cli-history-report` → `35552b0` written by `aire history record` against the merge commit (tests re-verified green there); `aire history report` now renders 2 tested promotions, 0 findings. Closeout folded into the opening commit of the CI promotion gate sprint — first exercise of the DEC-000018 provisional convention.

## Goal
Implement `aire history report` — the read side of the promotion record system. Renders the repo's audited development history from canonical state (promote/* tags + merges + sprint files + decision events) into audience-targeted views. Completes the Gate-Enforced Promotion milestone and produces the management-transparency artifact (NORTHSTAR success criterion 5).

## Deliverables
- `tools/aire/history_report.py` — gather + render (summary / detail / chain / JSON).
- `aire history report` wired into the CLI (default summary; `--detail`, `--chain <slug>`, `--json`).
- `claude/promotion-record-spec.md` refinement: recordless-merge classification (code-changing = finding; docs-only = expected, Profile A).
- `specs/tools/aire/history-spec.md` extended to cover the report command surface.
- Tests (stdlib unittest) per the spec's Test Strategy.

## Acceptance Criteria
- [x] `aire history report` renders this repo's history deterministically from canonical state; reads only (no writes, no network).
- [x] Summary view makes the strong claim from evidence (1 tested promotion, 11 docs merges, 0 findings on this repo).
- [x] Detail and chain views render per-promotion evidence; decision titles join best-effort from the local log, degrading to ID-only when the (private) log is absent.
- [x] Tests pass on the work branch tip (38 green).
- [x] Demonstrated on this repo: the report renders the `promote/aire-cli-bootstrap` promotion across summary/detail/chain/JSON.

## Notes (status)
Sprint work complete on the branch. Profile B: status moves to `completed` after merge + the `promote/cli-history-report` record is written by the tool against the merge commit (same post-merge pattern as sprint 02).

## Dependencies
- `aire history record` (sprint 02) — produces the records this reads.

## Notes
The decision log is private (gitignored); the report joins decision titles best-effort and never fails on their absence. Dates shown are canonical git commit dates (deterministic), not generation time.
