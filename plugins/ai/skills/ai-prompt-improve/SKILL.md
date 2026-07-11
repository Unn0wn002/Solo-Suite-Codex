---
name: ai-prompt-improve
description: "Rewrite vague coding prompts into precise agent instructions. Use when the user explicitly invokes $ai-prompt-improve or asks for this ai prompt-improve workflow."
---

# AI Prompt Improve

Follow this workflow using the user's supplied context. Preserve stated gates, evidence requirements, safety constraints, and output contracts.

Use $ai-output-auditor in prompt-improve mode. Apply it to the user's supplied arguments and surrounding request.

Rewrite into precise instructions: goal, relevant files/context, hard constraints, acceptance criteria (pass/fail), and the exact expected output format. Remove ambiguity that invites guessing.

## Output
End with the 7-part contract: **Summary · Findings/Work done · Risks · Required fixes · Suggested tasks** (→ `.solo/tasks.md`, stable T-IDs) **· Verification · Next skill** (exact skill invocation).
