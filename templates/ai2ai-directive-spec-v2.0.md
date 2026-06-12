# AI2AI Directive Specification (Revised)

**Status:** Active  
**Version:** 2.0 (Revised for Directive Logging & Autonomous Multi‑Agent Execution)  
**Maintainer:** Project Owner (Human User)

---

## Provenance
Revised via ROLE.REVISE directive to incorporate mandatory directive recording, completion/blocker semantics, autonomous decision‑making responsibilities, and expanded RESPOND behavior.

Intended path: `templates/ai2ai-directive-spec-v2.0.md`  
Revision date: 2026 (the original `$(date)` substitution was never expanded; exact date not recorded)  
Regenerator: Aire RoleSmith

---

## Purpose
This specification defines the structure, semantics, and behavioral requirements for AI2AI directives within Aire multi‑agent systems. This revision introduces:

- Mandatory file‑based recordkeeping for **every** AI2AI directive.  
- New responsibilities for **Architect** (autonomous decision‑making, directive logging, completion/blocking signals).  
- New responsibilities for **Runner and all execution roles** (RESPOND messages appended to directive logs).  
- Strict end‑of‑output signaling fields for both directive creation and directive response.  
- Strengthened chain‑of‑custody guarantees for fully auditable agent workflows.

---

## Structure (No Change)
Each directive consists of:

- **AI2AI / Context Envelope** – identifies recipient role  
- **OBJECTIVE** – single, testable outcome  
- **REQUIRES** – list of required specs/assets  
- **DELIVERABLES** – required artifact(s)  
- **VERIFICATION** – explicit acceptance criteria

The envelope remains unchanged, but the *semantics* governing its handling have been expanded.

---

# Revised Semantics (v2.0)

## 1. Mandatory Directive Logging
Every AI2AI directive MUST be permanently recorded.

### 1.1 Directory Structure
For any directive sent to role `<role-name>`:
```
directives/<role-name>/$(date +%Y%m%d-%H%M%S).md
```
The filename timestamp MUST be produced by executing the `date` command at directive creation time.
Hardcoded dates (including assumed day components) are forbidden.
The file **must contain the directive exactly as it was issued**, with no deletions or structural reformatting.

### 1.2 Directive Envelope Duplication
The directive file MUST include two consecutive, identical copies of the directive envelope:
- AI2AI / Context Envelope
- OBJECTIVE
- REQUIRES
- DELIVERABLES
- VERIFICATION

The copies MUST be byte-for-byte identical. If the directive must change, issue a new directive file.

### 1.3 Creation Rules
- **Architect MUST create the directive file** whenever it issues a directive.  
- Other roles (Runner, etc.) **MUST NOT create directive files**; they append RESPOND messages instead.

### 1.4 Required Final Output Field (Architect Only)
When Architect issues a directive, the final line of its output MUST be:
```
DIRECTIVE_FILE: directives/<role-name>/<filename>
```
This line must always be present and must always be the **last line**.

Reinforcement (MUSTs):
- Every directive is permanently recorded.
- Directive filenames use the `date` command output at creation time.
- Directive files contain two identical copies of the envelope.
- Architect creates the directive file; other roles do not.
- Architect output ends with the required `DIRECTIVE_FILE:` line.

### 1.5 State Tracker Requirements
Every directive MUST include `state/tracker.json` and `templates/state-tracker-spec.md` in REQUIRES.
The executing role MUST update `state/tracker.json` per the state tracker spec before completion.

Reinforcement (MUSTs):
- Directives always include the state tracker and its spec in REQUIRES.
- The state tracker is updated and appended on every directive.

### 1.6 State Pack Requirements (Stateless Roles)
For stateless roles, the directive `REQUIRES` list MUST enumerate the full state pack in deterministic order, as defined by `templates/state-pack-spec.md`.
Wildcard role paths (e.g., `roles/*.md`) are non-compliant unless explicitly required by the directive and allowed by the state-pack spec.

Reinforcement (MUSTs):
- `REQUIRES` enumerates the full state pack for stateless roles in deterministic order.
- Wildcard role paths are non-compliant unless explicitly required and allowed by the state-pack spec.

---

## 2. Autonomous Decision‑Making (Architect)
Architect must not ask for human input when presented with a choice.

### 2.1 Autonomous Choice Rule
When multiple valid paths exist:
- Architect MUST select the best option using the information available.  
- Architect MUST NOT pause for human clarification.

