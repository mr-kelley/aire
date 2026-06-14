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
**Status:** completed

**Outcome:** Promotion to `main` is gated by machinery, not discipline. Each promotion carries a structured record (tests run, outcomes, governing specs, exact SHA), and a generated history report can present a project's full audit trail — every promotion tested, every escalation resolved — in a form digestible by non-technical readers.

**Completion evidence:** Records (`aire history record`) and the audited history (`aire history report`) shipped in PRs #12/#14. The CI promotion gate (PR #15, sprint 04) enforces it server-side and was verified on both halves: a deliberate failing-test PR (#16) was *blocked* by the required `tests` check (prevention), and the gate's first push-to-main run *caught a real recordless code merge* and went red until the record was pushed (detection). Two tested promotions, zero findings, "every code merge into main carries a tested promotion record." Portable to Forgejo Actions for lab repos.

**Dependencies:** Governance Consolidation.

---

## Milestone: Harness Enforcement Layer
**Status:** planned

**Outcome:** Hard constraints (push policy, branch protection, scope boundaries, commit format) are enforced deterministically through permission rules and hooks rather than prose instructions. Project-specific policy lives in committed data files; enforcement logic lives in tested code. Prose governance is reserved for judgment calls.

**Design notes (input, pre-spec):**
- Classify each hard constraint by the **weakest permission mode it must survive**. The enforcement tiers are not equal under `--dangerously-skip-permissions` (bypass mode): prose does not survive it, and the server-side promotion gate (off-box, protects canonical history regardless of working-tree state) is the strongest tier. Pick the tier to match the constraint.
- **Open empirical question, gates the spec:** does a PreToolUse hook still *block* under bypass mode? The Outcome above lists hooks as a deterministic mechanism, but current Claude Code docs are ambiguous (`bypassPermissions` skips *prompts*, yet a hook exit-2 blocks before permission rules are evaluated). Verify with a test before treating hooks as a bypass-surviving guard rather than an audit layer.
- Harness policy (protected paths, egress allowlist, push posture) should be **committed, derivable data** — the coverage/digest declare-once-derive pattern extended to enforcement, so one source feeds both `aire audit` (verify) and any sandbox/permission config (enforce).
- Closing this milestone's hook layer is what resolves the open layered-enforcement decision.

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
