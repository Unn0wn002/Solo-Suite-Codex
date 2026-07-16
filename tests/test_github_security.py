"""Repository-local GitHub supply-chain policy checks."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
SHA_PIN = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")


def load_yaml(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path.relative_to(ROOT)} must contain a YAML mapping")
    return payload


class GitHubSecurityPolicy(unittest.TestCase):
    def test_every_workflow_declares_permissions_and_pins_actions(self):
        workflows = sorted(WORKFLOWS.glob("*.yml"))
        self.assertTrue(workflows)
        for path in workflows:
            payload = load_yaml(path)
            self.assertIn("permissions", payload, path.name)
            for job_name, job in payload.get("jobs", {}).items():
                for step in job.get("steps", []):
                    action = step.get("uses")
                    if not action or action.startswith("./"):
                        continue
                    self.assertRegex(action, SHA_PIN, f"{path.name}:{job_name}: {action}")
                    if action.startswith("actions/checkout@"):
                        self.assertIs(
                            step.get("with", {}).get("persist-credentials"),
                            False,
                            f"{path.name}:{job_name} must not persist checkout credentials",
                        )

    def test_dependabot_covers_python_and_workflow_actions(self):
        payload = load_yaml(ROOT / ".github" / "dependabot.yml")
        self.assertEqual(payload.get("version"), 2)
        updates = payload.get("updates", [])
        ecosystems = {item.get("package-ecosystem"): item for item in updates}
        self.assertEqual(set(ecosystems), {"pip", "github-actions"})
        for name, item in ecosystems.items():
            self.assertEqual(item.get("directory"), "/", name)
            self.assertEqual(item.get("schedule", {}).get("interval"), "weekly", name)
            self.assertGreater(item.get("open-pull-requests-limit", 0), 0, name)

    def test_codeql_has_only_the_permissions_it_needs(self):
        payload = load_yaml(WORKFLOWS / "codeql.yml")
        self.assertEqual(payload.get("permissions"), {})
        analyze = payload["jobs"]["analyze"]
        self.assertIn("ENABLE_PRIVATE_CODEQL", analyze.get("if", ""))
        self.assertEqual(
            analyze.get("permissions"),
            {"actions": "read", "contents": "read", "security-events": "write"},
        )
        actions = [step.get("uses", "") for step in analyze["steps"]]
        self.assertTrue(any(action.startswith("github/codeql-action/init@") for action in actions))
        self.assertTrue(any(action.startswith("github/codeql-action/analyze@") for action in actions))

    def test_release_publication_is_tag_bound_attested_draft_first_and_non_overwriting(self):
        path = WORKFLOWS / "publish-release.yml"
        payload = load_yaml(path)
        self.assertEqual(payload.get("permissions"), {})
        self.assertEqual(payload["on"], {"push": {"tags": ["v*"]}})
        build = payload["jobs"]["build"]
        self.assertEqual(
            build.get("permissions"), {"contents": "read"},
        )
        checkout = next(
            step
            for step in build["steps"]
            if step.get("uses", "").startswith("actions/checkout@")
        )
        self.assertEqual(checkout.get("with", {}).get("ref"), "${{ github.sha }}")
        attest = payload["jobs"]["attest"]
        self.assertEqual(
            attest.get("permissions"),
            {"attestations": "write", "contents": "read", "id-token": "write"},
        )
        self.assertIn("ENABLE_PRIVATE_ATTESTATIONS", attest.get("if", ""))
        publish = payload["jobs"]["publish"]
        self.assertEqual(publish.get("permissions"), {"contents": "write"})
        self.assertEqual(set(publish.get("needs", [])), {"build", "attest"})
        self.assertIn("attest.result == 'skipped'", publish.get("if", ""))
        steps = attest["steps"]
        attestation = next(
            step for step in steps if step.get("uses", "").startswith("actions/attest@")
        )
        self.assertIn("subject-path", attestation.get("with", {}))
        source = path.read_text(encoding="utf-8")
        self.assertIn("release tag", source)
        self.assertIn("--validation-state validated", source)
        self.assertIn("gh release create", source)
        self.assertIn("--verify-tag", source)
        self.assertIn("--draft", source)
        self.assertIn("gh release upload", source)
        self.assertIn("gh release edit", source)
        self.assertIn("--draft=false", source)
        self.assertIn(
            "authenticated historical Claude v1.0.26 overlay", source
        )
        self.assertIn("does not claim current Claude v1.0.27 byte parity", source)
        self.assertNotIn("--clobber", source)
        self.assertLess(source.index("gh release create"), source.index("gh release upload"))
        self.assertLess(source.index("gh release upload"), source.index("gh release edit"))


if __name__ == "__main__":
    unittest.main()
