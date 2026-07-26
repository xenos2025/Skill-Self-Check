#!/usr/bin/env python3
"""Integration checks for whole-suite audit and dual scorecard generation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO
    / "skills"
    / "skill-growth-scorecard"
    / "scripts"
    / "suite_scorecards.py"
)


class SuiteScorecardTests(unittest.TestCase):
    def test_private_run_writes_personal_and_project_scorecards(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "suite-audit"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(REPO),
                    "--out-dir",
                    str(output),
                    "--skip-tests",
                    "--pretty",
                ],
                cwd=REPO,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = {
                "suite-audit.json",
                "suite-hard-gates.json",
                "suite-ship-safety.json",
                "suite-behavior.json",
                "personal-profile.json",
                "project-profile.json",
                "personal-scorecard.html",
                "project-scorecard.html",
            }
            self.assertEqual({path.name for path in output.iterdir()}, expected)

            personal = json.loads(
                (output / "personal-profile.json").read_text(encoding="utf-8")
            )
            project = json.loads(
                (output / "project-profile.json").read_text(encoding="utf-8")
            )
            self.assertEqual(personal["default_view"], "growth")
            self.assertEqual(project["default_view"], "detection")
            self.assertEqual(personal["suite"]["summary"]["skills_total"], 4)
            self.assertEqual(
                personal["suite"]["summary"]["static_floor_pass"],
                4,
            )
            self.assertTrue(personal["suite"]["summary"]["target_unchanged"])
            self.assertTrue(personal["suite"]["target_integrity"]["unchanged"])
            finding_ids = {
                item["id"] for item in personal["suite"]["findings"]
            }
            self.assertIn("PORT.1", finding_ids)
            self.assertNotIn("ARCH.1", finding_ids)
            self.assertNotIn("SCORE.1", finding_ids)
            applicability = personal["skill_engineering"]["safety"][
                "applicability"
            ]
            self.assertEqual(
                applicability["write_back"]["status"],
                "not_applicable",
            )
            self.assertTrue(applicability["write_back"]["satisfied"])
            self.assertIn(
                "四个正式 Skill 的交付体检",
                (output / "project-scorecard.html").read_text(encoding="utf-8"),
            )

    def test_real_reports_are_refused_inside_repository(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(REPO),
                "--out-dir",
                str(REPO / "audit-output"),
                "--skip-tests",
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertIn("outside the source repository", payload["error"])
        self.assertFalse((REPO / "audit-output").exists())


if __name__ == "__main__":
    unittest.main()
