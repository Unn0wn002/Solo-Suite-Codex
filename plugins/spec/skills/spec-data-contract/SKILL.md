---
name: spec-data-contract
description: "Define database entities, constraints, and relationships. Use when the user explicitly invokes $spec-data-contract or asks for this spec data-contract workflow."
---

# Spec Data Contract

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $software-architect to define a data contract (do a lighter inline version if that plugin isn't installed). Apply it to the user's supplied arguments and surrounding request.

Specify entities, fields + types, keys, constraints (NOT NULL / unique / FK / check), relationships and cardinality, and indexes. Keep it consistent with the API contract and note migration impact. Pairs with `$site-doctor-audit-db` and, for Supabase, `$security-rls-test`.


Write the contract to **`.solo/data-contract.md`** (keep consistent with `.solo/api-contract.md`).

## Output
End with the 7-part contract: **Summary · Findings/Work done · Risks · Required fixes · Suggested tasks** (→ `.solo/tasks.md`, stable T-IDs) **· Verification · Next skill** (exact skill invocation).
