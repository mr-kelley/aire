---
sprint: 2
title: Aire CLI bootstrap — skeleton, doctor, first gate
milestone: Aire CLI
status: active
---

## Goal
First Profile B code in this repo: the CLI skeleton under `tools/`, the `doctor` subcommand, and enough of `history` to write this sprint's own promotion record.

## Deliverables
- [x] `tools/` package skeleton (Python, argparse, zero-dependency — DEC-000010, DEC-000016).
- [x] Component specs in `specs/` (architecture, doctor; `covers:` declarations per coverage-spec).
- [x] `aire doctor`: repo/config validation, version-pin check against the repo's declared minimum.
- [ ] `aire history record`: writes a valid promote/<slug> tag per promotion-record-spec.
- [x] Tests (stdlib unittest, DEC-000016) per each spec's Test Strategy — 22 tests green.

## Acceptance Criteria
- [x] Tests pass on the work branch tip (`python -m unittest discover -s tests/tools/aire`).
- [x] `aire doctor` runs clean on this repo (6 ok / 1 warn / 0 fail; the warn is the undeclared local-model floor, DEC-000014).
- [ ] Promotion to main carries the repo's first promote/* tag — written by the tool itself (blocked on `aire history record`).

## Dependencies
- Sprint 01 (NORTHSTAR approved).
