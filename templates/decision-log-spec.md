# Decision Log Spec v0.1

**Status:** Draft (ready to implement)

## Purpose
Create a deterministic, searchable decision record so roles (Architect/Developer/Runner/Tester) can **consult** past decisions instead of relying on conversation memory.

This spec defines:
- The **canonical** decision event format (append-only JSON)
- A **derived** SQLite full-text search index
- A minimal **CLI contract** for search and retrieval
- Required **governance behaviors** for autonomous roles

---

## Definitions
- **Decision Event**: An immutable record capturing a single decision, its context, alternatives, and rationale.
- **Canonical Store**: The source of truth. Must be human-auditable and VCS-friendly.
- **Derived Index**: Rebuildable artifacts used for fast searching/querying.
- **Decision ID**: Stable identifier of the form `DEC-000123`.

---

## Directory Layout
All paths are repo-relative.

- `decisions/`
  - `SEQ.txt` *(optional)*: monotonically increasing integer used to allocate the next decision ID
  - `events/` *(canonical)*
    - `DEC-000001.json`
    - `DEC-000002.json`
    - ...
  - `index.sqlite` *(derived; rebuildable)*
  - `README.md` *(optional)*: quick usage notes

Notes:
- `decisions/events/*` are the **only** canonical records.
- `decisions/index.sqlite` MUST be treated as **derived**; it may be deleted and regenerated at any time.
Reinforcement: `decisions/index.sqlite` is always derived and safely regenerable.

---

## Decision Event Schema

### File format
- Encoding: UTF-8
- Format: JSON object
- One decision per file

### Required top-level fields
- `schema` (string): must equal `coretexgrid.decisions.v0.1`
- `id` (string): `DEC-` + 6 digits, zero-padded
- `ts` (string): ISO-8601 timestamp with timezone offset
- `project` (string): short project name
- `repo` (string): repo identifier or path
- `role` (string): one of `architect|developer|runner|tester|other`
- `decision_class` (string): one of `A|B|C`
- `title` (string): concise, searchable summary
- `decision` (string): the chosen course of action, written as a single clear statement
- `context` (object): structured pointers to relevant state
- `scope` (object): where this applies (areas + paths)
- `options` (array): at least 1 option object; include the chosen option and alternatives
- `rationale` (string): why this choice was made
- `risk` (object): minimal risk + rollback info
- `links` (object): pointers to commits, PRs, run IDs, etc.
- `outcome` (object): status + verification pointers (may start as unknown)
- `tags` (array of strings): 0+ tags

### Recommended fields
- `context.assumptions` (array of strings)
- `context.spec_refs` (array of strings): canonical spec pointers (paths + optional anchors)
- `context.task_id` (string)
- `scope.areas` (array of strings)
- `scope.paths` (array of strings)

### Decision Class Semantics
- **Class A (Free to decide):** safe defaults, refactors preserving behavior, style/lint/doc wording, internal naming, test strategy improvements.
- **Class B (Decide + log):** behavior changes, public API shape, storage format, security posture, perf tradeoffs, new dependencies.
- **Class C (Escalate or pre-authorized policy):** irreversible/high-risk actions (data destruction, privilege expansion, licensing changes, major architecture pivots, paid services, production-impacting operations).

### Outcome Semantics
- `outcome.status` must be one of:
  - `unknown` (default)
  - `success`
  - `partial`
  - `failed`
  - `reverted`
- `outcome.verified_by` is an array of pointers (e.g., run IDs, test logs, commit SHAs).

---

## Canonical JSON Example (Normative)
Implementations MUST accept and produce JSON compatible with this structure.
Reinforcement: implementations accept and emit JSON that matches this canonical schema.

```json
{
  "schema": "coretexgrid.decisions.v0.1",
  "id": "DEC-000123",
  "ts": "2026-01-13T19:22:11-06:00",
  "project": "myapp",
  "repo": "gits/myapp",
  "role": "runner",
  "decision_class": "B",
  "title": "Use SQLite FTS5 for decision search index",
  "decision": "Index decision events into a generated SQLite database using FTS5; JSON files remain source of truth.",
  "context": {
    "task_id": "TASK-0042",
    "milestone": "v0.1",
    "spec_refs": ["specs/team/ai2ai.md#v2", "specs/meta/decision-log-spec.md#v0.1"],
    "inputs": ["STATE.md", "decisions/events/*"],
    "assumptions": ["Local-only usage for v0.1"]
  },
  "scope": {
    "areas": ["governance", "tooling"],
    "paths": ["decisions/", "tools/decision_indexer.py"]
  },
  "options": [
    {"name": "sqlite_fts5", "pros": ["fast local search", "structured queries"], "cons": ["needs rebuild script"]},
    {"name": "ripgrep_only", "pros": ["zero tooling"], "cons": ["weak structure, hard analytics"]},
    {"name": "postgres", "pros": ["powerful"], "cons": ["ops overhead"]}
  ],
  "rationale": "SQLite provides strong local query + FTS with minimal operational cost; keeping JSON as source-of-truth preserves portability.",
  "risk": {
    "level": "low",
    "reversibility": "high",
    "rollback": "Delete index.sqlite and regenerate or switch to grep."
  },
  "links": {
    "commit": null,
    "pr": null,
    "run_ids": []
  },
  "outcome": {
    "status": "unknown",
    "verified_by": [],
    "notes": null
  },
  "tags": ["search", "sqlite", "fts", "governance"]
}
```

