---
name: git-release-notes
description: "Generate user-facing and technical release notes since the last release. Use when the user explicitly invokes $git-release-notes or asks for this git release-notes workflow."
---

# Git Release Notes

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $git-workflow-manager in release-notes mode. Apply it to the user's supplied arguments and surrounding request.

From commits since the last tag plus `.solo/decisions.md` and Done tasks, produce two views: **user-facing** (new / fixed / changed, plain language) and **technical** (notable changes, migrations, breaking changes, upgrade steps).

## Output
End with the 7-part contract: **Summary · Findings/Work done · Risks · Required fixes · Suggested tasks** (→ `.solo/tasks.md`, stable T-IDs) **· Verification · Next skill** (exact skill invocation).