### 2.2 Work Stop Conditions
Architect stops only if:
1. **BLOCKED** – A blocker exists that the AI cannot overcome.  
2. **COMPLETE** – The final deliverable of the project has been achieved.

### 2.3 Required Terminal Keywords
At the end of output, Architect MUST emit exactly one of:

#### Blocked:
```
<explanation>
BLOCKED
```

#### Complete:
```
<description-of-deliverable>
COMPLETE
```

If Architect is simply performing a normal operation with no blocker or completion event, it ends normally with no keyword.

Reinforcement (MUSTs):
- Architect selects the best option without pausing for human clarification.
- Architect output ends with exactly one required terminal keyword when blocked or complete.

---

## 3. RUNNER & Non‑Architect Role Semantics
All non‑Architect roles (Runner in this test system) must:

### 3.1 Execute Assigned Work
They MUST execute the directive to the best of their ability.

### 3.2 Produce a RESPOND Message
Each role MUST output:
- A description of the work done.  
- The execution outcome.  
- A clarification request if necessary.
- A checksum manifest for every artifact touched (path + checksum).

### 3.3 Append RESPOND to Directive Log
RESPOND messages MUST be appended to the *same directive file* created by Architect.

### 3.4 Final Required Output Line
The final line of a non‑Architect role’s output MUST be:
```
RESPONSE SENT: <path/to/original/directive/file>
```
This must always be the last line.

Reinforcement (MUSTs):
- Non-Architect roles execute assigned work to the best of their ability.
- Each non-Architect response includes work description, outcome, and clarification request if needed.
- RESPOND messages append to the original directive file.
- Non-Architect output ends with the required `RESPONSE SENT:` line.
 - Responses include a checksum manifest for all touched artifacts.

---

## 4. Full Chain‑of‑Custody Requirement
All AI2AI interactions must be:
- Traceable  
- Ordered  
- Deterministic  
- Recorded

The directive file becomes the authoritative ledger for:
- The original directive  
- All RESPOND messages  
- All follow‑up entries  

No role may modify previous entries except to append.

---

## 5. Role Purity (No Change)
Roles MUST act only within their definitions.  
Execution roles cannot architect; architect roles cannot execute.

Reinforcement (MUSTs):
- Roles stay within their defined duties.

---

## 6. Error Handling & Failure Paths
### 6.1 Failed Execution (Runner)
Runner MUST produce a RESPOND with:
- Description of failure  
- Logs or error text if available  
- Whether retrying is possible

Reinforcement (MUSTs):
- Runner failure responses include failure details, logs, and retry feasibility.

### 6.2 Failure of Architect’s Autonomous Rules
If Architect cannot determine a valid next step, this is a **BLOCKED** state.

---

## 7. Verification Requirements
Any directive handled under this specification MUST:
1. Produce a complete directive log file.  
2. Contain mandatory final lines (`DIRECTIVE_FILE:` or `RESPONSE SENT:`).  
3. Preserve all append‑only semantics.  
4. Maintain deterministic formatting and ordering.  
5. Respect role purity and operational constraints.
6. Include the state tracker in REQUIRES and update `state/tracker.json` per spec.
7. Provide a checksum manifest for every artifact touched.

Reinforcement (MUSTs):
- Every handled directive results in a complete log file.
- Final-line markers are always present.
- Logs remain append-only and deterministic.
- Role purity and operational constraints are enforced.
 - State tracker inclusion, updates, and checksum manifests are required.

---

## 8. Change Control
- Future modifications must be made via ROLE.REVISE directives.  
- This revision supersedes version 1.1 but retains backward compatibility for envelope structure.

---

## 9. Appendices
### A. Example Architect Output Triggering a Directive
Note: directive log files include two consecutive copies of the envelope; the example shows one copy for brevity.
```
AI2AI — REQUEST → Runner
OBJECTIVE: Execute build pipeline step
REQUIRES: [...]
DELIVERABLES: [...]
VERIFICATION: [...]
DIRECTIVE_FILE: directives/runner/2025-01-05-153022.md
```

### B. Example Runner Response
```
RESPOND — Runner → Architect
Executed: build.sh
Outcome: success
Logs: [...]
RESPONSE SENT: directives/runner/2025-01-05-153022.md
```

---

# END OF SPEC
