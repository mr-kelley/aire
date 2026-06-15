---
sprint: 2
title: aire hook — Layer 2 enforcement primitive (engine + wire + dogfood)
milestone: Harness Enforcement Layer
status: active
---

## Goal
Build the `aire hook` PreToolUse enforcement primitive (Layer 2 of `claude/harness-enforcement-spec.md`): a hook that reads a tool-call event on stdin, evaluates it against the repo's `.aire/config.toml [harness]` typed policy, and allows/blocks fail-closed. **Collapsed scope** (operator decision): this sprint also declares aire's own `[harness]` policy, wires the hook into aire's `.claude/settings.json`, and dogfoods a real block — folding the governing spec's original sprint-3 into this one.

## Deliverables
- `specs/tools/aire/hook-spec.md` (v0.1.0) — implementation spec: command surface, the typed `[harness]` schema (`push_policy`, `protected_paths`), the decision/exit-code protocol, and fail-closed behavior. `covers: tools/aire/hook.py`.
- `tools/aire/hook.py` — the engine: event parsing, typed-constraint evaluation, exit-code protocol (0 allow / 2 block), fail-closed on policy/guard error.
- `hook` wired into the CLI dispatcher (`python3 -m aire hook`).
- `tests/tools/aire/test_hook.py` — unit tests over event fixtures + policy fixtures (push variants, protected-path tools, fail-closed, no-enrollment).
- `.aire/config.toml` — aire's own `[harness]` policy (push_policy human-only; protected_paths for operator.md / private / the hook config).
- `.claude/settings.json` — register `aire hook` as a `PreToolUse` hook.
- **DEC-000024** (private) — hook decision model: typed constraints, exit-code protocol, fail-closed = block-on-guard-error (operator-selected schema; derived fail-closed from the governing spec).
- `specs/INDEX.md`, `STATE.md`, `ROADMAP.md` updates; governing spec scope-list note that sprint 3 folded in.

## Acceptance Criteria
- [ ] `specs/tools/aire/hook-spec.md` conforms to `claude/spec-spec.md` and declares `covers: tools/aire/hook.py`.
- [ ] `aire hook` denies a `git push` Bash event (exit 2) and allows non-push Bash (`git status`, `echo "git push"`) — argv-parsed, not substring-matched.
- [ ] `aire hook` denies a Write/Edit to a protected path (exit 2) and allows writes elsewhere.
- [ ] Fail-closed: malformed `[harness]` policy → block (exit 2) + loud reason; no `[harness]` section → allow (exit 0); valid event for an unrestricted tool → allow (exit 0).
- [ ] Hook wired live in aire's `.claude/settings.json`; **dogfood**: a real protected-path write attempt is blocked in-session (safe sentinel), and a `git push` event is shown denied.
- [ ] Gates green: `aire map` (hook.py covered), `aire audit`, `aire digest check`, `aire doctor`, full test suite.

## Dependencies
- `claude/harness-enforcement-spec.md` v0.1.1 (the governing spec; Layer 2 + policy-as-data + fail-closed).
- DEC-000023 — policy lives in per-repo `.aire/config.toml [harness]` (the file this hook reads).
- The existing CLI dispatcher and `.aire/config.toml` loader.

## Notes
The live dogfood uses a **protected-path sentinel** (gitignored `private/` path) rather than a real `git push`, so a hypothetical hook failure cannot cause an actual push (DEC-000011 is a hard line); push enforcement is proven by unit tests + a piped real-event demonstration. Q2 (hook-integrity), Q4 (Stop-hook), and conditional push classification remain deferred to later sprints.
