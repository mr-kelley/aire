---
title: Git Hygiene Strategy (Claude Code, Audit-First)
version: 0.4.1
maintained_by: Aire System Architect (ASA)
domain_tags: [system, governance, git, hygiene]
status: draft
platform: claude-code
license: Apache-2.0
---

# Purpose

Define a consistent, effective, and audit-friendly **git hygiene strategy** for Aire projects operated by Claude Code.

This strategy is designed for environments where:
- **Claude Code** is a single-agent executor with direct filesystem and git access.
- **Remote publishing is a human decision** due to licensing, legal, and collaboration concerns.
- Tasks (user requests) are the primary unit of work and auditability.

# Normative References

- `claude/decision-log-spec.md`
- `claude/claude.role.base.md`

# Scope

## Covers
- Local branching, merging, and commit conventions.
- Task-based commit traceability.
- Promotion profiles (A/B) that projects select explicitly.
- Claude Code responsibilities for committing, merging, and preserving audit trails.

## Does Not Cover
- Remote publishing policy (explicitly human-only).
- CI vendor configuration, hosted branch protection settings, or platform-specific PR rules.
- Project-specific test definitions (projects define what tests exist; this spec defines how tested promotion is represented in git).

# Core Invariants (Normative)

1) **Default branch is `main`.**
   - If a repo is initialized with a different default (e.g., `master`), Claude Code MUST rename it to `main` immediately, before any other work begins. There is no `master` branch — only `main`.

2) **No untested code in `main`.**
   - Projects MUST define a promotion profile (A/B) that determines what "tested" means.
   - For Profile B: tests MUST exist and MUST pass before promotion. "Tests not written yet" is not a valid promotion state — it means the work is not done.
   - Profile A (docs/policy) is the only profile where untested promotion is permitted.

3) **Claude Code never pushes to remote.**
   - Claude Code MUST NOT execute `git push`, configure remotes, modify remote URLs, authenticate to remotes, or otherwise publish code.
   - Remote publishing is HUMAN-ONLY and case-by-case.

4) **Branch retention.**
   - Claude Code MUST NOT delete branches unless the user explicitly requests it.

5) **Commit before switching tasks.**
   - Claude Code MUST ensure the working tree is clean (all changes committed) before starting a different task.

6) **No file edited twice before committing.**
   - Claude Code MUST commit before any file that was modified would be modified again in a separate logical change.
   - Exception: iterative edits within the same atomic task (e.g., successive refinements to the same function) are permitted as a single commit.

# Promotion Profiles (Normative)

Each project MUST explicitly choose exactly one profile.

## Profile A — No-Test Promotion (Docs/Policy)
`work/<slug>` → `main`

For projects or changes that are purely documentation, governance, or policy. No tests required for promotion.

## Profile B — Tested Promotion (Default for Software)
`work/<slug>` → `main`, gated by a recorded test PASS against the exact SHA being merged.

The default for any project with testable code. All tests — unit, integration, e2e, whatever the governing spec's Test Strategy requires — run on the work branch tip before promotion to `main`.

Test categorization (unit vs. integration vs. e2e) is defined in specs and organized in test files, not in branch topology. This keeps branching simple while the spec-spec Test Strategy section ensures thorough coverage.

**Sprint-to-branch mapping:** Each sprint maps 1:1 to a work branch. One sprint, one `work/<timestamp>/<slug>` branch, one promotion to `main`. Claude MUST NOT mix work from multiple sprints on a single branch, and MUST NOT split a single sprint across multiple work branches.

**Promotion flow:**
1. Create `work/<timestamp>/<slug>` when the sprint starts.
2. Develop on the work branch (atomic commits as work progresses).
3. When implementation and tests are complete, run all tests required by the governing specs on the work branch tip.
4. If PASS: merge to `main` and write the promotion record (below).
5. If FAIL: fix on the work branch, re-run; do not promote until PASS.

**Promotion record:** every Profile B promotion to `main` MUST be recorded as an annotated tag `promote/<slug>` on the merge commit. The tag message records, at minimum: the sprint reference, the governing spec(s), the test outcome with the exact SHA the tests ran against, and related decision IDs. Promotion records are the auditable evidence that nothing reached `main` untested; a project history report can be generated from them at any time.

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
- *(Developer roles only)* `<slug>` MUST incorporate the project's versioning scheme (as defined in the role's normative requirements). For example, if the project uses SemVer and the work targets release 1.3.0, the slug should reflect that: `work/2025-12-20T213045Z/1.3.0-add-auth-flow`. The version component keeps branches sortable by release and makes it immediately clear which version a branch contributes to.

## Promotion tags
Format:
- `promote/<slug>`

The `<slug>` MUST match the corresponding work branch slug (including version component for developer roles).

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
- Claude Code MUST commit:
  - before switching to a different task,
  - before any file would be modified a second time in a separate logical change.
- Claude Code SHOULD make atomic, meaningful commits — one logical change per commit.

# Merge & Promotion Rules (Normative)

