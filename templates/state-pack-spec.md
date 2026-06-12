---
title: State Pack Specification (Template)
version: 0.1
maintained_by: Lead Architect (project)
domain_tags: [system, governance, state, ai2ai]
status: draft
license: Apache-2.0
---

# Purpose
Define the canonical, minimal, and deterministic **state pack** for stateless role execution.
The state pack is the complete input bundle required to reproduce a role run without relying on conversation history.

# File Location
`templates/state-pack-spec.md`

# Definitions
- **State pack**: The set of files provided to a stateless role for a single directive.
- **Target role**: The role receiving the directive.
- **Directive bundle**: The union of the state pack plus any explicitly listed input artifacts.

# Required Contents (Minimum)
Every stateless directive MUST include the following paths in the state pack:
1) The directive log file path: `directives/<role-name>/<timestamp>.md`
2) `state/tracker.json`
3) `templates/state-tracker-spec.md`
4) `templates/ai2ai-directive-spec-v2.0.md` (or the project-declared AI2AI spec)
5) Target role spec file (e.g., `teams/<team>/roles/<role>.role.md`)
6) Team spec file (e.g., `teams/<team>/<team>.team.md`)
7) All policy/spec paths referenced by the directive (e.g., `templates/spec-spec.md`, `templates/spec-ownership.md`, ADRs)
8) All directive-listed input artifacts
9) `templates/decision-log-spec.md` **if** decisions may be recorded

Reinforcement (MUSTs):
- All required contents above are included for stateless execution.
- The bundle is sufficient to reproduce the role output without conversational memory.
- The directive `REQUIRES` list enumerates the full state pack (in order), plus any additional inputs.

# Exclusions (Normative)
- **Do not include other role specs** unless the directive explicitly requires them.
- **Do not include the entire `roles/` directory** as a shortcut.
- **Do not include unrelated artifacts** not referenced by the directive or required by this spec.

Reinforcement (MUSTs):
- Only the target role spec is included unless explicitly required otherwise.
- Unrelated role files are excluded.

# Ordering & Determinism
State pack contents MUST be listed in deterministic order:
1) Required contents (items 1–9) in the order above
2) Remaining directive-listed inputs, sorted by path asc, then filename asc

Reinforcement (MUSTs):
- State packs are ordered deterministically.
- `REQUIRES` MUST enumerate state pack contents in this deterministic order.

# Role Responsibilities
## Architect
- MUST declare the required state pack in directives to stateless roles.
- MUST ensure directives list any additional required artifacts explicitly.

## Runner (or Orchestrator)
- MUST construct the state pack exactly as declared.
- MUST validate exclusions (no extra role files).
- MUST record the state pack list in the directive log.

# Verification
An invocation is compliant if:
1) All required contents are present.
2) No excluded role files are included.
3) The list is deterministic and complete.
4) The directive log references the exact state pack list.

Reinforcement (MUSTs):
- Required contents present, exclusions enforced, deterministic ordering, and logging.

# Change Control
Update version and provenance on every change.
