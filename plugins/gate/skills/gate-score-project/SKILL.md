---
name: gate-score-project
description: "Score the project across the same 14 production-readiness categories and fixed 140-point formula without issuing a launch status. Use when the user explicitly invokes $gate-score-project or asks for a trend score before the enforced production gate."
---

# Score the project

Use `$production-readiness-reviewer` in score-only mode. Score the canonical 14 categories from 0 to 10, report the total out of 140, and calculate `round(total / 140 * 100)`.

Require evidence for every score and an evidence-backed N/A reason for any inapplicable category. An all-N/A review is `INSUFFICIENT EVIDENCE`, never `SCORED`. Run provider checks only when `.solo/stack.md` records the provider. List missing, over-age, different-run/gate/commit/environment, or unnamespaced evidence as risks worth zero; do not invent a pass.

Write `solo-suite/score-evidence-v1` using the reviewer skill's `references/score-evidence-v1.schema.json`. Include the exact `run_id`, `gate_id`, commit, environment, reviewer, timestamps, 14 category records, fixed-denominator scores, `assessment_status`, and risks. Use only `SCORED` or `INSUFFICIENT EVIDENCE`; never add `launch_status` or a GO/NO-GO decision.

Validate it before reporting:

```text
<python> <resolved-plugin-root>/skills/production-readiness-reviewer/scripts/validate_gate_evidence.py <evidence.json> --root <project-root> --run-id <run-id> --gate-id <gate-id> --commit <sha> --environment <name> --mode score --max-age-hours <hours>
```

Record the dated score and evidence path in `.solo/project.md` only after the user has authorized project-memory writes. Recommend `$gate-production-ready` when an enforced launch verdict is needed.
