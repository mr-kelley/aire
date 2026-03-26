---
title: Git Hygiene Strategy (Runner-Managed, Audit-First)
version: 0.1.0
maintained_by: Aire System Architect (ASA)
domain_tags: [system, governance, git, hygiene]
status: draft
license: Apache-2.0
---

# Purpose

Define a consistent, effective, and audit-friendly **git hygiene strategy** for Aire projects.

This strategy is designed for environments where:
- A dedicated orchestration role (e.g., **Runner**) is the only role permitted to execute commands and alter the environment.
- **Remote publishing is a human decision** due to licensing, legal, and collaboration concerns.
- Directives (AI2AI v2.0) are the primary unit of work and auditability.

# Normative References

- `templates/ai2ai-directive-spec-v2.0.md` (AI2AI v2.0 semantics)
- `primitives/relational-primitives.md`

# Scope

## Covers
- Local branching, merging, and commit conventions.
- Directive log file conventions that make repository history searchable and reconstructable.
- Test-stage promotion models (A/B/C) that teams select explicitly.
- Runner responsibilities for committing, merging, and preserving audit trails.

## Does not cover
- Remote publishing policy (explicitly human-only).
- CI vendor configuration, hosted branch protection settings, or platform-specific PR rules.
- Project-specific test definitions (teams define what tests exist; this spec defines how test stages are represented in git).

# Core Invariants (Normative)

1) **Default branch is `main`.**
   - If a repo is initialized with a different default (e.g., `master`), the Runner MUST normalize the local repository to include `main` and treat `main` as the canonical integration branch.

2) **No untested code in `main`.**
   - Teams MUST define a promotion profile (A/B/C) that determines what “tested” means.

3) **Runner never pushes to remote.**
   - Runner MUST NOT execute `git push`, configure remotes, modify remote URLs, authenticate to remotes, or otherwise publish code.
   - Remote publishing is HUMAN-ONLY and case-by-case.

4) **Runner retains all branches indefinitely.**
   - Runner MUST NOT delete branches.

5) **Commit before handoff.**
   - Runner MUST ensure the working tree is clean (all changes committed) before passing control to another role.

6) **No file edited twice before committing.**
   - Runner MUST commit before any file that was modified would be modified again.
   - Exception: none.

7) **Directive files are commit-per-change.**
   - Any change to a directive file (including a single character) MUST be committed before further action.

8) **Every commit includes active directive log file name.**
   - Runner MUST include the active `directive` path in each commit message.

9) **State tracker is commit-per-directive.**
   - Runner MUST update `state/tracker.json` for every directive.
   - Runner MUST commit after directive completion with the updated tracker.

Reinforcement (MUSTs):
- Normalize the local repo to include `main` when the default differs.
- Define exactly one promotion profile to define “tested.”
- Never push to or reconfigure remotes from Runner.
- Never delete branches.
- Keep the working tree clean before handoff.
- Commit before editing a file a second time.
- Commit any directive file change immediately.
- Include the active directive path in every commit message.
- Update `state/tracker.json` per directive and commit on completion.

# Directive Phases (Normative)

This strategy defines two directive phases. Teams MAY add tiers, but MUST keep phase semantics.
Reinforcement: added tiers must preserve the defined phase semantics.
Reinforcement (MAY):
- Teams may add tiers as long as phase semantics are preserved.

## Phase 1 — Work Directive
- Executed on a `work/...` branch.
- Produces implementation artifacts (code/config/docs/policy) as requested.
- Ends when Runner promotes the work branch into the appropriate stage branch (or into `main` for Profile A).

## Phase 2 — Test Directive
- Executed on a `stage/...` branch corresponding to a test tier.
- Produces a test outcome: **PASS** or **FAIL** (or **BLOCKED** if verification cannot run due to missing inputs).
- If **PASS**, Runner promotes to the next stage (or merges to `main`).
- If **FAIL**, Runner emits a *new* Work Directive on a *new* `work/...` branch.

# Promotion Profiles (Normative)

Each team spec MUST explicitly choose exactly one profile for the project/team.
Reinforcement: each team spec picks exactly one promotion profile.

## Profile A — No-Test Promotion (Docs/Policy)
`work/<...>/<slug>` → `main`

## Profile B — Single Test Stage
`work/<...>/<slug>` → `stage/test/<slug>` → `main`

## Profile C — Tiered Test Stages
`work/<...>/<slug>` → `stage/unit/<slug>` → `stage/feature/<slug>` → `stage/e2e/<slug>` → `main`

Notes:
- “unit/feature/e2e” are branch-tier names, not mandates about tooling.
- The team spec defines what verification constitutes PASS at each tier.

# Branch Naming (Normative)

## Work branches
Format:
- `work/<role>/<timestamp>/<slug>`

Requirements:
- `<role>` MUST match the target role receiving/producing the directive.
- `<timestamp>` SHOULD be ISO-like and sortable (e.g., `2025-12-20T213045Z`).
- `<slug>` MUST be stable for the unit of work (human-recognizable identifier).
- *(Developer roles only)* `<slug>` MUST incorporate the project's versioning scheme. For example, if the project uses SemVer and the work targets release 1.3.0: `work/api-implementer/2025-12-20T213045Z/1.3.0-add-auth-flow`. The version component keeps branches sortable by release and makes it immediately clear which version a branch contributes to.
Reinforcement: work branch names always match the role and use a stable slug.
Reinforcement (SHOULD):
- Work branch timestamps are ISO-like and sortable.
Reinforcement (developer roles):
- Work branch slugs incorporate the project version.

## Stage branches
Format:
- `stage/<tier>/<slug>`

