# Aire Roadmap

Milestones are outcome-bound, not time-bound, per [claude/planning-spec.md](./claude/planning-spec.md) — this roadmap follows the same planning governance Aire prescribes for the projects it governs.

---

## Milestone: Governance Consolidation
**Status:** completed

**Outcome:** Every governance rule is stated exactly once, in exactly one owning spec. Reinforcement-style duplication is removed, internal inconsistencies are resolved, and other documents reference rules by pointer rather than restatement. The per-session token cost of loading governance drops materially with no loss of meaning.

**Completion evidence:** PRs #6–#8. All Reinforcement blocks removed across the governance set; Rule Ownership section live in spec-spec v0.4.0; the role base is pointer-style (v0.4.0); two internal contradictions (promotion profile residue, push-rule exception) found and resolved; constraints digest created as the single reinforcement source.

**Dependencies:** none.

---

## Milestone: Gate-Enforced Promotion
**Status:** active

**Outcome:** Promotion to `main` is gated by machinery, not discipline. Each promotion carries a structured record (tests run, outcomes, governing specs, exact SHA), and a generated history report can present a project's full audit trail — every promotion tested, every escalation resolved — in a form digestible by non-technical readers.

**Dependencies:** Governance Consolidation.

---

## Milestone: Harness Enforcement Layer
**Status:** planned

**Outcome:** Hard constraints (push policy, branch protection, scope boundaries, commit format) are enforced deterministically through permission rules and hooks rather than prose instructions. Project-specific policy lives in committed data files; enforcement logic lives in tested code. Prose governance is reserved for judgment calls.

**Dependencies:** Governance Consolidation.

---

## Milestone: Aire CLI
**Status:** planned

**Outcome:** A single system-installed command-line tool provides spec-coverage mapping (`map`), promotion records and history reports (`history`), governance health checks (`audit`), context digests (`digest`), and environment validation (`doctor`). The binary is generic; all project-specific behavior is configuration committed in each repo. Roles orchestrate; hooks automate; the tool stays a deterministic primitive — never a daemon, never an orchestrator.

**Dependencies:** Gate-Enforced Promotion, Harness Enforcement Layer (the CLI implements both).

---

## Milestone: Role Lifecycle Management
**Status:** active

**Outcome:** Generated roles record the governance spec versions they were built against. Drift between current governance and deployed roles is mechanically detectable, and reconciliation (regeneration via AireSmith) is deliberate and auditable rather than silent.

**Dependencies:** Governance Consolidation, Aire CLI.

---

## Milestone: Cross-Platform Parity
**Status:** planned

**Outcome:** The Codex implementation reaches functional parity with the Claude Code implementation, and the base templates remain platform-neutral so additional platforms can be added without forking governance concepts.

**Dependencies:** Role Lifecycle Management.

---

## Notes
- Milestones are refined as work progresses; completed milestones gain a brief completion-evidence note.
- Major direction changes are discussed in GitHub Discussions before adoption.
