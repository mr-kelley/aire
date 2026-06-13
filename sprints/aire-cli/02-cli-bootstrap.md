---
sprint: 2
title: Aire CLI bootstrap — skeleton, doctor, first gate
milestone: Aire CLI
status: completed
---

## Completion
Merged via PR #12 (merge commit `a0b9aa2`). The repo's first promotion record —
`promote/aire-cli-bootstrap` → `a0b9aa2`, JSON payload per promotion-record-spec —
was written by `aire history record` itself, against the merge commit, with tests
re-verified green on that commit. Self-hosting (NORTHSTAR success criterion 1)
demonstrated: the CLI certified its own first promotion. The promotion tag is
local; pushing tags is human-only.

## Goal
First Profile B code in this repo: the CLI skeleton under `tools/`, the `doctor` subcommand, and enough of `history` to write this sprint's own promotion record.

## Deliverables
- [x] `tools/` package skeleton (Python, argparse, zero-dependency — DEC-000010, DEC-000016).
- [x] Component specs in `specs/` (architecture, doctor, history; `covers:` declarations per coverage-spec).
- [x] `aire doctor`: repo/config validation, version-pin check against the repo's declared minimum.
- [x] `aire history record`: writes a valid promote/<slug> tag per promotion-record-spec (JSON payload, DEC-000017; `-rN` uniqueness; fail-closed validation).
- [x] Tests (stdlib unittest, DEC-000016) per each spec's Test Strategy — 30 tests green.

## Acceptance Criteria
- [x] Tests pass on the work branch tip (`python -m unittest discover -s tests/tools/aire`).
- [x] `aire doctor` runs clean on this repo (6 ok / 1 warn / 0 fail; the warn is the undeclared local-model floor, DEC-000014).
- [~] Promotion to main carries the repo's first promote/* tag — written by the tool itself. Capability complete and previewed via `--dry-run` against this branch (tag `promote/aire-cli-bootstrap`). The real tag lands on the merge commit post-merge (the record points at the merge commit, which doesn't exist until merge — inherent to the spec).

## Dependencies
- Sprint 01 (NORTHSTAR approved).
