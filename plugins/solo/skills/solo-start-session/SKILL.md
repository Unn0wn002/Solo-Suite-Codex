---
name: solo-start-session
description: "Resume the project - read .solo memory (incl. stack.md) and re-orient at the start of a session Use when the user explicitly invokes $solo-start-session or asks for this solo start-session workflow."
---

# Solo Start Session

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $project-memory-manager in start-session mode. Apply it to the user's supplied arguments and surrounding request.

Read .solo/stack.md, handoff.md, tasks.md, prd.md, architecture.md, design.md, and
decisions.md, then give a tight re-orientation: where the project stands (on which stack),
what was in flight, what's blocked, recent decisions worth remembering, and the recommended
next task with its first concrete step and which skill to invoke for it. If stack.md is
missing, recommend running $stack-intake first so every command this session is stack-aware.
This is the counterpart to $solo-end-session and the first thing to run when returning to a
project. If .solo/ doesn't exist, offer to initialize it.

## Output
End with the 7-part contract: **Summary · Findings/Work done · Risks · Required fixes · Suggested tasks** (→ `.solo/tasks.md`, stable T-IDs) **· Verification · Next skill** (exact skill invocation).
