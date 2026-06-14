---
sprint: 6
title: aire audit — mechanical governance liveness
milestone: Aire CLI
status: completed
---

## Completion
Merged via PR #19 (merge commit `ac3e141`). Promotion record `promote/aire-audit-liveness` → `ac3e141` written by `aire history record` against the merge commit (86 tests re-verified green there; `aire audit` exits 0 — 0 defect, 0 drift, 4 candidate, 2 n/a; `map check` 53/53 units). `aire history report` now shows 4 tested promotions, 0 findings. Closeout folded into the opening commit of the aire-digest sprint — third exercise of the DEC-000018 provisional convention (sprint 03 folded, sprint 04 bundled, sprint 05 folded).

## Goal
Implement `aire audit` — the mechanical half of the governance liveness audit (DEC-000004), the backward verification that what's already written is still true, exercised, and consistent. Mechanizes the nine checks in `claude/audit-spec.md`, reusing `map` (check 1) and `history report` (check 7). Dogfooded on aire: a clean-of-defects run, with not-applicable checks honestly reported for a role-less repo with a private decision log.

## Deliverables
- `specs/tools/aire/audit-spec.md` v0.1.0 — command surface, findings/severity model, per-check CLI realization (check semantics deferred to `claude/audit-spec.md`, Rule Ownership).
- `tools/aire/audit.py` — nine mechanical checks, each yielding findings or a reasoned `na`; deterministic Markdown/JSON report; exit 1 on any defect.
- `tools/aire/cli.py` — `audit` dispatch; `specs/tools/aire/architecture-spec.md` v0.1.3.
- `specs/INDEX.md` — audit-spec registered.
- `tests/tools/aire/test_audit.py` — pass/fail/na per check, determinism, exit codes, read-only.

## Acceptance Criteria
- [x] `aire audit` runs all nine mechanical checks; each produces findings or a reasoned `na`.
- [x] Exit code reflects defect presence (1) vs absence (0); not-a-directory → 2.
- [x] Deterministic Markdown/JSON report (check order, then severity, then location; no timestamps in the body).
- [x] Checks 1 and 7 reuse the `map` engine and `history report` rather than reimplementing them.
- [x] Tests pass on the work branch tip (86 green: 56 prior + 30 new).
- [x] **Dogfood:** `aire audit` on aire is clean of defects (0 defect; 4 candidate from `unknown` decision outcomes; 2 n/a — pin-currency, inventory). Exit 0.
- [ ] Promoted to `main` with a tested promotion record (post-merge, Profile B).

## Honest scoping
v0.1 mechanizes the *mechanical* set. Two reductions, stated rather than hidden:
- **digest-agreement** verifies that *cited* specs resolve, not that every rule line carries a citation (rule-vs-prose is judgment-tier) — semantic agreement stays in the judgment walk.
- **reference-resolution** checks **markdown link** targets only; backticked path tokens in prose are routinely illustrative examples (`src/auth/token.py`), so resolving them mechanically is too noisy and is left to the judgment walk.
Both reductions are flagged in the report's manual-residue footer. The judgment checks (exercised / agreement / necessity) remain a Claude-session walk, per `claude/audit-spec.md`.

## Dependencies
- `claude/audit-spec.md` — the check definitions this implements.
- `tools/aire/map.py` (sprint 05) — check 1 invokes it.
- `tools/aire/history_report.py` (sprint 03) — check 7 reuses its classification.

## Notes
The tool earned its keep during its own construction: its first run flagged a real gap (the new audit-spec missing from `specs/INDEX.md`) alongside heuristic false positives (inline example paths read as references). Triaging those into trustworthy signal — citations-resolve not citations-exist; links not backtick-tokens; strip inline code before link-scanning — was the substance of the sprint. An audit that cries wolf is worse than none; the discipline was making it quiet enough to trust.
