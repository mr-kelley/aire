---
title: aire digest Specification
version: 0.1.0
maintained_by: Aire System Architect (ASA)
domain_tags: [tooling, cli, governance, digest]
status: draft
platform: claude-code
license: Apache-2.0
covers:
  - tools/aire/digest.py
---

# Purpose
Define the `aire digest` subcommand — the CLI surface that makes the constraints digest a **derived artifact that cannot silently fork** from its owning specs. This spec owns the command surface (arguments, dispatch, exit codes), the derivation algorithm, and the canonical output format. The **digest's role in governance, the `digest:` declaration rule, and Rule Ownership are owned by `claude/spec-spec.md`** (Constraints Digest, Derived) and referenced here, never restated. `digest render` (the derived artifact) and `digest check` (the gate) are both covered.

# Scope

## Covers
- `aire digest render`: collecting declared `digest:` clauses and emitting the canonical `claude/constraints-digest.md`.
- `aire digest check`: regenerating and comparing against the committed digest; exit-code semantics.
- The derivation algorithm (which specs are scanned, clause collection, deterministic ordering) and the canonical file format.

## Does Not Cover
- *Why* the digest is derived, the `digest:` declaration requirement, and the authority of owning specs over their clauses — owned by `claude/spec-spec.md` (Constraints Digest, Derived).
- Which rules belong in the digest (a judgment-tier authoring concern: the author declares `digest:` clauses beside the rules they summarize). The tool enforces declaration→digest fidelity, not prose→declaration completeness.

# Derivation (Normative)

## Sources
The deriver scans every `.md` file under `claude/` and `specs/` for a `digest:` block in its YAML front matter — a block-list of clause strings. A spec with no `digest:` block contributes nothing (it is not an error). The constraints-digest file itself is the output target and is never scanned as a source.

A clause is paired with its **owning spec** — the repo-relative path of the file that declared it. This pairing is the Rule Ownership pointer: the digest line points back to where the rule is stated in full.

## Ordering (deterministic)
Clauses are emitted in a stable order: **owning spec path ascending, then declaration order within that spec** (the order the clauses appear in the `digest:` block). No timestamps, hostnames, or run-specific data enter the output — identical canonical state produces byte-identical output (architecture constraint 4).

## Canonical file format
`aire digest render` emits the complete `claude/constraints-digest.md` to stdout — the file is generated in full, not patched. The format is fixed (generic across repos; the per-repo data is only the clauses):

- YAML front matter: `title: Constraints Digest`, a static `maintained_by`, `domain_tags`, `status`, `platform`, `license`, and `generated_by: aire digest` (the marker that this file is derived, not authored). No `version` field — the file is downstream of its owning specs, which carry the versions.
- A heading and a short fixed intro stating the file is a derived artifact: do not edit it; edit the owning specs' `digest:` blocks and regenerate.
- The derived clause list, one line per clause: `- <clause> — `<owning-spec-path>`` (owning spec path in backticks), in the order above.
- A trailing "generated — do not hand-edit" footer.

The front matter, intro, and footer are generic scaffolding owned by the deriver; the clause lines are the only repo-specific content. Because the file carries no timestamp, `render` is deterministic and `check` can compare byte-for-byte.

# Invocation (Normative)

```
aire digest render
aire digest check
```

- `aire digest` with no action: usage to stderr, exit 2.
- Read-only: `digest` performs no writes (it emits to stdout only) and no network, per the architecture constraints. To update the committed digest, redirect `render` over it (`aire digest render > claude/constraints-digest.md`); `check` then verifies they match.

## `digest render`
Emits the complete canonical constraints digest to stdout (the only thing on stdout). The derived artifact — regenerable, never hand-edited.

### Exit codes (render)
- **0**: digest rendered.
- **2**: the digest cannot be derived — an unreadable spec, or a malformed `digest:` block (not a block-list of strings). Fails closed rather than emitting a partial digest.

## `digest check`
Regenerates the canonical digest and compares it to the committed `claude/constraints-digest.md`. The gate for "regenerate, don't patch": a hand-edit, a stale clause, or a governance change that did not re-derive the digest fails here. Suitable for hook gating and CI.

