---
title: Analysis-and-Design Specification
version: 0.1.1
maintained_by: Aire System Architect (ASA)
domain_tags: [system, governance, analysis, design, isad, feasibility]
status: stable
platform: claude-code
license: Apache-2.0
---

# Purpose

Own the **front-door disciplines of information-systems analysis and design (ISAD)** that aire practices but has never stated in one place: how a system-building task is analyzed before it is built (the approach-memo / feasibility discipline), how a store or format is migrated (the conversion-strategy menu), how the system's own structure is surfaced for reading (derived views over the canonical schemas), and how a shipped milestone is reviewed (predicted-vs-observed). It is the **incorporation of the ISAD canon into aire** decided by the `sprints/isad-incorporation/` brainstorm loop (plan of record: `03 §Plan`, auditor-signed `06`): four rules and a mapping table — everything the canon offers that aire did not already carry, and nothing it did (the org-scale apparatus is declined here, on the record, with reasons).

This spec adds **no rule that another spec already owns.** aire is already ISAD-shaped where it matters — spec-first *is* requirements-before-build, owner-gated milestones *are* phase gates, provenance + version-pinning + pull-by-check *is* change management, the decorrelated builder↔auditor split *is* design review. This spec states only the four disciplines that were **practiced-but-unowned** and provides the mapping table that keeps the canon's vocabulary from forking aire's.

# Scope

