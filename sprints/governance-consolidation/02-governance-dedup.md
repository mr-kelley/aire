---
sprint: 2
title: De-duplication — Rule Ownership, pointer-style role base, constraints digest
milestone: Governance Consolidation
status: completed
---

## Goal
Every rule stated exactly once in its owning spec (DEC-000003); resolve the push-rule contradiction (DEC-000011).

## Deliverables
- Reinforcement blocks removed across the governance set; Rule Ownership section (spec-spec v0.3.0); pointer-style role base (v0.3.0); git-hygiene v0.3.1 with codified PR authorization; constraints digest wired into project-init v0.2.0.

## Acceptance Criteria
- `grep -rn '^Reinforcement' claude/*.md` empty; role base and git-hygiene state the same remote-publishing rule. (Profile A.)

## Completion
Branch `work/2026-06-12T172718Z/governance-dedup`, five commits e15f0ea…71e880f, merged via PR #7.
