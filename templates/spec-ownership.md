---
title: Specification Ownership Index (Template)
version: 0.1
maintained_by: Lead Architect (project)
domain_tags: [system, governance, specs]
status: draft
license: Apache-2.0
---

# Purpose
Provide a canonical, auditable index of all specification files in the project and their functional domains.
This index supports ownership clarity, routing, and auditability across teams.

# Ownership Rules
- Every spec file must appear in this index before implementation begins.
- When multiple architects exist on a team, the Lead Architect owns this file and `spec-spec.md`.
- Additional metadata is allowed, but optional and architect-defined.

# Spec Index
Maintain a table using the following columns:

| Spec File Path | Domain | Notes/Metadata (Optional) |
|---|---|---|
| `specs/...` | <domain> | <optional flags or notes> |

# Notes
- Spec file paths must be project-relative and accurate.
- If generalized specs exist (not mapped 1:1 with implementation files), their paths must be included here.
- Architects may add optional flags or metadata in the Notes/Metadata column for future use.
