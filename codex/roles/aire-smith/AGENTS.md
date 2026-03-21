# Aire RoleSmith — Codex Setup

Use this AGENTS.md when invoking Codex as the RoleSmith to generate or revise Aire role specs.

---

## Role
Read and follow: `aire-smith.role.md`

## Governance
These specs govern what RoleSmith produces. Generated roles must comply with all of them:
- Base role template: `codex/codex.role.base.md`
- Spec structure: `codex/spec-spec.md`
- Decision logging: `codex/decision-log-spec.md`
- Git hygiene: `codex/codex.git-hygiene.md`
- State tracking: `codex/state-tracker-spec.md`
- Session context: `codex/state-pack-spec.md`
- Planning: `codex/planning-spec.md`
- Project initialization: `codex/project-init-spec.md`
- Documentation: `codex/documentation-spec.md`

## Conventions
- Output: one role file per task, placed in `roles/<role-slug>/`
- Format: Markdown, derived from `codex/codex.role.base.md`
- Naming: `<role-slug>.role.md` (kebab-case)
