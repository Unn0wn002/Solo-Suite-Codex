---
name: solo-sync-grafana
description: "Preview and, after explicit confirmation, synchronize sanitized project-health summaries from .solo/ to a Grafana dashboard. Use only when the user explicitly invokes $solo-sync-grafana."
---

# Sync project health to Grafana

Use `$memory-sync` in Grafana mode and preserve its complete safety contract.

Start in preview/dry-run mode. Read only the 16 allowlisted `.solo/` contract files; never read or sync `.solo/config.md`, `.env*`, credentials, raw request/response bodies, or secret-store data. Scan the proposed payload for likely credentials and stop if any are found.

`.solo/config.md` may contain only the Grafana URL, stable dashboard UID, and the name of the environment variable holding the token, such as `grafana_token_env: GRAFANA_TOKEN`. It must never contain a token value. Recommend or add `.solo/config.md` to `.gitignore` before creating it.

Build sanitized dashboard and annotation JSON locally. The preview shows only the destination host, dashboard UID, annotation IDs, and create/update/skip counts. Do not expose source note bodies or authentication metadata in output or logs.

If a secret-safe authenticated connector is available, use it only after the user confirms the exact preview. Otherwise use the named environment variable only through an execution path that redacts headers and errors; if that cannot be guaranteed, emit importable JSON instead of making an external request. Confirmation expires whenever the destination or payload changes.

Updates are idempotent by dashboard UID and annotation stable ID. Never delete user content. After an authorized write, verify the UID/counts and record only redacted operation metadata.

## Output

Report summary, preview versus applied state, sanitized evidence, risks, required fixes, suggested `.solo/tasks.md` entries, verification, and the next explicit `$solo-*` skill. Never include token values or copied memory contents.
