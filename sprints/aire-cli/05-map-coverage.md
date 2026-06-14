---
sprint: 5
title: aire map — mechanical spec coverage
milestone: Aire CLI
status: completed
---

## Completion
Merged via PR #18 (merge commit `8cc50e2`). Promotion record `promote/aire-map-coverage` → `8cc50e2` written by `aire history record` against the merge commit (56 tests re-verified green there; `map check` exits 0, 46/46 units). `aire history report` now shows 3 tested promotions, 0 findings. Closeout folded into the opening commit of the aire-audit sprint — second exercise of the DEC-000018 provisional convention (the first, sprint 03, folded; sprint 04 bundled).

## Goal
Implement `aire map` — the coverage mapper (NORTHSTAR success criterion 4). It verifies mechanically that every unit a repo produces is governed by a spec, replacing path-mirroring with declared-and-checked coverage. Dogfooded on aire itself: with the CLI source as the code domain, `map check` must prove every `tools/aire/` public symbol is claimed by a `specs/tools/aire/*.md` spec.

This sprint also resolves the milestone-deferred question — *where does a role-less repo's coverage binding live?* (DEC-000019).

## Deliverables
- **DEC-000019** — role-less repos declare bindings in `.aire/config.toml` `[[coverage]]`; resolution order role-headers-first, config-second.
- `claude/coverage-spec.md` v0.2.0 — Repo-Level Binding subsection + normative resolution order.
- `specs/tools/aire/map-spec.md` v0.1.0 — `map check`/`report` command surface and the `code` engine's extraction + cross-reference rules (coverage semantics deferred to coverage-spec, Rule Ownership).
- `tools/aire/map.py` — the `code` engine: AST symbol extraction, `covers:` cross-reference, uncovered/stale/conflict classification, `check` (gate) + `report` (Markdown/JSON, deterministic, best-effort staleness).
- `tools/aire/config.py` — `[[coverage]]` binding loader (`CoverageBinding`).
- `tools/aire/cli.py` — `map` dispatch; `specs/tools/aire/architecture-spec.md` v0.1.2 (dispatch + config note).
- `.aire/config.toml` — one `code` binding over `tools/aire/`.
- `tests/tools/aire/test_map.py` — extraction, whole-file/symbol coverage, stale, conflict, misconfiguration (fail-closed), determinism, read-only.

## Acceptance Criteria
- [x] `aire map check` verifies coverage from declared bindings + `covers:` declarations; fails closed (exit 2) on misconfiguration; exit 1 on findings.
- [x] `aire map report` emits a deterministic Markdown/JSON map (path-then-symbol order, no timestamps in the body).
- [x] The `code` engine extracts public functions/classes/methods via AST; private/dunder excluded; no-symbol files trivially covered.
- [x] Tests pass on the work branch tip (56 green: 38 prior + 18 new).
- [x] **Dogfood:** `map check` on aire exits 0 — 46/46 `tools/aire/` units covered by `specs/tools/aire/` specs. NORTHSTAR criterion 4 satisfied on aire itself.
- [ ] Promoted to `main` with a tested promotion record (post-merge, Profile B).

## Engine Scope
v0.1 implements the **`code`** engine only — the one aire needs. `artifact` and `advisory` are deferred contributions *into the shared library* (coverage-spec Mapper Library Rule), added when a governed repo first needs them; until then they fail closed (exit 2), never falsely report complete. Role-header binding discovery is likewise deferred — no role-bearing repo uses the CLI yet, so today bindings come from `.aire/config.toml` (DEC-000019); when a role-bearing repo adopts the CLI, role resolution is layered ahead of the config source per the coverage-spec order.

## Dependencies
- `claude/coverage-spec.md` — the contract this implements (the mapper interface).
- The zero-dependency CLI skeleton (architecture-spec) — `map` is another subcommand on it.

## Notes
The first finding the tool surfaced on its own source was a *staleness* signal: editing `cli.py`'s dispatch without touching `architecture-spec.md` (which owns dispatch) flagged the spec as older than the code — cleared by updating the spec in the same commit. The mapper earning its keep on its own author is the intended proof.
