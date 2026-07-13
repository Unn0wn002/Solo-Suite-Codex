"""Full Team version and selected-room capability preflight tests."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "plugins/full-team/skills/full-team-orchestrator/scripts/preflight.py"
)
CONTRACT = (
    ROOT / "plugins/full-team/skills/full-team-orchestrator/"
    "references/component-plugins.json"
)
ROOM = (
    ROOT / "plugins/ai/skills/agent-room-templates/agentsrooms/"
    "full-team-website.json"
)


spec = importlib.util.spec_from_file_location("full_team_preflight", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load Full Team preflight")
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


class FullTeamPreflight(unittest.TestCase):
    def test_current_suite_and_complete_room_pass(self):
        result = preflight.preflight(ROOT, ROOM, CONTRACT)
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["components_checked"], 17)
        self.assertGreater(result["commands_checked"], 50)
        self.assertIn("0 problem(s)", result["validator_output"])

    def test_version_skew_and_missing_room_command_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
            contract["components"][0]["minimum_version"] = "99.0.0"
            contract_path = root / "components.json"
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            room = json.loads(ROOM.read_text(encoding="utf-8"))
            room["seats"][1]["commands"].append("$missing-preflight-skill")
            room_path = root / "room.json"
            room_path.write_text(json.dumps(room), encoding="utf-8")
            result = preflight.preflight(ROOT, room_path, contract_path)
            self.assertEqual(result["status"], "FAIL")
            text = "\n".join(result["failures"])
            self.assertIn("below required 99.0.0", text)
            self.assertIn("$missing-preflight-skill", text)
            self.assertIn("validator rejected", text)


if __name__ == "__main__":
    unittest.main()
