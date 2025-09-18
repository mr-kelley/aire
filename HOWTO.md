# HOWTO: Create Roles (and Teams) in Aire

> **Audience:** Beginner.  
> **If you’re advanced:** See `README.md` for a more succinct reference.
> **Read this entire page before you begin.**

---

## Best Practices (quick hits)

- **Keep it small.** One clear responsibility per role. Split early.
- **Ask for clarifications.** Put this request at the **end** of your prompt.
- **Name roles clearly.** Choose names that reveal function, not flair.
- **One role ↔ one project / gem.** Never co‑locate roles.
- **Revise by replacement.** When you update, replace the entire instructions block.
- **Document changes.** Keep a simple change log (date, reason, version).

---

## What you’ll need

- `README.md` (project root)
- `templates/role.base.md`
- `primitives/relational-primitives.md`

**For a team of roles**, you’ll also want:

- `templates/team.base.md`
- `templates/ai2ai-directive-spec.md`

---

## Part A — Single Role

### 1) Prepare a prompt
In a new chat with your AI of choice:

1. Attach:
   - `README.md`
   - `templates/role.base.md`
   - `primitives/relational-primitives.md`
2. Write **one or two sentences** describing exactly what the new role should do.  
   - If it takes more than 1–2 sentences, **split it into multiple roles**.
3. End your prompt by **asking the AI to request clarifications** where needed.

> Example closer: “If anything is ambiguous, ask me clarifying questions before you draft the role.”

Send the prompt.

### 2) Instantiate the role
1. When the AI returns the role file, **save it** locally.
2. Create a **new project / gem** (or your platform’s equivalent).
3. **Copy the entire role file** and **paste it into the project / gem’s instructions**.
4. **Save** the project / gem.

Your new role is now ready. Begin work.

### 3) Iterate if needed
If the role’s behavior isn’t what you want:

1. Return to the original chat where you created the role.  
2. **Describe the discrepancies** (what you expected vs. what happened).  
3. Ask for an **updated role file**.  
4. In your project / gem, **replace the entire instructions** with the new version.

> Tip: Replace wholesale; don’t mix versions. Keep roles small and single‑purpose.

---

## Part B — A Team of Roles (Roles that work together)

### 1) Prepare a prompt for the team
In a new chat:

1. Attach **five files**:
   - `README.md`
   - `templates/role.base.md`
   - `templates/team.md` *(or `team.base.md`, depending on your repo)*
   - `templates/ai2ai-directive-spec.md`
   - `primitives/relational-primitives.md`
2. Write **1–2 sentences per role** describing what each role must accomplish.  
   - If any role needs more than two sentences, **split it**.
3. Ask the AI to:
   - **Generate one `role.<name>.md` per role**, each minimal and focused.
   - **Generate a `team.md`** that explains coordination, handoffs, and when to use AI2AI directives.
   - **List which files each role needs to receive** during handoffs.

### 2) Instantiate the team
1. **Create one project / gem per role.**  
   > **Vital:** Do **not** run two roles in the same project / gem.
2. For each role:
   - **Paste that role’s file** into its project / gem’s instructions.
   - Follow any **handoff / file‑sharing guidance** the team file specifies.
3. Start work. Use the team’s coordination rules (from `team.md`) to move artifacts between roles.

### 3) Iterate the team
When behavior is off:

- **Return to the team-creation chat**, explain what’s mismatching, and request updated role(s) and/or `team.md`.  
- **Update only the affected roles**, or the team file if coordination is the issue.


