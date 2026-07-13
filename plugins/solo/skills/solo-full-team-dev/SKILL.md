---
name: solo-full-team-dev
description: "Run the explicit, profile-aware Solo Suite full-team workflow across all required engineering roles with centralized memory, conditional reviews, and enforced evidence gates. Use when the user explicitly invokes $solo-full-team-dev or asks for end-to-end full-team delivery."
---

# Run full-team development

Use `$project-memory-manager` in full-team-dev mode and the strict `full-team-website` template from `$agent-room-templates` when parallel seats help. Select one profile before preparation: public marketing site, SaaS application, e-commerce, internal application, API/service, or library/package. Pass that profile with a unique Windows-safe run ID to `prepare_run.py`, then initialize `run_room.py` with the exact commit and environment. Use only tasks emitted by `next`, their run-scoped worktrees, and their declared artifacts. Do not infer providers, environments, data stores, forms, authentication, or deployment targets that stack intake did not establish.

Staff Product Manager, Software Architect, UI/UX Designer, Frontend Developer, Backend Developer, Database Engineer, QA Engineer, Browser QA Engineer, Security Engineer, DevOps Engineer, Release Manager, Documentation Writer, Git/PR Manager, Repo Analyst, AI Agent Reviewer, Growth/Conversion Reviewer, and Site Doctor. Route shared `.solo/` proposals through one memory steward.

Follow this evidence order:

1. Discovery: `$stack-intake`, `$stack-connector-check`, repository/risk/dependency maps, PRD, acceptance criteria, and profile.
2. Architecture and design: finish system/API/environment architecture first, then database/data/migration design from that artifact, then UX states and accessibility constraints.
3. Before code: `$gate-before-code` must be GO for current product, architecture, and design evidence.
4. Implementation: frontend/backend work, followed by post-implementation `$design-ui-review` and `$ai-review-output`.
5. QA and hardening: unit, integration, E2E, edge-case, lint, and static-type evidence; browser smoke/console/mobile/visual evidence; security and mandatory web checks.
6. Before merge: `$gate-before-merge` reads the detailed review, security, testing, browser, contract, migration, rollback, and web-quality artifacts.
7. Release preparation: documentation and PR/release notes first, then release management from those completed artifacts plus exact-environment readiness, monitoring, backups, and rollback ownership.
8. Before deploy: `$gate-before-deploy` reads the before-merge result plus browser QA, lint/types, migration, contracts, environment, release, accessibility, visual/cross-browser, forms/privacy, dependency/SBOM, performance/load, security, monitoring, and rollback evidence. This is a gate only; it does not authorize a deployment.
9. Production readiness: `$gate-production-ready` evaluates all 14 categories only after validating the latest before-deploy result as `GO` for the same run, commit, and environment.

Always include `$test-edge-cases`. Run `$growth-conversion-audit` only for conversion-oriented public experiences. Run Vercel, Supabase, Cloudflare, tag, payment, Grafana, and other provider checks only when `.solo/stack.md` records them.

For advanced websites, the following evidence bundle is mandatory:

- Accessibility: `$site-doctor-a11y`, including keyboard, focus, semantics, labels, contrast, and automated/manual limitations.
- Visual and cross-browser: `$browser-visual-check` plus smoke/mobile coverage across the support matrix recorded by stack intake.
- Forms and privacy: `$site-doctor-audit-forms` and `$site-doctor-compliance`; if there are no forms or regulated flows, record why the profile makes that sub-check N/A.
- Dependencies and SBOM: `$repo-dependency-map` and `$site-doctor-audit-deps`, with lockfile provenance, known-risk findings, licenses where available, and a reproducible component inventory.
- Performance and load: `$site-doctor-perf` and a safely bounded `$site-doctor-load-test` against localhost, staging, or a dedicated test environment. Never load-test production without separate explicit authorization.

Lint/type, contract, migration, browser, and environment evidence must name the exact command or procedure, exit status, commit, environment, artifact digest, reviewer, and expiration. A profile-aware N/A is allowed only with positive evidence that the capability is absent; it is never a substitute for a failed or unavailable check.

Default browser work to localhost, staging, or a dedicated test tenant with synthetic data. Do not invoke `$browser-form-submit-test` or another state-changing browser workflow without explicit confirmation and a cleanup plan.

For every skipped role or category, record evidence and a concrete N/A reason. Submit each seat's result contract to the runner, including exact artifact digests and only commands that seat actually executed. Stop immediately on a validator-backed `$gate-before-code` NO-GO. A `$gate-before-merge` or `$gate-before-deploy` NO-GO follows only the runner-selected bounded repair/retest route: assign the smallest owner-specific fixes, rerun invalidated checks, and regenerate exact-commit evidence. On exhaustion, preserve the persisted BLOCKED state and do not merge, deploy, or publish.

Finish with the 14-category `$gate-production-ready` status; production uses only BLOCKED, SAFE WITH WARNINGS, or SAFE TO LAUNCH. The strict room completes only on SAFE TO LAUNCH; SAFE WITH WARNINGS stops for explicit human direction. SAFE TO LAUNCH is not deployment authorization.

When integrated worker commits change the project HEAD, use the runner's explicit `rebind --commit <new-head>` before starting the next stage. Rebind must verify every clean worker HEAD was integrated and then restart evidence collection at discovery for the new commit; never relabel old evidence or reset the bounded repair counter.

Report the runner's current stage, profile, active commit, attempt and loop counters, artifacts produced, N/A decisions, unresolved blockers, validator transcripts, and exact next `$skill`. Resume with `status` and `next` from the persisted checkpoint rather than reconstructing state by hand.
