#!/usr/bin/env python3
"""Smoke-test a packaged Solo Suite ZIP from disposable external paths."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile


EXPECTED_FOLDER = "solo-suite-codex-v1.0.11"
HISTORICAL_SOURCE_NAME = "solo-suite-plugin-v1.0.10.zip"
HISTORICAL_SOURCE_SHA256 = (
    "3d8989c6e201215812b00f9299b47b5da0e12a7d54f899bbd7cffcea905c438a"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=180,
    )
    if result.returncode:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"{result.stdout}{result.stderr}"
        )
    return result


def safe_members(archive: zipfile.ZipFile) -> list[str]:
    names = archive.namelist()
    if not names:
        raise RuntimeError("package is empty")
    top = {PurePosixPath(name).parts[0] for name in names}
    if top != {EXPECTED_FOLDER}:
        raise RuntimeError(f"package must contain exactly {EXPECTED_FOLDER!r}: {top}")
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "" in path.parts:
            raise RuntimeError(f"unsafe archive member: {name}")
        if any(part in {".venv", "__pycache__", ".docx-qa", ".git"} for part in path.parts):
            raise RuntimeError(f"development artifact leaked into package: {name}")
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    archive_path = args.archive.resolve()
    adjacent = archive_path.with_suffix(archive_path.suffix + ".sha256")
    if adjacent.is_file():
        expected = adjacent.read_text(encoding="utf-8").split()[0]
        if sha256(archive_path) != expected:
            raise RuntimeError("adjacent ZIP SHA-256 does not match")
    with tempfile.TemporaryDirectory(prefix="solo-suite-package-") as temp:
        temp_root = Path(temp)
        extract_root = temp_root / "installed"
        outside = temp_root / "disposable-project"
        outside.mkdir()
        with zipfile.ZipFile(archive_path) as archive:
            names = safe_members(archive)
            archive.extractall(extract_root)
        suite = extract_root / EXPECTED_FOLDER
        checksum_path = suite / "RELEASE-CHECKSUMS.txt"
        declared = {}
        for line in checksum_path.read_text(encoding="utf-8").splitlines():
            digest, relative = line.split("  ", 1)
            target = (suite / relative).resolve()
            try:
                target.relative_to(suite.resolve())
            except ValueError as exc:
                raise RuntimeError(f"checksum path escapes package: {relative}") from exc
            if not target.is_file() or sha256(target) != digest:
                raise RuntimeError(f"content checksum mismatch: {relative}")
            declared[relative] = digest
        actual = {
            path.relative_to(suite).as_posix()
            for path in suite.rglob("*")
            if path.is_file() and path != checksum_path
        }
        if set(declared) != actual:
            raise RuntimeError(
                "content checksum inventory mismatch: "
                f"missing={sorted(actual-set(declared))}, extra={sorted(set(declared)-actual)}"
            )
        release = json.loads((suite / "RELEASE.json").read_text(encoding="utf-8"))
        if release["version"] != "1.0.11":
            raise RuntimeError("packaged release version mismatch")
        if release.get("source_archive_required_for_build") is not False:
            raise RuntimeError("historical source archive is incorrectly required")
        if release.get("source_archive_sha256") != HISTORICAL_SOURCE_SHA256:
            raise RuntimeError("historical source archive digest is not pinned")

        provenance = json.loads(
            (suite / "RELEASE-PROVENANCE.json").read_text(encoding="utf-8")
        )
        if provenance.get("build_type") != "reproducible-zip-from-git-tree":
            raise RuntimeError("package provenance does not identify the reproducible build")
        materials = provenance.get("materials", [])
        if not isinstance(materials, list):
            raise RuntimeError("package provenance materials must be a list")
        historical = next(
            (
                item for item in materials
                if isinstance(item, dict)
                and item.get("uri") == HISTORICAL_SOURCE_NAME
            ),
            None,
        )
        historical_digest = historical.get("digest") if historical else None
        if not (
            isinstance(historical_digest, dict)
            and historical_digest.get("sha256") == HISTORICAL_SOURCE_SHA256
        ):
            raise RuntimeError("package provenance lacks the pinned historical material")
        if historical.get("required_for_build") is not False:
            raise RuntimeError("historical material is incorrectly marked as a build input")
        if provenance.get("validation_state") in {"validated", "ci"}:
            commit = provenance.get("source_git_commit", "")
            if not (
                isinstance(commit, str)
                and len(commit) in {40, 64}
                and all(character in "0123456789abcdef" for character in commit)
            ):
                raise RuntimeError("validated package lacks a full Git source commit")
            if provenance.get("source_git_dirty") is not False:
                raise RuntimeError("validated package provenance identifies a dirty source")
            git_materials = [
                item for item in materials
                if isinstance(item, dict)
                and isinstance(item.get("digest"), dict)
                and item["digest"].get("gitCommit") == commit
            ]
            if len(git_materials) != 1:
                raise RuntimeError("validated package lacks its Git material identity")

        python = sys.executable
        run([python, str(suite / "tools/validate_plugins.py")], outside)
        self_check = suite / "plugins/solo/skills/suite-integrity/scripts/self_check.py"
        run([python, str(self_check), str(suite), "-"], outside)
        rooms = suite / "plugins/ai/skills/agent-room-templates/scripts/validate_rooms.py"
        run([python, str(rooms), "--suite", str(suite)], outside)

        cache_plugin = temp_root / "codex-cache/site-doctor/1.0.11"
        shutil.copytree(suite / "plugins/site-doctor", cache_plugin)
        run([python, str(self_check), str(cache_plugin), "-"], outside)

        fixture = outside / "package.json"
        fixture.write_text('{"dependencies":{"demo":"1.2.3"}}\n', encoding="utf-8")
        launcher = cache_plugin / "scripts/run_helper.py"
        helper = run(
            [python, str(launcher), "dependency-audit/check-deps", str(outside)],
            outside,
        )
        if "Node / npm" not in helper.stdout:
            raise RuntimeError("installed helper did not inspect disposable project")
        print(f"PASS one top-level folder with {len(names)} file(s)")
        print("PASS adjacent ZIP digest and internal content checksums")
        print("PASS source-checkout and installed-cache self-checks")
        print("PASS helper executed from disposable external working directory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
