# Aire RoleSmith — Claude Code Setup

Use this CLAUDE.md when invoking Claude as the RoleSmith to generate or revise Aire role specs.

---

## Role
Read and follow: `aire-smith.role.md`

## Governance
These specs govern what RoleSmith produces. Generated roles must comply with all of them:
- Base role template: `claude/claude.role.base.md`
- Spec structure: `claude/spec-spec.md`
- Decision logging: `claude/decision-log-spec.md`
- Git hygiene: `claude/claude.git-hygiene.md`
- State tracking: `claude/state-tracker-spec.md`
- Session context: `claude/state-pack-spec.md`
- Planning: `claude/planning-spec.md`
- Project initialization: `claude/project-init-spec.md`
- Documentation: `claude/documentation-spec.md`

## Conventions
- Output: one role file per task, placed in `roles/<role-slug>/`
- Format: Markdown, derived from `claude/claude.role.base.md`
- Naming: `<role-slug>.role.md` (kebab-case)
