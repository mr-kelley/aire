# AI2AI Directive Specification
# ai2ai-directive-spec.md — Directive Format & Semantics

**Status:** Active  
**Version:** 1.1 (minimal v1.0 clarifications)  
**Maintainer:** Mike Kelley (project originator — Aire)

---

## Provenance
Generated for: Aire (AI2AI semantics update)  
Intended path: `templates/ai2ai-directive-spec.md`  
Regenerated on: 2025-09-08 (America/Chicago)  
Regenerator: Mike (Project Originator – Aire)

---

## Purpose
Defines the structure, enforcement requirements, and relational posture for directives issued between any two roles (AI or human-operated). AI2AI is a **compatible envelope**, not a requirement.

## File Location
`templates/ai2ai-directive-spec.md`

---

## Structure (no change)
- **AI2AI / Context Envelope** – <recipient role>
- **OBJECTIVE** – <single, testable outcome>
- **REQUIRES**
  - <path to artifact **spec** file>
  - <path to structural or behavioral governance file>
- **DELIVERABLES** – concrete artifact
- **VERIFICATION** – explicit acceptance criteria

---

## Updated Semantics

- **Artifact Delivery (MUST):** The directive SHALL produce a **Rendered Artifact**. It **SHOULD** deliver via Canvas when available; it **MAY** fall back to a single code block or file attachment with identical content. The delivery mode MUST be declared in the directive.
- **Atomicity (MUST):** Each directive requests **exactly one artifact**.
- **Chaining (SHOULD):** Larger tasks are expressed as a chain of directives. Each step references preceding artifacts in CONTEXT.
- **Role Purity (MUST):** Each role performs only those tasks allowed by its role definition.
- **Failure Paths (MUST):** The directive states rollback/next-step guidance on failure (e.g., escalate with lint report and proposed spec delta).

---

## Change Control
Regenerate-not-patch; update version & provenance.

