---
name: repo-dependency-map
description: "Show internal module/service dependencies and import cycles. Use when the user explicitly invokes $repo-dependency-map or asks for this repo dependency-map workflow."
---

# Repo Dependency Map

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $repo-analyzer in dependency-map mode. Apply it to the user's supplied arguments and surrounding request.

Read the code (don't guess from names); use existing project tooling as ground truth.

Expected output: the most-depended-on modules (hubs), any import cycles with the exact files in the loop, and layering violations (e.g. UI importing data-access directly).

## Output
End with the 7-part contract: **Summary · Findings/Work done · Risks · Required fixes · Suggested tasks** (→ `.solo/tasks.md`, stable T-IDs) **· Verification · Next skill** (exact skill invocation).
