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
- **Versioning scheme requirement** for developer roles. Developer roles must now define and document a project-appropriate version-numbering convention (e.g., SemVer, CalVer, build numbers) and apply it consistently to releases, tags, and artifacts. The specific scheme is not prescribed — each role chooses what fits its project's release model.
- **Version-in-branch-slug** convention in git hygiene specs. Work branch slugs for developer roles must incorporate the project version (e.g., `work/2025-12-20T213045Z/1.3.0-add-auth-flow`), making branches sortable by release and immediately traceable to the version they target. Stage branch slugs must match.
- AireSmith updated to embed the versioning scheme requirement when generating new developer/implementation roles.

### Changed
- `claude/claude.role.base.md` (v0.2.0): added versioning scheme normative requirement (developer roles only) and reinforcement.
- `claude/claude.git-hygiene.md` (v0.2.0): added version-in-slug requirement for work branches and slug-matching for stage branches (developer roles only).
- `templates/role.base.md` (v0.3.1): added versioning scheme normative requirement (developer roles only) and reinforcement.
- `templates/team.git-hygiene.md` (v0.1.0): added version-in-slug requirement for work branches and slug-matching for stage branches (developer roles only).
- `aire-smith.role.md` (v0.4): added instruction to embed versioning scheme requirement in generated developer roles.
