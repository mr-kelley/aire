---
sprint: 2
title: Aire CLI bootstrap — skeleton, doctor, first gate
milestone: Aire CLI
status: planned
---

## Goal
First Profile B code in this repo: the CLI skeleton under `tools/`, the `doctor` subcommand, and enough of `history` to write this sprint's own promotion record.

## Deliverables
- `tools/` package skeleton (Python, argparse, no daemon — DEC-000010 constraints).
- Component specs in `specs/` for each module built (spec-first; `covers:` declarations per coverage-spec).
- `aire doctor`: repo/config validation, version-pin check against the repo's declared minimum.
- `aire history record`: writes a valid promote/<slug> tag per promotion-record-spec.
- Tests (pytest) per each spec's Test Strategy.

## Acceptance Criteria
- Tests pass on the work branch tip; promotion to main carries the repo's first promote/* tag — written by the tool itself.
- `aire doctor` runs clean on this repo.

## Dependencies
- Sprint 01 (NORTHSTAR approved).
