<!--
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy at http://www.apache.org/licenses/LICENSE-2.0
-->
# Contributing to Aire

Thank you for your interest in Aire! This document explains how to propose changes and participate in the project.

Aire is an open-source framework for **deterministic context orchestration and role-to-role collaboration**, built on **human- and AI-readable specifications**.

## Code of Conduct
By participating, you agree to uphold our [Code of Conduct](./CODE_OF_CONDUCT.md).

## Security
Do **not** file security issues in public. Please follow our [Security Policy](./SECURITY.md).

## License & IP
- All contributions are under the project’s **Apache 2.0** license.
- We use a **Developer Certificate of Origin (DCO)** model instead of a CLA.
  - Sign your commits with `Signed-off-by: Your Name <email>` or use `git commit -s`.

## How to Contribute
1. **Discuss first (recommended):** Open an issue to propose changes or ask questions.
2. **Fork & branch:** Create a feature branch from `main`.
3. **Make changes:** Follow style guides below and ensure license headers are present (see **Policies**).
4. **Tests & docs:** Add/update tests and documentation where applicable.
5. **Pull Request:** Submit a PR with a clear description, linking to the related issue.

### PR Review
- Reviews aim for clarity, determinism, and human-readability.
- Maintainers may request changes to align with policies and project goals.
- Merges require at least one maintainer approval.

## Project Structure Overview
- `roles/` - Role specifications (human-first `.txt`).
- `policies/` - Project policies; see `policies/index.md`.
- `docs/` - Concepts, guides, reference specs, and product docs.
- `examples/` - Example bundles and role sets.

## Policies (Required Reading)
The Architect role enforces policies during builds. At minimum:
- **License headers:** Every new or modified file must include the short Apache header unless explicitly exempt.
  - See `policies/license_headers.md` and `policies/index.md`.

## Style Guides
- **Docs/specs:** Prefer concise, human-readable prose. Avoid jargon.
- **Filenames:** `kebab-case` for docs; `snake_case` for code.
- **Commits:** Conventional, actionable messages. Example:
  - `feat: add photographer role`
  - `fix: correct Trace Manifest field names`
  - `docs: clarify AI2AI opt-in language`
- **SemVer:** We target semantic versioning once v1.0 is reached.

## RFCs & Larger Changes

For major changes to **project specifications** (not routine role definitions) or to **governance**, open an issue titled **“RFC: …”** that includes:

- **Problem statement** — what’s broken or missing and why it matters
- **Proposed design** — concise description of the change
- **Scope of impact** — affected areas (e.g., AI2AI envelope, `aire.yaml` schema, policy framework)
- **Alternatives considered** — and why they’re not chosen
- **Migration plan** — how users move from old to new
- **Policy/role impacts** — if this affects enforcement or requires role updates

**Notes**
- “Project specifications” means Aire’s framework-level specs and protocols.
- “Role definitions” are the human-readable overlays in `/roles/*.txt`. These typically do **not** require RFCs unless they introduce breaking behavior or policy conflicts.


## Releases
- Changelog updates follow **Keep a Changelog** style.
- Release notes summarize major changes, policy updates, and compatibility notes.

## Getting Help
Open an issue with the `question` label or join project discussions.

