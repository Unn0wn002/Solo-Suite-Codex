# Solo Suite for Codex

Solo Suite is a Codex-native plugin marketplace for planning, designing, building, testing, auditing, and releasing software with shared `.solo/` project memory. This edition preserves the 100 workflows from Solo Suite v1.0.10 by migrating each legacy command to an explicit Codex skill.

**18 plugins** · **157 skills** · **100 migrated commands** · **15 helper scripts**

The 157 skills comprise 56 specialist skills, 100 command-derived skills, and the new `full-team-orchestrator` meta-skill. The authoritative one-to-one migration is in [`command-map.json`](command-map.json) and the readable table is in [`COMMAND-MAP.md`](COMMAND-MAP.md).

## What changed for Codex

Codex plugins use `.codex-plugin/plugin.json` and expose workflows as skills. Invoke a migrated workflow with the specific `$<plugin>-<command>` skill shown in the map:

```text
Legacy lookup                 Codex invocation
/solo:start-session          $solo-start-session
/dev:implement-feature       $dev-implement-feature
/site-doctor:full-checkup    $site-doctor-full-checkup
/gate:production-ready       $gate-production-ready
```

The legacy names are documentation-only migration keys. There is no Claude command runtime or `${CLAUDE_PLUGIN_ROOT}` dependency in this release. Skills that can mutate files, deploy, synchronize externally, submit forms, handle secrets, or touch production are explicit-only through `agents/openai.yaml` policy.

## Install

Unpack the release so it has one enclosing `solo-suite-codex-v1.0.11/` folder, then register that folder as a local marketplace:

```powershell
codex plugin marketplace add "C:\path\to\solo-suite-codex-v1.0.11"
codex plugin add solo@solo-suite-codex
codex plugin add project@solo-suite-codex
codex plugin add dev@solo-suite-codex
```

On macOS or Linux, use the same commands with a POSIX path. Install any combination of component plugins from the inventory below. Start a new Codex task after installing or updating so the new skills are loaded.

For the complete team, install all 17 component plugins plus `full-team`:

```text
ai browser design dev docs gate git growth project release repo
security site-doctor solo spec stack test full-team
```

Then invoke:

```text
$full-team-orchestrator
```

Codex's current plugin manifest contract has no plugin-dependency field. Consequently, installing `full-team` does not silently install its components. The orchestrator checks the component list in `plugins/full-team/skills/full-team-orchestrator/references/component-plugins.json`, reports missing plugins, and degrades only with an explicit evidence-backed reason.

## Plugin inventory

| Plugin | Skills | Migrated workflows | Purpose |
|---|---:|---:|---|
| `solo` | 13 | 10 | Shared memory, sessions, sync, self-check, master workflow |
| `project` | 5 | 3 | PRD, architecture, task breakdown |
| `design` | 4 | 3 | UX flow, component system, post-build UI review |
| `dev` | 6 | 4 | Feature work, bug repair, refactoring, code review |
| `test` | 5 | 4 | Unit, integration, end-to-end, and edge-case testing |
| `release` | 6 | 4 | CI, preflight, deployment plan, rollback plan |
| `docs` | 5 | 4 | README, API, setup, and runbook documentation |
| `site-doctor` | 50 | 24 | Website, database, security, SEO, performance, and operations audits |
| `stack` | 14 | 7 | Stack intake, connector checks, and conditional vendor audits |
| `git` | 6 | 5 | Branch, commit, PR, release-note, and issue workflows |
| `spec` | 7 | 5 | Feature, acceptance, API, data, and environment contracts |
| `repo` | 6 | 5 | Read-only repository mapping and risk analysis |
| `security` | 6 | 5 | Threat, authorization, RLS, secret, and abuse-case reviews |
| `browser` | 6 | 5 | Browser smoke, console, visual, mobile, and form QA |
| `gate` | 7 | 5 | Before-code/merge/deploy and production gates |
| `ai` | 8 | 6 | Prompt, handoff, output, repair, and AgentRooms workflows |
| `growth` | 2 | 1 | Conditional conversion audit |
| `full-team` | 1 | 0 | Meta-orchestrator for the 17 components |

## Full-team workflow

`$full-team-orchestrator` and `$solo-full-team-dev` coordinate these roles when the project profile makes them relevant: Product Manager, Software Architect, UI/UX Designer, Frontend Developer, Backend Developer, Database Engineer, QA Engineer, Browser QA Engineer, Security Engineer, DevOps Engineer, Release Manager, Documentation Writer, Git/PR Manager, Repo Analyst, AI Agent Reviewer, Growth/Conversion Reviewer, and Site Doctor.

The flow begins with `$stack-intake` before `$stack-connector-check`, orders architecture before database architecture and design, performs `$ai-review-output` between major phases, includes `$test-edge-cases`, and runs `$design-ui-review` after implementation. The advanced-website room requires accessibility, visual/cross-browser, forms/privacy, dependency/SBOM, performance/load, lint/type, contract, migration, browser-QA, environment, and release evidence before its dedicated pre-deploy gate. Every gate consumes the prepared-room digest and evidence bound to the exact run, gate, commit, environment, declared prerequisite, producer command, artifact digest, and maximum age. A failed gate enters a status-driven, bounded three-iteration repair/retest loop; only a freshly revalidated before-deploy `GO` can reach production, and the strict room completes only with `SAFE TO LAUNCH`. Growth and provider-specific reviews run only when the project profile and `.solo/stack.md` make them applicable. Every skipped category needs a digest-bound profile reason permitted by the selected profile's narrow N/A policy.

Supported profiles include public marketing site, SaaS application, e-commerce, internal application, API/service, and library/package.

## Shared project memory

The suite uses 16 standard files under `.solo/`:

