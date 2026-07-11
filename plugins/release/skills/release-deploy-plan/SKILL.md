---
name: release-deploy-plan
description: "Plan a safe, ordered, low-risk deployment with post-deploy verification Use when the user explicitly invokes $release-deploy-plan or asks for this release deploy-plan workflow."
---

# Release Deploy Plan

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $devops-engineer in deploy-plan mode for the user's supplied arguments and surrounding request.

Read .solo/architecture.md for what's deployed where. Produce ordered steps: backup ->
migrate (backward-compatible, before/separate from dependent code) -> deploy -> verify
health -> shift traffic -> smoke test. Prefer simple + safe (rolling/blue-green/platform-
managed) over stop-start; graceful shutdown; migrations safe against live traffic; sane
timing. Specify exactly what to check post-deploy. Deep mechanics -> site-doctor
deployment-review. Record what shipped in .solo/.


Record the plan in **`.solo/release.md`**.

## Output
End with the 7-part contract: **Summary · Findings/Work done · Risks · Required fixes · Suggested tasks** (→ `.solo/tasks.md`, stable T-IDs) **· Verification · Next skill** (exact skill invocation).
