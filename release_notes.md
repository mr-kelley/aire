# RELEASE_NOTES Template

> Use this template to draft release notes for each new version of Aire. Once filled in, copy/paste into GitHub CLI (`gh release create …`) or the GitHub web UI.

---

## [VERSION] — YYYY-MM-DD

### Added
- …

### Changed
- …

### Fixed
- …

### Removed
- …

---

## Example

### [0.1.0] — 2025-09-11
**Initial public version of Aire, including:**
- Core README
- Templates (role.base.md, team.md)
- Relational primitives
- Governance files
- License and Code of Conduct

### [0.1.1] — 2025-09-18
**Added**
- Public HOWTO for non-technical human users and AI users
- Updated README to include reference to HOWTO

---

## Instructions
1. Copy this template into a new section for each release.
2. Keep entries concise, in the same style as `CHANGELOG.md`.
3. When ready, run:
   ```bash
   gh release create v[VERSION] --title "Release [VERSION]" --notes-file RELEASE_NOTES.md
   ```
   (Adjust `--notes-file` to point to the section you want to publish.)