```text
project.md        stack.md          prd.md            architecture.md
api-contract.md   data-contract.md  env-contract.md   design.md
tasks.md          decisions.md      risks.md          bugs.md
tests.md          release.md        monitoring.md     handoff.md
```

`.solo/config.md` is optional and must contain only non-secret configuration such as service URLs, resource identifiers, and environment-variable names. Token values belong in environment variables or an OS secret store. Add `.solo/config.md` to `.gitignore`; sync workflows exclude it and all detected secrets.

## Production gate

`$gate-production-ready` evaluates exactly 14 categories: Product, Architecture, Design, Frontend, Backend, Database, Security, Testing, Performance, SEO, Analytics, Deployment, Monitoring, and Documentation.

Each category is scored from 0 to 10. The total is `/140`; the normalized score is `round(total / 140 * 100)`. Production status is one of:

- `BLOCKED`
- `SAFE WITH WARNINGS`
- `SAFE TO LAUNCH`

The gate validates machine-readable evidence, the prepared-room digest, category-specific real-skill allowlists, nested run/gate identity, exact room-declared category artifacts, a separate project-profile applicability contract, typed provenance, structured actionable warnings, SHA-256 digests, commit/environment identity, chronology, expiration, and maximum age. An all-N/A score cannot become launch approval. Evidence from another run, gate, commit, or environment; invented or cross-category skills; substituted or reused artifacts; over-age evidence; changed digests; and provenance that postdates the review are rejected. Production also revalidates the required before-deploy phase evidence and all of its prerequisites. GO/NO-GO wording is reserved for the narrower before-code, before-merge, and before-deploy gates.

## AgentRooms

The `ai` plugin ships four schema-checked declarative room plans:

- `full-team-website.json`
- `production-release.json`
- `site-doctor-audit.json`
- `bug-fix-loop.json`

The v1 schema and validator enforce bounded loops with machine-readable trigger/exit statuses, reachable stages, artifact locks, unique task allocation, one memory steward, implicit `.solo/` effects, gate prerequisites, producer-command bindings, evidence declarations, gatekeeper read coverage, contract-specific gate schemas, exact-run freshness, status-driven transitions, and fail-closed gate routing. `prepare_run.py` reserves a lowercase, case-folded run ID per project. Instantiated work is isolated under `artifacts/runs/<run-id>/` and `worktrees/runs/<run-id>/`; production additionally requires the same room, run, commit, and environment's before-deploy `GO` evidence.

These JSON files are plans, not a hidden executable multi-agent runtime. `prepare_run.py` creates a validated, run-namespaced plan; Codex or another runner must still create workers stage by stage and enforce the declared workspaces, locks, status transitions, evidence contracts, handoffs, and confirmations. See `references/codex-runner-adapter.md` in the AgentRooms skill.

## Runtime and security guarantees

- Site Doctor helpers resolve from the installed plugin root through `plugins/site-doctor/scripts/run_helper.py`; they do not depend on the caller's working directory.
- Network helpers use the shared SSRF guard, validate every redirect hop, default to HTTPS, cap response sizes, and block private, metadata, reserved, and unsafe resolved addresses.
- The secret scanner emits only relative path, line number, rule, redaction, and irreversible SHA-256 fingerprint. It never emits a complete matched line or secret.
- Database audit SQL is read-only. Maintenance writes are routed to explicit fix workflows with confirmation, backup verification, mutation warning, and rollback guidance.
- Browser form submission is manual-only. Use synthetic data and a local, staging, or dedicated test tenant; production and side effects require explicit confirmation.
- External sync defaults to preview and requires confirmation before writing. Logs are redacted, and config/secrets are excluded.

## Standalone use

Install at plugin granularity for reliable dependency resolution. A skill directory is not automatically standalone merely because it contains `SKILL.md`. In particular:

- Site Doctor network skills rely on the plugin-level `lib/url_guard.py` and `scripts/run_helper.py`.
- AgentRooms relies on its schema, templates, references, and validator scripts.
- Production readiness relies on its evidence schema and validator.

Pure text-only skills can be copied to `~/.codex/skills/`, but copy every referenced file and revalidate the result. The package does not claim that every skill folder works independently.

## Validation

From the release root:

```powershell
python -m pip install --require-hashes -r requirements-dev.lock
python -m unittest discover -s tests -t . -v
python plugins/solo/skills/suite-integrity/scripts/self_check.py . -
python plugins/ai/skills/agent-room-templates/scripts/validate_rooms.py --suite .
```

`self_check.py` performs structural consistency checks; it is not proof of security or launch readiness. Release provenance, dependency inventory/SBOM, checksums, and exact validation state are shipped at the package root.

Publication-grade packages are built only from a clean Git commit. The packager snapshots `HEAD`, generates release metadata in a disposable staging directory, and leaves tracked source files unchanged:

```powershell
python tools/package_release.py --output ..\solo-suite-codex-v1.0.11.zip --validation-state validated
python tools/smoke_package.py ..\solo-suite-codex-v1.0.11.zip
git diff --exit-code
git status --short --untracked-files=all
```

The final status command must print nothing. Intentional release output under ignored `dist/` is omitted by Git.

The Site Doctor command reference and ready-to-adapt prompts are in `site-doctor-cheatsheet.docx`.

## Publisher and license

The original marketplace owner `Ayaya` and the MIT copyright holder Sakura Yukihira refer to the same publisher identity, recorded here as `Sakura Yukihira (Ayaya)`. The supplied archive did not contain a verified repository or homepage; this Codex release is maintained at [Unn0wn002/Solo-Suite-Codex](https://github.com/Unn0wn002/Solo-Suite-Codex), whose visibility and access are controlled by the publisher. See `LICENSE`, `SECURITY.md`, and `CONTRIBUTING.md`.
