---
title: Git Hygiene Strategy (Codex, Audit-First)
version: 0.1.0
maintained_by: Aire System Architect (ASA)
domain_tags: [system, governance, git, hygiene]
status: draft
platform: codex
license: Apache-2.0
---

# Purpose

Define a consistent, effective, and audit-friendly **git hygiene strategy** for Aire projects operated by Codex.

This strategy is designed for environments where:
- **Codex** is a single-agent executor with filesystem and git access inside a sandboxed container.
- **Remote publishing is a human decision** due to licensing, legal, and collaboration concerns.
- Tasks (user requests) are the primary unit of work and auditability.

# Normative References

- `codex/decision-log-spec.md`
- `codex/codex.role.base.md`

# Scope

## Covers
- Local branching, merging, and commit conventions.
- Task-based commit traceability.
- Test-stage promotion models (A/B) that projects select explicitly.
- Codex responsibilities for committing, merging, and preserving audit trails.

## Does Not Cover
- Remote publishing policy (explicitly human-only).
- CI vendor configuration, hosted branch protection settings, or platform-specific PR rules.
- Project-specific test definitions (projects define what tests exist; this spec defines how test stages are represented in git).

# Core Invariants (Normative)

1) **Default branch is `main`.**
   - If a repo is initialized with a different default (e.g., `master`), Codex MUST rename it to `main` immediately, before any other work begins. There is no `master` branch — only `main`.

2) **No untested code in `main`.**
   - Projects MUST define a promotion profile (A/B) that determines what "tested" means.
   - For profile B: tests MUST exist and MUST pass before promotion. "Tests not written yet" is not a valid promotion state — it means the work is not done.
   - Profile A (docs/policy) is the only profile where untested promotion is permitted.

3) **Codex never pushes to remote.**
   - Codex MUST NOT execute `git push`, configure remotes, modify remote URLs, authenticate to remotes, or otherwise publish code.
   - Remote publishing is HUMAN-ONLY and case-by-case.

4) **Branch retention.**
   - Codex MUST NOT delete branches unless the user explicitly requests it.

5) **Commit before switching tasks.**
   - Codex MUST ensure the working tree is clean (all changes committed) before starting a different task.

6) **No file edited twice before committing.**
   - Codex MUST commit before any file that was modified would be modified again in a separate logical change.
   - Exception: iterative edits within the same atomic task (e.g., successive refinements to the same function) are permitted as a single commit.

Reinforcement (MUSTs):
- Normalize the local repo to include `main` when the default differs.
- Define exactly one promotion profile to define "tested."
- Tests must exist and pass before promotion (profile B).
- Never push to or reconfigure remotes.
- Never delete branches unless the user explicitly requests it.
- Keep the working tree clean before switching tasks.
- Commit before re-editing a file in a separate logical change.

# Promotion Profiles (Normative)

Each project MUST explicitly choose exactly one profile.
Reinforcement: each project picks exactly one promotion profile.

## Profile A — No-Test Promotion (Docs/Policy)
`work/<slug>` → `main`

For projects or changes that are purely documentation, governance, or policy. No tests required for promotion.

## Profile B — Tested Promotion (Default for Software)
`work/<slug>` → `stage/test/<slug>` → `main`

The default for any project with testable code. All tests — unit, integration, e2e, whatever the governing spec's Test Strategy requires — run before promotion from `stage/test` to `main`.

Test categorization (unit vs. integration vs. e2e) is defined in specs and organized in test files, not in branch topology. One stage branch runs all required tests. This keeps branching simple while the spec-spec Test Strategy section ensures thorough coverage.

**Sprint-to-branch mapping:** Each sprint maps 1:1 to a work branch. One sprint, one `work/<timestamp>/<slug>` branch, one promotion path through `stage/test/<slug>` to `main`. Codex MUST NOT mix work from multiple sprints on a single branch, and MUST NOT split a single sprint across multiple work branches.

**Promotion flow:**
1. Create `work/<timestamp>/<slug>` when the sprint starts.
2. Develop on the work branch (atomic commits as work progresses).
3. When implementation and tests are complete, merge to `stage/test/<slug>`.
4. Run all tests required by governing specs on the stage branch.
5. If PASS: merge to `main`.
6. If FAIL: fix on the work branch, re-promote to `stage/test/<slug>`, re-test.

Notes:
- The project defines what verification constitutes PASS.
- "All tests pass" means all tests required by the governing specs, not just tests that happen to exist.

