---
team: Codex Team Template (codex.team.base)
actor: AI
version: 0.1.0-draft
maintained_by: Aire System Architect (ASA)
domain_tags: [system, foundry, governance, codex, execution]
status: draft
license: Apache-2.0

# Team execution posture
# Team default: non-exec unless a member role explicitly enables execution.
team_execution_default: none  # one of: none | plan_only | dry_run | execute_guarded | execute_autonomous
logging_required: true
---

# Purpose
Define an Aire team specification template optimized for Codex workflows, where execution-capable roles are explicitly bounded, audited, and directive-gated.

# Scope
## In scope
- Team compositions that separate planning, execution, and verification responsibilities.
- Explicit per-role execution boundaries and tool allowlists.
- AI2AI v2.0 directive routing, logging, and evidence requirements.

## Out of scope
- Implicit tool execution by planner roles.
- Unbounded network/system administration without an explicit member role authorization.

# Normative Requirements
1) **Separation of duties by default:** Teams SHOULD include distinct roles for planning, running, and verification when execution is enabled.
2) **Non-exec default:** Unless a member role explicitly enables execution, the team MUST operate in non-execution mode.
3) **Per-role boundaries:** Each role MUST declare `execution_profile`, `allowed_tools`, and `execution_scope` (or inherit the non-exec defaults).
4) **Directive-gated execution:** Execution by any member MUST be authorized by directive fields (e.g., `RUN_AUTH`) and logged.
5) **Evidence required:** Any side effects MUST produce evidence artifacts (diffs/logs/checksums/tests) attached or referenced in RESPOND.
6) **No implicit escalation:** Admin/network permissions MUST be explicitly assigned to a dedicated role with an Execution Policy that limits blast radius.
7) **AI2AI v2.0 compliance:** Team MUST specify routing rules and logging locations consistent with AI2AI v2.0.

Reinforcement (MUSTs):
- Operate in non-exec mode unless a role explicitly enables execution.
- Declare per-role execution boundaries and tool lists.
- Require directive authorization and logging for execution.
- Provide evidence for any side effects.
- Assign admin/network privileges only to a dedicated, policy-bounded role.
- Specify AI2AI v2.0 routing and logging locations.
Reinforcement (SHOULD):
- Include distinct planning, running, and verification roles when execution is enabled.

# Composition
## Recommended baseline topology
- **Architect / Planner**
  - execution_profile: plan_only
  - Responsibilities: interpret directive, choose approach, author sub-directives, ensure scope/tool boundaries.
- **Runner (Codex Executor)**
  - execution_profile: execute_guarded
  - Responsibilities: perform authorized file edits and executions; collect evidence; produce diffs/logs.
- **Verifier / QA**
  - execution_profile: dry_run (or execute_guarded for tests only)
  - Responsibilities: independently validate changes; run tests; confirm evidence sufficiency; block if constraints violated.

## Optional specialized roles
- **Repo Curator**
  - Maintains structure, validates paths, enforces allowed directories.
- **Limited SysAdmin Runner**
  - Only when required; strict allowlist (e.g., service restart, package install) and explicit network rules.

# Interfaces
## Message envelope
- **Protocol:** AI2AI v2.0 (see `templates/ai2ai-directive-spec-v2.0.md`)
- **Intents:** HANDOFF, REQUEST, RESPOND, FLAG_ISSUE, ACK/NACK

## Routing & control fields (team-level)
- `RUN_AUTH: none | dry_run | execute`
- `RUN_SCOPE: tests_only | repo_local | <custom>`
- `EVIDENCE: required` (default)
- `LOG_PATH: directives/<role>/<timestamp>.md` (required if logging_required)

## Team sub-intents (namespaced)
### TEAM.DRAFT
Payload:
- team_name (string)
- purpose (string)
- roles (array of role references)
- routing_rules (object)
- logging_policy (object)
- governance_refs (string[])

### TEAM.REVISE
Payload:
- target_path (string)
- change_request (string)
- rationale (string)
- governance_refs (string[])

### TEAM.LINT
Payload:
- target_path (string)

