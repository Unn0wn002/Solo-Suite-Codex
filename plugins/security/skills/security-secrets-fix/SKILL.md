---
name: security-secrets-fix
description: "Detect exposed secrets and provide rotation/fix steps. Use when the user explicitly invokes $security-secrets-fix or asks for this security secrets-fix workflow."
---

# Security Secrets Fix

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $security-review (site-doctor) to find and fix exposed secrets — do a lighter inline version following the same priorities if site-doctor isn't installed, and say so. Apply it to the user's supplied arguments and surrounding request.

Scan the repo (and history) for committed secrets/keys, then for each: rotate, remove from code/history, move to env vars, and prevent recurrence (gitignore, pre-commit hook). Never print full secret values.

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
None — complete this remediation only after the secret is rotated, removed from history as appropriate, and verification evidence is recorded.
```
