---
title: Specification Structure Standard
version: 0.5.0
maintained_by: Aire System Architect (ASA)
domain_tags: [system, governance, specs]
status: draft
platform: claude-code
license: Apache-2.0
digest:
  - "Spec-first: no implementation without a governing spec"
  - "Every rule stated once in its owning spec; pointers elsewhere"
  - "Tests are a completion requirement, never optional"
---

# Purpose
Define the canonical structure, required fields, and behavioral clarity rules for all project specification files. Specs are the primary source of truth for what software should do. Implementation follows specs, not the other way around.

This standard applies to every spec used to design, implement, or validate software in a project governed by the Aire system.

# Scope

## Covers
- Required structure and sections for all spec files.
- Behavioral declaration rules (what must be made explicit).
- Spec-first development principles, including what requires a spec.
- Spec coverage requirements (granularity and declarations; verification owned by `claude/coverage-spec.md`).
- Rule ownership: where governance rules are stated and how they are referenced.

## Does Not Cover
- Content of individual specs (each spec owns its domain).
- Test frameworks or CI tooling (specs define *what* to test, not *how*).
- Role definitions (governed by `claude.role.base.md`).

# Spec-First Development

Specs are written before implementation. This is not a suggestion — it is a structural requirement of the Aire system.

**Why spec-first:**
- Specs force clarity of intent before code is written. Ambiguity surfaces during spec writing, not during debugging.
- Specs make Claude's work auditable. The user can review what Claude intends to build before Claude builds it.
- Specs prevent scope drift. If it's not in the spec, it's not in the implementation.
- Specs survive sessions. Code without a spec relies on conversation history that disappears.

**Rules:**
- Claude MUST NOT begin implementation of a new module, feature, or component without a governing spec.
- If a spec doesn't exist for the target work, Claude MUST create one (or propose one for user review) before writing implementation code.
- Modifying existing behavior requires checking and updating the governing spec first. Code changes that contradict the spec are bugs, not features.
- The user MAY waive spec-first for trivial changes (typo fixes, formatting, one-line bug fixes). Claude should use judgment — if the change affects behavior, it needs a spec.
- If the spec and implementation disagree: the spec is authoritative. Fix the implementation, or update the spec with user approval, then fix the implementation.

**What requires a spec:**
- New modules, features, or components.
- Changes to public interfaces, APIs, or data formats.
- Architectural patterns that affect multiple files.
- Behavior that another developer (or future Claude session) would need to understand.

**What does not require a spec:**
- Trivial fixes (typos, formatting, one-line bug fixes with obvious correctness).
- Test files (they are governed by the spec of the code they test).
- Build configuration and generated code.

**Spec quality:**
- Specs MUST explicitly declare behavioral expectations. Implicit behavior is a defect.
- Specs MUST be clear enough that implementation is mechanical — if the spec is ambiguous, fix the spec before coding.
- Specs MUST stay current. A stale spec is worse than no spec because it misleads.

# Rule Ownership (Single Statement)

Every normative rule in the governance set has exactly one **owning spec** — the document where the rule is stated in full. All other documents (roles, specs, manuals, CLAUDE.md files) reference the owning spec by pointer (e.g., "per `claude/spec-spec.md`") and MUST NOT restate the rule beyond a one-clause summary.

- Duplicate statements of a rule are a governance defect: when two statements drift apart, readers cannot tell which is authoritative.
- If a restatement and its owning spec disagree, the owning spec is authoritative; the restatement is corrected or removed.
- Role generators (AireSmith) MUST produce pointer-style roles: generated roles cite owning specs rather than embedding rule text.
- A compact summary of active constraints (one clause + pointer per rule) is maintained as a session-start digest. It is a **derived artifact**, not an authored one: it is regenerated from owning-spec declarations whenever governance changes (see Constraints Digest below).

# Constraints Digest (Derived)

The constraints digest (`claude/constraints-digest.md`) is the one-line-per-rule, session-start summary of active judgment-tier constraints. It is **derived**, not hand-maintained — a digest that is patched by hand drifts from its owning specs and rots silently (the failure DEC-000003 and the regenerate-not-patch principle exist to prevent).

- **Declared, not inferred.** Each owning spec declares its digest-bound clauses in a `digest:` header field — a YAML block-list of one-clause rule summaries — in the same declared-not-inferred spirit as the `covers:` field. A clause is declared *beside* the rule it summarizes, so editing or removing the rule updates the declaration in the same edit. Rules are never extracted from prose heuristically.
- **Derivation.** The digest is the ordered concatenation of every owning spec's `digest:` clauses, each paired with its owning spec path. Order is deterministic: spec path ascending, then declaration order within a spec.
- **Authority is preserved.** The owning spec remains authoritative for the rule; the `digest:` clause is a downstream summary. A clause that disagrees with the rule it summarizes is a defect in the declaration, corrected at the spec.
- **Mechanically enforced.** `aire digest render` produces the canonical digest; `aire digest check` regenerates and compares against the committed file, failing closed on any mismatch (per `specs/tools/aire/digest-spec.md`). The committed `claude/constraints-digest.md` MUST equal its regeneration. This makes "regenerate, don't patch" a gate rather than a hope.

# Spec-to-Implementation Mapping

Every unit a role produces MUST be covered by a spec. Coverage is declared and mechanically verified per `claude/coverage-spec.md` (the owning spec): roles declare a coverage model (code, artifact, advisory, or justified none); specs declare what they cover via the `covers:` header field; a conforming mapper verifies that coverage is total.

