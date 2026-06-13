---
title: aire history Specification
version: 0.1.0
maintained_by: Aire System Architect (ASA)
domain_tags: [tooling, cli, history, promotion]
status: draft
platform: claude-code
license: Apache-2.0
covers:
  - tools/aire/history.py
---

# Purpose
Define the `aire history` subcommand group — the CLI surface for promotion records. This spec owns the command surface (arguments, dispatch, exit codes); the **record format and report views are owned by `claude/promotion-record-spec.md`** and referenced here, never restated (Rule Ownership, `claude/spec-spec.md`). This sprint implements `history record` (the write side); `history report` (the read side) is a later sprint.

# Scope

## Covers
- `aire history record`: arguments, slug/commit inference, validation, tag creation, `--dry-run`.
- Exit-code semantics for the command.

## Does Not Cover
- The promotion record payload schema, `-rN` uniqueness rule, and report views (owned by `claude/promotion-record-spec.md`).
- When a promotion is permitted (owned by `claude/claude.git-hygiene.md`).

# Responsibilities (Normative)

`aire history record` writes a promotion record — an annotated `promote/<slug>` git tag whose message is the JSON payload defined in `claude/promotion-record-spec.md`. It creates a **local tag only**; pushing is human-only (`claude/claude.git-hygiene.md`).

## Inputs (arguments)
- `--slug` — record slug. Default: inferred from the current branch (`work/<ts>/<slug>` → `<slug>`; otherwise the last path segment of the branch name).
- `--commit` — the commit to tag. Default: `HEAD`.
- `--tests-sha` — the exact commit the tests ran against. Default: the resolved `--commit`.
- `--tests-command` — how the tests were invoked.
- `--tests-outcome` — `PASS` (default) or `N/A` (Profile A).
- `--spec` (repeatable) — a governing spec path.
- `--sprint` — the governing sprint file path.
- `--decision` (repeatable) — a decision ID materially touched.
- `--note` — optional one-liner.
- `--dry-run` — print the computed tag name and payload; create nothing.

## Behavior
1. Resolve slug (infer if absent); error if indeterminable.
2. Resolve `--commit` and `--tests-sha` to full SHAs via `git rev-parse`.
3. Build the JSON payload (per promotion-record-spec) and **validate** it:
   - `tests.outcome` ∈ {`PASS`, `N/A`}.
   - If `PASS`: `tests.sha` and `tests.command` MUST be present (an untested or unattributed PASS record is refused — the gate cannot be satisfied by an empty claim).
4. Compute the tag name: `promote/<slug>`, or the next free `-rN` suffix if prior promotions of this slug exist (uniqueness rule owned by promotion-record-spec).
5. Unless `--dry-run`: create the annotated tag on the resolved commit with the JSON payload as its message.

## Exit codes
- **0**: record written (or, with `--dry-run`, previewed).
- **2**: validation failure (bad outcome, PASS without sha/command), indeterminable slug, or a git error. Records are never written on validation failure (fail closed).

# Inputs
- Command arguments above; the git repository in the working directory.

# Outputs
- An annotated `promote/<slug>[-rN]` tag (local), or a dry-run preview on stdout.
- A one-line confirmation (tag name → commit) on stdout.
- No network, no push.

# Edge Cases / Fault Handling
- **Slug indeterminable** (detached HEAD, no branch): exit 2 asking for `--slug`.
- **PASS without sha or command**: exit 2; no tag created.
- **Non-PASS/N-A outcome**: exit 2; no tag created.
- **Tag already exists** for the computed name: the `-rN` rule selects the next free name, so a normal re-run never overwrites an immutable tag.
- **Not a git repo / git failure**: exit 2 with the git error on stderr.
- **`aire history` with no action**: usage message to stderr, exit 2.

# Test Strategy
Unit tests (stdlib `unittest`, DEC-000016) in `tests/tools/aire/test_history.py`, using temporary git repositories (init + configured identity + a commit):
- Slug inference from a `work/<ts>/<slug>` branch.
- `record` creates an annotated tag; its message parses as JSON matching the payload.
- `-rN` uniqueness: a second record of the same slug produces `promote/<slug>-r2`.
- Validation: non-PASS outcome rejected; PASS without command/sha rejected; no tag created on rejection.
- `--dry-run` creates no tag and prints the payload.
- `N/A` outcome (Profile A) is accepted without command/sha.

# Completion Criteria
- `aire history record` writes a spec-conformant promotion record and refuses invalid ones (fail closed).
- All tests pass.
- The capability is demonstrated on this repo (at minimum via `--dry-run`); the first real `promote/*` tag is written by the tool against this sprint's own merge commit.

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-06-13
- summary: Initial `aire history` command spec (record side). Command surface only; defers payload schema, -rN rule, and report views to claude/promotion-record-spec.md (Rule Ownership). Validation fails closed; tags are local (push human-only).
