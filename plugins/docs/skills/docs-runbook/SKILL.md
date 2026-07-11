---
name: docs-runbook
description: "Write an operational runbook for a task or service (ops, failures, rollback, escalation). Use when the user explicitly invokes $docs-runbook or asks for this docs runbook workflow."
---

# Docs Runbook

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $documentation-writer in runbook mode. Apply it to the user's supplied arguments and surrounding request.

Produce an operational runbook: what it does and when to run it, prerequisites/access, exact step-by-step operating procedure, how to verify success, common failures and their fixes, rollback/recovery, and escalation. Keep steps copy-pasteable.

## Output
End with the 7-part contract: **Summary · Findings/Work done · Risks · Required fixes · Suggested tasks** (→ `.solo/tasks.md`, stable T-IDs) **· Verification · Next skill** (exact skill invocation).