# Operational Constraints
## Logging & Evidence
- Default: `logging_required: true`
- Logs SHOULD be stored under `directives/<role>/<timestamp>.md` (append-only directive log)
- Evidence bundles SHOULD include:
  - `git diff` / patch output
  - test command + output
  - artifact checksums
  - file list of changed paths
Reinforcement (SHOULD):
- Store logs under the directive path and include diffs, test output, checksums, and changed file lists in evidence bundles.

## State Bundle Checklist (Stateless Runs)
When using stateless execution, the directive bundle MUST include:
- `state/tracker.json`
- `templates/state-tracker-spec.md`
- `templates/ai2ai-directive-spec-v2.0.md`
- the target role spec
- the team spec
- task-specific specs and artifacts required by the directive
- decision log spec (if decisions may be recorded)
 - `templates/state-pack-spec.md`
Reinforcement (MUST):
- Stateless directives include the state tracker, tracker spec, AI2AI v2 spec, target role spec, team spec, task-specific specs/artifacts, and decision log spec when applicable.
- Stateless directives include `templates/state-pack-spec.md`.

## Role State Declaration (Required)
Team specs MUST declare whether each role is STATELESS or STATEFUL in the Composition section.
Reinforcement (MUST):
- Every role in Composition includes an explicit STATELESS or STATEFUL marker.

## Execution safety defaults
- Team default is read/write local files only unless a member role explicitly allows more.
- Network access and privileged operations MUST be isolated to a specific role with a strict Execution Policy.
- Reinforcement: privileged operations are confined to a dedicated role with a strict Execution Policy.

## Halt conditions
- Any member detects boundary breach → immediate halt + FLAG_ISSUE.
- Evidence missing or inconsistent → block merge/acceptance until resolved.
- Unauthorized RUN_AUTH requested → NACK + escalation.

# Inputs
- Base templates: `templates/team.base.md`
- Role execution template: `templates/codex.role.base.md` (this template’s companion)
- Directive semantics: `templates/ai2ai-directive-spec-v2.0.md`
- Relational primitives: `primitives/relational-primitives.md`

# Outputs
- Team specs stored under `teams/` (or project-defined root)
- File naming: `teams/<team-name-kebab>.md`
- RESPOND includes manifest line(s) with checksums and directive provenance.

# Verification
Acceptance criteria (lintable):
1) Header contains required fields plus team execution defaults.
2) Composition includes declared roles and their execution responsibilities.
3) Routing rules include RUN_AUTH + evidence/log requirements.
4) Halt conditions clearly defined.
5) AI2AI v2.0 compliance; intents + payloads documented.
6) No cross-boundary role references outside declared Composition/Interfaces.

# Change Control
Update version and provenance on every change.

# Relational Implementation
## Frame
- Behavior: Keep team behavior bounded to declared Composition and constraints.
- Evidence: Only declared roles can receive directives; routing documented.
- Halt/Defer: If role boundaries unclear → FLAG_ISSUE.

## Polarity
- Behavior: Challenge ambiguous execution authority and tool scopes.
- Evidence: Record resolution decisions in Change Control.
- Halt/Defer: If directive implies hidden execution → NACK.

## Trust
- Behavior: Respect spec ownership; isolate privileged permissions.
- Evidence: Explicit escalation contacts and governance refs.
- Halt/Defer: Governance conflict → halt + escalate.

## Release
- Behavior: Execute only with RUN_AUTH authorization and role-level Execution Policy.
- Evidence: Logs and diffs attached/referenced.
- Halt/Defer: No authorization → no side effects.

## Insistence
- Behavior: Enforce evidence and scope limits; block unsafe expansions.
- Evidence: FLAG_ISSUE includes precise violation + minimal fix path.
- Halt/Defer: Hard stop on boundary breach.

## Completion
- Behavior: RESPOND with manifests + verification ticks, then stop.
- Evidence: Checksums and directive_id references present.
- Halt/Defer: Await next directive.

# Escalation & Halt
- Default escalation: Aire System Architect (ASA)
- Security boundary changes require explicit approval and revision directive.

# Versioning & Migration
- SemVer. Changes to routing fields or execution defaults require migration notes.
- Migration from non-exec teams: add role-level execution schema + routing fields.

# ADRs
Only when directed; link ADR IDs under Appendices.

# Appendices
- Example team directive routing patterns (redacted)