### Exit codes (check)
- **0**: the committed digest equals its regeneration.
- **1**: they differ — the digest is out of date with its owning specs' declarations (a substantive negative). Output names the first divergence (or a compact diff) so the fix is obvious.
- **2**: misconfiguration — the digest file is missing or unreadable, or derivation fails (unreadable spec, malformed `digest:`). Fails closed.

# Relationship to the liveness audit
`digest check` is the stronger, regenerating successor to audit check #3's forward direction (digest agreement). The audit check remains the lighter, always-on signal (every cited spec resolves); `digest check` additionally guarantees the committed digest *equals* its regeneration — that no declared clause is missing and no undeclared line lingers. The reverse-completeness question audit check #3 deferred (every judgment-tier MUST is *declared*) still rests on the author; the tool enforces declaration→digest fidelity.

# Inputs
- Command arguments above.
- `digest:` front-matter blocks across `claude/` and `specs/`.
- The committed `claude/constraints-digest.md` (for `check`).

# Outputs
- `digest render`: the canonical digest on stdout.
- `digest check`: a match/diff verdict on stdout + exit code.
- No writes to the work tree; no network.

# Edge Cases / Fault Handling
- **No `digest:` blocks anywhere**: the digest derives to an empty clause list (scaffolding only). Not an error — a repo may legitimately declare no digest clauses; `check` then requires the committed file to match that empty-list form.
- **Malformed `digest:` block** (not a list, or non-string entries): exit 2 (fail closed); never emit a partial digest.
- **Committed digest missing** (`check`): exit 2 (misconfiguration), distinct from an out-of-date exit 1.
- **Spec header unparseable**: exit 2 with a diagnostic naming the spec — a source the digest depends on cannot be read, so the digest cannot be trusted (fail closed, unlike `map` which skips an unreadable spec's `covers:`; here the digest is the whole artifact, not one contribution among many).
- **Duplicate identical clause from two specs**: both emitted (each with its own owning-spec pointer); ordering keeps the output stable. A clause appearing under the wrong spec is an authoring defect for the judgment walk, not a mechanical error.
- **`aire digest` with no action**: usage to stderr, exit 2.

# Test Strategy
Unit tests (stdlib `unittest`, DEC-000016) in `tests/tools/aire/test_digest.py`, using temporary fixture trees (specs with `digest:` headers + a committed digest file):
- **Render determinism**: `digest render` is byte-identical across repeated runs on a fixed fixture; clauses ordered by spec path then declaration order.
- **Render content**: a clause declared in a spec appears as `- <clause> — `<spec>`` in the output, paired with the declaring spec; a spec without a `digest:` block contributes nothing.
- **Check pass**: when the committed digest equals `render`, `check` exits 0.
- **Check drift**: an added clause, a removed clause, and an edited clause each make `check` exit 1 and name the divergence.
- **Malformed `digest:`** (not a list of strings): both `render` and `check` exit 2 (fail closed).
- **Missing digest file** on `check`: exit 2.
- **Read-only**: `render`/`check` leave the fixture tree unchanged.
- **No action**: `aire digest` with no sub-action exits 2.
Tests follow the spec-to-test mapping in `claude/spec-spec.md`.

# Completion Criteria
- `aire digest render` emits the canonical constraints digest deterministically from declared `digest:` clauses.
- `aire digest check` regenerates and compares against the committed digest, failing closed on misconfiguration and exit 1 on drift.
- All tests pass.
- Demonstrated on this repo: the owning specs declare their `digest:` clauses, `claude/constraints-digest.md` is regenerated from them, and `aire digest check` exits 0 — the digest is now a derived artifact, and the regenerate-not-patch dead-letter is mechanically un-droppable (closes the Aire CLI milestone).

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-06-14 (v0.1.0)
- summary: Initial `aire digest` command spec (DEC-000020, sprint 07). Command surface (render/check, exit codes), the derivation algorithm (scan `digest:` blocks across claude/ and specs/, deterministic spec-path-then-declaration ordering), and the canonical generated-file format; the digest's governance role and the `digest:` declaration rule are deferred to claude/spec-spec.md (Constraints Digest, Derived — Rule Ownership). Closes the Aire CLI milestone.
