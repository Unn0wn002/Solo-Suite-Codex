---
name: spec-acceptance
description: "Create testable, pass/fail acceptance criteria for a feature. Use when the user explicitly invokes $spec-acceptance or asks for this spec acceptance workflow."
---

# Spec Acceptance

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $acceptance-criteria-writer in acceptance mode. Apply it to the user's supplied arguments and surrounding request.

Write Given/When/Then criteria that are objectively pass/fail, covering the happy path plus invalid input, empty/loading/error states, and permissions. Tie each to a stable `.solo/tasks.md` T-ID and note which `$test-e2e` will prove.

## Output
End with the 7-part contract: **Summary · Findings/Work done · Risks · Required fixes · Suggested tasks** (→ `.solo/tasks.md`, stable T-IDs) **· Verification · Next skill** (exact skill invocation).
