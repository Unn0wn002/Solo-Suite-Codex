---
name: security-rls-test
description: "Test Supabase RLS policies with realistic user roles. Use when the user explicitly invokes $security-rls-test or asks for this security rls-test workflow."
---

# Security RLS Test

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $authz-security-reviewer in rls-test mode, with $connector-auditor for the live Supabase schema/policies when available. Apply it to the user's supplied arguments and surrounding request.

For each table: confirm RLS is enabled, then test anon / owner / non-owner / admin against SELECT/INSERT/UPDATE/DELETE and confirm owner/tenant isolation. Give pass/fail per policy and the SQL to fix gaps.

## Output — evidence-based audit format
Never just "good" or "bad" — every claim names its proof. If nothing was actually inspected for an area, say "not checked", don't guess. End with exactly:

```
## Status
PASS / WARNING / FAIL

## Evidence Checked
- File: …
- Config: …
- Page: …
- Command output: …
- Screenshot: …
- Connector data: …
(only the lines that apply — but at least one; no evidence, no finding)

## Findings
1. …
2. …

## Risk Level
Low / Medium / High / Critical

## Required Fixes
1. …

## Suggested Tasks
→ `.solo/tasks.md` entries with stable T-IDs

## Verification Steps
1. …

## Next Recommended Skill
$database-audit — use it to investigate verified database authorization findings.
```
