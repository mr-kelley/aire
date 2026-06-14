---
title: Harness Enforcement Specification
version: 0.1.0
maintained_by: Aire System Architect (ASA)
domain_tags: [system, governance, enforcement, hooks]
status: draft
platform: claude-code
license: Apache-2.0
---

# Purpose
Define how the project's **hard constraints** (push policy, protected-path writes, commit format, working-tree/state freshness, and similar non-negotiables) are enforced **deterministically** — through tool/environment configuration, permission rules, and hooks consuming committed policy data — rather than by prose instructions that a session can drift past under context pressure. This spec owns the *enforcement model*; the owning spec of each rule continues to own the rule's *intent* (per `claude/spec-spec.md`, Rule Ownership). It formalizes DEC-000001 (layered harness enforcement) and incorporates the 2026-06-14 empirical finding that PreToolUse hooks block under bypass mode.

# Scope

## Covers
- The enforcement model: a local ladder (Layers 0–3) plus the off-box server-side gate.
- Classification of each hard constraint by the **weakest run mode it must survive** and placement at the lowest layer that can both express it and survive that mode.
- The **policy-as-data** convention: enforcement *logic* is tested code, project policy is committed data, and one source feeds both enforcement (the hook/permission config) and verification (`aire audit`).
- The verification contract: how `aire audit` confirms a repo's declared policy is actually wired in.

## Does Not Cover
- The concrete file format and code of the enforcing artifacts. The `aire hook` handler, the audit check, and any config generator are governed by their own implementation specs under `specs/tools/aire/` (forthcoming sprints).
- The intent/wording of individual constraints (owned by their specs — e.g., the push rule is `claude/claude.git-hygiene.md`; this spec does not restate it).
- OS-level sandboxing / containment of the host. That protects a different blast radius (the machine) and is an operator/environment concern, complementary to but outside this spec.
- Cross-platform (Codex) parity of the hook mechanism (deferred to the Cross-Platform Parity milestone).

# The Enforcement Model

## Threat model (what this enforces against)
The model assumed is a **cooperative agent degrading under context pressure, not an adversary**. Enforcement here is *mistake-proofing* — it stops a forbidden action a well-intentioned but context-degraded session would otherwise take. It is **not** a security sandbox against a determined adversarial process. Adversarial containment (OS sandbox, egress control) and the off-box gate cover the residual; they are out of scope here but named so the boundary is explicit.

## Local enforcement ladder
Each hard constraint is pushed to the **lowest layer that can express it**:

- **Layer 0 — Tool / environment.** Enforcement outside the agent's tool surface entirely: git remote push-URL disabling (`git remote set-url --push … DISABLED`), branch protection, filesystem permissions. Cannot be reached by any in-session action, so it survives every run mode.
- **Layer 1 — Permission rules.** Static `allow`/`deny`/`ask` rules in `.claude/settings.json`. Deterministic in normal (prompted) mode; expresses unconditional prohibitions and allowances cleanly. Does **not** survive bypass mode (see below).
- **Layer 2 — Hooks + policy data.** `PreToolUse`/`Stop` hooks (tested code) that read committed **policy-as-data** files and return allow / block (exit 2) / ask. Expresses *conditional* rules that Layer 1's prefix matching cannot (e.g. "push allowed to private remotes, denied to public, ask if unclassified"). **Survives bypass mode** (empirically verified).
- **Layer 3 — Prose.** Natural-language rules in specs/roles. Reserved for **judgment calls only** — anything a small script can check does not belong here.

## The off-box backstop
Independent of the local ladder, the **server-side promotion gate** (CI/Forgejo; the Gate-Enforced Promotion milestone) protects **canonical history**: nothing reaches `main` without a tested promotion record, regardless of what happened in any working tree. The ladder protects *the session and working tree*; the gate protects *the canonical branch*. Two blast radii, two mechanisms — the pairing is what makes the model robust.

## Bypass-mode survivability
The layers are **not equal** under `--dangerously-skip-permissions` (bypass mode), which many sessions run in. Verified empirically 2026-06-14 (control + bypass + positive-control runs; a `PreToolUse` hook exiting 2 stopped the tool call identically with and without the flag):

| Layer | Survives bypass mode? | Role |
|---|---|---|
| 0 — tool/environment | **Yes** — outside the tool surface | Hard guard for what it can express |
| 1 — permission rules | **No** — bypass skips permission evaluation | Reliable only in normal (prompted) mode |
| 2 — hooks + policy data | **Yes** — hook exit-2 stops the call *before* permission rules are evaluated | Deterministic guard, even in bypass |
| 3 — prose | **No** | Judgment calls only |
| Off-box gate | **Yes** — runs off-box, after the fact | Backstop for canonical history |

