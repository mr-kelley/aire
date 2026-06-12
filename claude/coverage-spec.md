---
title: Coverage Contract Specification
version: 0.1.0
maintained_by: Aire System Architect (ASA)
domain_tags: [system, governance, coverage, mapping, tooling]
status: draft
platform: claude-code
license: Apache-2.0
---

# Purpose
Define how spec coverage is declared, verified, and reported in Aire projects. Every role declares a **coverage model**; a **mapper** conforming to the interface in this spec verifies mechanically that every unit the role produces is governed by a spec. This contract replaces path-mirroring (spec-per-file) as the universal coverage rule: the invariant moves from "paths mirror" (a proxy) to "coverage is total, mechanically verified" (the goal).

This spec also governs the `map` subcommand of the Aire CLI (see DEC-000010): the CLI is the reference implementation of the mapper interface.

# Scope

## Covers
- Coverage models and their semantics (code, artifact, advisory, none).
- The mapper interface: invocation, exit codes, output schema.
- Role binding declarations (how a role selects and configures its coverage model).
- Spec-side coverage declarations (the `covers:` header field).
- The mapper library contribution rule.

## Does Not Cover
- Spec structure and content (owned by `claude/spec-spec.md`).
- Test coverage (owned by spec-spec's Test Strategy requirements; this spec covers *spec* coverage).
- Mapper implementation details (owned by the CLI project's own specs once it exists).

# Coverage Models

Every role MUST declare exactly one coverage model in its role header.

## `code`
Coverage units are public functions, classes, and methods, extracted mechanically (AST, tree-sitter). Every public symbol in the role's declared source paths maps to a spec that claims it. For developer roles producing source code.

## `artifact`
Coverage units are declarative artifacts matching the role's declared globs (e.g., libvirt domain XML, configuration files, generated fragments). Every matching artifact maps to a spec. Mappers MAY additionally compare live system state against the version-controlled artifact (drift detection) where the role's domain supports it.

## `advisory`
Coverage units are structural invariants over documents — joins that must hold (e.g., every inventory service has an owning role; every recommendation spec has a decision entry). The role declares its joins; the mapper checks them. For roles that produce analysis, recommendations, and registries rather than code.

## `none`
No mechanical coverage. MUST be accompanied by a one-line justification in the role header. The liveness audit treats unjustified `none` as a defect.

# Role Binding Declaration

Roles declare their binding in the role spec YAML header:

```yaml
coverage_model: code | artifact | advisory | none
coverage_config:
  paths: [<source roots>]          # code model
  globs: [<artifact patterns>]     # artifact model
  joins: [<invariant names>]       # advisory model
  justification: <one line>        # none model only
```

AireSmith embeds the declaration at generation time, derived from the role's domain.

# Spec-Side Declarations

Specs declare what they cover in their YAML header:

```yaml
covers:
  - src/auth/token.py              # whole file
  - src/auth/token.py:refresh      # specific symbol
  - vms/build-host.xml             # artifact
```

- Intent is **declared, never inferred**: the mapper cross-references two declared sources (spec says "I cover X"; extraction finds X) and never guesses.
- Many-to-one is permitted: a component spec may cover several files. Per-file specs remain valid where complexity warrants.
- `specs/INDEX.md` remains the human-readable overview (per `claude/documentation-spec.md`); the mapper derives the authoritative machine map from `covers:` declarations.

# Mapper Interface (Normative)

Implementations expose two verbs (CLI naming per DEC-000010; behavior is normative, names illustrative until the CLI lands):

**`map check`** — verify coverage. Exit 0 when coverage is total; nonzero otherwise, with uncovered units listed on stdout. Suitable for hook gating (PreToolUse on commit, Stop checks).

**`map report`** — emit the full coverage map: JSON for machines, Markdown for humans. Required fields per unit: identifier, kind, covering spec (or null), staleness indicator (spec older than unit, where derivable).

Rules:
- The map is a **derived artifact**: regenerable at any time from specs + sources, never hand-edited, never required for correctness.
- Output MUST be deterministic: stable ordering (path asc, then symbol asc), no timestamps in the JSON body.
- Mappers read repo state and configuration only; they perform no writes other than the report artifacts and no network access.

# Mapper Library Rule

Mapper engines live in the shared Aire CLI repository, versioned with the tool. A project needing a novel coverage domain builds its mapper **to this contract** and contributes it **into the library** — project-local mapper forks are a governance defect. Roles select and configure engines; they do not author them.

# Inputs
- Role header binding (`coverage_model`, `coverage_config`).
- Spec `covers:` declarations.
- Project sources/artifacts matching the binding.

# Outputs
- `map check`: exit code + uncovered-unit list.
- `map report`: JSON + Markdown coverage map (derived, deterministic).

# Edge Cases / Fault Handling
- **Unit with no covering spec**: listed by `map check`; gates fail closed.
- **Spec claiming a nonexistent unit**: reported as a stale declaration — a spec defect to fix, not silently ignored.
- **Two specs claiming the same unit**: reported as an ownership conflict (violates Rule Ownership, `claude/spec-spec.md`).
- **Binding references missing paths/globs**: configuration error; `map check` fails with a distinct exit code rather than reporting false-complete coverage.
- **Mapper unavailable**: gated operations HALT (fail closed); non-gated work proceeds. The repo must remain readable and workable without the tool.

# Test Strategy
This spec defines testable behavior implemented by the Aire CLI. Tests live in the CLI project per its specs and MUST verify: exit-code semantics for covered/uncovered/misconfigured cases, deterministic output ordering, stale-declaration and ownership-conflict detection, and each engine's extraction correctness against fixture repos (one fixture per coverage model). Until the CLI exists, compliance of role declarations is verified by the liveness audit (DEC-000004) rather than automated tests.

# Completion Criteria
- Roles declare valid bindings; AireSmith generates them.
- Specs carry `covers:` declarations for the units they govern.
- A conforming mapper verifies coverage with deterministic output; relevant tests pass in the CLI project.

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-06-12
- summary: Initial coverage contract per DEC-000006. Replaces universal spec-per-file path-mirroring with declared bindings (code/artifact/advisory/none), spec-side covers: declarations, a normative mapper interface, and the shared-library contribution rule. Ancestor: the CoretexGrid-era AST function-index script.
