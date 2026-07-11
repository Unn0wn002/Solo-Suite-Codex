---
name: git-pr-review
description: "Review a PR or branch diff for correctness, security, tests, docs, and risk. Use when the user explicitly invokes $git-pr-review or asks for this git pr-review workflow."
---

# Git Pr Review

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $git-workflow-manager in pr-review mode. Apply it to the user's supplied arguments and surrounding request.

Review across correctness, security, tests, docs, and risk. Use $repo-analyzer for context and $authz-security-reviewer / $security-review for the security pass; pull live PR data via $connector-auditor (GitHub) when available. End with a verdict: approve / approve-with-nits / request-changes, plus specific line-level asks.

## Output
End with the 7-part contract: **Summary · Findings/Work done · Risks · Required fixes · Suggested tasks** (→ `.solo/tasks.md`, stable T-IDs) **· Verification · Next skill** (exact skill invocation).
