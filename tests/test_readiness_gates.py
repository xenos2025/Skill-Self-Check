#!/usr/bin/env python3
"""Regression tests for agent-work-readiness/scripts/readiness_gates.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "agent-work-readiness"
SCRIPT = SKILL / "scripts" / "readiness_gates.py"
ORAL_FIXTURE = SKILL / "examples" / "fixtures" / "oral-process"
READY_FIXTURE = SKILL / "examples" / "fixtures" / "agent-ready"


def run_script(target: Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True,
    )
    return proc.returncode, json.loads(proc.stdout.decode("utf-8"))


class ReadinessGateTests(unittest.TestCase):
    def test_oral_process_stops_at_goal_clarity(self) -> None:
        code, report = run_script(ORAL_FIXTURE)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["level"]["id"], "B1")
        self.assertEqual(report["counts"]["passed_gates"], 1)
        self.assertEqual(report["next_quest"]["gate_id"], "workflow_clarity")

    def test_agent_ready_fixture_reaches_delegation_gate(self) -> None:
        code, report = run_script(READY_FIXTURE)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["level"]["id"], "B5")
        self.assertEqual(report["counts"]["passed_gates"], 5)
        self.assertEqual(report["next_quest"]["gate_id"], "learning_evidence")

    def test_two_local_runs_and_retro_unlock_operations_level(self) -> None:
        source = json.loads(
            (READY_FIXTURE / "work-readiness.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            for name in ("pilot-1.md", "pilot-2.md", "retro.md"):
                (package / name).write_text("脱敏运行证据\n", encoding="utf-8")
            source["evidence"] = {
                "version": "1.0",
                "pilot_runs": [
                    {
                        "run_id": "P1",
                        "outcome": "通过",
                        "reviewed_by": "销售主管",
                        "artifact": "pilot-1.md",
                    },
                    {
                        "run_id": "P2",
                        "outcome": "修正后通过",
                        "reviewed_by": "销售主管",
                        "artifact": "pilot-2.md",
                    },
                ],
                "retrospective": "retro.md",
            }
            (package / "work-readiness.json").write_text(
                json.dumps(source, ensure_ascii=False),
                encoding="utf-8",
            )
            code, report = run_script(package)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["level"]["id"], "B6")
        self.assertIsNone(report["next_quest"])

    def test_absolute_evidence_path_cannot_unlock_level(self) -> None:
        source = json.loads(
            (READY_FIXTURE / "work-readiness.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            source["evidence"] = {
                "version": "1.0",
                "pilot_runs": [
                    {
                        "run_id": "P1",
                        "outcome": "通过",
                        "reviewed_by": "主管",
                        "artifact": str((package / "outside.md").resolve()),
                    },
                    {
                        "run_id": "P2",
                        "outcome": "通过",
                        "reviewed_by": "主管",
                        "artifact": str((package / "outside-2.md").resolve()),
                    },
                ],
                "retrospective": str((package / "retro.md").resolve()),
            }
            (package / "work-readiness.json").write_text(
                json.dumps(source, ensure_ascii=False),
                encoding="utf-8",
            )
            code, report = run_script(package)
        self.assertEqual(code, 0)
        self.assertEqual(report["level"]["id"], "B5")
        notes = report["gates"][-1]["notes"]
        self.assertTrue(any("safe relative path" in item for item in notes))

    def test_invalid_json_returns_machine_readable_critical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "work-readiness.json"
            target.write_text("{broken", encoding="utf-8")
            code, report = run_script(target)
        self.assertEqual(code, 2)
        self.assertEqual(report["level"]["id"], "B0")
        self.assertEqual(report["findings"][0]["severity"], "critical")


if __name__ == "__main__":
    unittest.main(verbosity=2)
