# Codex AgentRoom adapter

AgentRoom JSON is a declarative plan, not an autonomous runtime. Use this adapter contract when orchestrating it with Codex subagents.

1. Validate the selected template with `scripts/validate_rooms.py`.
2. Instantiate it with a unique lowercase Windows-safe run ID using `scripts/prepare_run.py TEMPLATE OUTPUT --run-id RUN_ID --suite SUITE_ROOT --project-root PROJECT_ROOT`. Use only a plan with `prepared: true`: it namespaces every runner-owned artifact under `artifacts/runs/RUN_ID/` and worktree under `worktrees/runs/RUN_ID/`. The adapter atomically reserves a case-folded ID in `PROJECT_ROOT/artifacts/runs/.registry/`; an existing claim stops duplicate or case-colliding runs.
3. Create only the non-steward seats for the current stage. Give each seat its declared reads, workspace, commands, deliverable, and artifact lock; do not give it undeclared write access.
4. Run seats from the same stage in parallel only when their worktrees and artifact locks are disjoint.
5. Collect proposals from every seat. Send proposals to the single `memory_steward`; only that seat allocates task IDs and writes `.solo/` files.
6. Require the declared handoff check before starting a non-gate next stage. Stop on a missing artifact, conflicting proposal, undeclared write, or stale gate record.
7. For a gate, pass the prepared room to the contract-specific validator. Validate its room digest, exact ordered prerequisite set, declared producer commands, artifact digests and paths, run ID, gate ID, commit SHA, environment, reviewer, timestamp, expiry, and `max_age_hours`. Missing, substituted, over-age, or invalid evidence is a stopped run.
8. Read only the configured `transitions.status_field`. Select exactly one route whose `statuses` contains the validated value. If none or more than one matches, apply `default_action: stop`. Never follow a gatekeeper `handoff_to`.
9. Before a gate route enters production, validate every `required_gate_results` record against the latest evidence from the exact room, run, commit, and environment. Re-run the phase-evidence validator over the required artifact and all its prerequisites. A missing or invalid before-deploy `GO` blocks production.
10. Enforce loop bounds from the machine-readable `trigger` and `exit` gate/status signals. Use only the explicit loop edge, count every re-entry, and apply `on_exhaustion_action: stop`; the narrative `until` text is explanatory, not executable routing.

Codex collaboration tools provide the agent execution surface. The JSON and scripts provide validation and orchestration constraints; they do not themselves spawn agents, submit forms, deploy, merge, or write to external services.
