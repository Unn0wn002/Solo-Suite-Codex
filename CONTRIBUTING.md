# Contributing

Changes should preserve the Codex-native plugin contract, explicit side-effect policy, and one-to-one workflow mapping.

## Development setup

```text
python -m venv .venv
.venv/Scripts/python -m pip install --require-hashes -r requirements-dev.lock   # Windows
.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock       # macOS/Linux
```

Use the interpreter from the virtual environment for all checks.

## Required checks

```text
python -m unittest discover -s tests -t . -v
python plugins/solo/skills/suite-integrity/scripts/self_check.py . -
python plugins/ai/skills/agent-room-templates/scripts/validate_rooms.py --suite .
```

Also validate every `plugins/<name>` directory with the current Codex plugin validator when the CLI exposes one. A `validated` or `ci` package must come from a clean repository with a resolvable `HEAD`; write the ZIP outside tracked source (for example, ignored `dist/` or the parent directory), smoke-test it, and require both `git diff --exit-code` and `git status --short --untracked-files=all` to be empty. The packager snapshots the committed tree and generates archive metadata in a disposable staging directory, so it must not rewrite tracked or create unexpected untracked source files.

## Change rules

- Keep skill frontmatter limited to fields accepted by Codex. Put implicit-invocation policy in `agents/openai.yaml`.
- Never add a complete secret to source, fixtures, output snapshots, exceptions, or documentation. Construct synthetic secret shapes at test runtime.
- Require explicit invocation and confirmation for writes, migrations, deployments, sync, browser submissions, secret access, and destructive actions.
- Preserve portable paths. Test helpers with a current working directory outside the plugin.
- Update `command-map.json` only when preserving a deliberate one-to-one migration. Do not reuse an invocation or target path.
- Validate AgentRooms with both JSON Schema and the semantic validator. Declare implicit shared-memory effects, locks, evidence, and a single memory steward.
- Update manifests, README counts, changelog, release metadata, SBOM/provenance, tests, and the DOCX where behavior changes.
- Do not add a repository, homepage, publisher, or security-contact URL unless it is verified.

Do not publish, push, deploy, or open a pull request without the package owner's explicit authorization.
