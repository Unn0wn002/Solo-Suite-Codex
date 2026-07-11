---
name: agent-room-templates
description: "Prepare and validate bounded Codex multi-agent workflows with explicit stages, isolated worktrees, artifact locks, one memory steward, gate evidence, and bounded loops. Use for agent rooms, full-team parallel work, multi-agent planning, bug-fix loops, production-release rooms, or Site Doctor audit rooms."
---

# Use AgentRoom templates

Treat `agentsrooms/*.json` as declarative orchestration plans, not executable runtimes. Read `references/codex-runner-adapter.md` before starting subagents.

Validate all bundled rooms:

```text
<python> <skill-root>/scripts/validate_rooms.py --suite <suite-root>
```

Instantiate one room with a unique run ID:

```text
<python> <skill-root>/scripts/prepare_run.py <template.json> <run.json> --run-id <unique-lowercase-id> --suite <suite-root> --project-root <project-root>
```

Available templates:

- `full-team-website.json`: all product, architecture, design, frontend, backend, database, QA, browser QA, security, DevOps, release, documentation, Git/PR, repo-analysis, AI-review, growth, and Site Doctor roles; profile-aware checks; fail-closed before-code, before-merge, before-deploy, and 14-category production gates.
- `bug-fix-loop.json`: reproduce, fix, verify, review, security, and before-merge evidence with a maximum of three repair iterations.
- `site-doctor-audit.json`: parallel site and provider audit followed by centralized triage and scoring.
- `production-release.json`: collect all 14 category records, prepare a preview-only release plan and documentation in dependency order, pass before-deploy, and then run the production gate.

Keep exactly one `memory-steward` seat. All other seats propose shared-memory changes; only the steward writes `.solo/tasks.md`, `.solo/decisions.md`, `.solo/handoff.md`, or other `.solo/` files and allocates stable task IDs.

Use only an instantiated plan with `prepared: true`. The adapter reserves the case-folded run ID per project and isolates artifacts and worktrees under their exact run namespaces. Reject duplicate IDs, undeclared writes, simultaneous writers, same/later-stage producer reads, disconnected stages, invalid loop targets, shared run paths, incompatible evidence contracts, substituted prerequisites or producer commands, missing gate artifacts, over-age or mismatched run/gate/commit/environment evidence, unconditional gate handoffs, incomplete status routing, and a gatekeeper that cannot read every prerequisite. A production gate also requires the prepared profile contract and independently validated before-deploy `GO`. Do not deploy, merge, submit forms, or perform external writes merely because a template names that workflow; those actions remain explicit and confirmation-gated.
