---
name: gate-before-code
description: "Hard gate before coding starts — blocks if PRD, acceptance criteria, architecture, contracts, design (for user-facing work), or task scope are missing. Use when the user explicitly invokes $gate-before-code or asks for this gate before-code workflow."
---

# Gate Before Code

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $quality-gatekeeper in before-code mode. Apply it to the user's supplied arguments and surrounding request.

**Block coding if ANY is true:** no PRD · no acceptance criteria · no architecture · no API/data contract (for API/schema work) · no env contract (for config/secret work) · no UX flow/design doc (`.solo/design.md`) for user-facing work · unclear task scope. Verify each against the actual `.solo/` files (name the file checked as evidence). One missing item = NO-GO, routed to its fix invocation.

When an AgentRoom declares an evidence path, also emit and validate `solo-suite/phase-gate-evidence-v1` through the sibling `$quality-gatekeeper` validator using the prepared room. Bind its digest, exact ordered prerequisites, producer commands, run, gate, commit, environment, artifact digests, and maximum age; missing, substituted, over-age, or invalid evidence is `NO-GO`.

## Output
End with exactly:
- **Verdict** — GO / NO-GO (one missing blocker = NO-GO; never averaged away)
- **Blockers** — each failed check, with its evidence and the command that clears it
- **Passed checks** — with the evidence for each
- **Nits** — non-blocking improvements
- **Suggested tasks** → `.solo/tasks.md` (stable T-IDs); record open blockers in `.solo/risks.md`
- **Next skill** — what clears the top blocker, or the next phase command on GO
