# Project State — aire

## Project Overview
Aire is an open-source governance framework for human-AI collaborative development. This repository holds the public framework (governance specs in `claude/`, the AireSmith role generator, platform templates) and — beginning with the Aire CLI — the tooling that enforces it. Current focus: the 2026-06 governance modernization (decision log DEC-000001…DEC-000013) and the runway to the Aire CLI.

Repository: `gits/aire` (public mirror: github.com/mr-kelley/aire). Promotion: PRs to `main`; Profile A for governance docs, Profile B once `tools/` exists.

## Active Work
- **No active sprint.** The "finish out the CLI" arc is complete: all five subcommands shipped (`doctor`, `history`, `map`, `audit`, `digest`; PRs #12–#20) plus two real-use refinements — promotion tip-grace (PR #21) and CI re-trigger on promote-tag push (PR #22). Awaiting next operator direction. Candidate next threads: the optional `hook` shim (session-time enforcement), the role-vs-operator-session question for this repo, the migration pilot, or new direction entirely.
- **Aire CLI milestone — complete** (all subcommands shipped: doctor, history, map, audit, digest; PRs #12–#20; optional `hook` shim deferred).
- **Gate-Enforced Promotion milestone — complete** (CI gate verified both halves; PRs #15/#17).
- **Role migration pilot** (external: private roles repository) — first private role migrated to role-base v0.4.0. Status: waiting-on-operator (real-use observation gates the remaining migrations).

## Recent Completions
- CI: **re-trigger on `promote/**` tag push** — a record push triggers a detection-only `aire-gate` run (tests/doctor skipped on tag runs), so a real forgotten-then-fixed finding clears promptly (DEC-000022). Companion to tip-grace; Profile A, no record — PR #22 — 2026-06-14.
- Aire CLI: promotion **tip-grace** — newest first-parent merge is record-pending (not a finding); older recordless code merges stay findings (DEC-000021). Removes the merge-time false failure without suppression; **validated live** — PR #21's push-to-main run stayed green on its own merge. 108 tests green; promotion-record-spec v0.4.0; promotion record `promote/promotion-tip-grace` — PR #21 — 2026-06-14.
- Aire CLI: `aire digest` — derived constraints digest (owning specs declare `digest:` clauses; render/check, fail-closed; cures regenerate-not-patch, DEC-000020); dogfooded 15 clauses match, audit 0 defect; 104 tests green; promotion record `promote/aire-digest-constraints` — PR #20 — 2026-06-14. **Closed the Aire CLI milestone.**
- Aire CLI: `aire audit` — mechanical governance liveness (nine DEC-000004 checks; #1 reuses `map`, #7 reuses `history report`); dogfooded 0 defect on aire (4 candidate, 2 n/a); 86 tests green; promotion record `promote/aire-audit-liveness` — PR #19 — 2026-06-14.
- Aire CLI: `aire map` — mechanical spec coverage (code engine, AST + `covers:` cross-reference); dogfooded 46/46 units green on aire; role-less binding home `.aire/config.toml` `[[coverage]]` (DEC-000019); 56 tests green; promotion record `promote/aire-map-coverage` — PR #18 — 2026-06-14.
- **Gate-Enforced Promotion milestone complete**: CI promotion gate (GitHub Actions, required `tests` check + push-to-main findings detection), verified on both halves — PR #15 — 2026-06-13.
- Aire CLI: `aire history report` — audited history (summary/detail/chain/JSON), findings classification; 38 tests green; second self-written promotion record (`promote/cli-history-report`) — PR #14 — 2026-06-13.
- Aire CLI bootstrap: `aire doctor` + `aire history record`, zero-dependency, 30 tests green; first self-written promotion record (`promote/aire-cli-bootstrap`) — PR #12 — 2026-06-13.
- Project initialization: repo brought under its own governance (STATE/NORTHSTAR/INDEX/sprints) — PR #11 — 2026-06-12.
- CLI governing specs (promotion-record, audit) + roadmap maintenance — PR #9 — 2026-06-12.
- Coverage contract + governance version pinning (coverage-spec v0.1.0, role-base v0.4.0, aire-smith v0.7.0) — PR #8 — 2026-06-12.
- Governance de-duplication: Rule Ownership, pointer-style role base, constraints digest, push-contradiction fix — PR #7 — 2026-06-12.
- Spec edits: stage/test collapsed to promotion records, decision-log trim, static-first session loading — PR #6 — 2026-06-12.
- README rewrite, aire-smith v0.6.0 (permissions/sudoers), gitignore privacy cleanup, lineage templates, community docs, roadmap — PR #5 — 2026-06-12.
- Private role masters brought under version control in a dedicated private repository — 2026-06-12.

## Project Structure
- `claude/` — the governance spec set (the heart of the framework) + AireSmith role.
- `claude/decisions/` — project decision log (private, excluded from the public mirror).
- `templates/`, `codex/`, `primitives/` — platform templates and lineage.
- `specs/` — project specs for this repo's own deliverables (INDEX.md is the map).
- `sprints/` — sprint records by milestone.
- `tools/` — Aire CLI source (Python, zero-dependency; `aire` console command). First Profile B code in this repo.
- `tests/` — test suites mirroring source paths (stdlib unittest).
- `private/` — personal/legacy working files, never published.

## Key Decisions
Decision log: `claude/decisions/events/` (DEC-000001…DEC-000022, private). Load-bearing for current work:
- DEC-000010: single system-installed CLI; binaries are never orchestrators; no daemons.
- DEC-000006/000008: coverage contract + version pinning (mechanism live; 27 role migrations pending pilot).
- DEC-000019: role-less repos declare coverage bindings in `.aire/config.toml` `[[coverage]]`; resolution role-headers-first.
- DEC-000020: the constraints digest is a derived artifact — owning specs declare `digest:` clauses; `aire digest` re-derives and gates fail-closed (declared-not-inferred, like `covers:`).
- DEC-000021: promotion tip-grace — the newest first-parent merge is record-pending by construction (not a finding); older recordless code merges remain findings. Removes the merge-time false failure without suppression.
- DEC-000022: a `promote/**` tag push re-runs findings detection only (tests/doctor skipped on tag runs); clears a real forgotten-then-fixed finding promptly. Companion to DEC-000021.
- DEC-000013: private role masters versioned in a dedicated repository; pilot-first migration.
- DEC-000011: pushing human-only; PR creation per explicit case-by-case authorization.

## Open Questions
- Does this repo get its own AireSmith-generated maintainer role, or continue as operator-paired sessions? (Affects root CLAUDE.md generation; does not block CLI work. See `sprints/aire-cli/01-project-init.md`.)
- Pilot-role observations — any v0.4.0 structure friction feeds back before bulk migration.
- **Judgment-walk audit** (the non-mechanical half of `claude/audit-spec.md`: exercised / agreement / necessity) — the mechanical half now runs every gate via `aire audit`; schedule a periodic manual judgment walk when convenient. `aire audit` currently flags candidate decisions with `outcome.status: unknown` for closure review.

*Resolved:* DEC-000018 closeout convention — **PASS** after seven clean applications (folded 03/05/06/07/08, bundled 04/09); ratified into `claude/planning-spec.md` v0.2.0 (2026-06-14).

## Session Notes
2026-06-12: Marathon governance-modernization session. Thirteen decisions logged; PRs #5–#9 merged; publication boundary made mechanical; private role masters versioned; migration pilot complete. This file created during the project-init sprint. Next: NORTHSTAR approval → CLI bootstrap sprint (tools/, Profile B).
