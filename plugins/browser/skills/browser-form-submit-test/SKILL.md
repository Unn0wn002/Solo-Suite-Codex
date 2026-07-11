---
name: browser-form-submit-test
description: "Prepare and observe a manual-only form-submission test with synthetic data, sandboxed side effects, explicit confirmation, cleanup, and evidence. Use only when the user explicitly invokes $browser-form-submit-test."
---

# Test a form safely

Use `$browser-qa-engineer` in manual-only form-submit-test mode. Automation may navigate, inspect, and fill synthetic values only when filling itself has no side effect. It must stop before the final submit, confirm, delete, pay, send, or save control.

Default to localhost, staging, or a dedicated test tenant. Never use real PII, payment cards, production credentials, customer accounts, customer data, or production session cookies. Do not trigger real payment, email, SMS, push, webhook, deployment, account, or destructive workflows. Require sandboxed/stubbed integrations; otherwise mark the test blocked.

Before each state change, present the exact environment, synthetic data, affected system, expected sandbox events, and cleanup plan. Wait for the user to confirm that exact action and perform the final submission manually. Then inspect the resulting UI/network state read-only.

Cover valid, invalid, empty, boundary, network-failure, and double-submit behavior where the environment can reproduce them safely. Record every side effect with timestamp, environment, synthetic record ID, expected/observed sandbox events, outcome, and cleanup state. Sanitize cookies, tokens, PII, request bodies, and response bodies.

Cleanup is also manual-only when destructive. If the user cannot clean up, record the synthetic IDs as an open task. A submission that was not performed is `NOT CHECKED`, never PASS.

## Output

Return status, environment and scope, sanitized evidence, findings, risk, required fixes, side-effect ledger, suggested stable tasks, verification steps, cleanup state, and the next explicit `$browser-*` skill. No evidence means no finding.
