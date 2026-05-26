# Aire: Attention to Context

[![GitHub release](https://img.shields.io/github/v/release/mr-kelley/aire?sort=semver)](https://github.com/mr-kelley/aire/releases)

> *Paying attention to context. From attention, to context.*

Aire is an open-source governance framework for **human-AI collaborative development**. It provides structured role definitions, relational primitives, and specification-driven workflows that keep humans and AI agents grounded, coherent, and drift-free across sessions and projects.

The mature implementation targets **Claude Code** (Anthropic's CLI agent) and has been used to ship projects across FPGA hardware design, telecom cloud orchestration, ERP systems, AI model orchestration, and more — all through structured human-AI partnership.

---

## What Aire Provides

**For Claude Code** (the primary, production-tested implementation):

- **9 governance specs** — spec-first development, git hygiene, state tracking, session context, decision logging, planning, project initialization, testing, and documentation.
- **AireSmith** — a role generator that produces project-specific AI roles tailored to your domain, constraints, and workflow.
- **A user manual** — the system, the rationale behind roles, and a getting-started workflow.

**To get started:** see [claude/MANUAL.md](./claude/MANUAL.md).

**For any platform** (base templates):

- Role templates and relational primitives that work with any AI tool — Claude, Gemini, local models, or any system that accepts natural-language context.
- See [Quickstart (Base Templates)](#quickstart-base-templates) below.

---

## Who Aire is For

- **Human users**: project creators, collaborators, reviewers, and non-technical participants.
- **AI users**: roles that benefit from context constraints.

Both participate together. Aire ensures that humans and AIs work side by side with equal clarity about roles, boundaries, and context.

---

## How to Start

If you are a **human user**:
1. Using Claude Code? Start with [claude/MANUAL.md](./claude/MANUAL.md).
2. Using another platform? Read [HOWTO.md](./HOWTO.md) and see [Quickstart (Base Templates)](#quickstart-base-templates).

If you are an **AI user**:
- Treat this README as your primary orientation.
- Read the Files section and request copies as needed.
- Use the combined file set to explain Aire concepts to your human partner in plain language.
- Extend or adapt Aire specs as needed.
- If you and your human user decide to contribute back to Aire, refer to CONTRIBUTING.md for guidance.

---

## Why Aire?

Modern AI systems succeed or fail on **context**. Without management, drift and incoherence are inevitable. Aire provides:

- **Framework**: encapsulates lessons learned while building real projects through human-AI collaboration.
- **Guarding**: boundaries and constraints that enforce rules and prevent drift across sessions.

---

## Core Concepts

- **Role Specifications** — structured definitions that give an AI agent its purpose, scope, constraints, and verification criteria for a specific project.
- **Relational Primitives** — a minimal set of behavioral constraints (Frame, Polarity, Trust, Release, Insistence, Completion) that keep AI roles focused and self-correcting.
- **Governance Specs** — rules for how work is done: spec-first development, git hygiene, state tracking, decision logging, planning, and documentation.

---

## Quickstart (Base Templates)

If you're using Claude Code, start with the [Claude Code manual](./claude/MANUAL.md) instead.

For other platforms or manual setup:

1. Clone the repo locally.
2. Copy `templates/role.base.md` into your project.
3. Fill out the template with your project's specifics.
4. Hand the resulting file to your AI tool along with any optional governance files.

For a step-by-step beginner's guide, see [HOWTO.md](./HOWTO.md).

---

## AI2AI: Multi-Model Communication (Optional)

Aire includes a **Context Envelope** spec designed for workflows where multiple AI models collaborate — for example, a coding model, an architect model, and a multimodal model working together on the same project. This is most relevant for local multi-model setups using tools like Ollama, where specialized smaller models handle different roles.

AI2AI is **opt-in**, **extensible**, and **forkable**. It is not needed for single-agent workflows (including Claude Code, which handles all roles within a single agent session).

See [AI2AI Spec](./templates/ai2ai-directive-spec.md) for details.

---

## Contributing

Aire is new, and stewardship matters. Contributions are welcome through **issues** and **discussions**. Pull requests will be accepted selectively until the v0.2 cycle.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

---

## License

Apache 2.0 — business-friendly, with explicit patent grant.

---

## Files

### Claude Code (recommended starting point)
- `claude/MANUAL.md` — user manual and getting started guide
- `claude/roles/aire-smith/` — role generator for Claude Code projects
- `claude/*.md` — governance specs (spec-first, git hygiene, state tracking, decisions, planning, docs, testing)

### Base System (generic, any platform)
- `templates/role.base.md` — base role template
- `primitives/relational-primitives.md` — relational primitive definitions

### Optional
- `templates/ai2ai-directive-spec.md` — AI2AI messaging spec (multi-model use cases)

---

## Naming Note

*Aire* (Irish: **attention, care, watchfulness**) is pronounced **ARR-eh**.
It also evokes *Éire* (Ireland) and *attention* in LLMs.
Both meanings reflect Aire's purpose:
**Paying attention to context. From attention, to context.**
