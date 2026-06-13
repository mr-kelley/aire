# Project State — aire

## Project Overview
Aire is an open-source governance framework for human-AI collaborative development. This repository holds the public framework (governance specs in `claude/`, the AireSmith role generator, platform templates) and — beginning with the Aire CLI — the tooling that enforces it. Current focus: the 2026-06 governance modernization (decision log DEC-000001…DEC-000013) and the runway to the Aire CLI.

Repository: `gits/aire` (public mirror: github.com/mr-kelley/aire). Promotion: PRs to `main`; Profile A for governance docs, Profile B once `tools/` exists.

## Active Work
- **`aire history report` sprint** — branch `work/2026-06-13T140857Z/cli-history-report`. The read side of the promotion system: summary/detail/chain/JSON views, recordless-merge classification, best-effort decision-title join. Done on the branch (38 tests green; renders this repo's history). Status: awaiting merge + post-merge promotion record. Sprint file: `sprints/aire-cli/03-history-report.md`.
- **Role migration pilot** (external: private roles repository) — first private role migrated to role-base v0.4.0. Status: waiting-on-operator (real-use observation gates the remaining migrations).

## Recent Completions
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
Decision log: `claude/decisions/events/` (DEC-000001…DEC-000013, private). Load-bearing for current work:
- DEC-000010: single system-installed CLI; binaries are never orchestrators; no daemons.
- DEC-000006/000008: coverage contract + version pinning (mechanism live; 27 role migrations pending pilot).
- DEC-000013: private role masters versioned in a dedicated repository; pilot-first migration.
- DEC-000011: pushing human-only; PR creation per explicit case-by-case authorization.

## Open Questions
- Does this repo get its own AireSmith-generated maintainer role, or continue as operator-paired sessions? (Affects root CLAUDE.md generation; does not block CLI work. See `sprints/aire-cli/01-project-init.md`.)
- Pilot-role observations — any v0.4.0 structure friction feeds back before bulk migration.
- First liveness-audit run (manual, per `claude/audit-spec.md`) — schedule after init completes.

## Session Notes
2026-06-12: Marathon governance-modernization session. Thirteen decisions logged; PRs #5–#9 merged; publication boundary made mechanical; private role masters versioned; migration pilot complete. This file created during the project-init sprint. Next: NORTHSTAR approval → CLI bootstrap sprint (tools/, Profile B).