---

## Decision ID Allocation
Implementations MUST provide deterministic, collision-free decision IDs.
Reinforcement: decision IDs are deterministic and never collide.

### v0.1 recommended mechanism
- Store a single integer in `decisions/SEQ.txt`.
- To allocate:
  1. Read integer N
  2. Increment to N+1
  3. Write back atomically
  4. Use `DEC-` + zero-padded 6-digit N+1

If `SEQ.txt` does not exist, initialize at `0`.

---

## Search Index (SQLite, Derived)

### Source-of-truth rule
- The SQLite database MUST be reconstructible from `decisions/events/*.json`.
- The SQLite database MUST NOT be required for correctness (only for speed/UX).
Reinforcement: SQLite is always rebuildable from JSON and never required for correctness.

### Database location
- `decisions/index.sqlite`

### Required capabilities
- Full-text search across:
  - `title`, `decision`, `rationale`, `tags`, `scope.paths`, `scope.areas`
- Filter by structured fields:
  - `id`, `role`, `decision_class`, `project`, `ts` range
- Deterministic rebuild:
  - `rebuild-index` MUST fully regenerate the DB from canonical JSON events.
Reinforcement: `rebuild-index` fully regenerates the DB from canonical JSON.

### Minimal schema requirements (implementation-agnostic)
Implementations MUST store at least these logical fields:
- `id` (primary key)
- `ts` (sortable)
- `project`
- `role`
- `decision_class`
- `title`
- `decision`
- `rationale`
- `tags` (string or normalized table)
- `scope_paths` (string or normalized table)
- `scope_areas` (string or normalized table)
- `outcome_status`

FTS MUST support phrase and keyword search.
Reinforcement: store the required logical fields and support phrase/keyword FTS.

---

## CLI Contract (Minimal)
A deterministic engine should expose these verbs (names are illustrative; behavior is normative):

### `dec add`
- Creates a new decision event JSON file with the next ID
- Writes to `decisions/events/DEC-XXXXXX.json`
- MUST validate required fields
Reinforcement: `dec add` validates all required fields before writing.

### `dec show DEC-XXXXXX`
- Displays the canonical JSON (or a formatted view derived from it)

### `dec search <query>`
- Uses FTS index if available
- MUST fall back to scanning JSON files if index missing
- Returns ranked results with at least: `id`, `title`, `ts`, `role`, `decision_class`
Reinforcement: `dec search` falls back to JSON scanning when the index is missing.

### `dec list [filters]`
- Structured filters (no full-text required)
- Examples: `--class B`, `--role runner`, `--since 2026-01-01`, `--project myapp`

### `dec rebuild-index`
- Deletes and regenerates `decisions/index.sqlite` deterministically

---

## Role Governance Requirements

### Runner/Developer/Architect autonomy behavior
- For Class A decisions: proceed without escalation.
- For Class B decisions: proceed **and** record a decision event.
- For Class C decisions: do not block work; instead:
  - If a safe reversible default exists, proceed with that default and log a decision event noting the escalation concern.
  - If no safe path exists, produce a choice set (2–3 options), recommend one, and record a decision event with `decision_class: "C"` and `outcome.status: "unknown"`.

### Mandatory logging triggers
A decision event MUST be created when:
- Any new external dependency is introduced
- Any public interface is added/changed
- Any persistence format is added/changed
- Any security posture changes
- Any architectural pattern is adopted that affects multiple modules
Reinforcement: these triggers always require a decision event.

### Traceability requirement
When code is changed due to a decision:
- The resulting commit message or PR description SHOULD reference the decision ID(s), e.g. `DEC-000123`.
- The decision event `links.commit` SHOULD be filled in once available.
Reinforcement (SHOULD):
- Reference decision IDs in commits/PRs and fill `links.commit` once available.

---

## Determinism Requirements
- Given the same canonical event set, `dec rebuild-index` MUST produce functionally equivalent search results.
- `dec search` MUST return stable ordering for ties (e.g., sort by `ts desc`, then `id desc`).
- Canonical JSON events MUST be valid JSON and must not depend on runtime-only fields.
Reinforcement: rebuild results are equivalent, tie ordering is stable, and canonical events are valid JSON without runtime-only fields.

---

## Future-Compatible Extensions (Non-normative)
These are explicitly out of scope for v0.1 but supported by the schema approach:
- Separate outcome events (append-only) linked by decision ID
- Embedding-based semantic search
- Analytics pipelines (DuckDB/Spark/Trino)
- Fine-tuning datasets derived from decisions + outcomes

---

## Acceptance Criteria
An implementation is compliant with v0.1 if it:
1. Writes decision events to `decisions/events/*.json` in the required schema
2. Allocates deterministic `DEC-` IDs without collisions
3. Can rebuild a SQLite FTS index from canonical events
4. Supports `show`, `search`, `list`, and `rebuild-index` behaviors (with JSON-scan fallback for search)
5. Enables roles to reference and consult decisions by ID during task execution
