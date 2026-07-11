---
name: git-commit-plan
description: "Review changed files and propose clean, atomic, Conventional-Commit commits. Use when the user explicitly invokes $git-commit-plan or asks for this git commit-plan workflow."
---

# Git Commit Plan

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $git-workflow-manager in commit-plan mode. Apply it to the user's supplied arguments and surrounding request.

Inspect `git status`/`git diff`, group the changes into logical atomic commits with Conventional-Commit messages, and flag anything that must not be committed (secrets, `.env`, build output, large binaries). Give copy-paste `git add`/`commit` commands. Don't commit unless asked.

## Output
End with the 7-part contract: **Summary · Findings/Work done · Risks · Required fixes · Suggested tasks** (→ `.solo/tasks.md`, stable T-IDs) **· Verification · Next skill** (exact skill invocation).
