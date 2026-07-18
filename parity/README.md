# Claude to Codex capability parity

`capabilities.json` is the deterministic parity contract for the Solo Suite
adapter. The pinned reconstructed v1.0.26 Claude baseline paired with this
Codex v1.0.27 adapter is prepared for publication as
`solo-suite-plugin-v1.0.26-codex-v1.0.27-parity-source.zip`. Its SHA-256,
base archive, source commits, top-level folder, and manifest digest are pinned
in `canonical-source.json`. The exact archive and sidecar are checked in under
`parity/artifacts/` in the source checkout. The deterministic install ZIP
intentionally omits nested archives and checksum sidecars. After completion of
normal review and merge, protected-tag validation, and final private-draft asset
re-verification, the release workflow publishes and
attests the canonical archive and sidecar as separate assets alongside the
Codex package. At this source snapshot, the candidate has not yet completed that
publication workflow.

**Provenance scope:** the v1.0.26 base is independently reproducible from the
public immutable Solo Suite release, its annotated tag, and its published
provenance record. The exact 19 replacements and three generated additions are
disclosed with before/after SHA-256 digests in `source-overlay-manifest.json`.
This is the historical v1.0.26 baseline paired to this Codex adapter; it is not
a claim of byte parity with any later Claude v1.0.27 source release.

Reconstruct the canonical source from the public Claude v1.0.26 archive:

```text
python tools/build_canonical_source.py \
  --base-archive <solo-suite-plugin-v1.0.26.zip> \
  --output <solo-suite-plugin-v1.0.26-codex-v1.0.27-parity-source.zip>
```

The builder verifies the base archive digest, safely extracts it, overlays the
eight synchronized Site Doctor helpers, eight reviewed adapter command sources,
and three synchronized gate-policy files, installs the exact parity checker, regenerates the source manifest,
requires byte equality with this checkout's manifest, and runs the complete
source/target check. It emits a deterministic ZIP and adjacent SHA-256 file.
The command must reproduce the digest in `canonical-source.json`.

Verify the byte overlay independently from the builder, then rerun full parity:

```text
python tools/verify_source_overlay.py \
  --base-archive <solo-suite-plugin-v1.0.26.zip> \
  --canonical-source-archive <path-to-canonical-parity-source.zip> \
  --target .
```

For offline review or a network outage, verify the checked-in canonical result
without downloading the public base. This checks the pinned archive digest,
embedded provenance, declared result hashes, origins, and target parity; it is
not a substitute for the networked public-base provenance check:

```text
python tools/verify_source_overlay.py --canonical-only \
  --canonical-source-archive <path-to-canonical-parity-source.zip> \
  --target .
```

The verifier compares the archives directly, rejects any undeclared change,
checks the exact base and result digest for every changed path, validates the
checked-in overlay origins, and only then executes the digest-pinned parity
checker. It does not import or trust the source builder.

An independently extracted snapshot can be checked directly:

```text
python <canonical-source>/tools/parity.py check \
  --source <canonical-source> \
  --target <solo-suite-codex-checkout>
```

The checker is standard-library-only and fails closed. It verifies the exact
command-map IDs and paths, explicit-only policy, normalized bodies for all 102
command-derived skills and all non-waived specialists, byte hashes for
helper/schema files, all 159 Codex `openai.yaml` policies, and the byte-exact
Claude AgentRoom archive under `parity/claude-rooms`. Command normalization
replays the deterministic command converter and only the declared Codex path
and wording adaptations. It excludes only the suite's exact standardized
terminal output-contract block (and its legacy one-line predecessor); detailed
workflow and output instructions remain hash-bound.

Two skills are platform adapters rather than byte-identical copies:

* `ai:agent-room-templates` - Codex has a native runner, trust journal, and
  state machinery. The canonical Claude tree is archived for review.
* `solo:suite-integrity` - Codex validates Codex manifests and installed
  plugin metadata, so its implementation is intentionally native.

The only other permitted differences are the Codex-only
`full-team:full-team-orchestrator` skill and the six gate runtime support files
listed in `capabilities.json`. Any additional skill, helper, policy, or archive
file is a parity failure.
