---
name: spec-env-contract
description: "List required environment variables, secrets, and config by environment. Use when the user explicitly invokes $spec-env-contract or asks for this spec env-contract workflow."
---

# Spec Env Contract

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $software-architect to define an environment/config contract (lighter inline if that plugin isn't installed). Apply it to the user's supplied arguments and surrounding request.

List every required env var and secret, what it's for, and which environments (dev/preview/prod) it belongs to — **names only, never values**. Separate public vs secret; cross-check the code and `.env.example`. Pairs with `$security-secrets-fix` and `$stack-audit-vercel`.


Write the contract to **`.solo/env-contract.md`** — names only, never values.

## Output
End with the 7-part contract: **Summary · Findings/Work done · Risks · Required fixes · Suggested tasks** (→ `.solo/tasks.md`, stable T-IDs) **· Verification · Next skill** (exact skill invocation).
