# Aire for Codex — User Manual

## What is Aire?

Aire is a **context management system for AI-assisted development**. It gives Codex a structured understanding of what it should do, how it should work, and what standards to follow — before it writes a single line of code.

Without Aire, every Codex session starts from scratch. Codex has no memory of your project's conventions, no understanding of your quality standards, and no guardrails beyond its general training. You end up repeating yourself, correcting the same mistakes, and losing consistency across sessions.

Aire solves this by giving Codex a **role** — a specification that defines its responsibilities, constraints, and workflow for your specific project.

## Why Roles Matter

If you've used AI coding assistants, you've probably experienced this: you ask for a feature, the AI writes code, and the result is... fine. It works. But it doesn't follow your project's patterns. It skips tests. It doesn't document anything. It makes architectural decisions you didn't authorize. And when you start the next session, it has no memory of what it did or why.

**Roles fix this.** A role is a detailed specification that tells Codex:

- **What it's responsible for** (and what it must not touch).
- **How to work** — spec-first development, testing requirements, documentation expectations.
- **How to communicate** — when to proceed, when to ask, when to refuse.
- **How to track state** — so that context survives across sessions.
- **How to make decisions** — what it can decide freely, what needs logging, what requires your approval.

Without a role, Codex is a general-purpose assistant. With a role, Codex is a **team member** that understands the project, follows the process, and maintains continuity.

### The real benefit

The role isn't just instructions for Codex — it's a **contract between you and the AI**. When Codex follows a role:

- You can review the role spec to know exactly what Codex will and won't do.
- You can trust that tests will be written, because the role makes testing non-optional.
- You can pick up where you left off, because STATE.md tracks everything.
- You can make architectural decisions confidently, because Codex will ask instead of guessing.
- You can onboard to a project you haven't touched in weeks by reading STATE.md and ROADMAP.md.

This is the difference between "AI that writes code" and "AI that develops software."

## How Aire Works

Aire for Codex consists of:

1. **Governance specs** — standards that define how work is done (testing, git, specs, documentation, planning, decisions, state tracking).
2. **AireSmith** — a role that generates other roles. You describe what you need; AireSmith produces a role spec that follows all the governance standards.
3. **Project roles** — the roles AireSmith generates for your specific projects.

The governance specs are the foundation. AireSmith reads them and embeds their requirements into every role it creates. This means every role automatically inherits:

- Spec-first development (specs before code).
- Mandatory testing (no "(if applicable)" escape hatch).
- Git hygiene (branching, commits, promotion).
- State tracking (STATE.md at repo root, maintained across sessions).
- Decision logging (auditable record of why choices were made).
- Planning structure (northstar, roadmap, sprints).
- User-facing documentation requirements.

## Getting Started

### Prerequisites

