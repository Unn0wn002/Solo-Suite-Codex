---
name: memory-sync
description: "Preview and explicitly sync the project's non-secret .solo/ memory to an Obsidian vault or Grafana dashboard. Use when the user asks to push project notes, mirror project status, update an Obsidian vault, or prepare/update a Grafana project dashboard."
---

# Memory Sync

`.solo/` remains authoritative; Obsidian and Grafana are one-way mirrors. Every
run starts as a preview. External writes happen only after the user invokes
this skill explicitly and confirms the exact destination and proposed changes.

## Non-negotiable safety contract

- Never store a token, password, API key, cookie, authorization header,
  connection string, private key, or secret-store value in `.solo/config.md`,
  another `.solo/` file, generated payloads, logs, project memory, or chat.
- Read credentials only through a connector that handles authentication, an
  environment variable, or an OS secret store. Configuration stores only the
  *name* of the token environment variable. Never echo, print, interpolate, or
  otherwise expose its value in a model-visible command. If no secret-safe
  connector/API path exists, emit an import artifact instead of writing.
- Never sync `.solo/config.md`, `.env*`, credential files, secret-store data,
  or arbitrary `.solo/*.md` files. Use the explicit source allowlist below.
- Inspect allowlisted content for likely credentials before previewing it. Omit
  suspicious values from the preview and stop the external write until they
  are removed from memory. Report only relative path, line, rule, a short
  redaction, and a SHA-256 fingerprint.
- Logs contain only operation, destination host/path, stable resource ID,
  create/update/skip counts, status, and redacted errors. Never log request or
  response bodies, authorization metadata, source note contents, or tokens.
- Never delete user content. Updates are idempotent and limited to managed
  markers or a stable dashboard UID.

## Configuration

Read only these non-secret settings from `.solo/config.md`:

```yaml
obsidian_vault_path: /path/to/Vault/Projects
grafana_url: https://grafana.example.com
grafana_dashboard_uid: solo-project-example
grafana_token_env: GRAFANA_TOKEN
```

The values permitted here are a service URL, a local destination path,
non-secret resource identifiers, and an environment-variable *name*. A field
such as `token`, `api_key`, `password`, or `authorization` is invalid even if a
user offers it.

Before creating or changing `.solo/config.md`, add the exact line
`.solo/config.md` to the project-root `.gitignore` if it is not already covered.
If the workspace is read-only, show that recommendation and do not create the
config. Never weaken an existing ignore rule.

## Source allowlist

Read only these contract files when present: `project.md`, `stack.md`, `prd.md`,
`architecture.md`, `api-contract.md`, `data-contract.md`, `env-contract.md`,
`design.md`, `tasks.md`, `decisions.md`, `risks.md`, `bugs.md`, `tests.md`,
`release.md`, `monitoring.md`, and `handoff.md`. Do not replace this allowlist
with a glob.

## Required preview and confirmation flow

1. Resolve and validate the destination. Default to preview/dry-run even when a
   connector is authenticated.
2. Build sanitized Obsidian notes, dashboard JSON, or annotation payloads
   locally. Show only filenames/UIDs and create/update/skip counts; do not dump
   private note bodies into logs.
3. Present the exact destination, resource IDs, proposed creates/updates, any
   cleanup, and the fact that the next step is an external write.
4. Ask for explicit confirmation for this preview. A prior run's confirmation
   does not carry over after source, destination, or payload changes.
5. Write only the confirmed plan. Record redacted operation metadata and verify
   stable IDs/counts afterward. If the write differs from the preview, stop.

## Obsidian mode

Mirror the allowlisted memory into a project folder. Create an overview note
and one stable note per source file, with Obsidian frontmatter and wikilinks.
Convert tasks to checkboxes while preserving stable T-IDs. Manage only content
between `<!-- solo:begin -->` and `<!-- solo:end -->`; preserve all text outside
those markers. Re-running updates the same stable filenames and never creates
numbered duplicates.

The preview lists the resolved vault path and notes that would be created or
updated. Treat this filesystem destination as an external side effect: require
confirmation before writing, then clean up only records/files created by the
confirmed run if a failure leaves partial managed output. Never delete a user's
own note.

## Grafana mode

Generate a dashboard JSON with memory-derived task, blocker, audit, release,
and decision panels/annotations. Match by configured UID so reruns update in
place. Store only non-secret processed annotation IDs; never store annotation
payloads containing sensitive source text.

Prefer an authenticated Grafana connector, because it can keep the token out of
model-visible context. Otherwise a direct API may use the environment variable
named by `grafana_token_env` only if the execution path guarantees redacted
headers and errors. If that guarantee is unavailable, output sanitized JSON and
annotation payload files for manual import. Never stand up a metrics backend
without a separate explicit request.

## Report

Report preview versus applied state, destination path/host, stable note names or
dashboard UID, counts created/updated/skipped, cleanup performed, and any
redacted error fingerprint. Do not include credentials or copied note bodies.

## Session integration

Run after project memory is current, commonly after the end-session workflow.
Sync never changes the source-of-truth contract files. If a two-way workflow is
requested, stop and design conflict handling separately rather than silently
pulling external changes into `.solo/`.
