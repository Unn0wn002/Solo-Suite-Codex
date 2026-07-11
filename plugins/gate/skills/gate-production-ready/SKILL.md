---
name: gate-production-ready
description: "Run the explicit Solo Suite production gate across exactly 14 scored categories, validate current machine-readable evidence, and return only BLOCKED, SAFE WITH WARNINGS, or SAFE TO LAUNCH. Use when the user explicitly invokes $gate-production-ready or requests a launch verdict."
---

# Run the production gate

Use `$production-readiness-reviewer`. Identify the exact repository, `run_id`, `gate_id`, commit SHA, target environment, reviewer, and evidence expiration before evaluating anything.

Score Product, Architecture, Design, Frontend, Backend, Database, Security, Testing, Performance, SEO, Analytics, Deployment, Monitoring, and Documentation from 0 to 10. Report the total out of 140 and calculate `round(total / 140 * 100)`.

Instantiate and validate the room before scoring. Write its predeclared `solo-suite/project-profile-v1` artifact and `solo-suite/gate-evidence-v1`, then validate with `--mode production`, `--room`, `--run-id`, and `--gate-id`. Reject missing, changed, over-age, expired, unnamespaced, different-run, different-gate, different-commit, or different-environment evidence. The validator independently revalidates the room's exact-current before-deploy result and requires `GO`; absence or any other decision blocks production. Run vendor-specific checks only when `.solo/stack.md` records that vendor.

```text
<python> <resolved-plugin-root>/skills/production-readiness-reviewer/scripts/validate_gate_evidence.py <evidence.json> --root <project-root> --room <prepared-room.json> --run-id <run-id> --gate-id <gate-id> --commit <sha> --environment <name> --mode production
```

Return only `BLOCKED`, `SAFE WITH WARNINGS`, or `SAFE TO LAUNCH`. A hard blocker overrides the score. List every blocker and warning with evidence, owner, remediation skill, and verification step. Do not use GO/NO-GO wording for this production gate and do not deploy, publish, merge, or mutate production.
