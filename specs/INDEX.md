# Spec Index — aire

All specs governing this repository and its deliverables, sorted by path. The governance set in `claude/` defines the framework itself; specs under `specs/` (as they appear) govern this repo's own implementation work (the Aire CLI). Per `claude/documentation-spec.md`.

| Path | Title | Description | Status |
|---|---|---|---|
| `claude/audit-spec.md` | Governance Liveness Audit Specification | Recurring stale-governance detection: 9 mechanical checks + judgment walk | draft |
| `claude/claude.git-hygiene.md` | Git Hygiene Strategy | Branching, commits, tested promotion, promotion records | draft |
| `claude/claude.role.base.md` | Base Role Template | Structure all roles derive from; coverage binding + governance pins | draft |
| `claude/constraints-digest.md` | Constraints Digest | One-line-per-rule session reinforcement, derived from owning specs | draft |
| `claude/coverage-spec.md` | Coverage Contract Specification | Coverage models, role bindings, covers: declarations, mapper interface | draft |
| `claude/decision-log-spec.md` | Decision Log Specification | Append-only JSON decision events, IDs, classes A/B/C | draft |
| `claude/documentation-spec.md` | User-Facing Documentation Specification | README/HOWTO/reference requirements; this index's format | draft |
| `claude/github-issues-spec.md` | GitHub Issues Governance | Optional: Issues lifecycle for collaborative projects | draft |
| `claude/planning-spec.md` | Planning Artifacts Specification | NORTHSTAR, ROADMAP, sprints | draft |
| `claude/project-init-spec.md` | Project Initialization Specification | Bootstrap sequence; CLAUDE.md structure | draft |
| `claude/promotion-record-spec.md` | Promotion Record Specification | promote/<slug> tag schema; history report generator | draft |
| `claude/spec-spec.md` | Specification Structure Standard | Spec structure, spec-first, Rule Ownership | draft |
| `claude/state-pack-spec.md` | Session Context Specification | Static-first session load order | draft |
| `claude/state-tracker-spec.md` | Project State Tracker Specification | STATE.md format and maintenance | draft |
| `specs/tools/aire/architecture-spec.md` | Aire CLI Architecture Specification | Package, dispatch, config model, DEC-000010 constraints | draft |
| `specs/tools/aire/audit-spec.md` | aire audit Specification | Liveness audit command surface; nine mechanical checks; severities owned by claude/audit-spec | draft |
| `specs/tools/aire/digest-spec.md` | aire digest Specification | Constraints-digest command surface; render/check; derivation owned by spec-spec | draft |
| `specs/tools/aire/doctor-spec.md` | aire doctor Specification | Read-only repo/environment validation; extensible check registry | draft |
| `specs/tools/aire/history-spec.md` | aire history Specification | Promotion record command surface (record side); format owned by promotion-record-spec | draft |
| `specs/tools/aire/map-spec.md` | aire map Specification | Coverage command surface + code engine; models owned by coverage-spec | draft |
