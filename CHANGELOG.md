<!--
Licensed under the Apache License, Version 2.0 (the "License");
http://www.apache.org/licenses/LICENSE-2.0
-->
# Changelog
All notable changes to this project will be documented in this file.

The format is based on **Keep a Changelog**, and this project adheres to **Semantic Versioning**.

## [0.1.0] — 2025-08-31
### Added
- Initial aligned import of Aire with deterministic context orchestration framing.
- Public **README** (human+AI users), **Product Description**, and **AI2AI v1 (opt-in)** spec.
- **Architect** role (policy enforcement for license headers; Trace Manifest duties).
- **Policies**: `index.md` and `license_headers.md`.
- Repository hygiene: `.gitignore`, `.gitattributes`, initial docs layout.

### Notes
- AI2AI is optional; Aire remains fully functional without it.
- Trace Manifest structure is intentionally flexible for early tester feedback.

[0.1.0]: https://github.com/mr-kelley/aire/releases/tag/v0.1.0

## [0.1.1] — 2025-09-18
### Added
- Public **HOWTO** for non-technical human users and for AI users.
- Updated **README** to include reference to **HOWTO**.

[0.1.1]: https://github.com/mr-kelley/aire/releases/tag/v0.1.1

## [Unreleased]
### Added
- **GitHub Issues governance spec** (`claude/github-issues-spec.md`). Optional, opt-in spec that bridges GitHub Issues to existing Aire planning, decision-logging, and git hygiene governance for projects with collaborative workflows. Defines Issue lifecycle (creation → triage → self-assignment → sprint translation → work → closure), role permissions (`gh` CLI: read/close permitted, create/edit/triage human-only), traceability conventions (Issue ↔ commits, PRs, decision log, sprint files), and edge case handling.
- AireSmith updated to support optional GitHub Issues integration in generated roles — only when explicitly requested by the user.