**Granularity** is a project choice: per-file specs (mirroring paths, `-spec.md` suffix — e.g., `src/auth/token.py` → `specs/src/auth/token-spec.md`) remain a good default for complex modules, and component specs covering several related files are equally valid. Many-to-one coverage is permitted; uncovered units are not.

**When coverage doesn't apply:**
- Configuration files, build scripts, and generated code do not require specs.
- Test files do not require their own specs (they are *governed by* the spec of the code they test).
- Specs themselves do not require specs (this document is the meta-spec).

## Spec-to-Test Mapping

Parallel to spec coverage, every spec that defines testable behavior MUST have corresponding tests.

**Mapping convention:**
- Test location: `tests/` directory, mirroring the source path.
- Naming: source filename with a test prefix/suffix per the project's test framework convention.
- Example: `src/auth/token.py` → `tests/auth/test_token.py`

**Rules:**
- The spec's Test Strategy section defines what tests are needed. The test files implement them.
- A spec without tests (when the spec defines testable behavior) is incomplete work — same as code without a spec.
- Tests are written as part of implementation, not after. Spec-first naturally extends to test-first: the spec defines what to test, the tests verify the spec, the implementation satisfies both.

## Spec Index

All projects MUST maintain a spec index at `specs/INDEX.md`. See `claude/documentation-spec.md` for the spec index format and maintenance rules.

The spec index helps Claude locate specs without directory traversal and gives humans an overview of what's been specified.

# Required Sections for All Spec Files

Each spec MUST include the following:

1. **YAML Header**
   Every spec begins with:
   ```yaml
   ---
   title: <spec title>
   version: <semver>
   maintained_by: <owner>
   domain_tags: [<tags>]
   status: draft | stable | deprecated
   platform: claude-code
   license: <license>
   ---
   ```

2. **Purpose**
   Why this spec exists. What it governs. One to three sentences.

3. **Scope**
   What the spec covers and what it explicitly does not cover.

4. **Inputs**
   What the specified artifact expects: arguments, configuration, files, messages, environment.

5. **Outputs**
   What the artifact produces: return values, files, side effects, messages.

6. **Responsibilities**
   Behavioral rules, logic boundaries, and functional scope. This is the core of the spec — what the implementation MUST do.

7. **Edge Cases / Fault Handling**
   Expected behavior under invalid input, timeouts, missing dependencies, and system faults.

8. **Test Strategy**
   What tests are required for this artifact. This is not optional — every implementation spec MUST define its test strategy. Include:
   - What kinds of tests are needed (unit, integration, end-to-end).
   - What behaviors the tests must verify (derived from Responsibilities and Edge Cases).
   - Where the test files live (following the spec-to-test mapping convention below).
   If a spec genuinely requires no tests (e.g., a pure documentation spec), it MUST state "Tests: N/A" with justification. The absence of a Test Strategy section is a spec defect, not a signal that tests are unnecessary.

9. **Completion Criteria**
   The explicit conditions that signal the implementation is done and correct. Completion criteria MUST include "relevant tests pass" unless the spec explicitly declares Tests: N/A.

# Behavioral Declarations

Specs MUST explicitly declare operational behaviors that would otherwise be assumed or guessed. Implicit behavior is a spec defect.

Required declarations (when applicable):
- Serialization formats (JSON, YAML, Markdown, binary).
- Connection and session models.
- Message lifecycle and ordering expectations.
- Retry and timeout behavior.
- Error handling and recovery strategies.
- Runtime configuration (ports, paths, CLI arguments, environment variables).
- Concurrency model (if relevant).

If a required behavior is missing from a spec, Claude MUST flag it and amend the spec before implementing. Guessing critical behaviors is not permitted.

# Optional Sections
- Diagrams or message flow charts.
- References to related specs.
- Links to relevant tests.
- Version history or migration notes.
- Additional metadata in the YAML header.

# Compliance

- Every new or regenerated spec MUST conform to this structure.
- Omissions from the required sections MUST be justified (e.g., "Inputs: N/A — this is a pure output artifact").
- Spec compliance is a gate for implementation: code that lacks a compliant governing spec is incomplete work.

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-06-14 (v0.5.0)
- summary: Implements DEC-000020. Added the Constraints Digest (Derived) section — the digest is a derived artifact, not hand-maintained: owning specs declare digest-bound clauses in a `digest:` header field (declared-not-inferred, like `covers:`); `aire digest render`/`check` regenerate and gate it fail-closed (specs/tools/aire/digest-spec.md). Reworded the Rule Ownership digest bullet to point at the new section. Cures the regenerate-not-patch dead-letter.

- time: 2026-06-12
- summary: Implements DEC-000006. Spec-to-implementation mapping defers to claude/coverage-spec.md: path-mirroring is no longer the universal rule; coverage is declared (role bindings + covers: fields) and mechanically verified, with granularity a per-project choice. Uncovered units remain forbidden.

- time: 2026-06-12
- summary: Implements DEC-000003. Added the Rule Ownership (Single Statement) section — every rule has one owning spec; other documents point, never restate. Absorbed the "what requires a spec" and spec-quality content formerly duplicated in claude.role.base.md (this spec is the owner). Removed Reinforcement restatement blocks.

- source: Adapted from `templates/spec-spec.md` v0.1 (multi-agent, Architect-delegated model)
- time: 2026-03-05
- summary: Adapted for Claude Code single-agent + human model. Added spec-first development principles and rationale. Added spec-to-implementation mapping section. Removed Architect/implementer delegation language. Strengthened behavioral declaration requirements.
