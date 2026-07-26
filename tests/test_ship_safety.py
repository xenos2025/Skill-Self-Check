#!/usr/bin/env python3
"""Regression tests for skills/skill-ship-safety/scripts/ship_safety.py (stdlib only).

Run:
  python tests/test_ship_safety.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "skill-ship-safety" / "scripts" / "ship_safety.py"
BAD_FIXTURE = (
    REPO / "skills" / "skill-ship-safety" / "examples" / "fixtures" / "promise-gap"
)
SELF_CHECK_SKILL = REPO / "skills" / "skill-self-check"
SHIP_SAFETY_SKILL = REPO / "skills" / "skill-ship-safety"

GOOD_SKILL_MD = """---
name: good-cli
description: Fixture with a fully implemented documented command. Use when testing.
---

# Good CLI

```bash
python3 scripts/tool.py ping <host>
```
"""

GOOD_TOOL_PY = '''#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "ping":
        print("pong")
    else:
        print(f"Unknown command: {sys.argv[1:] or ''}")

if __name__ == "__main__":
    main()
'''


def run_script(target: Path, *flags: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(target), *flags],
        capture_output=True,
    )
    payload = json.loads(proc.stdout.decode("utf-8"))
    return proc.returncode, payload


class BadFixtureTests(unittest.TestCase):
    def test_promise_gap_stops_ship(self) -> None:
        code, report = run_script(BAD_FIXTURE)
        self.assertEqual(code, 1)
        self.assertEqual(report["verdict"], "stop_ship")
        ids = [f["id"] for f in report["findings"]]
        self.assertIn("CMD.1", ids, "missing script must be flagged")
        self.assertIn("CMD.2", ids, "unimplemented subcommand must be flagged")
        self.assertIn("EXT.1", ids, "smtplib without dry-run guard must be flagged")
        crit_ids = [f["id"] for f in report["findings"] if f["severity"] == "critical"]
        self.assertIn("CMD.2", crit_ids)
        self.assertIn("EXT.1", crit_ids)

    def test_exec_is_refused_without_trusted_isolation(self) -> None:
        code, report = run_script(BAD_FIXTURE, "--exec")
        self.assertEqual(code, 1)
        self.assertFalse(report["execution"]["performed"])
        self.assertEqual(report["execution"]["status"], "not_safely_verified")
        self.assertIn("EXEC.0", [f["id"] for f in report["findings"]])


class CleanTargetTests(unittest.TestCase):
    def test_fully_implemented_command_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "good-cli"
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text(GOOD_SKILL_MD, encoding="utf-8")
            (skill / "scripts" / "tool.py").write_text(GOOD_TOOL_PY, encoding="utf-8")
            code, report = run_script(skill)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["schema_version"], "1.0")
        self.assertEqual(report["audit_level"], "static_safety_scan")
        self.assertEqual(report["target_platform"], "generic")
        self.assertTrue(report["limitations"])
        self.assertEqual(report["verdict"], "static_pass")
        cmd = report["commands"][0]
        self.assertTrue(cmd["script_exists"])
        self.assertTrue(cmd["subcommand_implemented"])
        self.assertEqual(cmd["probe"]["status"], "not_run")

    def test_comment_only_subcommand_is_not_implementation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "comment-cli"
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                GOOD_SKILL_MD.replace("good-cli", "comment-cli").replace("ping", "deploy"),
                encoding="utf-8",
            )
            (skill / "scripts" / "tool.py").write_text(
                "# TODO: implement deploy\nprint('not implemented')\n",
                encoding="utf-8",
            )
            code, report = run_script(skill)
        self.assertEqual(code, 1)
        self.assertEqual(report["verdict"], "stop_ship")
        self.assertIn("CMD.2", [f["id"] for f in report["findings"]])

    def test_exec_request_on_clean_target_is_unverified_not_passed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "good-cli"
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text(GOOD_SKILL_MD, encoding="utf-8")
            (skill / "scripts" / "tool.py").write_text(GOOD_TOOL_PY, encoding="utf-8")
            code, report = run_script(skill, "--exec")
        self.assertEqual(code, 1)
        self.assertEqual(report["verdict"], "execution_unverified")
        self.assertFalse(report["execution"]["performed"])

    def test_placeholder_command_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "placeholder-cli"
            (skill / "references").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                GOOD_SKILL_MD.replace("good-cli", "placeholder-cli"),
                encoding="utf-8",
            )
            (skill / "scripts").mkdir()
            (skill / "scripts" / "tool.py").write_text(GOOD_TOOL_PY, encoding="utf-8")
            (skill / "references" / "template.md").write_text(
                "python scripts/<sender>.py batch.json\n",
                encoding="utf-8",
            )
            code, report = run_script(skill)
        self.assertEqual(code, 0, report["findings"])
        self.assertNotIn("CMD.1", [f["id"] for f in report["findings"]])

    def test_from_import_network_capability_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "network-cli"
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                GOOD_SKILL_MD.replace("good-cli", "network-cli"),
                encoding="utf-8",
            )
            (skill / "scripts" / "tool.py").write_text(
                "from urllib import request\n"
                "import sys\n"
                "DRY_RUN = True\n"
                "if len(sys.argv) > 1 and sys.argv[1] == 'ping':\n"
                "    print(request)\n",
                encoding="utf-8",
            )
            code, report = run_script(skill)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["external_actions"][0]["capabilities"], ["network"])

    def test_self_check_skill_has_no_criticals(self) -> None:
        code, report = run_script(SELF_CHECK_SKILL)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["counts"]["critical"], 0)

    def test_ship_safety_skill_ignores_its_unsafe_fixture(self) -> None:
        code, report = run_script(SHIP_SAFETY_SKILL)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["verdict"], "static_pass")
        self.assertEqual(report["counts"]["critical"], 0)
        self.assertEqual(report["external_actions"], [])

    def test_dual_report_templates_are_wired(self) -> None:
        skill_text = (SHIP_SAFETY_SKILL / "SKILL.md").read_text(encoding="utf-8")
        for name in ("REPORT-BUSINESS-TEMPLATE.md", "REPORT-TEMPLATE.md"):
            self.assertTrue((SHIP_SAFETY_SKILL / name).is_file())
            self.assertIn(name, skill_text)

    def test_missing_skill_md_stops_ship(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, report = run_script(Path(tmp))
        self.assertEqual(code, 1)
        self.assertEqual(report["verdict"], "stop_ship")
        self.assertEqual(report["findings"][0]["id"], "CMD.0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
