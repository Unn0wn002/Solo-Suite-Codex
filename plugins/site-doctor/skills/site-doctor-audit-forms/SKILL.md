---
name: site-doctor-audit-forms
description: "Audit web forms - usability, validation, accessibility, conversion, security, spam protection Use when the user explicitly invokes $site-doctor-audit-forms or asks for this site-doctor audit-forms workflow."
---

# Site Doctor Audit Forms

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $forms-audit on the user's supplied arguments and surrounding request.

If no target was provided, ask which forms matter and what each is for. Walk
through completing each form, then review friction/design, validation & error
handling, accessibility, submission feedback, security & spam protection, and
mobile. Rank by conversion and access impact.

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
$forms-audit — use it to investigate verified form and privacy findings.
```
