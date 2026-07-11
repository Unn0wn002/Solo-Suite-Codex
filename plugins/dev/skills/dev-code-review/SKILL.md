---
name: dev-code-review
description: "Review a change for correctness, security, readability, design, performance, tests Use when the user explicitly invokes $dev-code-review or asks for this dev code-review workflow."
---

# Dev Code Review

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $code-reviewer for the user's supplied arguments and surrounding request.

Read the change in context (.solo/ tasks + acceptance criteria + architecture; nearby
code for conventions). Prioritize correctness and edge cases, then security, readability,
design fit, performance, and test coverage. Label findings Must-fix / Should-fix /
Consider, each specific and actionable with the reasoning. Be honest, not a rubber stamp.
Route security depth to security-reviewer / site-doctor; test depth to qa-engineer.

Use $repo-analyzer for structural context on what the change touches.

## Output
End with the 7-part contract: **Summary · Findings/Work done · Risks · Required fixes · Suggested tasks** (→ `.solo/tasks.md`, stable T-IDs) **· Verification · Next skill** (exact skill invocation).
