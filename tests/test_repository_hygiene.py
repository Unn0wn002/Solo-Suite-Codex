"""Repository hygiene checks needed for reproducible GitHub releases."""

from __future__ import annotations

import re
import hashlib
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINARY_SUFFIXES = {
    ".coverage",
    ".docx",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".pyc",
    ".ttf",
    ".woff",
    ".woff2",
    ".zip",
}
PIN = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s]+)$")


def repository_text_files() -> list[Path]:
    from tools import package_release

    files = []
    for path in package_release.included_files(ROOT):
        if path.name in {".coverage", "coverage.xml"}:
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        files.append(path)
    return files


class RepositoryHygiene(unittest.TestCase):
    def test_generated_runtime_state_is_not_release_input(self):
        from tools import package_release

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            included = root / "plugins" / "demo" / "SKILL.md"
            included.parent.mkdir(parents=True)
            included.write_bytes(b"release input\n")
            runtime_paths = (
                root / ".solo" / "project.md",
                root / ".solo" / "gate-evidence" / "product.json",
                root / ".solo" / "run-state" / "run.json",
                root / "artifacts" / "runs" / "run-1" / "state.json",
                root / "worktrees" / "runs" / "run-1" / "worker" / "log.txt",
            )
            for path in runtime_paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"generated\r\n")

            packaged = set(package_release.included_files(root))
            self.assertIn(included, packaged)
            self.assertFalse(packaged.intersection(runtime_paths))

    def test_repository_text_is_lf_normalized(self):
        offenders = []
        for path in repository_text_files():
            data = path.read_bytes()
            if b"\r" in data:
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [], "non-LF text files: " + ", ".join(offenders))

        from tools import package_release
        declared = {}
        for line in (ROOT / "RELEASE-CHECKSUMS.txt").read_text(
                encoding="utf-8").splitlines():
            digest, relative = line.split("  ", 1)
            declared[relative] = digest
        actual = {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in package_release.included_files(ROOT)
            if path.name != "RELEASE-CHECKSUMS.txt"
        }
        self.assertEqual(declared, actual, "source checksum inventory is stale")

    def test_gitattributes_enforces_portable_text_and_binary_assets(self):
        attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("* text=auto eol=lf", attributes)
        for suffix in ("docx", "zip", "pdf", "png", "woff2"):
            self.assertIn(f"*.{suffix} binary", attributes)

    def test_validation_dependencies_are_hash_locked_and_used_by_ci(self):
        requested = set()
        for raw in (ROOT / "requirements-dev.txt").read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            match = PIN.fullmatch(line)
            self.assertIsNotNone(match, line)
            requested.add(match.group(1).lower().replace("_", "-"))

        lock = (ROOT / "requirements-dev.lock").read_text(encoding="utf-8")
        locked = {
            match.group(1).lower().replace("_", "-")
            for match in re.finditer(r"(?m)^([A-Za-z0-9_.-]+)==", lock)
        }
        self.assertTrue(requested.issubset(locked), sorted(requested - locked))
        blocks = re.split(r"(?m)(?=^[A-Za-z0-9_.-]+==)", lock)
        requirement_blocks = [block for block in blocks if PIN.match(block.split(" \\", 1)[0])]
        self.assertTrue(requirement_blocks)
        for block in requirement_blocks:
            self.assertIn("--hash=sha256:", block, block.splitlines()[0])

        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("--require-hashes", ci)
        self.assertIn("requirements-dev.lock", ci)


if __name__ == "__main__":
    unittest.main()
