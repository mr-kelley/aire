---
sprint: 9
title: CI re-trigger on promotion-tag push — clear a real finding promptly
milestone: Aire CLI
status: active
---

## Goal
Close the companion gap to sprint 08's tip-grace (explicitly deferred there). Tip-grace removed the *routine* false failure at merge time. What remains: when a **genuine** finding is red (a record was forgotten and a later merge made it real drift), pushing the missing `promote/<slug>` record does not re-run the gate — a `promote/**` tag push matches no trigger — so the cleared green lags to the next push to `main`. This sprint makes the detection re-evaluate when a record lands: a `promote/**` tag push triggers the gate, running **only** findings detection (tests/doctor already ran on the PR and the main push). Recovery + confirmation, not a routine path (DEC-000022).

## Deliverables
- **DEC-000022** (private) — re-run findings detection on `promote/**` tag pushes; skip the redundant test/doctor re-run on tag-triggered runs.
- `.github/workflows/ci.yml` — add `tags: ['promote/**']` to the push trigger; gate the Unit-tests and doctor steps to non-tag runs (`github.ref_type != 'tag'`); the history-report step already runs on any push and its `--ref "${GITHUB_REF_NAME}"` resolves correctly on a tag push (the tag points at a `main` merge commit, so `--first-parent` walks `main`).

## Acceptance Criteria
- [x] A `promote/**` tag push triggers the `aire-gate` workflow (`push.tags: ['promote/**']`).
- [x] On a tag-triggered run, Unit tests and `aire doctor` are skipped (`if: github.ref_type != 'tag'`); only findings detection runs (`if: github.event_name == 'push'`).
- [x] On a main push, behavior is unchanged (`ref_type == 'branch'` → tests + doctor + detection all run).
- [x] The change is Profile A (CI/config only; `.github/` is not in `DEFAULT_CODE_PATHS`) — no promotion record required for this merge.
- [x] Workflow YAML is valid (parsed; triggers and step conditions confirmed); reasoned through against GitHub Actions trigger/`ref_type` semantics. Live observation (a real promote-tag push triggering a detection-only run) confirmed on first use post-merge.

## Honest scoping
- This is **recovery + confirmation polish**, not a fix: after tip-grace, the normal flow is already green at merge time. The re-trigger matters only when a real finding exists and you push the missing record, or to flip CI status from `pending` to `recorded`.
- It cannot be exercised by the stdlib unit suite (it is GitHub Actions behavior). Validation is by reasoning about trigger semantics plus first real-use observation — same posture as the original gate (sprint: gate-enforced promotion).
- Cost acknowledged: a record push now spends one lightweight CI run (detection only). Accepted for prompt recovery and status confirmation.

## Dependencies
- `.github/workflows/ci.yml` (the gate) — sprint: gate-enforced promotion.
- `tools/aire/history_report.py` tip-grace (sprint 08) — the detection this re-runs already greens the routine case.

## Notes
Post-milestone refinement, real-use-driven. With this, the promotion gate's red/green tracks the true record state with no more than the deliberate one-merge tip-grace lag, and a forgotten-then-fixed record clears immediately instead of waiting for the next merge.
