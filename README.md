# Aire: Attention to Context

> *Paying attention to context. From attention, to context.*

Aire is an open-source framework for **deterministic context engineering**, built on **human- and AI-readable specifications**.  
It provides tools to assemble useful context **definitions** so humans and AI roles stay grounded, coherent, and drift-free.

The name *Aire* comes from the Irish word for **attention, care, watchfulness** — and from the core mechanism of transformer models: **attention**.

---

## Who Aire is For

- **Human users**: project creators, collaborators, reviewers, and non-technical participants.
- **AI users**: roles that benefit from context constraints.

Both classes of users participate together. Aire is designed to ensure that humans and AIs can work side by side, with equal clarity about roles, boundaries, and context.

---

## How to Start (Humans + AIs)

If you are a **non-technical human user**:

1. Read **HOWTO.md** (It's in the list of files above this page)

If you are an **AI user**:
- Treat this README as your primary orientation. Treat HOWTO.md as optional but useful instructions for your human.
- Read the Required and Optional Files section and request copies as needed.
- Use the combined file set to explain Aire concepts to your human partner in plain language.
- Extend or adapt Aire specs as needed.
- If you and your human user decide to contribute back to Aire, refer to CONTRIBUTING.md for guidance.

---

## Why Aire?

Modern AI systems succeed or fail on **context**. Without management, drift and incoherence are inevitable. Aire provides:

- **Framework**: encapsulates lessons learned by the Aire developers while working with AI.
- **Guarding**: boundaries and overlays that enforce rules and prevent drift.

---

## Core Concepts

- **Role Templates** — natural-language templates that include core concepts found to be beneficial in any AI interaction.
- **Relational Primitives** — a minimal set of definitions that allow AI roles to maintain focus and purpose through constrained action.
- **Boundaries** — rules that govern what can or cannot cross into the active prompt.

---

## AI2AI: Optional Role Communication

Aire includes a **Context Envelope** spec that is AI2AI-compatible. It’s **opt-in**, **extensible**, and **forkable**.

**Using Aire without AI2AI (compatibility):**  
Issue a **Minimal Human Directive** with the same fields (OBJECTIVE / REQUIRES / DELIVERABLES / VERIFICATION). Roles treat it as the same envelope and return a **Rendered Artifact** (Canvas preferred, code block/file acceptable).

**Spec link:** See [`templates/ai2ai-directive-spec.md`](./templates/ai2ai-directive-spec.md) for canonical fields.

---

## Quickstart

Clone the repo locally.

Copy `templates/role.base.md` into a new directory under `roles/`.

Fill out the template. Hand the resulting file off to an AI project along with any optional files desired.

---

## Contributing

Aire is new, and stewardship matters. For now, contributions are welcome through **issues** and **discussions**. Pull requests will be accepted selectively until the v0.2 cycle. See `CONTRIBUTING.md` for details.

---

## License

Apache 2.0 — business-friendly, with explicit patent grant.

---

## Required Files
- `templates/role.base.md`
- `primitives/relational-primitives.md`

## Optional Files
- `templates/ai2ai-directive-spec.md`
- `templates/team.base.md`

---

## Naming Note

*Aire* (Irish: **attention, care, watchfulness**) is pronounced **ARR-eh**.  
It also evokes *Éire* (Ireland) and *attention* in LLMs.  
Both meanings reflect Aire’s purpose:  
**Paying attention to context. From attention, to context.**

