---
sprint: 8
title: promotion tip-grace — distinguish record-pending from record-forgotten
milestone: Aire CLI
status: completed
---

## Completion
Merged via PR #21 (merge commit `3ca57af`). Promotion record `promote/promotion-tip-grace` → `3ca57af` written by `aire history record` (108 tests re-verified green; `audit`/`map`/`digest` clean). **Validated live on CI:** the push-to-main run for the merge came back green (9s) — before tip-grace it would have been red, because the merge is a recordless code merge at merge time. Reproduced locally: history report classified `3ca57af` as `pending` (0 findings, exit 0), the exact state CI evaluated. The fix proved itself on its own promotion — first real-infrastructure proof, not just unit tests. `aire history report` now shows 6 tested promotions, 0 findings. Closeout folded into the opening commit of the ci-retrigger sprint (DEC-000018, fifth exercise).

## Goal
Stop `aire history report` from raising a **false failure** in the unavoidable window between a code merge landing on `main` and its promotion record being pushed. The record certifies the merge commit, so it cannot exist until after the merge; the push-to-main gate runs detection *at merge time*, before the tag lands, and (correctly, but unhelpfully) flags the just-merged code as recordless. The fix differentiates **real** from **false** in the code, never by suppression: the single newest first-parent merge, if it is a recordless code merge, is reported as a distinct `pending` status (informational, exit 0); any *older* recordless code merge remains a finding (exit 1). A forgotten record is therefore still caught — one merge later, when the merge is no longer the tip.

This is a real-use-driven refinement ("building the plane while flying it"): the false failure was observed firsthand on PRs #18–#20.

## Deliverables
- **DEC-000021** (private) — tip-grace for recordless-merge classification: the newest first-parent merge is record-pending by construction; grace it, flag older recordless code merges as drift.
- `claude/promotion-record-spec.md` — define the `pending` classification and the tip-grace rule (it owns the history-report generator and recordless-merge classification). Version + provenance bump.
- `tools/aire/history_report.py` — `gather` classifies the tip recordless code merge as `pending`; summary/detail/JSON render it; exit code unchanged (1 iff findings; pending never fails).
- `tests/tools/aire/test_history_report.py` — tip recordless code merge → pending (exit 0); older recordless code merge → finding (exit 1); tip with record → skipped; pending + older finding coexist (still exit 1).

## Acceptance Criteria
- [x] The newest first-parent merge, when a recordless code merge, classifies as `pending` (not a finding); `history report` exits 0.
- [x] An older recordless code merge (a newer merge sits above it) remains a finding; `history report` exits 1.
- [x] A tip merge that already carries a record is skipped as before (no pending, no finding).
- [x] Docs/governance merges are unaffected (still "no record expected").
- [x] `audit` check #7 inherits the grace automatically (it reuses `gather().findings`); aire still reports 0 defect.
- [x] Tests pass on the work branch tip (108 green: 104 prior + 4 tip-grace).
- [x] **Dogfood:** with all records pushed, `history report` on aire is unchanged (5 promotions, 0 findings, 0 pending, exit 0).
- [ ] Promoted to `main` with a tested promotion record (post-merge, Profile B).

## Honest scoping
- The grace covers exactly the single newest first-parent merge. Two code merges landed back-to-back without an interleaving record would flag the older one — acceptable: the normal flow is merge → record → merge.
- Detection of a genuinely forgotten record now **lags by one merge** (it fires when the merge stops being the tip). This is the deliberate cost, and it is not suppression — the detector still fires; it just declines to alarm on a state that is *required* to exist briefly.
- Scope is the timing window only. The docs-vs-code classification (Profile A vs B) is unchanged; `specs/` and `claude/` remain docs (no record expected).

## Dependencies
- `claude/promotion-record-spec.md` — owns the classification contract this refines.
- `tools/aire/history_report.py` (sprint 03) — the generator being refined.
- `tools/aire/audit.py` check #7 — reuses the classification; inherits the change.

## Notes
The CI re-trigger question (a promote-tag push does not re-run the gate, so a cleared finding's green lags to the next main push) is **out of scope** here and noted for later: tip-grace removes the *false alarm at merge time*, which is the user-visible pain. Whether to also add `on.push.tags: ['promote/**']` so a pushed record re-evaluates immediately is a separate, optional CI change.
