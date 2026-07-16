#!/usr/bin/env python3
"""Verify the exact base-to-canonical Claude source overlay.

This verifier is deliberately independent of build_canonical_source.py.  It
compares the two archives directly, requires the complete changed-file set and
both sides of every changed-file digest to match the published manifest, and
can then run the digest-pinned parity checker against a Codex target checkout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "parity/source-overlay-manifest.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class VerificationError(RuntimeError):
    """Raised when an archive or overlay violates the published contract."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _download_pinned(url: str, limit: int = 64 * 1024 * 1024) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {
        "github.com",
        "objects.githubusercontent.com",
        "release-assets.githubusercontent.com",
    }:
        raise VerificationError(f"refusing untrusted public-source URL: {url}")
    request = Request(url, headers={"User-Agent": "solo-suite-overlay-verifier/1"})
    try:
        with urlopen(request, timeout=90) as response:
            final = urlparse(response.geturl())
            if final.scheme != "https" or final.hostname not in {
                "github.com",
                "objects.githubusercontent.com",
                "release-assets.githubusercontent.com",
            }:
                raise VerificationError(
                    f"public-source redirect left the permitted GitHub hosts: {response.geturl()}"
                )
            data = response.read(limit + 1)
    except VerificationError:
        raise
    except OSError as exc:
        raise VerificationError(f"could not download public source material: {exc}") from exc
    if len(data) > limit:
        raise VerificationError("public source material exceeds the download limit")
    return data


