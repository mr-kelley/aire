---
sprint: 1
title: Harness Enforcement — governing spec
milestone: Harness Enforcement Layer
status: active
---

## Goal
Write the governing spec for the Harness Enforcement Layer milestone, formalizing the layered enforcement model (DEC-000001) as a reviewable spec — spec-first, before any enforcement code. The spec folds in the 2026-06-14 empirical finding that PreToolUse hooks block under bypass mode, which clears the question that previously gated the milestone.

## Deliverables
- `claude/harness-enforcement-spec.md` (v0.1.0) — the enforcement model (Layer 0–3 ladder + off-box gate), bypass-mode survivability classification, the placement rule, the policy-as-data / declare-once-derive convention, the `aire audit` verification contract, the reference implementation scope (Sprints 1–4), and the open design questions for operator decision.
- **DEC-000001** (private) — outcome updated with the empirical finding (Layer 2 survives bypass); milestone now active to implement.
- `ROADMAP.md` — Harness Enforcement Layer `planned → active`; design-note's open empirical question flipped to *resolved*; governing-spec pointer added.
- `STATE.md` — active sprint and active milestone reflected.

## Acceptance Criteria
- [ ] `claude/harness-enforcement-spec.md` exists and conforms to `claude/spec-spec.md` required sections (Purpose, Scope, Inputs, Outputs, Responsibilities, Edge Cases, Test Strategy, Completion Criteria, Change Control).
- [ ] The spec faithfully formalizes DEC-000001's four-layer model and adds the bypass-survivability axis grounded in the recorded empirical test.
- [ ] Every existing hard constraint in the governance set is assignable to a layer under the placement rule (none left unclassifiable).
- [ ] The concrete enforcing code/file formats are explicitly deferred to forthcoming implementation specs (no implementation in this sprint).
- [ ] Open design questions are enumerated for operator decision before implementation sprints.
- [ ] Gates green: `aire digest check`, `aire audit`, `aire map`, `aire doctor`, full test suite.

## Dependencies
- DEC-000001 (layered harness enforcement) — the approved decision this spec formalizes.
- The 2026-06-14 hook-under-bypass empirical test — recorded in project memory; resolved the question gating this milestone.
- Gate-Enforced Promotion milestone — supplies the off-box backstop tier referenced by the model.

## Notes
This is the foundational sprint of the milestone the operator identified as upstream of Role Lifecycle Management: roles can declare the governance version they were built against, but those declarations are only as strong as the enforcement beneath them. Spec-first per Aire's own rule — the operator reviews the model (tiers, policy schema, who-guards-the-guards) before any enforcement code is written. The implementation sprints (`aire hook` shim, policy data + wiring, audit harness check) follow once the open design questions are decided.