The load-bearing correction to the pre-spec design input: **Layer 2 is a real deterministic guard, not an audit-only layer.** A constraint that must hold under bypass mode can be enforced by a hook; it does not require Layer 0 or the gate, though those remain available for what they uniquely cover.

## Placement rule
For each hard constraint:
1. Determine the **weakest run mode it must survive** (normal-only, or must-hold-under-bypass).
2. Place it at the **lowest layer that both expresses it and survives that mode.** A constraint that must survive bypass MUST NOT rely solely on Layer 1 or Layer 3.
3. Use Layer 3 (prose) only when no lower layer can mechanically check the constraint (genuine judgment).

# Policy as Data
Enforcement separates **logic** (code) from **policy** (data):

- **Logic is code, tested.** The hook handlers and audit checks are implementation code with tests, governed by their own specs.
- **Policy is committed data.** What a repo enforces — push posture / remote classification, protected paths, commit-format rule, etc. — lives in committed, diffable, machine-readable policy files. Changing policy is a one-line data diff, not a code or spec edit.
- **One source, two consumers (declare once, derive).** The same committed policy feeds **enforcement** (the hook/permission config that blocks) and **verification** (`aire audit`, which confirms the declared policy is actually wired in). This is the coverage/digest declare-once-derive pattern (DEC-000019/DEC-000020) extended to enforcement: policy is declared once and both the enforcer and the auditor derive from it.

The concrete file layout (a single `.aire/config.toml` section vs per-domain files such as `.claude/remote-policy.json`) is **deferred to the implementation spec** — see Open Design Questions.

# Inputs
- **Committed policy-data file(s)** declaring the repo's hard constraints (format owned by the implementation spec).
- **`.claude/settings.json`** — Layer 1 permission rules and Layer 2 hook registration.
- **Git remote configuration** — for Layer 0 push-URL classification.
- **The governance spec set** — each hard constraint's intent statement, owned by its spec; this spec enforces, it does not author the rules.

# Outputs
- **Tool-call enforcement decisions** at session time: allow / block (hook exit 2) / ask, emitted by Layer 1 rules and Layer 2 hooks.
- **Audit results**: `aire audit` reports whether each declared constraint's enforcing artifact is present and wired in (verify half of declare-once-derive).
- **Derived enforcement config** (optional, if a generator is later added): settings/permission fragments derived from the policy source rather than hand-written.

# Responsibilities
The enforcement system MUST:

- Enforce each hard constraint at the **lowest layer that expresses it and survives the weakest mode it must operate in** (Placement rule). A bypass-surviving constraint MUST NOT rely solely on Layer 1 or Layer 3.
- Keep **logic and policy separate**: enforcement logic is tested code; per-repo policy is committed data consumed by that code.
- Derive **both enforcement and verification from one declared policy source** — no second, hand-maintained copy of what is enforced.
- **Fail closed.** On malformed, missing, or unreadable policy, or on hook error, the hook MUST block or ask — never silently allow. (Consistent with the gates-fail-closed constraint, `claude/audit-spec.md`.)
- Fall back to **`ask`** (human prompt) for any case the policy does not classify (e.g. an unrecognized remote) — never a silent allow.
- **Not restate rule intent.** Owning specs keep the rule (Rule Ownership, single statement); this spec and the policy data carry enforcement, citing the owning spec. No rule text is duplicated.
- Treat the **off-box gate as the canonical-history backstop**; local enforcement never substitutes for it.
- Reserve **Layer 3 (prose) for judgment calls** only.

# Edge Cases / Fault Handling
- **Malformed / missing policy file** → hook fails closed (block or ask); `aire audit` flags the repo as declared-but-unenforceable.
- **Bypass mode active** → Layers 1 and 3 are inert; Layers 0 and 2 and the gate still hold. Any constraint that must survive bypass is, by the placement rule, already at Layer 0/2 or the gate.
- **Hook-config integrity (who-guards-the-guards)** → the hook scripts, `.claude/settings.json`, and policy files SHOULD themselves be protected paths so a session's attempt to disable enforcement is itself blocked. Within the cooperative threat model this is sufficient mistake-proofing; it is **not** an adversarial guarantee (a determined process can defeat its own guard) — that residual is covered by containment and the off-box gate, not by this layer.
- **Tool paths a hook does not match** (e.g. an action routed through a subcommand the matcher misses) → acknowledged coverage gap; structural layers cover the critical cases (Layer 0 push-URL disabling makes "never push to public" hold regardless of command shape; the gate makes "no untested code on main" hold regardless of the working tree).
- **Unclassified conditional case** (e.g. a remote absent from the remote policy) → `ask`, never silent allow.

# Verification
Conformance is mechanically verified by **`aire audit`** (extending the DEC-000004 liveness checks):