The `<slug>` MUST match the corresponding work branch slug (including version component for developer roles).

Where `<tier>` is one of:
- `test` (Profile B)
- `unit`, `feature`, `e2e` (Profile C)

## Main
- `main`

# Directive Log File Layout (Normative)

## Directive files
- `directives/<role>/$(date +%Y%m%d-%H%M%S).md`
  - The filename timestamp MUST be produced by executing the `date` command at directive creation time.
  - Hardcoded dates (including assumed day components) are forbidden.

Rules:
- A directive log is **single-use**.
- The directive log is appended until the directive reaches a terminal state:
  - `PASS`, `FAIL`, or `BLOCKED`.
- The log MUST include entries with:
  - branch name
  - relevant commit SHA(s)
  - outcome
  - verification artifact paths (if any)
  - brief summary of what was attempted
Reinforcement (MUSTs):
- Directive filenames use `date` output at creation time; hardcoded dates are forbidden.
- Directive logs always include branch, SHA, outcome, verification paths, and summary.

## Non-compliant directive handling
If a directive does not conform to AI2AI v2.0 (missing required fields, violates atomicity, etc.):
- Runner MUST keep the same `work/...` branch.
- Runner MUST commit the directive log with a searchable keyword in the commit message:
  - `AIRE_NONCOMPLIANT_DIRECTIVE`
- Runner MUST request correction from the directive authoring role.
Reinforcement: keep the same work branch, commit the noncompliant log, and request correction.

# Commit Policy (Normative)

## Commit message format

`<type>(<role>): <summary> [directive:<path>]`

Where:
- `<type>` ∈ {`feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `policy`}
- `<role>` is the role responsible for the change being committed (often the active worker role, with Runner as committer)

Examples:
- `feat(api-implementer): implement POST /v1/items [directive:directives/api-implementer/2025-12-20T213045Z.md]`
- `test(api-runner): run unit tests PASS [directive:directives/api-runner/2025-12-20T221100Z.md]`
- `policy(api-runner): AIRE_NONCOMPLIANT_DIRECTIVE missing VERIFICATION [directive:directives/api-implementer/2025-12-20T213045Z.md]`

## Commit frequency
- Runner MUST commit:
  - before handing off to another role,
  - after any change to the directive file,
  - before any file would be modified a second time.
Reinforcement: commit before handoff, after directive changes, and before re-editing files.

# Merge & Promotion Rules (Normative)

## General
- Runner MAY use merge commits, fast-forward merges, or squash merges on local branches.
- Teams MAY prefer squash merges into `main` to keep `main` sparse.
Reinforcement (MAY):
- Runner may use merge, fast-forward, or squash merges locally.
- Teams may prefer squash merges into `main`.

## Squash merges (allowed with audit preservation)
- Squash merges into `main` are ALLOWED.
- Because squash merges collapse commit detail on `main`, auditability MUST be preserved on the source branches:
  - Runner MUST retain all branches indefinitely (already required), ensuring the full pre-squash history remains reachable.
Reinforcement: preserve auditability by retaining all branches indefinitely.

## Promotion conditions
A promotion from one branch to the next (work → stage, stage → stage, stage → main) MUST occur only when:
- the relevant Test Directive outcome is **PASS**, and
- the directive log records the terminal PASS state, including the final SHA.
Reinforcement: promote only on PASS with a terminal PASS entry and final SHA.

If FAIL:
- do not promote;
- emit a new Work Directive on a new work branch.

If BLOCKED:
- do not promote;
- wait for clarified inputs.

# Final State Recording (Normative)

For every directive lifecycle, the directive log MUST end with a terminal entry that includes:
- terminal outcome: `PASS` | `FAIL` | `BLOCKED`
- final branch name
- final commit SHA
- verification artifact paths (if applicable)
Reinforcement: every directive log ends with a terminal entry including outcome, branch, SHA, and verification paths.

# PR Policy (Optional)

- PRs MAY be used when collaboration benefits.
- PRs are OPTIONAL and MUST NOT be required for single-team operation.
- If used, PR title/description SHOULD reference the same directive path used in commit messages.
Reinforcement: PRs remain optional and are never required for single-team operation.
Reinforcement (SHOULD):
- PR titles and descriptions reference the directive path when PRs are used.
Reinforcement (MAY):
- PRs may be used when they help collaboration.

# Tags & Releases (Optional)

- Annotated tags MAY be created locally to mark release points.
- Tag messages SHOULD include a brief summary and (when applicable) the directive path for the release candidate.
- Runner MUST NOT push tags to remote.
Reinforcement: tag pushes to remote are forbidden for Runner.
Reinforcement (SHOULD):
- Tag messages include a brief summary and the directive path when applicable.
Reinforcement (MAY):
- Annotated tags may be created locally to mark release points.

# Guardrails (Recommended)

Teams SHOULD adopt guardrails that increase determinism and reduce drift:
- Stable `.gitignore` conventions per language/platform.
- Local checks (lint/test) executed by Runner under explicit directives.
- Append-only directive logs.
Reinforcement (SHOULD):
- Adopt guardrails such as stable `.gitignore`, local checks under directives, and append-only logs.

# Change Control

Regenerate-not-patch. Update version and provenance on every change.

## Provenance
- directive_id: POLICY.DRAFT/git-hygiene
- time: 2025-12-20 (America/Chicago)
- actor_index: aire-rolesmith
- summary: Initial audit-first git hygiene strategy with runner-managed local git, two-phase directives, explicit promotion profiles A/B/C, branch retention, and commit-per-handoff directive log indexing.
