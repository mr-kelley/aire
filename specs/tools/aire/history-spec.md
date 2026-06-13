---
title: aire history Specification
version: 0.2.0
maintained_by: Aire System Architect (ASA)
domain_tags: [tooling, cli, history, promotion]
status: draft
platform: claude-code
license: Apache-2.0
covers:
  - tools/aire/history.py
  - tools/aire/history_report.py
---

# Purpose
Define the `aire history` subcommand group — the CLI surface for promotion records. This spec owns the command surface (arguments, dispatch, exit codes); the **record format and report views/semantics are owned by `claude/promotion-record-spec.md`** and referenced here, never restated (Rule Ownership, `claude/spec-spec.md`). `history record` (write side) and `history report` (read side) are both covered.

# Scope

## Covers
- `aire history record`: arguments, slug/commit inference, validation, tag creation, `--dry-run`.
- `aire history report`: arguments, view selection, output streams.
- Exit-code semantics for the command.

## Does Not Cover
- The promotion record payload schema, `-rN` uniqueness rule, report view definitions and recordless-merge classification (owned by `claude/promotion-record-spec.md`).
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

## Exit codes (record)
- **0**: record written (or, with `--dry-run`, previewed).
- **2**: validation failure (bad outcome, PASS without sha/command), indeterminable slug, or a git error. Records are never written on validation failure (fail closed).

# `aire history report` (Normative)

Renders the audited project history from canonical state (`promote/*` tags, first-parent merges into `main`, sprint files, decision events) per the view definitions and recordless-merge classification owned by `claude/promotion-record-spec.md`. **Read-only**: no writes, no network.

## Inputs (arguments)
- *(default, no flag)* — **summary** view: the one-screen, non-technical claim from evidence.
- `--detail` — **detail** view: per-promotion engineering evidence.
- `--chain <slug>` — **chain** view: the full audit chain for one promotion (matched by slug/tag).
- `--json` — machine-readable, deterministic; the only thing on stdout in this mode.
- `--ref <ref>` — the branch/ref to analyze (default `main`, falling back to `HEAD` if `main` is absent).

## Behavior
1. Collect promotion records (parse each `promote/*` tag's JSON payload; resolve the tagged commit).
2. Collect first-parent merges into the ref; classify each as a recorded promotion or a recordless merge (code-changing → finding; docs-only → expected), per promotion-record-spec.
3. Join sprint files (title/goal) and decision events (titles, best-effort) referenced by each record.
4. Render the selected view to stdout; output is deterministic (ordering by tagged-commit committer date, then tag name; canonical dates only).

## Exit codes (report)
- **0**: report rendered, no findings (no code merges lack a record).
- **1**: report rendered, but findings exist (code reached `main` without a record) — a substantive negative, gate-style.
- **2**: tool error (e.g., `--chain` slug not found, not a git repo).

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
Unit tests (stdlib `unittest`, DEC-000016) in `tests/tools/aire/`, using temporary git repositories (init + configured identity + commits + merges + tags):

`test_history.py` (record):
- Slug inference from a `work/<ts>/<slug>` branch.
- `record` creates an annotated tag; its message parses as JSON matching the payload.
- `-rN` uniqueness: a second record of the same slug produces `promote/<slug>-r2`.
- Validation: non-PASS outcome rejected; PASS without command/sha rejected; no tag created on rejection.
- `--dry-run` creates no tag and prints the payload.
- `N/A` outcome (Profile A) is accepted without command/sha.

`test_history_report.py` (report):
- A fixture repo with a recorded promotion, a docs-only recordless merge, and a code-changing recordless merge: summary surfaces the finding for the code merge, not the docs merge; exit 1 when a finding exists, 0 otherwise.
- Detail and chain views include the record's specs, tests, and decisions; `--chain` with an unknown slug exits 2.
- Determinism: `--json` is byte-identical across repeated runs on a fixed fixture.
- Decision-title join degrades to ID-only when the decision log is absent (no failure).
- Read-only: rendering leaves the fixture file tree unchanged.

# Completion Criteria
- `aire history record` writes a spec-conformant promotion record and refuses invalid ones (fail closed).
- `aire history report` renders summary/detail/chain/JSON deterministically from canonical state, read-only, with findings classified per promotion-record-spec.
- All tests pass.
- Both sides demonstrated on this repo: the `promote/aire-cli-bootstrap` record is rendered by `aire history report`.

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-06-13 (v0.2.0)
- summary: Added the `aire history report` command surface (summary/detail/chain/--json/--ref, exit codes) covering tools/aire/history_report.py. View definitions and recordless-merge classification deferred to claude/promotion-record-spec.md v0.3.0 (Rule Ownership).
- time: 2026-06-13 (v0.1.0)
- summary: Initial `aire history` command spec (record side). Command surface only; defers payload schema, -rN rule, and report views to claude/promotion-record-spec.md (Rule Ownership). Validation fails closed; tags are local (push human-only).
