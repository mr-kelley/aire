---
title: Constraints Digest
version: 0.1.0
maintained_by: Aire System Architect (ASA)
domain_tags: [system, governance, digest]
status: draft
platform: claude-code
license: Apache-2.0
---

# Constraints Digest

One line per active judgment-tier rule, each pointing to its owning spec. This file is a **derived summary** — the owning specs are authoritative (see Rule Ownership in `claude/spec-spec.md`). Reference it from CLAUDE.md (or inject at session start) for recency reinforcement. Audit it against the owning specs whenever governance changes; a digest line that disagrees with its owning spec is a defect in the digest.

- Spec-first: no implementation without a governing spec — `claude/spec-spec.md`
- Every rule stated once in its owning spec; pointers elsewhere — `claude/spec-spec.md`
- One deliverable at a time; complete or explicitly hand back — `claude/claude.role.base.md`
- Escalate ambiguity; never guess — `claude/claude.role.base.md`
- Tests are a completion requirement, never optional — `claude/spec-spec.md` (Test Strategy)
- User-facing docs accompany user-visible features — `claude/documentation-spec.md`
- Log Class B decisions; escalate Class C — `claude/decision-log-spec.md`
- Maintain STATE.md on meaningful state changes — `claude/state-tracker-spec.md`
- Load session context static-first at session start — `claude/state-pack-spec.md`
- Work within the active sprint and milestone — `claude/planning-spec.md`
- Atomic commits, `type(scope): summary` format; commit before task switches — `claude/claude.git-hygiene.md`
- Promote to main only with recorded test PASS (Profile B) — `claude/claude.git-hygiene.md`
- Pushing is human-only; PR creation needs explicit per-case authorization — `claude/claude.git-hygiene.md`
- Never delete branches without explicit user request — `claude/claude.git-hygiene.md`
- Implement the six relational primitives — `claude/claude.role.base.md`

# Change Control
Update version and provenance on every change. Re-derive from owning specs when any governance spec changes.

## Provenance
- time: 2026-06-12
- summary: Initial digest, created per DEC-000003 as the successor to in-spec Reinforcement blocks: same recency-reinforcement intent, placed at the session boundary, with a single source that cannot fork silently from the owning specs.
