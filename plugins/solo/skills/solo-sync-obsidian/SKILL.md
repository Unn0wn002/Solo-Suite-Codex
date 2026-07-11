---
name: solo-sync-obsidian
description: "Preview and, after explicit confirmation, mirror sanitized .solo/ project memory into an Obsidian vault using stable managed sections. Use only when the user explicitly invokes $solo-sync-obsidian."
---

# Sync project memory to Obsidian

Use `$memory-sync` in Obsidian mode and preserve its complete safety contract.

Start in preview/dry-run mode. Read only the 16 allowlisted `.solo/` contract files. Never read or copy `.solo/config.md`, `.env*`, credentials, secret-store data, or arbitrary extra `.solo/` files. Scan allowlisted content for likely credentials; omit suspicious content and block the write until the source is repaired.

The optional config may store only `obsidian_vault_path`. Recommend or add `.solo/config.md` to the project-root `.gitignore` before creating it. Do not store credentials or private note contents in config or logs.

Generate an Overview/MOC and one stable linked note per present allowlisted file. Convert tasks to checkboxes while retaining stable task IDs. Manage only content between `<!-- solo:begin -->` and `<!-- solo:end -->`, preserving all user-authored content outside those markers.

The preview names the resolved vault, notes to create/update/skip, and cleanup plan without dumping note bodies. Require explicit confirmation for that exact preview before any filesystem write outside the project. If the source, destination, or generated content changes, preview and confirm again.

Never delete a user's note. On a partial failure, clean up only new managed records from the confirmed run and report any remaining synthetic/managed IDs. Verify stable filenames and counts after the write.

## Output

Report summary, preview versus applied state, destination, stable filenames, create/update/skip counts, cleanup, risks, verification, and the next explicit `$solo-*` skill. Do not include credentials or copied note bodies.