def fetch_public_base(manifest: dict, destination: Path) -> Path:
    asset_url = manifest.get("base_asset_url")
    provenance_url = manifest.get("base_provenance_url")
    expected_provenance = manifest.get("base_provenance_sha256")
    if not all(isinstance(value, str) and value for value in (
        asset_url, provenance_url, expected_provenance,
    )):
        raise VerificationError(
            "overlay manifest lacks authenticated public base asset/provenance URLs"
        )
    asset = _download_pinned(asset_url)
    digest = sha256_bytes(asset)
    if digest != manifest["base_archive_sha256"]:
        raise VerificationError(
            "downloaded public base digest mismatch: "
            f"expected {manifest['base_archive_sha256']}, got {digest}"
        )
    provenance = _download_pinned(provenance_url, limit=4 * 1024 * 1024)
    provenance_digest = sha256_bytes(provenance)
    if provenance_digest != expected_provenance:
        raise VerificationError(
            "downloaded public provenance digest mismatch: "
            f"expected {expected_provenance}, got {provenance_digest}"
        )
    try:
        record = json.loads(provenance.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"public provenance is not valid JSON: {exc}") from exc
    if (
        record.get("source_commit") != manifest.get("base_git_commit")
        or record.get("source_tree_oid") != manifest.get("base_tree_oid")
    ):
        raise VerificationError(
            "public provenance commit/tree does not match the overlay manifest"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(asset)
    return destination


def load_manifest(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read overlay manifest {path}: {exc}") from exc
    if payload.get("schema") != "solo-suite/source-overlay-manifest-v1":
        raise VerificationError("overlay manifest has an unsupported schema")
    for key in ("base_archive_sha256", "canonical_archive_sha256"):
        if not SHA256_RE.fullmatch(str(payload.get(key, ""))):
            raise VerificationError(f"overlay manifest has an invalid {key}")
    top = payload.get("top_level_folder")
    if not isinstance(top, str) or not top or "/" in top or "\\" in top:
        raise VerificationError("overlay manifest has an invalid top_level_folder")
    changes = payload.get("changes")
    if not isinstance(changes, list) or not changes:
        raise VerificationError("overlay manifest must declare changed files")
    seen: set[str] = set()
    for item in changes:
        if not isinstance(item, dict):
            raise VerificationError("overlay manifest change entries must be objects")
        changed_path = item.get("path")
        if not isinstance(changed_path, str) or not _safe_relative(changed_path):
            raise VerificationError(f"unsafe overlay path: {changed_path!r}")
        if changed_path in seen:
            raise VerificationError(f"duplicate overlay path: {changed_path}")
        seen.add(changed_path)
        change = item.get("change")
        if change not in {"add", "replace", "delete"}:
            raise VerificationError(f"invalid change kind for {changed_path}: {change!r}")
        before = item.get("base_sha256")
        after = item.get("result_sha256")
        if change == "add":
            valid = before is None and SHA256_RE.fullmatch(str(after or ""))
        elif change == "delete":
            valid = SHA256_RE.fullmatch(str(before or "")) and after is None
        else:
            valid = (
                SHA256_RE.fullmatch(str(before or ""))
                and SHA256_RE.fullmatch(str(after or ""))
            )
        if not valid:
            raise VerificationError(f"invalid before/after digests for {changed_path}")
        origin = item.get("origin")
        if origin is not None and (
            not isinstance(origin, str) or not _safe_relative(origin)
        ):
            raise VerificationError(f"unsafe overlay origin for {changed_path}")
    return payload


def _safe_relative(value: str) -> bool:
    path = PurePosixPath(value)
    return (
        bool(value)
        and not path.is_absolute()
        and "\\" not in value
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def read_archive(path: Path, expected_digest: str, top_level: str) -> dict[str, bytes]:
    if not path.is_file():
        raise VerificationError(f"archive does not exist: {path}")
    actual_digest = sha256_file(path)
    if actual_digest != expected_digest:
        raise VerificationError(
            f"archive digest mismatch for {path.name}: "
            f"expected {expected_digest}, got {actual_digest}"
        )
    files: dict[str, bytes] = {}
    prefix = f"{top_level}/"
    try:
        with zipfile.ZipFile(path) as archive:
            if not archive.infolist():
                raise VerificationError(f"archive is empty: {path}")
            seen_members: set[str] = set()
            for info in archive.infolist():
                name = info.filename
                member = PurePosixPath(name)
                if (
                    member.is_absolute()
                    or "\\" in name
                    or any(part in {"", ".", ".."} for part in member.parts)
                    or not name.startswith(prefix)
                ):
                    raise VerificationError(f"unsafe archive member: {name!r}")
                if name in seen_members:
                    raise VerificationError(f"duplicate archive member: {name!r}")
                seen_members.add(name)
                if stat.S_ISLNK(info.external_attr >> 16):
                    raise VerificationError(f"archive contains a symbolic link: {name}")
                if info.is_dir():
                    continue
                relative = name[len(prefix):]
                if not _safe_relative(relative):
                    raise VerificationError(f"unsafe archive member: {name!r}")
                if relative in files:
                    raise VerificationError(f"duplicate relative archive member: {relative}")
                files[relative] = archive.read(info)
    except zipfile.BadZipFile as exc:
        raise VerificationError(f"invalid ZIP archive {path}: {exc}") from exc
    return files


def _digest(value: bytes | None) -> str | None:
    return None if value is None else sha256_bytes(value)


def _actual_changes(
    base: dict[str, bytes], canonical: dict[str, bytes]
) -> dict[str, tuple[str | None, str | None, str]]:
    result: dict[str, tuple[str | None, str | None, str]] = {}
    for path in sorted(set(base) | set(canonical)):
        before = base.get(path)
        after = canonical.get(path)
        if before == after:
            continue
        if before is None:
            kind = "add"
        elif after is None:
            kind = "delete"
        else:
            kind = "replace"
        result[path] = (_digest(before), _digest(after), kind)
    return result


def _verify_embedded_provenance(manifest: dict, canonical: dict[str, bytes]) -> None:
    try:
        provenance = json.loads(canonical["PARITY-SOURCE.json"].decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"canonical PARITY-SOURCE.json is invalid: {exc}") from exc
    for manifest_key, provenance_key in (
        ("base_archive_sha256", "base_archive_sha256"),
        ("base_git_commit", "base_git_commit"),
        ("target_sync_commit", "target_sync_commit"),
        ("capabilities_sha256", "capabilities_sha256"),
    ):
        if provenance.get(provenance_key) != manifest.get(manifest_key):
            raise VerificationError(
                f"embedded provenance {provenance_key} does not match overlay manifest"
            )
    expected_overlays = []
    for item in manifest["changes"]:
        role = item.get("provenance_role")
        if role is None:
            continue
        expected_overlays.append({
            "path": item["path"],
            "role": role,
            "origin": item["origin"],
            "sha256": item["result_sha256"],
        })
    if provenance.get("overlays") != expected_overlays:
        raise VerificationError(
            "embedded provenance overlay list does not match overlay manifest"
        )


def _verify_origins(manifest: dict, target: Path) -> None:
    root = target.resolve()
    for item in manifest["changes"]:
        origin = item.get("origin")
        if origin is None:
            continue
        candidate = (root / Path(*PurePosixPath(origin).parts)).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise VerificationError(f"overlay origin escapes target: {origin}") from exc
        if not candidate.is_file():
            raise VerificationError(f"overlay origin does not exist: {origin}")
        actual = sha256_file(candidate)
        if actual != item["result_sha256"]:
            raise VerificationError(
                f"overlay origin digest mismatch for {origin}: "
                f"expected {item['result_sha256']}, got {actual}"
            )


def _run_parity(canonical: dict[str, bytes], top_level: str, target: Path) -> str:
    with tempfile.TemporaryDirectory(prefix="solo-suite-overlay-verify-") as temp:
        source = Path(temp) / top_level
        for relative, content in canonical.items():
            destination = source.joinpath(*PurePosixPath(relative).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
        checker = source / "tools/parity.py"
        result = subprocess.run(
            [
                sys.executable,
                str(checker),
                "check",
                "--source",
                str(source),
                "--target",
                str(target.resolve()),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        if result.returncode:
            raise VerificationError(
                "canonical source/target parity failed:\n"
                f"{result.stdout}{result.stderr}"
            )
        return result.stdout.strip()


def verify(
    base_archive: Path,
    canonical_archive: Path,
    manifest_path: Path,
    target: Path | None = None,
) -> tuple[int, str | None]:
    manifest = load_manifest(manifest_path)
    top_level = manifest["top_level_folder"]
    base = read_archive(
        base_archive.resolve(), manifest["base_archive_sha256"], top_level
    )
    canonical = read_archive(
        canonical_archive.resolve(), manifest["canonical_archive_sha256"], top_level
    )
    expected = {
        item["path"]: (
            item["base_sha256"],
            item["result_sha256"],
            item["change"],
        )
        for item in manifest["changes"]
    }
    actual = _actual_changes(base, canonical)
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        unexpected = sorted(set(actual) - set(expected))
        mismatched = sorted(
            path for path in set(expected) & set(actual)
            if expected[path] != actual[path]
        )
        raise VerificationError(
            "archive delta does not match overlay manifest: "
            f"missing={missing}, unexpected={unexpected}, mismatched={mismatched}"
        )
    _verify_embedded_provenance(manifest, canonical)
    parity_output = None
    if target is not None:
        _verify_origins(manifest, target)
        parity_output = _run_parity(canonical, top_level, target)
    return len(actual), parity_output


def verify_canonical_only(
    canonical_archive: Path,
    manifest_path: Path,
    target: Path | None = None,
) -> tuple[int, str | None]:
    """Verify the checked-in canonical archive without downloading the base.

    The archive digest pins every member, so this mode can prove that the
    checked-in result has not changed while deliberately leaving the
    public-base provenance check to the networked mode.  This is useful for
    offline CI/review and is reported separately so it cannot be mistaken for
    full source provenance.
    """

    manifest = load_manifest(manifest_path)
    canonical = read_archive(
        canonical_archive.resolve(),
        manifest["canonical_archive_sha256"],
        manifest["top_level_folder"],
    )
    _verify_embedded_provenance(manifest, canonical)
    for item in manifest["changes"]:
        path = item["path"]
        content = canonical.get(path)
        if item["change"] == "delete":
            if content is not None:
                raise VerificationError(
                    f"canonical archive retains declared deleted path: {path}"
                )
            continue
        if content is None:
            raise VerificationError(
                f"canonical archive lacks declared result path: {path}"
            )
        actual = sha256_bytes(content)
        if actual != item["result_sha256"]:
            raise VerificationError(
                f"canonical result digest mismatch for {path}: "
                f"expected {item['result_sha256']}, got {actual}"
            )
    parity_output = None
    if target is not None:
        _verify_origins(manifest, target)
        parity_output = _run_parity(
            canonical, manifest["top_level_folder"], target
        )
    return len(manifest["changes"]), parity_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base_group = parser.add_mutually_exclusive_group()
    base_group.add_argument("--base-archive", type=Path)
    base_group.add_argument(
        "--fetch-public-base", action="store_true",
        help="download and authenticate the base asset/provenance URLs pinned in the manifest",
    )
    base_group.add_argument(
        "--canonical-only", action="store_true",
        help="verify the checked-in canonical archive and embedded provenance without downloading the base",
    )
    parser.add_argument("--canonical-source-archive", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--target", type=Path)
    args = parser.parse_args()
    try:
        manifest = load_manifest(args.manifest)
        if args.fetch_public_base:
            with tempfile.TemporaryDirectory(prefix="solo-suite-public-base-") as temp:
                base_archive = fetch_public_base(manifest, Path(temp) / manifest["base_archive"])
                count, parity_output = verify(
                    base_archive,
                    args.canonical_source_archive,
                    args.manifest,
                    args.target,
                )
        elif args.base_archive is not None:
            count, parity_output = verify(
                args.base_archive,
                args.canonical_source_archive,
                args.manifest,
                args.target,
            )
        elif args.canonical_only:
            count, parity_output = verify_canonical_only(
                args.canonical_source_archive,
                args.manifest,
                args.target,
            )
        else:
            parser.error(
                "one of --base-archive, --fetch-public-base, or --canonical-only is required"
            )
    except (OSError, VerificationError) as exc:
        parser.error(str(exc))
    if args.fetch_public_base:
        print("PUBLIC BASE PASS: authenticated pinned asset and provenance record")
    elif args.canonical_only:
        print(
            "OFFLINE CANONICAL PASS: checked-in archive digest and embedded "
            "provenance verified (public base not downloaded)"
        )
    print(f"OVERLAY PASS: {count} exact archive differences verified")
    if parity_output:
        print(parity_output)
    caveat = load_manifest(args.manifest)["provenance_caveat"]
    print(f"PROVENANCE CAVEAT: {caveat}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
