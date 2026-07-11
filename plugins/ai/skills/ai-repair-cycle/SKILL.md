---
name: ai-repair-cycle
description: "Take failed AI output, diagnose why it failed, and rewrite the prompt. Use when the user explicitly invokes $ai-repair-cycle or asks for this ai repair-cycle workflow."
---

# AI Repair Cycle

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $ai-output-auditor in repair-cycle mode. Apply it to the user's supplied arguments and surrounding request.

Diagnose the root cause of the failure (missing context? ambiguous ask? wrong model? unstated constraint?) and produce a rewritten prompt that removes that cause so the next attempt succeeds.

## Output
End with the 7-part contract: **Summary · Findings/Work done · Risks · Required fixes · Suggested tasks** (→ `.solo/tasks.md`, stable T-IDs) **· Verification · Next skill** (exact skill invocation).
