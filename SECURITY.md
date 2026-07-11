# Security policy

## Supported release

Solo Suite Codex `1.0.11` is the supported release in this package. The original `1.0.10` archive is optional external historical material: only its verified SHA-256 digest is pinned here, and the archive is neither bundled nor required to build v1.0.11. It must not be treated as containing the v1.0.11 hardening.

## Reporting a vulnerability

Do not include credentials, tokens, private keys, customer data, or an exploitable production target in a report. Use a [private GitHub security advisory](https://github.com/Unn0wn002/Solo-Suite-Codex/security/advisories/new) when you have repository access, or the same private channel through which you received the package. Do not disclose a vulnerability in a public issue.

Include the affected plugin/skill, release version, platform, minimal reproduction with synthetic data, impact, and any proposed mitigation. Avoid public disclosure until the maintainer has had a reasonable opportunity to investigate and distribute a corrected package.

## Security boundaries

- Skills are instruction packages, not a sandbox. Review proposed commands and diffs before approving writes.
- Mutation, deployment, external sync, secret handling, browser submission, and production workflows are explicit-only and require confirmation at the point of effect.
- `.solo/config.md` may name token environment variables but must never store token values. Keep it out of version control.
- Site Doctor network helpers block unsafe targets and revalidate redirects, but this does not replace network egress controls.
- The structural self-check verifies package consistency; it is not a security certification or production-readiness verdict.
- AgentRooms files are declarative plans. A runner must enforce their locks, workspaces, stage order, evidence, and confirmation rules.

## Release integrity

Verify the distributed ZIP with its adjacent `.sha256` file or `RELEASE-CHECKSUMS.txt`. Review `RELEASE-PROVENANCE.json` and `SBOM.spdx.json` before installation. Publication packages are built only from a clean committed tree; the packager reads committed blobs directly so untracked Git attributes, replacement refs, filters, and working-tree line endings cannot alter the archive, and it refuses to overwrite tracked source. A mismatch means the artifact must not be installed.
