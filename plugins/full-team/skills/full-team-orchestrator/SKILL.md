---
name: full-team-orchestrator
description: "Coordinate all 17 Solo Suite component plugins as one profile-aware Codex delivery team, detect missing capabilities, enforce centralized project memory and evidence gates, and route work from discovery through production readiness. Use for full-team development, whole-product delivery, or checking that the complete Solo Suite team is installed."
---

# Coordinate the full team

Read `references/component-plugins.json`. Enforce each component's `minimum_version`, treat its representative skill as the discovery minimum, then preflight every command declared by the selected AgentRoom against the skills actually available for this run. Report missing or version-skewed capabilities before starting; do not claim a hard plugin dependency was installed automatically because Codex plugin manifests do not expose dependency metadata.

Run the deterministic preflight before preparation:

```text
<python> <skill-root>/scripts/preflight.py <room.json> --suite-root <suite-root>
```

Do not start when it reports `FAIL`; repair the missing component, version, skill, or room contract first.

If all required capabilities are available, invoke `$solo-full-team-dev` and follow `$project-memory-manager` plus `$agent-room-templates`. Choose the project profile explicitly when preparing the room, initialize `run_room.py` with the exact commit and environment, and create only tasks emitted by its `next` command. Record each seat result, route shared-memory proposals through one steward, and call `advance` only after all current-stage tasks are recorded. The runner's validator-backed transition is authoritative; never substitute a prose handoff or self-reported gate status.

If components are missing, continue only with an explicit degraded-mode plan that lists the missing role, the lost checks, and the installation needed to restore coverage. Never silently replace security, database, browser, deployment, or production-gate evidence with model judgment.

Keep mutation-capable work explicit. Preview external sync, deployment, migration, browser submission, Git publication, and production operations; require confirmation before acting. This orchestrator does not publish, deploy, merge, or submit merely because the full-team workflow reaches that stage.
