---
name: site-doctor-audit-mobile
description: "Audit the mobile experience - responsive layout, touch targets, mobile performance, PWA Use when the user explicitly invokes $site-doctor-audit-mobile or asks for this site-doctor audit-mobile workflow."
---

# Site Doctor Audit Mobile

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $mobile-audit on the user's supplied arguments and surrounding request.

If no URL was provided, ask for it. Run the mobile checker, then review
viewport/responsive (test 320/375/768px), touch usability, mobile performance
on throttled conditions, legibility, and PWA readiness. Rank by how badly each
issue blocks a mobile user completing the core task.

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
$mobile-audit — use it to investigate and prioritize verified mobile findings.
```