- [Codex CLI](https://github.com/openai/codex) installed and working.
- A git repository for your project (or willingness to create one).
- The `codex/` directory from this repository.

### Step 1: Copy Aire into your project

Copy the `codex/` directory into your project repository:

```
your-project/
  codex/
    codex.role.base.md
    codex.git-hygiene.md
    spec-spec.md
    state-tracker-spec.md
    state-pack-spec.md
    decision-log-spec.md
    planning-spec.md
    project-init-spec.md
    documentation-spec.md
    roles/
      aire-smith/
        aire-smith.role.md
        AGENTS.md
```

You do NOT need the entire Aire repository — just the `codex/` directory with the governance specs and the AireSmith role.

### Step 2: Generate your project role

Copy the AireSmith AGENTS.md to your project root:

```bash
cp codex/roles/aire-smith/AGENTS.md ./AGENTS.md
```

Start a Codex session. Codex will read AGENTS.md and load the AireSmith role. Then describe the role you need:

```
I need a developer role for a Python web API. It uses FastAPI, PostgreSQL,
and SQLAlchemy. The project is a task management API. The role should cover
backend implementation, database schema, API endpoints, and tests. It should
NOT cover frontend, deployment, or infrastructure.
```

AireSmith will generate a role spec tailored to your project. Review it — this is the contract that will govern Codex's behavior. Edit it if needed. The role file goes in your project (e.g., `developer.role.md` at the root, or wherever you prefer).

### Step 3: Set up your project AGENTS.md

Replace the AireSmith AGENTS.md with one that points to your new project role. The generated role includes an AGENTS.md — use that as your starting point. It should reference:

- Your project role file.
- STATE.md for state tracking.
- NORTHSTAR.md and ROADMAP.md for planning.
- The governance specs in `codex/`.

### Step 4: Initialize the project

Start a new Codex session with your project AGENTS.md in place. Codex will:

1. Read AGENTS.md and load the role.
2. Notice STATE.md doesn't exist and offer to create it.
3. Help you create NORTHSTAR.md (project vision, success criteria, guiding principles).
4. Help you create ROADMAP.md (milestones and outcomes).
5. Create sprints for the first milestone.
6. Begin work.

For existing projects, the initialization is similar but Codex will audit existing code against the new standards and build STATE.md from the current project state.

## The Governance Specs

Here's what each spec does and why it matters:

### codex.role.base.md
The base template for all roles. Defines the sections every role must have, the verification checklist, and the relational primitives (behavioral rules for how Codex interacts with you). You rarely edit this directly — AireSmith uses it to generate roles.

### spec-spec.md
Defines how specs are structured. Every spec in your project follows this standard. Key feature: the mandatory **Test Strategy** section — every spec must define what tests are needed, making testing a design decision, not an afterthought.

### codex.git-hygiene.md
Git branching, commit conventions, and promotion rules. Two profiles: **Profile A** (docs/policy, no tests needed) and **Profile B** (software, tests required before merging to main). Each sprint maps 1:1 to a git branch.

### state-tracker-spec.md
Defines STATE.md — a human-readable project state file at the repo root. This is your primary way to see where things stand. Codex maintains it; you can read or edit it at any time.

### state-pack-spec.md (Session Context)
Defines what Codex loads at the start of each session to restore context. STATE.md first, then role spec, then git state, then whatever else is relevant.

### decision-log-spec.md
Structured decision recording. Three classes: **A** (free to decide), **B** (decide and log), **C** (escalate to you). Decisions are stored as JSON files — searchable, auditable, and version-controlled.

### planning-spec.md
Defines three planning artifacts: **NORTHSTAR.md** (vision and principles), **ROADMAP.md** (milestones and outcomes), and **sprint files** (granular work units). Planning is outcome-bound, not time-bound.

### project-init-spec.md
The bootstrap sequence: how to go from "I have role files" to "Codex is working." Covers AGENTS.md setup, directory scaffolding, and the planning phase.

### documentation-spec.md
Requirements for user-facing documentation. README always required. HOWTOs, reference docs, manpages per project type. Also defines the **spec index** (specs/INDEX.md) — a table of contents for all specs.

## Codex-Specific Notes

### Sandboxed execution
Codex runs inside a sandboxed container. Network access is disabled by default. Roles and specs are designed with this in mind — no governance rule assumes network availability. If your project requires network access (e.g., fetching dependencies), you'll need to enable it in Codex's configuration.

### AGENTS.md vs CLAUDE.md
If you're familiar with Aire for Claude Code, the structure is identical. The only entry-point difference is that Codex uses `AGENTS.md` instead of `CLAUDE.md`. All governance specs, role structures, and workflows are the same.

## Tips

### Switching roles mid-project
If your project needs multiple roles (e.g., an architect and a developer), keep both role files in the project. Swap AGENTS.md to point to the role you need for the current session. STATE.md provides continuity regardless of which role is active.

### Customizing governance
The governance specs are starting points. If your project doesn't need decision logging, remove it from the role. If you want different git conventions, edit codex.git-hygiene.md. The system is modular — use what helps, skip what doesn't.

### For existing projects
You don't need to start from scratch. Copy in the `codex/` directory, generate a role, and let Codex audit your existing code against the new standards. It will identify gaps in specs, tests, and documentation and help you close them incrementally.

### When Codex pushes back
If Codex halts and asks for clarification, that's the role working correctly. The role is designed to make Codex stop when things are ambiguous rather than guess. Answer the question and Codex will proceed. If Codex halts too often, your specs may need more detail — that's useful signal.

## File Inventory

```
codex/
  MANUAL.md                 # This file
  codex.role.base.md        # Base role template
  codex.git-hygiene.md      # Git branching and commit standards
  spec-spec.md              # Spec structure standard
  state-tracker-spec.md     # STATE.md format and rules
  state-pack-spec.md        # Session context loading rules
  decision-log-spec.md      # Decision logging standard
  planning-spec.md          # Northstar, roadmap, sprint specs
  project-init-spec.md      # Project bootstrap sequence
  documentation-spec.md     # User-facing documentation standard
  roles/
    aire-smith/
      aire-smith.role.md    # The role that generates roles
      AGENTS.md             # AGENTS.md for AireSmith sessions
```
