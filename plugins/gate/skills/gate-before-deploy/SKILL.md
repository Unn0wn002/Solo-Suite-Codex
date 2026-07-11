---
name: gate-before-deploy
description: "Hard gate before deploy — blocks on missing env vars, skipped stack audits, no backup, no monitoring, or no rollback plan. Use when the user explicitly invokes $gate-before-deploy or asks for this gate before-deploy workflow."
---

# Gate Before Deploy

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $quality-gatekeeper in before-deploy mode. Apply it to the user's supplied arguments and surrounding request.

**Block the deploy if ANY is true:** env vars missing in the target (check `.solo/env-contract.md`) · stack audits not done for this release — Vercel/Supabase/Cloudflare, plus tags/payments where `.solo/stack.md` says they're in play · no backup with a tested restore · no monitoring live (`.solo/monitoring.md`) · no rollback plan (`.solo/release.md`). One missing item = NO-GO; record blockers in `.solo/risks.md`.

When an AgentRoom declares an evidence path, also emit and validate `solo-suite/phase-gate-evidence-v1` through the sibling `$quality-gatekeeper` validator using the prepared room. Bind its digest, exact ordered prerequisites, producer commands, run, gate, commit, environment, artifact digests, and maximum age; missing, substituted, over-age, or invalid evidence is `NO-GO` and must never route to production.

## Output
End with exactly:
- **Verdict** — GO / NO-GO (one missing blocker = NO-GO; never averaged away)
- **Blockers** — each failed check, with its evidence and the command that clears it
- **Passed checks** — with the evidence for each
- **Nits** — non-blocking improvements
- **Suggested tasks** → `.solo/tasks.md` (stable T-IDs); record open blockers in `.solo/risks.md`
- **Next skill** — what clears the top blocker, or the next phase command on GO
