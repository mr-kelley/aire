---
sprint: 7
title: aire digest — derived constraints digest (regenerate-not-patch)
milestone: Aire CLI
status: active
---

## Goal
Implement `aire digest` — the subcommand that makes `claude/constraints-digest.md` a **derived artifact that cannot silently fork** from its owning specs. Closes the Aire CLI milestone (last subcommand) and cures a documented wound: the governance-drift investigation found *regenerate-not-patch* had been a dead letter for months — stale digest lines persisted because nobody re-derived the digest. `aire digest` makes regeneration mechanical and drift fail-closed.

The mechanism is **declared-not-inferred**, mirroring the coverage contract's `covers:` field (no heuristic MUST-extraction from prose — that path was rejected to avoid the cry-wolf noise the audit was tightened against). Each owning spec declares its digest-bound clauses in a `digest:` header block; `aire digest render` re-derives the digest from those declarations; `aire digest check` regenerates and diffs against the committed file, failing closed on any mismatch.

## Deliverables
- **DEC-000020** (private) — the `digest:` declaration mechanism: derive the constraints digest from declared clauses in owning specs, ordered deterministically; resolution and format. Establishes the rule the spec change implements.
- `claude/spec-spec.md` — Rule Ownership extension: the constraints digest is a derived artifact; owning specs declare their digest-bound clauses in a `digest:` header block; the committed digest MUST equal the regeneration. Version + provenance bump.
- `claude/constraints-digest.md` — regenerated from the new declarations (byte-identical to `aire digest render`); provenance notes the derivation source.
- `digest:` header blocks added to the ~5 owning specs currently feeding the digest (declared-not-inferred).
- `specs/tools/aire/digest-spec.md` v0.1.0 — command surface for `render` / `check`, exit codes, the deterministic derivation + ordering rules (digest *semantics* deferred to `claude/spec-spec.md` + `claude/constraints-digest.md`, Rule Ownership). `covers: tools/aire/digest.py`.
- `tools/aire/digest.py` — the deriver: collect `digest:` clauses from owning specs, render the canonical digest, `check` (regenerate + diff, fail-closed) and `render` (emit to stdout).
- `tools/aire/cli.py` — `digest` dispatch; `specs/tools/aire/architecture-spec.md` v0.1.4.
- `specs/INDEX.md` — digest-spec registered.
- `tests/tools/aire/test_digest.py` — render determinism, check pass/drift (added/removed/edited clause), dangling-spec fail-closed, read-only, exit codes.

## Acceptance Criteria
- [x] `aire digest render` emits the canonical digest from declared `digest:` clauses; deterministic ordering (spec path ascending, then declaration order); byte-identical across runs.
- [x] `aire digest check` regenerates and diffs against `claude/constraints-digest.md`; exit 0 on match, exit 1 on drift (a substantive negative), exit 2 on misconfiguration (unreadable spec, malformed `digest:`).
- [x] The committed `claude/constraints-digest.md` equals `aire digest render` (the digest is now genuinely derived, not hand-maintained).
- [x] Audit check #3 (digest agreement) still passes; `aire digest check` is the stronger, regenerating successor for the forward direction.
- [x] Tests pass on the work branch tip (104 green: 86 prior + 18 new).
- [x] **Dogfood:** `aire digest check` on aire exits 0 (15 clauses match) — the dead-letter is now mechanically un-droppable on this repo. With it, `audit` reports 0 defect, `map check` 58/58, `doctor` 6 ok/1 warn.
- [ ] Promoted to `main` with a tested promotion record (post-merge, Profile B).

## Honest scoping
- `check` verifies the digest equals its regeneration — i.e. every declared clause appears and no undeclared line lingers. It does **not** verify that a spec's prose still *states* the rule a `digest:` clause summarizes (clause-vs-prose agreement is judgment-tier, same boundary the audit drew). What it guarantees is that the digest cannot drift from the *declarations*, and the declarations live beside the rules they summarize — so a rule's removal that also clears its `digest:` entry regenerates the digest correctly.
- Reverse completeness ("every judgment-tier MUST in the set is declared") still rests on the author declaring it; the tool enforces declaration→digest fidelity, not prose→declaration. This is the declared-not-inferred boundary, stated rather than hidden.

## Dependencies
- `claude/spec-spec.md` — owns the digest derivation rule (this sprint extends it).
- `claude/constraints-digest.md` — the artifact being made derivable.
- The zero-dependency CLI skeleton (architecture-spec) — `digest` is another subcommand on it.

## Notes
This is the milestone-closing subcommand. With it, the CLI mechanizes the full backward-verification loop: `map` (coverage), `history` (promotion records), `audit` (liveness), and now `digest` (the constraints summary that can no longer rot). The proof is the same shape as the others — the tool earns its keep on its own repo: after this sprint, editing a governance rule without re-deriving the digest is a fail-closed `digest check`, not a silent dead letter.