# Branch Naming (Normative)

## Work branches
Format:
- `work/<timestamp>/<slug>`

Requirements:
- `<timestamp>` SHOULD be ISO-like and sortable (e.g., `2025-12-20T213045Z`).
- `<slug>` MUST be a stable, human-recognizable identifier for the unit of work.
Reinforcement: work branch names use a stable slug.
Reinforcement (SHOULD):
- Work branch timestamps are ISO-like and sortable.

## Stage branches
Format:
- `stage/test/<slug>`

## Main
- `main`

# Commit Policy (Normative)

## Commit message format

`<type>(<scope>): <summary>`

Where:
- `<type>` ∈ {`feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `policy`}
- `<scope>` is the module, component, or area affected

Examples:
- `feat(api): implement POST /v1/items`
- `test(api): add unit tests for POST /v1/items`
- `fix(auth): correct token expiry check`
- `docs(readme): update installation instructions`

## Decision ID references
When a commit implements or relates to a logged decision, the commit message body SHOULD reference the decision ID:
- `Implements DEC-000123`
- `Related: DEC-000045`

## Commit frequency
- Codex MUST commit:
  - before switching to a different task,
  - before any file would be modified a second time in a separate logical change.
- Codex SHOULD make atomic, meaningful commits — one logical change per commit.
Reinforcement: commit before task switches and before re-editing files in separate changes.

# Merge & Promotion Rules (Normative)

## General
- Codex MAY use merge commits, fast-forward merges, or squash merges on local branches.
- Projects MAY prefer squash merges into `main` to keep `main` history sparse.
Reinforcement (MAY):
- Codex may use merge, fast-forward, or squash merges locally.
- Projects may prefer squash merges into `main`.

## Squash merges (allowed with audit preservation)
- Squash merges into `main` are ALLOWED.
- Because squash merges collapse commit detail on `main`, auditability MUST be preserved on the source branches:
  - Codex MUST retain all branches (already required), ensuring the full pre-squash history remains reachable.
Reinforcement: preserve auditability by retaining all branches.

## Promotion conditions
A promotion from one branch to the next (work → stage, stage → stage, stage → main) MUST occur only when:
- tests exist for all testable deliverables (per the governing spec's Test Strategy section),
- the relevant test outcome is **PASS**, and
- the outcome is recorded (in commit message or decision log) including the final SHA.

There is no "promote now, test later" path. If tests are missing, the work is incomplete and MUST NOT be promoted.

Reinforcement: promote only when tests exist, tests PASS, and the outcome is recorded with the final SHA.

If FAIL:
- do not promote;
- fix on the work branch or create a new work branch.

If BLOCKED:
- do not promote;
- wait for clarified inputs from the user.

# PR Policy (Optional)

- PRs MAY be used when collaboration benefits.
- PRs are OPTIONAL and MUST NOT be required for single-developer operation.
- If used, PR title/description SHOULD reference relevant decision IDs and task context.
Reinforcement: PRs remain optional and are never required for solo operation.
Reinforcement (SHOULD):
- PR titles and descriptions reference decision IDs when PRs are used.
Reinforcement (MAY):
- PRs may be used when they help collaboration.

# Tags & Releases (Optional)

- Annotated tags MAY be created locally to mark release points.
- Tag messages SHOULD include a brief summary and relevant decision IDs.
- Codex MUST NOT push tags to remote.
Reinforcement: tag pushes to remote are forbidden for Codex.
Reinforcement (SHOULD):
- Tag messages include a brief summary and decision IDs when applicable.
Reinforcement (MAY):
- Annotated tags may be created locally to mark release points.

# Guardrails (Recommended)

Projects SHOULD adopt guardrails that increase determinism and reduce drift:
- Stable `.gitignore` conventions per language/platform.
- Local checks (lint/test) executed under explicit user request.
- Meaningful commit messages that enable `git log` archaeology.
Reinforcement (SHOULD):
- Adopt guardrails such as stable `.gitignore`, local checks, and meaningful commit messages.

# Change Control

Regenerate-not-patch. Update version and provenance on every change.

## Provenance
- source: Adapted from `claude/claude.git-hygiene.md` v0.2.0
- time: 2026-03-21
- actor_index: aire-system
- summary: Git hygiene strategy adapted for Codex single-agent execution. Replaced Claude Code references with Codex throughout. Preserved all core invariants, promotion profiles, branch naming, commit policy, and human-only remote publishing.
