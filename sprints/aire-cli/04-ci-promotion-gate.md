---
sprint: 4
title: CI promotion gate — machinery, not discipline
milestone: Gate-Enforced Promotion
status: active
---

## Goal
Complete Gate-Enforced Promotion: a CI status check that mechanically enforces git-hygiene's promotion conditions, verified by watching it fail a bad PR and pass a clean one. Portable to Forgejo Actions for lab-only repos.

## Deliverables
- `claude/claude.git-hygiene.md` — a "Promotion Gate (CI Enforcement)" subsection owning the gate's behavior (two triggers; prevention vs detection; platform portability).
- `.github/workflows/ci.yml` — the gate: on `pull_request` run the suite + `aire doctor` (prevention); on `push` to `main` additionally run `aire history report` for findings detection.
- `.gitignore` — un-ignore `.github/workflows/` (a real pipeline now exists).
- Branch protection: the `tests` check made **required** via the ruleset (extends DEC-000012).

## Acceptance Criteria
- [ ] The workflow runs green on a clean PR (tests + doctor pass).
- [ ] A deliberately-bad PR (failing test) is **blocked** by the required check — verified, not asserted.
- [ ] On push to `main`, findings detection runs; `aire history report` exit 1 fails the job.
- [ ] The workflow is portable: documented as runnable on Forgejo Actions with a self-hosted runner.
- [ ] Gate-Enforced Promotion milestone marked completed with this evidence.

## Dependencies
- `aire history report` (sprint 03) — the detection the gate runs.
- The zero-dependency CLI (DEC-000016) — makes the CI job trivial and air-gap-friendly.

## Notes
Record-existence cannot be a pre-merge gate (the record tags the merge commit, which doesn't exist until merge). So the gate splits: PR = tests required (prevention); push-to-main = findings detection. The promotion record stays the post-merge step; the main job catches any miss at once.
