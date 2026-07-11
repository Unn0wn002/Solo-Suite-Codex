# Changelog

## 1.0.11 — 2026-07-11

### Advanced website hardening — 2026-07-11

- Added stack intake, a dedicated pre-deploy gate, complete gate prerequisites, mandatory advanced-web evidence, and a three-iteration repair/retest loop to the Full Team website room.
- Strengthened production evidence with category-specific real-skill allowlists, typed provenance, chronology checks, and structured actionable warnings.
- Replaced 42 invalid `$plugin-command` follow-ups with real contextual skills and fixed the command converter so the placeholder cannot return.
- Fixed installed-cache self-check discovery when a personal marketplace exists above an unrelated cache plugin.
- Added 63 behavior and regression tests across Site Doctor helpers, AgentRoom routing, evidence contracts, release reproducibility, and repository hygiene, bringing the suite to 174 tests and measured coverage to 65%; CI enforces a 62% floor.
- Split architecture/database and documentation/release-management stages, bound all gate evidence to the exact run, gate, commit, environment, and artifact digest, and made every negative or insufficient verdict stop or enter the bounded repair loop.
- Added prepared-room digests, exact prerequisite/producer bindings, per-project run-ID reservations, run-scoped artifacts, maximum-age enforcement, machine-readable loop signals, a profile-specific N/A contract, and independent before-deploy revalidation; an all-N/A score can no longer approve production.
- Added a hash-locked eight-package validation environment, LF-only repository policy, committed-blob packaging immune to local Git attributes and replacement refs, byte-reproducibility tests across clean clones, tracked-output protection, and fail-closed dirty/no-commit release checks.

### Codex-native release

- Converted the 17-component Solo Suite v1.0.10 marketplace to 18 native Codex plugins using `.codex-plugin/plugin.json` and repo-local `.agents/plugins/marketplace.json` metadata.
- Migrated all 100 legacy command workflows one-to-one into explicit Codex skills. Added `command-map.json` and `COMMAND-MAP.md` for deterministic migration lookup.
- Added the `full-team` meta-plugin and `full-team-orchestrator`, with an honest component-availability check because the current Codex plugin manifest has no plugin-dependency field.
- Added UI metadata for all 157 skills and explicit-only policy for workflows involving mutation, deployment, synchronization, form submission, secrets, or production access.

### Security and runtime hardening

- Added the installed-root-aware Site Doctor launcher and external-working-directory regression coverage.
- Reworked secret findings to emit only path, line, rule, redaction, and SHA-256 fingerprint; added realistic leak regression fixtures and scanner self-suppression.
- Removed write-capable SQL from the read-only database audit and routed maintenance work to the explicitly confirmed database-fix workflow.
- Secured memory synchronization, token configuration, sync exclusions, log redaction, dry-run defaults, browser form submission, and production-side-effect policy.
- Corrected HSTS, redirect, mixed-content, DMARC, recursive SPF, nested-H1, tracker, cookie, and dependency-range behavior.

### AgentRooms and gates

- Added the strict AgentRooms v1 JSON Schema, semantic validator, memory-steward ownership, unique task allocation, workspaces, artifact locks, bounded loops, implicit `.solo/` effects, and gate evidence requirements.
- Rebuilt all four room templates and added a declarative Codex runner adapter. Room JSON remains a validated execution plan, not an unclaimed automatic runtime.
- Standardized production readiness on 14 categories, 140 points, three launch statuses, provider-aware applicability, artifact digests, and commit/environment/expiry validation.

### Release engineering and documentation

- Added source-checkout and installed-cache self-check modes, complete native manifest validation, Windows/Ubuntu CI, coverage, package smoke tests, SBOM, provenance, and checksums.
- Updated the Site Doctor DOCX for Codex and removed comments/legacy invocation text. Structural Open XML checks pass; visual rendering remains unverified where Office/LibreOffice is unavailable.
- Corrected plugin, skill, workflow, and helper counts and removed unsupported standalone-skill and uniform-output-contract claims.

## 1.0.10 — 2026-07-10

The supplied historical source release contained 17 plugins, 56 specialist skills, 100 Claude-oriented commands, 10 helper scripts, SSRF protection, AgentRooms templates, and the original shared `.solo/` workflow. That archive is optional external historical material and is not bundled or required for the v1.0.11 build; `RELEASE-PROVENANCE.json` pins its verified SHA-256 digest.