- For each hard constraint a repo **declares** in its policy data, the audit confirms the **enforcing artifact is present and registered** — the hook is wired in `.claude/settings.json`, the Layer 1 rule exists, the Layer 0 push-URL classification is applied, as applicable to that constraint's placement.
- A constraint **declared but not enforced** (policy says it is enforced; the wiring is absent) is a finding (exit 1) — the audit's fail-closed posture.
- This closes the loop on declare-once-derive: the policy is the source, the hook/permission config is the *enforce* derivation, and the audit is the *verify* derivation; the audit catches drift between declaration and enforcement.

# Test Strategy
This document specifies a model and conventions; its enforcing **code** is implemented and tested under its own implementation specs (forthcoming sprints), where the required tests are:

- **Hook handler:** blocks a violating command (exit 2) and allows a compliant one; fails closed on malformed/missing policy; returns `ask` for unclassified conditional cases. Unit tests under `tests/tools/aire/`.
- **Audit harness check:** flags a declared-but-unenforced constraint; passes when policy and wiring agree.
- **Policy-data parsing/validation:** well-formed policy parses; malformed policy is rejected (fail closed).
- **Bypass-survivability** of the hook layer is an *environment* property, not unit-testable in the stdlib suite. It is validated by the operator-run harness test (recorded 2026-06-14: control + bypass + positive-control), re-runnable on demand — same validation posture as the CI promotion gate.

This spec file itself contains no executable code; it has no unit tests of its own. Its conformance is verified by `aire audit` once the harness check ships (see Verification). **Tests: deferred to the implementation specs named above**, not N/A.

# Completion Criteria
**Spec-level (this sprint):**
- The model, layers, bypass-survivability classification, placement rule, policy-as-data convention, and audit contract are stated unambiguously enough that the implementation specs can be written mechanically.
- Every existing hard constraint in the governance set is assignable to a layer under the placement rule (none left unclassifiable).
- The open design questions are enumerated for operator decision before implementation begins.

**Milestone-level (later sprints, tracked in ROADMAP):**
- The `aire hook` handler, Layer 1 rules, and Layer 0 classification are implemented and tested.
- aire's own hard constraints are declared in committed policy and the enforcement is wired into aire's `.claude/`, dogfooded by **blocking a real violation**.
- `aire audit` confirms the declared policy is in force. This is the condition that closes DEC-000001.

# Reference Implementation Scope
Drawn from DEC-000001 and the milestone decomposition:

- **Sprint 1 (this):** this governing spec.
- **Sprint 2 — `aire hook` shim:** the deferred CLI `hook` primitive — a `PreToolUse` handler that reads policy-as-data and enforces fail-closed. Governed by `specs/tools/aire/hook-spec.md`.
- **Sprint 3 — policy data + wiring:** declare aire's hard constraints (push posture / remote classification, protected paths *including the hook config*, commit format) in committed policy; wire the hook + Layer 1 deny rules into `.claude/settings.json`; add Layer 0 push-URL classification to project-init; dogfood blocking a real violation.
- **Sprint 4 — audit harness check:** `aire audit` verifies declared policy is in force; closes DEC-000001.

# Open Design Questions
*(For operator decision before the implementation sprints — surfaced here rather than silently chosen.)*

1. **Policy-data layout.** One `.aire/config.toml` `[harness]` section (favored by declare-once-derive — a single source) vs per-domain files such as `.claude/remote-policy.json` (named in DEC-000001). Decide before Sprint 2.
2. **Hook-integrity scope.** Protect the hook config/scripts/policy as protected paths (who-guards-the-guards) — accepting it is mistake-proofing within the cooperative threat model, not an adversarial guarantee — or rely on the off-box gate plus containment for that residual?
3. **Constraint migration order.** Which hard constraints move from prose to hooks first? Push posture is the obvious first; commit format, protected-path writes, and working-tree-clean / `STATE.md` freshness follow.
4. **Stop-hook scope.** DEC-000001 named a `Stop` hook for working-tree-clean / `STATE.md` freshness. Include it in this milestone or defer?
5. **Cross-platform.** The hook mechanism is Claude-Code-specific; Codex parity is deferred to the Cross-Platform Parity milestone but should be kept in mind so the *policy-data* format stays platform-neutral.

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-06-14 (v0.1.0)
- summary: Initial spec. Formalizes DEC-000001 (layered harness enforcement) as a governing spec: the Layer 0–3 ladder plus the off-box gate, the bypass-mode survivability classification, the placement rule, the policy-as-data / declare-once-derive convention, and the `aire audit` verification contract. Incorporates the 2026-06-14 empirical finding that PreToolUse hooks block under `--dangerously-skip-permissions` (Layer 2 is a deterministic guard, not audit-only). Concrete file formats and enforcing code are deferred to forthcoming implementation specs under `specs/tools/aire/`.
