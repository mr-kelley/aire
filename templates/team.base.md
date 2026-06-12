---

team:

version: 0.1
maintained_by: <name/role>
domain_tags: [system, governance, collaboration]
status: draft | stable | deprecated
license: Apache-2.0
optional_feature: true
-----------------------

# Purpose

<why this team exists; link governing specs, project objectives>

# Composition

- Roles: [list of roles with file paths/links]
- Membership type: fixed | dynamic
- Topology: freeform description (hierarchical, flat, peer-net, etc.)

# Collective Relational Implementation (Optional — remove if unused)

If this section is implemented, reference `primitives/relational-primitives.md` in the Aire repo. These are **normative references only when this section is present**.

Note: Teams should not redefine primitives; they should contextualize how the primitives manifest collectively across roles. This helps avoid role dilution and keeps scope boundaries intact.

**Frame** — how the team maintains collective purpose and boundaries.  
**Polarity** — how tension between roles is structured and mediated.  
**Trust** — how roles defer to each other within the team.  
**Release** — how the team avoids premature or duplicate action.  
**Insistence** — how the team ensures issues are raised and resolved.  
**Completion** — how the team signals group-level task or deliverable closure.

# Interfaces (Optional — remove if unused)

If AI2AI is chosen as the communication interface, reference `templates/ai2ai-directive-spec.md` in the Aire repo. This is a **normative reference only when present**.

Teams may also mix interfaces (e.g., AI2AI for some flows, ad-hoc text for others). Document the hybrid strategy here.

- Default AI2AI flows between roles (handoff, request, consensus, etc.)
- Cross-role message expectations (broadcast, chain, hub/spoke)
- Optional escalation routes to humans or governance roles

# Inputs

- Shared specs, policies, ADRs (team-wide context)
- Role outputs that feed other roles

# Outputs

- Team-level deliverables (integrated artifacts, reports, consensus decisions)
- Trace Manifest fields:
  - team_index
  - collective summary
  - mapping: role_index → actor_index

# Governance & Halt Conditions

- Shared halt rules (e.g., stop if polarity breaks, or if any role escalates a governance/safety issue)
- Escalation paths to external owners (spec, policy, safety)

# Verification

- Criteria for team-level acceptance
- Evidence required (e.g., consensus ACKs, checksum manifests from each role)

# Change Control

- Update version and provenance on every change
- Migration notes for membership or topology changes

# Appendices

- Example team composition
- Example AI2AI topologies

