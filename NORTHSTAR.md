# Northstar — Aire

## Project Identity

**Aire** is an open-source governance framework for human-AI collaborative development. It gives AI roles the structure to act as accountable team members — spec-first, tested, documented, auditable — and gives the human operator durable control over vision and direction. It serves operators who build software in partnership with AI and need that partnership to survive context limits, session boundaries, and time.

## Vision

An operator can hand any project to an Aire-governed role and trust, without watching:

- Nothing reaches `main` untested, and the evidence is a record a gate physically could not skip.
- Every artifact the role produces is covered by a spec; every significant decision is logged with its rationale and alternatives.
- A fresh session resumes cold from the repo alone — state, plan, and vision intact — and continues as if no boundary existed.
- A non-technical stakeholder can read a generated project history and see for themselves that the work was fast *and* safe.

When this is true, AI roles are not assistants that write code; they are governed engineers an operator can delegate to — and, eventually, the foundation on which roles orchestrate real infrastructure.

## Success Criteria

1. **Self-hosting:** the Aire CLI is built in this repo under Aire governance, gated by itself — its own history report is the proof artifact.
2. **Cold resume:** a session started with no prior context, loading only the state pack, correctly identifies the active sprint, the applicable constraints, and the project vision — verifiable by inspection.
3. **Mechanical audit:** `aire audit` runs clean on this repository (or every finding is dispositioned); drift introduced deliberately is caught by the next run.
4. **Coverage is total:** `aire map check` exits 0 for this repo's bindings; an uncovered unit fails the gate.
5. **Generated trust:** the history report renders the repo's full development — every promotion tested, every escalation human-resolved — readable by someone with no git knowledge.
6. **Role fidelity holds at scale:** roles migrated to the current base operate across many sessions without scope drift, vision loss, or governance erosion, as judged by the operator and the audit together.

## Guiding Principles

1. **Role fidelity to operator goals, as expressed in this file's counterpart in every project.** The non-negotiable. Everything else in Aire — enforcement, spec alignment, state tracking, context loading — exists so that a role stays true to the operator's vision: no drift, no context loss, and a fresh session never costs the project its direction. When any trade-off arises, the option that best preserves vision-fidelity wins.
2. **Enforce by mechanism, not discipline.** Anything checkable by a script must not depend on model memory. Prose governs judgment; gates govern everything else.
3. **Every rule has exactly one home.** Stated once in its owning spec, referenced everywhere else. Two statements of one rule is one defect.
4. **Canonical state, derived views, gated changes.** Sources of truth are append-only or version-controlled; maps, reports, and digests are regenerable; changes pass through gates that record evidence.
5. **Roles judge; hooks automate; tools stay deterministic.** Binaries are never orchestrators and never daemons. Judgment lives at the top, in the role, where the operator's vision lives.
6. **Serve both model classes.** Every mechanism must work for frontier models and for less sophisticated local models — precomputed structure over inferred structure, deterministic interfaces over clever prompting.

## Non-Goals

- **Not an orchestration platform.** Aire governs roles; roles orchestrate. The tooling binaries never grow a control plane, a daemon, or a scheduler.
- **Not a multi-agent framework.** The model is one governed role in partnership with one human operator. (The multi-agent lineage is preserved in `templates/` as history.)
- **Not a hosted service.** Aire is files in repos: specs, roles, records, and a local CLI. Nothing phones home.
- **Not prompt-engineering tricks.** Aire's value is structure and enforcement, not magic words. If a mechanism only works on one model, it violates principle 6.
