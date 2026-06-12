---
sprint: 1
title: Coverage contract and governance version pinning
milestone: Role Lifecycle Management
status: completed
---

## Goal
Replace universal spec-per-file with declared, mechanically verifiable coverage (DEC-000006); make governance-to-role drift visible via version pins (DEC-000008).

## Deliverables
- coverage-spec v0.1.0; spec-spec v0.4.0; role base v0.4.0 (binding + pin block + pinning lifecycle); aire-smith v0.7.0 (generates pointer-style, stamps pins, derives bindings; first pinned role).

## Acceptance Criteria
- Role base template and aire-smith's own header agree on binding/pin shape; no spec-per-file mandate outside provenance. (Profile A.)

## Completion
Branch `work/2026-06-12T180917Z/coverage-contract-and-pinning`, commits 9275229/0a7d4f5, merged via PR #8.
