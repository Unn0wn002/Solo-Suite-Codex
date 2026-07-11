---
name: production-readiness-reviewer
description: "Evaluate production readiness across exactly 14 evidence-backed categories, calculate a 140-point and normalized score, emit only BLOCKED, SAFE WITH WARNINGS, or SAFE TO LAUNCH, and reject stale commit or environment evidence. Use for launch readiness, production-ready checks, score-project requests, release preflight, and go-live reviews."
---

# Review production readiness

Read `.solo/project.md`, `.solo/stack.md`, `.solo/risks.md`, `.solo/tests.md`, `.solo/release.md`, and the current commit/environment before scoring. Do not infer a pass from a plan, file name, or unexecuted command.

Score these categories in this exact order, each from 0 to 10:

1. Product
2. Architecture
3. Design
4. Frontend
5. Backend
6. Database
7. Security
8. Testing
9. Performance
10. SEO
11. Analytics
12. Deployment
13. Monitoring
14. Documentation

Use product scope and acceptance criteria for Product; boundaries and failure modes for Architecture; implemented flows and states for Design; browser behavior for Frontend; API validation and authorization for Backend; integrity, access controls, backup, and restore for Database; secrets, authz, dependencies, and threat evidence for Security; unit/integration/e2e/edge evidence for Testing; measured vitals and hot paths for Performance; crawl/index/meta evidence for SEO; consent-safe funnel measurement for Analytics; environment separation and rollback for Deployment; error, uptime, log, metric, and alert evidence for Monitoring; and verified setup/API/runbook material for Documentation.

Use a provider-specific skill only when `.solo/stack.md` records that provider. Otherwise mark the provider check not applicable with evidence; do not run Vercel, Supabase, Cloudflare, Grafana, payment, or other vendor checks unconditionally.

For an inapplicable category, record `applicability: not-applicable`, a concrete `na_reason`, and evidence proving the selected project profile makes it structurally inapplicable. The prepared room must predeclare a `solo-suite/project-profile-v1` artifact, and production validation binds its digest, run, project, commit, environment, timestamp, profile, and canonical 14-category applicability map. Core controls cannot be waived by calling everything N/A; each of the six supported profiles has a narrow N/A allowlist enforced by the validator. Because the required denominator remains 140, a verified permitted N/A receives 10/10 as a satisfied applicability control; an unsupported N/A is invalid evidence and a blocker.

Calculate:

```text
total_score = sum(the 14 category scores)          # maximum 140
normalized_score = round(total_score / 140 * 100)  # maximum 100
```

In production mode, use only these launch statuses:

- `BLOCKED`: any hard blocker, unsupported N/A, expired/mismatched evidence, score below 70, or unverified critical control.
- `SAFE WITH WARNINGS`: no hard blocker, normalized score at least 70, and every warning has an owner, remediation, and verification plan.
- `SAFE TO LAUNCH`: no hard blocker, normalized score at least 85, no category below 7, and no unresolved warning requiring launch-day action.

Hard blockers include a committed secret; missing required auth or authorization; exposed data/RLS failure; unverified payments or transactional email when used; no tested backup/restore or rollback; broken core mobile/accessibility flow; missing error monitoring; missing required funnel measurement; or evidence from a different commit, environment, or expired review window.

In score-only mode, write `references/score-evidence-v1.schema.json`, set `assessment_status` to `SCORED` or `INSUFFICIENT EVIDENCE`, list concrete risks, and never emit a launch or phase verdict.

In production mode, write `references/gate-evidence-v1.schema.json`; the profile artifact uses `references/project-profile-v1.schema.json`. Both modes require exact top-level `run_id` and `gate_id`. Every category record must repeat those run/gate IDs and contain project/repository, commit SHA, environment, timestamp, category, command executed, exit code, evidence type, provenance, the room's exact predeclared category artifact, SHA-256 artifact digest, reviewer, and expiration. Store run-owned evidence only under `artifacts/runs/<run-id>/`.

Set `command_executed` to the single bundled `$skill-name` that produced the category evidence. Use only a skill permitted for that category by the schema; never write a shell command, an invented skill, or the production gate itself as evidence. Provider-specific skills remain conditional on `.solo/stack.md`.

Classify the artifact with exactly one `evidence_type`: `ci-report`, `tool-report`, `manual-observation`, `narrative-assertion`, or `applicability-record`. Record provenance as `source_kind`, `producer`, `source_reference`, and `generated_at`. Match `source_kind` to the type: CI reports use `ci`, local tool reports use `local-tool`, manual observations use `manual-review`, narrative assertions use `manual-review` or `repository-record`, and applicability records use `repository-record`. Treat a narrative assertion as an assertion, not as raw CI or tool output. Use `applicability-record` only for a verified `not-applicable` control.

Represent each warning as an object with `message`, `category`, `owner`, `remediation`, and `verification`. The `verification` object must contain a concrete `method` and `success_criteria`; plain warning strings are invalid.

Validate the evidence before issuing a status:

```text
<python> <skill-root>/scripts/validate_gate_evidence.py <evidence.json> --root <project-root> --room <prepared-room.json> --run-id <run-id> --gate-id <gate-id> --commit <sha> --environment <name> --mode production
<python> <skill-root>/scripts/validate_gate_evidence.py <evidence.json> --root <project-root> --run-id <run-id> --gate-id <gate-id> --commit <sha> --environment <name> --mode score --max-age-hours <hours>
```

Do not accept a copied score, an all-N/A `SCORED` result, an artifact whose digest changed, a record from another run/gate/commit/environment, evidence outside the run namespace, evidence older than the allowed maximum, unknown evidence provenance, or a skill invocation outside the category allowlist. Production validation must independently revalidate the prepared room's required before-deploy phase record and see `GO`. End with the 14-line scorecard, total `/140`, normalized `/100`, the mode-appropriate status, risks or blockers, structured production warnings when applicable, evidence file path, and the next explicit `$gate-*` or `$release-*` skill.
