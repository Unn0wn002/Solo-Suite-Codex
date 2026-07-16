#!/usr/bin/env python3
"""Reconstruct and package the pinned Claude v1.0.26 baseline for Codex v1.0.27.

The public Claude v1.0.26 archive is the immutable base. Reviewed release-sync
files are overlaid before the canonical parity manifest is
regenerated.  A build succeeds only when that manifest is byte-identical to
the Codex checkout's pinned manifest and the full source/target parity check
passes.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
TARGET_VERSION = "1.0.27"
SOURCE_FOLDER = "solo-suite-plugin-v1.0.26"
BASE_ARCHIVE_NAME = f"{SOURCE_FOLDER}.zip"
BASE_ARCHIVE_SHA256 = (
    "b691905f8ade4c2fb7e0084a46f537c9be8d7b2bf0f4d160c38c5e930aed1d43"
)
BASE_GIT_COMMIT = "99eb54f9113a1dab279135024ced11dc88970ef5"
BASE_TAG = "v1.0.26"
BASE_TAG_OBJECT = "2846a430cc7391218346e087cb90b0e515934883"
BASE_TREE_OID = "c5992b7b9082e160705c41421603d31471025403"
BASE_REPOSITORY = "https://github.com/Unn0wn002/solo-suite"
BASE_RELEASE_URL = f"{BASE_REPOSITORY}/releases/tag/{BASE_TAG}"
BASE_ASSET_URL = (
    f"{BASE_REPOSITORY}/releases/download/{BASE_TAG}/{BASE_ARCHIVE_NAME}"
)
BASE_PROVENANCE_URL = (
    f"{BASE_REPOSITORY}/releases/download/{BASE_TAG}/provenance.json"
)
BASE_PROVENANCE_SHA256 = (
    "c55f8fb0700d015af778d081037ae623d962097c2ea1a912498b84bfa4f31c6b"
)
TARGET_SYNC_COMMIT = "3d16f56fd4a924bd56da3b57de69b4dc3f52f684"
SOURCE_DATE_EPOCH = 1_784_103_592
OUTPUT_NAME = (
    f"{SOURCE_FOLDER}-codex-v{TARGET_VERSION}-parity-source.zip"
)
EXPECTED_CAPABILITIES_SHA256 = (
    "f1ea0261f28de025d0626f5d1bdc4ded6667b4167d1dc310e74c79349cf9ec6a"
)
EXPECTED_OVERLAY_MANIFEST_SHA256 = (
    "e3e8eb70863549d1f892d3f0a550e8dbbb88b5a15563ce39b0016c5484868d61"
)
EXPECTED_ARCHIVE_SHA256 = (
    "49a0eab223d2014506fade29189419e7d096f3b935be35078d1a46e58d6db652"
)

HELPER_OVERLAYS = (
    "plugins/site-doctor/lib/url_guard.py",
    "plugins/site-doctor/skills/compliance-check/scripts/scan_trackers.py",
    "plugins/site-doctor/skills/dependency-audit/scripts/check_deps.py",
    "plugins/site-doctor/skills/email-deliverability/scripts/check_email_dns.py",
    "plugins/site-doctor/skills/security-review/scripts/scan_secrets.py",
    "plugins/site-doctor/skills/seo-optimization/scripts/extract_meta.py",
    "plugins/site-doctor/skills/website-audit/scripts/check_headers.py",
    "plugins/site-doctor/skills/website-audit/scripts/check_links.py",
)
COMMAND_OVERLAYS = (
    "plugins/browser/commands/form-submit-test.md",
    "plugins/release/commands/deploy-plan.md",
    "plugins/release/commands/rollback-plan.md",
    "plugins/gate/commands/production-ready.md",
    "plugins/full-team/commands/verify.md",
    "plugins/solo/commands/full-team-dev.md",
    "plugins/solo/commands/sync-grafana.md",
    "plugins/solo/commands/sync-obsidian.md",
)
GATE_POLICY_OVERLAYS = (
    "plugins/gate/skills/production-readiness-reviewer/SKILL.md",
    "plugins/gate/lib/gate_policy.py",
    "plugins/gate/skills/production-readiness-reviewer/scripts/check_evidence.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _safe_relative(name: str) -> PurePosixPath:
    value = PurePosixPath(name)
    if (
        value.is_absolute()
        or "\\" in name
        or not value.parts
        or any(part in {"", ".", ".."} for part in value.parts)
        or value.parts[0] != SOURCE_FOLDER
    ):
        raise RuntimeError(f"unsafe or unexpected source archive member: {name!r}")
    return value


def extract_base(archive_path: Path, destination: Path) -> Path:
    if not archive_path.is_file():
        raise RuntimeError(f"base source archive does not exist: {archive_path}")
    actual = sha256(archive_path)
    if actual != BASE_ARCHIVE_SHA256:
        raise RuntimeError(
            "base source archive digest mismatch: "
            f"expected {BASE_ARCHIVE_SHA256}, got {actual}"
        )
    with zipfile.ZipFile(archive_path) as archive:
        if not archive.infolist():
            raise RuntimeError("base source archive is empty")
        seen: set[str] = set()
        for info in archive.infolist():
            relative = _safe_relative(info.filename)
            key = relative.as_posix()
            if key in seen:
                raise RuntimeError(f"duplicate source archive member: {info.filename!r}")
            seen.add(key)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise RuntimeError(f"source archive contains a symbolic link: {info.filename}")
            target = destination.joinpath(*relative.parts)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(info))
    source = destination / SOURCE_FOLDER
    if not source.is_dir():
        raise RuntimeError(f"base source archive lacks {SOURCE_FOLDER!r}")
    return source


def overlay_files(source: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for relative in HELPER_OVERLAYS:
        origin = ROOT / relative
        role = "target-synchronized-helper"
        if not origin.is_file():
            raise RuntimeError(f"helper overlay is missing: {origin}")
        destination = source / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(origin.read_bytes())
        records.append({
            "path": relative,
            "role": role,
            "origin": relative,
            "sha256": sha256(origin),
        })
    for relative in COMMAND_OVERLAYS:
        origin = ROOT / "parity/canonical-source-overrides" / relative
        if not origin.is_file():
            raise RuntimeError(f"Claude command overlay is missing: {origin}")
        destination = source / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(origin.read_bytes())
        records.append({
            "path": relative,
            "role": "reviewed-adapter-command-source",
            "origin": origin.relative_to(ROOT).as_posix(),
            "sha256": sha256(origin),
        })
    for relative in GATE_POLICY_OVERLAYS:
        origin = ROOT / "parity/canonical-source-overrides" / relative
        if not origin.is_file():
            raise RuntimeError(f"gate policy overlay is missing: {origin}")
        destination = source / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(origin.read_bytes())
        records.append({
            "path": relative,
            "role": "synchronized-gate-policy-source",
            "origin": origin.relative_to(ROOT).as_posix(),
            "sha256": sha256(origin),
        })
    checker = ROOT / "tools/parity.py"
    destination = source / "tools/parity.py"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(checker.read_bytes())
    records.append({
        "path": "tools/parity.py",
        "role": "canonical-parity-checker",
        "origin": "tools/parity.py",
        "sha256": sha256(checker),
    })
    return records


def run_parity(source: Path) -> None:
    checker = source / "tools/parity.py"
    generated = subprocess.run(
        [sys.executable, str(checker), "generate", "--source", str(source)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    if generated.returncode:
        raise RuntimeError(
            "canonical source manifest generation failed:\n"
            f"{generated.stdout}{generated.stderr}"
        )
    source_manifest = source / "parity/capabilities.json"
    target_manifest = ROOT / "parity/capabilities.json"
    source_digest = sha256(source_manifest)
    if source_digest != EXPECTED_CAPABILITIES_SHA256:
        raise RuntimeError(
            "canonical source manifest has an unexpected digest: "
            f"expected {EXPECTED_CAPABILITIES_SHA256}, got {source_digest}"
        )
    if source_manifest.read_bytes() != target_manifest.read_bytes():
        raise RuntimeError(
            "generated canonical source manifest is not byte-identical to "
            "target parity/capabilities.json"
        )
    checked = subprocess.run(
        [
            sys.executable,
            str(checker),
            "check",
            "--source",
            str(source),
            "--target",
            str(ROOT),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    if checked.returncode:
        raise RuntimeError(
            "canonical source does not match the Codex target:\n"
            f"{checked.stdout}{checked.stderr}"
        )
    print(generated.stdout.strip())
    print(checked.stdout.strip())


def tree_digest(source: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(
        (
            path for path in source.rglob("*")
            if path.is_file() and path.name != "PARITY-SOURCE.json"
        ),
        key=lambda path: path.relative_to(source).as_posix(),
    ):
        relative = path.relative_to(source).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256(path)))
        digest.update(b"\n")
    return digest.hexdigest()


def write_provenance(source: Path, overlays: list[dict[str, str]]) -> None:
    instant = datetime.fromtimestamp(SOURCE_DATE_EPOCH, timezone.utc)
    write_json(source / "PARITY-SOURCE.json", {
        "schema": "solo-suite/canonical-parity-source-v1",
        "source_suite": "solo-suite-plugin",
        "source_version": "1.0.26",
        "target_suite": "solo-suite-codex",
        "target_version": TARGET_VERSION,
        "source_date_epoch": SOURCE_DATE_EPOCH,
        "built_at": instant.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "base_archive": BASE_ARCHIVE_NAME,
        "base_archive_sha256": BASE_ARCHIVE_SHA256,
        "base_git_commit": BASE_GIT_COMMIT,
        "base_tag": BASE_TAG,
        "base_tag_object": BASE_TAG_OBJECT,
        "base_tree_oid": BASE_TREE_OID,
        "base_repository": BASE_REPOSITORY,
        "base_release_url": BASE_RELEASE_URL,
        "base_asset_url": BASE_ASSET_URL,
        "base_provenance_url": BASE_PROVENANCE_URL,
        "base_provenance_sha256": BASE_PROVENANCE_SHA256,
        "target_sync_commit": TARGET_SYNC_COMMIT,
        "capabilities_sha256": EXPECTED_CAPABILITIES_SHA256,
        "tree_sha256": tree_digest(source),
        "overlays": overlays,
        "verification": [
            "python tools/parity.py generate --source <canonical-source>",
            "python tools/parity.py check --source <canonical-source> --target <codex-target>",
        ],
    })


def package_source(source: Path, output: Path) -> str:
    instant = datetime.fromtimestamp(SOURCE_DATE_EPOCH, timezone.utc)
    zip_time = (
        instant.year,
        instant.month,
        instant.day,
        instant.hour,
        instant.minute,
        instant.second - instant.second % 2,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for path in sorted(
            (path for path in source.rglob("*") if path.is_file()),
            key=lambda path: path.relative_to(source).as_posix(),
        ):
            relative = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(f"{SOURCE_FOLDER}/{relative}", zip_time)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    digest = sha256(output)
    with output.with_suffix(output.suffix + ".sha256").open(
        "w", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(f"{digest}  {output.name}\n")
    return digest


def verify_published_overlay(base_archive: Path, output: Path) -> None:
    manifest = ROOT / "parity/source-overlay-manifest.json"
    actual_manifest_digest = sha256(manifest)
    if actual_manifest_digest != EXPECTED_OVERLAY_MANIFEST_SHA256:
        raise RuntimeError(
            "source overlay manifest digest mismatch: "
            f"expected {EXPECTED_OVERLAY_MANIFEST_SHA256}, "
            f"got {actual_manifest_digest}"
        )
    verifier = ROOT / "tools/verify_source_overlay.py"
    checked = subprocess.run(
        [
            sys.executable,
            str(verifier),
            "--base-archive",
            str(base_archive),
            "--canonical-source-archive",
            str(output),
            "--manifest",
            str(manifest),
            "--target",
            str(ROOT),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    if checked.returncode:
        raise RuntimeError(
            "published source overlay verification failed:\n"
            f"{checked.stdout}{checked.stderr}"
        )
    print(checked.stdout.strip())


def build(base_archive: Path, output: Path) -> str:
    base_archive = base_archive.resolve()
    output = output.resolve()
    with tempfile.TemporaryDirectory(prefix="solo-suite-canonical-source-") as temp:
        source = extract_base(base_archive, Path(temp))
        overlays = overlay_files(source)
        run_parity(source)
        write_provenance(source, overlays)
        digest = package_source(source, output)
    verify_published_overlay(base_archive, output)
    if EXPECTED_ARCHIVE_SHA256 and digest != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError(
            "canonical source archive digest mismatch: "
            f"expected {EXPECTED_ARCHIVE_SHA256}, got {digest}"
        )
    return digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base_group = parser.add_mutually_exclusive_group()
    base_group.add_argument("--base-archive", type=Path)
    base_group.add_argument(
        "--fetch-public-base", action="store_true",
        help="download the authenticated base asset/provenance pinned in parity/source-overlay-manifest.json",
    )
    parser.add_argument("--output", type=Path, default=ROOT.parent / OUTPUT_NAME)
    args = parser.parse_args()
    try:
        if args.fetch_public_base:
            from verify_source_overlay import fetch_public_base, load_manifest

            manifest = load_manifest(ROOT / "parity/source-overlay-manifest.json")
            with tempfile.TemporaryDirectory(prefix="solo-suite-public-base-") as temp:
                base_archive = fetch_public_base(
                    manifest, Path(temp) / manifest["base_archive"]
                )
                digest = build(base_archive, args.output)
        elif args.base_archive is not None:
            digest = build(args.base_archive, args.output)
        else:
            parser.error("one of --base-archive or --fetch-public-base is required")
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        parser.error(str(exc))
    output = args.output.resolve()
    print(f"CANONICAL_SOURCE {output}")
    print(f"SHA256 {digest}")
    print(f"SOURCE_DATE_EPOCH {SOURCE_DATE_EPOCH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
