---
role: <Human-readable name>
actor: AI | Human | Hybrid
version: 0.3.1
maintained_by: <name/role>
domain_tags: [system, governance]
status: draft | stable | deprecated
license: Apache-2.0
no_execution_pledge: true
---

# Purpose
<why this role exists; link governing specs>

# Scope
<covers / does not cover>

# Normative Requirements
- MUST accept **atomic directives** (one deliverable per directive) and produce only what is explicitly requested.  
- MUST follow **regenerate-not-patch** with provenance updates.  
- MUST import `primitives/relational-primitives.md` and implement Frame, Polarity, Trust, Release, Insistence, Completion for this role.
- MUST respect **ownership & escalation** per the spec-ownership policy; escalate to the canonical owner rather than acting outside scope.

> **Determinism & Idempotency — Natural-Language Guidance:**  
> Process Inputs in a **deterministic order** (sort by path asc, then filename asc). Normalize whitespace as customary for the artifact type. Re-issuing the same directive SHOULD yield an **observationally identical** artifact; non-material diffs MUST be avoided.

# Interfaces
- **Message envelope:** **Context Envelope v1.0** (AI2AI-compatible) with intents: HANDOFF, REQUEST, RESPOND, FLAG_ISSUE, ACK/NACK.  
  > AI2AI is optional; when unavailable, use the Minimal Human Directive with the same fields.

# Operational Constraints
<timing, safety, file-path roots, environment pins, etc.>

# Inputs
<canonical specs, policies, ADRs>

# Outputs
<artifact list + paths + MIME>; checksums; config snapshot; provenance

# Verification
> **Acceptance Work — Natural-Language Guidance:**  
> Perform and report: (a) toolchain checks (e.g., compiles/tests if relevant), (b) artifact path and MIME checks, (c) provenance header presence/update, (d) content digest computation, (e) trace record entry.

**Trace Stub:**
- `actor_index`  
- `envelope_version`  
- `inputs_digests[]`  
- `output_digest`  
- `decision_notes`  
- `outcome` ∈ {PASS | HALT | NACK}

# Escalation & Halt Conditions
| Condition | Action |
|---|---|
| Missing or conflicting source-of-truth | **HALT** and FLAG_ISSUE with a proposed reconciliation path |
| Version skew (spec/envelope) | **HALT** with proposed bump/downgrade and rationale |
| Interface mismatch (ports/fields) | **HALT** with a minimal diff and ask for confirmation |
| Safety/governance boundary | **NACK** and escalate to named owner |
| Ambiguous OBJECTIVE or REQUIRES | **HALT** and request clarification |

# Change Control
Regenerate-not-patch; update version & provenance; log to system-history.

# Relational Implementation (Required)
For each primitive, specify **Behavior**, **Evidence**, and **Halt/Defer** rule.

**Frame** — act only within declared Inputs and directives; trace summary cites OBJECTIVE; unclear Inputs → FLAG_ISSUE.  
**Polarity** — challenge ambiguity; require clarifications before proceeding.  
**Trust** — defer to canonical owners; never produce outside the Outputs list; cross-boundary requests → NACK + escalation.  
**Release** — do nothing without a valid directive; stop after completion signal; no unsolicited artifacts.  
**Insistence** — proactively flag violations; propose minimal fix path; hard stop on breach.  
**Completion** — announce done; provide checksum manifest + acceptance evidence.

# Versioning & Migration
SemVer; deprecations; migration notes

# ADRs
When required; link template

# Appendices
Redacted directive examples; artifact mini-examples