## Covers
- **G1 — the analysis-phase discipline:** the approach-memo artifact class (schema, the feasibility fourfold re-grounded in aire's real cost substrate, the approach-of-record freeze rule) and its activation gate.
- **G2 — the conversion-strategy menu:** the named migration modes and the reversibility/rehearsal requirement any migration-bearing plan binds.
- **G3 — the derived-views rule:** the artifact-schema index and the information-flow map as regenerable views over schemas that stay in their owning specs.
- **G4 — the post-implementation review rule:** the review record a shipped milestone closes with.
- The **mapping table** (ISAD term → aire artifact) that prevents terminology forks.
- The **declined set** (the org-scale ISAD apparatus that does not enter aire), named with reasons.

## Does Not Cover
- **Any rule an existing spec already owns.** Requirements → `claude/spec-spec.md`; phasing/milestones → `claude/planning-spec.md` + `claude/project-init-spec.md`; structured investigation → `claude/discovery-driven-diagnostics-spec.md`; design-decision records → `claude/decision-log-spec.md`; documentation → `claude/documentation-spec.md`; testing/acceptance → `claude/claude.role.base.md` (test-as-completion) + `claude/coverage-spec.md`; change management → change-control/provenance + Governance Version Pinning (`claude/claude.role.base.md`) + `claude/roles-compliance-spec.md` pull-by-check; cross-session memory & prospective obligations → `claude/memory-spec.md`; context-bundle composition → `claude/dt-spec.md` / `claude/dt-instrument-spec.md`; the memory-store schema → the 3D-memory blueprint (`sprints/3d-memory/10 §Blueprint`). This spec **binds those by pointer and restates none of them.**
- **The generator tooling** for G3's derived views (a stdlib-python regenerator with fail-closed gates) — owner-scoped OUT of the initial adoption ([OWNER-B] resolved: hand-authored index first; generators are a separately-gated later milestone).
- **Adoption.** The builder authors, the auditor verifies, the owner adopts — per the standing governance-change discipline.

# Inputs
- The **task at hand**, classified by the G1 activation gate (system-building vs routine).
- The existing **governance set** (the owning specs named in §Does-Not-Cover) — G1–G4 compose with these by pointer.
- The **owning specs' `§Outputs` schemas** (anchor record, memory node, comms frontmatter, dt bundle, STATE structure) — the canonical data G3's views are *derived from*, never a second home for.
- For G1's schedule leg: the **prospective-obligations ledger** (`obligations.<role-slug>.md` per `claude/memory-spec.md`) — the carrier a dated window binds to.
- The **plan of record** for any milestone the disciplines govern (`sprints/…`), where G2's migration mode and G4's review record land.

# Outputs
- An **approach memo** (G1) — one per activated analysis, `sprints/…` or the plan-of-record's own §Feasibility: `{problem, options, feasibility-fourfold, recommendation, owner-gate}`. On owner adoption it becomes **approach-of-record: cited, frozen, never edited** (the history carve-out).
- A named **migration mode + reversibility rehearsal** (G2) in any migration-bearing plan.
- Two **derived views** (G3), regenerable, never canonical: the **artifact-schema index** (artifact-class → schema-owning-spec pointer table) and the **information-flow map** (who-reads/who-writes, derived from role `Inputs`/`Outputs`).
- A **review record** (G4) at each shipped milestone: predicted-vs-observed (the R10-ledger form).

# Responsibilities

The four rules are labelled **G1–G4** — the "G" denotes the *gap* each closes (the plan's derivation ID; kept, not renamed, so the plan↔spec traceability the loop verified stays intact and no synonym forks).

## G1 — The analysis-phase discipline (owning statement)

A **system-building task** (a new mechanism, tool, store, or migration — the activation gate below) is analyzed **before** it is built, and the analysis is recorded as an **approach memo**:

- **Schema:** `problem` · `options` · `feasibility (the fourfold)` · `recommendation` · `owner-gate`.
  - **`options` MUST name the compose-with-existing / adopt / build fork** (ISAD build-vs-buy, re-grounded): the first option is always *compose with or extend an existing aire mechanism*; *adopt* an external instrument; *build* new — in that order of preference (the dt / a3m never-reinvent lesson, mechanized where it belongs). An analysis that jumps to "build" without disposing "compose" is an incomplete memo.
- **The feasibility fourfold, in aire's real cost substrate** (NOT the classical dollars-and-org fourfold):
  - **technical** = harness capability + the single-machine trust model (what the environment can actually enforce vs. what rides discipline).
  - **economic** = **token / context budget** (the dt-budgets substrate — never dollars-ROI).
  - **operational** = **owner attention / gate load** (counted, not vibed — how many decisions and reviews the path asks of the owner).
  - **schedule** = **a dated window names its CARRIER**: a prospective-obligation entry per `claude/memory-spec.md`, **or explicitly "owner-carried."** A dated obligation with no named carrier is a G1 defect (the "dated obligations without watchers" failure class this rule exists to close).
- **Approach-of-record freeze (the class rule, stated once here):** an **adopted** approach memo is **cited, frozen, never edited** — the history carve-out. Superseding analysis is a *new* memo that cites the old, never an edit of it. (This absorbs the freeze convention previously restated in ≥3 specs in local wording — `dt-spec`, `memory-spec`, `loop-contract`, each at L15 — a distributed quasi-rule now homed. Those restatements convert to one-clause pointers to this rule; per the plan of record they ride each spec's **next natural edit** rather than a dedicated stroke, and — so that deferral does not go silent (GP3: two homes is one defect) — the conversions are **tracked as prospective obligations** per `claude/memory-spec.md`. That is G1's own schedule-carrier rule applied to this spec's own rollout: the two-homes window is *watched*, not merely promised.)
- **Activation gate ([OWNER-C] resolved: system-building tasks only).** G1 **fires** on a task with a new-mechanism / new-tool / new-store / migration component; **routine amendments do not activate it** (*always-in-force ≠ always-firing* — the DDD activation precedent). A routine version bump, a pointer-line add, a fold of an auditor note: no memo owed. A new checker, a new store, a format migration: memo owed.
- **Born-conformant.** The existing approach memos (`opus-hardening-approach-memo.md`, `dt-revival-approach-memo.md`, `loop-contract-approach-memo.md`, `memory-governance-approach-memo.md`) are the class's **precedents** — the discipline names what practice already proved; it does not indict the memos that predate it.

## G2 — The conversion-strategy menu (owning statement)

A **migration-bearing** plan (any plan that moves a store, format, or deployed artifact from one shape to another) MUST **select and name** a migration mode and its reversibility requirement:

- **The modes:** **parallel** (old + new run together, compared, then old retired) · **phased** (migrate in bounded increments) · **pilot** (migrate one subject, validate, then the rest) · **direct cutover** (replace in one stroke — permitted only with a rehearsed rollback).
- **Reversibility rehearsal:** the plan states its rollback, and **rehearses it where cheap** — a described escape hatch is a claim; an *executed* one is evidence (the 3D-blueprint bar-7 precedent, generalized). Direct cutover without a rehearsed rollback is a G2 defect.
- Stated once here; migration-bearing plans and `claude/roles-compliance-spec.md` bind by pointer and restate no mode text.

## G3 — The derived-views rule (owning statement)

Two **derived views** exist over the governance set, each **regenerable, never canonical, never a second home for any schema** — an application of **NORTHSTAR Guiding Principle 4 (GP4): "canonical state, derived views, gated changes"**, cited as ground and not restated (NORTHSTAR labels its principles by number; "GP4" is the conventional shorthand for its Guiding Principle 4):

- **The artifact-schema index:** a table `artifact-class → schema-owning-spec pointer`. The schema itself stays in its owning spec (the anchor record's schema stays in `reanchor-spec` §Outputs; the memory node's in the 3D blueprint; the comms frontmatter's in `.comms/README.md`; the dt bundle's in `dt-spec`). The index **points**; it never copies. (A3m's store schema stays a3m's — the composition seam held.)
- **The information-flow map:** who-reads / who-writes, **derived from** role `Inputs` / `Outputs` sections and the comms topology. It is a reading of the canonical role files, not a new declaration.
- **Hand-authored first.** Both views are small enough to maintain by hand at adoption. The stdlib-python **regenerator** (with a3m-style fail-closed gates: hand-edit diff + regeneration equality) is **out of the initial adoption** ([OWNER-B]) — a separately-gated later milestone; the hand-authored index does not wait for it.
- **Motivating exhibits (why the rule):** hand-maintained enumerations rot — this loop found `specs/INDEX.md` miscounting the approach-memos (three named, four on disk) and the compliance checker's self-description stale against the rows it runs. The derived-view discipline is the answer to exactly that decay: regenerate, don't hand-copy.

## G4 — The post-implementation review rule (owning statement)

A **shipped milestone** closes with a **review record**: what was **predicted** vs. what was **observed** (the R10 causal-ledger form generalized). Retrospective sprints are the existing practice; this names it as a completion step. Presence-checkable at milestone close; a milestone that ships with no review record is a G4 omission.

## The mapping table (prevents terminology forks — travels with this spec; existing aire names KEEP)

| ISAD term | aire artifact (name KEPT; no synonym introduced) |
|---|---|
| Requirements specification | **spec** (`claude/spec-spec.md`) |
| Feasibility study | **approach memo §Feasibility** (G1) |
| System proposal | **approach memo** (G1) |
| Phase gate | **owner-gated milestone** (`claude/planning-spec.md`) |
| Build-vs-buy / procurement | **memo §options fork: compose / adopt / build** (G1) |
| Controls design (validation, audit trails, access) | **spec-spec Edge-Cases/Fault-Handling + audit surface + the single-machine trust model** (covered; no new rule) |
| Data dictionary | **artifact-schema index** (G3 view; schemas stay in owning specs) |
| DFD / process model | **information-flow map** (G3 view; flows live in role Inputs/Outputs) |
| Logical design | **owning spec** (spec-first) |
| Physical design | **implementation under the adopted spec** |
| Conversion strategy | **migration mode** (G2) |
| Post-implementation review | **retrospective sprint / review record** (G4) |
| Design decision record | **decision log entry** (`claude/decision-log-spec.md`) |
| Change control board | **the owner** |
| CASE tooling | *(declined — see below)* |

## The declined set (the selection filter's output — the canon that does NOT enter aire, with reasons)

1. **Steering committees / change-control boards / sign-off chains** — the owner IS the gate; committee ceremony on a one-owner system is pure overhead.
2. **Waterfall big-bang phase gates** — owner-gated incremental milestones stand; analysis-before-build survives per-task via G1's activation gate, not as a project-lifecycle dam.
3. **CASE tool suites** — aire instruments are minimal, stdlib, invention-granted per case (the a3m precedent); no modeling-suite dependency.
4. **Analyst / designer / programmer actor separation** — aire's actors are owner + decorrelated pair + generated roles; the builder/auditor split already carries the design-review separation.
5. **Interview / questionnaire elicitation apparatus** — owner directives + comms + the verbatim-directive rule are the elicitation, with higher fidelity than requirement-gathering forms.
6. **Dollars-ROI economic feasibility** — replaced by the token/attention substrate (G1's fourfold).
7. **Big-upfront total-system modeling** — analysis scales to the task (activation gate); the whole-system view is served by the G3 *derived* views, not an upfront modeling phase.
8. **Maintenance as a separate lifecycle phase** — living governance already (version bumps, pull-by-check propagation, re-anchor cadence); a separate maintenance regime would be a second home.
9. **Requirements-traceability matrixing** — the substance is carried by the verbatim-directive rule + `decision-log-spec` + provenance discipline; **no honest mechanical check exists at the per-requirement grain** (a per-NR source-class check is version-diffing wearing a grep costume — tested and killed in the incorporation loop, volley 2). Declined rather than adopted as a prose promise.

# Edge Cases / Fault Handling
- **A build task with no memo** (G1 activated, no approach memo): a G1 omission — surface it; the analysis is owed before the build, not after.
- **A memo that skips the compose/adopt/build fork:** incomplete — the "compose with existing" option must be disposed before "build" is chosen (the never-reinvent guard).
- **A dated obligation with no named carrier** (G1 schedule leg): a defect — every dated window names a prospective-obligation entry or "owner-carried"; an unwatched date is the failure class this closes.
- **A migration plan with no named mode** (G2): a defect — parallel/phased/pilot/direct must be chosen and named.
- **Direct cutover with no rehearsed rollback** (G2): a defect — the escape hatch is a claim until executed.
- **A G3 view that restates a schema instead of pointing:** a defect (second-home / GP4 violation) — the view points, the owning spec holds the schema.
- **A G3 view gone stale** (governance changed, the derived view not regenerated): a G3 **currency** defect — the views are re-derived at governance-change events; a drifted view is the exact rot the rule exists to prevent (the `specs/INDEX.md` memo-miscount that motivated the rule was one). Presence-**and-currency**-checkable — the omission-defect symmetric to G1's "no memo" and G4's "no review record."
- **An edited approach-of-record** (a frozen adopted memo edited in place rather than superseded by a new citing memo): a G1 **freeze** defect — supersession is a new memo, never an edit; freeze enforcement rides existing provenance/immutability discipline by pointer.
- **A shipped milestone with no review record** (G4): a G4 omission — presence-checkable at close.
- **Activation misfire** (a routine amendment treated as system-building, or vice-versa): the gate is the new-mechanism/tool/store/migration test; a version bump or pointer-add is routine (no memo); a new checker/store/format is system-building (memo owed). When genuinely ambiguous, the memo is cheap — write it.

# Test Strategy

This spec's conformance is verified two ways: **mechanically** (a compliance-checker row, the machine jaw) and by the **decorrelated auditor** (judgment jaw). The falsifiable acceptance bars (Fable-set 2026-07-05 in the incorporation loop; the Opus implementation phase cannot lower them):

1. **One home per adopted rule:** no G1–G4 rule text appears outside this spec **within the governance homes** (`claude/*-spec.md`, `roles/**`, and role files) — grep-checkable, **exempting** (a) the `sprints/isad-incorporation/` design records and the precedent approach-memos (the derivation and the born-conformant precedents are not rule homes — the same carve-out G1's precedents get; a repo-wide grep that failed against the loop's own records would be dishonestly scoped), and (b) — **transitional** — the three pre-existing approach-of-record-freeze restatements at `dt-spec` L15, `memory-spec` L15, `loop-contract` L15, **while their tracked conversion obligations stand open** (the freeze-conversion prospective obligation in `obligations.aire-smith.md`, gated on M1 adoption); bar 1 **binds fully against each of those three the moment its conversion lands.** The bar carries its own transitional state rather than false-FAILing against the rollout G1 declares two bullets above — the bar-8 currency precedent from this loop, applied to bar 1 itself. The compliance-checker rows pass on all subject roles.
2. **The declined set survives** into this spec, **non-empty, all nine entries reasoned** (the selection filter's permanent output — a spec that adopts the canon wholesale never ran the filter).
3. **The mapping table is present** and introduces **zero new synonyms** for existing aire artifact classes (table presence + auditor sweep).
4. **The propagation row is era-conditioned:** roles generated/pinned before the base-template binding lands read **WORK**, never a retroactive FAIL (the P13 precedent — proven by a pre-era negative-control fixture).
5. **The checker suite strictly grows, GREEN,** with per-row negative controls; zero prior-row regressions.
6. **Born-compliant forge holds:** a freshly forged role passes the new row (the fixture green-team, post-bump).
7. **Propagation lands COMPLIANT:** each subject team returns `VERDICT: COMPLIANT` after its retrofit (ArcBoard the first subject).
8. **Self-application:** any plan adopting these disciplines carries its **own** G1-form feasibility record, true at each gate (a stale feasibility record is a G1 violation *inside* the G1 adoption — the discipline proves itself on its own adoption).

**Per-role conformance mechanism:** `claude/roles-compliance-spec.md` **will carry** the **analysis-design row (P14)** — delivered as milestone **M2**'s propagation step (base v0.4.2 binding line + the P14 row + suite extension), not present on disk until then; this spec **specifies** the row, M2 **lands** it. P14: pointer + a grep-check that the role binds this discipline by pointer (binding line + governance pin present) with the no-restatement jaw (no G1–G4 rule prose in the role), class **M, era-conditioned on the base-template version that lands the binding line** (`tests/roles-compliance/`). Test files: the checker (`tests/roles-compliance/run.sh`) + its suite (`run-tests.sh`), extended with the P14 block and its negative controls.

# Completion Criteria
1. Structure conformant to `claude/spec-spec.md` v0.4.0 (header, nine sections, behavioral declarations explicit).
2. G1–G4 each an explicit behavioral rule with its activation/defect conditions; the mapping table and the nine-entry declined set present.
3. Auditor verdict CONFORMANT against the incorporation loop's signed §Plan and pre-registered bars.
4. The eight acceptance bars each mechanical or auditor-sweep-defined; the propagation row (P14) drafted and era-conditioned.
5. Owner adoption (the plan of record's milestones remain owner-gated; adoption is his).
6. Relevant tests pass — the P14 checker row + suite extension GREEN (per the Test Strategy; this spec is a discipline spec, but it *does* define a mechanically-checkable propagation surface, so tests are required, not N/A).

# Behavioral Declarations
- **Serialization:** approach memos and review records are Markdown (`sprints/…` or a plan's own section); the artifact-schema index and information-flow map are Markdown tables (derived views — regenerable, never canonical). No new binary or on-disk format is introduced (G3's store schemas stay in their owning specs).
- **Activation model:** G1 is activation-gated (system-building tasks only); G2/G4 fire on migration-bearing / shipped-milestone events respectively; G3's views are maintained on governance change (hand-authored; regenerator deferred).
- **Concurrency:** none introduced — the disciplines are authoring-time and review-time acts, not runtime processes; no daemon, no always-on obligation (the open-triangulation daemon space is untouched here).
- **Composition:** every rule binds existing owning specs by pointer (§Does-Not-Cover); this spec adds no schema and no second home.

# Change Control
Update version and provenance on every change.

## Provenance
- time: 2026-07-05
- summary: **OWNER-ADOPTED 2026-07-05** — Completion Criterion 5 met; `status:` draft → stable; content unchanged from the auditor-CONFORMANT v0.1.1 (the owner reviewed the M1 synopsis + the four-rules approach and adopted). **Adoption-time riders fire:** (1) the July-9 prospective-obligation entry stands (landed early per F-P1, `obligations.aire-smith.md`, the named carrier); (2) the three freeze-conversion obligations (dt-spec/memory-spec/loop-contract L15 → one-clause pointers to §G1) **ARM** — condition changes from "pending M1 adoption" to active-against-each-spec's-next-natural-edit (ledger-watched, the GP3 two-homes window now watched-and-live). Content version stays v0.1.1 (adoption is a status transition, not a content edit).
- time: 2026-07-05
- summary: v0.1.1 — **Auditor M1 verdict fold (CONFORMANT-WITH-NOTES → one required fix; aire-smith-auditor on Fable 5, verdict `2026-07-05-auditor-VERDICT-M1-analysis-design-spec-CWN-bar1-transition-exemption-required`).** **F1 (required):** Test-Strategy bar 1 ("no G1–G4 rule text in the governance homes") was false-FAILing against the spec's own G1 rollout — the three approach-of-record-freeze restatements at `dt-spec`/`memory-spec`/`loop-contract` L15 that G1 declares (two bullets above) as tracked-conversion-deferred. Bar 1 now carries a **transitional exemption** for exactly those three while their conversion obligations stand open, binding fully as each conversion lands (the bar-8 currency precedent applied to bar 1 itself). The collision was the half my Opus 6-lens pre-handoff pass missed and the Fable-side derive-then-compare caught — first live decorrelation dividend of the distinct-model split, on the record. **N1 (non-blocking, folded in-stroke):** G3's comms-frontmatter pointer aligned from informal "the comms README" to `.comms/README.md`. No other change — the load-bearing set (structure, both folds, the ledger obligation verified real at the artifact, [OWNER-A/B/C] resolutions, the mapping table + declined set, no-restatement, references-resolve, negative controls) was CONFIRMED against refutation at v0.1.0. aire-smith-auditor delta-verifies this one-clause fix same-turn; owner adoption is the M1 gate.
- time: 2026-07-05
- summary: v0.1.0 — Initial draft, incorporating the ISAD canon into aire per the `sprints/isad-incorporation/` brainstorm loop (owner directive 2026-07-05: "plan on implementing ISAD … which will also need to be pushed to all roles"; plan of record `03 §Plan` as amended, auditor-signed `06`; loop converged at volley 6, one clean catch apiece). Four owning rules — **G1** analysis-phase discipline (approach-memo schema with the compose/adopt/build fork = ISAD build-vs-buy re-grounded; the feasibility fourfold re-grounded in aire's cost substrate — technical=harness+trust-model, economic=token budget, operational=owner gate-load, schedule=carrier-named per `memory-spec` [the volley-4 required fold]; the approach-of-record freeze absorbed as the class rule; activation-gated to system-building tasks per [OWNER-C]); **G2** the conversion-strategy menu (parallel/phased/pilot/direct + rehearsed rollback); **G3** the derived-views rule (artifact-schema index + information-flow map, GP4-grounded, hand-first, regenerator deferred per [OWNER-B]); **G4** the post-implementation review record. Plus the mapping table (terminology-fork guard; controls-design = element 14 disposed as a covered mapping row) and the nine-entry declined set (the selection filter's output; DECLINE #9 = requirements-traceability matrixing, killed on grep-checkability in the loop). Born-conformant on the four existing approach memos. Authored by RoleSmith (aire-smith, Opus 4.8) as ISAD milestone M1; aire-smith-auditor (Fable 5 — genuine cross-model decorrelation this session) verifies refute-default against the signed §Plan + the eight bars; owner adopts. Spec name resolved [OWNER-A] = `analysis-design-spec.md`.
