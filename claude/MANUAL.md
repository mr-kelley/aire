# Aire for Claude Code — User Manual

## What is Aire?

Aire is a **context management system for AI-assisted development**. It gives Claude Code a structured understanding of what it should do, how it should work, and what standards to follow — before it writes a single line of code.

Without Aire, every Claude Code session starts from scratch. Claude has no memory of your project's conventions, no understanding of your quality standards, and no guardrails beyond its general training. You end up repeating yourself, correcting the same mistakes, and losing consistency across sessions.

Aire solves this by giving Claude a **role** — a specification that defines its responsibilities, constraints, and workflow for your specific project.

## Why Roles Matter

If you've used AI coding assistants, you've probably experienced this: you ask for a feature, the AI writes code, and the result is... fine. It works. But it doesn't follow your project's patterns. It skips tests. It doesn't document anything. It makes architectural decisions you didn't authorize. And when you start the next session, it has no memory of what it did or why.

**Roles fix this.** A role is a detailed specification that tells Claude:

- **What it's responsible for** (and what it must not touch).
- **How to work** — spec-first development, testing requirements, documentation expectations.
- **How to communicate** — when to proceed, when to ask, when to refuse.
- **How to track state** — so that context survives across sessions.
- **How to make decisions** — what it can decide freely, what needs logging, what requires your approval.

Without a role, Claude is a general-purpose assistant. With a role, Claude is a **team member** that understands the project, follows the process, and maintains continuity.

### The real benefit

The role isn't just instructions for Claude — it's a **contract between you and the AI**. When Claude follows a role:

- You can review the role spec to know exactly what Claude will and won't do.
- You can trust that tests will be written, because the role makes testing non-optional.
- You can pick up where you left off, because STATE.md tracks everything.
- You can make architectural decisions confidently, because Claude will ask instead of guessing.
- You can onboard to a project you haven't touched in weeks by reading STATE.md and ROADMAP.md.

This is the difference between "AI that writes code" and "AI that develops software."

## How Aire Works

Aire for Claude Code consists of:

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

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and working.
- A git repository for your project (or willingness to create one).
- The `claude/` directory from this repository.

### Step 1: Copy Aire into your project

Copy the `claude/` directory into your project repository:

```
your-project/
  claude/
    claude.role.base.md
    claude.git-hygiene.md
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
        CLAUDE.md
```

You do NOT need the entire Aire repository — just the `claude/` directory with the governance specs and the AireSmith role.

### Step 2: Generate your project role

Copy the AireSmith CLAUDE.md to your project root:

```bash
cp claude/roles/aire-smith/CLAUDE.md ./CLAUDE.md
```

Start a Claude Code session. Claude will read CLAUDE.md and load the AireSmith role. Then describe the role you need:

```
I need a developer role for a Python web API. It uses FastAPI, PostgreSQL,
and SQLAlchemy. The project is a task management API. The role should cover
backend implementation, database schema, API endpoints, and tests. It should
NOT cover frontend, deployment, or infrastructure.
```

AireSmith will generate a role spec tailored to your project. Review it — this is the contract that will govern Claude's behavior. Edit it if needed. The role file goes in your project (e.g., `developer.role.md` at the root, or wherever you prefer).

### Step 3: Set up your project CLAUDE.md

Replace the AireSmith CLAUDE.md with one that points to your new project role. The generated role includes a CLAUDE.md — use that as your starting point. It should reference:

- Your project role file.
- STATE.md for state tracking.
- NORTHSTAR.md and ROADMAP.md for planning.
- The governance specs in `claude/`.

### Step 4: Initialize the project

Start a new Claude Code session with your project CLAUDE.md in place. Claude will:

1. Read CLAUDE.md and load the role.
2. Notice STATE.md doesn't exist and offer to create it.
3. Help you create NORTHSTAR.md (project vision, success criteria, guiding principles).
4. Help you create ROADMAP.md (milestones and outcomes).
5. Create sprints for the first milestone.
6. Begin work.

For existing projects, the initialization is similar but Claude will audit existing code against the new standards and build STATE.md from the current project state.

## The Governance Specs

Here's what each spec does and why it matters:

### claude.role.base.md
The base template for all roles. Defines the sections every role must have, the verification checklist, and the relational primitives (behavioral rules for how Claude interacts with you). You rarely edit this directly — AireSmith uses it to generate roles.

### spec-spec.md
Defines how specs are structured. Every spec in your project follows this standard. Key feature: the mandatory **Test Strategy** section — every spec must define what tests are needed, making testing a design decision, not an afterthought.

### claude.git-hygiene.md
Git branching, commit conventions, and promotion rules. Two profiles: **Profile A** (docs/policy, no tests needed) and **Profile B** (software, tests required before merging to main). Each sprint maps 1:1 to a git branch.

### state-tracker-spec.md
Defines STATE.md — a human-readable project state file at the repo root. This is your primary way to see where things stand. Claude maintains it; you can read or edit it at any time.

### state-pack-spec.md (Session Context)
Defines what Claude loads at the start of each session to restore context. STATE.md first, then role spec, then git state, then whatever else is relevant.

### decision-log-spec.md
Structured decision recording. Three classes: **A** (free to decide), **B** (decide and log), **C** (escalate to you). Decisions are stored as JSON files — searchable, auditable, and version-controlled.

### planning-spec.md
Defines three planning artifacts: **NORTHSTAR.md** (vision and principles), **ROADMAP.md** (milestones and outcomes), and **sprint files** (granular work units). Planning is outcome-bound, not time-bound.

### project-init-spec.md
The bootstrap sequence: how to go from "I have role files" to "Claude is working." Covers CLAUDE.md setup, directory scaffolding, and the planning phase.

### documentation-spec.md
Requirements for user-facing documentation. README always required. HOWTOs, reference docs, manpages per project type. Also defines the **spec index** (specs/INDEX.md) — a table of contents for all specs.

## Tips

### Switching roles mid-project
If your project needs multiple roles (e.g., an architect and a developer), keep both role files in the project. Swap CLAUDE.md to point to the role you need for the current session. STATE.md provides continuity regardless of which role is active.

### Customizing governance
The governance specs are starting points. If your project doesn't need decision logging, remove it from the role. If you want different git conventions, edit claude.git-hygiene.md. The system is modular — use what helps, skip what doesn't.

### For existing projects
You don't need to start from scratch. Copy in the `claude/` directory, generate a role, and let Claude audit your existing code against the new standards. It will identify gaps in specs, tests, and documentation and help you close them incrementally.

### When Claude pushes back
If Claude halts and asks for clarification, that's the role working correctly. The role is designed to make Claude stop when things are ambiguous rather than guess. Answer the question and Claude will proceed. If Claude halts too often, your specs may need more detail — that's useful signal.

## File Inventory

```
claude/
  MANUAL.md                 # This file
  claude.role.base.md       # Base role template
  claude.git-hygiene.md     # Git branching and commit standards
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
      CLAUDE.md             # CLAUDE.md for AireSmith sessions
```
