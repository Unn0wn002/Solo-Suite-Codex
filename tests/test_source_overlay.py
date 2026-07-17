"""Tests for the independently replayable canonical-source overlay contract."""

from __future__ import annotations

import hashlib
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import ssl
import sys
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.request import Request
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "source_overlay_verifier", ROOT / "tools/verify_source_overlay.py"
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VERIFY
SPEC.loader.exec_module(VERIFY)
BUILD_SPEC = importlib.util.spec_from_file_location(
    "canonical_source_builder", ROOT / "tools/build_canonical_source.py"
)
assert BUILD_SPEC is not None and BUILD_SPEC.loader is not None
BUILDER = importlib.util.module_from_spec(BUILD_SPEC)
sys.modules[BUILD_SPEC.name] = BUILDER
BUILD_SPEC.loader.exec_module(BUILDER)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_zip(path: Path, top: str, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        for relative, content in sorted(files.items()):
            archive.writestr(f"{top}/{relative}", content)


class PublishedOverlayTests(unittest.TestCase):
    class _Response:
        def __init__(self, data: bytes, url: str) -> None:
            self.data = data
            self.url = url

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def geturl(self) -> str:
            return self.url

        def read(self, _limit: int) -> bytes:
            return self.data

    def test_download_retries_transient_network_failure(self) -> None:
        attempts = 0
        sleeps: list[float] = []

        def opener(_request, *, timeout: int):
            nonlocal attempts
            self.assertEqual(timeout, 90)
            attempts += 1
            if attempts == 1:
                raise VERIFY.URLError(
                    ConnectionResetError(104, "connection reset")
                )
            return self._Response(b"pinned", "https://release-assets.githubusercontent.com/base.zip")

        result = VERIFY._download_pinned(
            "https://github.com/owner/repo/releases/download/v1/base.zip",
            opener=opener,
            sleeper=sleeps.append,
        )
        self.assertEqual(result, b"pinned")
        self.assertEqual(attempts, 2)
        self.assertEqual(sleeps, [1.0])

    def test_download_fails_closed_after_bounded_retries(self) -> None:
        attempts = 0
        sleeps: list[float] = []

        def opener(_request, *, timeout: int):
            nonlocal attempts
            self.assertEqual(timeout, 90)
            attempts += 1
            raise ConnectionResetError("connection reset")

        with self.assertRaisesRegex(
            VERIFY.VerificationError, "after 3 attempts: connection reset"
        ):
            VERIFY._download_pinned(
                "https://github.com/owner/repo/releases/download/v1/base.zip",
                opener=opener,
                sleeper=sleeps.append,
            )
        self.assertEqual(attempts, 3)
        self.assertEqual(sleeps, [1.0, 2.0])

    def test_download_retries_transient_http_status(self) -> None:
        attempts = 0
        sleeps: list[float] = []

        def opener(request, *, timeout: int):
            nonlocal attempts
            self.assertEqual(timeout, 90)
            attempts += 1
            if attempts == 1:
                raise HTTPError(
                    request.full_url, 503, "busy", hdrs={}, fp=BytesIO()
                )
            return self._Response(b"pinned", "https://objects.githubusercontent.com/base.zip")

        result = VERIFY._download_pinned(
            "https://github.com/owner/repo/releases/download/v1/base.zip",
            opener=opener,
            sleeper=sleeps.append,
        )
        self.assertEqual(result, b"pinned")
        self.assertEqual(attempts, 2)
        self.assertEqual(sleeps, [1.0])

    def test_download_does_not_retry_certificate_failure(self) -> None:
        attempts = 0
        sleeps: list[float] = []

        def opener(_request, *, timeout: int):
            nonlocal attempts
            self.assertEqual(timeout, 90)
            attempts += 1
            raise ssl.SSLCertVerificationError("certificate rejected")

        with self.assertRaisesRegex(
            VERIFY.VerificationError, "certificate rejected"
        ):
            VERIFY._download_pinned(
                "https://github.com/owner/repo/releases/download/v1/base.zip",
                opener=opener,
                sleeper=sleeps.append,
            )
        self.assertEqual(attempts, 1)
        self.assertEqual(sleeps, [])

    def test_download_does_not_retry_unrelated_os_error(self) -> None:
        attempts = 0
        sleeps: list[float] = []

        def opener(_request, *, timeout: int):
            nonlocal attempts
            self.assertEqual(timeout, 90)
            attempts += 1
            raise PermissionError("local transport policy")

        with self.assertRaisesRegex(
            VERIFY.VerificationError, "local transport policy"
        ):
            VERIFY._download_pinned(
                "https://github.com/owner/repo/releases/download/v1/base.zip",
                opener=opener,
                sleeper=sleeps.append,
            )
        self.assertEqual(attempts, 1)
        self.assertEqual(sleeps, [])

    def test_download_does_not_retry_permanent_http_status(self) -> None:
        attempts = 0
        sleeps: list[float] = []

        def opener(request, *, timeout: int):
            nonlocal attempts
            self.assertEqual(timeout, 90)
            attempts += 1
            raise HTTPError(request.full_url, 404, "not found", hdrs={}, fp=BytesIO())

        with self.assertRaisesRegex(
            VERIFY.VerificationError, "not found"
        ):
            VERIFY._download_pinned(
                "https://github.com/owner/repo/releases/download/v1/base.zip",
                opener=opener,
                sleeper=sleeps.append,
            )
        self.assertEqual(attempts, 1)
        self.assertEqual(sleeps, [])

    def test_download_does_not_retry_an_untrusted_redirect(self) -> None:
        attempts = 0
        sleeps: list[float] = []

        def opener(_request, *, timeout: int):
            nonlocal attempts
            self.assertEqual(timeout, 90)
            attempts += 1
            return self._Response(b"pinned", "https://example.com/base.zip")

        with self.assertRaisesRegex(
            VERIFY.VerificationError, "redirect left the permitted GitHub hosts"
        ):
            VERIFY._download_pinned(
                "https://github.com/owner/repo/releases/download/v1/base.zip",
                opener=opener,
                sleeper=sleeps.append,
            )
        self.assertEqual(attempts, 1)
        self.assertEqual(sleeps, [])

    def test_malformed_source_url_fails_closed(self) -> None:
        with self.assertRaisesRegex(VERIFY.VerificationError, "is malformed"):
            VERIFY._download_pinned("https://[malformed")

    def test_redirect_handler_rejects_an_untrusted_intermediate_hop(self) -> None:
        request = Request("https://github.com/owner/repo/releases/download/v1/base.zip")
        handler = VERIFY._PinnedRedirectHandler()
        with self.assertRaisesRegex(
            VERIFY.VerificationError, "redirect left the permitted GitHub hosts"
        ):
            handler.redirect_request(
                request,
                None,
                302,
                "Found",
                {},
                "https://example.com/intermediate",
            )

    def test_manifest_matches_canonical_archive_and_checked_in_origins(self) -> None:
        manifest_path = ROOT / "parity/source-overlay-manifest.json"
        manifest = VERIFY.load_manifest(manifest_path)
        self.assertTrue(manifest["base_git_commit_authenticated"])
        self.assertEqual(
            manifest["provenance_status"],
            "public-release-reproducible-overlay",
        )
        self.assertIn("not a claim of byte parity", manifest["provenance_caveat"])

        changes = manifest["changes"]
        self.assertEqual(len(changes), 22)
        self.assertEqual(
            {kind: sum(item["change"] == kind for item in changes)
             for kind in ("replace", "add", "delete")},
            {"replace": 19, "add": 3, "delete": 0},
        )
        self.assertEqual(
            sum(item["category"] == "site-doctor-helper-hardening"
                for item in changes),
            8,
        )
        self.assertEqual(
            sum(item["category"] == "reviewed-command-source"
                for item in changes),
            8,
        )
        self.assertTrue(all(
            item.get("provenance_role") != "preserved-claude-command-source"
            for item in changes
        ))
        self.assertEqual(
            sum(item["category"] == "synchronized-gate-policy"
                for item in changes),
            3,
        )

        archive = ROOT / "parity/artifacts" / manifest["canonical_archive"]
        self.assertEqual(sha256_file(archive), manifest["canonical_archive_sha256"])
        canonical = VERIFY.read_archive(
            archive,
            manifest["canonical_archive_sha256"],
            manifest["top_level_folder"],
        )
        for item in changes:
            self.assertEqual(
                VERIFY.sha256_bytes(canonical[item["path"]]),
                item["result_sha256"],
                item["path"],
            )
            if item.get("origin"):
                self.assertEqual(
                    sha256_file(ROOT / item["origin"]),
                    item["result_sha256"],
                    item["origin"],
                )
        VERIFY._verify_embedded_provenance(manifest, canonical)

    def test_builder_pins_the_checked_in_archive_and_overlay_manifest(self) -> None:
        archive = ROOT / "parity/artifacts" / "solo-suite-plugin-v1.0.26-codex-v1.0.27-parity-source.zip"
        manifest = ROOT / "parity/source-overlay-manifest.json"
        self.assertRegex(BUILDER.EXPECTED_ARCHIVE_SHA256, r"^[0-9a-f]{64}$")
        self.assertRegex(
            BUILDER.EXPECTED_OVERLAY_MANIFEST_SHA256, r"^[0-9a-f]{64}$"
        )
        self.assertEqual(sha256_file(archive), BUILDER.EXPECTED_ARCHIVE_SHA256)
        self.assertEqual(sha256_file(manifest), BUILDER.EXPECTED_OVERLAY_MANIFEST_SHA256)

    def test_canonical_only_mode_verifies_checked_in_result(self) -> None:
        manifest = ROOT / "parity/source-overlay-manifest.json"
        archive = ROOT / "parity/artifacts" / json.loads(
            manifest.read_text(encoding="utf-8")
        )["canonical_archive"]
        count, parity_output = VERIFY.verify_canonical_only(
            archive, manifest, target=ROOT,
        )
        self.assertEqual(count, 22)
        self.assertIsNotNone(parity_output)

    def test_fixture_rejects_an_undeclared_archive_change(self) -> None:
        top = "source"
        old = b"old\n"
        new = b"new\n"
        provenance = {
            "base_archive_sha256": "placeholder",
            "base_git_commit": "a" * 40,
            "target_sync_commit": "b" * 40,
            "capabilities_sha256": "c" * 64,
            "overlays": [{
                "path": "replace.txt",
                "role": "fixture-overlay",
                "origin": "replacement.txt",
                "sha256": sha256_bytes(new),
            }],
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.zip"
            canonical = root / "canonical.zip"
            base_files = {"same.txt": b"same\n", "replace.txt": old}
            write_zip(base, top, base_files)
            provenance["base_archive_sha256"] = sha256_file(base)
            canonical_files = {
                "same.txt": b"same\n",
                "replace.txt": new,
                "PARITY-SOURCE.json": (
                    json.dumps(provenance, sort_keys=True).encode("utf-8")
                ),
            }
            write_zip(canonical, top, canonical_files)
            manifest = {
                "schema": "solo-suite/source-overlay-manifest-v1",
                "top_level_folder": top,
                "base_archive_sha256": sha256_file(base),
                "canonical_archive_sha256": sha256_file(canonical),
                "base_git_commit": "a" * 40,
                "target_sync_commit": "b" * 40,
                "capabilities_sha256": "c" * 64,
                "provenance_caveat": "fixture",
                "changes": [
                    {
                        "path": "replace.txt",
                        "change": "replace",
                        "base_sha256": sha256_bytes(old),
                        "result_sha256": sha256_bytes(new),
                        "origin": "replacement.txt",
                        "provenance_role": "fixture-overlay",
                    },
                    {
                        "path": "PARITY-SOURCE.json",
                        "change": "add",
                        "base_sha256": None,
                        "result_sha256": sha256_bytes(
                            canonical_files["PARITY-SOURCE.json"]
                        ),
                        "origin": None,
                    },
                ],
            }
            manifest_path = root / "manifest.json"
            manifest_path.write_bytes(json.dumps(manifest).encode("utf-8"))
            count, parity_output = VERIFY.verify(
                base, canonical, manifest_path, target=None
            )
            self.assertEqual(count, 2)
            self.assertIsNone(parity_output)

            canonical_files["undeclared.txt"] = b"surprise\n"
            write_zip(canonical, top, canonical_files)
            manifest["canonical_archive_sha256"] = sha256_file(canonical)
            manifest_path.write_bytes(json.dumps(manifest).encode("utf-8"))
            with self.assertRaisesRegex(
                VERIFY.VerificationError, "unexpected=.*undeclared.txt"
            ):
                VERIFY.verify(base, canonical, manifest_path, target=None)


if __name__ == "__main__":
    unittest.main()