## General
- Claude Code MAY use merge commits, fast-forward merges, or squash merges on local branches.
- Projects MAY prefer squash merges into `main` to keep `main` history sparse.

## Squash merges (allowed with audit preservation)
- Squash merges into `main` are ALLOWED.
- Because squash merges collapse commit detail on `main`, auditability MUST be preserved on the source branches:
  - Claude Code MUST retain all branches (already required), ensuring the full pre-squash history remains reachable.

## Promotion conditions
A promotion from a work branch to `main` MUST occur only when:
- tests exist for all testable deliverables (per the governing spec's Test Strategy section),
- the relevant test outcome is **PASS**, and
- the outcome is recorded in the promotion record (annotated `promote/<slug>` tag) including the exact SHA tested.

There is no "promote now, test later" path. If tests are missing, the work is incomplete and MUST NOT be promoted.

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
- Pushing remains human-only in all cases (Core Invariant 3). On a branch the user has already pushed, Claude Code MAY create a PR only when the user explicitly authorizes it for that specific PR; standing authorization is never assumed. (Per DEC-000011.)

# Promotion Gate (CI Enforcement)

The promotion conditions above ("promote only when tests PASS and the outcome is recorded") are enforced by **machinery, not discipline**, via a CI status check. Because the merge to `main` happens on the hosting platform (a PR merge), the enforcing check is server-side (GitHub Actions, or Forgejo Actions for lab-only repos) — not a local hook, which cannot intercept a platform-side merge.

The gate has **two triggers**, because record-existence cannot be checked before the merge commit it tags exists:

1. **On pull request → prevention.** Run the project's test suite (and `aire doctor`). The check is made **required** via branch protection, so code that fails tests cannot merge. This is the strong gate: no untested code reaches `main`.
2. **On push to `main` → detection.** Run `aire history report`; its nonzero exit on a recordless code merge (a *finding*) fails the job, surfacing any process slip immediately after it lands.

The promotion record itself remains the post-merge step (it annotates the merge commit). Prevention stops untested code; detection catches recordless code at once. Together they satisfy the promotion conditions mechanically.

**Promotion records MUST be pushed to the remote.** The detection job runs on the CI runner, which sees only the *remote* view. A promotion record tag that exists locally but was not pushed is invisible to the gate — so the just-merged code reads as recordless and detection goes red. Consequently, after a code merge, `main`'s detection check sits red in the window between the merge and pushing the record (`git push origin promote/<slug>` — human-only). This is intended: the red is the reminder that the promotion is not complete until its record is public. Push the record to clear it.

**Portability.** The gate is authored as a platform-Actions workflow and depends only on the zero-dependency `aire` CLI (no packages to fetch), so the *same* workflow runs on public GitHub and on a private Forgejo instance with a self-hosted runner — serving both published repos and repos that never leave the lab.

# Tags & Releases (Optional)

- Annotated tags MAY be created locally to mark release points.
- Tag messages SHOULD include a brief summary and relevant decision IDs.
- Claude Code MUST NOT push tags to remote.

# Guardrails (Recommended)

Projects SHOULD adopt guardrails that increase determinism and reduce drift:
- Stable `.gitignore` conventions per language/platform.
- Local checks (lint/test) executed under explicit user request.
- Meaningful commit messages that enable `git log` archaeology.

# Change Control

Update version and provenance on every change.

## Provenance
- time: 2026-06-13 (v0.4.1)
- summary: Added the record-push requirement to the Promotion Gate section — the lesson from the gate's first live run: promotion record tags must be pushed for the CI detection (which sees only the remote) to clear; main's detection sits red between a code merge and pushing its record, by design.
- time: 2026-06-13 (v0.4.0)
- summary: Added the Promotion Gate (CI Enforcement) section — promotion conditions enforced server-side via a CI status check (GitHub/Forgejo Actions); two triggers (PR = tests required, push-to-main = findings detection); platform-portable via the zero-dependency CLI. Completes the enforcement half of Gate-Enforced Promotion (sprint 04).

- time: 2026-06-12
- summary: Implements DEC-000003 (Reinforcement blocks removed; rules stated once) and codifies the DEC-000011 ruling: PR creation on an already-pushed branch is permitted with explicit per-case user authorization; pushing remains human-only.

- time: 2026-06-12
- summary: Implements DEC-000002 and DEC-000007. Removed Profile C residue (A/B/C → A/B). Collapsed the stage/test branch layer: Profile B now promotes work → main directly, gated by a recorded test PASS against the exact merged SHA, with promotion evidence captured in annotated `promote/<slug>` tags. Promotion records replace branch topology as the audit mechanism.

- source: Adapted from `templates/team.git-hygiene.md` v0.1.0
- time: 2026-03-04
- actor_index: aire-system
- summary: Git hygiene strategy adapted for Claude Code single-agent execution. Removed Runner intermediary, directive log references, and role-based branch paths. Simplified promotion profiles from A/B/C to A/B — test categorization lives in specs, not branch topology. Preserved commit conventions, branch retention, and human-only remote publishing. Fixed normative references to claude/ paths.
